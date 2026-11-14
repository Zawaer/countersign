#!/usr/bin/env python3
"""Regenerate the README screenshots in docs/img/ from the built site.

Needs Playwright (with Chromium) and Pillow:
    pip install playwright pillow && python -m playwright install chromium

Usage:
    python3 site/build.py
    python3 scripts/screenshots.py            # serves site/ itself on a free port
    python3 scripts/screenshots.py --url http://localhost:3472

Shots are 1280x800 at device scale 2, light theme, then palette-quantised
so each PNG stays well under 300 KB.
"""
import argparse
import functools
import http.server
import io
import pathlib
import threading

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "img"
MAX_BYTES = 300 * 1024


def serve_site():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / "site"))
    handler.log_message = lambda *a: None
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


def save(png_bytes, name):
    img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    for colors in (256, 128, 64):
        buf = io.BytesIO()
        img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(
            buf, "PNG", optimize=True)
        if buf.tell() <= MAX_BYTES:
            break
    path = OUT / name
    path.write_bytes(buf.getvalue())
    print(f"{path.relative_to(ROOT)}  {buf.tell() // 1024} KB  ({colors} colours)")


def shoot(page, base, path, name, action=None):
    page.goto(f"{base}/{path}")
    page.wait_for_load_state("networkidle")
    if action:
        action(page)
    page.wait_for_timeout(400)
    save(page.screenshot(), name)


def after_fade(page):
    page.wait_for_timeout(4500)  # the first screen reveals "It fixes the wrong bug." with a CSS fade


def tamper(page):
    page.click("#tamper")
    page.wait_for_function("document.querySelector('#lstatus').textContent.trim().length > 0")
    page.locator("#lstatus").scroll_into_view_if_needed()
    page.evaluate("window.scrollBy(0, -200)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", help="base URL of a running site server (default: serve site/ here)")
    args = ap.parse_args()
    httpd = None
    base = args.url
    if not base:
        httpd, base = serve_site()
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=2,
                                  color_scheme="light")
        ctx.add_init_script("try{localStorage.setItem('cs-theme','light')}catch(_){}")
        page = ctx.new_page()
        shoot(page, base, "index.html", "scene.png", after_fade)
        shoot(page, base, "prs.html", "pr.png")
        shoot(page, base, "tour.html#6", "ledger-tamper.png", tamper)
        shoot(page, base, "overview.html", "overview.png")
        browser.close()
    if httpd:
        httpd.shutdown()


if __name__ == "__main__":
    main()
