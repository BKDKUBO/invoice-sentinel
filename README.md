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
| AI | Gemini via `google-generativeai` | `GEMINI_API_KEY` from AI Studio |
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
# optional: export GEMINI_API_KEY=... GEMINI_MODEL=gemini-2.0-flash
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
3. Default model: `gemini-2.0-flash` (override with `GEMINI_MODEL`).
4. The analyzer requests structured JSON: vendor, invoice_number, date, currency, totals, line_items, `risk_flags[]`, `overall_risk_score`.

Risk flag codes: `GHOST_VENDOR`, `DUPLICATE_INVOICE`, `AMOUNT_MISMATCH`, `TEMPLATE_LOOKING`, `MATH_ERROR`, `UNUSUAL_PAYMENT_CHANGE`, `MISSING_FIELDS`.

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
