# Site critique (independent review, 2026-11-14)

Reviewed: index, attack, tour (all 8 steps, tamper + rehash + reset), pitch, packs/2234 at 390 and 1280 px, light and dark,
with Playwright. No console errors. No horizontal page scroll at 390 px on any page. Arrow keys move the tour.

Overall: the base is sound. It already looks like a developer tool (Primer palette, system fonts, mono for ids,
real data on the first screen, every number linked to a file, status always carries a word and glyph). No gradients,
glass, emoji or icon cards. The problems are about what a judge understands in the first few seconds, plus terms that
are never defined.

## 5-second test (before the fixes)

- 1280: a 4-line, 27-word H1 ("...under a mandate. It clears what it can prove, refuses what it can't, and a named human
  countersigns the rest"), then a lead with three separate statistics. A developer takes away "AI review plus human
  sign-off" and some numbers they can't place yet. The "whoa" (change 2234 is green in CI, an AI reviewer says
  every requirement is met, and it still fixes the wrong bug) starts at y≈470. Only the top of the red card shows.
- 390: the whoa is a full screen down. The first screen is headline plus number soup.
- "Mandate", the core concept, appears in the first line and is never defined anywhere on the page.

## Issues, ranked by impact on judges

1. **The whoa is not the first claim (Clarity).** The headline describes the mechanism, and the lead lists three
   numbers before the reader has any context for them. The single most persuasive fact, the 2234 catch, waits under an
   H2. *Fixed:* the H1 is now 2 lines ("AI review that clears only what it can prove. A named human signs for
   the rest."). The lead is the 2234 catch in one bold sentence, read from the pack (owner name included). The cards
   now start at y≈455 on desktop.
2. **Core jargon undefined (Clarity).** The pages never define *mandate*, *tier* or the four tier words
   (`SILENT/NOTIFY/ASK/BLOCK`, which appear as badges on every page), *escape*, *spot-check* or the `-mutN` ids.
   A Tieto engineer can't tell what ASK or BLOCK commits a human to. *Fixed:* a one-line mandate definition under
   the lead, and a tier legend (wording taken from README/PRINCIPLES) under the story cards, above the attack-page
   table and under the tour's area table. "Escape" and "spot-check" are now defined inline. The id scheme is
   explained on the attack page ("2234-mut2 = change 2234, seeded bug 2"). "Original" became "Tier without the bug".
3. **"0 of 4" reads as "the tool does nothing" (Practicality/Measurement).** It is the first big number, and the
   reason (a repo with no track record starts strict) was three sections further down. *Fixed:* the reason is now in
   the stat's own caption.
4. **Stale or missing trust-rule text (Evidence).** The mandate's `trust` block is being changed to staged trust
   (ask → notify → silent). The old `escape_cap` / `restore_after_agreeing_spotchecks` keys are gone, so the index
   and tour step 7 would have rendered "until ? spot-checks". *Fixed:* `trust_rule()` reads whichever form the
   mandate has (it currently renders "Climbing back to notify takes 20 agreeing spot-checks in a row").
5. **Accessibility and mobile polish.** (a) The keyboard focus ring on nav links was clipped by the nav's
   `overflow-x:auto`, so only a 2 px sliver showed. *Fixed* with an inset outline. (b) At 390 the nav cut off "Pitch"
   and hid "Evidence pack" with no scroll cue. *Fixed:* it wraps onto two lines. (c) The 390 bug picker showed bare
   ids (`2234-mut4`) and hid the kind. *Fixed:* the kind is back, left-aligned. (d) In stacked tables at 390,
   numeric cells were right-aligned away from their label. *Fixed.*

## Left as is / not fixed (lower impact)

- **Equal-height story cards leave big empty areas** in cards 1 and 2 at 1280 (card 3 carries the citations). It's
  honest and readable. Making it compact would mean dropping evidence from card 3.
- **The tour step 4 reviewer quote is a 13-line wall of text** (raw finding text from the pack). It's authentic, but a
  two-sentence summary with the full text in a `<details>` would read faster. That needs a summary written in the
  pack, not on the site.
- **Tour step labels truncate at 1280** ("The facts, before any …"). The full title is in `title=` and in the H1.
- **Stat captions mix measures:** "11 of 14 failed a check" next to "12 of 14 reach a human". Both are correct and
  explained, but a judge has to read carefully. A small table (caught by checks / routed to human / got through)
  would be clearer.
- **Long deciding-reason strings** in the "All four changes" table ("Risk score 145.2 reaches the block band
  (>= 130), mostly 2 failed check(s) x 25: ... solution_membership") are engine output and contain internal check
  names. They come from pack.json and are left verbatim on purpose.
- **Contrast:** the Primer tokens pass. Muted #59636e on white is about 6.1:1, dark muted #9198a1 on #0d1117 about
  6.9:1, and warn #9a6700 on #fff8c5 about 4.6:1, close to the 4.5:1 floor. No change needed.
- **Pitch page:** the title slide still uses the long mechanism sentence (it comes from docs/pitch/deck.md, outside
  site/). It's fine for a spoken pitch.
- **AI-smell check:** none found. Copy is plain and specific. The one pattern to watch is the repeated
  "X of Y" bold numbers in every paragraph, which can read as stat-stuffing. The hero no longer does it.
