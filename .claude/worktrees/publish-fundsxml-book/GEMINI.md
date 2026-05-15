# FundsXML Book Project: GEMINI Context

This repository is a **book-writing project** for *FundsXML — The European Standard for Fund Data Exchange* (subtitle: *A Practical Handbook for Fund Professionals*), based on FundsXML schema version 4.2.x (dated 2026).

## Directory Overview
The project consists of 14 chapters, 5 appendices, and an index, all authored in Markdown with corresponding standalone HTML renditions. It is a documentation-centric project with a specialised workflow for maintaining consistency across a ~521-page technical handbook.

## Key Files
- **`FundsXML_Book_TableOfContents.md`**: The master plan, containing chapter summaries, page budgets, and the overall structure.
- **`ChapterNN.md` / `ChapterNN.html`**: The primary content files (e.g., `Chapter01.md`). Each chapter exists as a pair that must be kept in sync.
- **`Appendix[A-E].md` / `Appendix[A-E].html`**: Reference materials, glossaries, and sample files.
- **`FundsXML4.xsd` / `xmldsig-core-schema.xsd`**: The XML schema definitions that the book documents.
- **`build_complete.sh`**: A shell script that concatenates all individual HTML files into a single, comprehensive `FundsXML_Book_Complete.html`.
- **`Index.md`**: The source for the book's index.
- **`CLAUDE.md`**: Contains detailed editorial and technical guidance for AI agents.

## Usage & Workflow

### Editing Workflow
1.  **Source First**: Always edit the `.md` files.
2.  **HTML Sync**: After editing a Markdown file, regenerate the corresponding `.html` file. 
3.  **Standalone HTML**: HTML files are self-contained. When creating a new chapter, copy the `<head>` and `<style>` blocks from `Chapter01.html` to maintain consistent typography (Source Serif Pro for body, Inter for headings).
4.  **Full Build**: Run `./build_complete.sh` to generate the final consolidated book.

### Editorial Conventions
- **Language**: British English (e.g., *standardisation*, *colour*).
- **Example**: Use the **Europa Growth Fund** (a Luxembourg-domiciled UCITS equity fund) as the consistent narrative example across all chapters.
- **Structure**:
    - **Chapters**: Start with an italic subtitle, a narrative intro, and learning outcomes. End with "Key Takeaways" and a pointer to the next chapter.
    - **Numbering**: Section headers use hierarchical numbering (e.g., `## 1.1`, `### 1.1.1`).
    - **No Exercises**: Individual chapters must not contain exercises (despite the TOC mentioning Appendix F).
- **Tone**: Professional, explanatory, and reflective; use first-person plural ("we").

### Formatting
- **Tables**: GitHub-flavoured Markdown tables, numbered and captioned (e.g., `**Table 1.1 — ...**`).
- **Styles**: Accent colour `#0b5394`, ink `#1a1a1a`, callout background `#f3f6fb`, max-width `46em`.
