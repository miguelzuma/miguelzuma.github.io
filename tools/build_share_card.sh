#!/usr/bin/env bash
# Render tools/share-card.html to imgs/share-card.png at the Open Graph size.
# The PNG is committed: GitHub Pages serves files, it does not run a browser.
set -euo pipefail
cd "$(dirname "$0")/.."
google-chrome --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1200,630 --default-background-color=0a0c11ff \
  --screenshot=imgs/share-card.png "file://$PWD/tools/share-card.html"
echo "wrote imgs/share-card.png"
