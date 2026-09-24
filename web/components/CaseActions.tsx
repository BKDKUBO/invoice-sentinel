"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { postAction, type Case } from "@/lib/api";

export function CaseActions({ caseId, status }: { caseId: string; status: Case["status"] }) {
  const router = useRouter();
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run(action: "approve" | "escalate" | "request_docs") {
    setBusy(action);
    setError(null);
    try {
      await postAction(caseId, action, note);
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Action failed");
    } finally {
      setBusy(null);
    }
  }

  const disabled = status !== "open" || !!busy;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-navy-900">Human-in-the-loop decision</h3>
      <p className="mt-1 text-xs text-slate-500">
        Approve for payment path, escalate to fraud/finance, or request supporting documents.
        Actions append to the audit trail.
      </p>
      <textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="Optional note for audit log…"
        rows={2}
        disabled={status !== "open"}
        className="mt-3 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-100 disabled:bg-slate-50"
      />
      <div className="mt-3 flex flex-wrap gap-2">
        <button
          type="button"
          disabled={disabled}
          onClick={() => void run("approve")}
          className="rounded-lg bg-emerald-700 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-600 disabled:opacity-50"
        >
          {busy === "approve" ? "…" : "Approve"}
        </button>
        <button
          type="button"
          disabled={disabled}
          onClick={() => void run("escalate")}
          className="rounded-lg bg-red-700 px-3 py-2 text-sm font-medium text-white hover:bg-red-600 disabled:opacity-50"
        >
          {busy === "escalate" ? "…" : "Escalate"}
        </button>
        <button
          type="button"
          disabled={disabled}
          onClick={() => void run("request_docs")}
          className="rounded-lg bg-sky-700 px-3 py-2 text-sm font-medium text-white hover:bg-sky-600 disabled:opacity-50"
        >
          {busy === "request_docs" ? "…" : "Request docs"}
        </button>
      </div>
      {status !== "open" && (
        <p className="mt-2 text-xs text-slate-500">
          Case already decided ({status}). Reset demo from dashboard to replay.
        </p>
      )}
      {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
    </div>
  );
}
