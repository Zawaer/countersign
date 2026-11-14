# site/: the judge-facing pages

Static, self-contained (no CDN, no build tools): `index.html` (overview and the 2234 story), `attack.html` (pick a seeded bug and see what caught it; real escapes from MessagePack's history), `tour.html` (8-step walkthrough, with an in-browser ledger tamper check), `pitch.html` (the deck from `docs/pitch/deck.md`, arrow keys or swipe; N for notes, F for full screen), and `packs/` (copies of `packs/*/pack.html`).

Every page is generated, so numbers stay in sync with the repo:

```bash
python3 site/build.py                                        # stdlib only; reads measurement/, evidence/, reviews/, packs/, ledger/, mandate/, docs/pitch/
python3 -m http.server 3472 --bind 0.0.0.0 --directory site  # then open http://localhost:3472/
```

Rerun `build.py` after anything under those folders changes. Missing inputs show as "not recorded yet", never as a made-up number. Design rules: [DESIGN.md](DESIGN.md).

**Publishing.** `.github/workflows/pages.yml` rebuilds and publishes `site/` to GitHub Pages on every push to `main` that touches its inputs. It only works once the repository is public (planned for Sunday, by Toivo) and Pages is set to "GitHub Actions" in the repo settings; until then the deploy step fails and the preview at http://localhost:3472/ is the live copy.
