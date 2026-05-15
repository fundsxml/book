# FundsXML — The European Standard for Fund Data Exchange

*A Practical Handbook for Fund Professionals*
Based on FundsXML Schema Version 4.2.x · 2026

This repository contains the full source of the book *FundsXML — The European
Standard for Fund Data Exchange*: 14 chapters across four parts, appendices A–E,
and an index. It is published openly so the fund-data community can read it
freely and propose improvements.

## Read the book

The book is published with GitHub Pages:

**→ https://fundsxml.github.io/book/**

From the landing page you can:

- **Read the complete book online** as a single scrollable page
  (`FundsXML_Book_Complete.html`)
- **Download the PDF** (`FundsXML_Book.pdf`)
- **Open individual chapters** — each chapter and appendix is a standalone page
  with previous / next / contents navigation, so you can scroll through them
  one at a time

## Repository layout

Every artifact exists as a `.md` / `.html` pair with the same stem
(`Chapter01.md` ↔ `Chapter01.html`, etc.). The Markdown is the editorial
source; the HTML is the rendered, self-contained page (embedded CSS, no
external assets beyond the logo).

| Path | Purpose |
|------|---------|
| `ChapterNN.md` / `.html` | The 14 chapters |
| `AppendixX.md` / `.html` | Appendices A–E |
| `Index`, `ManagementSummary`, `TitlePage`, `FundsXML_Book_TableOfContents` | Front/back matter |
| `polish_styles.py` | Single source of truth for the embedded CSS, theme toggle, and per-chapter navigation; idempotently rewrites every HTML file |
| `build_complete.sh` | Concatenates everything into `FundsXML_Book_Complete.html`, generates `index.html`, then builds the PDF |
| `build_pdf.js` | Playwright/Chromium PDF renderer |
| `examples/` | Code samples (C#, Java, JavaScript, Python, XSLT) |
| `*.xsd`, `europa_growth_fund.xml` | FundsXML schema and the running-example fund |

`FundsXML_Book.pdf` is **not** committed — it is regenerated on every build and
published to GitHub Pages by CI.

## Building locally

Requirements: Python 3.10+, Node.js 18+, and Playwright's Chromium.

```bash
npm install
npx playwright install --with-deps chromium
python3 polish_styles.py        # refresh CSS / theme / chapter nav in every HTML
bash build_complete.sh          # build complete HTML + index.html + PDF
```

`python3 polish_styles.py --check` does a dry run and reports what would change.
The rewrite is idempotent: a second run reports no changes.

## Contributing

Corrections and improvements are very welcome via pull request. Please read
[CONTRIBUTING.md](CONTRIBUTING.md) first — the key rule is that you must edit
**both** the `.md` and its matching `.html`, run the build, and commit the
regenerated files.

## Licence

- **Book text** (`*.md`, `*.html`, this README): Creative Commons
  Attribution 4.0 International (CC BY 4.0) — see [LICENSE](LICENSE).
- **Code** (`examples/`, build scripts): MIT — see [LICENSE-CODE](LICENSE-CODE).

When reusing the text, attribute it as *“FundsXML — The European Standard for
Fund Data Exchange”* with a link back to this repository.
