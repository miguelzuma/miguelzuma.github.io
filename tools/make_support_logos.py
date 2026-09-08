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
  key_white   drop the white page a mark was printed on, for a source with no
              transparency (Heidelberg, Marie Curie, the Berkeley wordmark)
  negative    keep the brand colour and paint only the near-grey parts white,
              lifting any colour too dark to read against #0a0c11
  dark_value  where that treatment puts the line between a dark hue worth
              keeping and lettering to be whitened (default 0.28)
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

# The trajectory strip, most recent first. These keep their brand colour: the
# lettering goes white so it reads on the dark ground, and everything with a hue
# stays as the institution drew it. Two of the sources are derived rather than
# shipped, and tools/README-logos.md records where they came from:
# berkeley_wordmark.png is lifted from the Berkeley letterhead, and
# nordita_colour_star_white_text.png is the white-text EPS in imgs/ rasterised
# with ghostscript, which is the only Nordita file that suits a dark page.
PAST = [
    ("past-berkeley.png",   "berkeley_wordmark.png",
     30, {"negative": True, "key_white": True, "dark_value": 0.42,
          "crop": "alpha"}),
    ("past-bccp.png",       "bccp_logo.png",
     30, {"negative": True, "dark_value": 0.42, "crop": "alpha"}),
    ("past-marie-curie.png", "logo_marie-curie.jpg",
     40, {"negative": True, "key_white": True, "dark_value": 0.10,
          "crop": "alpha"}),
    ("past-nordita.png",    "nordita_colour_star_white_text.png",
     30, {"crop": "alpha"}),
    ("past-heidelberg.png", "logo_HD.jpg",
     40, {"negative": True, "key_white": True, "crop": "alpha"}),
    ("past-iccub.png",      "logo_iccub_grande_invertit.png",
     40, {"negative": True, "colour_only": True, "crop": "alpha"}),
    ("past-uam.png",        "logo_UAM_trans.gif",
     30, {"negative": True, "crop": "alpha"}),
]


# What counts as lettering rather than as colour: too little chroma to be a
# brand colour, or too dark to be one. The dark cut is per mark, because it is
# the one judgement that varies: the Berkeley and BCCP wordmarks are navy,
# which is a hue on paper and a smudge on a near-black page, while the Marie
# Curie block wants every one of its portraits kept, dark purple included.
GREY_CHROMA = 0.22
DARK_VALUE = 0.28
# A hue that survives both tests is lifted to at least this value, so it reads
# against #0a0c11 without changing which colour it is.
MIN_VALUE = 0.72


def to_negative(img, unpremultiply=False, dark_value=DARK_VALUE):
    """Paint the lettering white and keep the colour, brightened if need be.

    A mark drawn for a white page is black text plus brand colour. Inverting it
    wholesale would turn the colour into its complement, and whitening it
    wholesale would throw the colour away, so the two parts are separated by
    saturation: near-grey pixels become white, and hues are kept and lifted to
    a value that reads against the near-black background.
    """
    import numpy as np

    a = np.asarray(img).astype(np.float32) / 255.0
    rgb, alpha = a[..., :3], a[..., 3:]

    # Lettering and colour are told apart on the source as it stands, before
    # any un-premultiplying: dividing a pale anti-aliased grey by its small
    # alpha amplifies a couple of levels of JPEG chroma into a saturated hue,
    # which once turned the whole Heidelberg wordmark red.
    high = rgb.max(axis=2, keepdims=True)
    chroma = high - rgb.min(axis=2, keepdims=True)

    if unpremultiply:
        # The source was composited on white, so recover the mark's own colour
        # before touching it. Nearly transparent pixels stay as they are.
        safe = np.maximum(alpha, 1e-3)
        rgb = np.clip((rgb - (1.0 - alpha)) / safe, 0.0, 1.0)
        high = rgb.max(axis=2, keepdims=True)

    # Ramped rather than switched, so an anti-aliased edge between the colour
    # and the lettering does not band.
    colourness = np.minimum(
        np.clip(chroma / GREY_CHROMA, 0.0, 1.0),
        np.clip((high - dark_value) / 0.12, 0.0, 1.0),
    )

    lifted = rgb * np.maximum(1.0, MIN_VALUE / np.maximum(high, 1e-6))
    out = colourness * np.clip(lifted, 0.0, 1.0) + (1.0 - colourness) * 1.0

    return Image.fromarray(
        (np.concatenate([out, alpha], axis=2) * 255).round().astype(np.uint8), "RGBA")


def build(name, source, css_height, whiten=False, renorm=False,
          key_white=False, negative=False, dark_value=DARK_VALUE,
          colour_only=False, crop=None):
    img = Image.open(ROOT / "imgs" / source).convert("RGBA")
    r, g, b, a = img.split()

    if key_white:
        # Distance from white becomes opacity, so the page the mark was printed
        # on falls away while the artwork keeps its anti-aliased edges. The
        # darkest channel drives it, which leaves a saturated colour (the
        # Heidelberg red, the Marie Curie yellow) fully opaque.
        darkest = ImageChops.darker(ImageChops.darker(r, g), b)
        a = ImageChops.invert(darkest)

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

    if negative:
        img = to_negative(img, unpremultiply=key_white, dark_value=dark_value)

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
