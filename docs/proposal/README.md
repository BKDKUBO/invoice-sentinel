# Proposal source

`proposal.html` + `style.css` are the source for `../InvoiceSentinel-Proposal.pdf` (14 landscape 16:9 pages, the hackathon's "deck converted to PDF" format). `InvoiceSentinel-Proposal.docx` is the editable copy (also in Google Drive as a Google Doc).

- `assets/`: real screenshots of the live Cloud Run app (captured Oct 12, 2026 with headless Chrome/Playwright; demo reset afterwards) and `architecture.png`, rendered from `architecture.html`.
- Rebuild: `pip install playwright python-docx beautifulsoup4 && python build.py` (uses Chrome at `/usr/bin/google-chrome`).
- Placeholders still to fill are highlighted in yellow: team name, member names and roles, demo video link.
