const STEPS = [
  { n: 1, label: "Upload", hint: "Invoice photo or PDF" },
  { n: 2, label: "Check", hint: "Gemini + vendor, PO & BIR checks" },
  { n: 3, label: "Decide", hint: "Ask the agent, approve or hold" },
];

export function Stepper({ current }: { current: 1 | 2 | 3 }) {
  return (
    <nav aria-label="Progress">
      <ol className="grid grid-cols-3 gap-2">
        {STEPS.map((s) => {
          const state = s.n < current ? "done" : s.n === current ? "current" : "todo";
          return (
            <li
              key={s.n}
              aria-current={state === "current" ? "step" : undefined}
              className={`rounded-lg border px-3 py-2 ${
                state === "current" ? "border-gold-400 bg-gold-50" : state === "done" ? "border-emerald-200 bg-emerald-50" : "border-slate-200 bg-white"
              }`}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                    state === "current" ? "bg-navy-950 text-gold-300" : state === "done" ? "bg-emerald-600 text-white" : "bg-slate-200 text-slate-700"
                  }`}
                  aria-hidden="true"
                >
                  {state === "done" ? "✓" : s.n}
                </span>
                <span className="text-sm font-semibold text-navy-950">{s.label}</span>
                <span className="sr-only">{state === "done" ? "(completed)" : state === "current" ? "(current step)" : ""}</span>
              </div>
              <p className="mt-0.5 hidden text-xs text-slate-600 sm:block">{s.hint}</p>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
