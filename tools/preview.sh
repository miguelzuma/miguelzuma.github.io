#!/usr/bin/env bash
# Build the site with Jekyll and serve it at http://127.0.0.1:8794
#
#     tools/preview.sh                # build + serve on port 8794
#     PORT=4000 tools/preview.sh     # another port
#     BIND=127.0.0.1 tools/preview.sh  # this machine only (default is
#                                      # 0.0.0.0, reachable from a phone
#                                      # on the same network)
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
PORT="${PORT:-8794}"
BIND="${BIND:-0.0.0.0}"

echo "Building ${ROOT} -> ${DEST}"
ruby "${ROOT}/tools/jekyll_build.rb" "${ROOT}" "${DEST}"

echo
echo "Serving at http://127.0.0.1:${PORT}  (Ctrl-C to stop)"
if [ "${BIND}" = "0.0.0.0" ]; then
  ip="$(hostname -I 2>/dev/null | awk '{print $1}')"
  [ -n "${ip}" ] && echo "From a phone on this network: http://${ip}:${PORT}"
fi
cd "${DEST}"
exec python3 -m http.server "${PORT}" --bind "${BIND}"
