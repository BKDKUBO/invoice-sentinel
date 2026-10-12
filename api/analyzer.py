"""Gemini multimodal invoice analyzer with mock/heuristic fallback."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone, timedelta
from typing import Any
from zoneinfo import ZoneInfo

MANILA = ZoneInfo("Asia/Manila")

RISK_SCHEMA_HINT_RAW = """
Return ONLY valid JSON (no markdown) matching this schema:
{
  "vendor": string,
  "vendor_tin": string,
  "vendor_address": string,
  "invoice_number": string,
  "po_number": string (purchase order number referenced on the invoice, e.g. "PO-2026-0145"; "" if none),
  "payment": {"method": "bank"|"gcash"|"maya"|"check"|"cash"|"", "bank": string, "account_number": string, "account_name": string} (the account the invoice asks to be paid to; empty strings if not stated),
  "date": string (YYYY-MM-DD if possible),
  "currency": string (prefer PHP),
  "subtotal": number,
  "tax": number,
  "total": number,
  "line_items": [{"description": string, "qty": number, "unit_price": number, "amount": number}],
  "summary": string (1-2 sentences),
  __BIR__,
  "risk_flags": [{
    "code": one of GHOST_VENDOR|DUPLICATE_INVOICE|AMOUNT_MISMATCH|OVERBILLING|TEMPLATE_LOOKING|MATH_ERROR|UNUSUAL_PAYMENT_CHANGE|MISSING_FIELDS,
    "severity": low|medium|high|critical,
    "title": string,
    "explanation": string,
    "evidence": string
  }],
  "overall_risk_score": integer 0-100
}

Context: Philippine SME accounts-payable risk triage BEFORE payment.
Flag ghost/fictitious vendors, duplicates, amount mismatches, template-looking docs, math errors, unusual payment changes, missing fields.
Do NOT claim BIR compliance or tax authority status. Be conservative: unexplained high totals + vague services + placeholder TIN → GHOST_VENDOR.
Calibration rules:
- A complete, internally consistent invoice (real-looking TIN, address, ATP/series, correct 12% VAT) should score 0-20 with no flags. Plain or computer-generated layout alone is NOT a risk; do not raise TEMPLATE_LOOKING for that alone.
- Low image quality (blur, skew, dim photo) is not fraud. If a field is unreadable, lower confidence in the summary instead of flagging; only use MISSING_FIELDS for fields actually absent.
- Small non-VAT vendor receipts without customer TIN/terms are normal in PH; don't flag missing customer details.
- Unit prices far above typical PH market prices for common goods/services → OVERBILLING (not AMOUNT_MISMATCH), with the typical price range as evidence. AMOUNT_MISMATCH is only for totals that do not add up.
- Requests to pay a new/different bank account, a personal name, or a personal e-wallet, or "don't call us" → UNUSUAL_PAYMENT_CHANGE (high or critical).
- Same vendor + same total + same/similar date as an existing case but a different invoice number → DUPLICATE_INVOICE (near-duplicate).
- A vendor whose TIN matches an existing case is a known vendor; do not flag its TIN pattern as GHOST_VENDOR.
- Do not raise MISSING_FIELDS for BIR invoice elements (buyer TIN, VAT statement, ATP, serial, address); report those only in bir_elements. Use MISSING_FIELDS only for data needed to pay (amount, vendor name, invoice reference).
- Extract the payment account and PO number exactly as printed; vendor-master and PO checks are done separately by the system, so do not guess them.
"""


from compliance import BIR_SCHEMA_HINT  # noqa: E402

RISK_SCHEMA_HINT = RISK_SCHEMA_HINT_RAW.replace("__BIR__", BIR_SCHEMA_HINT)


from compliance import BIR_ELEMENTS as _BIR_EL  # noqa: E402

_STR = {"type": "string"}
_NUM = {"type": "number"}
_RISK_CODES = ["GHOST_VENDOR", "DUPLICATE_INVOICE", "AMOUNT_MISMATCH", "OVERBILLING", "TEMPLATE_LOOKING",
               "MATH_ERROR", "UNUSUAL_PAYMENT_CHANGE", "MISSING_FIELDS"]
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "vendor": _STR, "vendor_tin": _STR, "vendor_address": _STR, "invoice_number": _STR, "po_number": _STR,
        "payment": {"type": "object", "properties": {"method": _STR, "bank": _STR, "account_number": _STR, "account_name": _STR}},
        "date": _STR, "currency": _STR, "subtotal": _NUM, "tax": _NUM, "total": _NUM,
        "line_items": {"type": "array", "items": {"type": "object", "properties": {
            "description": _STR, "qty": _NUM, "unit_price": _NUM, "amount": _NUM}, "required": ["description", "qty", "unit_price", "amount"]}},
        "summary": _STR,
        "document_type": {"type": "string", "enum": ["invoice", "official_receipt", "billing_statement", "other"]},
        "seller_vat_registered": {"type": ["boolean", "null"]},
        "bir_elements": {"type": "object", "properties": {k: {"type": "string", "enum": ["present", "missing", "unreadable"]} for k, _, _ in _BIR_EL},
                         "required": [k for k, _, _ in _BIR_EL]},
        "risk_flags": {"type": "array", "items": {"type": "object", "properties": {
            "code": {"type": "string", "enum": _RISK_CODES},
            "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
            "title": _STR, "explanation": _STR, "evidence": _STR}, "required": ["code", "severity", "title", "explanation", "evidence"]}},
        "overall_risk_score": {"type": "integer"},
    },
    "required": ["vendor", "vendor_tin", "invoice_number", "po_number", "payment", "date", "subtotal", "tax", "total",
                 "line_items", "summary", "document_type", "bir_elements", "risk_flags", "overall_risk_score"],
}


class AnalysisUnavailable(RuntimeError):
    """Gemini is configured but analysis failed after retries."""


_OVERBILL_WORDS = ("overbill", "over-bill", "overpric", "inflated", "above market", "market price")


def now_manila_iso() -> str:
    return datetime.now(MANILA).isoformat(timespec="seconds")


def score_to_severity(score: int) -> str:
    if score >= 85:
        return "critical"
    if score >= 65:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def gemini_configured() -> bool:
    return bool(os.getenv("GEMINI_API_KEY", "").strip())


def gemini_model_name() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip() or "gemini-3.8-flash"


def _parse_json_loose(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            return json.loads(m.group(0))
        raise


def analyze_with_gemini(file_bytes: bytes, mime_type: str, filename: str, existing_cases: list[dict], master: tuple[list, list] | None = None) -> dict[str, Any]:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options=types.HttpOptions(timeout=60_000))

    known = []
    for c in existing_cases[:40]:
        ex = c.get("extraction") or {}
        known.append(
            {
                "id": c.get("id"),
                "vendor": ex.get("vendor"),
                "invoice_number": ex.get("invoice_number"),
                "total": ex.get("total"),
                "date": ex.get("date"),
                "vendor_tin": ex.get("vendor_tin"),
            }
        )

    prompt = (
        f"Analyze this accounts-payable invoice/receipt for fraud and AP risk.\n"
        f"Filename: {filename}\n"
        f"Existing cases (for duplicate detection): {json.dumps(known)}\n"
        f"{RISK_SCHEMA_HINT}"
    )

    part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type or "application/octet-stream")
    import time

    response = None
    for attempt in range(4):
        try:
            response = client.models.generate_content(
                model=gemini_model_name(),
                contents=[prompt, part],
                config=types.GenerateContentConfig(temperature=0.0, seed=7, response_mime_type="application/json", response_json_schema=RESPONSE_SCHEMA),
            )
            break
        except Exception as exc:  # retry transient overload / rate limits
            msg = str(exc)
            if attempt < 3 and any(c in msg for c in ("503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "timed out", "Timeout", "ReadTimeout")):
                time.sleep(2 * (attempt + 1))
                continue
            raise
    data = _parse_json_loose(response.text or "{}")
    return _normalize_analysis(data, existing_cases, master)


def analyze_mock(filename: str, existing_cases: list[dict], master: tuple[list, list] | None = None) -> dict[str, Any]:
    """Heuristic analyzer for demo without GEMINI_API_KEY."""
    name = filename.lower()

    # Match seed-style filenames for consistent demos
    if "duplicate" in name or "inv-88421" in name and "acme" in name:
        return _normalize_analysis(
            {
                "vendor": "Acme Office Supplies Inc.",
                "vendor_tin": "204-318-557-000",
                "invoice_number": "INV-88421",
                "date": "2026-09-18",
                "currency": "PHP",
                "subtotal": 12500,
                "tax": 1500,
                "total": 14000,
                "line_items": [
                    {"description": "A4 Bond Paper (ream)", "qty": 20, "unit_price": 250, "amount": 5000},
                    {"description": "Ballpoint Pens (box)", "qty": 50, "unit_price": 80, "amount": 4000},
                    {"description": "Staplers & clips kit", "qty": 10, "unit_price": 350, "amount": 3500},
                ],
                "summary": "Mock: filename suggests duplicate of known Acme INV-88421.",
                "risk_flags": [
                    {
                        "code": "DUPLICATE_INVOICE",
                        "severity": "high",
                        "title": "Possible duplicate invoice",
                        "explanation": "Filename/content pattern matches an existing Acme INV-88421 case.",
                        "evidence": f"filename={filename}",
                    }
                ],
                "overall_risk_score": 78,
            },
            existing_cases,
            master,
        )

    if "ghost" in name or "rapid" in name or "fictitious" in name:
        return _normalize_analysis(
            {
                "vendor": "Rapid Trade Solutions PH",
                "vendor_tin": "000-000-000-000",
                "invoice_number": "RTS-00991",
                "date": datetime.now(MANILA).strftime("%Y-%m-%d"),
                "currency": "PHP",
                "subtotal": 82142.86,
                "tax": 9857.14,
                "total": 92000,
                "line_items": [
                    {"description": "Consulting / facilitation fee", "qty": 1, "unit_price": 82142.86, "amount": 82142.86}
                ],
                "summary": "Mock: ghost-vendor pattern (placeholder TIN, vague service line).",
                "risk_flags": [
                    {
                        "code": "GHOST_VENDOR",
                        "severity": "critical",
                        "title": "Suspected fictitious / ghost vendor",
                        "explanation": "Placeholder TIN and opaque single-line fee — classic ghost-receipt signal.",
                        "evidence": "TIN=000-000-000-000",
                    },
                    {
                        "code": "TEMPLATE_LOOKING",
                        "severity": "medium",
                        "title": "Template-looking layout",
                        "explanation": "Generic layout with little vendor substance.",
                        "evidence": "filename heuristic",
                    },
                ],
                "overall_risk_score": 92,
            },
            existing_cases,
            master,
        )

    if "math" in name or "mismatch" in name or "error" in name:
        return _normalize_analysis(
            {
                "vendor": "Cebu Island Catering Services",
                "vendor_tin": "456-789-012-000",
                "invoice_number": "CICS-772",
                "date": "2026-09-19",
                "currency": "PHP",
                "subtotal": 28000,
                "tax": 3360,
                "total": 38500,
                "line_items": [
                    {"description": "Corporate lunch buffet (80 pax)", "qty": 80, "unit_price": 350, "amount": 28000},
                    {"description": "Service charge", "qty": 1, "unit_price": 0, "amount": 0},
                ],
                "summary": "Mock: line+tax math does not equal stated total.",
                "risk_flags": [
                    {
                        "code": "AMOUNT_MISMATCH",
                        "severity": "high",
                        "title": "Total does not match line items + tax",
                        "explanation": "Expected ₱31,360 vs stated ₱38,500.",
                        "evidence": "delta_php=7140",
                    },
                    {
                        "code": "MATH_ERROR",
                        "severity": "high",
                        "title": "Arithmetic inconsistency",
                        "explanation": "Totals appear altered after line calculation.",
                        "evidence": "filename heuristic",
                    },
                ],
                "overall_risk_score": 81,
            },
            existing_cases,
            master,
        )

    # Default: relatively clean invoice derived from filename
    vendor = re.sub(r"[_\-.]+", " ", Path_stem(filename)).title()[:48] or "Unknown Vendor"
    total = 18500.0
    if "freight" in name or "logistics" in name:
        vendor = "Manila Bay Logistics Co."
        total = 50400.0
    return _normalize_analysis(
        {
            "vendor": vendor,
            "vendor_tin": "111-222-333-000",
            "invoice_number": f"MOCK-{abs(hash(filename)) % 100000:05d}",
            "date": datetime.now(MANILA).strftime("%Y-%m-%d"),
            "currency": "PHP",
            "subtotal": round(total / 1.12, 2),
            "tax": round(total - total / 1.12, 2),
            "total": total,
            "line_items": [
                {"description": "Goods / services (mock extraction)", "qty": 1, "unit_price": total, "amount": total}
            ],
            "summary": "Mock analyzer: no high-risk signals from filename; treat as routine AP review.",
            "risk_flags": [],
            "overall_risk_score": 15,
        },
        existing_cases,
        master,
    )


def Path_stem(filename: str) -> str:
    base = filename.rsplit("/", 1)[-1]
    if "." in base:
        return base.rsplit(".", 1)[0]
    return base


def _normalize_analysis(data: dict[str, Any], existing_cases: list[dict], master: tuple[list, list] | None = None) -> dict[str, Any]:
    line_items = data.get("line_items") or []
    norm_items = []
    for li in line_items:
        if not isinstance(li, dict):
            continue
        norm_items.append(
            {
                "description": str(li.get("description") or ""),
                "qty": float(li.get("qty") or 0),
                "unit_price": float(li.get("unit_price") or 0),
                "amount": float(li.get("amount") or 0),
            }
        )

    flags = []
    for f in data.get("risk_flags") or []:
        if not isinstance(f, dict):
            continue
        flags.append(
            {
                "code": str(f.get("code") or "MISSING_FIELDS"),
                "severity": str(f.get("severity") or "medium"),
                "title": str(f.get("title") or f.get("code") or "Flag"),
                "explanation": str(f.get("explanation") or ""),
                "evidence": str(f.get("evidence") or ""),
            }
        )

    for f in flags:
        if f["code"] == "AMOUNT_MISMATCH" and any(
            w in (f["title"] + " " + f["explanation"]).lower() for w in _OVERBILL_WORDS
        ):
            f["code"] = "OVERBILLING"

    vendor = str(data.get("vendor") or "Unknown")
    inv = str(data.get("invoice_number") or "")
    total = float(data.get("total") or 0)

    # Extra duplicate check against store
    if inv:
        for c in existing_cases:
            ex = c.get("extraction") or {}
            if (
                str(ex.get("invoice_number") or "") == inv
                and str(ex.get("vendor") or "").lower() == vendor.lower()
                and abs(float(ex.get("total") or 0) - total) < 0.01
            ):
                if not any(x["code"] == "DUPLICATE_INVOICE" for x in flags):
                    flags.append(
                        {
                            "code": "DUPLICATE_INVOICE",
                            "severity": "high",
                            "title": "Possible duplicate invoice",
                            "explanation": f"Matches existing case {c.get('id')} (same vendor, invoice #, total).",
                            "evidence": f"case_id={c.get('id')}",
                        }
                    )
                break

    # Math check
    lines_sum = sum(i["amount"] for i in norm_items)
    tax = float(data.get("tax") or 0)
    subtotal = float(data.get("subtotal") or 0)
    # Deterministic 12% VAT check (PH standard rate)
    if subtotal > 0 and tax > 0 and abs(tax - subtotal * 0.12) > max(1.0, subtotal * 0.12 * 0.01):
        if not any(x["code"] == "MATH_ERROR" for x in flags):
            flags.append(
                {
                    "code": "MATH_ERROR",
                    "severity": "high",
                    "title": "VAT is not 12% of VATable sales",
                    "explanation": f"12% of {subtotal:,.2f} is {subtotal*0.12:,.2f}, but invoice shows {tax:,.2f}.",
                    "evidence": f"subtotal={subtotal}; tax={tax}; rate={tax/subtotal:.4f}",
                }
            )
    if norm_items and total > 0:
        expected = lines_sum + tax
        tol = max(1.0, total * 0.02)
        # VAT-inclusive receipts: line amounts already include VAT, so total == lines_sum is fine
        if abs(expected - total) > tol and abs(lines_sum - total) > tol:
            if not any(x["code"] in ("AMOUNT_MISMATCH", "MATH_ERROR") for x in flags):
                flags.append(
                    {
                        "code": "AMOUNT_MISMATCH",
                        "severity": "high",
                        "title": "Total does not match line items + tax",
                        "explanation": f"Lines+tax ≈ {expected:.2f} but total is {total:.2f}.",
                        "evidence": f"lines_sum={lines_sum}; tax={tax}; total={total}",
                    }
                )

    pay = data.get("payment") if isinstance(data.get("payment"), dict) else {}
    payment = {k: str(pay.get(k) or "") for k in ("method", "bank", "account_number", "account_name")}
    extraction = {
        "vendor": vendor,
        "vendor_tin": str(data.get("vendor_tin") or ""),
        "vendor_address": str(data.get("vendor_address") or ""),
        "invoice_number": inv,
        "po_number": str(data.get("po_number") or ""),
        "payment": payment,
        "date": str(data.get("date") or ""),
        "currency": str(data.get("currency") or "PHP"),
        "subtotal": float(data.get("subtotal") or 0),
        "tax": tax,
        "total": total,
        "line_items": norm_items,
        "summary": str(data.get("summary") or ""),
        "document_type": str(data.get("document_type") or ""),
        "seller_vat_registered": data.get("seller_vat_registered") if isinstance(data.get("seller_vat_registered"), bool) else None,
        "bir_elements": {str(k): str(v) for k, v in (data.get("bir_elements") or {}).items()} if isinstance(data.get("bir_elements"), dict) else {},
    }

    from compliance import DEFAULT_SETTINGS, bir_checklist, split_flag, tin_flag

    tf = tin_flag(extraction["vendor_tin"])
    if tf and not any(x["code"] == "TIN_INVALID" for x in flags):
        flags.append(tf)
    bir = bir_checklist(extraction)
    if bir and bir["flag"] and not any(x["code"] == "BIR_FORMAT_ISSUE" for x in flags):
        flags.append(bir["flag"])
    if bir:
        bir.pop("flag", None)

    matching = None
    if master is not None:
        from master import match_invoice

        matching, mflags = match_invoice(extraction, master[0], master[1])
        rank = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        for mf in mflags:
            if mf["code"] == "UNKNOWN_VENDOR":
                ghost = next((x for x in flags if x["code"] == "GHOST_VENDOR"), None)
                if ghost:  # strengthen existing ghost flag instead of duplicating
                    ghost["explanation"] += " Not found in the approved-vendor master."
                    ghost["evidence"] = (ghost["evidence"] + " | " if ghost["evidence"] else "") + "vendor master: no match"
                    if rank.get(ghost["severity"], 1) < 2:
                        ghost["severity"] = "high"
                    continue
            same = next((x for x in flags if x["code"] == mf["code"]), None)
            if same and mf["code"] == "UNUSUAL_PAYMENT_CHANGE":
                same.update(severity="critical", title=mf["title"],
                            explanation=mf["explanation"] + " " + same["explanation"], evidence=mf["evidence"])
                continue
            flags.append(mf)

    from master import _norm_name, _tin9

    settings = (master[2] if master is not None and len(master) > 2 else None) or DEFAULT_SETTINGS
    vn, vt = _norm_name(vendor), _tin9(extraction["vendor_tin"])

    def _same_vendor(ex: dict) -> bool:
        return (bool(vn) and _norm_name(ex.get("vendor", "")) == vn) or (
            len(vt) == 9 and vt != "000000000" and _tin9(ex.get("vendor_tin", "")) == vt)

    sf = split_flag(extraction, existing_cases, settings, _same_vendor)
    if sf:
        # Gemini often labels the same pattern a near-duplicate; keep the more specific SPLIT_INVOICE
        flags = [x for x in flags if not (x["code"] == "DUPLICATE_INVOICE" and not x["explanation"].startswith("Matches existing case"))]
        flags.append(sf)

    from scoring import compute_score, normalize_flags

    exact_dup = bool(inv) and any(
        str((c.get("extraction") or {}).get("invoice_number") or "") == inv and _same_vendor(c.get("extraction") or {})
        for c in existing_cases
    )
    flags = normalize_flags(flags, extraction, float(settings.get("approval_limit") or 50000), exact_dup)
    # Deterministic score from flags (severity weights + small bonus for extra flags). Gemini's own
    # overall_risk_score is kept for reference only. Floors still hold: high ≥ 70 ≥ 65, critical ≥ 90 ≥ 85.
    score = compute_score(flags)
    gemini_score = int(data.get("overall_risk_score") or 0)

    return {
        "extraction": extraction,
        "matching": matching,
        "bir": bir,
        "gemini_score": gemini_score,
        "risk_flags": flags,
        "overall_risk_score": score,
        "severity": score_to_severity(score),
    }


def analyze_invoice(
    file_bytes: bytes,
    mime_type: str,
    filename: str,
    existing_cases: list[dict],
    master: tuple[list, list] | None = None,
) -> tuple[dict[str, Any], str]:
    """Returns (analysis_dict, mode) where mode is 'gemini' or 'mock'."""
    if gemini_configured():
        try:
            return analyze_with_gemini(file_bytes, mime_type, filename, existing_cases, master), "gemini"
        except Exception as exc:  # noqa: BLE001
            # Never fabricate a case when live analysis was expected.
            raise AnalysisUnavailable(str(exc)) from exc
    return analyze_mock(filename, existing_cases, master), "mock"
