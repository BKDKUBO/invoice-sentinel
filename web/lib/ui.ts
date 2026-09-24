import type { CaseStatus, Severity } from "./api";

export function severityBadge(sev: Severity): string {
  switch (sev) {
    case "critical":
      return "bg-red-100 text-red-800 ring-red-600/20";
    case "high":
      return "bg-orange-100 text-orange-800 ring-orange-600/20";
    case "medium":
      return "bg-amber-100 text-amber-900 ring-amber-600/20";
    default:
      return "bg-emerald-100 text-emerald-800 ring-emerald-600/20";
  }
}

export function statusBadge(status: CaseStatus): string {
  switch (status) {
    case "approved":
      return "bg-emerald-50 text-emerald-700 ring-emerald-600/20";
    case "escalated":
      return "bg-red-50 text-red-700 ring-red-600/20";
    case "docs_requested":
      return "bg-sky-50 text-sky-700 ring-sky-600/20";
    default:
      return "bg-slate-100 text-slate-700 ring-slate-500/20";
  }
}

export function statusLabel(status: CaseStatus): string {
  switch (status) {
    case "docs_requested":
      return "Docs requested";
    default:
      return status.charAt(0).toUpperCase() + status.slice(1);
  }
}
