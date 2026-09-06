#!/usr/bin/env python3
"""Build the small white marks for the home page's "Supported by" strip.

The originals in imgs/ are institutional files of wildly different sizes and
colour treatments, and three of them are wrong for a near-black background:
the IFT and Max Planck Society marks are dark artwork, and the AEI wordmark is
white but has an alpha channel that peaks at 136 of 255, so it renders at
roughly half opacity. This script normalises all six into imgs/support/ at
twice their CSS display height and leaves the originals untouched.

Run it after replacing any source file:  python3 tools/make_support_logos.py
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "imgs" / "support"

# (output name, source, display height in CSS px, whiten, renormalise alpha)
MARKS = [
    ("ift.png",        "ift_logo.png",                             44, True,  False),
    ("aei.png",        "MPI-AEI_wide_E_neg_rgb_transparent.png",   32, False, True),
    ("erc-eu.png",     "erc_eu_funding_dark.png",                  44, False, False),
    ("miciu-aei.png",  "logo_miciu_aei_dark.png",                  32, False, False),
    ("csic.png",       "logo_csic_dark.png",                       32, False, False),
    ("mpg.png",        "2560px-Max-Planck-Gesellschaft.png",       44, True,  False),
]

SCALE = 2  # serve at twice the CSS height, for high-density screens


def build(name, source, css_height, whiten, renormalise):
    img = Image.open(ROOT / "imgs" / source).convert("RGBA")
    r, g, b, a = img.split()

    if whiten:
        # The standard negative treatment for a monochrome mark: keep the
        # shape the alpha channel describes, paint it white.
        white = Image.new("L", img.size, 255)
        r, g, b = white, white.copy(), white.copy()

    if renormalise:
        peak = a.getextrema()[1]
        if peak and peak < 255:
            a = a.point(lambda v, p=peak: min(255, round(v * 255 / p)))

    img = Image.merge("RGBA", (r, g, b, a))

    target_h = css_height * SCALE
    target_w = max(1, round(img.width * target_h / img.height))
    img = img.resize((target_w, target_h), Image.LANCZOS)

    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / name, optimize=True)
    return target_w, target_h


if __name__ == "__main__":
    for name, source, h, whiten, renorm in MARKS:
        w, th = build(name, source, h, whiten, renorm)
        print(f"{name:<15} {w}x{th}  from {source}")
