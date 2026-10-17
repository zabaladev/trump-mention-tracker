#!/usr/bin/env python3
"""Pre-publish checks for the tracker (backlog #16).

Run: python check.py            -> checks the local index.html
     python check.py --live     -> also loads the live GitHub Pages site
Exits non-zero if anything fails, so publish.sh stops before pushing.

Checks:
 1. Every public JSON file parses; every feed XML parses.
 2. mentions.json has the required fields, valid dates/groups, and an http(s) source.
 3. No private content: nothing from private/ is in the allow-list, and no public file
    contains the word "watchlist" or any ticker+note text that only exists in private/.
 4. The dashboard loads in headless Chromium at 1280px and 390px wide with no page
    errors or console errors, and the key sections render text.
"""
import json, re, sys, pathlib, datetime, xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent
LIVE = "https://zabaladev.github.io/trump-mention-tracker/"
JSON_FILES = ["data.json", "mentions.json", "disclosures.json", "exclusions.json", "congress.json",
              "sectors.json", "family_cos.json", "committees.json", "rankings.json",
              "feed.json", "feed-trump.json", "feed-family.json", "feed-admin.json"]
XML_FILES = ["feed.xml", "feed-trump.xml", "feed-family.xml", "feed-admin.xml"]
TEXT_FILES = ["index.html", "template.html", "README.md"] + JSON_FILES + XML_FILES
REQ = ["date", "who", "asset", "ticker", "type", "category", "quote", "source", "group"]
GROUPS = {"Trump", "Family", "Admin"}
fails = []

def fail(msg):
    fails.append(msg); print("FAIL:", msg)

def check_files():
    for f in JSON_FILES:
        try: json.loads((ROOT / f).read_text())
        except Exception as e: fail(f"{f} is not valid JSON ({e})")
    for f in XML_FILES:
        try: ET.parse(ROOT / f)
        except Exception as e: fail(f"{f} is not valid XML ({e})")

def check_mentions():
    try: m = json.loads((ROOT / "mentions.json").read_text())
    except Exception: return
    for i, r in enumerate(m):
        tag = f"mentions.json row {i} ({r.get('ticker')} {r.get('date')})"
        miss = [k for k in REQ if not str(r.get(k, "")).strip()]
        if miss: fail(f"{tag} missing {miss}")
        try: datetime.date.fromisoformat(str(r.get("date")))
        except Exception: fail(f"{tag} has a bad date")
        if r.get("group") not in GROUPS: fail(f"{tag} has unknown group {r.get('group')!r}")
        for k in ("source", "orig_url", "archive_url"):
            if k in r and not str(r[k]).startswith(("http://", "https://")): fail(f"{tag} {k} is not a link")
    print(f"mentions.json: {len(m)} rows checked")

def private_markers():
    """Distinctive strings that exist only in the private watchlist."""
    out = set()
    for p in list((ROOT / "private").glob("*.json")) + [ROOT.parent / "watchlist.json"]:
        try: data = json.loads(p.read_text())
        except Exception: continue
        def walk(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if k.lower() in ("what", "status", "why", "reason", "note", "notes", "rationale") and isinstance(v, str) and len(v) >= 40:
                        out.add(v[:60])
                    walk(v)
            elif isinstance(x, list):
                for v in x: walk(v)
        walk(data)
    return out

def check_private():
    pub = re.search(r"PUBLIC=\(([^)]*)\)", (ROOT / "publish.sh").read_text())
    names = pub.group(1).split() if pub else []
    if not names: fail("could not read the PUBLIC allow-list in publish.sh")
    for n in names:
        if n.startswith("private") or "watchlist" in n.lower(): fail(f"allow-list includes private file {n}")
    marks = private_markers()
    for f in TEXT_FILES:
        t = (ROOT / f).read_text(errors="ignore")
        if re.search(r"watchlist", t, re.I): fail(f"{f} mentions the private watchlist")
        for s in marks:
            if s in t: fail(f"{f} contains text from the private watchlist: {s[:30]}…")
    print(f"private guard: {len(names)} allow-listed files, {len(marks)} private text markers checked")

def check_page(url, label):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w in (1280, 390):
            pg = b.new_page(viewport={"width": w, "height": 900})
            errs = []
            pg.on("pageerror", lambda e: errs.append("page error: " + str(e)))
            pg.on("console", lambda c: errs.append("console: " + c.text) if c.type == "error" else None)
            r = pg.goto(url, wait_until="load")
            if r is not None and r.status >= 400: fail(f"{label} {w}px returned HTTP {r.status}")
            pg.wait_for_timeout(2500)
            for e in errs: fail(f"{label} {w}px {e}")
            for sel in ("#gen", "#takeP"):
                try: txt = pg.inner_text(sel, timeout=3000).strip()
                except Exception: txt = ""
                if len(txt) < 10: fail(f"{label} {w}px: {sel} is empty")
            k0 = len(errs)
            # design system v2: six tabs; each must open without errors
            tabs = pg.evaluate("[...document.querySelectorAll('#tabs a')].map(a=>a.dataset.tab)")
            if len(tabs) < 6: fail(f"{label} {w}px: expected 6 tabs, found {tabs}")
            for t in tabs:
                pg.evaluate(f"showTab('{t}')"); pg.wait_for_timeout(300)
                if not pg.evaluate(f"document.getElementById('pane-{t}').offsetHeight>0"): fail(f"{label} {w}px: tab {t} is empty")
            if not pg.evaluate("!!(D.rank&&D.rank.members&&D.rank.members.length)"): fail(f"{label} {w}px: rankings data missing")
            if len(pg.inner_text('#rkSum').strip()) < 20: fail(f"{label} {w}px: rankings summary is empty")
            for e in errs[k0:]: fail(f"{label} {w}px (while switching tabs) {e}")
            pg.evaluate("showTab('overview')"); pg.wait_for_timeout(200)
            n = pg.evaluate("document.querySelectorAll('canvas').length")
            if n < 3: fail(f"{label} {w}px: only {n} charts drawn")
            print(f"{label} {w}px: loaded, {len(errs)} errors, {n} charts")
            pg.close()
        b.close()

if __name__ == "__main__":
    check_files(); check_mentions(); check_private()
    check_page((ROOT / "index.html").as_uri(), "local")
    if "--live" in sys.argv: check_page(LIVE, "live")
    if fails: print(f"\n{len(fails)} check(s) failed."); sys.exit(1)
    print("\nAll checks passed.")
