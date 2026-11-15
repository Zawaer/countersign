"""Export the pitch deck (site/pitch.html) to docs/pitch/deck.pdf: 16:9, one slide per page, notes hidden, no footer.

Run after `python3 site/build.py`, with any Python that has Playwright and Chromium:
    python docs/pitch/export_pdf.py [out.pdf]
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs/pitch/deck.pdf"
W, H = 1280, 720

CSS = f"""
@page{{size:{W}px {H}px;margin:0}}
html,body{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.top,.deckbar,.foot,footer,.note,.skip{{display:none!important}}
main{{padding:0!important}}
.slide{{display:flex!important;flex-direction:column;justify-content:center;box-sizing:border-box;height:{H}px!important;
min-height:0!important;padding:56px 72px!important;overflow:hidden;break-after:page;position:relative}}
.slide:last-child{{break-after:auto}}
.sfoot{{display:none!important}}
.title-slide .urls,.title-slide .event{{display:none!important}}
"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": W, "height": H})
    page.goto((ROOT / "site/pitch.html").as_uri())
    page.evaluate("document.documentElement.dataset.theme='light'; document.body.classList.remove('notes')")
    page.emulate_media(media="screen")
    page.add_style_tag(content=CSS)
    page.pdf(path=str(OUT), width=f"{W}px", height=f"{H}px", print_background=True,
             margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
    n = page.locator(".slide").count()
    browser.close()
print(f"wrote {OUT} ({n} slides)")
