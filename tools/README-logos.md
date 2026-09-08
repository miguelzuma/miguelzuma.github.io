# Where the logo sources come from

`tools/make_support_logos.py` builds everything in `imgs/support/` from files in
`imgs/`. Most of those sources are the institutions' own press or brand files.
Two are derived, and this note records how, so they can be rebuilt if the
originals ever improve.

## `imgs/berkeley_wordmark.png`

The Berkeley wordmark ("Berkeley / UNIVERSITY OF CALIFORNIA") lifted from the
university letterhead template in
`~/Dropbox/Documentos/MSC Berkeley/UCB Letterhead custom.odt`, which carries it
as a vector metafile. Rebuild:

    soffice --headless --convert-to pdf --outdir /tmp "UCB Letterhead custom.odt"
    pdftoppm -r 600 -png -f 1 -l 1 "/tmp/UCB Letterhead custom.pdf" /tmp/ucb
    # then crop to the wordmark's bounding box

## `imgs/nordita_colour_star_white_text.png`

Rasterised from `imgs/nordita_logo_text_colour_star_white_text_CMYK.eps`, which
is the only Nordita file with white lettering and therefore the only one that
suits a dark page. The GIF and PNG beside it set the same star against black
text. Rebuild:

    gs -dQUIET -dNOPAUSE -dBATCH -dEPSCrop -sDEVICE=pngalpha -r600 \
       -sOutputFile=nordita.png imgs/nordita_logo_text_colour_star_white_text_CMYK.eps
    # then trim to the alpha bounding box and downscale to 1600 px wide

## A note on colour

The marks in the "Previously supported by" row keep their brand colour. Only
the lettering is repainted white, and a hue too dark to read against `#0a0c11`
is lifted in value without changing which colour it is. Two wordmarks are navy
rather than black (Berkeley and the BCCP), so they carry a higher `dark_value`
in the script: navy is a colour on paper and a smudge here.
