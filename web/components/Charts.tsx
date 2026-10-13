import type { Analytics } from "@/lib/api";
import { formatPHP, riskLabel } from "@/lib/api";

const SEV_COLORS: Record<string, string> = { low: "#059669", medium: "#c99a12", high: "#ea580c", critical: "#be123c" };

export function FlagBreakdown({ a }: { a: Analytics }) {
  const max = Math.max(1, ...a.flags.map((f) => f.count));
  return (
    <section aria-labelledby="flag-h" className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h2 id="flag-h" className="text-sm font-semibold text-navy-950">Flag breakdown</h2>
      {a.flags.length === 0 ? (
        <p className="mt-3 text-sm text-slate-600">No flags yet.</p>
      ) : (
        <ul className="mt-3 space-y-2">
          {a.flags.slice(0, 8).map((f) => (
            <li key={f.code} className="grid grid-cols-[8.5rem_1fr_2rem] items-center gap-2 text-sm">
              <span className="truncate text-slate-700" title={f.code}>{riskLabel(f.code)}</span>
              <span className="h-2.5 rounded-full bg-slate-100" aria-hidden="true">
                <span className="block h-2.5 rounded-full bg-gradient-to-r from-navy-700 to-gold-400" style={{ width: `${(f.count / max) * 100}%` }} />
              </span>
              <span className="text-right font-semibold tabular-nums text-navy-950">{f.count}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export function SeverityMix({ a }: { a: Analytics }) {
  const order = ["critical", "high", "medium", "low"] as const;
  const total = order.reduce((s, k) => s + (a.severity[k] || 0), 0) || 1;
  let acc = 0;
  const R = 34, C = 2 * Math.PI * R;
  return (
    <section aria-labelledby="sev-h" className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h2 id="sev-h" className="text-sm font-semibold text-navy-950">Severity mix</h2>
      <div className="mt-2 flex items-center gap-4">
        <svg viewBox="0 0 90 90" className="h-24 w-24 shrink-0 -rotate-90" role="img" aria-label={order.map((k) => `${k} ${a.severity[k] || 0}`).join(", ")}>
          <circle cx="45" cy="45" r={R} fill="none" stroke="#e2e8f0" strokeWidth="12" />
          {order.map((k) => {
            const v = (a.severity[k] || 0) / total;
            const el = <circle key={k} cx="45" cy="45" r={R} fill="none" stroke={SEV_COLORS[k]} strokeWidth="12" strokeDasharray={`${v * C} ${C}`} strokeDashoffset={-acc * C} />;
            acc += v;
            return el;
          })}
        </svg>
        <ul className="space-y-1 text-sm">
          {order.map((k) => (
            <li key={k} className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full" style={{ background: SEV_COLORS[k] }} aria-hidden="true" />
              <span className="capitalize text-slate-700">{k}</span>
              <span className="font-semibold tabular-nums text-navy-950">{a.severity[k] || 0}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

export function RiskTrend({ a }: { a: Analytics }) {
  const W = 420, H = 120, pad = 18;
  const max = Math.max(1, ...a.trend.map((d) => d.cases));
  const bw = (W - pad * 2) / a.trend.length;
  const risk = a.trend.reduce((s, d) => s + d.at_risk, 0);
  return (
    <section aria-labelledby="trend-h" className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-baseline justify-between gap-2">
        <h2 id="trend-h" className="text-sm font-semibold text-navy-950">Risk trend · last 14 days</h2>
        <span className="text-xs text-slate-600">{formatPHP(risk)} flagged high/critical</span>
      </div>
      <svg viewBox={`0 0 ${W} ${H + 16}`} className="mt-2 max-h-44 w-full" role="img"
        aria-label={`Cases per day over 14 days; ${a.trend.reduce((s, d) => s + d.cases, 0)} cases, ${a.trend.reduce((s, d) => s + d.flagged, 0)} flagged high or critical`}>
        <line x1={pad} y1={H} x2={W - pad} y2={H} stroke="#cbd5e1" />
        {a.trend.map((d, i) => {
          const h = (d.cases / max) * (H - 10), hf = (d.flagged / max) * (H - 10);
          const x = pad + i * bw + 3;
          return (
            <g key={d.date}>
              <rect x={x} y={H - h} width={bw - 6} height={h} rx="2" fill="#bcccdc"><title>{`${d.date}: ${d.cases} cases, ${d.flagged} flagged`}</title></rect>
              <rect x={x} y={H - hf} width={bw - 6} height={hf} rx="2" fill="#be123c" />
              {i % 2 === 0 && <text x={x + (bw - 6) / 2} y={H + 12} fontSize="8" textAnchor="middle" fill="#475569">{d.date.slice(5)}</text>}
            </g>
          );
        })}
      </svg>
      {a.trend.every((d) => d.cases === 0) && <p className="-mt-16 mb-10 text-center text-sm text-slate-600">No invoices checked in the last 14 days — try a sample.</p>}
      <p className="mt-1 flex gap-3 text-xs text-slate-600">
        <span><span className="mr-1 inline-block h-2 w-2 rounded-sm bg-[#bcccdc]" aria-hidden="true" />All cases</span>
        <span><span className="mr-1 inline-block h-2 w-2 rounded-sm bg-[#be123c]" aria-hidden="true" />High / critical</span>
      </p>
    </section>
  );
}
