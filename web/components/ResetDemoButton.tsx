"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { resetDemo } from "@/lib/api";

export function ResetDemoButton() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);

  return (
    <button
      type="button"
      disabled={busy}
      onClick={async () => {
        setBusy(true);
        try {
          await resetDemo();
          router.refresh();
        } finally {
          setBusy(false);
        }
      }}
      className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
    >
      {busy ? "Resetting…" : "Reset seed demo"}
    </button>
  );
}
