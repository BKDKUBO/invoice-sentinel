# InvoiceSentinel: demo video script (v3, target 2:58–3:00, hard limit 3:00)

Live app: **https://invoicesentinel.web.app** (Firebase Hosting → Cloud Run). Record from this URL.
Before recording: **Reset demo**, then load each page once to warm it. Use 1440×900. All data is fictional.

| # | Screen | Voice-over |
|---|---|---|
| 1 | Proposal cover (BKD KUBO logo) → problem slide (BIR ghost-receipt figures) | In the Philippines, ghost receipts are an industry. The BIR has filed cases alleging over twenty-five billion pesos in lost taxes, and in 2025 it went after the companies that bought them: twenty-three firms, their officers and their accountants. For a small business with no fraud team, one fake or redirected invoice is cash out the door. This is InvoiceSentinel, by team BKD KUBO. |
| 2 | Dashboard at invoicesentinel.web.app: KPI cards, risk trend, flag breakdown | It's live at invoicesentinel dot web dot app: a pre-payment risk desk for accounts payable. At a glance: pesos at risk, open high-risk cases, the risk trend, and the fraud patterns we're catching. |
| 3 | Check an invoice → Try a sample → 09 Known vendor, new bank (analysis progress steps) | No files needed. One click on Try a sample. This invoice is from Northstar IT, a supplier we already know. Gemini 3.8 Flash reads the image, then our code checks it against the vendor master, the purchase order and BIR rules. |
| 4 | Case: critical 90 → vendor master table, red bank-account row (BPI vs Metrobank) | Critical, score ninety. Vendor, TIN, PO and line items all match, except the bank account. The invoice says Metrobank; our verified master says BPI. That's a textbook payment-redirection scam, caught by a deterministic rule. |
| 5 | Ask the case: "Ligtas ba itong bayaran?" → agent steps stream → Tagalog HOLD with evidence | Now I ask in Tagalog: is this safe to pay? A Google ADK agent with seven read-only tools works live: checking the vendor master, the PO, vendor history, the TIN and the BIR checklist. It answers in Tagalog: HOLD, with every claim tied to evidence. |
| 6 | Email language Tagalog → Draft verification email (to contact on file) | One click drafts a verification email in Tagalog. It goes to the contact on file in our vendor master, never the one printed on the invoice. Code sets the recipient, and nothing is sent automatically. |
| 7 | BIR RR 7-2024 checklist + valid-TIN badge | The BIR RR 7-2024 checklist confirms the required invoice elements and validates the TIN. It's advisory: we support triage; we don't certify compliance. |
| 8 | Try a sample 12 (clean) → 13 → SPLIT_INVOICE high card | Split invoices. Sample twelve alone is clean. Sample thirteen, from the same vendor two days later, pushes the combined total over the approval limit, so it's flagged as a split invoice. |
| 9 | Note → Escalate → audit trail | The analyst adds a note and escalates. Every decision lands in the audit trail. |
| 10 | Submission deck, Performance slide (11): benchmark (14 samples × 3 runs, zero spread; flag detection table) | Is it reliable? We ran fourteen test invoices three times each. Every one landed in its expected band, with zero score variance, and every expected fraud flag was detected. |
| 11 | Submission deck, Architecture slide (7): architecture (Firebase Hosting → Cloud Run, Gemini, ADK, Firestore, Cloud Storage) | Under the hood, it's all Google: Firebase Hosting in front of Cloud Run for the web app and API, Gemini 3.8 Flash to read invoices, Google ADK for the agent, Firestore for cases and audit trails, and Cloud Storage for files. About thirty-one centavos per invoice. |
| 12 | End card: BKD KUBO · invoicesentinel.web.app · Google Cloud AI Builder Cup 2026 · BFSI | InvoiceSentinel. Stop paying the ghost. Try it live at invoicesentinel dot web dot app. |

## Editing notes
- Trim the ~20 s analysis waits and the email-draft wait, and label each cut on screen. Speed up the agent run slightly (about 1.2×) but keep every streamed step visible. Show only real results.
- Run sample 12 before 13. Reset demo afterwards.
- Reference draft: `InvoiceSentinel-Demo-Draft-v3.mp4` (AI voiceover, burned-in captions). Built with `invoice-sentinel-video/v3` (`rec2.py`, `tts.py`, `build3.py`).
