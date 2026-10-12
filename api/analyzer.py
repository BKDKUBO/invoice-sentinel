"""Gemini multimodal invoice analyzer with mock/heuristic fallback."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone, timedelta
from typing import Any
from zoneinfo import ZoneInfo

MANILA = ZoneInfo("Asia/Manila")

RISK_SCHEMA_HINT = """
Return ONLY valid JSON (no markdown) matching this schema:
{
  "vendor": string,
  "vendor_tin": string,
  "invoice_number": string,
  "date": string (YYYY-MM-DD if possible),
  "currency": string (prefer PHP),
  "subtotal": number,
  "tax": number,
  "total": number,
  "line_items": [{"description": string, "qty": number, "unit_price": number, "amount": number}],
  "summary": string (1-2 sentences),
  "risk_flags": [{
    "code": one of GHOST_VENDOR|DUPLICATE_INVOICE|AMOUNT_MISMATCH|TEMPLATE_LOOKING|MATH_ERROR|UNUSUAL_PAYMENT_CHANGE|MISSING_FIELDS,
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
"""


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


def analyze_with_gemini(file_bytes: bytes, mime_type: str, filename: str, existing_cases: list[dict]) -> dict[str, Any]:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

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
            }
        )

    prompt = (
        f"Analyze this accounts-payable invoice/receipt for fraud and AP risk.\n"
        f"Filename: {filename}\n"
        f"Existing cases (for duplicate detection): {json.dumps(known)}\n"
        f"{RISK_SCHEMA_HINT}"
    )

    part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type or "application/octet-stream")
    response = client.models.generate_content(
        model=gemini_model_name(),
        contents=[prompt, part],
        config=types.GenerateContentConfig(temperature=0.2, response_mime_type="application/json"),
    )
    data = _parse_json_loose(response.text or "{}")
    return _normalize_analysis(data, existing_cases)


def analyze_mock(filename: str, existing_cases: list[dict]) -> dict[str, Any]:
    """Heuristic analyzer for demo without GEMINI_API_KEY."""
    name = filename.lower()

    # Match seed-style filenames for consistent demos
    if "duplicate" in name or "inv-88421" in name and "acme" in name:
        return _normalize_analysis(
            {
                "vendor": "Acme Office Supplies Inc.",
                "vendor_tin": "123-456-789-000",
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
    )


def Path_stem(filename: str) -> str:
    base = filename.rsplit("/", 1)[-1]
    if "." in base:
        return base.rsplit(".", 1)[0]
    return base


def _normalize_analysis(data: dict[str, Any], existing_cases: list[dict]) -> dict[str, Any]:
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
    if norm_items and total > 0:
        expected = lines_sum + tax
        if abs(expected - total) > max(1.0, total * 0.02):
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

    score = int(data.get("overall_risk_score") or 0)
    if flags and score < 40:
        sev_rank = {"low": 30, "medium": 50, "high": 75, "critical": 90}
        score = max(score, max(sev_rank.get(f["severity"], 40) for f in flags))
    score = max(0, min(100, score))

    return {
        "extraction": {
            "vendor": vendor,
            "vendor_tin": str(data.get("vendor_tin") or ""),
            "invoice_number": inv,
            "date": str(data.get("date") or ""),
            "currency": str(data.get("currency") or "PHP"),
            "subtotal": float(data.get("subtotal") or 0),
            "tax": tax,
            "total": total,
            "line_items": norm_items,
            "summary": str(data.get("summary") or ""),
        },
        "risk_flags": flags,
        "overall_risk_score": score,
        "severity": score_to_severity(score),
    }


def analyze_invoice(
    file_bytes: bytes,
    mime_type: str,
    filename: str,
    existing_cases: list[dict],
) -> tuple[dict[str, Any], str]:
    """Returns (analysis_dict, mode) where mode is 'gemini' or 'mock'."""
    if gemini_configured():
        try:
            return analyze_with_gemini(file_bytes, mime_type, filename, existing_cases), "gemini"
        except Exception as exc:  # noqa: BLE001 — fall back for demo resilience
            mock = analyze_mock(filename, existing_cases)
            mock["extraction"]["summary"] = (
                f"(Gemini failed: {exc}; used mock analyzer) " + mock["extraction"].get("summary", "")
            )
            return mock, "mock"
    return analyze_mock(filename, existing_cases), "mock"
