"""Assemble the site's visible prose into one HTML file for LibreOffice.

Reads the built pages, keeps only <main>, drops the navigation furniture
(subnav pill rows, button rows) and non-text media, and prefixes each page
with a heading so edits can be traced back to a source file.

Usage:  python3 tools/extract_site_text.py _site out.html
Normally run via tools/make_review_doc.sh, which also converts the HTML
to ODT and PDF and copies them to ~/Dropbox/website_text/.
"""
import html
import re
import sys
from pathlib import Path

SITE = Path(sys.argv[1])
OUT = Path(sys.argv[2])

PAGES = [
    ("index.html", "Home"),
    ("research.html", "Research"),
    ("group.html", "Group"),
    ("projects.html", "Projects & Funding"),
    ("software.html", "Software"),
    ("talks.html", "Talks & Teaching"),
    ("outreach.html", "Outreach"),
    ("cv.html", "CV"),
    ("contact.html", "Contact"),
]

# Blocks that are navigation or media rather than prose. Figures stay: the
# <figure> wrapper and its media are dropped below, but the caption is text
# the reader sees and so belongs in the document.
DROP_BLOCKS = [
    r'<nav\b[^>]*>.*?</nav>',
    r'<div class="btn-row">.*?</div>',
    r'<div class="video">.*?</div>',
    r'<script\b[^>]*>.*?</script>',
    r'<video\b[^>]*>.*?</video>',
    r'<source\b[^>]*>',
    r'<picture\b[^>]*>|</picture>',
    r'<img\b[^>]*>',
    r'<svg\b[^>]*>.*?</svg>',
    # A photographer's credit is not prose to revise.
    r'<figcaption class="photo-credit">.*?</figcaption>',
    # The research-page rosette legend repeats the subnav labels, not prose.
    r'<div class="venn-hero"[^>]*>.*?</ul>\s*</div>',
]


def extract(path):
    raw = path.read_text(encoding="utf-8")
    body = re.search(r'<main\b[^>]*>(.*?)</main>', raw, re.S).group(1)
    for pat in DROP_BLOCKS:
        body = re.sub(pat, '', body, flags=re.S)
    # Cards are links wrapping prose: keep the words, drop the link chrome so
    # the document does not read as a wall of blue.
    body = re.sub(r'<a class="card card-link"[^>]*>', '<div>', body)
    # Label captions, so it is obvious which text belongs to which picture and
    # an edit can be routed back to the right figcaption.
    body = re.sub(r'<figcaption[^>]*>', '<p><i>Figure caption:</i> ', body)
    body = body.replace('</figcaption>', '</p>')
    # Demote everything one level: the page title becomes the h1.
    for n in (5, 4, 3, 2, 1):
        body = re.sub(rf'<(/?)h{n}\b', rf'<\g<1>h{min(n + 1, 6)}', body)
    return body


parts = [
    '<html><head><meta charset="utf-8">'
    '<title>miguelzuma.github.io — site text</title></head><body>',
    '<h1>Site text — miguelzuma.github.io</h1>',
    '<p><i>One section per page, in navigation order. Headings carry the '
    'source file name so edits can be traced back. Navigation, buttons, '
    'images and video captions are omitted.</i></p>',
]

for fname, label in PAGES:
    path = SITE / fname
    if not path.exists():
        print(f"missing: {fname}", file=sys.stderr)
        continue
    parts.append('<hr/>')
    parts.append(f'<h1>{html.escape(label)} <span style="color:#888">'
                 f'[{html.escape(fname)}]</span></h1>')
    parts.append(extract(path))

parts.append('</body></html>')
OUT.write_text('\n'.join(parts), encoding="utf-8")
print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")
