# Brief description

InvoiceSentinel is a pre-payment fraud and risk desk for Philippine SMEs. It catches ghost receipts, bank-change scams, duplicates, overbilling and split invoices before money leaves the account.

**Core AI:** Gemini 3.8 Flash reads invoice photos and PDFs into structured JSON. Deterministic checks then compare each invoice against the vendor master, purchase orders, TIN rules and BIR RR 7-2024 to give a repeatable risk score. A Google ADK agent uses those checks as tools. It answers in English or Tagalog, shows each step live, cites evidence, recommends PAY, HOLD or VERIFY, and drafts verification emails.

**Scalability:** Firebase Hosting serves invoicesentinel.web.app and sends requests to Next.js and FastAPI services on Cloud Run. Each service scales automatically with traffic and keeps one instance warm so responses start fast. Firestore, a serverless database, stores cases, vendors, POs, chats and audit trails without any servers to manage.

**Security:** Secret Manager holds the Gemini key, so it never appears in the code. Uploaded invoices stay in a private Cloud Storage bucket. Every decision is logged, and a person approves every payment.

Built by BKD KUBO for the Google Cloud AI Builder Cup 2026; not affiliated with other projects of similar name.
