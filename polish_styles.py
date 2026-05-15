#!/usr/bin/env python3
"""Apply the polished CSS block to every FundsXML book HTML file.

The book is a collection of standalone HTML documents with embedded <style>
blocks. This script owns the canonical stylesheet and rewrites the <style>
block of each target file idempotently, leaving <body> and scripts untouched.

Three style variants are kept in sync here:
  * BASE — chapters, appendices, Index, ManagementSummary.
  * TITLE — the bespoke TitlePage layout.
  * TOC   — the FundsXML_Book_TableOfContents card layout.

The Complete-book CSS lives inside build_complete.sh and is built by
concatenating BASE + COVER_EXTRA; run build_complete.sh after this script.

Usage:
    python3 polish_styles.py             # rewrite every known file
    python3 polish_styles.py --check     # dry-run, print what would change
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

STYLE_OPEN = "<style>"
STYLE_CLOSE = "</style>"


# ---------------------------------------------------------------------------
# CSS blocks
# ---------------------------------------------------------------------------

BASE_CSS = """\
  :root {
    --ink: #1a1a1a;
    --ink-soft: #444;
    --ink-muted: #6b7280;
    --accent: #0b5394;
    --accent-soft: #e3ecf6;
    --accent-hover: #083d73;
    --rule: #d0d7de;
    --rule-soft: #e8ecf1;
    --bg: #fbfbf8;
    --paper: #ffffff;
    --callout: #f3f6fb;
    --row-alt: #f6f8fa;
    --code-bg: #f4f6f9;
    --code-ink: #22272e;
    --tip: #1a7f4b;
    --tip-bg: #effaf3;
    --warn: #a85a00;
    --warn-bg: #fff5e6;
    --example: #5b4ab3;
    --example-bg: #f1eefb;
    --shadow-sm: 0 1px 2px rgba(15,23,42,0.04);
    --shadow-md: 0 2px 8px rgba(15,23,42,0.08);
  }
  html[data-theme="dark"] {
    --ink: #e6e8eb;
    --ink-soft: #b1b6bd;
    --ink-muted: #858a93;
    --accent: #79b8ff;
    --accent-soft: #17304b;
    --accent-hover: #a8d0ff;
    --rule: #2e333b;
    --rule-soft: #24282f;
    --bg: #101214;
    --paper: #191c1f;
    --callout: #1b2432;
    --row-alt: #171a1e;
    --code-bg: #161a1f;
    --code-ink: #d9dde3;
    --tip: #6bd494;
    --tip-bg: #122820;
    --warn: #e7a76b;
    --warn-bg: #2b1f12;
    --example: #b4a6f4;
    --example-bg: #231d37;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
    --shadow-md: 0 2px 10px rgba(0,0,0,0.45);
  }
  html[data-theme="dark"] img { filter: brightness(0.92) contrast(1.05); }

  html {
    -webkit-text-size-adjust: 100%;
    scroll-behavior: smooth;
  }
  body {
    font-family: "Source Serif Pro", "Source Serif 4", Georgia, "Times New Roman", serif;
    font-size: 18px;
    line-height: 1.65;
    color: var(--ink);
    background: var(--bg);
    max-width: 46em;
    margin: 3em auto;
    padding: 0 1.5em;
    hyphens: auto;
    hyphenate-limit-chars: 7 3 3;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    font-feature-settings: "kern", "liga", "calt";
  }
  ::selection { background: var(--accent-soft); color: var(--ink); }

  h1, h2, h3, h4 {
    font-family: "Inter", -apple-system, "Helvetica Neue", Arial, sans-serif;
    color: var(--ink);
    line-height: 1.25;
    margin-top: 2em;
    scroll-margin-top: 1.5em;
    font-feature-settings: "kern", "liga";
    letter-spacing: -0.005em;
  }
  h1 {
    font-size: 2.1em;
    border-bottom: 3px solid var(--accent);
    padding-bottom: 0.3em;
    margin-top: 0;
    letter-spacing: -0.015em;
  }
  h1 .subtitle {
    display: block;
    font-size: 0.55em;
    font-weight: 400;
    font-style: italic;
    color: var(--ink-soft);
    margin-top: 0.4em;
    letter-spacing: 0;
  }
  h2 {
    font-size: 1.45em;
    margin-top: 2.4em;
    border-bottom: 1px solid var(--rule);
    padding-bottom: 0.2em;
  }
  h3 { font-size: 1.15em; color: var(--accent); }
  h4 { font-size: 1em; color: var(--ink-soft); }

  p {
    margin: 0.9em 0;
    text-align: justify;
    text-justify: inter-word;
    orphans: 2;
    widows: 2;
  }

  ul, ol { padding-left: 1.4em; }
  li { margin: 0.35em 0; }
  li::marker { color: var(--accent); }

  strong { color: var(--ink); font-weight: 600; }
  em { color: var(--ink-soft); }

  hr {
    border: none;
    border-top: 1px solid var(--rule);
    margin: 2.4em 0;
  }

  a {
    color: var(--accent);
    text-decoration: underline;
    text-decoration-thickness: 1px;
    text-decoration-color: rgba(11, 83, 148, 0.35);
    text-underline-offset: 0.18em;
    transition: color 0.15s ease, text-decoration-color 0.15s ease;
  }
  a:hover {
    color: var(--accent-hover);
    text-decoration-color: var(--accent);
  }
  a:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
    border-radius: 2px;
  }
  html[data-theme="dark"] a { text-decoration-color: rgba(121, 184, 255, 0.4); }

  table {
    border-collapse: collapse;
    width: 100%;
    margin: 1.8em 0;
    font-size: 0.92em;
    font-family: "Inter", -apple-system, sans-serif;
    font-variant-numeric: tabular-nums lining-nums;
    background: var(--paper);
    border-radius: 4px;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
  }
  caption {
    caption-side: bottom;
    text-align: left;
    color: var(--ink-soft);
    font-family: "Inter", sans-serif;
    font-size: 0.9em;
    font-style: italic;
    padding: 0.6em 0.2em 0;
  }
  th, td {
    text-align: left;
    padding: 0.6em 0.85em;
    border-bottom: 1px solid var(--rule-soft);
    vertical-align: top;
  }
  th {
    background: var(--callout);
    border-bottom: 2px solid var(--accent);
    font-weight: 600;
    color: var(--ink);
  }
  tbody tr:nth-child(even) { background: var(--row-alt); }
  tbody tr:hover { background: var(--accent-soft); }
  tbody tr:last-child td { border-bottom: none; }

  blockquote {
    margin: 1.4em 0;
    padding: 1em 1.2em;
    background: var(--callout);
    border-left: 4px solid var(--accent);
    color: var(--ink-soft);
    font-size: 0.95em;
    border-radius: 0 4px 4px 0;
  }
  blockquote p { margin: 0.4em 0; }
  blockquote p:first-child { margin-top: 0; }
  blockquote p:last-child { margin-bottom: 0; }
  blockquote.tip { background: var(--tip-bg); border-color: var(--tip); }
  blockquote.warning { background: var(--warn-bg); border-color: var(--warn); color: var(--ink); }
  blockquote.example { background: var(--example-bg); border-color: var(--example); }

  code {
    font-family: "JetBrains Mono", "Source Code Pro", "SF Mono", Menlo, Consolas, monospace;
    font-size: 0.9em;
    background: var(--code-bg);
    color: var(--code-ink);
    padding: 0.1em 0.35em;
    border-radius: 3px;
    font-feature-settings: "liga" 0, "calt" 0;
    word-break: break-word;
  }
  pre {
    font-family: "JetBrains Mono", "Source Code Pro", "SF Mono", Menlo, Consolas, monospace;
    font-size: 0.85em;
    line-height: 1.55;
    background: var(--code-bg);
    color: var(--code-ink);
    border-left: 3px solid var(--accent);
    padding: 1em 1.2em;
    margin: 1.4em 0;
    overflow-x: auto;
    hyphens: none;
    tab-size: 2;
    border-radius: 0 4px 4px 0;
    box-shadow: var(--shadow-sm);
    font-feature-settings: "liga" 0, "calt" 0;
  }
  pre code {
    background: none;
    padding: 0;
    border-radius: 0;
    font-size: 1em;
    word-break: normal;
  }

  figure { margin: 1.6em 0; text-align: center; }
  figure img { max-width: 100%; height: auto; border-radius: 4px; box-shadow: var(--shadow-sm); }
  figcaption {
    font-family: "Inter", sans-serif;
    font-size: 0.88em;
    color: var(--ink-soft);
    margin-top: 0.6em;
    font-style: italic;
  }
  img { max-width: 100%; height: auto; }

  .chapter-meta {
    font-family: "Inter", sans-serif;
    font-size: 0.85em;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--accent);
    font-weight: 600;
    margin-bottom: 0.6em;
  }
  .lead { font-size: 1.08em; color: var(--ink-soft); font-style: italic; }

  .glossary-entry { margin: 0.6em 0; }
  .glossary-entry strong { color: var(--accent); }
  .idx { line-height: 1.55; margin: 0.15em 0; }
  .idx strong { color: var(--ink); }
  .index-note { font-size: 0.9em; color: var(--ink-soft); margin-bottom: 1em; }

  /* --- sticky chapter nav --- */
  #toc-nav {
    position: fixed;
    top: 0;
    left: 0;
    width: 18em;
    max-height: 100vh;
    overflow-y: auto;
    background: var(--bg);
    border-right: 1px solid var(--rule);
    padding: 1em 0.8em 1.5em 0.8em;
    font-family: "Inter", -apple-system, "Helvetica Neue", Arial, sans-serif;
    font-size: 0.72em;
    line-height: 1.4;
    z-index: 1000;
    box-shadow: 2px 0 8px rgba(0,0,0,0.06);
    transition: transform 0.25s ease;
    scrollbar-width: thin;
    scrollbar-color: var(--rule) transparent;
  }
  #toc-nav::-webkit-scrollbar { width: 6px; }
  #toc-nav::-webkit-scrollbar-thumb { background: var(--rule); border-radius: 3px; }
  #toc-nav::-webkit-scrollbar-track { background: transparent; }
  #toc-nav.collapsed { transform: translateX(-100%); box-shadow: none; }
  #toc-nav .toc-title {
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 0.8em;
    padding-bottom: 0.4em;
    font-size: 1.05em;
    letter-spacing: 0.03em;
    border-bottom: 1px solid var(--rule-soft);
  }
  #toc-nav ul { list-style: none; padding: 0; margin: 0; }
  #toc-nav li { margin: 0.2em 0; }
  #toc-nav li.toc-h1 {
    font-weight: 700;
    margin-top: 0.7em;
    color: var(--accent);
  }
  #toc-nav a {
    color: var(--ink-soft);
    text-decoration: none;
    display: block;
    padding: 0.2em 0.5em;
    border-radius: 3px;
    border-left: 2px solid transparent;
    transition: background 0.15s, color 0.15s, border-color 0.15s;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  #toc-nav a:hover { background: var(--callout); color: var(--accent); }
  #toc-nav a.active {
    background: var(--callout);
    color: var(--accent);
    border-left-color: var(--accent);
    font-weight: 600;
  }
  #toc-toggle {
    position: fixed;
    top: 0.5em;
    left: 0.5em;
    z-index: 1001;
    width: 2.1em;
    height: 2.1em;
    border: 1px solid var(--rule);
    border-radius: 4px;
    background: var(--bg);
    color: var(--accent);
    font-size: 1.1em;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-sm);
    transition: left 0.25s ease, transform 0.15s;
    font-family: "Inter", sans-serif;
  }
  #toc-toggle:hover { transform: scale(1.05); }
  #toc-toggle:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  #toc-toggle.open { left: 18.5em; }

  /* --- heading anchor links --- */
  .heading-anchor {
    color: var(--rule);
    text-decoration: none;
    font-weight: 400;
    margin-left: 0.35em;
    opacity: 0;
    transition: opacity 0.15s;
    font-size: 0.72em;
    vertical-align: middle;
  }
  h1:hover .heading-anchor,
  h2:hover .heading-anchor,
  h3:hover .heading-anchor,
  h4:hover .heading-anchor { opacity: 1; color: var(--accent); }
  .heading-anchor:hover { color: var(--accent-hover); }
  .heading-anchor:focus-visible {
    opacity: 1;
    outline: 2px solid var(--accent);
    outline-offset: 2px;
    border-radius: 2px;
  }

  /* --- back-to-top button --- */
  #top-btn {
    position: fixed;
    bottom: 1.5em;
    right: 1.5em;
    padding: 0.6em 1em;
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 999px;
    font-family: "Inter", -apple-system, sans-serif;
    font-size: 0.85em;
    font-weight: 600;
    letter-spacing: 0.03em;
    cursor: pointer;
    opacity: 0;
    pointer-events: none;
    transform: translateY(6px);
    transition: opacity 0.2s ease, transform 0.2s ease, background 0.15s;
    box-shadow: var(--shadow-md);
    z-index: 999;
  }
  #top-btn.visible { opacity: 0.95; pointer-events: auto; transform: translateY(0); }
  #top-btn:hover { opacity: 1; background: var(--accent-hover); }
  #top-btn:focus-visible { outline: 2px solid #fff; outline-offset: 2px; }

  /* --- per-chapter navigation bar (standalone pages only; stripped from
         the concatenated complete book by build_complete.sh) --- */
  .chapter-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1em;
    margin: 2.5em 0;
    padding: 0.9em 0;
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    font-family: "Inter", -apple-system, sans-serif;
    font-size: 0.85em;
    font-weight: 600;
    letter-spacing: 0.02em;
  }
  .chapter-nav:first-child { margin-top: 0; }
  .chapter-nav a {
    color: var(--accent);
    text-decoration: none;
    padding: 0.35em 0.2em;
    transition: color 0.15s;
  }
  .chapter-nav a:hover { color: var(--accent-hover); }
  .chapter-nav .cn-toc { color: var(--ink-muted); font-weight: 500; }
  .chapter-nav .cn-disabled { color: var(--rule); cursor: default; }
  .chapter-nav .cn-next { text-align: right; }

  /* --- theme toggle --- */
  #theme-btn {
    position: fixed;
    top: 0.5em;
    right: 0.5em;
    width: 2.1em;
    height: 2.1em;
    border-radius: 50%;
    border: 1px solid var(--rule);
    background: var(--paper);
    color: var(--accent);
    font-size: 1em;
    line-height: 1;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-sm);
    transition: transform 0.15s ease, background 0.15s, border-color 0.15s;
    font-family: "Inter", -apple-system, sans-serif;
    z-index: 1001;
  }
  #theme-btn:hover { transform: scale(1.05); border-color: var(--accent); }
  #theme-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  #theme-btn .icon-sun { display: none; }
  #theme-btn .icon-moon { display: inline; }
  html[data-theme="dark"] #theme-btn .icon-sun { display: inline; }
  html[data-theme="dark"] #theme-btn .icon-moon { display: none; }

  /* --- download link (pill, visible only on screen) --- */
  .download-link {
    display: inline-block;
    padding: 0.55em 1.1em;
    background: var(--accent);
    color: #fff;
    text-decoration: none;
    font-family: "Inter", -apple-system, sans-serif;
    font-weight: 600;
    font-size: 0.9em;
    letter-spacing: 0.02em;
    border-radius: 999px;
    box-shadow: var(--shadow-sm);
    transition: background 0.15s, transform 0.15s;
  }
  .download-link:hover {
    background: var(--accent-hover);
    color: #fff;
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
    text-decoration: none;
  }
  .download-link:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
  .download-link::before {
    content: "↓";
    display: inline-block;
    margin-right: 0.4em;
    font-weight: 700;
  }

  /* --- medium viewports: push body right so the sidebar doesn't
         overlap the first characters of each line --- */
  @media (min-width: 901px) and (max-width: 1400px) {
    body:has(#toc-nav:not(.collapsed)) {
      padding-left: 18em;
    }
  }

  /* --- small screens --- */
  @media (max-width: 900px) {
    body { margin: 2em auto; padding: 0 1em; }
    #toc-nav { width: 82%; max-width: 20em; }
    #toc-toggle.open { left: calc(82% + 0.5em); }
  }

  /* --- reduced motion --- */
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.001ms !important;
      transition-duration: 0.001ms !important;
      scroll-behavior: auto !important;
    }
  }

  /* --- print --- */
  @page { size: A4; margin: 22mm 18mm 20mm 18mm; }
  @page :first { margin-top: 0; }

  @media print {
    html[data-theme="dark"] { /* force light theme in PDF regardless of user toggle */
      --ink: #000; --ink-soft: #333; --ink-muted: #5a5f66;
      --accent: #0b5394; --accent-soft: #e3ecf6; --accent-hover: #083d73;
      --rule: #cfd4d9; --rule-soft: #e8ecf1;
      --bg: #fff; --paper: #fff; --callout: #f5f7fb; --row-alt: #f7f9fc;
      --code-bg: #f4f6f9; --code-ink: #22272e;
    }
    :root {
      --bg: #fff; --paper: #fff;
      --ink: #000; --ink-soft: #333;
      --rule: #cfd4d9; --callout: #f5f7fb; --row-alt: #f7f9fc;
    }
    #toc-nav, #toc-toggle, #top-btn, #theme-btn, .chapter-nav,
    .heading-anchor, .download-link { display: none !important; }
    body {
      font-size: 10.5pt;
      max-width: none;
      margin: 0;
      padding: 0;
      line-height: 1.5;
      background: #fff;
      color: #000;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    h1 { font-size: 1.8em; }
    h2 { font-size: 1.3em; page-break-after: avoid; }
    h3, h4 { page-break-after: avoid; }
    p, li { orphans: 3; widows: 3; }
    table, blockquote, figure { page-break-inside: avoid; }
    pre { page-break-inside: auto; white-space: pre-wrap; word-wrap: break-word; }
    th, tbody tr:nth-child(even), .pages, h2.part-title {
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    a { color: var(--accent); text-decoration: none; }
  }
"""

COVER_EXTRA_CSS = """\

  /* Cover page */
  .cover {
    text-align: center;
    padding: 6em 1em 4em 1em;
    page-break-after: always;
  }
  .cover .cover-logo {
    display: block;
    margin: 0 auto 2.5em auto;
    height: 140px;
    width: auto;
  }
  .cover h1 {
    font-size: 2.8em;
    border-bottom: none;
    color: var(--accent);
    margin-bottom: 0.2em;
  }
  .cover .cover-subtitle {
    font-size: 1.3em;
    font-style: italic;
    color: var(--ink-soft);
    margin-bottom: 2em;
  }
  .cover .cover-edition {
    font-size: 1em;
    color: var(--ink-soft);
    margin-top: 3em;
  }

  /* Chapter separator */
  .chapter-break {
    page-break-before: always;
    border-top: 4px solid var(--accent);
    margin-top: 4em;
    padding-top: 2em;
  }

  @page cover { size: A4; margin: 0; }
  .cover { page: cover; }

  @media print {
    .chapter-break { page-break-before: always; margin-top: 0; padding-top: 1em; border-top: none; }
    .cover { padding: 8cm 1cm 4cm 1cm; page-break-after: always; }
  }
"""


# --- TitlePage-specific polish (keeps its centred layout) --------------------

TITLE_CSS = """\
  :root {
    --ink: #1a1a1a;
    --ink-soft: #444;
    --accent: #0b5394;
    --accent-hover: #083d73;
    --rule: #d0d7de;
    --bg: #fbfbf8;
    --callout: #f3f6fb;
    --shadow-md: 0 2px 8px rgba(15,23,42,0.08);
  }
  html[data-theme="dark"] {
    --ink: #e6e8eb;
    --ink-soft: #b1b6bd;
    --accent: #79b8ff;
    --accent-hover: #a8d0ff;
    --rule: #2e333b;
    --bg: #101214;
    --callout: #1b2432;
    --paper: #191c1f;
  }
  html[data-theme="dark"] img { filter: brightness(0.92) contrast(1.05); }
  html {
    -webkit-text-size-adjust: 100%;
    scroll-behavior: smooth;
  }
  body {
    font-family: "Source Serif Pro", "Source Serif 4", Georgia, "Times New Roman", serif;
    font-size: 18px;
    line-height: 1.65;
    color: var(--ink);
    background: var(--bg);
    max-width: 46em;
    margin: 3em auto;
    padding: 0 1.5em;
    hyphens: auto;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    font-feature-settings: "kern", "liga";
  }
  h1, h2, h3, h4 {
    font-family: "Inter", -apple-system, "Helvetica Neue", Arial, sans-serif;
    color: var(--ink);
    line-height: 1.25;
    margin-top: 2em;
    font-feature-settings: "kern", "liga";
  }
  h1 {
    font-size: 2.1em;
    border-bottom: 3px solid var(--accent);
    padding-bottom: 0.3em;
    margin-top: 0;
  }
  h1 .subtitle {
    display: block;
    font-size: 0.55em;
    font-weight: 400;
    font-style: italic;
    color: var(--ink-soft);
    margin-top: 0.4em;
  }
  p { margin: 0.9em 0; text-align: justify; }
  hr { border: none; border-top: 1px solid var(--rule); margin: 2.4em 0; }

  /* --- title page --- */
  body.title-page {
    text-align: center;
    margin-top: 6em;
  }
  body.title-page p { text-align: center; }
  .title-logo {
    max-width: 420px;
    width: 80%;
    height: auto;
    margin: 0 auto 3em;
    display: block;
    filter: drop-shadow(0 4px 14px rgba(11,83,148,0.12));
  }
  .title-heading {
    font-size: 3.2em;
    border: none;
    padding: 0;
    margin: 0 0 0.2em;
    letter-spacing: -0.025em;
    font-feature-settings: "kern", "liga", "ss01";
  }
  .title-tagline {
    font-family: "Inter", sans-serif;
    font-size: 1.15em;
    color: var(--accent);
    margin: 0 0 2em;
    letter-spacing: 0.01em;
    font-weight: 500;
  }
  .title-subtitle {
    font-style: italic;
    font-size: 1.1em;
    color: var(--ink-soft);
    margin: 0 0 3em;
  }
  .title-rule {
    border: none;
    border-top: 2px solid var(--accent);
    width: 4em;
    margin: 2em auto;
  }
  .title-meta {
    font-family: "Inter", sans-serif;
    font-size: 0.95em;
    color: var(--ink-soft);
    margin: 0.3em 0;
  }
  .title-year {
    font-family: "Inter", sans-serif;
    font-size: 1.1em;
    font-weight: 600;
    letter-spacing: 0.05em;
    color: var(--ink);
    margin: 0.3em 0;
  }

  @media print {
    body.title-page { margin-top: 0; page-break-after: always; }
  }

  /* --- back-to-top button --- */
  #top-btn {
    position: fixed;
    bottom: 1.5em;
    right: 1.5em;
    padding: 0.6em 1em;
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 999px;
    font-family: "Inter", -apple-system, sans-serif;
    font-size: 0.85em;
    font-weight: 600;
    letter-spacing: 0.03em;
    cursor: pointer;
    opacity: 0;
    pointer-events: none;
    transform: translateY(6px);
    transition: opacity 0.2s ease, transform 0.2s ease, background 0.15s;
    box-shadow: var(--shadow-md);
    z-index: 999;
  }
  #top-btn.visible { opacity: 0.95; pointer-events: auto; transform: translateY(0); }
  #top-btn:hover { opacity: 1; background: var(--accent-hover); }
  #top-btn:focus-visible { outline: 2px solid #fff; outline-offset: 2px; }
  @media print { #top-btn { display: none; } }

  /* --- theme toggle --- */
  #theme-btn {
    position: fixed;
    top: 0.5em;
    right: 0.5em;
    width: 2.1em;
    height: 2.1em;
    border-radius: 50%;
    border: 1px solid var(--rule);
    background: var(--bg);
    color: var(--accent);
    font-size: 1em;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-md);
    transition: transform 0.15s ease, background 0.15s, border-color 0.15s;
    font-family: "Inter", -apple-system, sans-serif;
    z-index: 1001;
  }
  #theme-btn:hover { transform: scale(1.05); border-color: var(--accent); }
  #theme-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  #theme-btn .icon-sun { display: none; }
  #theme-btn .icon-moon { display: inline; }
  html[data-theme="dark"] #theme-btn .icon-sun { display: inline; }
  html[data-theme="dark"] #theme-btn .icon-moon { display: none; }
  @media print { #theme-btn { display: none !important; } }

  /* --- download link --- */
  .download-link {
    display: inline-block;
    margin-top: 2em;
    padding: 0.55em 1.1em;
    background: var(--accent);
    color: #fff;
    text-decoration: none;
    font-family: "Inter", -apple-system, sans-serif;
    font-weight: 600;
    font-size: 0.9em;
    letter-spacing: 0.02em;
    border-radius: 999px;
    box-shadow: 0 2px 8px rgba(11,83,148,0.15);
    transition: background 0.15s, transform 0.15s;
  }
  .download-link:hover {
    background: var(--accent-hover);
    color: #fff;
    transform: translateY(-1px);
  }
  .download-link::before {
    content: "↓";
    display: inline-block;
    margin-right: 0.4em;
    font-weight: 700;
  }
  @media print { .download-link { display: none !important; } }

  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.001ms !important;
      transition-duration: 0.001ms !important;
    }
  }
"""


# --- ToC-specific polish (keeps the card-grid layout) ------------------------

TOC_CSS = """\
  :root {
    --navy: #1B2A4A;
    --blue: #3B7DD8;
    --blue-hover: #2960ba;
    --light: #F4F7FB;
    --border: #D8E2F0;
    --text: #1F2937;
    --muted: #5B6B82;
    --paper: #FFFFFF;
    --accent: var(--blue);
    --ink-soft: var(--muted);
    --rule: var(--border);
    --bg: var(--paper);
    --callout: var(--light);
    --shadow-sm: 0 1px 2px rgba(27,42,74,0.05);
    --shadow-md: 0 4px 14px rgba(27,42,74,0.10);
  }
  html[data-theme="dark"] {
    --navy: #a8bbe0;
    --blue: #79b8ff;
    --blue-hover: #a8d0ff;
    --light: #1b2432;
    --border: #2e333b;
    --text: #e6e8eb;
    --muted: #b1b6bd;
    --paper: #101214;
    --bg: #101214;
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    font-family: "Inter", "Source Sans Pro", -apple-system, "Helvetica Neue", Arial, sans-serif;
    color: var(--text);
    background: var(--paper);
    margin: 0;
    padding: 0;
    line-height: 1.55;
    -webkit-font-smoothing: antialiased;
    font-feature-settings: "kern", "liga";
  }
  ::selection { background: rgba(59,125,216,0.18); color: var(--text); }
  .container {
    max-width: 960px;
    margin: 0 auto;
    padding: 48px 40px 80px;
  }
  header.book-header {
    border-bottom: 4px solid var(--blue);
    padding-bottom: 24px;
    margin-bottom: 32px;
  }
  header.book-header h1 {
    color: var(--navy);
    font-size: 2.2em;
    margin: 0 0 8px;
    letter-spacing: -0.02em;
    font-weight: 700;
  }
  header.book-header .subtitle {
    color: var(--blue);
    font-style: italic;
    font-size: 1.15em;
    margin-bottom: 6px;
  }
  header.book-header .meta {
    color: var(--muted);
    font-size: 0.95em;
    font-variant-numeric: tabular-nums;
  }
  .summary-box {
    background: var(--light);
    border-left: 4px solid var(--blue);
    padding: 16px 20px;
    margin: 24px 0 40px;
    color: var(--navy);
    font-weight: 600;
    border-radius: 0 4px 4px 0;
  }
  h2.part-title {
    color: #FFFFFF;
    background: var(--navy);
    padding: 12px 20px;
    margin-top: 48px;
    margin-bottom: 24px;
    font-size: 1.2em;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    border-radius: 3px;
    box-shadow: var(--shadow-sm);
  }
  .chapter {
    display: block;
    border: 1px solid var(--border);
    border-left: 4px solid var(--blue);
    padding: 18px 22px;
    margin-bottom: 18px;
    background: var(--paper);
    border-radius: 3px;
    transition: box-shadow 0.2s ease, transform 0.15s ease, border-color 0.15s;
  }
  .chapter:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
    border-left-color: var(--blue-hover);
  }
  .chapter h3 {
    color: var(--navy);
    margin: 0 0 4px;
    font-size: 1.15em;
    letter-spacing: -0.005em;
  }
  .chapter .chapter-sub {
    color: var(--blue);
    font-style: italic;
    font-size: 0.95em;
    margin-bottom: 10px;
  }
  .chapter p.description {
    margin: 8px 0 12px;
    color: var(--text);
    font-size: 0.97em;
    line-height: 1.55;
  }
  .pages {
    display: inline-block;
    background: var(--blue);
    color: #FFFFFF;
    font-size: 0.82em;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 999px;
    letter-spacing: 0.03em;
    font-variant-numeric: tabular-nums;
  }
  .appendix .chapter { border-left-color: var(--muted); }
  .appendix .chapter:hover { border-left-color: var(--navy); }
  .appendix .pages { background: var(--muted); }
  footer {
    margin-top: 56px;
    padding-top: 20px;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: 0.85em;
    text-align: center;
  }

  /* --- sticky chapter nav --- */
  #toc-nav {
    position: fixed;
    top: 0;
    left: 0;
    width: 16em;
    max-height: 100vh;
    overflow-y: auto;
    background: var(--bg);
    border-right: 1px solid var(--rule);
    padding: 1em 0.8em 1.5em 0.8em;
    font-family: "Inter", -apple-system, "Helvetica Neue", Arial, sans-serif;
    font-size: 0.75em;
    line-height: 1.4;
    z-index: 1000;
    box-shadow: 2px 0 8px rgba(0,0,0,0.06);
    transition: transform 0.25s ease;
    scrollbar-width: thin;
    scrollbar-color: var(--rule) transparent;
  }
  #toc-nav::-webkit-scrollbar { width: 6px; }
  #toc-nav::-webkit-scrollbar-thumb { background: var(--rule); border-radius: 3px; }
  #toc-nav.collapsed { transform: translateX(-100%); box-shadow: none; }
  #toc-nav .toc-title {
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 0.6em;
    font-size: 1.05em;
    letter-spacing: 0.03em;
  }
  #toc-nav ul { list-style: none; padding: 0; margin: 0; }
  #toc-nav li { margin: 0.25em 0; }
  #toc-nav a {
    color: var(--ink-soft);
    text-decoration: none;
    display: block;
    padding: 0.2em 0.5em;
    border-radius: 3px;
    border-left: 2px solid transparent;
    transition: background 0.15s, color 0.15s, border-color 0.15s;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  #toc-nav a:hover { background: var(--callout); color: var(--accent); }
  #toc-nav a.active {
    background: var(--callout);
    color: var(--accent);
    border-left-color: var(--accent);
    font-weight: 600;
  }
  #toc-toggle {
    position: fixed;
    top: 0.5em;
    left: 0.5em;
    z-index: 1001;
    width: 2.1em;
    height: 2.1em;
    border: 1px solid var(--rule);
    border-radius: 4px;
    background: var(--bg);
    color: var(--accent);
    font-size: 1.1em;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-sm);
    transition: left 0.25s ease, transform 0.15s;
    font-family: "Inter", sans-serif;
  }
  #toc-toggle:hover { transform: scale(1.05); }
  #toc-toggle:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  #toc-toggle.open { left: 16.5em; }

  .heading-anchor {
    color: var(--rule);
    text-decoration: none;
    font-weight: 400;
    margin-left: 0.3em;
    opacity: 0;
    transition: opacity 0.15s;
    font-size: 0.72em;
    vertical-align: middle;
  }
  h1:hover .heading-anchor,
  h2:hover .heading-anchor,
  h3:hover .heading-anchor,
  h4:hover .heading-anchor { opacity: 1; color: var(--accent); }
  .heading-anchor:hover { text-decoration: underline; }

  #top-btn {
    position: fixed;
    bottom: 1.5em;
    right: 1.5em;
    padding: 0.6em 1em;
    background: var(--blue);
    color: #fff;
    border: none;
    border-radius: 999px;
    font-family: "Inter", -apple-system, sans-serif;
    font-size: 0.85em;
    font-weight: 600;
    letter-spacing: 0.03em;
    cursor: pointer;
    opacity: 0;
    pointer-events: none;
    transform: translateY(6px);
    transition: opacity 0.2s ease, transform 0.2s ease, background 0.15s;
    box-shadow: var(--shadow-md);
    z-index: 999;
  }
  #top-btn.visible { opacity: 0.95; pointer-events: auto; transform: translateY(0); }
  #top-btn:hover { opacity: 1; background: var(--blue-hover); }
  #top-btn:focus-visible { outline: 2px solid #fff; outline-offset: 2px; }

  /* --- theme toggle --- */
  #theme-btn {
    position: fixed;
    top: 0.5em;
    right: 0.5em;
    width: 2.1em;
    height: 2.1em;
    border-radius: 50%;
    border: 1px solid var(--border);
    background: var(--paper);
    color: var(--blue);
    font-size: 1em;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-sm);
    transition: transform 0.15s ease, background 0.15s, border-color 0.15s;
    font-family: "Inter", -apple-system, sans-serif;
    z-index: 1001;
  }
  #theme-btn:hover { transform: scale(1.05); border-color: var(--blue); }
  #theme-btn:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; }
  #theme-btn .icon-sun { display: none; }
  #theme-btn .icon-moon { display: inline; }
  html[data-theme="dark"] #theme-btn .icon-sun { display: inline; }
  html[data-theme="dark"] #theme-btn .icon-moon { display: none; }
  @media print { #theme-btn { display: none !important; } }

  /* --- download link --- */
  .download-link {
    display: inline-block;
    padding: 6px 14px;
    margin-left: 12px;
    background: var(--blue);
    color: #fff;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.85em;
    letter-spacing: 0.02em;
    border-radius: 999px;
    transition: background 0.15s, transform 0.15s;
    vertical-align: middle;
  }
  .download-link:hover {
    background: var(--blue-hover);
    color: #fff;
    transform: translateY(-1px);
    text-decoration: none;
  }
  .download-link::before {
    content: "↓";
    margin-right: 6px;
    font-weight: 700;
  }
  @media print { .download-link { display: none !important; } }

  @media (min-width: 901px) and (max-width: 1400px) {
    body:has(#toc-nav:not(.collapsed)) { padding-left: 17em; }
  }

  @media (max-width: 900px) {
    .container { padding: 28px 20px 56px; }
    header.book-header h1 { font-size: 1.7em; }
    #toc-nav { width: 82%; max-width: 20em; }
    #toc-toggle.open { left: calc(82% + 0.5em); }
  }

  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.001ms !important;
      transition-duration: 0.001ms !important;
      scroll-behavior: auto !important;
    }
  }

  @media print {
    #toc-nav, #toc-toggle, #top-btn, #theme-btn, .download-link { display: none !important; }
    body { background: #fff; color: #000; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .chapter { break-inside: avoid; box-shadow: none; border: 1px solid #bcc5d4; }
    .chapter:hover { transform: none; box-shadow: none; }
    h2.part-title { background: #1B2A4A !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .pages { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
"""


# ---------------------------------------------------------------------------
# File classification
# ---------------------------------------------------------------------------

def files_for(kind: str) -> list[Path]:
    if kind == "base":
        names: list[str] = []
        for i in range(1, 15):
            names.append(f"Chapter{i:02d}.html")
        for letter in "ABCDE":
            names.append(f"Appendix{letter}.html")
        names.extend(["Index.html", "ManagementSummary.html"])
        return [ROOT / n for n in names]
    if kind == "title":
        return [ROOT / "TitlePage.html"]
    if kind == "toc":
        return [ROOT / "FundsXML_Book_TableOfContents.html"]
    raise ValueError(kind)


# ---------------------------------------------------------------------------
# Rewriter
# ---------------------------------------------------------------------------

STYLE_RE = re.compile(r"<style>.*?</style>", re.DOTALL)

# Theme-preload runs in <head> before first paint to prevent FOUC.
THEME_PRELOAD = (
    '<script id="theme-preload">'
    "(function(){try{var t=localStorage.getItem('fundsxml-theme');"
    "if(t==='dark')document.documentElement.setAttribute('data-theme','dark');"
    "}catch(e){}})();"
    "</script>"
)

# Button + click handler injected at end of <body>.
THEME_BUTTON = (
    '<button id="theme-btn" type="button" aria-label="Toggle light/dark theme"'
    ' title="Toggle light/dark theme">'
    '<span class="icon-moon" aria-hidden="true">☽</span>'
    '<span class="icon-sun" aria-hidden="true">☀</span>'
    '</button>'
)
THEME_SCRIPT = (
    '<script id="theme-toggle">'
    "(function(){var b=document.getElementById('theme-btn');if(!b)return;"
    "b.addEventListener('click',function(){"
    "var isDark=document.documentElement.getAttribute('data-theme')==='dark';"
    "if(isDark){document.documentElement.removeAttribute('data-theme');"
    "try{localStorage.setItem('fundsxml-theme','light');}catch(e){}}"
    "else{document.documentElement.setAttribute('data-theme','dark');"
    "try{localStorage.setItem('fundsxml-theme','dark');}catch(e){}}"
    "});})();"
    "</script>"
)

# Leading \s* so stripping also consumes the newline we insert with the tag;
# without it every re-run would accumulate a blank line (non-idempotent).
PRELOAD_RE = re.compile(r'\s*<script id="theme-preload">.*?</script>', re.DOTALL)
BUTTON_RE = re.compile(r'\s*<button id="theme-btn"[^>]*>.*?</button>', re.DOTALL)
TOGGLE_RE = re.compile(r'\s*<script id="theme-toggle">.*?</script>', re.DOTALL)


def inject_theme(html: str) -> str:
    """Ensure exactly one theme-preload in <head> and one button + toggle
    before </body>. Removes all existing copies first (critical for the
    concatenated complete-book HTML where each chapter body previously
    contained its own copy)."""
    # Strip every existing copy anywhere in the document
    html = PRELOAD_RE.sub("", html)
    html = BUTTON_RE.sub("", html)
    html = TOGGLE_RE.sub("", html)
    # Insert fresh, single copies at the canonical locations
    html = re.sub(r"</head>", THEME_PRELOAD + "\n</head>", html, count=1)
    html = re.sub(
        r"</body>",
        THEME_BUTTON + "\n" + THEME_SCRIPT + "\n</body>",
        html,
        count=1,
    )
    return html


# Reading order for the standalone pages. Front matter first, then the 14
# chapters, the appendices, and the index last. "Contents" always links to
# the generated landing page (index.html).
NAV_SEQUENCE: list[tuple[str, str]] = (
    [("ManagementSummary.html", "Management Summary")]
    + [(f"Chapter{i:02d}.html", f"Chapter {i}") for i in range(1, 15)]
    + [(f"Appendix{c}.html", f"Appendix {c}") for c in "ABCDE"]
    + [("Index.html", "Index")]
)
NAV_INDEX = {name: i for i, (name, _) in enumerate(NAV_SEQUENCE)}

NAV_RE = re.compile(r'\s*<nav class="chapter-nav".*?</nav>', re.DOTALL)


def _nav_bar(name: str) -> str:
    """Single-line prev / contents / next bar for the given file name."""
    i = NAV_INDEX[name]
    if i > 0:
        pf, pl = NAV_SEQUENCE[i - 1]
        prev = f'<a class="cn-prev" href="{pf}">&lsaquo; {pl}</a>'
    else:
        prev = '<span class="cn-prev cn-disabled">&lsaquo; Start</span>'
    if i < len(NAV_SEQUENCE) - 1:
        nf, nl = NAV_SEQUENCE[i + 1]
        nxt = f'<a class="cn-next" href="{nf}">{nl} &rsaquo;</a>'
    else:
        nxt = '<span class="cn-next cn-disabled">End &rsaquo;</span>'
    toc = '<a class="cn-toc" href="index.html">Contents</a>'
    return (
        '<nav class="chapter-nav" aria-label="Chapter navigation">'
        f"{prev}{toc}{nxt}</nav>"
    )


def inject_nav(html: str, name: str) -> str:
    """Ensure exactly one chapter-nav bar right after <body> and one right
    before </body>. No-op for files outside NAV_SEQUENCE (TitlePage, TOC).
    Idempotent: strips every existing copy first."""
    if name not in NAV_INDEX:
        return html
    html = NAV_RE.sub("", html)
    bar = _nav_bar(name)
    html = re.sub(r"<body>", f"<body>\n{bar}", html, count=1)
    html = re.sub(r"</body>", f"{bar}\n</body>", html, count=1)
    return html


def rewrite(path: Path, css: str, check: bool) -> bool:
    if not path.exists():
        print(f"skip (missing): {path.name}")
        return False
    original = path.read_text(encoding="utf-8")
    new_block = f"<style>\n{css}</style>"
    replaced, n = STYLE_RE.subn(new_block, original, count=1)
    if n == 0:
        print(f"WARN no <style> block in {path.name}")
        return False
    # Order matters for idempotency: inject_nav first, then inject_theme.
    # Both insert before </body>; theme always re-strips and re-appends after
    # the nav bar, giving a stable canonical order on every re-run.
    replaced = inject_nav(replaced, path.name)
    replaced = inject_theme(replaced)
    if replaced == original:
        print(f"unchanged: {path.name}")
        return False
    if check:
        print(f"would rewrite: {path.name}  (bytes {len(original)} -> {len(replaced)})")
        return True
    path.write_text(replaced, encoding="utf-8")
    print(f"rewrote:   {path.name}  (bytes {len(original)} -> {len(replaced)})")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="dry run")
    ap.add_argument(
        "--print-css",
        choices=["base", "complete", "title", "toc"],
        help="print a CSS block to stdout and exit (used by build_complete.sh)",
    )
    args = ap.parse_args()

    if args.print_css:
        if args.print_css == "base":
            sys.stdout.write(BASE_CSS)
        elif args.print_css == "complete":
            sys.stdout.write(BASE_CSS + COVER_EXTRA_CSS)
        elif args.print_css == "title":
            sys.stdout.write(TITLE_CSS)
        elif args.print_css == "toc":
            sys.stdout.write(TOC_CSS)
        return 0

    any_change = False
    for path in files_for("base"):
        any_change |= rewrite(path, BASE_CSS, args.check)
    for path in files_for("title"):
        any_change |= rewrite(path, TITLE_CSS, args.check)
    for path in files_for("toc"):
        any_change |= rewrite(path, TOC_CSS, args.check)

    if args.check:
        print("\nDone (check).")
    else:
        print("\nDone. Run build_complete.sh to regenerate FundsXML_Book_Complete.html.")
    return 0 if any_change or args.check else 0


if __name__ == "__main__":
    sys.exit(main())
