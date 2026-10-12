# InvoiceSentinel

**AI accounts-payable risk desk for Philippine SMEs** — Google Cloud AI Builder Cup 2026 (BFSI theme).

Upload invoices/receipts (PDF/PNG/JPG) → Gemini multimodal extracts fields and flags ghost/fictitious vendors, duplicates, amount mismatches, and other AP anomalies → human-in-the-loop case inbox (Approve / Escalate / Request docs) with explainable risk cards and an audit trail.

> **Disclaimer:** InvoiceSentinel is **AP risk triage before payment**. It does **not** claim BIR compliance, does **not** replace the Bureau of Internal Revenue or any tax authority, and must not be marketed as a tax-filing or e-invoicing compliance product.

## Why this exists (PH context)

Ghost and fictitious receipts remain a material fraud and leakage risk for Philippine businesses. High-profile enforcement actions — including cases publicly reported in the **₱25.5B** range involving fake invoices/receipts — underscore how fabricated vendor documents can inflate deductible expenses and move cash. SMEs often lack dedicated fraud teams; a lightweight multimodal AP desk that **triages before payment** closes that gap without pretending to be a regulator.

## Theme

**BFSI** (Banking, Financial Services & Insurance) — finance operations / AP controls for SMEs and mid-market finance teams.

## Architecture

| Layer | Stack | Notes |
|-------|--------|--------|
| `web/` | Next.js 14 App Router, TypeScript, Tailwind | Finance risk-desk UI (navy/slate) |
| `api/` | Python FastAPI | Intended for Cloud Run |
| AI | Gemini via `google-genai` | `GEMINI_API_KEY` from AI Studio |
| Persistence (MVP) | JSON under `data/` | No Firebase credentials required locally |
| Persistence (prod map) | Firestore + Cloud Storage | Documented below |

```
invoice-sentinel/
├── api/                 # FastAPI + Gemini/mock analyzer
├── web/                 # Next.js UI
├── data/
│   └── seed-cases.json  # 5 demo cases (2 clean, 3 risky)
├── docs/
│   └── PROPOSAL_OUTLINE.md
├── .env.example
└── README.md
```

### Production mapping (Firebase / GCP)

| Local MVP | Production |
|-----------|------------|
| `data/cases.json` | Firestore collection `cases` |
| `data/uploads/` | Cloud Storage bucket `gs://…/invoices/` |
| Env `GEMINI_API_KEY` | Secret Manager + Cloud Run env |
| No auth | Firebase Auth / Identity Platform (see TODOs) |

## Prerequisites

- Node.js 20+
- Python 3.11+
- Optional: [Google AI Studio](https://aistudio.google.com/) API key for live Gemini analysis

## Local run

### 1. Environment

```bash
cd /workspace/invoice-sentinel   # or your clone path
cp .env.example .env
# Optionally set GEMINI_API_KEY=... for live multimodal analysis
```

Without `GEMINI_API_KEY`, the API runs in **mock mode** (filename heuristics + seed data) so judges can walk the full UI.

### 2. API (port 8080)

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# DATA_DIR points at monorepo data/
export DATA_DIR=../data UPLOAD_DIR=../data/uploads CORS_ORIGINS=http://localhost:3000
# optional: export GEMINI_API_KEY=... GEMINI_MODEL=gemini-3.8-flash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Health check: `curl http://localhost:8080/health`

### 3. Web (port 3000)

```bash
cd web
cp .env.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8080
npm install
npm run dev
```

Open http://localhost:3000

### Demo without API key

1. Start API + web (leave `GEMINI_API_KEY` empty).
2. Dashboard shows seed cases; **₱ at risk** sums high/critical open totals.
3. Inbox → open **Rapid Trade Solutions PH** (ghost vendor) or math-error catering case → read risk cards → **Escalate** / **Approve** / **Request docs**.
4. Upload a file named e.g. `ghost-receipt.pdf` or `math-error.png` to trigger mock flags.
5. **Reset seed demo** on the dashboard to restore `data/seed-cases.json`.

## Cloud Run deploy outline

**API** (from repo root):

```bash
gcloud run deploy invoice-sentinel-api \
  --source . \
  --dockerfile api/Dockerfile \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest \
  --set-env-vars=DATA_DIR=/data,CORS_ORIGINS=https://YOUR_WEB_URL
```

Or build explicitly:

```bash
docker build -f api/Dockerfile -t REGION-docker.pkg.dev/PROJECT/REPO/invoice-sentinel-api .
docker push ...
gcloud run deploy invoice-sentinel-api --image ... --region asia-southeast1
```

**Web:**

```bash
cd web
docker build --build-arg NEXT_PUBLIC_API_URL=https://YOUR_API_URL -t .../invoice-sentinel-web .
gcloud run deploy invoice-sentinel-web --image ... --region asia-southeast1
```

Attach a GCS volume or switch the store to Firestore before production traffic.

## Gemini / AI Studio

1. Create an API key in Google AI Studio.
2. Set `GEMINI_API_KEY` in `.env` / Cloud Run secrets.
3. Default model: `gemini-3.8-flash` (override with `GEMINI_MODEL`).
4. The analyzer requests structured JSON: vendor, invoice_number, date, currency, totals, line_items, `risk_flags[]`, `overall_risk_score`.

Risk flag codes: `GHOST_VENDOR`, `DUPLICATE_INVOICE`, `AMOUNT_MISMATCH`, `OVERBILLING`, `TEMPLATE_LOOKING`, `MATH_ERROR`, `UNUSUAL_PAYMENT_CHANGE`, `MISSING_FIELDS`, plus the deterministic vendor-master / PO codes `UNKNOWN_VENDOR`, `VENDOR_TIN_MISMATCH`, `MISSING_PO`, `PO_MISMATCH` (see below).

## 3-minute demo script

| Time | Action |
|------|--------|
| 0:00 | Open dashboard — show cases this week, **₱ at risk**, approved vs escalated. Mention BFSI / PH SME AP desk. |
| 0:40 | Inbox — severity badges; open ghost vendor case; read explainable cards (TIN zeros, vague fee). |
| 1:20 | Open math-error case — show amount mismatch evidence. |
| 1:50 | Hit **Escalate** — audit trail updates. |
| 2:10 | Upload (or note mock mode) — drag a PDF; show extraction + flags. |
| 2:40 | Disclaimer slide: triage before payment, **not** a BIR tool. Cite ₱25.5B motivation briefly. |

## Seed data

`data/seed-cases.json` — 5 cases:

1. Acme office supplies — clean  
2. Manila Bay Logistics — clean  
3. Duplicate Acme INV-88421 — `DUPLICATE_INVOICE`  
4. Rapid Trade Solutions — `GHOST_VENDOR` / template / missing fields  
5. Cebu catering — `AMOUNT_MISMATCH` / `MATH_ERROR`

## Vendor master & PO matching

After Gemini extracts the invoice (including vendor TIN, the **pay-to account** and any **PO number**), `api/master.py` runs deterministic checks against an approved-vendor master and purchase-order register (fictional seed data in `api/seed/seed-vendors.json` and `api/seed/seed-pos.json`; runtime copies in `DATA_DIR/vendors.json` / `pos.json`, restored by `POST /api/reset-demo`).

| Check | Flag | Severity |
|---|---|---|
| Vendor not in master | `UNKNOWN_VENDOR` (or strengthens an existing `GHOST_VENDOR`) | medium |
| Known vendor, different TIN | `VENDOR_TIN_MISMATCH` (≤2 digits off = likely OCR misread → low) | high |
| TIN belongs to another vendor name | `VENDOR_TIN_MISMATCH` | high |
| Pay-to account not one of the vendor's verified accounts | `UNUSUAL_PAYMENT_CHANGE` with call-back contact from the master | critical |
| Cited PO does not exist | `MISSING_PO` | high |
| Qty / unit price / subtotal above the PO by more than 5%, or line not on PO | `PO_MISMATCH` with specifics | high |

Every flag carries `expected: … | found: …` evidence, and each case has a **Matched against vendor master / PO** panel (`GET /api/cases/{id}/matching`; computed live for older/seed cases). Invoices without a PO number are treated as non-PO spend (no flag). The score-floor rules still apply (high ≥ 65, critical ≥ 85).

Manage data at **/vendors** in the web app, or via `GET/POST /api/vendors`, `DELETE /api/vendors/{id}`, `GET/POST /api/pos`, `DELETE /api/pos/{po_number}`.

Test samples `samples/09-known-vendor-new-bank.png`, `10-exceeds-po-qty.png`, `11-nonexistent-po.png` exercise these checks (`python samples/run_round.py`).

## Ask the case (Gemini chat) & verification email drafts

Each case page has an **Ask the case** panel (`POST /api/cases/{id}/ask`, history at `GET /api/cases/{id}/chat`, stored in `DATA_DIR/chats.json`, cleared by reset-demo). Gemini gets an evidence pack: **E1** extraction, **E2** flags + evidence, **E3** score/status, **E4** vendor-master record, **E5** matched PO, **E6** this vendor's other invoices, **E7** master/PO match checks, plus **IMG** (the uploaded invoice image). It answers only from that evidence, cites IDs like `[E4]`, states what's missing, and ends with **PAY / HOLD / VERIFY**. It never suggests contacting the vendor via details printed on the invoice.

- Replies in the user's language (English, Tagalog, Taglish, Cebuano, Bahasa, Thai, Vietnamese, …); a language picker overrides (`language` field; `auto` = match).
- Suggested chips: "Is this safe to pay?", "What changed vs this vendor's past invoices?", "What should I verify first?", "Does this match the PO?".
- **Draft verification email** (`POST /api/cases/{id}/draft-email`, `{language}`): addressed to the vendor's contact **on file** in the vendor master; if the vendor isn't in the master it drafts an **internal escalation memo** to the Finance Manager instead. Shown with a Copy button — nothing is ever sent.
- Same retry policy as the analyzer (503/429 retried); if Gemini still fails the API returns HTTP 503 and no mock answer is saved.

Screenshots: `docs/proposal/assets/ask-*.png`.

## API surface

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness + Gemini mode |
| GET | `/api/dashboard` | KPI strip |
| GET | `/api/cases` | List |
| GET | `/api/cases/{id}` | Detail |
| POST | `/api/analyze` | multipart file upload |
| POST | `/api/cases/{id}/action` | approve / escalate / request_docs |
| POST | `/api/reset-demo` | Restore seed |

## TODOs (post-MVP)

- [ ] Firebase Auth / Identity Platform wiring (login, role: analyst vs approver)
- [ ] Firestore + Cloud Storage adapters (replace JSON store)
- [ ] Vendor master / TIN lookup enrichment
- [ ] Email “request docs” notifications
- [ ] Hardening: virus scan uploads, signed URLs, rate limits

## License

Demo / hackathon MVP — not for production use without security review.

## Deploy (Google Cloud Run)

**Live demo**
- Web: https://invoicesentinel-web-1034883854575.asia-southeast1.run.app
- API: https://invoicesentinel-api-1034883854575.asia-southeast1.run.app (`/health`)

Project `gen-lang-client-0252871691`, region `asia-southeast1`. Redeploy with:

```bash
./deploy.sh   # PROJECT / REGION env vars override defaults
```

- **API** (`invoicesentinel-api`): built from `api/Dockerfile.standalone` via `gcloud run deploy --source`; 1 vCPU / 512Mi, 0–2 instances, 120 s timeout, public. `GEMINI_API_KEY` comes from Secret Manager (`gemini-api-key`), mounted as an env var.
- **Web** (`invoicesentinel-web`): built with Cloud Build (`deploy/cloudbuild-web.yaml`) because `NEXT_PUBLIC_API_URL` is inlined at build time. If the API URL changes, rebuild the web.
- **CORS**: the API's `CORS_ORIGINS` is set to the web service URLs.
- **Data is ephemeral**: cases are local JSON inside the container. Each new instance starts from the 5 seed cases baked into the image; uploads and actions are lost when an instance scales to zero or restarts. Use `POST /api/reset-demo` (or the Reset button) before a demo. With up to 2 instances, two instances can briefly show different case lists.
- **Cost guard**: a USD 8 (~PHP 500) budget alert is set on the billing account (50/90/100% thresholds).
