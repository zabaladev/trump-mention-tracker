#!/usr/bin/env bash
# Daily routine: regenerate dashboard, then push ONLY the allow-listed public files to GitHub.
set -e; cd "$(dirname "$0")"; source /workspace/venv/bin/activate; python update.py
# Pre-publish checks (JSON/XML validity, mentions schema, private-content guard, page loads with no errors at 1280px/390px).
python check.py
# Screenshots of the PUBLIC dashboard only (PNG files in screens/). Refresh latest-*.png before pushing:
#   python shots.py   (writes screens/latest-desktop.png and screens/latest-mobile.png)
PUBLIC=(index.html data.json mentions.json disclosures.json exclusions.json congress.json sectors.json family_cos.json committees.json feed.xml feed.json feed-trump.xml feed-trump.json feed-family.xml feed-family.json feed-admin.xml feed-admin.json update.py template.html README.md publish.sh check.py .gitignore rankings.json rank.py shots.py .github/workflows/screens.yml screens/*.png)
# Safety guard: never publish anything from private/ (the unusual-timing watchlist is local-only).
for f in "${PUBLIC[@]}"; do case "$f" in private/*|*watchlist*) echo "REFUSING to publish $f"; exit 1;; screens/*) case "$f" in screens/*.png) ;; *) echo "REFUSING: screens/ may only hold PNG files ($f)"; exit 1;; esac;; esac; done
if grep -qi "watchlist" index.html data.json feed*.xml feed*.json; then echo "REFUSING: watchlist content found in public files"; exit 1; fi
echo "OK to push (allow-list): ${PUBLIC[*]}"
# Push via the GitHub connector (agent step): user-GitHub-xai push_files owner=zabaladev repo=trump-mention-tracker branch=main,
#   max 4 "$file:/workspace/trump-tracker/<name>" args per call, ONLY files from PUBLIC above. Never pass anything under private/.
# Screenshots: the connector only sends text, so push each screens/<name>.png as screens/<name>.png.b64
#   (base64 -w0 screens/<name>.png > /tmp/<name>.png.b64) and .github/workflows/screens.yml decodes it to PNG in the repo.
# Pages workflow (.github/workflows/pages.yml) redeploys on push to main.
