#!/usr/bin/env bash
# Regenerate the site-text review documents and drop them in Dropbox.
#
# Builds the site, extracts the visible prose into one HTML file
# (tools/extract_site_text.py), converts it to ODT + PDF with LibreOffice,
# and copies both to ~/Dropbox/website_text/ for offline revision.
#
#     tools/make_review_doc.sh              # -> ~/Dropbox/website_text/
#     OUTDIR=~/Desktop tools/make_review_doc.sh   # somewhere else

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTDIR="${OUTDIR:-${HOME}/Dropbox/website_text}"
WORK="$(mktemp -d)"
trap 'rm -rf "${WORK}"' EXIT

echo "Building ${ROOT} -> ${ROOT}/_site"
ruby "${ROOT}/tools/jekyll_build.rb" "${ROOT}" "${ROOT}/_site" >/dev/null

python3 "${ROOT}/tools/extract_site_text.py" "${ROOT}/_site" \
        "${WORK}/miguelzuma-site-text.html"

# A private LibreOffice profile so a running desktop instance doesn't block
# the headless conversion.
LO_PROFILE="file://${WORK}/lo-profile"
soffice -env:UserInstallation="${LO_PROFILE}" --headless \
        --convert-to 'odt:writer8' --outdir "${WORK}" \
        "${WORK}/miguelzuma-site-text.html" >/dev/null
soffice -env:UserInstallation="${LO_PROFILE}" --headless \
        --convert-to pdf --outdir "${WORK}" \
        "${WORK}/miguelzuma-site-text.html" >/dev/null

mkdir -p "${OUTDIR}"
cp "${WORK}/miguelzuma-site-text.odt" "${WORK}/miguelzuma-site-text.pdf" "${OUTDIR}/"
ls -l "${OUTDIR}/miguelzuma-site-text.odt" "${OUTDIR}/miguelzuma-site-text.pdf"
