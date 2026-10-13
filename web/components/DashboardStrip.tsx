import type { DashboardStats } from "@/lib/api";
import { formatPHP } from "@/lib/api";

export function DashboardStrip({ stats }: { stats: DashboardStats }) {
  const cards = [
    { label: "₱ at risk (open)", value: formatPHP(stats.amount_at_risk, stats.currency), hint: `${stats.high_critical_open} high/critical cases awaiting a decision`, accent: true },
    { label: "Open cases", value: String(stats.open_count), hint: "Awaiting decision" },
    { label: "Checked this week", value: String(stats.cases_this_week), hint: "Ingested last 7 days" },
    { label: "Approved", value: String(stats.approved_count), hint: "Cleared for payment" },
    { label: "Escalated / docs", value: `${stats.escalated_count} / ${stats.docs_requested_count}`, hint: "Held for review" },
  ];
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
      {cards.map((c) => (
        <div
          key={c.label}
          className={`rounded-xl p-4 shadow-sm ${c.accent ? "bg-navy-950 text-white ring-1 ring-gold-400 sm:col-span-2 lg:col-span-1" : "border border-slate-200 bg-white"}`}
        >
          <div className={`text-xs font-semibold uppercase tracking-wide ${c.accent ? "text-gold-200" : "text-slate-600"}`}>{c.label}</div>
          <div className={`mt-1 text-2xl font-bold tracking-tight tabular-nums ${c.accent ? "text-gold-300" : "text-navy-950"}`}>{c.value}</div>
          <div className={`mt-1 text-xs ${c.accent ? "text-navy-100" : "text-slate-600"}`}>{c.hint}</div>
        </div>
      ))}
    </div>
  );
}
