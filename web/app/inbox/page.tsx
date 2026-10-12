import Link from "next/link";
import { SeverityBadge, StatusBadge, RiskScore } from "@/components/SeverityBadge";
import { fetchCases, formatPHP, riskLabel } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function InboxPage() {
  let cases: Awaited<ReturnType<typeof fetchCases>> = [];
  let err: string | null = null;
  try {
    cases = await fetchCases();
  } catch (e) {
    err = e instanceof Error ? e.message : "Failed to load";
  }

  const open = cases.filter((c) => c.status === "open");
  const rest = cases.filter((c) => c.status !== "open");
  const ordered = [...open, ...rest];

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-navy-950">Case inbox</h1>
        <p className="mt-1 text-sm text-slate-600">
          Severity-ranked queue for AP analysts. Open high/critical items first.
        </p>
      </div>

      {err && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
          {err}
        </div>
      )}

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-2.5 font-medium">Severity</th>
              <th className="px-4 py-2.5 font-medium">Vendor / file</th>
              <th className="px-4 py-2.5 font-medium">Flags</th>
              <th className="px-4 py-2.5 font-medium">Total</th>
              <th className="px-4 py-2.5 font-medium">Score</th>
              <th className="px-4 py-2.5 font-medium">Status</th>
              <th className="px-4 py-2.5 font-medium">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {ordered.map((c) => (
              <tr key={c.id} className="hover:bg-slate-50/80">
                <td className="px-4 py-3">
                  <SeverityBadge severity={c.severity} />
                </td>
                <td className="px-4 py-3">
                  <Link href={`/cases/${c.id}`} className="font-medium text-navy-900 hover:underline">
                    {c.extraction.vendor || "Unknown vendor"}
                  </Link>
                  <div className="text-xs text-slate-400">
                    {c.extraction.invoice_number || "—"} · {c.filename}
                  </div>
                </td>
                <td className="px-4 py-3">
                  {c.risk_flags.length === 0 ? (
                    <span className="text-xs text-emerald-700">None</span>
                  ) : (
                    <div className="flex flex-wrap gap-1">
                      {c.risk_flags.map((f) => (
                        <span
                          key={f.code + f.title}
                          className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[10px] text-slate-700"
                        >
                          {riskLabel(f.code)}
                        </span>
                      ))}
                    </div>
                  )}
                </td>
                <td className="px-4 py-3 tabular-nums">
                  {formatPHP(c.extraction.total, c.extraction.currency)}
                </td>
                <td className="px-4 py-3">
                  <RiskScore score={c.overall_risk_score} />
                </td>
                <td className="px-4 py-3">
                  <StatusBadge status={c.status} />
                </td>
                <td className="px-4 py-3 text-xs text-slate-500 whitespace-nowrap">
                  {c.created_at.replace("T", " ").slice(0, 19)}
                </td>
              </tr>
            ))}
            {ordered.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-10 text-center text-slate-500">
                  Inbox empty.{" "}
                  <Link href="/upload" className="text-sky-700 hover:underline">
                    Upload an invoice
                  </Link>
                  .
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
