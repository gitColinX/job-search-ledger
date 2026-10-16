"""One overview screenshot per theme: python shoot_themes.py <port>"""
import sys
import urllib.parse
from playwright.sync_api import sync_playwright

from themes import THEMES

port = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1500, "height": 1000})
    for name in THEMES:
        pg.goto(f"http://localhost:{port}/?theme={urllib.parse.quote(name)}")
        pg.wait_for_selector(".stat", timeout=30000)
        pg.wait_for_timeout(4500)
        slug = name.lower().replace(" ", "_")
        pg.screenshot(path=f"screenshots/theme_{slug}.png", full_page=True)
        print("saved", slug)
    b.close()
