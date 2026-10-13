"use client";

import { useEffect, useRef, useState } from "react";
import { ProgressSteps } from "@/components/ProgressSteps";
import { AgentStep, askCaseStream, ChatMsg, draftEmail, EmailDraft, fetchChat } from "@/lib/api";

const LANGS = ["auto", "English", "Tagalog", "Taglish", "Cebuano", "Ilocano", "Bahasa Indonesia", "Bahasa Melayu", "Thai", "Vietnamese", "Japanese", "Korean", "Mandarin Chinese", "Hindi"];
const CHIPS = [
  "Is this safe to pay?",
  "What changed vs this vendor's past invoices?",
  "What should I verify first?",
  "Does this match the PO?",
];
const recTone: Record<string, string> = {
  PAY: "bg-emerald-100 text-emerald-800 ring-emerald-300",
  HOLD: "bg-red-100 text-red-800 ring-red-300",
  VERIFY: "bg-amber-100 text-amber-900 ring-amber-300",
};

function Md({ text }: { text: string }) {
  // tiny markdown: **bold**, bullet lines
  return (
    <div className="space-y-1">
      {text.split("\n").filter((l) => l.trim()).map((l, i) => {
        const bullet = /^\s*[-*•]\s+/.test(l);
        const html = l
          .replace(/^\s*[-*•]\s+/, "")
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
          .replace(/\[(E\d[^\]]*|IMG[^\]]*)\]/g, '<span class="rounded bg-sky-50 px-1 font-mono text-[10px] text-sky-700 ring-1 ring-sky-200">$1</span>');
        return (
          <p key={i} className={bullet ? "pl-3 before:-ml-3 before:mr-1.5 before:content-['•']" : ""} dangerouslySetInnerHTML={{ __html: html }} />
        );
      })}
    </div>
  );
}

function Steps({ steps }: { steps?: AgentStep[] }) {
  if (!steps?.length) return null;
  return (
    <details className="mt-2 rounded-md border border-slate-200 bg-white text-xs">
      <summary className="cursor-pointer select-none px-2 py-1 font-medium text-slate-600">
        Agent steps · Google ADK · {steps.length} tool call{steps.length > 1 ? "s" : ""}
      </summary>
      <ol className="space-y-1 border-t border-slate-100 px-2 py-1.5">
        {steps.map((s, i) => (
          <li key={i}>
            <span className="font-mono font-semibold text-navy-900">{i + 1}. {s.tool}</span>
            <span className="font-mono text-slate-500">({Object.entries(s.args || {}).map(([k, v]) => `${k}=${JSON.stringify(v)}`).join(", ")})</span>
            {s.result && <div className="ml-4 truncate font-mono text-[10px] text-slate-500" title={s.result}>→ {s.result}</div>}
          </li>
        ))}
      </ol>
    </details>
  );
}

const TOOL_LABEL: Record<string, string> = {
  get_case_evidence: "Reading case evidence (extraction, flags, score)",
  lookup_vendor: "Checking vendor master",
  lookup_po: "Looking up purchase order",
  validate_tin: "Validating TIN format",
  bir_checklist: "Running BIR checklist (RR 7-2024)",
  search_vendor_history: "Searching vendor history (duplicates, splits)",
  draft_verification_email: "Fetching contact on file",
};

export function AskCase({ caseId }: { caseId: string }) {
  const [msgs, setMsgs] = useState<ChatMsg[]>([]);
  const [q, setQ] = useState("");
  const [lang, setLang] = useState("auto");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [emailLang, setEmailLang] = useState("English");
  const [draft, setDraft] = useState<EmailDraft | null>(null);
  const [drafting, setDrafting] = useState(false);
  const [copied, setCopied] = useState(false);
  const end = useRef<HTMLDivElement>(null);
  const [live, setLive] = useState<string[]>([]);

  useEffect(() => {
    fetchChat(caseId).then(setMsgs).catch(() => {});
  }, [caseId]);
  useEffect(() => {
    end.current?.scrollIntoView({ block: "nearest" });
  }, [msgs, busy]);

  async function send(text: string) {
    if (!text.trim() || busy) return;
    setBusy(true);
    setErr("");
    setMsgs((m) => [...m, { role: "user", content: text, at: "" }]);
    setQ("");
    try {
      setLive([]);
      const r = await askCaseStream(caseId, text, lang, (st) => setLive((l) => [...l, `${TOOL_LABEL[st.tool] || st.tool}`]));
      setMsgs(r.history);
    } catch (e) {
      setMsgs((m) => m.slice(0, -1));
      setQ(text);
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function makeDraft() {
    setDrafting(true);
    setErr("");
    setCopied(false);
    try {
      setDraft(await draftEmail(caseId, emailLang));
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setDrafting(false);
    }
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-sm font-semibold text-navy-900">Ask the case <span className="font-normal text-slate-500">· Google ADK agent · Gemini + InvoiceSentinel tools</span></h2>
        <label className="text-xs text-slate-600">
          Reply language{" "}
          <select className="rounded border border-slate-300 px-1.5 py-0.5 text-xs" value={lang} onChange={(e) => setLang(e.target.value)}>
            {LANGS.map((l) => (
              <option key={l} value={l}>{l === "auto" ? "Auto (match my language)" : l}</option>
            ))}
          </select>
        </label>
      </div>

      <div className="mt-3 max-h-[32rem] space-y-3 overflow-y-auto" aria-live="polite" aria-label="Conversation">
        {msgs.length === 0 && !busy && (
          <p className="text-sm text-slate-500">Ask anything about this invoice — in English, Tagalog, Taglish, Cebuano, Bahasa, Thai, Vietnamese… Answers cite evidence: E1 extraction, E2 flags, E4 vendor master, E5 PO, E6 vendor history, IMG invoice image.</p>
        )}
        {msgs.map((m, i) =>
          m.role === "user" ? (
            <div key={i} className="ml-auto max-w-[85%] rounded-lg bg-navy-900 px-3 py-2 text-sm text-white">{m.content}</div>
          ) : (
            <div key={i} className="max-w-[95%] rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-800">
              {m.recommendation && (
                <span className={`mb-1.5 inline-flex rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${recTone[m.recommendation]}`}>
                  Recommendation: {m.recommendation}
                </span>
              )}
              <Md text={m.content} />
              {!!m.missing_info?.length && (
                <p className="mt-1.5 text-xs text-amber-800">Missing info: {m.missing_info.join("; ")}</p>
              )}
              {m.language && <p className="mt-1 text-[10px] text-slate-500">Language: {m.language}</p>}
              <Steps steps={m.agent_steps} />
            </div>
          )
        )}
        {busy && (
          <ProgressSteps
            title="ADK agent is investigating this case"
            live={live}
            steps={["Planning which checks to run…", "Calling tools…"]}
          />
        )}
        <div ref={end} />
      </div>

      <div className="mt-3 flex flex-wrap gap-1.5">
        {CHIPS.map((c) => (
          <button key={c} disabled={busy} onClick={() => send(c)} className="rounded-full border border-gold-300 bg-gold-50 px-2.5 py-1 text-xs text-navy-900 hover:bg-gold-100 disabled:opacity-50">
            {c}
          </button>
        ))}
      </div>
      <form className="mt-2 flex gap-2" onSubmit={(e) => { e.preventDefault(); send(q); }}>
        <label htmlFor="ask-input" className="sr-only">Ask a question about this case</label>
        <input id="ask-input" value={q} onChange={(e) => setQ(e.target.value)} placeholder="e.g. Ligtas ba itong bayaran?" className="flex-1 rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-sky-500 focus:outline-none" />
        <button disabled={busy || !q.trim()} className="rounded-md bg-navy-950 px-3 py-1.5 text-sm font-semibold text-white hover:bg-navy-800 disabled:opacity-50">Ask</button>
      </form>
      {err && <p className="mt-2 rounded-md bg-red-50 px-3 py-2 text-xs text-red-700">{err}</p>}

      <div className="mt-4 border-t border-slate-100 pt-3">
        <div className="flex flex-wrap items-center gap-2">
          <button onClick={makeDraft} disabled={drafting} className="rounded-md bg-navy-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-navy-800 disabled:opacity-50">
            {drafting ? "Drafting…" : "Draft verification email"}
          </button>
          <select aria-label="Email language" className="rounded border border-slate-300 px-1.5 py-1 text-xs" value={emailLang} onChange={(e) => setEmailLang(e.target.value)}>
            {LANGS.filter((l) => l !== "auto").map((l) => <option key={l}>{l}</option>)}
          </select>
          <span className="text-[11px] text-slate-500">Uses the contact on file in the vendor master — never the invoice’s. Nothing is sent.</span>
        </div>
        {drafting && (
          <div className="mt-3">
            <ProgressSteps
              title="ADK agent is drafting"
              interval={3500}
              steps={["Reading case evidence…", "Fetching the vendor contact on file…", "Checking vendor master & PO…", "Writing the message…"]}
            />
          </div>
        )}
        {draft && (
          <div className="mt-3 rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm">
            <div className="flex items-start justify-between gap-2">
              <div className="text-xs text-slate-600">
                <span className={`mr-1 rounded px-1.5 py-0.5 font-semibold ${draft.kind === "internal_escalation" ? "bg-red-100 text-red-800" : "bg-emerald-100 text-emerald-800"}`}>
                  {draft.kind === "internal_escalation" ? "Internal escalation memo (vendor not in master)" : "Vendor verification email"}
                </span>
                To: {draft.to}
              </div>
              <button
                onClick={async () => { await navigator.clipboard.writeText(`Subject: ${draft.subject}\n\n${draft.body}`); setCopied(true); }}
                className="rounded border border-slate-300 bg-white px-2 py-0.5 text-xs hover:bg-slate-100"
              >
                {copied ? "Copied ✓" : "Copy"}
              </button>
            </div>
            <p className="mt-2 font-semibold text-navy-900">Subject: {draft.subject}</p>
            <pre className="mt-1 whitespace-pre-wrap font-sans text-sm text-slate-700">{draft.body}</pre>
            <Steps steps={draft.agent_steps} />
          </div>
        )}
      </div>
    </section>
  );
}
