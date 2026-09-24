import Link from "next/link";
import { DashboardStrip } from "@/components/DashboardStrip";
import { ResetDemoButton } from "@/components/ResetDemoButton";
import { SeverityBadge, StatusBadge, RiskScore } from "@/components/SeverityBadge";
import { fetchCases, fetchDashboard, fetchHealth, formatPHP, API_URL } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  let stats = null;
  let cases: Awaited<ReturnType<typeof fetchCases>> = [];
  let health = null;
  let err: string | null = null;

  try {
    [stats, cases, health] = await Promise.all([fetchDashboard(), fetchCases(), fetchHealth()]);
  } catch (e) {
    err = e instanceof Error ? e.message : "API unreachable";
  }

  const recent = cases.slice(0, 6);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-navy-950">AP risk desk</h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-600">
            Multimodal invoice triage for Philippine SMEs — flag ghost receipts, duplicates, and
            amount anomalies before payment. Human decisions stay on the audit trail.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {health && (
            <span className="rounded-full bg-white px-2.5 py-1 text-xs font-medium text-slate-600 ring-1 ring-slate-200">
              API {health.status} · mode{" "}
              <span className="font-mono text-navy-800">{health.mode}</span>
              {health.gemini_configured ? ` · ${health.gemini_model}` : " · no GEMINI_API_KEY"}
            </span>
          )}
          <ResetDemoButton />
          <Link
            href="/upload"
            className="rounded-lg bg-navy-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-navy-800"
          >
            Upload invoice
          </Link>
        </div>
      </div>

      {err && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          Cannot reach API at <code className="font-mono">{API_URL}</code>: {err}. Start the FastAPI
          server on port 8080.
        </div>
      )}

      {stats && <DashboardStrip stats={stats} />}

      <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
          <h2 className="text-sm font-semibold text-navy-900">Recent cases</h2>
          <Link href="/inbox" className="text-xs font-medium text-sky-700 hover:underline">
            Open inbox →
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-2 font-medium">Vendor</th>
                <th className="px-4 py-2 font-medium">Invoice #</th>
                <th className="px-4 py-2 font-medium">Total</th>
                <th className="px-4 py-2 font-medium">Score</th>
                <th className="px-4 py-2 font-medium">Severity</th>
                <th className="px-4 py-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {recent.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                    No cases yet.
                  </td>
                </tr>
              )}
              {recent.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50/80">
                  <td className="px-4 py-3">
                    <Link href={`/cases/${c.id}`} className="font-medium text-navy-900 hover:underline">
                      {c.extraction.vendor || "—"}
                    </Link>
                    <div className="text-xs text-slate-400">{c.filename}</div>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs">{c.extraction.invoice_number || "—"}</td>
                  <td className="px-4 py-3 tabular-nums">
                    {formatPHP(c.extraction.total, c.extraction.currency)}
                  </td>
                  <td className="px-4 py-3">
                    <RiskScore score={c.overall_risk_score} />
                  </td>
                  <td className="px-4 py-3">
                    <SeverityBadge severity={c.severity} />
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={c.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
