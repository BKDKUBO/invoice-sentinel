"use client";

import { useEffect, useState } from "react";
import { fetchSettings, saveSettings, Settings } from "@/lib/api";

export function SettingsCard() {
  const [s, setS] = useState<Settings | null>(null);
  const [msg, setMsg] = useState("");
  useEffect(() => {
    fetchSettings().then(setS).catch((e) => setMsg(String(e)));
  }, []);
  if (!s) return null;
  const inp = "w-32 rounded-md border border-slate-300 px-2 py-1 text-sm";
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="text-sm font-semibold text-navy-900">Approval settings (split-invoice detection)</h2>
      <div className="mt-2 flex flex-wrap items-end gap-4 text-xs text-slate-600">
        <label>Approval limit (₱)<br /><input type="number" className={inp} value={s.approval_limit} onChange={(e) => setS({ ...s, approval_limit: Number(e.target.value) })} /></label>
        <label>Window (days)<br /><input type="number" className={inp} value={s.split_window_days} onChange={(e) => setS({ ...s, split_window_days: Number(e.target.value) })} /></label>
        <label>“Just under limit” band (%)<br /><input type="number" className={inp} value={s.near_limit_pct} onChange={(e) => setS({ ...s, near_limit_pct: Number(e.target.value) })} /></label>
        <button
          className="rounded-md bg-sky-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-sky-700"
          onClick={async () => {
            try { setS(await saveSettings(s)); setMsg("Saved ✓"); } catch (e) { setMsg(e instanceof Error ? e.message : String(e)); }
          }}
        >
          Save
        </button>
        {msg && <span>{msg}</span>}
      </div>
      <p className="mt-2 text-[11px] text-slate-500">Flags SPLIT_INVOICE when the same vendor bills 2+ invoices within the window, each under the limit but together above it (or all just under the limit).</p>
    </section>
  );
}
