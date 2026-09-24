import type { DashboardStats } from "@/lib/api";
import { formatPHP } from "@/lib/api";

export function DashboardStrip({ stats }: { stats: DashboardStats }) {
  const cards = [
    { label: "Cases this week", value: String(stats.cases_this_week), hint: "Ingested last 7 days" },
    {
      label: "₱ at risk",
      value: formatPHP(stats.amount_at_risk, stats.currency),
      hint: `${stats.high_critical_open} high/critical open`,
      accent: true,
    },
    { label: "Open", value: String(stats.open_count), hint: "Awaiting decision" },
    { label: "Approved", value: String(stats.approved_count), hint: "Cleared for payment path" },
    { label: "Escalated", value: String(stats.escalated_count), hint: "Fraud / finance review" },
  ];

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
      {cards.map((c) => (
        <div
          key={c.label}
          className={`rounded-xl border bg-white p-4 shadow-sm ${
            c.accent ? "border-orange-200 ring-1 ring-orange-100" : "border-slate-200"
          }`}
        >
          <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{c.label}</div>
          <div className={`mt-1 text-2xl font-semibold tracking-tight ${c.accent ? "text-orange-800" : "text-navy-900"}`}>
            {c.value}
          </div>
          <div className="mt-1 text-xs text-slate-500">{c.hint}</div>
        </div>
      ))}
    </div>
  );
}
