#!/bin/bash
# Build complete book HTML from individual chapter/appendix HTML files
# Output: FundsXML_Book_Complete.html

# Resolve the directory this script lives in, so the build works from any
# checkout location (local clone, CI runner, etc.).
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$DIR/FundsXML_Book_Complete.html"

# Extract body content (between <body> and </body>) from an HTML file,
# stripping per-chapter <script> blocks and the per-page theme-toggle button
# (the complete file has its own single copy at the end).
extract_body() {
    sed -n '/<body>/,/<\/body>/p' "$1" \
      | sed '1s/.*<body>//' \
      | sed '$s/<\/body>.*//' \
      | sed -E '/<script( [^>]*)?>/,/<\/script>/d' \
      | sed -E 's|<button id="theme-btn"[^>]*>.*</button>||g' \
      | sed -E 's|<nav class="chapter-nav"[^>]*>.*</nav>||g'
}

cat > "$OUT" << 'HEADER'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>FundsXML — The European Standard for Fund Data Exchange</title>
<link rel="icon" type="image/png" href="FundsXML-Logo.png">
<style>
HEADER

# Canonical CSS lives in polish_styles.py (single source of truth).
python3 "$DIR/polish_styles.py" --print-css complete >> "$OUT"

cat >> "$OUT" << 'HEADER_END'
</style>
</head>
<body>
HEADER_END

cat >> "$OUT" << 'COVER'

<!-- ============================================================ -->
<!-- COVER PAGE                                                    -->
<!-- ============================================================ -->
<div class="cover">
  <img src="FundsXML-Logo.png" alt="FundsXML" class="cover-logo">
  <div class="cover-subtitle">The European Standard for Fund Data Exchange</div>
  <p style="font-size: 1.15em; color: #1a1a1a; margin-top: 1em;">A Practical Handbook for Fund Professionals</p>
  <p style="font-size: 1em; color: #444; margin-top: 0.5em;">Based on FundsXML Schema Version 4.2.x</p>
  <div class="cover-edition">2026</div>
</div>
COVER

# Table of Contents (from the TOC HTML)
echo '<!-- ============================================================ -->' >> "$OUT"
echo '<!-- TABLE OF CONTENTS                                            -->' >> "$OUT"
echo '<!-- ============================================================ -->' >> "$OUT"
echo '<div class="chapter-break">' >> "$OUT"
extract_body "$DIR/FundsXML_Book_TableOfContents.html" >> "$OUT"
echo '</div>' >> "$OUT"

# Management Summary (front matter)
if [ -f "$DIR/ManagementSummary.html" ]; then
    echo "" >> "$OUT"
    echo '<!-- ============================================================ -->' >> "$OUT"
    echo '<!-- MANAGEMENT SUMMARY                                            -->' >> "$OUT"
    echo '<!-- ============================================================ -->' >> "$OUT"
    echo '<div class="chapter-break">' >> "$OUT"
    extract_body "$DIR/ManagementSummary.html" >> "$OUT"
    echo '</div>' >> "$OUT"
fi

# Part I — Foundations
for ch in 01 02 03; do
    f="$DIR/Chapter${ch}.html"
    if [ -f "$f" ]; then
        echo "" >> "$OUT"
        echo "<!-- ============================================================ -->" >> "$OUT"
        echo "<!-- CHAPTER ${ch}                                                -->" >> "$OUT"
        echo "<!-- ============================================================ -->" >> "$OUT"
        echo '<div class="chapter-break">' >> "$OUT"
        extract_body "$f" >> "$OUT"
        echo '</div>' >> "$OUT"
    fi
done

# Part II — FundsXML in Detail
for ch in 04 05 06 07 08 09; do
    f="$DIR/Chapter${ch}.html"
    if [ -f "$f" ]; then
        echo "" >> "$OUT"
        echo "<!-- CHAPTER ${ch} -->" >> "$OUT"
        echo '<div class="chapter-break">' >> "$OUT"
        extract_body "$f" >> "$OUT"
        echo '</div>' >> "$OUT"
    fi
done

# Part III — Implementation and Practice
for ch in 10 11 12 13; do
    f="$DIR/Chapter${ch}.html"
    if [ -f "$f" ]; then
        echo "" >> "$OUT"
        echo "<!-- CHAPTER ${ch} -->" >> "$OUT"
        echo '<div class="chapter-break">' >> "$OUT"
        extract_body "$f" >> "$OUT"
        echo '</div>' >> "$OUT"
    fi
done

# Part IV — Outlook and Reference
for ch in 14; do
    f="$DIR/Chapter${ch}.html"
    if [ -f "$f" ]; then
        echo "" >> "$OUT"
        echo "<!-- CHAPTER ${ch} -->" >> "$OUT"
        echo '<div class="chapter-break">' >> "$OUT"
        extract_body "$f" >> "$OUT"
        echo '</div>' >> "$OUT"
    fi
done

# Appendices
for app in A B C D E; do
    f="$DIR/Appendix${app}.html"
    if [ -f "$f" ]; then
        echo "" >> "$OUT"
        echo "<!-- APPENDIX ${app} -->" >> "$OUT"
        echo '<div class="chapter-break">' >> "$OUT"
        extract_body "$f" >> "$OUT"
        echo '</div>' >> "$OUT"
    fi
done

# Index
f="$DIR/Index.html"
if [ -f "$f" ]; then
    echo "" >> "$OUT"
    echo "<!-- INDEX -->" >> "$OUT"
    echo '<div class="chapter-break">' >> "$OUT"
    extract_body "$f" >> "$OUT"
    echo '</div>' >> "$OUT"
fi

# Unified navigation script for the complete book
cat >> "$OUT" << 'SCRIPT'

<script>
(function() {
  var headings = document.querySelectorAll('h1, h2');
  if (headings.length === 0) return;

  var nav = document.createElement('nav');
  nav.id = 'toc-nav';
  var title = document.createElement('div');
  title.className = 'toc-title';
  title.textContent = 'Contents';
  nav.appendChild(title);
  var ul = document.createElement('ul');

  var counter = 0;
  headings.forEach(function(h) {
    // Skip the cover h1
    if (h.closest('.cover')) return;
    var id = 'nav-' + counter++;
    h.id = id;
    var li = document.createElement('li');
    if (h.tagName === 'H1') li.className = 'toc-h1';
    var a = document.createElement('a');
    a.href = '#' + id;
    // Use only the first text node to keep it short
    var text = h.childNodes[0] ? h.childNodes[0].textContent.trim() : h.textContent.trim();
    // Truncate long titles
    if (text.length > 50) text = text.substring(0, 47) + '...';
    a.textContent = text;
    li.appendChild(a);
    ul.appendChild(li);
  });
  nav.appendChild(ul);
  document.body.insertBefore(nav, document.body.firstChild);

  var btn = document.createElement('button');
  btn.id = 'toc-toggle';
  btn.className = 'open';
  btn.textContent = '\u2630';
  btn.title = 'Toggle navigation';
  btn.addEventListener('click', function() {
    nav.classList.toggle('collapsed');
    btn.classList.toggle('open');
  });
  document.body.insertBefore(btn, document.body.firstChild);

  // Scroll tracking
  var links = nav.querySelectorAll('a');
  var navHeadings = [];
  links.forEach(function(a) {
    var target = document.getElementById(a.getAttribute('href').substring(1));
    if (target) navHeadings.push(target);
  });
  function updateActive() {
    var scrollPos = window.scrollY + 100;
    var current = -1;
    for (var i = 0; i < navHeadings.length; i++) {
      if (navHeadings[i].offsetTop <= scrollPos) current = i;
    }
    links.forEach(function(a, i) {
      a.classList.toggle('active', i === current);
    });
    // Scroll the active item into view in the nav
    if (current >= 0 && links[current]) {
      links[current].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }
  window.addEventListener('scroll', updateActive, {passive: true});
  updateActive();
})();
</script>
SCRIPT

# Heading-anchor injector + back-to-top button
cat >> "$OUT" << 'EXTRAS'
<script>
document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll("h1, h2, h3, h4").forEach(function(el) {
    var subtitle = el.querySelector(".subtitle");
    var text = (subtitle && el.firstChild && el.firstChild.nodeType === 3)
      ? el.firstChild.textContent.trim()
      : el.textContent.trim();
    var match = text.match(/^(\d+\.\d+(?:\.\d+)?)/);
    var id;
    if (match) {
      id = "s" + match[1];
    } else {
      id = text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").substring(0, 60);
    }
    if (!el.id) el.id = id;
    var a = document.createElement("a");
    a.className = "heading-anchor";
    a.href = "#" + el.id;
    a.textContent = "#";
    a.title = "Link to this section";
    if (subtitle) {
      el.insertBefore(a, subtitle);
    } else {
      el.appendChild(a);
    }
  });
});
</script>
<button id="top-btn" onclick="window.scrollTo({top:0,behavior:'smooth'})">↑ Top</button>
<script>
(function(){
  var btn=document.getElementById('top-btn');
  window.addEventListener('scroll',function(){
    btn.classList.toggle('visible', window.scrollY>400);
  });
})();
</script>
EXTRAS

# Close HTML
echo '' >> "$OUT"
echo '</body>' >> "$OUT"
echo '</html>' >> "$OUT"

# Inject the theme-toggle (preload in <head>, button + script before </body>).
# Reuses the idempotent helper from polish_styles.py.
python3 - <<PYEOF
import sys
sys.path.insert(0, "$DIR")
from polish_styles import inject_theme
p = "$OUT"
html = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(inject_theme(html))
PYEOF

echo "Done. Output: $OUT"
wc -l "$OUT"
du -h "$OUT"

# ---------------------------------------------------------------------------
# Generate the GitHub Pages landing page (index.html).
# Reuses the Table-of-Contents CSS so the look matches the book, links every
# chapter/appendix for individual reading, plus the complete HTML and PDF.
# ---------------------------------------------------------------------------
IDX="$DIR/index.html"

# Emit a linked card for a file: <stem> <fallback-label>
card() {
    local file="$1" fallback="$2"
    [ -f "$DIR/$file" ] || return 0
    local title
    title="$(grep -oE '<title>[^<]*</title>' "$DIR/$file" | head -1 | sed -E 's|</?title>||g')"
    [ -n "$title" ] || title="$fallback"
    echo "    <a class=\"chapter\" href=\"${file}\">${title}</a>" >> "$IDX"
}

part() { echo "    <h2 class=\"part-title\">$1</h2>" >> "$IDX"; }

cat > "$IDX" << 'IDX_HEAD'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FundsXML — The European Standard for Fund Data Exchange</title>
<link rel="icon" type="image/png" href="FundsXML-Logo.png">
<style>
IDX_HEAD
python3 "$DIR/polish_styles.py" --print-css toc >> "$IDX"
cat >> "$IDX" << 'IDX_MID'
</style>
</head>
<body>
  <div class="container">
    <header class="book-header">
      <img src="FundsXML-Logo.png" alt="FundsXML" style="max-width:240px;height:auto;margin-bottom:1em;">
      <div class="subtitle">A Practical Handbook for Fund Professionals</div>
      <h1>FundsXML &ndash; The European Standard for Fund Data Exchange</h1>
      <div class="meta">Based on FundsXML Schema Version 4.2.x &nbsp;&middot;&nbsp; 2026</div>
      <div class="summary-box" style="text-align:center;">
        <a class="download-link" href="FundsXML_Book_Complete.html">Read the complete book online &rarr;</a>
        &nbsp;&nbsp;
        <a class="download-link" href="FundsXML_Book.pdf">Download PDF</a>
      </div>
    </header>
IDX_MID

part "Front Matter"
card "ManagementSummary.html" "Management Summary"
part "Part I — Foundations"
card "Chapter01.html" "Chapter 1"
card "Chapter02.html" "Chapter 2"
card "Chapter03.html" "Chapter 3"
part "Part II — FundsXML in Detail"
for ch in 04 05 06 07 08 09; do card "Chapter${ch}.html" "Chapter ${ch}"; done
part "Part III — Implementation and Practice"
for ch in 10 11 12 13; do card "Chapter${ch}.html" "Chapter ${ch}"; done
part "Part IV — Outlook and Reference"
card "Chapter14.html" "Chapter 14"
part "Appendices"
for app in A B C D E; do card "Appendix${app}.html" "Appendix ${app}"; done
card "Index.html" "Index"

cat >> "$IDX" << 'IDX_FOOT'
  </div>
</body>
</html>
IDX_FOOT

# Single theme toggle for the landing page too.
python3 - <<PYEOF
import sys
sys.path.insert(0, "$DIR")
from polish_styles import inject_theme
p = "$IDX"
html = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(inject_theme(html))
PYEOF
echo "Generated landing page: $IDX"

# Build the PDF if node + playwright + build_pdf.js are available.
if command -v node >/dev/null 2>&1 && [ -f "$DIR/build_pdf.js" ]; then
    echo "Generating PDF..."
    ( cd "$DIR" && node build_pdf.js )
else
    echo "Skipping PDF build (node or build_pdf.js missing)."
fi
