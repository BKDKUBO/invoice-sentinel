"""InvoiceSentinel FastAPI — AP risk desk API for Cloud Run."""

from __future__ import annotations

import logging

import os
import uuid
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from analyzer import AnalysisUnavailable, analyze_invoice, gemini_configured, gemini_model_name, now_manila_iso
from models import ActionRequest, AnalyzeResponse, Case, DashboardStats, HealthResponse
from storage import CaseStore
from master import MasterStore, match_invoice, find_vendor
from assistant import ChatStore, LANGUAGES, ask as ask_case, build_evidence, draft_email
from pathlib import Path
from compliance import SettingsStore, bir_checklist, validate_tin

load_dotenv()
# Also load monorepo root .env if present
_root_env = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(_root_env)

MANILA = ZoneInfo("Asia/Manila")
store = CaseStore()
master = MasterStore()
chats = ChatStore()
settings_store = SettingsStore()

app = FastAPI(
    title="InvoiceSentinel API",
    description="AI AP risk triage for PH SMEs — Gemini multimodal + human-in-the-loop cases.",
    version="0.1.0",
)

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    configured = gemini_configured()
    return HealthResponse(
        status="ok",
        gemini_configured=configured,
        gemini_model=gemini_model_name() if configured else None,
        case_count=len(store.list_cases()),
        mode="gemini" if configured else "mock",
    )


@app.get("/api/dashboard", response_model=DashboardStats)
def dashboard() -> DashboardStats:
    cases = store.list_cases()
    week_ago = datetime.now(MANILA) - timedelta(days=7)
    cases_this_week = 0
    amount_at_risk = 0.0
    approved = escalated = open_c = docs = high_crit = 0

    for c in cases:
        created = c.get("created_at") or ""
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=MANILA)
            if dt >= week_ago:
                cases_this_week += 1
        except ValueError:
            cases_this_week += 1

        status = c.get("status") or "open"
        if status == "approved":
            approved += 1
        elif status == "escalated":
            escalated += 1
        elif status == "docs_requested":
            docs += 1
        else:
            open_c += 1

        sev = c.get("severity") or "low"
        if status == "open" and sev in ("high", "critical"):
            high_crit += 1
            amount_at_risk += float((c.get("extraction") or {}).get("total") or 0)

    return DashboardStats(
        cases_this_week=cases_this_week,
        amount_at_risk=round(amount_at_risk, 2),
        approved_count=approved,
        escalated_count=escalated,
        open_count=open_c,
        docs_requested_count=docs,
        high_critical_open=high_crit,
    )


@app.get("/api/cases")
def list_cases() -> list[dict[str, Any]]:
    return store.list_cases()


@app.get("/api/cases/{case_id}")
def get_case(case_id: str) -> dict[str, Any]:
    case = store.get_case(case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    return case


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(file: UploadFile = File(...)) -> AnalyzeResponse:
    content = await file.read()
    if not content:
        raise HTTPException(400, "Empty file")
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 20MB)")

    filename = file.filename or "upload.bin"
    mime = file.content_type or "application/octet-stream"
    allowed = {
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/webp",
        "application/octet-stream",
    }
    # Allow by extension if mime is generic
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if mime not in allowed and ext not in ("pdf", "png", "jpg", "jpeg", "webp"):
        raise HTTPException(400, "Unsupported type — use PDF/PNG/JPG")

    if ext == "pdf":
        mime = "application/pdf"
    elif ext in ("png",):
        mime = "image/png"
    elif ext in ("jpg", "jpeg"):
        mime = "image/jpeg"
    elif ext == "webp":
        mime = "image/webp"

    existing = store.list_cases()
    try:
        analysis, mode = analyze_invoice(content, mime, filename, existing, (master.list_vendors(), master.list_pos(), settings_store.get()))
    except AnalysisUnavailable as exc:
        logging.getLogger("invoicesentinel").warning("Gemini analysis failed: %s", str(exc)[:300])
        raise HTTPException(503, "Analysis unavailable, please retry")

    case_id = f"case-{uuid.uuid4().hex[:10]}"
    ts = now_manila_iso()
    store.save_upload(case_id, filename, content)

    case: dict[str, Any] = {
        "id": case_id,
        "status": "open",
        "created_at": ts,
        "updated_at": ts,
        "filename": filename,
        "mime_type": mime,
        "source": "upload",
        "extraction": analysis["extraction"],
        "risk_flags": analysis["risk_flags"],
        "overall_risk_score": analysis["overall_risk_score"],
        "severity": analysis["severity"],
        "matching": analysis.get("matching"),
        "bir": analysis.get("bir"),
        "audit_log": [
            {
                "at": ts,
                "action": "ingested",
                "actor": "system",
                "note": f"Uploaded {filename}; analyzer mode={mode}",
            }
        ],
    }
    if analysis["risk_flags"]:
        case["audit_log"].append(
            {
                "at": ts,
                "action": "flagged",
                "actor": "analyzer",
                "note": ", ".join(f["code"] for f in analysis["risk_flags"]),
            }
        )

    store.upsert_case(case)
    return AnalyzeResponse(case=Case.model_validate(case), mode=mode)  # type: ignore[arg-type]


@app.post("/api/cases/{case_id}/action")
def case_action(case_id: str, body: ActionRequest) -> dict[str, Any]:
    case = store.get_case(case_id)
    if not case:
        raise HTTPException(404, "Case not found")

    mapping = {
        "approve": ("approved", "approved"),
        "escalate": ("escalated", "escalated"),
        "request_docs": ("docs_requested", "docs_requested"),
    }
    status, action_name = mapping[body.action]
    ts = now_manila_iso()
    case["status"] = status
    case["updated_at"] = ts
    log = list(case.get("audit_log") or [])
    log.append(
        {
            "at": ts,
            "action": action_name,
            "actor": body.actor or "ap_analyst",
            "note": body.note or "",
        }
    )
    case["audit_log"] = log
    store.upsert_case(case)
    return case


@app.post("/api/reset-demo")
def reset_demo() -> dict[str, Any]:
    n = store.reset_from_seed()
    m = master.reset_from_seed()
    chats.clear()
    settings_store.reset()
    return {"ok": True, "case_count": n, "vendor_count": m["vendors"], "po_count": m["pos"],
            "message": "Restored seed cases, vendor master and POs"}


@app.get("/api/cases/{case_id}/matching")
def case_matching(case_id: str) -> dict[str, Any]:
    """Vendor/PO evidence panel; computed live for cases ingested before the master existed (e.g. seeds)."""
    case = store.get_case(case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    if case.get("matching"):
        return {**case["matching"], "live": False}
    panel, flags = match_invoice(case.get("extraction") or {}, master.list_vendors(), master.list_pos())
    return {**panel, "live": True, "suggested_flags": flags}


def _case_ctx(case_id: str):
    case = store.get_case(case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    vendors, pos = master.list_vendors(), master.list_pos()
    matching = case.get("matching") or match_invoice(case.get("extraction") or {}, vendors, pos)[0]
    ev = build_evidence(case, store.list_cases(), vendors, pos, matching)
    safe = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in case.get("filename", ""))
    img = Path(store.upload_dir) / f"{case_id}_{safe}"
    vendor, _ = find_vendor(vendors, (case.get("extraction") or {}).get("vendor", ""), (case.get("extraction") or {}).get("vendor_tin", ""))
    return case, ev, (img if img.exists() else None), vendor


@app.get("/api/settings")
def get_settings() -> dict[str, Any]:
    return settings_store.get()


@app.post("/api/settings")
def set_settings(body: dict[str, Any]) -> dict[str, Any]:
    try:
        return settings_store.update(body)
    except (ValueError, TypeError) as exc:
        raise HTTPException(400, str(exc))


@app.get("/api/cases/{case_id}/bir")
def case_bir(case_id: str) -> dict[str, Any]:
    case = store.get_case(case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    ex = case.get("extraction") or {}
    ok, why = validate_tin(ex.get("vendor_tin", ""))
    bir = case.get("bir") or bir_checklist(ex)
    return {"tin": {"value": ex.get("vendor_tin", ""), "valid": ok, "reason": why}, "checklist": bir}


@app.get("/api/languages")
def languages() -> list[str]:
    return LANGUAGES


@app.get("/api/cases/{case_id}/chat")
def get_chat(case_id: str) -> list[dict[str, Any]]:
    return chats.get(case_id)


@app.post("/api/cases/{case_id}/ask")
def ask_endpoint(case_id: str, body: dict[str, Any]) -> dict[str, Any]:
    q = str(body.get("question") or "").strip()
    if not q:
        raise HTTPException(400, "Question is required")
    if not gemini_configured():
        raise HTTPException(503, "Ask the case needs Gemini (no API key configured)")
    case, ev, img, _ = _case_ctx(case_id)
    try:
        res = ask_case(case, ev, chats.get(case_id), q[:2000], str(body.get("language") or "auto"), img)
    except AnalysisUnavailable as exc:
        logging.getLogger("invoicesentinel").warning("Ask failed: %s", str(exc)[:300])
        raise HTTPException(503, "Assistant unavailable, please retry")
    ts = now_manila_iso()
    msgs = chats.append(case_id, {"role": "user", "content": q, "at": ts},
                        {"role": "assistant", "content": res["answer"], "at": now_manila_iso(), **{k: v for k, v in res.items() if k != "answer"}})
    return {"reply": msgs[-1], "history": msgs}


@app.post("/api/cases/{case_id}/draft-email")
def draft_email_endpoint(case_id: str, body: dict[str, Any]) -> dict[str, Any]:
    if not gemini_configured():
        raise HTTPException(503, "Email drafting needs Gemini (no API key configured)")
    case, ev, _, vendor = _case_ctx(case_id)
    try:
        return draft_email(case, ev, str(body.get("language") or "English"), vendor)
    except AnalysisUnavailable as exc:
        logging.getLogger("invoicesentinel").warning("Draft failed: %s", str(exc)[:300])
        raise HTTPException(503, "Assistant unavailable, please retry")


@app.get("/api/vendors")
def list_vendors() -> list[dict[str, Any]]:
    return master.list_vendors()


@app.post("/api/vendors")
def save_vendor(body: dict[str, Any]) -> dict[str, Any]:
    if not str(body.get("name") or "").strip():
        raise HTTPException(400, "Vendor name is required")
    body.setdefault("verified_accounts", [])
    body.setdefault("contact", {})
    body.setdefault("status", "approved")
    return master.upsert_vendor(body)


@app.delete("/api/vendors/{vendor_id}")
def delete_vendor(vendor_id: str) -> dict[str, Any]:
    if not master.delete_vendor(vendor_id):
        raise HTTPException(404, "Vendor not found")
    return {"ok": True}


@app.get("/api/pos")
def list_pos() -> list[dict[str, Any]]:
    return master.list_pos()


@app.post("/api/pos")
def save_po(body: dict[str, Any]) -> dict[str, Any]:
    vendors = {v["id"]: v for v in master.list_vendors()}
    if body.get("vendor_id") not in vendors:
        raise HTTPException(400, "Unknown vendor_id")
    body["vendor"] = vendors[body["vendor_id"]]["name"]
    body["items"] = [
        {"description": str(i.get("description") or ""), "qty": float(i.get("qty") or 0), "unit_price": float(i.get("unit_price") or 0)}
        for i in body.get("items") or [] if str(i.get("description") or "").strip()
    ]
    body.setdefault("status", "open")
    return master.upsert_po(body)


@app.delete("/api/pos/{po_number}")
def delete_po(po_number: str) -> dict[str, Any]:
    if not master.delete_po(po_number):
        raise HTTPException(404, "PO not found")
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8080"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
