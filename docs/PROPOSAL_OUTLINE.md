# InvoiceSentinel — Proposal slide outline

Google Cloud AI Builder Cup 2026 · **BFSI** theme

---

## Slide 1 — Title

- **InvoiceSentinel**: AI AP risk desk for PH SMEs
- Tagline: *Triage invoices before payment — catch ghost receipts in the queue*
- Team / track: BFSI
- Visual: navy risk-desk UI mock (inbox + risk card)

## Slide 2 — Problem (PH)

- SME and mid-market AP still rely on manual invoice eyeballing
- **Ghost / fictitious receipts** used to invent expenses or siphon payments
- Fraud and tax leakage scale: public reporting around a **₱25.5B** BIR-linked fake-invoice case as motivation for stronger *private-sector* controls
- Cost of a bad payment: hard cash out the door + audit remediation

### Footnotes (PH problem size)

1. Bureau of Internal Revenue (BIR) and media coverage of large-scale **fake or fraudulent receipt / invoice** schemes — cite the widely reported **₱25.5 billion** magnitude case as *motivating context* for AP controls (not as a claim that this product investigates that case).
2. World Bank / ADB / Bangko Sentral materials on MSME formalization and cash-flow fragility — late or fraudulent payables disproportionately hurt SMEs.
3. Industry AP surveys (global, adapted to PH): duplicate payments and vendor master weaknesses remain top leakage sources even in digitized finance stacks.

> On slides: footnote the ₱25.5B figure to a public news/BIR-adjacent source your team verified for the submission date; do not invent citations.

## Slide 3 — Why BFSI

- Accounts payable is a core **financial-controls** workflow
- Overlaps banking (payments), insurance (claims docs), and corporate finance
- Cup-aligned: Gemini multimodal on financial documents + Cloud Run deploy path

## Slide 4 — Solution

1. Upload PDF/image invoice  
2. **Gemini** extracts structured fields + risk flags with explanations  
3. Case inbox for humans: Approve / Escalate / Request docs  
4. Audit trail for every decision  

Positioning: **pre-payment risk triage**, not tax compliance software.

## Slide 5 — Risk signals

| Code | Meaning |
|------|---------|
| GHOST_VENDOR | Fictitious / thin vendor (TIN, brand, substance) |
| DUPLICATE_INVOICE | Same vendor + invoice # + amount |
| AMOUNT_MISMATCH / MATH_ERROR | Lines + tax ≠ total |
| TEMPLATE_LOOKING | Generic / low-substance layout |
| MISSING_FIELDS | Address, remittance, TIN gaps |
| UNUSUAL_PAYMENT_CHANGE | Optional banking-detail drift |

## Slide 6 — Architecture (GCP)

- Next.js web → FastAPI on **Cloud Run**
- **Gemini** (AI Studio / Vertex path) for multimodal JSON extraction
- MVP: JSON/SQLite; Prod: **Firestore** + **Cloud Storage** + Secret Manager
- Optional later: Firebase Auth

## Slide 7 — Demo flow (3 min)

Dashboard KPIs → ghost case explainability → escalate + audit → live/mock upload → disclaimer

## Slide 8 — Differentiation

- PH-first framing (TIN, PHP, ghost-receipt narrative)
- Explainable flags (not opaque “fraud score only”)
- Works **without** API key for judging (seed + mock)
- Honest scope: does **not** replace BIR

## Slide 9 — Roadmap

- Auth + roles  
- Vendor master / TIN enrichment  
- Payment-file export gates  
- Vertex AI + evaluation set of labeled PH invoices  

## Slide 10 — Ask / closing

- Built for Cup: Gemini + Cloud Run + BFSI impact story  
- Call to action: stop paying the ghost before the wire goes out  

---

## Speaker disclaimer (every pitch)

“InvoiceSentinel does not certify BIR compliance and is not a tax-authority system. It helps finance teams triage AP risk before payment.”
