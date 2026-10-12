"""Pydantic models for InvoiceSentinel API."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


Severity = Literal["low", "medium", "high", "critical"]
CaseStatus = Literal["open", "approved", "escalated", "docs_requested"]
RiskCode = Literal[
    "GHOST_VENDOR",
    "DUPLICATE_INVOICE",
    "AMOUNT_MISMATCH",
    "OVERBILLING",
    "TEMPLATE_LOOKING",
    "MATH_ERROR",
    "UNUSUAL_PAYMENT_CHANGE",
    "MISSING_FIELDS",
    "UNKNOWN_VENDOR",
    "VENDOR_TIN_MISMATCH",
    "MISSING_PO",
    "PO_MISMATCH",
]


class LineItem(BaseModel):
    description: str = ""
    qty: float = 0
    unit_price: float = 0
    amount: float = 0


class RiskFlag(BaseModel):
    code: str
    severity: Severity
    title: str
    explanation: str
    evidence: str = ""


class Payment(BaseModel):
    method: str = ""
    bank: str = ""
    account_number: str = ""
    account_name: str = ""


class Extraction(BaseModel):
    vendor: str = ""
    vendor_tin: str = ""
    vendor_address: str = ""
    invoice_number: str = ""
    po_number: str = ""
    payment: Payment = Field(default_factory=Payment)
    date: str = ""
    currency: str = "PHP"
    subtotal: float = 0
    tax: float = 0
    total: float = 0
    line_items: list[LineItem] = Field(default_factory=list)
    summary: str = ""


class AuditEntry(BaseModel):
    at: str
    action: str
    actor: str = "user"
    note: str = ""


class Case(BaseModel):
    id: str
    status: CaseStatus = "open"
    created_at: str
    updated_at: str
    filename: str
    mime_type: str = "application/octet-stream"
    source: str = "upload"
    extraction: Extraction
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    overall_risk_score: int = 0
    severity: Severity = "low"
    matching: Optional[dict[str, Any]] = None
    audit_log: list[AuditEntry] = Field(default_factory=list)


class ActionRequest(BaseModel):
    action: Literal["approve", "escalate", "request_docs"]
    note: str = ""
    actor: str = "ap_analyst"


class DashboardStats(BaseModel):
    cases_this_week: int
    amount_at_risk: float
    currency: str = "PHP"
    approved_count: int
    escalated_count: int
    open_count: int
    docs_requested_count: int
    high_critical_open: int


class AnalyzeResponse(BaseModel):
    case: Case
    mode: Literal["gemini", "mock"]


class HealthResponse(BaseModel):
    status: str = "ok"
    gemini_configured: bool
    gemini_model: Optional[str] = None
    case_count: int = 0
    mode: str = "mock"
