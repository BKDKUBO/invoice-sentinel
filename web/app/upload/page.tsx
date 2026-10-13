import { UploadDropzone } from "@/components/UploadDropzone";

export default function UploadPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-5">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-navy-950">Check an invoice</h1>
        <p className="mt-1 text-sm text-slate-600">
          Upload a supplier invoice before you pay it. Gemini reads it, then InvoiceSentinel checks the vendor master, purchase
          order, BIR invoice elements and payment history — you decide with the evidence in front of you.
        </p>
      </div>
      <UploadDropzone />
    </div>
  );
}
