import type { CaseStatus, Severity } from "@/lib/api";
import { severityBadge, statusBadge, statusLabel } from "@/lib/ui";

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ring-1 ring-inset ${severityBadge(
        severity
      )}`}
    >
      {severity}
    </span>
  );
}

export function StatusBadge({ status }: { status: CaseStatus }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${statusBadge(
        status
      )}`}
    >
      {statusLabel(status)}
    </span>
  );
}

export function RiskScore({ score }: { score: number }) {
  const color =
    score >= 85
      ? "text-red-700"
      : score >= 65
        ? "text-orange-700"
        : score >= 40
          ? "text-amber-700"
          : "text-emerald-700";
  return (
    <span className={`font-mono text-sm font-semibold tabular-nums ${color}`}>{score}</span>
  );
}
