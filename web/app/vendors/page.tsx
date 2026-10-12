import { VendorsManager } from "@/components/VendorsManager";

export const dynamic = "force-dynamic";

export default function VendorsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-navy-950">Vendors &amp; purchase orders</h1>
        <p className="mt-1 text-sm text-slate-500">
          Every invoice is checked against this approved-vendor master (TIN, verified bank/GCash account) and the
          purchase orders it cites (qty, unit price, subtotal, 5% tolerance). Demo data is fictional; “Reset seed demo”
          restores it.
        </p>
      </div>
      <VendorsManager />
    </div>
  );
}
