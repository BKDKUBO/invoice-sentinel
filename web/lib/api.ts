const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export type Severity = "low" | "medium" | "high" | "critical";
export type CaseStatus = "open" | "approved" | "escalated" | "docs_requested";

export interface LineItem {
  description: string;
  qty: number;
  unit_price: number;
  amount: number;
}

export interface RiskFlag {
  code: string;
  severity: Severity;
  title: string;
  explanation: string;
  evidence: string;
}

export interface Payment {
  method: string;
  bank: string;
  account_number: string;
  account_name: string;
}

export interface Extraction {
  vendor: string;
  vendor_tin: string;
  vendor_address?: string;
  invoice_number: string;
  po_number?: string;
  payment?: Payment;
  date: string;
  currency: string;
  subtotal: number;
  tax: number;
  total: number;
  line_items: LineItem[];
  summary: string;
}

export interface AuditEntry {
  at: string;
  action: string;
  actor: string;
  note: string;
}

export interface Case {
  id: string;
  status: CaseStatus;
  created_at: string;
  updated_at: string;
  filename: string;
  mime_type: string;
  source: string;
  extraction: Extraction;
  risk_flags: RiskFlag[];
  overall_risk_score: number;
  severity: Severity;
  audit_log: AuditEntry[];
}

export interface DashboardStats {
  cases_this_week: number;
  amount_at_risk: number;
  currency: string;
  approved_count: number;
  escalated_count: number;
  open_count: number;
  docs_requested_count: number;
  high_critical_open: number;
}

export interface Health {
  status: string;
  gemini_configured: boolean;
  gemini_model: string | null;
  case_count: number;
  mode: string;
}

export const RISK_LABELS: Record<string, string> = {
  GHOST_VENDOR: "Ghost vendor",
  DUPLICATE_INVOICE: "Duplicate invoice",
  AMOUNT_MISMATCH: "Amount mismatch",
  OVERBILLING: "Overbilling",
  TEMPLATE_LOOKING: "Template-looking",
  MATH_ERROR: "Math error",
  UNUSUAL_PAYMENT_CHANGE: "Payment change",
  MISSING_FIELDS: "Missing fields",
  UNKNOWN_VENDOR: "Unknown vendor",
  VENDOR_TIN_MISMATCH: "TIN mismatch",
  MISSING_PO: "Missing PO",
  PO_MISMATCH: "PO mismatch",
};

export interface VerifiedAccount {
  method: string;
  bank: string;
  account_number: string;
  account_name: string;
}

export interface Vendor {
  id?: string;
  name: string;
  tin: string;
  address: string;
  vat_registered?: boolean;
  contact: { name?: string; phone?: string; email?: string };
  verified_accounts: VerifiedAccount[];
  status?: string;
  notes?: string;
}

export interface POItem {
  description: string;
  qty: number;
  unit_price: number;
}

export interface PurchaseOrder {
  po_number?: string;
  vendor_id: string;
  vendor?: string;
  date: string;
  status?: string;
  items: POItem[];
  subtotal?: number;
}

export interface MatchCheck {
  label: string;
  status: "pass" | "fail" | "info";
  expected: string;
  found: string;
}

export interface Matching {
  vendor_match: { id: string; name: string; how: string } | null;
  po_match: { po_number: string; subtotal: number } | null;
  checks: MatchCheck[];
  live?: boolean;
  suggested_flags?: RiskFlag[];
}

export async function fetchMatching(id: string): Promise<Matching> {
  return handle(await fetch(`${API_URL}/api/cases/${id}/matching`, { cache: "no-store" }));
}

export async function fetchVendors(): Promise<Vendor[]> {
  return handle(await fetch(`${API_URL}/api/vendors`, { cache: "no-store" }));
}

export async function fetchPOs(): Promise<PurchaseOrder[]> {
  return handle(await fetch(`${API_URL}/api/pos`, { cache: "no-store" }));
}

async function send<T>(path: string, method: string, body?: unknown): Promise<T> {
  return handle(
    await fetch(`${API_URL}${path}`, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  );
}

export const saveVendor = (v: Vendor) => send<Vendor>("/api/vendors", "POST", v);
export const deleteVendor = (id: string) => send<{ ok: boolean }>(`/api/vendors/${encodeURIComponent(id)}`, "DELETE");
export const savePO = (p: PurchaseOrder) => send<PurchaseOrder>("/api/pos", "POST", p);
export const deletePO = (n: string) => send<{ ok: boolean }>(`/api/pos/${encodeURIComponent(n)}`, "DELETE");

export function riskLabel(code: string): string {
  return RISK_LABELS[code] ?? code;
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export async function fetchHealth(): Promise<Health> {
  return handle(await fetch(`${API_URL}/health`, { cache: "no-store" }));
}

export async function fetchDashboard(): Promise<DashboardStats> {
  return handle(await fetch(`${API_URL}/api/dashboard`, { cache: "no-store" }));
}

export async function fetchCases(): Promise<Case[]> {
  return handle(await fetch(`${API_URL}/api/cases`, { cache: "no-store" }));
}

export async function fetchCase(id: string): Promise<Case> {
  return handle(await fetch(`${API_URL}/api/cases/${id}`, { cache: "no-store" }));
}

export async function analyzeFile(file: File): Promise<{ case: Case; mode: string }> {
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(`${API_URL}/api/analyze`, { method: "POST", body: fd });
  if (res.status === 503) {
    throw new Error(
      "The AI analyzer is busy right now and couldn't check this invoice. Nothing was saved — please try again in a few seconds."
    );
  }
  return handle(res);
}

export async function postAction(
  id: string,
  action: "approve" | "escalate" | "request_docs",
  note = ""
): Promise<Case> {
  return handle(
    await fetch(`${API_URL}/api/cases/${id}/action`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, note, actor: "ap_analyst" }),
    })
  );
}

export async function resetDemo(): Promise<{ ok: boolean; case_count: number }> {
  return handle(await fetch(`${API_URL}/api/reset-demo`, { method: "POST" }));
}

export function formatPHP(amount: number, currency = "PHP"): string {
  try {
    return new Intl.NumberFormat("en-PH", {
      style: "currency",
      currency: currency || "PHP",
      maximumFractionDigits: 2,
    }).format(amount);
  } catch {
    return `₱${amount.toLocaleString("en-PH", { maximumFractionDigits: 2 })}`;
  }
}

export { API_URL };

export interface ChatMsg {
  role: "user" | "assistant";
  content: string;
  at: string;
  recommendation?: "PAY" | "HOLD" | "VERIFY";
  citations?: string[];
  language?: string;
  missing_info?: string[];
}

export interface EmailDraft {
  kind: "vendor_verification" | "internal_escalation";
  to: string;
  subject: string;
  body: string;
  language: string;
}

const BUSY = "The AI assistant is busy right now. Nothing was lost — please try again in a few seconds.";

export async function fetchChat(id: string): Promise<ChatMsg[]> {
  return handle(await fetch(`${API_URL}/api/cases/${id}/chat`, { cache: "no-store" }));
}

export async function askCase(id: string, question: string, language: string): Promise<{ history: ChatMsg[] }> {
  const res = await fetch(`${API_URL}/api/cases/${id}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, language }),
  });
  if (res.status === 503) throw new Error(BUSY);
  return handle(res);
}

export async function draftEmail(id: string, language: string): Promise<EmailDraft> {
  const res = await fetch(`${API_URL}/api/cases/${id}/draft-email`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ language }),
  });
  if (res.status === 503) throw new Error(BUSY);
  return handle(res);
}
