import { UploadDropzone } from "@/components/UploadDropzone";

export default function UploadPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-navy-950">Upload invoice</h1>
        <p className="mt-1 text-sm text-slate-600">
          Send PDF or image bytes to the analyzer. With{" "}
          <code className="rounded bg-slate-100 px-1 text-xs">GEMINI_API_KEY</code> set, Gemini
          extracts structured fields and risk flags. Without a key, mock heuristics still power the
          full demo.
        </p>
      </div>
      <UploadDropzone />
    </div>
  );
}
