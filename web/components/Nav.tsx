"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { LogoMark } from "@/components/Logo";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/inbox", label: "Case inbox" },
  { href: "/upload", label: "Check an invoice" },
  { href: "/vendors", label: "Vendors & POs" },
];

export function Nav() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const isActive = (href: string) => pathname === href || (href !== "/" && pathname.startsWith(href));
  return (
    <header className="bg-navy-950 text-white shadow-sm">
      <div className="ph-accent h-1 w-full" aria-hidden="true" />
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2.5" aria-label="InvoiceSentinel home">
          <LogoMark />
          <div>
            <div className="text-base font-bold tracking-tight">
              Invoice<span className="text-gold-300">Sentinel</span>
            </div>
            <div className="text-[10px] font-medium uppercase tracking-[0.14em] text-navy-200">AP risk desk · PH SMEs</div>
          </div>
        </Link>
        <nav aria-label="Main" className="hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              aria-current={isActive(l.href) ? "page" : undefined}
              className={`rounded-md px-3 py-2 text-sm font-medium transition ${
                isActive(l.href) ? "bg-white/10 text-gold-200 shadow-[inset_0_-2px_0_#e6b422]" : "text-navy-100 hover:bg-white/5 hover:text-white"
              }`}
            >
              {l.label}
            </Link>
          ))}
        </nav>
        <button
          type="button"
          className="rounded-md p-2 text-navy-100 hover:bg-white/10 md:hidden"
          aria-label={open ? "Close menu" : "Open menu"}
          aria-expanded={open}
          aria-controls="mobile-nav"
          onClick={() => setOpen((o) => !o)}
        >
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
            {open ? <path strokeLinecap="round" d="M6 6l12 12M18 6 6 18" /> : <path strokeLinecap="round" d="M4 7h16M4 12h16M4 17h16" />}
          </svg>
        </button>
      </div>
      {open && (
        <nav id="mobile-nav" aria-label="Main mobile" className="border-t border-white/10 px-4 pb-3 md:hidden">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              onClick={() => setOpen(false)}
              aria-current={isActive(l.href) ? "page" : undefined}
              className={`block rounded-md px-3 py-2.5 text-sm font-medium ${isActive(l.href) ? "bg-white/10 text-gold-200" : "text-navy-100"}`}
            >
              {l.label}
            </Link>
          ))}
        </nav>
      )}
    </header>
  );
}
