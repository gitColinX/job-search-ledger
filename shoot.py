"""Screenshot each tab: python shoot.py <port> <filename prefix>"""
import sys
from playwright.sync_api import sync_playwright

port, prefix = sys.argv[1], sys.argv[2]
names = ["overview", "applications", "needs", "weekly"]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1500, "height": 1000})
    pg.goto(f"http://localhost:{port}")
    pg.wait_for_selector(".stat", timeout=30000)
    pg.wait_for_timeout(4000)
    for i, n in enumerate(names):
        if i:
            pg.get_by_role("tab").nth(i).click()
        pg.wait_for_timeout(3000)
        pg.screenshot(path=f"screenshots/{prefix}{i + 1}_{n}.png", full_page=True)
    b.close()
