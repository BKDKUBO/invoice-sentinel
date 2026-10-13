"""Generates proposal.html (Sentinel brand). Run via build.py."""
import math, pathlib
HERE = pathlib.Path(__file__).resolve().parent
URL = "invoicesentinel-web-1034883854575.asia-southeast1.run.app"
I = {  # lucide-style icon paths
 "alert":'<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/>',
 "shield":'<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
 "upload":'<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5M12 3v12"/>',
 "scan":'<path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M7 12h10"/>',
 "gavel":'<path d="m14 13-7.5 7.5a2.1 2.1 0 0 1-3-3L11 10"/><path d="m16 16 6-6M8 8l6-6M9 7l8 8M21 11l-8-8"/>',
 "users":'<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
 "bank":'<path d="M3 21h18M5 21V10M19 21V10M9 21V10M15 21V10M2 10l10-7 10 7Z"/>',
 "link":'<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>',
 "bot":'<rect x="3" y="8" width="18" height="12" rx="2"/><path d="M12 8V4M8 14h.01M16 14h.01"/>',
 "globe":'<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20 15 15 0 0 1 0-20"/>',
 "file":'<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M9 15l2 2 4-4"/>',
 "id":'<rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="8" cy="12" r="2"/><path d="M14 10h4M14 14h4"/>',
 "split":'<path d="M16 3h5v5M8 3H3v5M12 22v-8.3a4 4 0 0 0-1.2-2.9L3 3M21 3l-7.8 7.8"/>',
 "gauge":'<path d="m12 14 4-4"/><path d="M3.3 19a10 10 0 1 1 17.4 0"/>',
 "mail":'<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
 "coins":'<circle cx="8" cy="8" r="6"/><path d="M18.1 10.4A6 6 0 1 1 10.3 18M7 6h1v4"/>',
 "rocket":'<path d="M4.5 16.5c-1.5 1.3-2 5-2 5s3.7-.5 5-2c.7-.8.7-2.1-.1-2.9a2.2 2.2 0 0 0-2.9-.1Z"/><path d="m12 15-3-3a22 22 0 0 1 2-4A12.9 12.9 0 0 1 22 2c0 2.7-.8 7.5-6 11a22 22 0 0 1-4 2Z"/>',
 "access":'<circle cx="12" cy="4" r="2"/><path d="M5 8h14M12 8v6M9 22l3-8 3 8"/>',
 "lock":'<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
 "chart":'<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>',
}
def ic(n): return f'<span class="ic"><svg viewBox="0 0 24 24">{I[n]}</svg></span>'
def logo(s=40, stroke="#e6b422"):
    rays = "".join(f'<line x1="{20+math.cos(i*math.pi/4)*6.5:.2f}" y1="{18+math.sin(i*math.pi/4)*6.5:.2f}" x2="{20+math.cos(i*math.pi/4)*9.5:.2f}" y2="{18+math.sin(i*math.pi/4)*9.5:.2f}"/>' for i in range(8))
    return (f'<svg viewBox="0 0 40 40" width="{s}" height="{s}"><path d="M20 2 35 8v11c0 9.5-6.4 16.4-15 19-8.6-2.6-15-9.5-15-19V8L20 2Z" fill="#0b1c2c" stroke="{stroke}" stroke-width="2"/>'
            f'<g stroke="#fcd116" stroke-width="1.6" stroke-linecap="round">{rays}</g><circle cx="20" cy="18" r="4.6" fill="#fcd116"/>'
            '<path d="m17.6 18.1 1.7 1.7 3.3-3.5" fill="none" stroke="#0b1c2c" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
def head(k, n, title, crit):
    c = "".join(f"<span>{x}</span>" for x in crit)
    return f'<div class="tri"></div><div class="head"><div><p class="kicker"><b>{n}</b>{k}</p><h1>{title}</h1></div><div class="crit">{c}</div></div>'
SEV = {"critical":"#ce1126","high":"#e8761c","medium":"#e6b422","low":"#2e9d5b"}

def problem_chart():
    rows=[("4 ghost corporations: alleged tax loss, 2019–21 [1][2]",25.5),("Ever Bilena: alleged total tax liability [5]",1.6),("23 buyer firms: alleged deficiencies, 2025 [3][4]",1.41),("World Balance: alleged basic deficiencies [6]",0.1788)]
    W=520; out=['<svg viewBox="0 0 560 210" width="560" height="210" font-family="Inter">']
    for i,(l,v) in enumerate(rows):
        y=i*52; w=max(6,W*v/25.5)
        out.append(f'<text x="0" y="{y+13}" font-size="12" fill="#4a5b70">{l}</text><rect x="0" y="{y+19}" width="{w:.0f}" height="20" rx="4" fill="{"#0b1c2c" if i==0 else "#e6b422"}"/>'
                   f'<text x="{min(w+8,W-60) if i else w-70:.0f}" y="{y+34}" font-size="13" font-weight="800" fill="{"#fcd116" if i==0 else "#0b1c2c"}">₱{v:g}B</text>')
    return "".join(out)+"</svg>"

EV=[("01","Legit VAT invoice",0,"low","—"),("02","Small non-VAT receipt",0,"low","—"),("03","Ghost vendor",100,"critical","GHOST_VENDOR, TIN_INVALID"),
("04","VAT math wrong",70,"high","MATH_ERROR"),("05","Bank-change BEC",90,"critical","UNUSUAL_PAYMENT_CHANGE"),("06","Overbilled vs PO",75,"high","OVERBILLING, PO_MISMATCH"),
("07","Near-duplicate",70,"high","DUPLICATE_INVOICE"),("08","Blurry legit photo",20,"low","VENDOR_TIN_MISMATCH (low)"),("09","Known vendor, new bank",90,"critical","UNUSUAL_PAYMENT_CHANGE"),
("10","Qty exceeds PO",70,"high","PO_MISMATCH"),("11","PO not found",70,"high","MISSING_PO"),("12","Split invoice A",0,"low","—"),("13","Split invoice B",70,"high","SPLIT_INVOICE"),("14","Malformed TIN, no BIR fields",80,"high","TIN_INVALID, BIR_FORMAT_ISSUE")]
def eval_chart():
    H=200; bw=26; g=12; out=['<svg viewBox="0 0 560 250" width="560" height="250" font-family="Inter">']
    for t in (0,50,100):
        y=20+H-H*t/100; out.append(f'<line x1="30" x2="555" y1="{y}" y2="{y}" stroke="#dfe5ec"/><text x="24" y="{y+4}" font-size="10" text-anchor="end" fill="#7b8a9c">{t}</text>')
    for i,(n,_,s,sev,_f) in enumerate(EV):
        x=40+i*(bw+g); h=max(3,H*s/100); y=20+H-h
        out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{h}" rx="3" fill="{SEV[sev]}"/>')
        for k in range(3): out.append(f'<circle cx="{x+5+k*8}" cy="{y-7}" r="2.6" fill="#0b1c2c"/>')
        out.append(f'<text x="{x+bw/2}" y="{H+36}" font-size="11" font-weight="700" text-anchor="middle" fill="#16263a">{n}</text>')
    return "".join(out)+"</svg>"
def cost_chart():
    rows=[("200 / mo","Small SME",62,124),("2,000 / mo","Mid-market team",623,1246),("50,000 / mo","Shared services / bank",16000,31000)]
    out=['<svg viewBox="0 0 520 200" width="520" height="200" font-family="Inter">']
    mx=math.log10(31000)
    for i,(v,u,a,b) in enumerate(rows):
        y=i*64
        out.append(f'<text x="0" y="{y+14}" font-size="13" font-weight="700" fill="#0b1c2c">{v}</text><text x="0" y="{y+30}" font-size="11" fill="#4a5b70">{u}</text>')
        for j,(val,col) in enumerate(((a,"#0b1c2c"),(b,"#e6b422"))):
            w=40+300*math.log10(val)/mx; yy=y+4+j*22
            out.append(f'<rect x="130" y="{yy}" width="{w-40:.0f}" height="18" rx="4" fill="{col}"/><text x="{130+w-32:.0f}" y="{yy+13}" font-size="12" font-weight="700" fill="#16263a">₱{val:,}</text>')
    return "".join(out)+"</svg>"

ARCH = '''<svg viewBox="0 0 1160 420" width="1160" height="420" font-family="Inter">
<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#a27a06"/></marker></defs>
<rect x="250" y="20" width="640" height="380" rx="16" fill="#f6f8fb" stroke="#c7d2de" stroke-dasharray="6 5"/>
<text x="270" y="46" font-size="13" font-weight="700" fill="#4a5b70">GOOGLE CLOUD · asia-southeast1 (Singapore)</text>
<g font-size="13">
<rect x="10" y="150" width="190" height="110" rx="12" fill="#fff" stroke="#c7d2de"/><text x="105" y="185" text-anchor="middle" font-weight="800" fill="#0b1c2c">AP analyst</text><text x="105" y="207" text-anchor="middle" fill="#4a5b70">Browser · desktop / phone</text><text x="105" y="229" text-anchor="middle" fill="#4a5b70">Upload or "Try a sample"</text>
<rect x="290" y="70" width="250" height="110" rx="12" fill="#0b1c2c"/><text x="415" y="104" text-anchor="middle" font-weight="800" fill="#fff">Cloud Run · Web</text><text x="415" y="126" text-anchor="middle" fill="#c9d6e3">Next.js 14 · Tailwind · Inter</text><text x="415" y="148" text-anchor="middle" fill="#fcd116">Dashboard · Upload · Case · Vendors</text>
<rect x="290" y="230" width="250" height="140" rx="12" fill="#0b1c2c" stroke="#e6b422" stroke-width="2.5"/><text x="415" y="262" text-anchor="middle" font-weight="800" fill="#fff">Cloud Run · API</text><text x="415" y="284" text-anchor="middle" fill="#c9d6e3">FastAPI · deterministic checks</text><text x="415" y="304" text-anchor="middle" fill="#c9d6e3">vendor/PO · TIN · BIR · split · scoring</text><text x="415" y="330" text-anchor="middle" fill="#fcd116" font-weight="700">Google ADK agent (7 tools)</text><text x="415" y="350" text-anchor="middle" fill="#c9d6e3">NDJSON step streaming</text>
<rect x="610" y="60" width="250" height="70" rx="12" fill="#fff" stroke="#e6b422" stroke-width="2"/><text x="735" y="90" text-anchor="middle" font-weight="800" fill="#0b1c2c">Gemini 3.8 Flash</text><text x="735" y="111" text-anchor="middle" fill="#4a5b70">multimodal read · JSON schema · T=0</text>
<rect x="610" y="145" width="250" height="56" rx="12" fill="#fff" stroke="#c7d2de"/><text x="735" y="170" text-anchor="middle" font-weight="800" fill="#0b1c2c">Firestore</text><text x="735" y="189" text-anchor="middle" fill="#4a5b70">cases · vendors · POs · chats · audit</text>
<rect x="610" y="215" width="250" height="56" rx="12" fill="#fff" stroke="#c7d2de"/><text x="735" y="240" text-anchor="middle" font-weight="800" fill="#0b1c2c">Cloud Storage</text><text x="735" y="259" text-anchor="middle" fill="#4a5b70">private invoice file bucket</text>
<rect x="610" y="285" width="250" height="56" rx="12" fill="#fff" stroke="#c7d2de"/><text x="735" y="310" text-anchor="middle" font-weight="800" fill="#0b1c2c">Secret Manager</text><text x="735" y="329" text-anchor="middle" fill="#4a5b70">Gemini API key, mounted at runtime</text>
<rect x="610" y="352" width="250" height="38" rx="10" fill="#fff" stroke="#c7d2de"/><text x="735" y="376" text-anchor="middle" fill="#4a5b70"><tspan font-weight="800" fill="#0b1c2c">Cloud Build</tspan> · deploy.sh builds both images</text>
<rect x="940" y="120" width="210" height="190" rx="12" fill="#fbf8ef" stroke="#f0e3b8"/><text x="1045" y="150" text-anchor="middle" font-weight="800" fill="#0b1c2c">Analyst decides</text>
<text x="1045" y="178" text-anchor="middle" fill="#4a5b70">PAY · HOLD · VERIFY</text><text x="1045" y="202" text-anchor="middle" fill="#4a5b70">Approve / Escalate /</text><text x="1045" y="222" text-anchor="middle" fill="#4a5b70">Request docs</text><text x="1045" y="250" text-anchor="middle" fill="#4a5b70">Verification email draft</text><text x="1045" y="272" text-anchor="middle" fill="#4a5b70">(copied, never auto-sent)</text>
</g>
<g stroke="#a27a06" stroke-width="2" fill="none" marker-end="url(#a)">
<path d="M200 190 L285 130"/><path d="M200 220 L285 290"/><path d="M415 180 L415 226"/>
<path d="M540 270 L605 98"/><path d="M540 285 L605 173"/><path d="M540 300 L605 243"/><path d="M540 320 L605 313"/><path d="M860 215 L935 215"/>
</g></svg>'''

PAGES = []
PAGES.append(f'''<section class="page cover"><div class="tri"></div>
<svg class="rays" viewBox="0 0 40 40">{''.join(f'<line x1="20" y1="20" x2="{20+math.cos(i*math.pi/4)*19:.2f}" y2="{20+math.sin(i*math.pi/4)*19:.2f}" stroke="#fcd116" stroke-width="2.4"/>' for i in range(8))}<circle cx="20" cy="20" r="6" fill="#fcd116"/></svg>
<div style="display:flex;align-items:center;gap:14px;margin-top:70px">{logo(64)}<div><div style="font-size:24px;font-weight:800;color:#fff">InvoiceSentinel</div><div style="font-size:12px;letter-spacing:.18em;color:#e6b422;font-weight:700">AP RISK DESK · PH SMES</div></div></div>
<h1 style="margin-top:60px">Stop paying the <span class="gold">ghost</span><br>before the money moves.</h1>
<p style="font-size:19px;max-width:760px;color:#c9d6e3;margin-top:18px">A Gemini + Google ADK risk desk that checks every supplier invoice against your vendor master, purchase orders and BIR rules, then tells the analyst <b style="color:#fff">PAY, HOLD or VERIFY</b>, with evidence.</p>
<div style="margin-top:26px"><span class="theme">Theme · BFSI: Intelligent Risk, Fraud &amp; Financial Experiences</span></div>
<div style="position:absolute;left:70px;right:70px;bottom:40px;display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:28px;font-size:13px;color:#c9d6e3;border-top:1px solid #2a4663;padding-top:16px">
<div><div class="tiny" style="color:#e6b422;font-weight:700">LIVE PROTOTYPE · CLOUD RUN</div>{URL}</div>
<div><div class="tiny" style="color:#e6b422;font-weight:700">TEAM BKD KUBO</div>Manuel III Ocaña · Elson Mojics</div>
<div><div class="tiny" style="color:#e6b422;font-weight:700">GOOGLE CLOUD AI BUILDER CUP 2026</div>Prototype submission · Oct 2026</div></div></section>''')

PAGES.append(f'''<section class="page">{head("The problem","01","Fake receipts are an industry, and accounts payable is where they get paid",["Problem &amp; impact"])}
<div class="grid" style="grid-template-columns:600px 1fr;gap:34px">
<div><h2>Ghost-receipt cases filed by the BIR (alleged, ₱ billions)</h2>{problem_chart()}
<div class="card cream small" style="margin-top:8px"><b>68%</b> of organizations hit at least one AP fraud attempt in 2024; only <b>31%</b> use automated fraud detection (Basware survey of 100 finance leaders [7]).</div>
<p class="src">BIR figures are allegations in complaints and filings, not final court findings. Sources on page 13.</p></div>
<div><div class="card" style="margin-bottom:12px">{ic("file")}<h3>The documents look real</h3><p class="small mute">Ghost receipts carry a TIN, a VAT line and a clean letterhead. They come from corporations with no operations, set up only to issue receipts [3].</p></div>
<div class="card" style="margin-bottom:12px">{ic("bank")}<h3>The buyer takes the hit</h3><p class="small mute">In the 2025 cases, purchasing companies, their officers and their CPAs faced complaints [3]. A fake expense means cash out the door, then audit exposure.</p></div>
<div class="card">{ic("alert")}<h3>Bank-change scams hit the same desk</h3><p class="small mute">A "new bank account, please don't call" note on an otherwise normal invoice can empty an SME account in one transfer. Most SMEs have no fraud team; the only control is the clerk who opens the PDF.</p></div></div></div></section>''')

PAGES.append(f'''<section class="page">{head("The solution","02","A pre-payment risk desk: upload, check, decide",["GenAI","UX"])}
<div class="flow" style="margin-bottom:18px">
<div class="st">{ic("upload")}<h3><span class="num">1</span>Upload</h3><p class="small mute">Photo, scan or PDF, or one click on <b>Try a sample</b>.</p></div><div class="ar">›</div>
<div class="st">{ic("scan")}<h3><span class="num">2</span>Gemini reads</h3><p class="small mute">Fields, line items, payee and bank details in structured JSON. No OCR templates.</p></div><div class="ar">›</div>
<div class="st">{ic("shield")}<h3><span class="num">3</span>Code checks</h3><p class="small mute">Vendor master, PO, TIN, BIR RR 7-2024, split invoices, VAT math: deterministic rules.</p></div><div class="ar">›</div>
<div class="st">{ic("bot")}<h3><span class="num">4</span>Agent explains</h3><p class="small mute">Ask the case in any language; the ADK agent cites evidence and drafts a verification email.</p></div><div class="ar">›</div>
<div class="st">{ic("gavel")}<h3><span class="num">5</span>Human decides</h3><p class="small mute">Approve, Escalate or Request docs. Every step goes to the audit trail.</p></div></div>
<div class="grid" style="grid-template-columns:1.55fr 1fr;gap:26px"><div><img class="shot" src="assets/after/dashboard.png" style="height:370px;object-fit:cover;object-position:top;width:100%"><p class="cap">Live dashboard: KPI cards, risk trend, flag breakdown and severity mix.</p></div>
<div><h2>Design principles</h2><ul class="chk small">
<li><b>Triage, not verdicts.</b> The score orders the queue; it never pays or blocks anything by itself.</li>
<li><b>Evidence for every claim.</b> Risk cards and agent answers cite evidence IDs (E1–E9, IMG) that the analyst can open.</li>
<li><b>Code for facts, AI for judgment.</b> Matching, TIN checks, BIR rules and scoring are deterministic; Gemini reads the document and explains.</li>
<li><b>Never fake an answer.</b> If Gemini is down, the API returns a retryable error. It never invents a clean case.</li>
<li><b>Honest scope.</b> Supports AP triage; it does not certify BIR compliance.</li></ul></div></div></section>''')

PAGES.append(f'''<section class="page">{head("Theme fit","03","Built for BFSI: trust, fraud and risk at the last control before cash moves",["Problem alignment"])}
<div class="grid g3" style="margin-bottom:20px">
<div class="card navy">{ic("alert")}<h2>Fraud</h2><p class="small">Named fraud types are first-class flags: ghost vendor, bank-change / BEC payment redirection, duplicates, overbilling, split invoices that dodge approval limits.</p></div>
<div class="card navy">{ic("gauge")}<h2>Risk</h2><p class="small">A deterministic 0–100 score with severity floors ranks the inbox. Shows "₱ at risk" and high/critical open cases, so controllers can see their exposure at a glance.</p></div>
<div class="card navy">{ic("shield")}<h2>Trust</h2><p class="small">Every flag is explained with evidence. The verification email goes only to the contact <i>on file</i>, never the one printed on the invoice. A person makes every payment decision.</p></div></div>
<div class="grid g2"><div class="card"><h2>Financial experience for the people who pay</h2>
<table><tr><th>User</th><th>Gets</th></tr>
<tr><td><b>AP clerk</b></td><td>Ranked inbox, one-click samples, plain-language answers in English, Tagalog and more</td></tr>
<tr><td><b>Controller</b></td><td>KPI dashboard, Escalate / Request docs, timestamped audit trail</td></tr>
<tr><td><b>SME owner</b></td><td>Protection from bank-change scams for centavos per invoice, on a phone</td></tr>
<tr><td><b>Banks / lenders</b></td><td>A pattern that carries over to SME payment portals and claims-document review</td></tr></table></div>
<div class="card cream"><h2>Why it matters beyond one company</h2><ul class="chk small">
<li>The theme asks for AI that detects and mitigates fraud or risk and automates complex financial processes [10]. InvoiceSentinel does both, before the payment goes out.</li>
<li>BIR RR 7-2024 invoice checks and TIN validation make it harder for ghost receipts to enter the books, which protects tax revenue.</li>
<li>A light browser tool rather than an ERP, so SMEs can adopt it without a fraud team.</li></ul></div></div></section>''')

PAGES.append(f'''<section class="page">{head("Features · controls","04","Deterministic checks catch what a tired reviewer misses",["Technical merit","Innovation"])}
<div class="grid" style="grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:16px">
<div class="card">{ic("link")}<h3>Vendor master &amp; PO matching</h3><p class="small mute">Vendor, TIN, bank account, PO number, line quantities and prices vs the master. A changed bank account is a <b>critical</b> flag.</p></div>
<div class="card">{ic("id")}<h3>TIN validation</h3><p class="small mute">Format and branch-code checks; compares the vendor TIN with the master record.</p></div>
<div class="card">{ic("file")}<h3>BIR RR 7-2024 checklist</h3><p class="small mute">Required invoice elements with section references, buyer-TIN rule for VAT sales ≥ ₱1,000. Advisory only.</p></div>
<div class="card">{ic("split")}<h3>Split-invoice detection</h3><p class="small mute">Same vendor, close dates, combined total above the approval limit (set in Settings) → <b>SPLIT_INVOICE</b>.</p></div>
<div class="card">{ic("gauge")}<h3>Deterministic scoring</h3><p class="small mute">Severity weights (low 20 · medium 45 · high 70 · critical 90) +5 per extra flag. Same input, same score.</p></div>
<div class="card">{ic("scan")}<h3>Gemini extraction</h3><p class="small mute">Multimodal read with a JSON schema at temperature 0, seed 7, with retries and a 60 s timeout.</p></div></div>
<div class="grid g3" style="gap:16px"><div><img class="shot" src="assets/after/vendor-master-mismatch.png" style="height:190px;width:100%;object-fit:cover;object-position:top"><p class="cap">Sample 09: bank account differs from the vendor master.</p></div>
<div><img class="shot" src="assets/after/bir-checklist.png" style="height:190px;width:100%;object-fit:cover;object-position:top"><p class="cap">BIR RR 7-2024 checklist with TIN status.</p></div>
<div><img class="shot" src="assets/after/split-invoice-risk-card.png" style="height:190px;width:100%;object-fit:contain;background:#fff"><p class="cap">Sample 13 flagged as a split of sample 12.</p></div></div></section>''')

PAGES.append(f'''<section class="page">{head("Features · agent","05","Ask the case: a Google ADK agent that shows its work as it goes",["GenAI","UX"])}
<div class="grid" style="grid-template-columns:330px 1fr 1fr;gap:20px">
<div><div class="card navy small" style="margin-bottom:12px">{ic("bot")}<h3>7 tools, all read-only</h3><p>get_case_evidence · lookup_vendor · lookup_po · validate_tin · bir_checklist · search_vendor_history · draft_verification_email</p></div>
<ul class="chk small"><li><b>Streamed steps:</b> each tool call shows up live ("Checking vendor master…") over NDJSON. The first step arrives in about 5 s.</li>
<li><b>Grounded:</b> answers cite evidence IDs and end with <b>PAY, HOLD or VERIFY</b>.</li>
<li><b>Multilingual:</b> replies in the user's language. Tagalog and English were tested live.</li>
<li><b>Safe email:</b> code, not the model, sets the recipient from the vendor master. Drafts are copied, never auto-sent.</li></ul></div>
<div><img class="shot" src="assets/after/agent-streaming-progress.png" style="width:100%;height:250px;object-fit:cover;object-position:top"><p class="cap">Agent steps arriving live.</p>
<img class="shot" src="assets/after/ask-tagalog-answer.png" style="width:100%;height:200px;object-fit:cover;object-position:top;margin-top:10px"><p class="cap">Tagalog answer: HOLD, with cited evidence.</p></div>
<div><img class="shot" src="assets/after/email-draft-tagalog-crop.png" style="width:100%"><p class="cap">Tagalog verification email to the contact on file (sample 09).</p></div></div></section>''')

PAGES.append(f'''<section class="page">{head("Architecture","06","Serverless on Google Cloud, end to end",["Technical merit"])}
{ARCH}
<div class="grid g3 small" style="margin-top:6px;gap:16px"><p><b>Stateless services.</b> Both containers autoscale on Cloud Run; all state lives in Firestore and Cloud Storage.</p>
<p><b>Secrets stay secret.</b> The Gemini key is in Secret Manager, never in code or images. Uploads go to a private bucket.</p>
<p><b>One-command deploy.</b> <code>deploy.sh</code> provisions Firestore, the bucket and IAM, then builds and deploys both services with Cloud Build.</p></div></section>''')

rows="".join(f'<tr><td><b>{n}</b></td><td>{d}</td><td><span class="pill p-{ {"critical":"crit","high":"high","medium":"med","low":"low"}[sv] }">{sv}</span></td><td>{s} / {s} / {s}</td><td class="tiny">{f}</td></tr>' for n,d,s,sv,f in EV)
PAGES.append(f'''<section class="page">{head("Evaluation","07","14 test invoices × 3 runs: identical results every time",["Technical merit"])}
<div class="grid" style="grid-template-columns:580px 1fr;gap:30px"><div>
<h2>Risk score per sample (dots = 3 runs, all equal)</h2>{eval_chart()}
<div style="display:flex;gap:14px;font-size:11px;margin:4px 0 12px">{''.join(f'<span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:{c};margin-right:4px"></span>{k}</span>' for k,c in SEV.items() if k!="medium")}</div>
<div class="grid g3" style="gap:10px"><div class="card"><div class="stat">0</div><p class="tiny">score spread over 3 passes, all 14 samples</p></div>
<div class="card"><div class="stat">14<small>/14</small></div><p class="tiny">in the expected severity band</p></div>
<div class="card"><div class="stat">~20<small>s</small></div><p class="tiny">upload to verdict, live on Cloud Run</p></div></div></div>
<div><table><tr><th>#</th><th>Sample (fictional)</th><th>Band</th><th>Scores</th><th>Key flags</th></tr>{rows}</table>
<p class="tiny" style="margin-top:6px">Run with <code>samples/stability.py 3</code> on gemini-3.8-flash, Oct 12, 2026, resetting between passes. Bank-change samples 05 and 09 and split samples 12 and 13 were re-checked on the live deployment on Oct 13. Sample 08 is a known limit: a blurry TIN gives a low-severity flag, not a fraud flag.</p></div></div></section>''')

PAGES.append(f'''<section class="page">{head("User guide","08","Try it in 60 seconds, with no files needed",["UX"])}
<div class="grid" style="grid-template-columns:1.5fr 1fr 230px;gap:24px">
<div><img class="shot" src="assets/after/upload.png" style="width:100%;height:400px;object-fit:cover;object-position:top"><p class="cap">Upload page: stepper, drop zone and the <b>Try a sample</b> grid.</p></div>
<div><div class="card navy" style="margin-bottom:12px"><div class="tiny" style="color:#e6b422;font-weight:700">LIVE URL</div><div style="font-weight:700;color:#fff;font-size:13px;word-break:break-all">https://{URL}</div></div>
<ol class="small" style="padding-left:18px"><li><b>Check an invoice → Try a sample.</b> Click <b>09 known vendor, new bank</b>. The steps animate while Gemini reads it.</li>
<li><b>Read the case.</b> A critical risk card plus a vendor-master table showing the bank-account mismatch.</li>
<li><b>Ask the case.</b> Type "Ligtas ba itong bayaran?" and watch the agent steps stream in.</li>
<li><b>Draft verification email</b> in Tagalog. It goes to the contact on file. Copy it; nothing is sent.</li>
<li><b>Splits:</b> run sample 12, then 13. The second one is flagged SPLIT_INVOICE.</li>
<li><b>Decide:</b> Approve, Escalate or Request docs. The decision is logged in the audit trail.</li>
<li><b>Vendors &amp; POs</b> page: edit the master data the checks use.</li></ol>
<p class="tiny">"Reset demo" restores the seed data. All vendors, people and accounts are fictional.</p></div>
<div><img class="shot" src="assets/after/mobile-case.png" style="width:100%"><p class="cap">Mobile layout.</p></div></div></section>''')

PAGES.append(f'''<section class="page">{head("Community benefit &amp; accessibility","09","Fraud protection for the businesses that have no fraud team",["Impact","UX"])}
<div class="grid g3" style="margin-bottom:18px">
<div class="card">{ic("users")}<h2>SMEs</h2><p class="small mute">MSMEs are most businesses in the Philippines, and most have no AP controls beyond one person. A browser tool that works from a phone photo brings bank-grade checks within reach.</p></div>
<div class="card">{ic("coins")}<h2>Tax revenue</h2><p class="small mute">Every ghost receipt that is stopped is a fake deduction and fake input VAT kept out of the books. BIR RR 7-2024 checks point clerks to the missing elements before payment.</p></div>
<div class="card">{ic("globe")}<h2>Multilingual</h2><p class="small mute">Clerks ask in Tagalog, English or mixed Taglish and get answers and supplier emails in that language, so staff and suppliers both understand them.</p></div></div>
<div class="grid g2"><div class="card cream">{ic("access")}<h2>Accessibility built in</h2><ul class="chk small">
<li>WCAG AA contrast for body text; severity is shown as text labels, not only color</li>
<li>Visible gold focus rings and full keyboard navigation; aria-current in the nav</li>
<li>ARIA labels on inputs, live regions for agent progress, reduced-motion support</li>
<li>Responsive layouts tested at phone width (390 px)</li></ul></div>
<div class="card">{ic("lock")}<h2>Responsible by design</h2><ul class="chk small">
<li>Human in the loop: no automatic rejection or payment</li>
<li>Small and non-VAT vendors are not penalized for normal informality; blur is not treated as fraud</li>
<li>Emails are only drafted; the recipient comes from the master record</li>
<li>Paid-tier Gemini API: content is not used to train Google's models [8]</li></ul></div></div></section>''')

PAGES.append(f'''<section class="page">{head("Scalability, production &amp; cost","10","Centavos per invoice, from a single SME to a bank portfolio",["Scalability","Impact"])}
<div class="grid" style="grid-template-columns:1fr 1fr 1fr;gap:22px">
<div><div class="card navy" style="margin-bottom:12px"><div class="stat" style="color:#fcd116">~₱0.31</div><p class="small">Gemini cost per invoice (3.8 Flash, promo pricing to Dec 31, 2026; ~₱0.62 from 2027) [8]</p></div>
<h2>Monthly model cost by volume</h2>{cost_chart()}
<div class="tiny"><span style="color:#0b1c2c">■</span> 2026 promo · <span style="color:#a27a06">■</span> from 2027. FX ₱62.77/US$. Log scale.</div></div>
<div><h2>Infrastructure</h2><ul class="chk small"><li>Cloud Run scales to zero; at SME volumes usage fits within the free tier [9].</li>
<li>For judging, one instance of each service stays warm (min-instances 1) so there are no cold starts: about <b>US$23 / ~₱1,450 per month</b>. Set to 0 afterwards.</li>
<li>Firestore and Cloud Storage cost almost nothing at prototype scale.</li></ul>
<h2 style="margin-top:14px">Scalability</h2><ul class="chk small"><li>Stateless API, horizontal autoscaling</li><li>Gemini Batch API for overnight payment runs at half the token price [8]</li><li>Tenant-scoped Firestore collections for multiple companies</li></ul></div>
<div class="card cream"><h2>Path to production</h2><table>
<tr><td><b>Done</b></td><td class="small">Cloud Run, Firestore, private bucket, Secret Manager, ADK agent, deterministic controls</td></tr>
<tr><td><b>Next</b></td><td class="small">Identity Platform sign-in with analyst / approver roles; signed URLs; rate limits</td></tr>
<tr><td><b>Then</b></td><td class="small">Per-tenant data isolation, retention policies, upload malware scanning, audit export</td></tr>
<tr><td><b>Ops</b></td><td class="small">Budget alerts, labeled evaluation set and regression tests on every prompt or model change</td></tr></table></div></div></section>''')

PAGES.append(f'''<section class="page">{head("Roadmap","11","From prototype to the payment-control layer for PH SMEs",["Innovation","Impact"])}
<div class="grid g4" style="margin-top:20px">
{''.join(f'<div class="card{" navy" if i==0 else ""}"><div class="tiny" style="color:{"#fcd116" if i==0 else "#a27a06"};font-weight:800;letter-spacing:.1em">{h}</div><h2 style="margin-top:4px">{t}</h2><ul class="chk small">{"".join(f"<li>{x}</li>" for x in xs)}</ul></div>' for i,(h,t,xs) in enumerate([
 ("NOW · OCT 2026","Live prototype",["Vendor/PO matching, TIN, BIR RR 7-2024, split detection","ADK agent with streamed steps","Multilingual Q&amp;A and verification emails","Firestore + Cloud Storage on Cloud Run"]),
 ("Q1 2027","Pilot-ready",["Sign-in and approver roles","Email-inbox intake of supplier bills","CSV import of vendor master and POs","Labeled PH evaluation set, precision/recall per flag"]),
 ("Q2 2027","Integrations",["QuickBooks / Xero bill sync; hold payment on Escalate","Batch review of whole payment runs","Bank-account change history per vendor"]),
 ("LATER","Ecosystem",["Bank SME portals: pre-transfer check API","Claims-document review for insurers","Tagalog / Cebuano UI","Optional BIR ATP and series lookups as signals"])])) }
</div>
<div class="card cream small" style="margin-top:22px"><b>Guardrails stay fixed as we grow:</b> a person decides every payment, every flag carries evidence, nothing is auto-sent, and the product never claims to certify BIR compliance.</div></section>''')

PAGES.append(f'''<section class="page">{head("Team &amp; references","12","The team behind InvoiceSentinel",["Submission"])}
<div class="grid" style="grid-template-columns:1fr 1.25fr;gap:30px">
<div><div class="card navy" style="display:flex;align-items:center;gap:14px;margin-bottom:14px">{logo(48)}<div><div class="tiny" style="color:#e6b422;font-weight:700;letter-spacing:.12em">TEAM</div><div style="font-size:28px;font-weight:800;color:#fff">BKD KUBO</div></div></div>
<div class="grid g2" style="gap:12px">
<div class="card">{ic("rocket")}<h3>Manuel III Ocaña</h3><p class="small mute">Product Lead &amp; Solution Architect</p></div>
<div class="card">{ic("coins")}<h3>Elson Mojics</h3><p class="small mute">Domain Lead (Finance) &amp; QA</p></div></div>
<table style="margin-top:14px"><tr><th colspan="2">Submission links</th></tr><tr><td>Live prototype</td><td class="small">{URL}</td></tr><tr><td>Demo video</td><td class="small">[VIDEO LINK]</td></tr><tr><td>Theme</td><td class="small">BFSI: Intelligent Risk, Fraud &amp; Financial Experiences</td></tr></table></div>
<div><h2>References (accessed Oct 12, 2026)</h2><ol class="tiny" style="padding-left:16px;line-height:1.35">
<li>Rappler, "P25.5 billion 'lost': BIR files tax complaints vs firms selling fake receipts," Mar 16, 2023.</li>
<li>BusinessWorld, "BIR goes after firms issuing fake receipts," Mar 17, 2023 (₱17.63B income tax, ₱7.91B VAT).</li>
<li>BIR press release, Aug 7, 2025: 23 corporations, 56 officers, 17 CPAs; ₱1.41B. bir-cdn.bir.gov.ph/BIR/pdf/PR37AUG0725.pdf</li>
<li>Philstar, "23 firms face tax evasion cases for P1.4 billion ghost receipts," Aug 8, 2025.</li>
<li>Philstar, "BIR files case vs Ever Bilena over P1.6 billion tax liability," Feb 6, 2024.</li>
<li>Manila Bulletin, "BIR snares World Balance over fictitious receipts," Jul 21, 2025 (₱178.8M).</li>
<li>Basware / sharedserviceslink, "The Rise in AP Fraud: Frequency, Sophistication, and Impact."</li>
<li>Google AI for Developers, "Gemini Developer API pricing," updated Oct 9, 2026. ai.google.dev/gemini-api/docs/pricing</li>
<li>Google Cloud, "Cloud Run pricing." cloud.google.com/run/pricing</li>
<li>Google Cloud AI Builder Cup 2026, themes and judging criteria. aibuildercup.com/themes.html</li>
<li>BIR Revenue Regulations No. 7-2024 (invoicing requirements under the EOPT Act).</li></ol></div></div></section>''')

def main():
    n=len(PAGES); body=[]
    for i,p in enumerate(PAGES,1):
        if i>1: p=p.replace("</section>",f'<div class="foot"><span style="display:flex;align-items:center;gap:6px">{logo(14)}<b style="color:#0b1c2c">InvoiceSentinel</b> · Google Cloud AI Builder Cup 2026 · BFSI</span><span class="pg">{i:02d} / {n:02d}</span></div></section>')
        body.append(p)
    html=f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>InvoiceSentinel proposal</title><link rel="stylesheet" href="style.css"></head><body>{"".join(body)}</body></html>'
    (HERE/"proposal.html").write_text(html); return n
if __name__=="__main__": print(main())
