"""BIR/TIN compliance checks (RR 7-2024, EOPT Act) and split-invoice detection."""

from __future__ import annotations

import json
import re
import threading
from datetime import date, datetime
from pathlib import Path
from typing import Any

from db import collection

_lock = threading.Lock()
DEFAULT_SETTINGS = {"approval_limit": 50000.0, "split_window_days": 7, "near_limit_pct": 10.0}


class SettingsStore:
    def __init__(self) -> None:
        self.col = collection("settings", "id")

    def get(self) -> dict[str, Any]:
        cur = self.col.get("app") or {}
        return {k: cur.get(k, v) for k, v in DEFAULT_SETTINGS.items()}

    def update(self, body: dict[str, Any]) -> dict[str, Any]:
        cur = self.get()
        for k in DEFAULT_SETTINGS:
            if k in body and body[k] is not None:
                cur[k] = type(DEFAULT_SETTINGS[k])(body[k])
        if cur["approval_limit"] <= 0 or cur["split_window_days"] < 1:
            raise ValueError("approval_limit must be > 0 and split_window_days ≥ 1")
        self.col.put({"id": "app", **cur})
        return cur

    def reset(self) -> dict[str, Any]:
        self.col.replace_all([{"id": "app", **DEFAULT_SETTINGS}])
        return dict(DEFAULT_SETTINGS)


# ---------------- TIN ----------------
# BIR TIN = 9 digits + branch code (3 digits, or 5 digits as printed per RR 7-2024 example "123-456-789-00000").
_TIN_RE = re.compile(r"^\d{3}-?\d{3}-?\d{3}(?:-?\d{3}|-?\d{5})?$")
_PLACEHOLDERS = {"123456789": "BIR's own sample TIN (123-456-789)", "987654321": "BIR's own sample TIN (987-654-321)"}


def validate_tin(tin: str) -> tuple[bool, str]:
    raw = (tin or "").strip()
    if not raw:
        return False, "missing"
    s = re.sub(r"\s+", "", raw)
    if not _TIN_RE.match(s):
        return False, "malformed — not a 9-digit NNN-NNN-NNN TIN with a 3- or 5-digit branch code (e.g. 123-456-789-00000)"
    d9 = re.sub(r"\D", "", s)[:9]
    if len(set(d9)) == 1:
        return False, f"placeholder — repeated digit {d9[0]} (e.g. 000-000-000)"
    if d9 in _PLACEHOLDERS:
        return False, f"placeholder — {_PLACEHOLDERS[d9]}"
    return True, "valid format"


def tin_flag(tin: str) -> dict | None:
    ok, why = validate_tin(tin)
    if ok or why == "missing":
        return None  # missing TIN is covered by the BIR checklist
    placeholder = why.startswith("placeholder")
    return {"code": "TIN_INVALID", "severity": "high" if placeholder else "medium",
            "title": "Placeholder TIN" if placeholder else "Malformed TIN",
            "explanation": f"Seller TIN “{tin}” is {why}. A real BIR TIN cannot be verified from this.",
            "evidence": f"expected: NNN-NNN-NNN-BBB(BB) | found: {tin}"}


# ---------------- BIR invoice elements (RR 7-2024 Sec. 6(B)) ----------------
BIR_ELEMENTS = [
    # key, label, rule ref, applies(ctx) -> required?
    ("invoice_title", "Document titled “Invoice” (Sales/Service/Cash/Charge Invoice)", "RR 7-2024 §6(B)(4)"),
    ("seller_registered_name", "Seller registered name", "§6(B)(1)"),
    ("vat_status_statement", "“VAT Reg.” / “Non-VAT Reg.” statement", "§6(B)(2)"),
    ("seller_tin_branch", "Seller TIN with branch code", "§6(B)(2)"),
    ("business_address", "Registered business address", "§6(B)(3)"),
    ("transaction_date", "Date of transaction", "§6(B)(5)"),
    ("serial_number", "Serial number", "§6(B)(7)"),
    ("buyer_details", "Buyer registered name, address and TIN (VAT sale ≥ ₱1,000)", "§6(B)(6); Sec. 113(B)(4)"),
    ("item_details", "Quantity, unit cost, description", "§6(B)(8)-(10)"),
    ("vat_breakdown", "VAT shown separately / VATable-exempt-zero-rated breakdown", "§6(B)(11)-(13)"),
    ("permit_info", "ATP / CAS permit or printer accreditation details", "RR 7-2024 §6 printing; RR 18-2012"),
]
BIR_SCHEMA_HINT = (
    '"document_type": "invoice"|"official_receipt"|"billing_statement"|"other",\n'
    '  "seller_vat_registered": true|false|null,\n'
    '  "bir_elements": {' + ", ".join(f'"{k}": "present"|"missing"|"unreadable"' for k, _, _ in BIR_ELEMENTS) + "},\n"
    '  (bir_elements: for each Philippine BIR invoice element, is it printed on the document? Use "unreadable" if the image is too blurry to tell. '
    'invoice_title = the word "Invoice" in the document title; buyer_details = buyer name AND TIN present; vat_breakdown = VAT shown as a separate line; '
    'permit_info = ATP number, CAS/BIR permit, or accredited printer details.)'
)
_CORE = {"seller_registered_name", "seller_tin_branch", "serial_number", "transaction_date", "invoice_title"}


def bir_checklist(extraction: dict[str, Any]) -> dict[str, Any] | None:
    els = extraction.get("bir_elements") or {}
    if not els:
        return None
    total = float(extraction.get("total") or 0)
    vat = extraction.get("seller_vat_registered")
    if vat is None:
        vat = float(extraction.get("tax") or 0) > 0
    small_nonvat = (not vat) and total < 5000
    tin_ok, tin_why = validate_tin(extraction.get("vendor_tin", ""))
    items, missing, advisory = [], [], []
    for key, label, ref in BIR_ELEMENTS:
        st = str(els.get(key) or "missing").lower()
        st = st if st in ("present", "missing", "unreadable") else "missing"
        required = True
        note = ""
        if key == "buyer_details":
            required = bool(vat) and total >= 1000
            if not required:
                note = "not required (non-VAT seller or below ₱1,000)"
        if key == "vat_breakdown":
            required = bool(vat)
            if not required:
                note = "not required for non-VAT seller"
        if key == "permit_info":
            required = False
            note = "advisory (supports authenticity)"
        if key == "seller_tin_branch" and st == "present" and not tin_ok:
            st, note = "invalid", f"TIN {tin_why}"
        if key == "invoice_title" and st == "missing" and extraction.get("document_type") == "official_receipt":
            note = "Official Receipt — post-EOPT, ORs are supplementary, not valid invoices (unused ORs only if stamped “Invoice”)"
            if small_nonvat:
                required = False
                note += "; small non-VAT receipt, advisory only"
        status = st if st != "missing" else ("missing" if required else "advisory")
        items.append({"key": key, "label": label, "ref": ref, "status": status, "required": required, "note": note})
        if status in ("missing", "invalid"):
            missing.append(label)
        elif status == "advisory" and st == "missing":
            advisory.append(label)
    flag = None
    buyer_label = next(l for k, l, _ in BIR_ELEMENTS if k == "buyer_details")
    if missing == [buyer_label]:
        # Only the buyer's own name/TIN block is missing: AP can fix this by asking for a re-issued invoice; checklist only, no flag.
        missing_for_flag = []
    else:
        missing_for_flag = missing
    if missing_for_flag:
        core = any(i["key"] in _CORE and i["status"] in ("missing", "invalid") for i in items)
        sev = "medium" if (core and len(missing) >= 2) or len(missing) >= 3 else "low"
        flag = {"code": "BIR_FORMAT_ISSUE", "severity": sev,
                "title": f"Missing {len(missing)} BIR invoice element(s)",
                "explanation": "Per RR 7-2024 §6(B) this document lacks: " + "; ".join(missing)
                               + ". Not proof of fraud, but the invoice may not support input-tax or expense claims.",
                "evidence": "missing: " + "; ".join(missing)}
    return {"items": items, "missing": missing, "advisory": advisory, "document_type": extraction.get("document_type", ""),
            "seller_vat_registered": vat, "flag": flag}


# ---------------- split invoices ----------------
def _d(s: str) -> date | None:
    try:
        return datetime.fromisoformat(str(s)[:10]).date()
    except ValueError:
        return None


def split_flag(extraction: dict[str, Any], existing: list[dict], settings: dict[str, Any], same_vendor) -> dict | None:
    limit = float(settings["approval_limit"])
    window = int(settings["split_window_days"])
    near = limit * (1 - float(settings["near_limit_pct"]) / 100)
    total = float(extraction.get("total") or 0)
    d0 = _d(extraction.get("date", ""))
    if not total or total >= limit or not d0:
        return None
    related = []
    for c in existing:
        ex = c.get("extraction") or {}
        if not same_vendor(ex):
            continue
        if ex.get("invoice_number") and ex.get("invoice_number") == extraction.get("invoice_number"):
            continue  # exact duplicate handled by DUPLICATE_INVOICE
        po_a, po_b = str(extraction.get("po_number") or "").strip(), str(ex.get("po_number") or "").strip()
        if po_a and po_b and po_a.upper() != po_b.upper():
            continue  # each invoice is covered by its own approved PO
        t, d = float(ex.get("total") or 0), _d(ex.get("date", ""))
        if not t or t >= limit or not d or abs((d - d0).days) > window:
            continue
        related.append({"case_id": c.get("id"), "invoice_number": ex.get("invoice_number"), "date": ex.get("date"), "total": t})
    if not related:
        return None
    combined = total + sum(r["total"] for r in related)
    near_all = total >= near and all(r["total"] >= near for r in related)
    if combined <= limit and not near_all:
        return None
    lst = "; ".join(f"{r['invoice_number'] or r['case_id']} ({r['date']}, ₱{r['total']:,.2f}, {r['case_id']})" for r in related)
    return {"code": "SPLIT_INVOICE", "severity": "high",
            "title": "Possible split invoice to stay under approval limit",
            "explanation": (f"This ₱{total:,.2f} invoice and {len(related)} other(s) from the same vendor within {window} days are each under the "
                            f"₱{limit:,.0f} approval limit but total ₱{combined:,.2f}."
                            + (" Amounts sit just under the limit." if near_all else "") + f" Related: {lst}."),
            "evidence": f"expected: single invoice ≤ ₱{limit:,.0f} or approval | found: combined ₱{combined:,.2f} across "
                        f"{len(related) + 1} invoices — {lst}"}
