"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { analyzeFile } from "@/lib/api";

export function UploadDropzone() {
  const router = useRouter();
  const [drag, setDrag] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<string | null>(null);

  const onFiles = useCallback(
    async (files: FileList | null) => {
      if (!files?.length) return;
      const file = files[0];
      setError(null);
      setBusy(true);
      try {
        const res = await analyzeFile(file);
        setMode(res.mode);
        router.push(`/cases/${res.case.id}`);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Upload failed");
        setBusy(false);
      }
    },
    [router]
  );

  return (
    <div className="space-y-4">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          void onFiles(e.dataTransfer.files);
        }}
        className={`relative flex min-h-[220px] flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-12 text-center transition ${
          drag
            ? "border-sky-500 bg-sky-50"
            : "border-slate-300 bg-white hover:border-navy-400 hover:bg-slate-50"
        }`}
      >
        <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-navy-50 text-navy-700 ring-1 ring-navy-100">
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
          </svg>
        </div>
        <p className="text-sm font-medium text-navy-900">
          Drag & drop invoice PDF or image
        </p>
        <p className="mt-1 text-xs text-slate-500">PDF, PNG, JPG · max 20MB</p>
        <label className="mt-4 cursor-pointer rounded-lg bg-navy-900 px-4 py-2 text-sm font-medium text-white hover:bg-navy-800">
          {busy ? "Analyzing…" : "Choose file"}
          <input
            type="file"
            accept=".pdf,.png,.jpg,.jpeg,.webp,application/pdf,image/*"
            className="hidden"
            disabled={busy}
            onChange={(e) => void onFiles(e.target.files)}
          />
        </label>
        {busy && (
          <p className="mt-3 text-xs text-slate-500">
            Running multimodal extraction & risk flags…
          </p>
        )}
      </div>
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
          {error}
        </div>
      )}
      {mode && (
        <p className="text-xs text-slate-500">
          Analyzer mode: <span className="font-mono font-medium">{mode}</span>
        </p>
      )}
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs text-slate-600">
        <p className="font-semibold text-slate-800">Demo tip (no API key)</p>
        <p className="mt-1">
          Name files with <code className="rounded bg-white px-1 ring-1 ring-slate-200">ghost</code>,{" "}
          <code className="rounded bg-white px-1 ring-1 ring-slate-200">duplicate</code>, or{" "}
          <code className="rounded bg-white px-1 ring-1 ring-slate-200">math</code> to trigger mock
          risk patterns. Or walk the seeded cases in the inbox.
        </p>
      </div>
    </div>
  );
}
