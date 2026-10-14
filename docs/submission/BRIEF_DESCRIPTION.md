# Brief description (982 chars, form limit 1024)

InvoiceSentinel is a pre-payment fraud desk for Philippine SMEs, catching ghost receipts, bank-change scams, duplicates, overbilling and split invoices before payment.
Core AI: Gemini 3.8 Flash reads invoice photos and PDFs into structured JSON. Deterministic checks against the vendor master, POs, TIN rules and BIR RR 7-2024 give a repeatable risk score. A Google ADK agent uses these checks as tools, answers in English or Tagalog, cites evidence, recommends PAY/HOLD/VERIFY and drafts verification emails.
Scalability: Firebase Hosting serves the app and routes to Next.js and FastAPI services on Cloud Run, which autoscale with traffic. Firestore, a serverless database, stores cases, vendors, POs, chats and audit trails.
Security: Secret Manager holds the Gemini key, invoices stay in private Cloud Storage, every action is logged, and a person approves every payment.
Built by BKD KUBO for the Google Cloud AI Builder Cup 2026; not affiliated with similarly named projects.
