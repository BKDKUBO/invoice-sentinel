"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/inbox", label: "Case inbox" },
  { href: "/upload", label: "Upload" },
  { href: "/vendors", label: "Vendors & POs" },
];

export function Nav() {
  const pathname = usePathname();
  return (
    <header className="border-b border-navy-800/10 bg-navy-950 text-white shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-md bg-sky-500/20 text-sm font-bold text-sky-300 ring-1 ring-sky-400/30">
            IS
          </span>
          <div>
            <div className="text-sm font-semibold tracking-tight">InvoiceSentinel</div>
            <div className="text-[10px] uppercase tracking-wider text-navy-300">
              AP risk desk · PH SMEs
            </div>
          </div>
        </Link>
        <nav className="flex items-center gap-1">
          {links.map((l) => {
            const active = pathname === l.href || (l.href !== "/" && pathname.startsWith(l.href));
            return (
              <Link
                key={l.href}
                href={l.href}
                className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                  active
                    ? "bg-white/10 text-white"
                    : "text-navy-200 hover:bg-white/5 hover:text-white"
                }`}
              >
                {l.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
