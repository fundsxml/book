# Contributing

Thank you for helping improve *FundsXML — The European Standard for Fund Data
Exchange*. Corrections, clarifications, and new material are welcome through
pull requests.

## The one rule that matters

Every artifact is a **`.md` / `.html` pair**. There is **no Markdown→HTML
converter** in this repository — the HTML is maintained alongside the Markdown.
When you change content you must:

1. Edit the Markdown source (e.g. `Chapter06.md`).
2. Apply the **same** change to the matching HTML (`Chapter06.html`), keeping
   the existing structure and classes.
3. Run the build so styling, theme toggle, navigation, the complete book and
   the PDF stay in sync:

   ```bash
   python3 polish_styles.py && bash build_complete.sh
   ```

4. Commit the Markdown, the HTML, and the regenerated
   `FundsXML_Book_Complete.html` and `index.html`. (`FundsXML_Book.pdf` is
   git-ignored and rebuilt by CI — do not commit it.)

CI runs `python3 polish_styles.py --check` on every pull request; if the
committed HTML is not in sync with `polish_styles.py`, the check fails.

## Editorial conventions

These keep the book consistent — please match them:

- **British English** throughout: *standardisation*, *organisation*,
  *recognised*, *behaviour*, *colour*, etc. Do not Americanise.
- **Running example:** the fictional **Europa Growth Fund** (a mid-sized
  Luxembourg-domiciled UCITS equity fund distributed across eleven European
  countries) is the continuous thread. Reuse it rather than inventing new
  example funds.
- **Tone:** professional, explanatory, reflective; first-person plural. No
  marketing language, no emoji.
- **Section numbering** is hierarchical and matches the chapter number
  (`## 6.1`, `### 6.3.1`).
- **Tables** are GitHub-flavoured Markdown, numbered and captioned
  (`**Table 6.3 — …**`).
- **No exercises** inside chapters. Keep key-takeaways / summary sections.
- Respect the **chapter ownership** described in
  `FundsXML_Book_TableOfContents.md`: do not introduce a topic in a chapter
  that a later chapter owns.

## Pull request checklist

The pull-request template repeats this — please confirm each item:

- [ ] `.md` and matching `.html` both updated
- [ ] `python3 polish_styles.py && bash build_complete.sh` run; regenerated
      files committed
- [ ] `python3 polish_styles.py --check` reports no further changes
- [ ] British English; Europa Growth Fund used for examples
- [ ] Cross-references and the table of contents updated if structure changed

## Licensing of contributions

By contributing you agree that your text contributions are licensed under
CC BY 4.0 and any code contributions under MIT, consistent with this
repository's [LICENSE](LICENSE) and [LICENSE-CODE](LICENSE-CODE).
