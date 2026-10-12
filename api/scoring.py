"""Deterministic severity normalisation and risk scoring (score stability).

Gemini decides *which* issues exist and explains them; these rules fix *how severe* each one is
and compute the final 0-100 score from the flags, so the same invoice scores the same every run.
"""

from __future__ import annotations

from typing import Any

SEV_WEIGHT = {"low": 20, "medium": 45, "high": 70, "critical": 90}
SEV_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}
EXTRA_PER_FLAG = 5      # each additional medium+ flag adds 5 points
EXTRA_CAP = 10          # ...up to +10
ADVISORY_CODES = {"TEMPLATE_LOOKING", "MISSING_FIELDS"}


def _cap(sev: str, top: str) -> str:
    return sev if SEV_RANK.get(sev, 1) <= SEV_RANK[top] else top


def normalize_flags(flags: list[dict[str, Any]], ex: dict[str, Any], approval_limit: float = 50000.0) -> list[dict[str, Any]]:
    codes = {f["code"] for f in flags}
    total = float(ex.get("total") or 0)
    sub = float(ex.get("subtotal") or 0)
    tax = float(ex.get("tax") or 0)
    out: list[dict[str, Any]] = []
    for f in flags:
        f = dict(f)
        c = f["code"]
        if f.get("severity") not in SEV_RANK:
            f["severity"] = "medium"
        if c == "MATH_ERROR":
            if sub > 0 and tax > 0 and total > 0:
                pct = abs(tax - 0.12 * sub) / total
                f["severity"] = "high" if pct >= 0.02 else ("medium" if pct >= 0.002 else "low")
            else:
                f["severity"] = "high"
        elif c == "AMOUNT_MISMATCH":
            f["severity"] = "high"
        elif c == "DUPLICATE_INVOICE":
            exact = f.get("explanation", "").startswith("Matches existing case") or "exact" in (f.get("title", "") + f.get("explanation", "")).lower()
            f["severity"] = "critical" if exact else "high"
        elif c == "GHOST_VENDOR":
            corroborated = bool(codes & {"TIN_INVALID", "UNKNOWN_VENDOR"}) or "vendor master: no match" in f.get("evidence", "")
            if corroborated:
                f["severity"] = "critical" if total >= approval_limit else "high"
            else:
                f["severity"] = "medium"
        elif c == "UNUSUAL_PAYMENT_CHANGE":
            # deterministic master mismatch is already critical; Gemini-only (e-wallet / personal name) → high
            f["severity"] = "critical" if f.get("title", "").startswith("Payment account differs") else "high"
        elif c == "OVERBILLING":
            f["severity"] = "high"
        elif c in ADVISORY_CODES:
            f["severity"] = _cap(f["severity"], "medium")
        out.append(f)
    # Drop generic Gemini flags already covered by the deterministic BIR checklist
    if any(f["code"] == "BIR_FORMAT_ISSUE" for f in out):
        out = [f for f in out if f["code"] not in ADVISORY_CODES]
    return out


def compute_score(flags: list[dict[str, Any]]) -> int:
    if not flags:
        return 0
    sev = sorted((SEV_WEIGHT[f["severity"]] for f in flags), reverse=True)
    extra = min(EXTRA_CAP, EXTRA_PER_FLAG * sum(1 for w in sev[1:] if w >= SEV_WEIGHT["medium"]))
    return max(0, min(100, sev[0] + extra))
