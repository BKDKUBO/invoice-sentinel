import type { Metadata } from "next";
import "./globals.css";
import { Nav } from "@/components/Nav";

export const metadata: Metadata = {
  title: "InvoiceSentinel — AP Risk Desk",
  description:
    "AI accounts-payable risk triage for PH SMEs. Multimodal invoice review before payment — not a tax authority tool.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen flex flex-col">
          <Nav />
          <main className="flex-1 mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
            {children}
          </main>
          <footer className="border-t border-slate-200 bg-white">
            <div className="mx-auto max-w-7xl px-4 py-4 text-xs text-slate-500 sm:px-6 lg:px-8">
              InvoiceSentinel MVP · BFSI theme · Google Cloud AI Builder Cup 2026 ·{" "}
              <span className="font-medium text-slate-600">
                Not a BIR / tax-authority tool — AP risk triage before payment only.
              </span>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
