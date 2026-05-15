#!/usr/bin/env node
/**
 * Build FundsXML_Book.pdf from FundsXML_Book_Complete.html.
 *
 * Uses Playwright's bundled Chromium in headless mode to render the book
 * with the print CSS, A4 page size, margins, page numbers, and a running
 * header. The cover page (@page cover { margin: 0 }) suppresses header/
 * footer via the CSS named-page rule + headerTemplate/footerTemplate
 * filtering.
 *
 * Run:  node build_pdf.js
 */

const path = require("path");
const fs = require("fs");

(async () => {
  const ROOT = __dirname;
  const INPUT = path.join(ROOT, "FundsXML_Book_Complete.html");
  const OUTPUT = path.join(ROOT, "FundsXML_Book.pdf");

  if (!fs.existsSync(INPUT)) {
    console.error(`error: ${INPUT} not found. Run build_complete.sh first.`);
    process.exit(1);
  }

  let chromium;
  try {
    ({ chromium } = require("playwright"));
  } catch (err) {
    console.error(
      "error: 'playwright' package not available. Install with 'npm i -g playwright' or 'npx playwright install chromium'."
    );
    process.exit(1);
  }

  const startedAt = Date.now();
  const browser = await chromium.launch();
  const page = await browser.newPage();

  const url = "file://" + INPUT;
  await page.goto(url, { waitUntil: "networkidle" });

  // Give the injected TOC-building and anchor scripts a moment to finish.
  await page.waitForTimeout(500);

  await page.emulateMedia({ media: "print" });

  // Running header: book title left, section (doc title) right.
  // Chromium substitutes <span class="title"> with the <title> tag content.
  const headerTemplate = `
    <div style="font-size:8pt;width:100%;padding:0 18mm;color:#555;font-family:Inter,Arial,sans-serif;display:flex;justify-content:space-between;align-items:baseline;border-bottom:0.5pt solid #cfd4d9;padding-bottom:2pt;">
      <span>FundsXML &mdash; The European Standard for Fund Data Exchange</span>
      <span class="title" style="font-style:italic;color:#0b5394;"></span>
    </div>`;

  const footerTemplate = `
    <div style="font-size:8pt;width:100%;padding:0 18mm;color:#555;font-family:Inter,Arial,sans-serif;text-align:center;">
      <span class="pageNumber"></span> &#8201;/&#8201; <span class="totalPages"></span>
    </div>`;

  await page.pdf({
    path: OUTPUT,
    format: "A4",
    printBackground: true,
    displayHeaderFooter: true,
    margin: {
      top: "22mm",
      bottom: "20mm",
      left: "18mm",
      right: "18mm",
    },
    headerTemplate,
    footerTemplate,
  });

  await browser.close();

  const sizeMB = (fs.statSync(OUTPUT).size / (1024 * 1024)).toFixed(2);
  const secs = ((Date.now() - startedAt) / 1000).toFixed(1);
  console.log(`Done. ${OUTPUT} (${sizeMB} MB, ${secs}s)`);
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
