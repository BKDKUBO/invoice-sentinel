import type { Matching } from "@/lib/api";

const icon = { pass: "✓", fail: "✕", info: "•" } as const;
const tone = {
  pass: "text-emerald-700 bg-emerald-50 ring-emerald-200",
  fail: "text-red-700 bg-red-50 ring-red-200",
  info: "text-slate-600 bg-slate-50 ring-slate-200",
} as const;

export function MatchingPanel({ m }: { m: Matching | null }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="text-sm font-semibold text-navy-900">Matched against vendor master / PO</h2>
      {!m ? (
        <p className="mt-2 text-sm text-slate-500">Matching unavailable.</p>
      ) : (
        <>
          <p className="mt-1 text-xs text-slate-500">
            Vendor: {m.vendor_match ? `${m.vendor_match.name} (${m.vendor_match.id}, matched by ${m.vendor_match.how})` : "no match in master"}
            {" · "}PO: {m.po_match ? m.po_match.po_number : "none"}
            {m.live && " · computed live (case predates vendor master)"}
          </p>
          <div className="mt-3 overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="text-xs uppercase text-slate-500">
                <tr>
                  <th className="py-1.5 pr-3 font-medium">Check</th>
                  <th className="py-1.5 pr-3 font-medium">Expected (master / PO)</th>
                  <th className="py-1.5 font-medium">Found on invoice</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {m.checks.map((c, i) => (
                  <tr key={i} className="align-top">
                    <td className="py-2 pr-3">
                      <span className={`mr-2 inline-flex h-5 w-5 items-center justify-center rounded-full text-xs font-bold ring-1 ${tone[c.status]}`}>
                        {icon[c.status]}
                      </span>
                      {c.label}
                    </td>
                    <td className="py-2 pr-3 text-xs text-slate-600">{c.expected}</td>
                    <td className={`py-2 text-xs ${c.status === "fail" ? "font-semibold text-red-700" : "text-slate-700"}`}>{c.found}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
}
