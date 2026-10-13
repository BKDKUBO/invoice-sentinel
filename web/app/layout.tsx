import type { Metadata, Viewport } from "next";
import "@fontsource-variable/inter";
import "./globals.css";
import { Nav } from "@/components/Nav";

export const metadata: Metadata = {
  title: "InvoiceSentinel — AP Risk Desk",
  description:
    "AI accounts-payable risk triage for PH SMEs. Multimodal invoice review before payment — not a tax authority tool.",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1, themeColor: "#0b1c2c" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-3 focus:top-3 focus:z-50 focus:rounded-md focus:bg-gold-300 focus:px-3 focus:py-2 focus:text-navy-950">
          Skip to content
        </a>
        <div className="flex min-h-screen flex-col">
          <Nav />
          <main id="main" className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 lg:px-8">
            {children}
          </main>
          <footer className="border-t border-slate-200 bg-white">
            <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-2 px-4 py-4 text-xs text-slate-600 sm:px-6 lg:px-8">
              <span className="font-semibold text-navy-900">InvoiceSentinel</span> · Google Cloud AI Builder Cup 2026 · BFSI ·
              <span>Gemini + Google ADK on Cloud Run, Firestore</span> ·
              <span className="font-medium text-slate-700">Not a BIR / tax-authority tool — AP risk triage before payment only.</span>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
