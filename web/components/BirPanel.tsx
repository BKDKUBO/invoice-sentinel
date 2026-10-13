import type { BirInfo } from "@/lib/api";

const tone: Record<string, [string, string]> = {
  present: ["✓", "text-emerald-700 bg-emerald-50 ring-emerald-200"],
  missing: ["✕", "text-red-700 bg-red-50 ring-red-200"],
  invalid: ["!", "text-red-700 bg-red-50 ring-red-200"],
  unreadable: ["?", "text-amber-800 bg-amber-50 ring-amber-200"],
  advisory: ["–", "text-slate-500 bg-slate-50 ring-slate-200"],
};

export function BirPanel({ b }: { b: BirInfo | null }) {
  if (!b) return null;
  const c = b.checklist;
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-sm font-semibold text-navy-900">BIR compliance checklist <span className="font-normal text-slate-500">· RR 7-2024 (EOPT Act)</span></h2>
        <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ring-1 ${b.tin.valid ? tone.present[1] : tone.missing[1]}`}>
          TIN {b.tin.value || "—"}: {b.tin.reason}
        </span>
      </div>
      {!c ? (
        <p className="mt-2 text-sm text-slate-500">Checklist not extracted for this case (seed/legacy case). TIN format check shown above.</p>
      ) : (
        <>
          <p className="mt-1 text-xs text-slate-500">
            Document: {c.document_type || "—"} · Seller {c.seller_vat_registered ? "VAT-registered" : "non-VAT"} ·{" "}
            {c.missing.length ? <span className="font-semibold text-red-700">{c.missing.length} required element(s) missing/invalid</span> : <span className="font-semibold text-emerald-700">all required elements present</span>}
          </p>
          <ul className="mt-3 grid gap-1.5 sm:grid-cols-2">
            {c.items.map((i) => (
              <li key={i.key} className="flex items-start gap-2 text-sm">
                <span className={`mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-xs font-bold ring-1 ${tone[i.status]?.[1]}`}>{tone[i.status]?.[0]}</span>
                <span>
                  <span className={i.status === "missing" || i.status === "invalid" ? "font-semibold text-red-700" : "text-slate-800"}>{i.label}</span>
                  <span className="ml-1 text-[10px] text-slate-500">{i.ref}</span>
                  {i.note && <span className="block text-[11px] text-slate-500">{i.note}</span>}
                </span>
              </li>
            ))}
          </ul>
        </>
      )}
      <p className="mt-3 text-[11px] text-slate-500">Format check only — not a BIR certification. Verify registration via BIR ORUS / Form 2303.</p>
    </section>
  );
}
