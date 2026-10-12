"""Approved-vendor master + purchase orders (ephemeral JSON, seeded) and deterministic matching."""

from __future__ import annotations

import difflib
import json
import re
from pathlib import Path
from typing import Any

from db import collection

SEED_DIR = Path(__file__).resolve().parent / "seed"
PO_TOLERANCE = 0.05  # 5% over PO qty / unit price / subtotal is tolerated


def po_subtotal(po: dict[str, Any]) -> float:
    return round(sum(float(i.get("qty") or 0) * float(i.get("unit_price") or 0) for i in po.get("items") or []), 2)


class MasterStore:
    def __init__(self) -> None:
        self.cols = {"vendors": collection("vendors", "id"), "pos": collection("pos", "po_number")}
        self.seeds = {"vendors": SEED_DIR / "seed-vendors.json", "pos": SEED_DIR / "seed-pos.json"}
        for k, col in self.cols.items():
            if not col.exists():
                self._reset(k)

    def _reset(self, kind: str) -> int:
        rows = json.loads(self.seeds[kind].read_text("utf-8")) if self.seeds[kind].exists() else []
        self.cols[kind].replace_all(rows)
        return len(rows)

    def reset_from_seed(self) -> dict[str, int]:
        return {k: self._reset(k) for k in self.cols}

    # vendors
    def list_vendors(self) -> list[dict[str, Any]]:
        return sorted(self.cols["vendors"].all(), key=lambda r: str(r.get("id")))

    def upsert_vendor(self, v: dict[str, Any]) -> dict[str, Any]:
        if not v.get("id"):
            nums = [int(m.group(1)) for r in self.list_vendors() if (m := re.match(r"V-(\d+)", str(r.get("id"))))]
            v["id"] = f"V-{(max(nums) if nums else 0) + 1:03d}"
        return self.cols["vendors"].put(v)

    def delete_vendor(self, vid: str) -> bool:
        return self.cols["vendors"].delete(vid)

    # POs
    def list_pos(self) -> list[dict[str, Any]]:
        rows = sorted(self.cols["pos"].all(), key=lambda r: str(r.get("po_number")))
        for r in rows:
            r["subtotal"] = po_subtotal(r)
        return rows

    def upsert_po(self, po: dict[str, Any]) -> dict[str, Any]:
        po.pop("subtotal", None)
        if not po.get("po_number"):
            nums = [int(m.group(1)) for r in self.list_pos() if (m := re.search(r"(\d+)$", str(r.get("po_number"))))]
            po["po_number"] = f"PO-2026-{(max(nums) if nums else 0) + 1:04d}"
        self.cols["pos"].put(po)
        po["subtotal"] = po_subtotal(po)
        return po

    def delete_po(self, num: str) -> bool:
        return self.cols["pos"].delete(num)


# ---------------- matching ----------------

_SUFFIX = re.compile(r"\b(inc|incorporated|corp|corporation|co|company|ltd|opc|ph|philippines|services?)\b")


def _norm_name(s: str) -> str:
    s = re.sub(r"[^a-z0-9 ]", " ", (s or "").lower().replace("'", ""))
    s = _SUFFIX.sub(" ", s)
    return " ".join(s.split())


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def _tin9(s: str) -> str:
    return _digits(s)[:9]


def _norm_po(s: str) -> str:
    d = re.sub(r"[^A-Z0-9]", "", (s or "").upper())
    return d.removeprefix("PONO").removeprefix("PO")


def find_vendor(vendors: list[dict], name: str, tin: str) -> tuple[dict | None, str]:
    """Return (vendor, how) where how is 'tin+name', 'name', 'tin' or ''."""
    n, t = _norm_name(name), _tin9(tin)
    by_name = None
    for v in vendors:
        vn = _norm_name(v.get("name", ""))
        if vn and n and (vn == n or difflib.SequenceMatcher(None, vn, n).ratio() >= 0.88):
            by_name = v
            break
    by_tin = None
    if len(t) == 9 and t != "000000000":
        by_tin = next((v for v in vendors if _tin9(v.get("tin", "")) == t), None)
    if by_name and by_tin and by_name is by_tin:
        return by_name, "tin+name"
    if by_name:
        return by_name, "name"
    if by_tin:
        return by_tin, "tin"
    return None, ""


def _fmt(x: float) -> str:
    return f"₱{x:,.2f}"


def _flag(code: str, sev: str, title: str, expl: str, expected: str, found: str) -> dict[str, Any]:
    return {"code": code, "severity": sev, "title": title, "explanation": expl,
            "evidence": f"expected: {expected} | found: {found}"}


def match_invoice(extraction: dict[str, Any], vendors: list[dict], pos: list[dict]) -> tuple[dict[str, Any], list[dict]]:
    """Deterministic vendor-master + PO checks. Returns (matching_panel, flags)."""
    flags: list[dict] = []
    checks: list[dict] = []
    name, tin = extraction.get("vendor", ""), extraction.get("vendor_tin", "")
    v, how = find_vendor(vendors, name, tin)
    panel: dict[str, Any] = {"vendor_match": None, "po_match": None, "checks": checks}

    def chk(label: str, ok: bool | None, expected: str, found: str) -> None:
        checks.append({"label": label, "status": "pass" if ok else ("info" if ok is None else "fail"),
                       "expected": expected, "found": found})

    if not v:
        chk("Vendor in approved master", False, "an approved vendor", f"{name or '—'} (TIN {tin or '—'})")
        flags.append(_flag("UNKNOWN_VENDOR", "medium", "Vendor not in approved-vendor master",
                           f"“{name or 'Unknown'}” is not an approved vendor. Onboard and verify (TIN, address, bank) before paying.",
                           "vendor in master", f"{name or '—'} / TIN {tin or '—'}"))
    else:
        panel["vendor_match"] = {"id": v["id"], "name": v["name"], "how": how}
        chk("Vendor in approved master", True, v["name"], name)
        vt = _tin9(v.get("tin", ""))
        it = _tin9(tin)
        diff = sum(x != y for x, y in zip(it, vt)) + abs(len(it) - len(vt)) if it else 0
        if how == "tin":
            chk("Vendor name", False, v["name"], name)
            flags.append(_flag("VENDOR_TIN_MISMATCH", "high", "TIN belongs to a different vendor name",
                               f"TIN {tin} is registered in the master to {v['name']}, but the invoice says {name}.",
                               f"{v['name']} for TIN {v['tin']}", f"{name}"))
        elif not it:
            chk("TIN", None, v.get("tin", ""), "not shown")
        elif it == vt:
            chk("TIN", True, v.get("tin", ""), tin)
        elif diff <= 2 and it != "000000000":  # likely OCR misread on a blurry photo, not impersonation
            chk("TIN", None, v.get("tin", ""), f"{tin} (near-match, {diff} digit(s) differ)")
            flags.append(_flag("VENDOR_TIN_MISMATCH", "low", "TIN near-match — confirm on the original",
                               f"{v['name']} is on file with TIN {v['tin']}; the invoice reads {tin} ({diff} digit(s) differ), "
                               "which usually means a blurry photo or misread digit. Check the paper copy.", v.get("tin", ""), tin))
        else:
            chk("TIN", False, v.get("tin", ""), tin)
            flags.append(_flag("VENDOR_TIN_MISMATCH", "high", "TIN differs from vendor master",
                               f"{v['name']} is on file with TIN {v['tin']}, but this invoice shows {tin}. Possible impersonation.",
                               v.get("tin", ""), tin))

        pay = extraction.get("payment") or {}
        acct = _digits(pay.get("account_number", ""))
        verified = v.get("verified_accounts") or []
        exp = "; ".join(f"{a.get('bank')} {a.get('account_number')} ({a.get('account_name')})" for a in verified) or "none on file"
        if acct:
            found = f"{pay.get('bank') or ''} {pay.get('account_number')} ({pay.get('account_name') or '—'})".strip()
            hit = next((a for a in verified if _digits(a.get("account_number", "")) == acct), None)
            if hit:
                chk("Payment account", True, exp, found)
            else:
                chk("Payment account", False, exp, found)
                flags.append(_flag("UNUSUAL_PAYMENT_CHANGE", "critical", "Payment account differs from verified account",
                                   f"{v['name']}'s verified account is {exp}. The invoice asks for payment to {found}. "
                                   f"Call {v.get('contact', {}).get('name', 'the vendor')} at {v.get('contact', {}).get('phone', 'the number on file')} (not the number on the invoice) before paying.",
                                   exp, found))
        else:
            chk("Payment account", None, exp, "not stated on invoice")

    # PO matching
    ref = (extraction.get("po_number") or "").strip()
    po = None
    if ref:
        po = next((p for p in pos if _norm_po(p.get("po_number", "")) == _norm_po(ref)), None)
        if not po:
            chk("Purchase order", False, "an existing PO", ref)
            flags.append(_flag("MISSING_PO", "high", "Referenced PO not found",
                               f"The invoice cites {ref}, but no such purchase order exists. Goods/services may not have been ordered.",
                               "PO in register", ref))
    else:
        chk("Purchase order", None, "PO # on invoice", "none cited (non-PO spend)")
    if po:
        panel["po_match"] = {"po_number": po["po_number"], "subtotal": po_subtotal(po)}
        if v and po.get("vendor_id") and po["vendor_id"] != v["id"]:
            chk("PO vendor", False, po.get("vendor", ""), name)
            flags.append(_flag("PO_MISMATCH", "high", "PO belongs to another vendor",
                               f"{po['po_number']} was issued to {po.get('vendor')}, not {name}.", po.get("vendor", ""), name))
        else:
            chk("Purchase order", True, po["po_number"], ref)
        problems = []
        po_items = po.get("items") or []
        for li in extraction.get("line_items") or []:
            desc = li.get("description", "")
            if not desc or (not li.get("amount") and not li.get("qty")):
                continue
            best, br = None, 0.0
            for pi in po_items:
                r = difflib.SequenceMatcher(None, desc.lower(), str(pi.get("description", "")).lower()).ratio()
                if r > br:
                    best, br = pi, r
            if not best or br < 0.55:
                problems.append(f"“{desc}” is not on {po['po_number']}")
                chk(f"Line: {desc}", False, "item on PO", "not on PO")
                continue
            q, u = float(li.get("qty") or 0), float(li.get("unit_price") or 0)
            pq, pu = float(best.get("qty") or 0), float(best.get("unit_price") or 0)
            bad = []
            if pq and q > pq * (1 + PO_TOLERANCE):
                bad.append(f"qty {q:g} vs PO {pq:g}")
            if pu and u > pu * (1 + PO_TOLERANCE):
                bad.append(f"unit price {_fmt(u)} vs PO {_fmt(pu)} (+{(u / pu - 1) * 100:.0f}%)")
            chk(f"Line: {desc}", not bad, f"qty ≤ {pq:g} @ ≤ {_fmt(pu)}", f"qty {q:g} @ {_fmt(u)}")
            if bad:
                problems.append(f"{desc}: " + ", ".join(bad))
        inv_sub = float(extraction.get("subtotal") or 0) or sum(float(li.get("amount") or 0) for li in extraction.get("line_items") or [])
        ps = po_subtotal(po)
        if ps and inv_sub > ps * (1 + PO_TOLERANCE):
            problems.append(f"subtotal {_fmt(inv_sub)} vs PO {_fmt(ps)} (+{(inv_sub / ps - 1) * 100:.0f}%)")
            chk("Subtotal vs PO", False, f"≤ {_fmt(ps * (1 + PO_TOLERANCE))}", _fmt(inv_sub))
        else:
            chk("Subtotal vs PO", True, f"≤ {_fmt(ps * (1 + PO_TOLERANCE))}", _fmt(inv_sub))
        if problems:
            flags.append({"code": "PO_MISMATCH", "severity": "high", "title": f"Invoice exceeds {po['po_number']}",
                          "explanation": f"Billed beyond the approved PO (tolerance {PO_TOLERANCE:.0%}): " + "; ".join(problems) + ".",
                          "evidence": "; ".join(problems)})
    return panel, flags
