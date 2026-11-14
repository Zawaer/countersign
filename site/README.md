# site/: the judge-facing pages

Static, self-contained (no CDN, no build tools): `index.html` (the main screen: the real diff with a few pins; its "sneak a bug in" mode shows each seeded bug, whether a check caught it and whether a reviewer flagged the line), `overview.html` (the numbers: three on the first screen, the rows below), `tour.html` (8 steps, one visual each, with an in-browser ledger tamper check), `pitch.html` (8 slides, one message each; arrow keys or swipe, N for speaker notes, F for full screen), `attack.html` (a redirect into the main screen's sneak-a-bug mode, kept for old links) and `packs/` (copies of `packs/*/pack.html`).

Every page is generated, so numbers stay in sync with the repo:

```bash
python3 site/build.py                                        # stdlib only; reads measurement/, evidence/, reviews/, packs/, ledger/, mandate/, docs/pitch/
python3 -m http.server 3472 --bind 0.0.0.0 --directory site  # then open http://localhost:3472/
```

Rerun `build.py` after anything under those folders changes. The README screenshots in `docs/img/` come from these pages: rerun `python3 scripts/screenshots.py` (Playwright + Pillow; serves `site/` itself, light theme, 1280x800 at 2x) after a page changes. Missing inputs show as "not recorded yet", never as a made-up number. Design rules: [DESIGN.md](DESIGN.md).

**Publishing.** `.github/workflows/pages.yml` rebuilds and publishes `site/` to GitHub Pages on every push to `main` that touches its inputs. It only works once the repository is public (planned for Sunday, by Toivo) and Pages is set to "GitHub Actions" in the repo settings; until then the deploy step fails and the preview at http://localhost:3472/ is the live copy.
