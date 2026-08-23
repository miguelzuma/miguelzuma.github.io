#!/usr/bin/env python3
r"""Generate the site icons: a script M with a subscript z.

The mark is the redshifted chirp mass, $\mathcal{M}_z$ — the one parameter a
gravitational-wave detection measures best, and also the owner's initials.

The outlines come from Computer Modern (cmsy10's calligraphic M and cmmi10's
italic z), lifted once from a LaTeX run and baked in below, so regenerating
the icons needs no TeX. To re-derive them:

    latex mz.tex && dvisvgm --no-fonts --exact --bbox=min -p1 -o M.svg mz.dvi

with mz.tex containing $\mathcal{M}$ and $z$ on separate pages; --bbox=min
makes dvisvgm report each glyph's tight bounding box, which is what lets the
two be composed and then scaled to fill the icon square exactly.

Set as a true subscript the mark is nearly twice as wide as it is tall and
swims in empty space at 16px, so the z is enlarged and tucked under the M's
right arm until the composite is close to square. The outlines are also
stroked in their own color: these are text fonts, and their hairlines
disappear below about 24px.

Usage:  python3 tools/make_icons.py [scheme]
        scheme = amber (default) | cyan | gold | mono

Writes favicon.svg, favicon-32.png and apple-touch-icon.png in the repo root.
Rasterizing uses headless Chrome, as tools/make_review_pdf.py already does.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Glyph outlines and their bounding boxes relative to each glyph's own origin,
# as (x, y, width, height) in TeX points.
M_PATH = "M3.835616-5.569116C4.104608-4.273973 4.542964-2.141968 5.110834-.986301C5.330012-.557908 5.439601-.33873 5.539228-.33873C5.579078-.33873 5.599004-.33873 5.778331-.518057C6.535492-1.24533 7.053549-1.823163 7.750934-2.620174L9.932752-5.160648C9.793275-4.313823 9.43462-2.072229 9.43462-.9066C9.43462-.637609 9.444583-.37858 9.474471-.109589C9.484433 0 9.524284 .288917 9.942715 .288917S11.118306-.14944 11.118306-.348692C11.118306-.408468 11.058531-.418431 11.028643-.418431C10.899128-.418431 10.699875-.328767 10.590286-.259029C10.351183-.288917 10.331258-.448319 10.311333-.67746C10.281445-.996264 10.281445-1.295143 10.281445-1.334994C10.281445-2.440847 10.719801-5.459527 11.008717-6.694894C11.01868-6.764633 11.028643-6.784558 11.028643-6.864259C11.028643-6.90411 11.01868-7.013699 10.948941-7.013699C10.909091-7.013699 10.899128-7.003736 10.709838-6.784558C9.77335-5.648817 6.864259-2.161893 5.877958-1.325031C5.628892-1.853051 5.449564-2.231631 5.100872-3.626401C4.811955-4.752179 4.64259-5.579078 4.473225-6.545455C4.443337-6.684932 4.393524-6.953923 4.393524-6.973848C4.363636-7.023661 4.313823-7.023661 4.283935-7.023661C4.104608-7.023661 3.686177-6.804483 3.656289-6.595268C3.536737-5.758406 3.337484-4.443337 2.6401-2.540473C1.843088-.418431 1.62391-.418431 1.43462-.418431C1.305106-.418431 .936488-.498132 .71731-.697385C.667497-.747198 .647572-.747198 .627646-.747198C.488169-.747198 .268991-.298879 .268991-.019925C.268991 .069738 .268991 .18929 .587796 .358655C.836862 .488169 1.075965 .498132 1.125778 .498132C1.743462 .498132 2.331258-.926526 2.530511-1.43462C2.998755-2.560399 3.556663-4.134496 3.835616-5.569116Z"
M_BBOX = (0.268991, -7.023662, 10.849315, 7.521793)
Z_PATH = "M1.325031-.826899C1.863014-1.404732 2.15193-1.653798 2.510585-1.96264C2.510585-1.972603 3.128269-2.500623 3.486924-2.859278C4.433375-3.785803 4.652553-4.26401 4.652553-4.303861C4.652553-4.403487 4.562889-4.403487 4.542964-4.403487C4.473225-4.403487 4.443337-4.383562 4.393524-4.293898C4.094645-3.815691 3.88543-3.656289 3.646326-3.656289S3.287671-3.805729 3.138232-3.975093C2.948941-4.204234 2.779577-4.403487 2.450809-4.403487C1.703611-4.403487 1.24533-3.476961 1.24533-3.267746C1.24533-3.217933 1.275218-3.158157 1.364882-3.158157S1.474471-3.20797 1.494396-3.267746C1.683686-3.726027 2.261519-3.73599 2.34122-3.73599C2.550436-3.73599 2.739726-3.666252 2.968867-3.58655C3.367372-3.437111 3.476961-3.437111 3.73599-3.437111C3.377335-3.008717 2.540473-2.291407 2.351183-2.132005L1.454545-1.295143C.777086-.627646 .428394-.059776 .428394 .009963C.428394 .109589 .52802 .109589 .547945 .109589C.627646 .109589 .647572 .089664 .707347-.019925C.936488-.368618 1.235367-.637609 1.554172-.637609C1.783313-.637609 1.882939-.547945 2.132005-.259029C2.30137-.049813 2.480697 .109589 2.769614 .109589C3.755915 .109589 4.333748-1.155666 4.333748-1.424658C4.333748-1.474471 4.293898-1.524284 4.214197-1.524284C4.124533-1.524284 4.104608-1.464508 4.07472-1.39477C3.845579-.747198 3.20797-.557908 2.879203-.557908C2.67995-.557908 2.500623-.617684 2.291407-.687422C1.952677-.816936 1.803238-.856787 1.594022-.856787C1.574097-.856787 1.414695-.856787 1.325031-.826899Z"
Z_BBOX = (0.428393, -4.403487, 4.224159, 4.513076)

# Composition, in units of the M's own size.
ZFRAC = 0.72   # z height as a fraction of the M's height
GAP = -0.18    # space after the M, in M widths; negative tucks the z under it
DROP = 0.40    # how far the z's bottom falls below the M's, in M heights

# The favicon sits on an unknown ground — a white browser tab or a dark one —
# so it uses the palette's dimmer, higher-contrast pair. The touch icon has a
# known dark tile behind it and can use the brighter site colors.
SCHEMES = {
    #          favicon M   favicon z   touch M    touch z
    "amber": ("#8b74e8", "#d9853f", "#b7a2ff", "#e8963f"),
    "cyan":  ("#8b74e8", "#3aa8c4", "#b7a2ff", "#6fd8ee"),
    "gold":  ("#8b74e8", "#d9a63f", "#b7a2ff", "#e8b54a"),
    "mono":  ("#8b74e8", "#8b74e8", "#b7a2ff", "#b7a2ff"),
}
TILE = "#151926"   # --bg-card, the ground iOS composites the touch icon on

TITLE = "Miguel Zumalacárregui"
LABEL = "Script M with subscript z, the redshifted chirp mass"


def build_svg(size, pad, bold, col_m, col_z, ground=None):
    """Compose the mark into a square viewBox and return the SVG source."""
    mx, my, mw, mh = M_BBOX
    zx, zy, zw, zh = Z_BBOX
    k = (ZFRAC * mh) / zh
    zox = mw + GAP * mw - zx * k
    zoy = mh + DROP * mh - (zy + zh) * k
    w = max(mw, zox + (zx + zw) * k)
    h = max(mh, zoy + (zy + zh) * k)
    s = (size - 2 * pad) / max(w, h)
    offx = (size - w * s) / 2
    offy = (size - h * s) / 2
    # Stroke widths are given in glyph units, so undo the enclosing scales.
    bw_m = bold * size / s
    bw_z = bw_m / k
    sk_m = f' stroke="{col_m}" stroke-width="{bw_m:.4f}" stroke-linejoin="round"'
    sk_z = f' stroke="{col_z}" stroke-width="{bw_z:.4f}" stroke-linejoin="round"'
    bg = f'  <rect width="{size}" height="{size}" fill="{ground}"/>\n' if ground else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}"'
        f' role="img" aria-label="{LABEL}">\n'
        f'  <title>{TITLE}</title>\n'
        f'{bg}'
        f'  <g transform="translate({offx:.3f},{offy:.3f}) scale({s:.6f})">\n'
        f'    <g transform="translate({-mx:.4f},{-my:.4f})">'
        f'<path fill="{col_m}"{sk_m} d="{M_PATH}"/></g>\n'
        f'    <g transform="translate({zox:.4f},{zoy:.4f}) scale({k:.6f})">'
        f'<path fill="{col_z}"{sk_z} d="{Z_PATH}"/></g>\n'
        f'  </g>\n</svg>\n')


def rasterize(svg_source, size, out, transparent=True):
    """Render SVG source to a PNG of exactly `size` square, via Chrome."""
    tmp_svg = out + ".tmp.svg"
    tmp_html = out + ".tmp.html"
    with open(tmp_svg, "w", encoding="utf-8") as fh:
        fh.write(svg_source)
    body = "" if transparent else "background:#000;"
    with open(tmp_html, "w", encoding="utf-8") as fh:
        fh.write(f'<style>html,body{{margin:0;padding:0;{body}'
                 f'width:{size}px;height:{size}px;overflow:hidden}}'
                 f'img{{display:block;width:{size}px;height:{size}px}}</style>'
                 f'<img src="file://{os.path.abspath(tmp_svg)}">')
    cmd = ["google-chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars",
           "--force-device-scale-factor=1", f"--window-size={size},{size}",
           f"--screenshot={out}", tmp_html]
    if transparent:
        cmd.insert(4, "--default-background-color=00000000")
    subprocess.run(cmd, check=True, capture_output=True)
    os.remove(tmp_svg)
    os.remove(tmp_html)
    return out


def main():
    scheme = sys.argv[1] if len(sys.argv) > 1 else "amber"
    if scheme not in SCHEMES:
        sys.exit(f"unknown scheme {scheme!r}; choose from {', '.join(SCHEMES)}")
    fav_m, fav_z, touch_m, touch_z = SCHEMES[scheme]

    favicon = build_svg(64, pad=2.0, bold=0.013, col_m=fav_m, col_z=fav_z)
    path = os.path.join(ROOT, "favicon.svg")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(favicon)
    print("wrote", path)

    # The 32px PNG is the fallback for browsers that ignore SVG favicons.
    print("wrote", rasterize(favicon, 32, os.path.join(ROOT, "favicon-32.png")))

    # iOS rounds the corners of the touch icon and composites it on an opaque
    # tile, so this one carries its own ground and keeps clear of the edges.
    touch = build_svg(180, pad=26.0, bold=0.005, col_m=touch_m, col_z=touch_z,
                      ground=TILE)
    print("wrote", rasterize(touch, 180, os.path.join(ROOT, "apple-touch-icon.png"),
                             transparent=False))


if __name__ == "__main__":
    main()
