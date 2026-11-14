# v3: one story, one action (wins over v2)

1. The first screen is the story of change 2234 in big type, no code: an AI agent wrote this fix; three green checks; then (CSS fade) "It fixes the wrong bug."; then who must decide and two buttons. About 30 words.
2. "Show me where" is one hunk (at most 12 lines), one pin, one sentence, one small link to the evidence pack.
3. "Try to sneak a bug in" is three cards and one big result each, with the planted line.
4. Depth is one small "More" link (more.html). Numbers: three huge numbers, captions of at most 8 words. Tour: at most 6 steps, one sentence and one visual each.
5. Pack first screen: verdict pill, the change, "Why:" (at most 12 words), three marks (checks, reviewers, signature from the ledger); everything else behind one Evidence fold.
6. Every line still comes from a record (site/scene.py); no JavaScript needed on the first screen; light by default; status is glyph + words.

# v2: the code is the scene

1. The landing page is one scene: the real diff of the agent-written change, full viewport, calm monospace, subtle syntax colour. No hero, no paragraphs, no tables, no number tiles, no side panels.
2. On it, 3 to 5 pins sit at the end of the exact lines they are about (error-lens style): a status glyph and 2-5 words. `✗` problem, `◐` weak evidence, `✓` proven, `?` refused / not checked.
3. One verdict pill on top: tier → named owner, plus 3-6 words. One muted line above it: the issue title.
4. Tap a pin (or the pill): a small card under the line with one sentence, who agreed or disagreed (tiny chips), the evidence (cited line, test and run), the source file, and a link into the full evidence pack. Nothing else.
5. One bar at the bottom switches the scene: 2234 · 2283 · 2129 · 2297 · up-1967 · sneak a bug in (pick a seeded bug; its pin says whether the checks caught it).
6. Unpinned code folds into one-line `⋯ +12 −4` rows that open on tap; files without pins collapse into one "+N files" row.
7. Under 40 words of prose on the first screen. Depth (tour, pitch, attack, overview numbers, packs) is one tap away, small, top right.
8. Every pin, sentence and verdict is resolved by `site/scene.py` from pack.json / facts.json / results.json at build time; the short labels are the only editorial text and each names the record it summarises. A pin whose source record is missing is dropped, not invented.
9. Same tokens as v1 (Primer neutrals, one blue accent, green/amber/red for status only, glyph + word, 4.5:1 contrast), light default, dark supported. 390 px phone and projector both first-class.
10. Before shipping any change to the scene, ask "what can I remove?".

# v1 rules (secondary pages; v2 wins where they conflict)


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
