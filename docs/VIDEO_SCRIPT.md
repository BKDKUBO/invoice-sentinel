# InvoiceSentinel: demo video script (target 2:50, hard limit 3:00)

Live app: https://invoicesentinel-web-1034883854575.asia-southeast1.run.app
Before you record: click **Reset demo**, then warm both pages once. Use a 1440×900 browser at 100% zoom with the system clock in Manila time. Every name and account shown is fictional.

| Time | Screen | Voice-over (about 150 wpm) |
|---|---|---|
| 0:00–0:15 | Cover slide, then the dashboard | "In the Philippines, ghost receipts are an industry. The BIR has filed cases alleging over ₱25 billion in lost taxes. For an SME, though, the real danger is simpler: paying a fake or redirected invoice. This is InvoiceSentinel." |
| 0:15–0:30 | Dashboard: KPI cards, risk trend, flag breakdown. Hover the PH-flag accent and the logo | "It's a pre-payment risk desk for accounts payable. At a glance you see ₱ at risk, open high-risk cases, the risk trend and which fraud patterns we're catching." |
| 0:30–0:50 | **Check an invoice** → stepper → **Try a sample** grid → click **09 Known vendor, new bank** | "No files needed: one click on Try a sample. This invoice comes from a supplier we already know, Northstar IT. Watch the steps: Gemini 3.8 Flash reads the image, then our code checks it against the vendor master, the PO and BIR rules." |
| 0:50–1:10 | Case page: critical score 90, risk card, then scroll to the **vendor master** table with the red bank-account row | "Critical, score 90. Everything matches: vendor, TIN, PO, line items. Everything except the bank account. The invoice says Metrobank; our verified master says BPI. That's a textbook payment-redirection scam, and a deterministic rule caught it, not a guess." |
| 1:10–1:40 | **Ask the case**: type "Ligtas ba itong bayaran?" Show the agent steps streaming (vendor master, PO, history, TIN, BIR), then the HOLD answer with evidence chips | "Now I ask in Tagalog: is it safe to pay? This is a Google ADK agent with seven read-only tools, and you can watch it work live: checking the vendor master, the PO, vendor history, the TIN, the BIR checklist. It answers in Tagalog: HOLD, with every claim tied to an evidence ID." |
| 1:40–2:00 | Set the language to **Tagalog** → **Draft verification email** | "One click drafts a verification email in Tagalog. Note the recipient: the contact on file in our master, never the one printed on the invoice. The code sets it, not the model, and nothing is sent automatically." |
| 2:00–2:15 | Scroll to the **BIR compliance checklist** (RR 7-2024) and the TIN badge | "The BIR RR 7-2024 checklist confirms the required invoice elements and validates the TIN. It's advisory: we support AP triage; we don't certify compliance." |
| 2:15–2:35 | Try a sample **12** (clean, 0) → then **13** → SPLIT_INVOICE high card | "Split invoices: sample 12 alone is clean. Sample 13, from the same vendor two days later, pushes the combined total over our approval limit, so it's flagged as a split invoice. Same input, same score: we ran 14 samples three times with zero variance." |
| 2:35–2:50 | Click **Escalate** → audit trail. Optionally flash the mobile view. Then the architecture slide | "The analyst decides and every step is logged. Under the hood it's all Google Cloud: Gemini 3.8 Flash, Google ADK, Cloud Run, Firestore, Cloud Storage and Secret Manager, at about thirty-one centavos per invoice. InvoiceSentinel: stop paying the ghost." |

## Recording tips
- The agent answer takes about 20–35 s. Keep recording and cut the wait in editing, leaving the streamed steps visible.
- If Gemini returns a temporary 503, click Retry; don't edit around a fake result.
- Run sample 12 before 13 (split detection needs both). Reset demo afterwards.
- End card: [TEAM NAME] · live URL · "Google Cloud AI Builder Cup 2026 · BFSI".
