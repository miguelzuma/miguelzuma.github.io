#!/usr/bin/env python3
"""Flatten the built site into one print-friendly HTML for review on a phone.

Keeps the text: headings, paragraphs, lists, figure captions and link targets.
Drops navigation, the repeated footer, images and video. Chrome then prints it.
"""
import io, os, re, subprocess, sys
from bs4 import BeautifulSoup

SITE = "_site"
PAGES = [
    ("index.html", "Home"),
    ("research.html", "Research"),
    ("group.html", "Group"),
    ("projects.html", "Projects"),
    ("software.html", "Software"),
    ("talks.html", "Talks"),
    ("outreach.html", "Outreach"),
    ("cv.html", "CV"),
    ("contact.html", "Contact"),
]

CSS = """
@page { size: A4; margin: 16mm 14mm; }
body { font: 11.5pt/1.5 Georgia, 'Times New Roman', serif; color: #111; }
h1 { font-size: 20pt; margin: 0 0 2mm; }
h2 { font-size: 15pt; margin: 7mm 0 2mm; border-bottom: 1px solid #bbb; padding-bottom: 1mm; }
h3 { font-size: 12.5pt; margin: 5mm 0 1.5mm; }
h4 { font-size: 11pt; margin: 4mm 0 1mm; font-variant: small-caps; letter-spacing: .04em; }
p, li { orphans: 2; widows: 2; }
ul { margin: 1.5mm 0 3mm; padding-left: 6mm; }
li { margin-bottom: 1.2mm; }
.pagebreak { page-break-before: always; }
.pagehead { font-size: 8.5pt; letter-spacing: .12em; text-transform: uppercase;
            color: #777; margin: 0 0 3mm; }
.lede { font-style: italic; color: #333; }
.cap { font-size: 9.5pt; color: #555; border-left: 2px solid #ccc;
       padding-left: 3mm; margin: 2mm 0 3mm; }
.meta { font-size: 9.5pt; color: #555; }
a { color: #111; text-decoration: none; }
a::after { content: " <" attr(href) ">"; font-size: 7.5pt; color: #888;
           word-break: break-all; }
a.plain::after { content: ""; }
.toc a::after { content: ""; }
"""

def clean(soup):
    for sel in ["header", "footer", ".skip-link", "script", "style",
                "img", "video", "iframe", "figure > a", ".btn-row"]:
        for el in soup.select(sel):
            el.decompose()
    return soup

def render(path, title):
    html = io.open(os.path.join(SITE, path), encoding="utf-8").read()
    soup = clean(BeautifulSoup(html, "html.parser"))
    main = soup.find("main") or soup.body
    out = [f'<section class="pagebreak"><p class="pagehead">{title}</p>']
    for el in main.find_all(["h1", "h2", "h3", "h4", "p", "li", "figcaption"],
                            recursive=True):
        if el.find_parent("figcaption"):
            continue
        text = " ".join(el.get_text(" ", strip=True).split())
        if not text:
            continue
        name = el.name
        if name == "figcaption":
            out.append(f'<p class="cap">Figure: {text}</p>')
        elif name == "li":
            out.append(f"<li>{el.decode_contents()}</li>")
        else:
            klass = ""
            cls = el.get("class") or []
            if "lede" in cls:
                klass = ' class="lede"'
            elif {"card-meta", "authors", "journal", "person-role"} & set(cls):
                klass = ' class="meta"'
            out.append(f"<{name}{klass}>{el.decode_contents()}</{name}>")
    out.append("</section>")
    body = "\n".join(out)
    body = re.sub(r"(?:<li>.*?</li>\s*)+", lambda m: "<ul>" + m.group(0) + "</ul>", body,
                  flags=re.S)
    return body

def main():
    parts = [f"<style>{CSS}</style>",
             '<h1>Miguel Zumalac&aacute;rregui &mdash; site text</h1>',
             '<p class="meta">Full text of the site-makeover branch, for review. '
             'Images, video and navigation omitted; link targets shown inline.</p>',
             '<ul class="toc">' +
             "".join(f'<li>{t}</li>' for _, t in PAGES) + "</ul>"]
    parts += [render(p, t) for p, t in PAGES]
    out_html = "/tmp/site-review.html"
    io.open(out_html, "w", encoding="utf-8").write("\n".join(parts))
    dest = sys.argv[1] if len(sys.argv) > 1 else "/tmp/site-review.pdf"
    subprocess.run(["google-chrome", "--headless", "--disable-gpu",
                    "--no-sandbox", "--no-pdf-header-footer",
                    f"--print-to-pdf={dest}", "file://" + out_html],
                   check=True, capture_output=True)
    print(dest, os.path.getsize(dest), "bytes")

if __name__ == "__main__":
    main()
