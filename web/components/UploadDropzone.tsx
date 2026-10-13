"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { analyzeFile, analyzeSample, API_URL, fetchSamples, type Sample } from "@/lib/api";
import { ProgressSteps } from "@/components/ProgressSteps";
import { Stepper } from "@/components/Stepper";

const ANALYSIS_STEPS = [
  "Reading invoice with Gemini (multimodal)…",
  "Extracting vendor, TIN, line items and pay-to account…",
  "Checking vendor master and verified bank accounts…",
  "Matching purchase order (qty, unit price, 5% tolerance)…",
  "Running BIR checklist (RR 7-2024) and TIN validation…",
  "Searching vendor history for duplicates and split invoices…",
  "Scoring risk and opening the case…",
];

export function UploadDropzone() {
  const router = useRouter();
  const [drag, setDrag] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [samples, setSamples] = useState<Sample[]>([]);
  const retry = useRef<(() => void) | null>(null);

  useEffect(() => {
    fetchSamples().then(setSamples).catch(() => setSamples([]));
  }, []);

  const run = useCallback(
    async (label: string, fn: () => Promise<{ case: { id: string } }>) => {
      setError(null);
      setBusy(label);
      retry.current = () => void run(label, fn);
      try {
        const res = await fn();
        router.push(`/cases/${res.case.id}`);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Upload failed");
        setBusy(null);
      }
    },
    [router]
  );

  const onFiles = (files: FileList | null) => {
    const f = files?.[0];
    if (f) void run(f.name, () => analyzeFile(f));
  };

  return (
    <div className="space-y-5">
      <Stepper current={busy ? 2 : 1} />

      {busy ? (
        <ProgressSteps title={`Checking ${busy}`} steps={ANALYSIS_STEPS} />
      ) : (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDrag(true);
          }}
          onDragLeave={() => setDrag(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDrag(false);
            onFiles(e.dataTransfer.files);
          }}
          className={`flex min-h-[200px] flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-10 text-center transition ${
            drag ? "border-gold-400 bg-gold-50" : "border-slate-300 bg-white hover:border-navy-400"
          }`}
        >
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-navy-950 text-gold-300" aria-hidden="true">
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
            </svg>
          </div>
          <p className="text-sm font-semibold text-navy-950">Drag & drop an invoice or receipt</p>
          <p className="mt-1 text-xs text-slate-600">PDF, PNG, JPG · max 20 MB · phone photos are fine</p>
          <label className="mt-4 cursor-pointer rounded-lg bg-navy-950 px-4 py-2 text-sm font-semibold text-white hover:bg-navy-800 focus-within:outline focus-within:outline-[3px] focus-within:outline-gold-400">
            Choose file
            <input type="file" accept=".pdf,.png,.jpg,.jpeg,.webp,application/pdf,image/*" className="sr-only" onChange={(e) => onFiles(e.target.files)} />
          </label>
        </div>
      )}

      {error && (
        <div role="alert" className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
          {error}
          <button type="button" onClick={() => retry.current?.()} className="ml-2 font-semibold underline">
            Retry
          </button>
        </div>
      )}

      {samples.length > 0 && (
        <section aria-labelledby="try-sample" className="rounded-2xl border border-gold-200 bg-white p-4 shadow-sm">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h2 id="try-sample" className="text-sm font-semibold text-navy-950">
              <span className="mr-1.5 rounded bg-gold-300 px-1.5 py-0.5 text-[10px] font-bold uppercase text-navy-950">Judges</span>
              Try a sample — one click
            </h2>
            <p className="text-xs text-slate-600">Fictional PH invoices bundled with the app</p>
          </div>
          <ul className="mt-3 grid gap-2 sm:grid-cols-2">
            {samples.map((s) => (
              <li key={s.name}>
                <button
                  type="button"
                  disabled={!!busy}
                  onClick={() => void run(s.name, () => analyzeSample(s.name))}
                  className="flex w-full items-center gap-3 rounded-lg border border-slate-200 p-2 text-left hover:border-gold-400 hover:bg-gold-50 disabled:opacity-50"
                  aria-label={`Analyze sample ${s.name}: ${s.description}`}
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={`${API_URL}${s.url}`} alt="" className="h-12 w-10 shrink-0 rounded border border-slate-200 object-cover object-top" loading="lazy" />
                  <span>
                    <span className="block font-mono text-[11px] text-slate-600">{s.name.split("-")[0]}</span>
                    <span className="block text-sm font-medium text-navy-950">{s.description}</span>
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
