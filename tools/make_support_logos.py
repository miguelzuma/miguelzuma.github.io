#!/usr/bin/env python3
"""Build the small white marks for the home page's logo strips.

The originals in imgs/ are institutional files of wildly different sizes and
colour treatments, and most of them are wrong for a near-black background: the
IFT, Max Planck Society, Nordita and UAM marks are dark artwork, the AEI
wordmark is white but has an alpha channel that peaks at 136 of 255 (so it
renders at roughly half opacity), and the Heidelberg mark is a JPEG with no
alpha at all. This script normalises them into imgs/support/ at twice their CSS
display height and leaves the originals untouched.

Run it after replacing any source file:  python3 tools/make_support_logos.py

Options per mark:
  whiten      paint the shape white, keeping the alpha channel that describes it
  renorm      rescale alpha so the artwork reaches full opacity
  key_white   derive alpha from darkness, for a mark that ships on white with
              no transparency (Heidelberg)
  colour_only keep the coloured pixels and drop the white ones, which on the
              ICCUB lockup leaves the mark without the white leaf behind it
              and without the institute's name (unreadable at 34 px anyway)
  crop        "alpha"  trim to the bounding box of the visible pixels
"""

from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "imgs" / "support"

SCALE = 2  # serve at twice the CSS height, for high-density screens

# Institutions and funders behind the work today.
MARKS = [
    ("ift.png",       "ift_logo.png",                           44, {"whiten": True}),
    ("aei.png",       "MPI-AEI_wide_E_neg_rgb_transparent.png", 32, {"renorm": True}),
    ("erc-eu.png",    "erc_eu_funding_dark.png",                44, {}),
    ("miciu-aei.png", "logo_miciu_aei_dark.png",                32, {}),
    ("csic.png",      "logo_csic_dark.png",                     32, {}),
    ("mpg.png",       "2560px-Max-Planck-Gesellschaft.png",     44, {"whiten": True}),
]

# The trajectory strip: every past mark is whitened, so the row reads as one
# quiet band of history rather than as six competing brand palettes.
PAST = [
    ("past-berkeley.png",   "bccp_logo_w.png",
     26, {"whiten": True, "crop": "alpha"}),
    ("past-nordita.png",    "nordita_logo_textfull_colour_star_black_text_425x115.gif",
     26, {"whiten": True, "crop": "alpha"}),
    ("past-heidelberg.png", "logo_HD.jpg",
     34, {"whiten": True, "key_white": True, "crop": "alpha"}),
    ("past-iccub.png",      "logo_iccub_grande_invertit.png",
     34, {"whiten": True, "colour_only": True, "crop": "alpha"}),
    ("past-uam.png",        "logo_UAM_trans.gif",
     26, {"whiten": True, "crop": "alpha"}),
]


def build(name, source, css_height, whiten=False, renorm=False,
          key_white=False, colour_only=False, crop=None):
    img = Image.open(ROOT / "imgs" / source).convert("RGBA")
    r, g, b, a = img.split()

    if key_white:
        # Darkness becomes opacity: the white page the mark was printed on
        # falls away and the artwork keeps its anti-aliased edges.
        grey = Image.merge("RGB", (r, g, b)).convert("L")
        a = ImageChops.invert(grey)

    if renorm:
        peak = a.getextrema()[1]
        if peak and peak < 255:
            a = a.point(lambda v, p=peak: min(255, round(v * 255 / p)))

    if colour_only:
        # Saturation, not luminance, separates the mark from the white shapes
        # around it: the ICCUB lockup sets its blue line art over a solid white
        # leaf, and whitening the leaf would swallow the mark whole. The test
        # has to run over visible pixels only, because a fully transparent
        # pixel still carries an arbitrary RGB value and can look saturated.
        sat = Image.merge("RGB", (r, g, b)).convert("HSV").split()[1]
        sat = ImageChops.multiply(sat, a.point(lambda v: 255 if v > 20 else 0))
        # Ramped rather than thresholded, so anti-aliased edges survive.
        a = ImageChops.multiply(a, sat.point(lambda v: min(255, round(v * 255 / 60))))

    if crop == "alpha":
        box = a.point(lambda v: 255 if v > 20 else 0).getbbox()
    else:
        box = None

    if box:
        r, g, b, a = (ch.crop(box) for ch in (r, g, b, a))

    if whiten:
        # The standard negative treatment for a monochrome mark: keep the
        # shape the alpha channel describes, paint it white.
        white = Image.new("L", a.size, 255)
        r, g, b = white, white.copy(), white.copy()

    img = Image.merge("RGBA", (r, g, b, a))

    target_h = css_height * SCALE
    target_w = max(1, round(img.width * target_h / img.height))
    img = img.resize((target_w, target_h), Image.LANCZOS)

    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / name, optimize=True)
    return target_w, target_h


if __name__ == "__main__":
    for name, source, height, opts in MARKS + PAST:
        w, h = build(name, source, height, **opts)
        print(f"{name:<20} {w}x{h}  from {source}")
