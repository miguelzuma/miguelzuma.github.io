#!/usr/bin/env bash
# Build _cv/cv.tex into the PDF the website offers for download.
# Two passes, so hyperref's page references settle. Aux files stay in _cv/build.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out="$root/files/CV_Miguel_Zumalacarregui.pdf"
build="$root/_cv/build"

mkdir -p "$build"
for _ in 1 2; do
	pdflatex -interaction=nonstopmode -halt-on-error \
		-output-directory "$build" "$root/_cv/cv.tex" >/dev/null
done

cp "$build/cv.pdf" "$out"
echo "Built ${out#"$root"/} ($(du -h "$out" | cut -f1), $(pdfinfo "$out" 2>/dev/null | awk '/^Pages/{print $2" pages"}'))"
