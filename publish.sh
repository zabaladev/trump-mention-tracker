#!/usr/bin/env bash
# Daily routine: regenerate dashboard, then push ONLY the allow-listed public files to GitHub.
set -e; cd "$(dirname "$0")"; source /workspace/venv/bin/activate; python update.py
PUBLIC=(index.html data.json mentions.json disclosures.json exclusions.json congress.json sectors.json family_cos.json committees.json feed.xml feed.json feed-trump.xml feed-trump.json feed-family.xml feed-family.json feed-admin.xml feed-admin.json update.py template.html README.md publish.sh .gitignore)
# Safety guard: never publish anything from private/ (the unusual-timing watchlist is local-only).
for f in "${PUBLIC[@]}"; do case "$f" in private/*|*watchlist*) echo "REFUSING to publish $f"; exit 1;; esac; done
if grep -qi "watchlist" index.html data.json feed*.xml feed*.json; then echo "REFUSING: watchlist content found in public files"; exit 1; fi
echo "OK to push (allow-list): ${PUBLIC[*]}"
# Push via the GitHub connector (agent step): user-GitHub-xai push_files owner=zabaladev repo=trump-mention-tracker branch=main,
#   max 4 "$file:/workspace/trump-tracker/<name>" args per call, ONLY files from PUBLIC above. Never pass anything under private/.
# Pages workflow (.github/workflows/pages.yml) redeploys on push to main.
