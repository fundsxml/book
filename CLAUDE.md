# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is a **book-writing project**, not a software project. The book is *FundsXML — The European Standard for Fund Data Exchange* (subtitle: *A Practical Handbook for Fund Professionals*), based on FundsXML schema version 4.2.x, dated 2026. The master plan lives in `FundsXML_Book_TableOfContents.md`: 14 chapters across four parts (Foundations / FundsXML in Detail / Implementation and Practice / Outlook and Reference), plus appendices A–F and an index, targeting ~521 pages.

There is no test suite, but there is a small build layer: `polish_styles.py` is the single source of truth for the embedded CSS and idempotently rewrites the `<style>` block, injects a theme-toggle, and injects a per-chapter prev/next/contents navigation bar into every standalone HTML file. The rewrite is idempotent — a second run reports no changes (the strip regexes consume their own leading whitespace; `inject_nav` runs before `inject_theme` for a stable canonical order). `build_complete.sh` resolves its own directory (no hardcoded paths — works in any checkout or CI), concatenates the chapters into `FundsXML_Book_Complete.html` (stripping the per-chapter nav bars), generates the GitHub Pages landing page `index.html`, and then calls `node build_pdf.js` (Playwright) to regenerate `FundsXML_Book.pdf`. After any HTML edit, run `python3 polish_styles.py && bash build_complete.sh` to bring the bundled HTML, landing page and PDF back in sync.

The book is published at **https://fundsxml.github.io/book/** (repo `github.com/fundsxml/book`). `.github/workflows/build-and-deploy.yml` rebuilds everything on each PR (a sync check fails the PR if committed HTML drifted from `polish_styles.py`) and deploys to GitHub Pages on push to `master`. `FundsXML_Book.pdf` stays git-ignored and is rebuilt by CI. Contributor rules live in `CONTRIBUTING.md`; licensing is CC BY 4.0 for text (`LICENSE`) and MIT for code (`LICENSE-CODE`).

## File layout conventions

Each top-level artifact exists as a **pair** of files with the same stem:

- `FundsXML_Book_TableOfContents.md` ↔ `FundsXML_Book_TableOfContents.html`
- `ChapterNN.md` ↔ `ChapterNN.html` (zero-padded, e.g. `Chapter01.md`)

When editing a Markdown source, the corresponding HTML must be regenerated so the two stay in sync. When creating a new chapter, create both files.

The HTML files are **standalone, self-contained documents** with an embedded `<style>` block — there is no shared stylesheet, template engine, or static-site generator. New chapters should copy the `<head>`/`<style>` block from `Chapter01.html` verbatim so typography stays consistent across the book:

- Body font: Source Serif Pro / Source Serif 4 (serif)
- Headings: Inter (sans-serif)
- Accent colour `#0b5394`, ink `#1a1a1a`, callout background `#f3f6fb`, max-width `46em`

## Editorial conventions (follow these when writing)

These are derived from the existing `Chapter01.md` and must be matched in new material:

- **Language: British English.** Use *standardisation*, *organisation*, *recognised*, *behaviour*, *colour*, etc. Do not Americanise.
- **Running example:** the fictional **Europa Growth Fund** — a mid-sized Luxembourg-domiciled UCITS equity fund distributed across eleven European countries. It appears in every chapter as the continuous narrative thread; reuse it rather than inventing new example funds.
- **Chapter opening pattern:** chapter number and title, italic subtitle, a narrative "setting the scene" section, then a bulleted *"By the end of this chapter, you should be able to…"* list of learning outcomes.
- **Chapter closing pattern:** a `## N.9 Key Takeaways` (or similar) bullet list summarising the chapter's main points. Chapters typically end with a one-sentence pointer to the next chapter.
- **Section numbering:** `## 1.1`, `### 1.3.1`, etc. — hierarchical, matching the chapter number.
- **Tables:** use GitHub-flavoured Markdown tables, numbered and captioned as `**Table 1.3 — …**`.
- **Tone:** professional, explanatory, reflective; first-person plural ("we look at them in turn"). No marketing language, no emoji, no code before Chapter 2.
- **NO exercises inside chapters.** Despite Appendix F in the TOC ("Solutions to the Exercises"), the user has decided individual chapters must not contain exercise/practice-question sections. Keep key-takeaways and summaries; omit exercises entirely.
- **Chapter length** is specified in the TOC in pages (e.g. Chapter 1 = 25 pages, Chapter 6 = 45 pages). Treat these as target budgets when drafting.

## Cross-chapter consistency

The TOC prescribes how the material is partitioned. Before introducing a topic in a chapter, check the TOC summaries to confirm it belongs there and is not owned by a later chapter. Typical pitfalls:

- XML/XSD syntax belongs to Chapter 2 and later — Chapter 1 is deliberately technology-free.
- ControlData, Funds/Sub-Funds/Share Classes, Portfolio, Transactions, and Regulatory Modules (EMT/EPT/EET/EFT/TPT) each have a dedicated chapter (4–8). Don't pre-empt them.
- Tools (FreeXmlToolkit, Online Schema Viewer, CSV Converter, Generator, IDE integration) are Chapter 11's territory.
- Appendix D holds the complete schema-valid sample files for the Europa Growth Fund.

When updating the TOC, also update the matching HTML and any affected chapter cross-references.
