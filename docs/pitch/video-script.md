# Demo video script (target 1:55, hard limit 2:00)

One take of the real site, no mock-ups. Record the voice-over first (about 190 words, calm pace), then cut the screen capture to it. Captions are burned in, bottom-left, at most 6 words each.

All URLs are relative to the site root: GitHub Pages once public, or locally `python3 -m http.server 3472 -d site` → `http://localhost:3472/`.

## Shot list

| Time | On screen (page, click) | Caption | Voice-over |
|---|---|---|---|
| 0:00–0:10 | `pitch.html#4`: slide "Green CI. AI says met. Wrong bug." Cursor rests on the CI tile (✓ 175/175), then the AI review tile (✓ 4/4 met). | Everything is green | An agent opens a pull request. The build passes, all 175 tests pass, and an AI reviewer says every requirement is met. |
| 0:10–0:15 | Switch tab to `index.html#2234`: the real diff, four pins, verdict pill on top. No click. | The code, with pins | Countersign shows the code itself, with a few pins. |
| 0:15–0:27 | Click pin **✗ Fixes a different crash** (line 1383). Its card opens under the line. | It fixes a different bug | This one: the reported crash comes from a commit that isn't in this branch. The agent fixed a different bug. |
| 0:27–0:38 | Click pin **✗ Still crashes on Key(null) · reproduced** (line 985). Hold on the chips "Claude found it" and "pipeline reproduced it". | Still crashes. Reproduced. | This line still crashes on Key null. A reviewer claimed it; the pipeline reproduced it. |
| 0:38–0:47 | Scroll a little; click pin **◐ Passes without the fix** (test line 21). | Tests pass without the fix | Revert the fix, and four of the eight new tests still pass. They prove nothing. |
| 0:47–0:53 | Scroll to top; hover the pill **ASK → Toivo**. | ASK → Toivo | So the AI can't clear it. It asks the named owner, Toivo. |
| 0:53–1:08 | Switch tab to `tour.html#6` ("Try to forge the record"). Hover **LINE 7 signoff by Toivo**. Click **1. Tamper** → red "LEDGER INVALID … does not match its hash". Click **2. Recompute the hash** → "signature does not verify". | Edit one line: invalid | Toivo requests changes and signs into a hash-chained ledger. Edit one line: invalid. Recompute the hash: still invalid. Only his key signs. |
| 1:08–1:24 | Back to the `index.html` tab. Bottom bar: click **sneak a bug in**, then **removed guard 2234·2**. Pins: **◐ Got past every check**, **✗ Claude flagged it**; pill **ASK → Toivo · checks missed it; Claude flagged it**. | Every test missed it | Now sneak a bug in: delete one line. Every test passes. A reviewer still points at that line, so it goes to Toivo. |
| 1:24–1:42 | Switch tab to `overview.html`: the three numbers. Hold on the first one (<!--n:history_cleared-->24<!--/n-->/<!--n:history_prs-->109<!--/n--> cleared, <!--n:history_escapes_cleared-->0<!--/n--> of <!--n:history_escapes-->11<!--/n--> escapes), then the red-team tile. | <!--n:history_escapes_cleared-->0<!--/n--> of <!--n:history_escapes-->11<!--/n--> escapes cleared · then: Red team: <!--n:redteam_stopped-->35<!--/n--> of <!--n:redteam_total-->35<!--/n--> stopped | Replayed on <!--n:history_prs-->109<!--/n--> real merged pull requests, the AI would have cleared <!--n:history_cleared-->24<!--/n-->, and none of the <!--n:history_escapes-->11<!--/n--> that later needed a revert or fix. We attacked our own pipeline <!--n:redteam_total-->35<!--/n--> ways; it stops all <!--n:redteam_stopped-->35<!--/n-->. |
| 1:42–1:55 | Switch tab to `pitch.html#1`: title slide with the punchline and the repo URL. Hold to the end. | (none: the slide says it) | Countersign. AI clears what it can prove, refuses what it can't, and a named human countersigns the rest. |

## Voice-over (read straight through, 192 words)

> An agent opens a pull request. The build passes, all 175 tests pass, and an AI reviewer says every requirement is met.
>
> Countersign shows the code itself, with a few pins.
>
> This one: the reported crash comes from a commit that isn't in this branch. The agent fixed a different bug.
>
> This line still crashes on Key null. A reviewer claimed it; the pipeline reproduced it.
>
> Revert the fix, and four of the eight new tests still pass. They prove nothing.
>
> So the AI can't clear it. It asks the named owner, Toivo.
>
> Toivo requests changes and signs into a hash-chained ledger. Edit one line: invalid. Recompute the hash: still invalid. Only his key signs.
>
> Now sneak a bug in: delete one line. Every test passes. A reviewer still points at that line, so it goes to Toivo.
>
> Replayed on <!--n:history_prs-->109<!--/n--> real merged pull requests, the AI would have cleared <!--n:history_cleared-->24<!--/n-->, and none of the <!--n:history_escapes-->11<!--/n--> that later needed a revert or fix. We attacked our own pipeline <!--n:redteam_total-->35<!--/n--> ways; it stops all <!--n:redteam_stopped-->35<!--/n-->.
>
> Countersign. AI clears what it can prove, refuses what it can't, and a named human countersigns the rest.

## Numbers used

| Number | Where it is said | Source |
|---|---|---|
| <!--n:t2234_suite_passed-->175<!--/n--> of <!--n:t2234_suite_total-->175<!--/n--> tests pass | 0:00 | `evidence/2234/facts.json`, check `tests.full_suite` ("175 tests, 175 passed"); also pitch slide 4 |
| AI reviewer: every requirement met (4 of 4) | 0:00 | `reviews/2234/codex.json`, `requirement_verdicts` (pitch slide 4, "AI review ✓ 4/4 met") |
| Fixes a different crash (commit not in the branch) | 0:15 | `packs/2234/pack.json`, finding `claude:C1` (upstream `1a74a620` not in base) |
| Key(null) still crashes, reproduced | 0:27 | `packs/2234/pack.json`, finding `claude:C2` and check `repro.claude.C2` (fails on head and base, passes on control) |
| <!--n:t2234_pass_without_fix-->4<!--/n--> of <!--n:t2234_new_tests-->8<!--/n--> new tests pass without the fix | 0:38 | `evidence/2234/facts.json`, check `tests.fail_without_fix` ("4/8 failed … 4 new tests pass without the fix") |
| ASK → Toivo | 0:47 | `packs/2234/pack.json` (`tier`, `owner`) |
| Toivo's request-changes sign-off | 0:53 | `ledger/ledger.jsonl` line 7 (signoff, change 2234, decision request-changes) |
| Tamper → invalid; rehash → signature fails | 0:53 | live check in `tour.html` step 6 against `ledger/ledger.jsonl` and `keys/toivo.pub` |
| Seeded bug every test missed, reviewer on the line | 1:08 | `measurement/results.md`, row `2234-mut2` (tests missed it: yes; tier ask; claude N1, nemotron M1 on the planted line ±3) |
| <!--n:history_prs-->109<!--/n--> PRs, <!--n:history_cleared-->24<!--/n--> cleared, <!--n:history_escapes_cleared-->0<!--/n--> of <!--n:history_escapes-->11<!--/n--> escapes | 1:24 | `measurement/history/results.md` (mandate v<!--n:history_mandate-->6<!--/n-->); README "In numbers" |
| Red team: <!--n:redteam_total-->35<!--/n--> attacks, <!--n:redteam_stopped-->35<!--/n--> stopped | 1:24 | README "Red team"; `docs/security/REDTEAM.md`; `tests/redteam/test_redteam_attacks.py` (`KNOWN_MISSES` empty; `scripts/sync_numbers.py` key `redteam_stopped`) |
| On screen only: <!--n:seeded_caught_by_checks-->14<!--/n--> of <!--n:seeded_total-->18<!--/n--> seeded changes failed a check | 1:24 | `measurement/results.json` via `overview.html` |

## Recording checklist

- **Window:** browser content area exactly 1280×800 (record the window, not the screen). On a Retina Mac this records at 2560×1600; export 1080p or 1440p.
- **Zoom:** 100%. The 2234 scene and its pins fit one screen at 100%; at 110% the test pins fall below the fold.
- **Theme:** light (the default; click ◐ top right if the OS is in dark mode). Check every tab is light before rolling.
- **Clean browser:** a fresh profile or guest window, no bookmarks bar, no extensions, notifications off (macOS Focus on). Hide the dock.
- **Pre-open tabs, in order:** `pitch.html#4`, `index.html#2234`, `tour.html#6`, `overview.html`, `pitch.html#1`. Load each once, so nothing renders mid-shot. Reset tour step 6 (**Reset**) before the take.
- **Cursor:** turn on a cursor highlight in the recorder (QuickTime: "Show Mouse Clicks"). Move slowly; rest the cursor on each pin for a beat before clicking.
- **Timing:** record the voice-over first, then click to it. Hold every number on screen at least 2 seconds. Leave 5 seconds of slack under 2:00: the target is 1:55.
- **If it runs long:** shorten the overview hold (1:24) first; keep the "still crashes" and "sneak a bug in" shots, they are the story.
- **Audio:** a headset or lavalier, a quiet room, one take per paragraph, normalised to -16 LUFS.
- **Captions:** burned in, bottom-left, white on a dark 80%-opacity box, same font as the site (system sans), up 2+ seconds each.

## 30-second cut

| Time | On screen | Caption | Voice-over |
|---|---|---|---|
| 0:00–0:05 | `pitch.html#4` (green tiles) | Everything is green | An agent's pull request. Every test passes. |
| 0:05–0:16 | `index.html#2234`: click **✗ Fixes a different crash**, then **✗ Still crashes on Key(null)** | Wrong bug. Still crashes. | Countersign shows the code: it fixes a different bug, it still crashes, and half its new tests prove nothing. |
| 0:16–0:21 | Hover **ASK → Toivo** | ASK → Toivo | So it asks the named owner, Toivo, who signs. |
| 0:21–0:26 | `overview.html`, middle number | 0 of 11 escapes cleared | On 109 real pull requests, it would have cleared 24, and none of the 11 escapes. |
| 0:26–0:30 | `pitch.html#1` | (none) | AI clears what it can prove. A named human signs the rest. |

## Rendering the video (scripts/video/)

The video is rendered, not filmed: `scripts/video/make_video.py` drives the real `site/` in headless Chromium (1280×720 CSS at device scale 1.5, captured as 1920×1080 frames through the DevTools screencast), moves a visible cursor dot and clicks on the voice-over's words, then burns in the captions with ffmpeg. Nothing on screen is generated.

```bash
python3 site/build.py
uv run --with playwright python -m playwright install chromium --with-deps   # once
uv run --with playwright python scripts/video/make_video.py            # ElevenLabs voice
uv run --with playwright python scripts/video/make_video.py --silent   # silent placeholder voice, same pipeline
```

- **Input:** the voice-over paragraphs and captions are read from this file (number markers stripped), one paragraph per shot. `SHOT_OVERRIDES` in the script lists where the video departs from the table.
- **Voice:** ElevenLabs `eleven_multilingual_v2`, voice "George" (`JBFqnCBsd6RMkjVDRZzb`), one clip per shot via the `with-timestamps` endpoint. The key is read from `/data/work/secrets/elevenlabs.key` inside the script and never printed. Clips are cached in `/data/work/video/audio/`, keyed by a hash of the text, voice and settings: re-renders spend no characters unless a paragraph changes.
- **Timing:** each shot lasts a short lead-in + its clip + a short tail; clicks (Tamper, Recompute, sneak a bug in) are timed to the words that describe them using the character timestamps.
- **Output:** `/data/work/video/countersign-demo.mp4` (H.264/AAC, yuv420p, faststart, -16 LUFS) and `contact-sheet.png`; the frames, captions and `timeline.json` (each shot's midpoint, for spot checks) are in `/data/work/video/build/`. Neither the video nor any audio is committed.
- **Where the video departs from the table above** (the site was redesigned after this script was written; the facts are the same):
  - 0:10: `index.html` has no pins any more; the shot shows its first screen ("It fixes the wrong bug." fades in), says "Countersign checks the evidence itself, and says no: it fixes the wrong bug." and clicks **Show me where**.
  - 0:15: the single pin **Untouched by the fix** on line 1383 (`index.html#where`).
  - 0:27: Key(null) is Claude's finding C2 in the evidence pack (`packs/2234/pack.html`, Evidence open), "reproduced by the pipeline (repro.claude.C2)".
  - 0:38 and 0:47: `tour.html#2` (4 of 8 tests pass without the fix) and `tour.html#5` (the **ASK → Toivo** pill).
  - 0:53: as scripted; the tamper edits the newest ledger line (line 14), so the banner names line 14.
  - 1:08: **Try to sneak a bug in** → **Delete a guard** → "Caught by a reviewer (tests missed it)."
  - 1:24: `overview.html` now leads with 11/11 later-reverted PRs sent to a human, then the 35/35 tile.
