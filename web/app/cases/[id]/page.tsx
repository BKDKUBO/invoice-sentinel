import Link from "next/link";
import { notFound } from "next/navigation";
import { CaseActions } from "@/components/CaseActions";
import { SeverityBadge, StatusBadge, RiskScore } from "@/components/SeverityBadge";
import { fetchCase, formatPHP, riskLabel } from "@/lib/api";
import { severityBadge } from "@/lib/ui";

export const dynamic = "force-dynamic";

export default async function CaseDetailPage({ params }: { params: { id: string } }) {
  let c: Awaited<ReturnType<typeof fetchCase>>;
  try {
    c = await fetchCase(params.id);
  } catch {
    notFound();
  }

  const ex = c.extraction;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link href="/inbox" className="text-xs font-medium text-sky-700 hover:underline">
            ← Back to inbox
          </Link>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-navy-950">
            {ex.vendor || "Case detail"}
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            {c.id} · {c.filename} · source {c.source}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <SeverityBadge severity={c.severity} />
          <StatusBadge status={c.status} />
          <span className="rounded-full bg-white px-2.5 py-1 text-xs ring-1 ring-slate-200">
            Risk score <RiskScore score={c.overall_risk_score} />
          </span>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="text-sm font-semibold text-navy-900">Extracted fields</h2>
            <dl className="mt-3 grid gap-3 sm:grid-cols-2">
              {[
                ["Vendor", ex.vendor],
                ["TIN", ex.vendor_tin || "—"],
                ["Invoice #", ex.invoice_number || "—"],
                ["Date", ex.date || "—"],
                ["Currency", ex.currency],
                ["Subtotal", formatPHP(ex.subtotal, ex.currency)],
                ["Tax", formatPHP(ex.tax, ex.currency)],
                ["Total", formatPHP(ex.total, ex.currency)],
              ].map(([k, v]) => (
                <div key={k as string} className="rounded-lg bg-slate-50 px-3 py-2">
                  <dt className="text-[10px] font-medium uppercase tracking-wide text-slate-500">
                    {k}
                  </dt>
                  <dd className="mt-0.5 text-sm font-medium text-navy-900">{v}</dd>
                </div>
              ))}
            </dl>
            {ex.summary && (
              <p className="mt-3 rounded-lg border border-slate-100 bg-slate-50/80 px-3 py-2 text-sm text-slate-700">
                {ex.summary}
              </p>
            )}
          </section>

          <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="text-sm font-semibold text-navy-900">Line items</h2>
            <div className="mt-2 overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="text-xs uppercase text-slate-500">
                  <tr>
                    <th className="py-1.5 pr-3 font-medium">Description</th>
                    <th className="py-1.5 pr-3 font-medium">Qty</th>
                    <th className="py-1.5 pr-3 font-medium">Unit</th>
                    <th className="py-1.5 font-medium">Amount</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {(ex.line_items || []).map((li, i) => (
                    <tr key={i}>
                      <td className="py-2 pr-3">{li.description}</td>
                      <td className="py-2 pr-3 tabular-nums">{li.qty}</td>
                      <td className="py-2 pr-3 tabular-nums">
                        {formatPHP(li.unit_price, ex.currency)}
                      </td>
                      <td className="py-2 tabular-nums">{formatPHP(li.amount, ex.currency)}</td>
                    </tr>
                  ))}
                  {(ex.line_items || []).length === 0 && (
                    <tr>
                      <td colSpan={4} className="py-4 text-slate-500">
                        No line items extracted.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="text-sm font-semibold text-navy-900">Explainable risk cards</h2>
            {c.risk_flags.length === 0 ? (
              <p className="mt-3 text-sm text-emerald-700">
                No risk flags — routine AP review recommended.
              </p>
            ) : (
              <ul className="mt-3 space-y-3">
                {c.risk_flags.map((f, i) => (
                  <li
                    key={i}
                    className="rounded-lg border border-slate-200 bg-slate-50/50 p-3"
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <span
                        className={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ring-1 ring-inset ${severityBadge(
                          f.severity
                        )}`}
                      >
                        {f.severity}
                      </span>
                      <span className="rounded bg-white px-1.5 py-0.5 font-mono text-[10px] text-slate-600 ring-1 ring-slate-200">
                        {riskLabel(f.code)}
                      </span>
                      <span className="text-sm font-semibold text-navy-900">{f.title}</span>
                    </div>
                    <p className="mt-2 text-sm text-slate-700">{f.explanation}</p>
                    {f.evidence && (
                      <p className="mt-1 font-mono text-[11px] text-slate-500">
                        Evidence: {f.evidence}
                      </p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>

        <div className="space-y-4">
          <CaseActions caseId={c.id} status={c.status} />

          <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 className="text-sm font-semibold text-navy-900">Audit trail</h3>
            <ol className="mt-3 space-y-3 border-l border-slate-200 pl-3">
              {(c.audit_log || []).map((a, i) => (
                <li key={i} className="relative">
                  <span className="absolute -left-[17px] top-1.5 h-2 w-2 rounded-full bg-navy-400" />
                  <div className="text-xs font-medium text-navy-900">
                    {a.action}{" "}
                    <span className="font-normal text-slate-500">by {a.actor}</span>
                  </div>
                  <div className="text-[11px] text-slate-400">{a.at}</div>
                  {a.note && <div className="mt-0.5 text-xs text-slate-600">{a.note}</div>}
                </li>
              ))}
            </ol>
          </section>

          <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
            <strong>Disclaimer:</strong> InvoiceSentinel supports AP risk triage before payment. It
            does not certify BIR compliance and does not replace tax-authority systems.
          </div>
        </div>
      </div>
    </div>
  );
}
