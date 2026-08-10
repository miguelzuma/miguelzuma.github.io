#!/usr/bin/env bash
# Build the downloadable CV, files/CV_Miguel_Zumalacarregui.pdf.
#
# The LaTeX is generated: cv.tex is a Jekyll template over _data/cv.yml and
# _data/people.yml, so the site build has to run first. Two pdflatex passes,
# so hyperref's references settle. Aux files stay in _cv/build.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out="$root/files/CV_Miguel_Zumalacarregui.pdf"
build="$root/_cv/build"

ruby "$root/tools/jekyll_build.rb" "$root" "$root/_site" >/dev/null

mkdir -p "$build"
for _ in 1 2; do
	pdflatex -interaction=nonstopmode -halt-on-error \
		-output-directory "$build" "$root/_site/cv.tex" >/dev/null \
		|| { echo "pdflatex failed; see $build/cv.log" >&2; exit 1; }
done

cp "$build/cv.pdf" "$out"
echo "Built ${out#"$root"/} ($(du -h "$out" | cut -f1), $(pdfinfo "$out" 2>/dev/null | awk '/^Pages/{print $2" pages"}'))"
