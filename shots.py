#!/usr/bin/env python3
"""Screenshots of the PUBLIC dashboard (index.html) for screens/: desktop 1280x800 and mobile 390x844.
Usage: python shots.py [prefix]   -> screens/<prefix>-desktop.png, screens/<prefix>-mobile.png (default prefix: latest)
Only the public page is captured; never point this at anything in private/."""
import sys, pathlib
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent; pre = sys.argv[1] if len(sys.argv) > 1 else 'latest'
(ROOT / 'screens').mkdir(exist_ok=True); url = (ROOT / 'index.html').as_uri()
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vp, kw in (('desktop', {'width': 1280, 'height': 800}, {}), ('mobile', {'width': 390, 'height': 844}, {'is_mobile': True, 'has_touch': True, 'device_scale_factor': 2})):
        pg = b.new_page(viewport=vp, color_scheme='light', **kw); pg.goto(url); pg.wait_for_timeout(2500)
        pg.screenshot(path=str(ROOT / 'screens' / f'{pre}-{name}.png')); pg.close()
    b.close()
print('saved', pre)
