#!/usr/bin/env python3
"""Pack the built Jekyll site into one self-contained HTML page for review.

Images and video are inlined as data URIs and third-party embeds are swapped
for links, because the preview host blocks every external request. Element ids
are namespaced per page, since all pages share one DOM here and several ids
repeat across them.

Usage:  ruby tools/jekyll_build.rb . _site && python3 tools/make_preview.py out.html
"""
import base64, io, mimetypes, os, re, sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "_site")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "site-preview.html")

PAGES = [
    ("home", "index.html", "Home"),
    ("research", "research.html", "Research"),
    ("group", "group.html", "Group"),
    ("projects", "projects.html", "Projects"),
    ("software", "software.html", "Software"),
    ("talks", "talks.html", "Talks"),
    ("outreach", "outreach.html", "Outreach"),
    ("cv", "cv.html", "CV"),
    ("contact", "contact.html", "Contact"),
]
SLUG = {f: s for s, f, _ in PAGES}

MAX_W = 760
_cache = {}


def data_uri(path):
    """Inline an asset, downscaling raster images to keep the page reasonable."""
    if path in _cache:
        return _cache[path]
    full = os.path.join(SITE, path.lstrip("/"))
    if not os.path.exists(full):
        return None
    ext = os.path.splitext(full)[1].lower()
    if ext == ".gif":                       # animated; re-encoding would flatten it
        raw, mime = open(full, "rb").read(), "image/gif"
    elif ext in (".png", ".jpg", ".jpeg"):
        im = Image.open(full)
        if im.width > MAX_W:
            im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        transparent = im.convert("RGBA").getchannel("A").getextrema()[0] < 250
        if ext == ".png" and transparent:
            im.save(buf, "PNG", optimize=True)
            mime = "image/png"
        else:
            im.convert("RGB").save(buf, "JPEG", quality=78, optimize=True)
            mime = "image/jpeg"
        raw = buf.getvalue()
    else:
        raw = open(full, "rb").read()
        mime = mimetypes.guess_type(full)[0] or "application/octet-stream"
    uri = f"data:{mime};base64,{base64.b64encode(raw).decode()}"
    _cache[path] = uri
    return uri


EMBED_LABELS = {
    "youtube-nocookie.com/embed/zv9tStMviwA":
        ("Introductory video on gravitational-wave lensing",
         "https://www.youtube.com/watch?v=zv9tStMviwA", "YouTube"),
    "prezi.com/embed/ebm8rviupnqz":
        ("Cosmology overview presentation",
         "https://prezi.com/ebm8rviupnqz/", "Prezi"),
    "prezi.com/embed/a2mhizem_sod":
        ("PhD defense: Probing the Foundations of the Standard Cosmological Model",
         "https://prezi.com/a2mhizem_sod/", "Prezi"),
}


def replace_iframe(m):
    tag = m.group(0)
    src = re.search(r'src="([^"]+)"', tag).group(1)
    title = re.search(r'title="([^"]*)"', tag)
    title = title.group(1) if title else "Embedded media"
    for key, (label, url, host) in EMBED_LABELS.items():
        if key in src:
            return (f'<a class="embed-stub" href="{url}" rel="noopener">'
                    f'<span class="embed-stub-kind">{host} embed</span>'
                    f'<span class="embed-stub-title">{label}</span>'
                    '<span class="embed-stub-note">Blocked in this preview — opens on the live site</span></a>')
    if "ivoox" in src:
        return ('<a class="embed-stub embed-stub-audio" '
                'href="https://www.ivoox.com/podcast-horizonte-sucesos-cine-ciencia-entre_sq_f1432346_1.html" rel="noopener">'
                '<span class="embed-stub-kind">Podcast player</span>'
                f'<span class="embed-stub-title">{title}</span>'
                '<span class="embed-stub-note">Blocked in this preview — opens on the live site</span></a>')
    return f'<p class="embed-stub-plain">[embed: {title}]</p>'


def build_page(slug, filename):
    html = open(os.path.join(SITE, filename), encoding="utf-8").read()
    body = re.search(r'<main id="main">(.*?)</main>', html, re.S).group(1)

    ids = set(re.findall(r'\sid="([^"]+)"', body))
    body = re.sub(r'(\sid=")([^"]+)(")', lambda m: f'{m.group(1)}{slug}--{m.group(2)}{m.group(3)}', body)
    body = re.sub(r'(\saria-labelledby=")([^"]+)(")',
                  lambda m: f'{m.group(1)}{slug}--{m.group(2)}{m.group(3)}', body)

    def fix_href(m):
        href = m.group(1)
        if href.startswith("#"):
            frag = href[1:]
            return f'href="#{slug}--{frag}"' if frag in ids else f'href="{href}"'
        if href.startswith("/") and href.endswith(".html"):
            target = SLUG.get(href.lstrip("/"))
            return f'href="#" data-goto="{target}"' if target else 'href="#"'
        m2 = re.match(r'^/([a-z0-9_]+\.html)#(.+)$', href)
        if m2 and m2.group(1) in SLUG:
            return f'href="#" data-goto="{SLUG[m2.group(1)]}" data-frag="{SLUG[m2.group(1)]}--{m2.group(2)}"'
        if href.startswith("/"):
            return 'href="#" data-local="1"'      # PDFs etc. — nothing to link to here
        return m.group(0)

    body = re.sub(r'href="([^"]+)"', fix_href, body)
    body = re.sub(r'<iframe\b[^>]*>\s*</iframe>', replace_iframe, body, flags=re.S)

    def fix_img(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        if not src or not src.group(1).startswith("/"):
            return tag
        uri = data_uri(src.group(1))
        return tag.replace(src.group(1), uri) if uri else tag

    body = re.sub(r'<img\b[^>]*>', fix_img, body)

    def fix_source(m):
        src = re.search(r'src="([^"]+)"', m.group(0))
        if not src:
            return m.group(0)
        uri = data_uri(src.group(1))
        return m.group(0).replace(src.group(1), uri) if uri else ""

    body = re.sub(r'<source\b[^>]*>', fix_source, body)
    body = re.sub(r'(poster=")(/[^"]+)(")',
                  lambda m: m.group(1) + (data_uri(m.group(2)) or "") + m.group(3), body)
    body = re.sub(r'<script\b.*?</script>', '', body, flags=re.S)
    return body


site_css = open(os.path.join(SITE, "assets/css/main.css"), encoding="utf-8").read()

footer = re.search(r'<footer class="site-footer">(.*?)</footer>',
                   open(os.path.join(SITE, "index.html"), encoding="utf-8").read(), re.S).group(1)
footer = re.sub(r'href="/[^"]*"', 'href="#"', footer)

nav = "\n".join(
    f'      <button type="button" class="pv-tab" data-goto="{s}"'
    f'{" aria-current=\"page\"" if i == 0 else ""}>{label}</button>'
    for i, (s, _, label) in enumerate(PAGES))

sections = "\n".join(
    f'<section class="pv-page" id="pv-{s}"{"" if i == 0 else " hidden"}>{build_page(s, f)}</section>'
    for i, (s, f, _) in enumerate(PAGES))

CHROME = """
/* ---- Preview chrome -------------------------------------------------
   Deliberately quiet and visually distinct from the site itself, so what
   you are reviewing is the site, not this wrapper. */
.pv-bar {
  position: sticky; top: 0; z-index: 60;
  background: #0d1017; border-bottom: 1px solid var(--border);
}
.pv-bar-inner {
  max-width: var(--measure); margin: 0 auto; padding: 0.55rem 1.25rem;
  display: flex; flex-wrap: wrap; align-items: center; gap: 0.4rem 1.2rem;
}
.pv-label {
  font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.13em;
  font-weight: 650; color: var(--text-mute); white-space: nowrap;
}
.pv-tabs { display: flex; flex-wrap: wrap; gap: 0.2rem; margin-left: auto; }
.pv-tab {
  font: inherit; font-size: 0.9rem; font-weight: 500;
  background: none; border: 0; border-radius: 6px;
  padding: 0.28em 0.62em; color: var(--text-soft); cursor: pointer;
}
.pv-tab:hover { color: var(--text); background: var(--bg-card); }
.pv-tab[aria-current="page"] {
  color: var(--accent-strong); background: var(--bg-card);
  box-shadow: inset 0 -2px 0 var(--accent);
}
.pv-note {
  max-width: var(--measure); margin: 0 auto; padding: 0.9rem 1.25rem 0;
  font-size: 0.84rem; color: var(--text-mute);
}
.pv-page[hidden] { display: none; }

/* Stand-ins for embeds the sandbox blocks */
.embed-stub {
  display: block; max-width: 760px; margin: 1.4rem 0;
  padding: 1.1rem 1.25rem; border: 1px dashed var(--border-strong);
  border-radius: var(--radius); background: var(--bg-raised);
  text-decoration: none; color: inherit;
}
.embed-stub:hover, .embed-stub:focus-visible {
  border-color: var(--accent-dim); background: #1a1e2d;
}
.embed-stub-kind {
  display: block; font-size: 0.68rem; text-transform: uppercase;
  letter-spacing: 0.12em; font-weight: 650; color: var(--accent); margin-bottom: 0.3rem;
}
.embed-stub-title { display: block; font-weight: 600; color: var(--text); }
.embed-stub-note { display: block; font-size: 0.8rem; color: var(--text-mute); margin-top: 0.25rem; }
.embed-stub-audio { margin-bottom: 0.7rem; }
"""

page = f"""<title>Site preview — Miguel Zumalacárregui</title>
<style>
{site_css}
{CHROME}
</style>

<div class="pv-bar">
  <div class="pv-bar-inner">
    <span class="pv-label">Preview · site-makeover branch</span>
    <nav class="pv-tabs" aria-label="Preview pages">
{nav}
    </nav>
  </div>
</div>

<p class="pv-note">
  Static preview of the rebuilt site. Everything is the real Jekyll output;
  only third-party embeds (YouTube, Prezi, podcast players) and PDF links are
  inert here, since the sandbox blocks outside requests.
</p>

{sections}

<footer class="site-footer">{footer}</footer>

<script>
(function () {{
  var tabs = document.querySelectorAll('.pv-tab');
  var pages = document.querySelectorAll('.pv-page');

  function show(slug, frag) {{
    pages.forEach(function (p) {{ p.hidden = (p.id !== 'pv-' + slug); }});
    tabs.forEach(function (t) {{
      if (t.dataset.goto === slug) t.setAttribute('aria-current', 'page');
      else t.removeAttribute('aria-current');
    }});
    if (frag) {{
      var el = document.getElementById(frag);
      if (el) {{ el.scrollIntoView({{ block: 'start' }}); return; }}
    }}
    window.scrollTo(0, 0);
  }}

  document.addEventListener('click', function (e) {{
    var el = e.target.closest('[data-goto]');
    if (el) {{ e.preventDefault(); show(el.dataset.goto, el.dataset.frag); return; }}
    var dead = e.target.closest('[data-local]');
    if (dead) e.preventDefault();
  }});

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {{
    document.querySelectorAll('video[autoplay]').forEach(function (v) {{
      v.removeAttribute('autoplay'); v.controls = true; v.pause();
    }});
  }}
}})();
</script>
"""


def css_escape(text):
    """CSS does not decode HTML entities, so non-ASCII there needs \\XXXX escapes."""
    return "".join(c if ord(c) < 128 else f"\\{ord(c):04X} " for c in text)


def html_escape(text):
    return text.encode("ascii", "xmlcharrefreplace").decode("ascii")


# Escape the style block as CSS and everything else as HTML, so the page renders
# identically no matter what charset the host or server declares.
head, rest = page.split("<style>", 1)
css_body, tail = rest.split("</style>", 1)
body, script = tail.split("<script>", 1)

page = (html_escape(head) + "<style>" + css_escape(css_body) + "</style>"
        + html_escape(body) + "<script>" + script)

assert page.isascii(), "non-ASCII survived escaping"
open(OUT, "w", encoding="ascii").write(page)
print(f"wrote {OUT}  ({len(page)/1024/1024:.2f} MB, ascii-safe)")
