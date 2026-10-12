# InvoiceSentinel: Demo Video Script (target 2:50, hard max 2:55)

Google Cloud AI Builder Cup 2026 (Hack2skill, JAPAC) | Theme: BFSI
Video rules: English, publicly viewable link, 3:00 max.

Live app: https://invoicesentinel-web-1034883854575.asia-southeast1.run.app
Repo: https://github.com/BKDKUBO/invoice-sentinel

Judging weights this script is built around: GenAI use 40% | Problem/impact 25% | Innovation 25% | UX 10%.

Voiceover total: 381 words at about 140 wpm, which is about 2:45 spoken, leaving 5 to 10 s of breathing room for transitions.

---

## Script

| # | Time | ON SCREEN (exact clicks / visuals) | VOICEOVER | Words |
|---|------|------------------------------------|-----------|-------|
| 1 | 0:00 to 0:10 | **Hook.** Full-screen zoom on `samples/03-ghost-placeholder-tin.png` (letterhead, TIN, VAT line). At 0:05 hard cut to its case page: red **CRITICAL** badge, risk score **96**, `GHOST_VENDOR` card. Title lower-third: "InvoiceSentinel: AP risk triage before payment". | This invoice has a TIN, a VAT line, and a clean letterhead. It's fake. InvoiceSentinel flagged it before a single peso was paid. | 23 |
| 2 | 0:10 to 0:28 | **Problem.** Title card, dark navy. Three stat lines animate in, each with a footnote marker: "₱25.5B alleged tax loss, 4 ghost firms (2019 to 2021)¹" / "₱1.41B deficiencies: 23 corps, 56 officers, 17 CPAs bought ghost receipts²" / "68% of orgs saw an AP fraud attempt in 2024³". Footnotes in small text at bottom (see Sources). | Fake receipts are a real problem in the Philippines. The BIR has alleged about twenty-five billion pesos in tax losses from just four ghost firms. Globally, sixty-eight percent of organizations saw an accounts payable fraud attempt last year. Most SMEs have no fraud team. | 44 |
| 3 | 0:28 to 0:42 | **Dashboard.** Browser on live URL `/` (Dashboard). Cursor circles KPI strip: Cases this week, **₱ at risk = ₱144,500**, Open, Approved, Escalated. Hover the 5 seed cases. Click **Upload** in the nav. | InvoiceSentinel is a risk desk for accounts payable. It triages supplier invoices before payment. The dashboard shows this week's cases, with one hundred forty-four thousand pesos currently at risk. Let's add a new invoice. | 34 |
| 4 | 0:42 to 1:22 | **Live upload, ghost vendor (GenAI core).** Drag `03-ghost-placeholder-tin.png` onto "Drag & drop invoice PDF or image". Button shows "Analyzing…". **CUT** the wait (keep 1 to 2 s of spinner, then jump; optional "~20 s, sped up" caption). Case page loads: zoom on **Risk score 96, CRITICAL**. Scroll to **Extracted fields** (vendor, TIN `000-000-000-000`, invoice no., totals) and **Line items**. Scroll to **Explainable risk cards**: highlight `GHOST_VENDOR` (placeholder TIN) and the personal GCash payment card. | I'll drop in a supplier invoice image. Gemini 3.8 Flash reads it directly, with no OCR templates, and returns vendor, TIN, line items, and totals as structured fields. The score is ninety-six, critical. Every flag explains itself. The TIN is all zeros, a placeholder, so it's marked as a ghost vendor. And payment goes to a personal GCash number, not a business account. Gemini reasons across the whole document like a senior AP reviewer, and shows its evidence so an analyst can verify it in seconds. | 86 |
| 5 | 1:22 to 1:40 | **Bank-change scam.** Upload `05-bec-bank-change.png` (cut the wait). Case page: **95 CRITICAL**; highlight `UNUSUAL_PAYMENT_CHANGE` card quoting the "new bank details" text. | Next, a classic bank-change scam. The invoice says the supplier has new bank details, effective immediately. Gemini flags the unusual payment change and scores it ninety-five, critical. This is the trick that quietly drains SME accounts. | 36 |
| 6 | 1:40 to 1:58 | **VAT math error.** Upload `04-vat-math-wrong.png` (cut the wait). Case page: **65 HIGH**. Zoom on `MATH_ERROR` card; on-screen callout box: "VAT shown ₱7,860 vs correct 12% = ₱6,288". | Not every risk is fraud. Here, twelve percent VAT should be six thousand two hundred eighty-eight pesos, but the invoice charges seven thousand eight hundred sixty. Gemini extracts the numbers, and a deterministic check confirms the math. High risk. | 39 |
| 7 | 1:58 to 2:14 | **Quick montage (split screen or two fast cuts).** Left: `06-overbilled-bond-paper.png` case with `OVERBILLING` card, callout "₱2,450/ream, about 10x market". Right: `07-near-duplicate-acme.png` case with `DUPLICATE_INVOICE` card pointing at the seed Acme invoice. | It also catches overbilling. Bond paper at two thousand four hundred fifty pesos a ream is about ten times market price. And this near-copy of an earlier Acme invoice is flagged as a duplicate, so you never pay twice. | 39 |
| 8 | 2:14 to 2:34 | **Human decision + audit trail (UX).** Flash a legit case (`01-legit-vat-invoice.png`, pre-uploaded) showing **LOW, score 0 to 5**. Then open **Case inbox**, click the ghost vendor case, click **Escalate**. Scroll to **Audit trail**: new "escalated" entry with timestamp. Quick cut back to Dashboard: Escalated count +1. | Legitimate invoices score zero to five, so analysts aren't buried in false alarms. And a human always decides: approve, escalate, or request documents. I'll escalate the ghost vendor, and the audit trail records who did what, and when. | 38 |
| 9 | 2:34 to 2:52 | **Impact + tech close.** Architecture card: "Upload → Gemini 3.8 Flash (multimodal, structured JSON) → explainable flags + score → Case inbox → Approve / Escalate / Request docs → Audit trail". Logos/labels: Gemini, Cloud Run (asia-southeast1), Next.js, FastAPI, Secret Manager. Small disclaimer line: "AP risk triage before payment. Not a BIR or tax compliance tool." End card: live URL + GitHub repo. | InvoiceSentinel isn't a BIR replacement. It's the safety check before money moves. It's built on Gemini 3.8 Flash multimodal, with Next.js and FastAPI on Cloud Run in Asia Southeast, and the key in Secret Manager. Stop ghost invoices before you pay them. | 42 |

**End by 2:52. Do not exceed 2:55.**

### Sources (show as on-screen footnotes in section 2; keep the caveats)
1. Bureau of Internal Revenue, March 2023: about ₱25.5B in *alleged* tax losses linked to 4 ghost corporations, 2019 to 2021 (allegation, not a court finding).
2. Bureau of Internal Revenue, August 2025: ₱1.41B in tax deficiencies against 23 corporations, 56 officers, and 17 CPAs that allegedly bought ghost receipts.
3. Basware survey: 68% of organizations experienced an AP fraud attempt in 2024 (global survey, not PH-specific).

Caveat line under the footnotes: "Figures as publicly reported by BIR/Basware. InvoiceSentinel is AP triage, not a BIR tool."

---

## Pre-recording checklist

- [ ] **Warm both Cloud Run services** (min instances may be 0): open https://invoicesentinel-api-1034883854575.asia-southeast1.run.app/health and the web URL 2 to 3 minutes before recording; reload until fast. Confirm `/health` shows Gemini (live) mode, not mock.
- [ ] **Reset demo:** Dashboard → **Reset seed demo**. Confirm 5 seed cases and **₱ at risk = ₱144,500**.
- [ ] **Do a full dry run** of uploads 03, 05, 04, 06, 07, 01 and note the actual scores (expect 95 to 96 / 95 / 65 / OVERBILLING / DUPLICATE_INVOICE / 0 to 5). If any differ, update the on-screen callouts, not the facts.
- [ ] Upload 07 **after** the reset, so the seed Acme invoice exists for the duplicate match.
- [ ] Recommended: pre-record each upload as its own clip, then **Reset seed demo** again before recording the dashboard (section 3) and escalate (section 8) clips so the KPI numbers match the voiceover.
- [ ] Have the `samples/` folder open in a file manager window beside the browser for clean drag and drop.
- [ ] Browser: clean profile, no bookmarks bar, no extensions, 100% zoom (or 110% for readability), hide other tabs. Close notifications (Do Not Disturb).
- [ ] Prepare title card (section 2), callout boxes (sections 6 and 7), architecture/end card (section 9) as images in advance.
- [ ] Record voiceover separately in a quiet room with a decent USB mic; read at a calm pace (about 140 wpm).

## Recording tips

- **Recorder:** OBS Studio (free) or Loom/ScreenPal; edit in CapCut, DaVinci Resolve, or Clipchamp.
- **Resolution:** record at **1920x1080, 30 fps**; export MP4 (H.264), 1080p.
- **Cut the wait:** Gemini analysis takes about 10 to 34 s. Keep 1 to 2 s of "Analyzing…", then hard cut or speed ramp (8x) to the result. Add a tiny caption "analysis about 20 s, sped up" to stay honest.
- **Zoom and highlight:** use zoom-ins on the score badge, TIN, GCash line, and VAT numbers. Judges watch on laptops; small text must be readable.
- **Lead with GenAI (40%):** sections 1, 4, 5, 6 explicitly say what Gemini is doing (multimodal read, structured extraction, cross-document reasoning, explanations). Do not cut those lines first.
- **If running long,** trim in this order: section 7 right half (duplicate), then the false-positive line in section 8, then the last sentence of section 4.
- **Upload:** YouTube, visibility **Public**, English title, e.g. "InvoiceSentinel: Gemini AP fraud triage for PH SMEs | Google Cloud AI Builder Cup 2026". Verify the link in an incognito window and confirm runtime is ≤ 2:55.
- Add English captions (YouTube auto captions, then fix "GCash", "TIN", "BIR").
