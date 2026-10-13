"use client";

import { useEffect, useState } from "react";

/** Animated checklist for long waits. Advances on a timer; `live` items (e.g. real agent tool calls) are shown as done. */
export function ProgressSteps({ steps, live, title, interval = 2600 }: { steps: string[]; live?: string[]; title: string; interval?: number }) {
  const [i, setI] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setI((x) => Math.min(x + 1, steps.length - 1)), interval);
    return () => clearInterval(t);
  }, [steps.length, interval]);
  const items = live && live.length ? live : steps;
  const cur = live && live.length ? live.length : i;
  return (
    <div role="status" aria-live="polite" className="rounded-xl border border-navy-100 bg-white p-4 shadow-sm">
      <div className="flex items-center gap-2 text-sm font-semibold text-navy-950">
        <svg className="h-4 w-4 animate-spin text-gold-500" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" opacity=".25" />
          <path d="M22 12a10 10 0 0 0-10-10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
        </svg>
        {title}
      </div>
      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-100" aria-hidden="true">
        <div className="is-indeterminate h-full w-2/5 rounded-full bg-gradient-to-r from-navy-700 via-gold-400 to-navy-700" />
      </div>
      <ol className="mt-3 space-y-1.5 text-sm">
        {items.map((s, k) => {
          const done = live && live.length ? true : k < cur;
          const now = !(live && live.length) && k === cur;
          return (
            <li key={k} className={`flex items-center gap-2 ${done ? "text-emerald-800" : now ? "font-medium text-navy-950" : "text-slate-500"}`}>
              <span aria-hidden="true" className="w-4 text-center">{done ? "✓" : now ? "›" : "·"}</span>
              {s}
            </li>
          );
        })}
        {live && live.length > 0 && (
          <li className="flex items-center gap-2 font-medium text-navy-950"><span aria-hidden="true" className="w-4 text-center">›</span>Writing grounded answer…</li>
        )}
      </ol>
    </div>
  );
}
