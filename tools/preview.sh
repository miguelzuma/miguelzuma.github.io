#!/usr/bin/env bash
# Build the site with Jekyll and serve it at http://127.0.0.1:4000
#
# Works around a local toolchain limitation: this machine has Ruby but no
# development headers, so gems with native extensions (eventmachine,
# http_parser.rb) cannot compile. Those are only needed by `jekyll serve
# --livereload`, never by `jekyll build` — but RubyGems activates them anyway
# when you run the `jekyll` binary. tools/jekyll_build.rb loads Jekyll directly
# and skips that activation, and we serve the output with Python instead.
#
# If you ever install the headers (`sudo apt install ruby-dev build-essential`),
# `bundle install && bundle exec jekyll serve` works normally and this script
# becomes unnecessary.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${ROOT}/_site"
PORT="${PORT:-4000}"

echo "Building ${ROOT} -> ${DEST}"
ruby "${ROOT}/tools/jekyll_build.rb" "${ROOT}" "${DEST}"

echo
echo "Serving at http://127.0.0.1:${PORT}  (Ctrl-C to stop)"
cd "${DEST}"
exec python3 -m http.server "${PORT}" --bind 127.0.0.1
