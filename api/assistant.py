"""'Ask the case' chat + vendor verification email drafting, grounded in case evidence (Gemini)."""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any

from analyzer import AnalysisUnavailable, _parse_json_loose, gemini_configured, gemini_model_name, now_manila_iso
from master import find_vendor, _norm_po
from storage import _default_data_dir

_lock = threading.Lock()

LANGUAGES = ["auto", "English", "Tagalog", "Taglish", "Cebuano", "Ilocano", "Bahasa Indonesia", "Bahasa Melayu",
             "Thai", "Vietnamese", "Japanese", "Korean", "Mandarin Chinese", "Hindi"]


class ChatStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.path = (data_dir or _default_data_dir()) / "chats.json"

    def _read(self) -> dict[str, list]:
        with _lock:
            return json.loads(self.path.read_text("utf-8") or "{}") if self.path.exists() else {}

    def get(self, case_id: str) -> list[dict]:
        return self._read().get(case_id, [])

    def append(self, case_id: str, *msgs: dict) -> list[dict]:
        data = self._read()
        data.setdefault(case_id, []).extend(msgs)
        with _lock:
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), "utf-8")
            tmp.replace(self.path)
        return data[case_id]

    def clear(self, case_id: str | None = None) -> None:
        data = {} if case_id is None else {k: v for k, v in self._read().items() if k != case_id}
        with _lock:
            self.path.write_text(json.dumps(data), "utf-8")


def build_evidence(case: dict, cases: list[dict], vendors: list[dict], pos: list[dict], matching: dict | None) -> dict:
    ex = case.get("extraction") or {}
    v, how = find_vendor(vendors, ex.get("vendor", ""), ex.get("vendor_tin", ""))
    po = None
    if ex.get("po_number"):
        po = next((p for p in pos if _norm_po(p.get("po_number", "")) == _norm_po(ex["po_number"])), None)
    history = []
    for c in cases:
        if c.get("id") == case.get("id"):
            continue
        cx = c.get("extraction") or {}
        cv, _ = find_vendor([v] if v else [{"id": "x", "name": ex.get("vendor", ""), "tin": ex.get("vendor_tin", "")}],
                            cx.get("vendor", ""), cx.get("vendor_tin", ""))
        if cv:
            history.append({"case_id": c.get("id"), "invoice_number": cx.get("invoice_number"), "date": cx.get("date"),
                            "total": cx.get("total"), "payment": cx.get("payment"), "po_number": cx.get("po_number"),
                            "status": c.get("status"), "flags": [f.get("code") for f in c.get("risk_flags") or []]})
    return {
        "E1_invoice_extraction": ex,
        "E2_risk_flags": [{k: f.get(k) for k in ("code", "severity", "title", "explanation", "evidence")} for f in case.get("risk_flags") or []],
        "E3_overall_risk": {"score": case.get("overall_risk_score"), "severity": case.get("severity"), "status": case.get("status")},
        "E4_vendor_master_record": v or f"NOT FOUND — vendor '{ex.get('vendor')}' is not in the approved-vendor master",
        "E5_purchase_order": po or (f"NOT FOUND — {ex['po_number']} does not exist" if ex.get("po_number") else "No PO cited on invoice"),
        "E6_vendor_history": history or "No other invoices from this vendor on file",
        "E7_master_match_checks": (matching or {}).get("checks", []),
        "E8_bir_compliance_checklist": case.get("bir") or "Not extracted for this case (seed/legacy case)",
    }


def _gemini(contents: list, temperature: float = 0.3) -> dict[str, Any]:
    if not gemini_configured():
        raise AnalysisUnavailable("Gemini not configured")
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options=types.HttpOptions(timeout=60_000))
    last: Exception | None = None
    for attempt in range(4):
        try:
            r = client.models.generate_content(
                model=gemini_model_name(), contents=contents,
                config=types.GenerateContentConfig(temperature=temperature, response_mime_type="application/json"))
            return _parse_json_loose(r.text or "{}")
        except Exception as exc:  # noqa: BLE001
            last = exc
            msg = str(exc)
            if attempt < 3 and any(c in msg for c in ("503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "timed out", "Timeout", "ReadTimeout")):
                time.sleep(2 * (attempt + 1))
                continue
            break
    raise AnalysisUnavailable(str(last))


def _image_part(path: Path | None, mime: str):
    if not path or not path.exists():
        return None
    from google.genai import types

    return types.Part.from_bytes(data=path.read_bytes(), mime_type=mime or "application/octet-stream")


ASK_RULES = """You are InvoiceSentinel's AP risk analyst assistant for a Philippine SME, reviewing ONE invoice before payment.
Answer ONLY from the evidence pack (E1-E8) and the attached invoice image (cite it as IMG). Do not use outside facts about this vendor.
- Cite evidence IDs in square brackets after each point, e.g. [E4], [E2: UNUSUAL_PAYMENT_CHANGE], [IMG].
- If the evidence doesn't contain the answer, say so plainly ("Not in the evidence: …") and say what document would answer it.
- Never tell the user to contact the vendor using phone/email/bank details printed on the invoice; only use contact details from E4.
- Always end with a recommendation: PAY (no material risk), HOLD (do not pay until resolved) or VERIFY (pay only after a specific check).
- Be concise: 3-6 short bullet points or sentences. This is triage support, not BIR certification.
LANGUAGE: {lang}
Return JSON: {{"answer": string (markdown allowed), "recommendation": "PAY"|"HOLD"|"VERIFY", "citations": [string], "language": string (language you replied in), "missing_info": [string]}}"""


def ask(case: dict, evidence: dict, history: list[dict], question: str, language: str, image: Path | None) -> dict:
    lang = ("Reply in the same language/register the user wrote their latest question in (e.g. Tagalog → Tagalog, "
            "Taglish → Taglish, Cebuano → Cebuano, Thai → Thai). Keep codes, amounts, account numbers unchanged."
            if not language or language == "auto" else
            f"Reply in {language} regardless of the question's language. Keep codes, amounts, account numbers unchanged.")
    convo = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in history[-10:])
    prompt = (ASK_RULES.format(lang=lang) + "\n\nEVIDENCE PACK:\n" + json.dumps(evidence, ensure_ascii=False, default=str)
              + ("\n\nCONVERSATION SO FAR:\n" + convo if convo else "") + f"\n\nUSER QUESTION: {question}")
    parts: list = [prompt]
    img = _image_part(image, case.get("mime_type", ""))
    if img is not None:
        parts.append(img)
    else:
        parts[0] += "\n(No invoice image on file for this case; rely on E1-E7 and do not cite IMG.)"
    out = _gemini(parts)
    rec = str(out.get("recommendation") or "VERIFY").upper()
    return {"answer": str(out.get("answer") or ""), "recommendation": rec if rec in ("PAY", "HOLD", "VERIFY") else "VERIFY",
            "citations": [str(c) for c in out.get("citations") or []], "language": str(out.get("language") or ""),
            "missing_info": [str(c) for c in out.get("missing_info") or []]}


EMAIL_RULES = """Draft a message for an accounts-payable officer at Ocaña Trading OPC (a fictional PH SME) about the invoice below.
Language: {lang}. Keep invoice numbers, account numbers and codes unchanged; write amounts like PHP 50,400.00.
{mode}
Use only facts from the evidence pack. Be polite, specific (invoice #, amount, what differs: expected vs found), and short.
Do NOT accuse; ask for confirmation. Do NOT include or ask the reader to use any phone/email/bank details that appear only on the invoice.
Return JSON: {{"kind": "vendor_verification"|"internal_escalation", "to": string, "subject": string, "body": string}}"""


def draft_email(case: dict, evidence: dict, language: str, vendor: dict | None) -> dict:
    if vendor:
        c = vendor.get("contact") or {}
        mode = (f"Write a VERIFICATION EMAIL to the vendor's contact ON FILE in the vendor master: {c.get('name')} <{c.get('email') or 'no email on file'}>, "
                f"phone on file {c.get('phone')}. Ask them to confirm the invoice and the payment details, and suggest a call-back to the number on file. "
                "Sign as 'Accounts Payable, Ocaña Trading OPC'.")
        to = f"{c.get('name', '')} <{c.get('email', '')}>" if c.get("email") else f"{c.get('name', '')} (no email on file; phone {c.get('phone', '')})"
    else:
        mode = ("The vendor is NOT in the approved-vendor master, so there is NO trusted contact. Do NOT write to the vendor. "
                "Instead write an INTERNAL ESCALATION MEMO to the Finance Manager recommending payment be held, listing the red flags with evidence, "
                "and the next steps (vendor onboarding/KYC: BIR Form 2303/COR, DTI/SEC registration, bank certificate; confirm who requested the service).")
        to = "Finance Manager (internal)"
    prompt = EMAIL_RULES.format(lang=language or "English", mode=mode) + "\n\nEVIDENCE PACK:\n" + json.dumps(evidence, ensure_ascii=False, default=str)
    out = _gemini([prompt], temperature=0.4)
    return {"kind": "vendor_verification" if vendor else "internal_escalation", "to": to,
            "subject": str(out.get("subject") or ""), "body": str(out.get("body") or ""), "language": language or "English",
            "generated_at": now_manila_iso(), "sent": False}
