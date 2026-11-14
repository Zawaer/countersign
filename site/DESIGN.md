# Site design rules

Audience: engineers and engineering leads (Tieto, Junction peer reviewers, jurors). It should read like a developer tool's own docs (GitHub's Primer, Stripe docs, Sigstore provenance pages): calm, dense, real data. Sources: Primer color and typography foundations (semantic roles, ~80ch lines, left-aligned text, never colour alone), WCAG 2.2 SC 1.4.3 / 1.4.11 (contrast).

1. Neutral canvas, one accent (blue: links, focus, the current step). Green, amber and red mean status only: pass, ask, fail/block.
2. Status is never colour alone: every status carries a word and a glyph (`PASS ✓`, `FAIL ✗`, `ASK`, `BLOCK`).
3. System font stack for text; `ui-monospace` for ids, hashes, file:line, commands and code.
4. Type scale 12 / 14 / 16 / 20 / 24 / 32 px; body 16px at line-height 1.5, headings 1.25. Weight 400 and 600 only.
5. Spacing on an 8px grid (4px allowed inside dense rows). Radius 6px, 1px borders, no shadows, gradients, blur or glow.
6. Text columns max ~70ch, left-aligned, ragged right. No centred hero; the first screen shows real data.
7. Every number on the page is read from a repo file by `site/build.py` at build time and links to that file. Nothing typed by hand; missing data shows as "not recorded yet".
8. Contrast: body text at least 4.5:1, borders of controls and large text at least 3:1, in light and dark. Visible focus ring.
9. Tables: dense rows, muted header, tabular numerals, numbers right-aligned; on a 390px phone they scroll inside their own box, the page never scrolls sideways.
10. Copy: plain verbs, short sentences, no hype words or emoji; say "simulated" or "estimate" wherever it applies.
