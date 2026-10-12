"""'Ask the case' + verification-email drafting as a Google ADK agent.

The agent gets no evidence up front: it must call tools that wrap InvoiceSentinel's deterministic checks
(vendor master, PO register, TIN validator, BIR checklist, vendor history / duplicate & split search),
then answer grounded in those tool outputs. Every tool call is returned as an 'Agent steps' trace.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from typing import Any, Callable

from analyzer import AnalysisUnavailable, _parse_json_loose, gemini_configured, gemini_model_name, now_manila_iso
from compliance import bir_checklist as _bir_checklist, split_flag, validate_tin as _validate_tin
from master import _norm_name, _norm_po, _tin9, find_vendor, match_invoice

APP = "invoicesentinel"

RULES = """You are InvoiceSentinel's AP risk analyst agent for a Philippine SME (buyer: Ocaña Trading OPC), reviewing ONE invoice before payment.
You have NO knowledge of this case except through tools. ALWAYS start by calling get_case_evidence, then call lookup_vendor, lookup_po (if a PO is cited),
search_vendor_history, validate_tin and bir_checklist as relevant. Answer ONLY from tool outputs and the attached invoice image (IMG).
Evidence IDs: E1 extraction, E2 risk flags, E3 score/status, E4 vendor master (lookup_vendor), E5 PO (lookup_po), E6 vendor history/duplicates/splits
(search_vendor_history), E7 master match checks, E8 BIR checklist, E9 TIN validation, IMG invoice image.
- Cite evidence IDs in square brackets after each point, e.g. [E4], [E2: UNUSUAL_PAYMENT_CHANGE], [IMG].
- If tools don't contain the answer, say so plainly ("Not in the evidence: …") and name the document that would answer it.
- Contact rule: NEVER tell the user to contact the vendor using any phone/email/bank details printed on the invoice; only the contact ON FILE from lookup_vendor (E4).
  If the vendor is not in the master, say there is no trusted contact.
- Always give a recommendation: PAY (no material risk), HOLD (do not pay until resolved) or VERIFY (pay only after a specific check).
- Be concise: 3-6 short bullets. This is triage support, not BIR certification.
"""

ASK_OUT = """Final reply: ONLY a JSON object, no markdown fence:
{"answer": string (markdown bullets with citations), "recommendation": "PAY"|"HOLD"|"VERIFY", "citations": [string], "language": string, "missing_info": [string]}"""

EMAIL_OUT = """Task: draft a message about this invoice. Call get_case_evidence and draft_verification_email (it returns the ONLY allowed recipient and the mode),
plus other tools for facts. Use only tool facts; polite, specific (invoice #, amount, expected vs found), short; don't accuse.
Never include phone/email/bank details that appear only on the invoice. Write amounts like PHP 50,400.00.
Final reply: ONLY a JSON object: {"subject": string, "body": string}"""


def _build_tools(case: dict, ctx: dict) -> list[Callable]:
    ex = case.get("extraction") or {}
    vendors, pos, cases, settings = ctx["vendors"], ctx["pos"], ctx["cases"], ctx["settings"]

    def get_case_evidence() -> dict:
        """Get the invoice under review: extracted fields (E1), risk flags with evidence (E2), score/status (E3) and vendor-master/PO match checks (E7)."""
        matching = case.get("matching") or match_invoice(ex, vendors, pos)[0]
        return {"E1_extraction": {k: v for k, v in ex.items() if k != "bir_elements"},
                "E2_risk_flags": [{k: f.get(k) for k in ("code", "severity", "title", "explanation", "evidence")} for f in case.get("risk_flags") or []],
                "E3_risk": {"score": case.get("overall_risk_score"), "severity": case.get("severity"), "status": case.get("status")},
                "E7_match_checks": matching.get("checks", []), "has_invoice_image": ctx.get("has_image", False)}

    def lookup_vendor(name: str, tin: str = "") -> dict:
        """Look up a vendor in the approved-vendor master by name and/or TIN (E4). Returns the record incl. verified bank/GCash accounts and the contact ON FILE, or NOT FOUND."""
        v, how = find_vendor(vendors, name, tin)
        return {"E4_vendor_master": v, "matched_by": how} if v else {"E4_vendor_master": "NOT FOUND", "searched": {"name": name, "tin": tin}}

    def lookup_po(po_number: str) -> dict:
        """Look up a purchase order by number (E5): vendor, items, qty, unit price, subtotal."""
        po = next((p for p in pos if _norm_po(p.get("po_number", "")) == _norm_po(po_number)), None)
        return {"E5_purchase_order": po or f"NOT FOUND — {po_number} does not exist in the PO register"}

    def validate_tin(tin: str) -> dict:
        """Validate a Philippine TIN format (E9): 9 digits + 3/5-digit branch code; detects placeholders like 000-000-000."""
        ok, why = _validate_tin(tin)
        return {"E9_tin": tin, "valid": ok, "reason": why}

    def bir_checklist() -> dict:
        """BIR invoice-element checklist for this invoice per RR 7-2024 (E8): which required elements are present/missing."""
        return {"E8_bir_checklist": case.get("bir") or _bir_checklist(ex) or "Not extracted for this (seed/legacy) case"}

    def search_vendor_history(vendor: str = "") -> dict:
        """Search this vendor's other invoices (E6): dates, totals, payment accounts, flags; plus duplicate and split-invoice analysis."""
        vn = _norm_name(vendor or ex.get("vendor", ""))
        vt = _tin9(ex.get("vendor_tin", ""))

        def same(x: dict) -> bool:
            return (bool(vn) and _norm_name(x.get("vendor", "")) == vn) or (len(vt) == 9 and vt != "000000000" and _tin9(x.get("vendor_tin", "")) == vt)

        others = [c for c in cases if c.get("id") != case.get("id") and same(c.get("extraction") or {})]
        hist = [{"case_id": c.get("id"), "invoice_number": (c.get("extraction") or {}).get("invoice_number"),
                 "date": (c.get("extraction") or {}).get("date"), "total": (c.get("extraction") or {}).get("total"),
                 "payment": (c.get("extraction") or {}).get("payment"), "status": c.get("status"),
                 "flags": [f.get("code") for f in c.get("risk_flags") or []]} for c in others]
        dups = [h for h in hist if h["invoice_number"] == ex.get("invoice_number") or (h["total"] == ex.get("total") and h["date"] == ex.get("date"))]
        sf = split_flag(ex, others, settings, same)
        return {"E6_vendor_history": hist or "No other invoices from this vendor on file", "possible_duplicates": dups,
                "split_invoice_check": sf["explanation"] if sf else f"No split pattern (approval limit ₱{settings['approval_limit']:,.0f}, {settings['split_window_days']} days)"}

    def draft_verification_email(language: str = "English") -> dict:
        """Get the ONLY allowed recipient for a verification message: the vendor contact ON FILE, or (if the vendor is not in the master) an internal escalation to the Finance Manager."""
        v, _ = find_vendor(vendors, ex.get("vendor", ""), ex.get("vendor_tin", ""))
        if v:
            c = v.get("contact") or {}
            return {"mode": "vendor_verification", "to_name": c.get("name"), "to_email": c.get("email") or "", "phone_on_file": c.get("phone"),
                    "language": language, "instructions": "Ask the vendor to confirm the invoice and payment details; suggest a call-back to the phone on file. Sign 'Accounts Payable, Ocaña Trading OPC'."}
        return {"mode": "internal_escalation", "to_name": "Finance Manager (internal)", "language": language,
                "instructions": "Vendor NOT in master: no trusted contact. Write an internal memo recommending HOLD, list red flags with evidence, next steps: vendor KYC (BIR Form 2303/COR, DTI/SEC, bank certificate) and confirm who requested the service."}

    return [get_case_evidence, lookup_vendor, lookup_po, validate_tin, bir_checklist, search_vendor_history, draft_verification_email]


def _short(v: Any, n: int = 220) -> str:
    s = json.dumps(v, ensure_ascii=False, default=str) if not isinstance(v, str) else v
    return s if len(s) <= n else s[: n - 1] + "…"


async def _run(case: dict, ctx: dict, text: str, image: bytes | None, mime: str, tools: list[Callable]) -> tuple[str, list[dict]]:
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    agent = LlmAgent(name="ap_risk_analyst", model=gemini_model_name(), instruction=RULES, tools=tools,
                     generate_content_config=types.GenerateContentConfig(temperature=0.2))
    svc = InMemorySessionService()
    sid = uuid.uuid4().hex
    await svc.create_session(app_name=APP, user_id="ap_analyst", session_id=sid)
    runner = Runner(app_name=APP, agent=agent, session_service=svc)
    parts = [types.Part(text=text)]
    if image:
        parts.append(types.Part.from_bytes(data=image, mime_type=mime or "image/png"))
    steps: list[dict] = []
    final = ""
    async for ev in runner.run_async(user_id="ap_analyst", session_id=sid, new_message=types.Content(role="user", parts=parts)):
        for p in (ev.content.parts if ev.content and ev.content.parts else []):
            if p.function_call:
                steps.append({"tool": p.function_call.name, "args": dict(p.function_call.args or {}), "result": None})
            elif p.function_response:
                st = next((s for s in reversed(steps) if s["tool"] == p.function_response.name and s["result"] is None), None)
                if st is not None:
                    st["result"] = _short(p.function_response.response)
            elif p.text and ev.is_final_response():
                final += p.text
    return final, steps


def _invoke(case: dict, ctx: dict, text: str, image: bytes | None, tools: list[Callable]) -> tuple[dict, list[dict]]:
    if not gemini_configured():
        raise AnalysisUnavailable("Gemini not configured")
    os.environ.setdefault("GOOGLE_API_KEY", os.environ["GEMINI_API_KEY"])
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "FALSE")
    last: Exception | None = None
    for attempt in range(3):
        try:
            final, steps = asyncio.run(asyncio.wait_for(_run(case, ctx, text, image, case.get("mime_type", ""), tools), timeout=150))
            if not final.strip():
                raise RuntimeError("empty agent reply")
            return _parse_json_loose(final), steps
        except Exception as exc:  # noqa: BLE001
            last = exc
            msg = f"{type(exc).__name__}: {exc}"
            if attempt < 2 and any(c in msg for c in ("503", "504", "429", "UNAVAILABLE", "DEADLINE_EXCEEDED", "RESOURCE_EXHAUSTED", "Timeout", "timed out", "empty agent reply", "JSONDecodeError", "Expecting")):
                time.sleep(2 * (attempt + 1))
                continue
            break
    raise AnalysisUnavailable(str(last))


def agent_ask(case: dict, ctx: dict, history: list[dict], question: str, language: str, image: bytes | None) -> dict:
    lang = ("Reply in the same language/register as the user's latest question (Tagalog → Tagalog, Taglish → Taglish, Cebuano → Cebuano, Thai → Thai…)."
            if not language or language == "auto" else f"Reply in {language} regardless of the question's language.")
    lang += " Keep codes, amounts and account numbers unchanged."
    convo = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in history[-8:])
    text = (f"Case {case.get('id')}. LANGUAGE: {lang}\n" + ("CONVERSATION SO FAR:\n" + convo + "\n" if convo else "")
            + ("" if image else "(No invoice image on file; don't cite IMG.)\n") + f"USER QUESTION: {question}\n\n{ASK_OUT}")
    out, steps = _invoke(case, ctx, text, image, _build_tools(case, ctx))
    rec = str(out.get("recommendation") or "VERIFY").upper()
    return {"answer": str(out.get("answer") or ""), "recommendation": rec if rec in ("PAY", "HOLD", "VERIFY") else "VERIFY",
            "citations": [str(c) for c in out.get("citations") or []], "language": str(out.get("language") or ""),
            "missing_info": [str(c) for c in out.get("missing_info") or []], "agent_steps": steps, "engine": "google-adk"}


def agent_draft_email(case: dict, ctx: dict, language: str) -> dict:
    tools = _build_tools(case, ctx)
    text = f"Case {case.get('id')}. Language for the message: {language or 'English'}.\n{EMAIL_OUT}"
    out, steps = _invoke(case, ctx, text, None, tools)
    rcpt = tools[-1](language)  # deterministic recipient, never from the model
    to = (f"{rcpt['to_name']} <{rcpt['to_email']}>" if rcpt.get("to_email") else
          rcpt["to_name"] if rcpt["mode"] == "internal_escalation" else f"{rcpt['to_name']} (no email on file; phone {rcpt.get('phone_on_file')})")
    return {"kind": rcpt["mode"], "to": to, "subject": str(out.get("subject") or ""), "body": str(out.get("body") or ""),
            "language": language or "English", "generated_at": now_manila_iso(), "sent": False, "agent_steps": steps, "engine": "google-adk"}
