export function LogoMark({ className = "h-9 w-9" }: { className?: string }) {
  // Shield with an eight-rayed sun (nod to the PH flag) and a check — "Sentinel"
  return (
    <svg viewBox="0 0 40 40" className={className} aria-hidden="true">
      <path d="M20 2 35 8v11c0 9.5-6.4 16.4-15 19-8.6-2.6-15-9.5-15-19V8L20 2Z" fill="#0b1c2c" stroke="#e6b422" strokeWidth="2" />
      <g stroke="#fcd116" strokeWidth="1.6" strokeLinecap="round">
        {Array.from({ length: 8 }).map((_, i) => {
          const a = (i * Math.PI) / 4;
          return <line key={i} x1={20 + Math.cos(a) * 6.5} y1={18 + Math.sin(a) * 6.5} x2={20 + Math.cos(a) * 9.5} y2={18 + Math.sin(a) * 9.5} />;
        })}
      </g>
      <circle cx="20" cy="18" r="4.6" fill="#fcd116" />
      <path d="m17.6 18.1 1.7 1.7 3.3-3.5" fill="none" stroke="#0b1c2c" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
