# Deck outline (9 slides)

One message per slide. Visuals are captures of real artifacts unless marked "diagram". Speaker notes are what to say if the deck is presented live; the PDF can carry them as small text or leave them out.

---

## 1. Title

- **Message:** Countersign. AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it can't, and a named human countersigns the rest.
- **Visual:** the punchline on a plain background; small line: "Junction 2026 · Tieto: Earned Trust in AI Code · github.com/Zawaer/countersign".
- **Speaker note:** We are not proposing a better AI reviewer. We are proposing a way to delegate review authority to AI that a named person can still sign for.

## 2. The question is wrong

- **Message:** Stop asking "did a human read every line?" Ask "did a named human sign for what was proven, what was refused, and the risk that is left?"
- **Visual:** left, a 262-line diff (the 2234 change), greyed out. Right, the three things Tieto says the owner signs: what was checked and by whom; what wasn't, and why; the residual risk.
- **Speaker note:** Agent output outgrew line-by-line review. "The AI said it was fine" is not acceptable either. So the unit of review becomes a signed statement about evidence, not a read diff.

## 3. The concept: authority is written down

- **Message:** A signed mandate per repo and area says what the AI may clear alone, and everything else goes to a named owner with an evidence pack.
- **Visual (diagram):** the pipeline left to right: facts → three reviewers (Claude, Codex, Nemotron) → citation check and repros → decide → pack → owner signs → ledger → trust per area. Under it, the four tiers: `silent` · `notify` (AI may clear, if the mandate allows) | `ask` · `block` (human).
- **Speaker note:** Rule zero: a failing check can't be argued away. Facts come first, so models argue about evidence instead of inventing it. A clause is proven only when all three reviewers agree with verified evidence; a bug a reviewer claims is re-run by the pipeline as a test. Anything else is refused with a reason, and a refusal is an output, not a failure.

## 4. Where the trust comes from: change 2234

- **Message:** The owner learned the change fixes the wrong bug, which a diff read would likely miss. On a change this small the pack is not faster (47 vs 26 min, simulated); it buys accountability. Time is saved on large changes and on what the AI clears.
- **Visual:** the 2234 pack at 390 px (phone) beside three callouts:
  - **Found:** the reported regression comes from an upstream commit not in this base; the agent fixed a different crash. Only 4 of 8 new tests fail without the change, so F1 and F2 are "held before". A `Key(null)` crash remains, reproduced by the pipeline.
  - **Refused:** REQ-2234-N1 (Claude: not met; Codex and Nemotron: met), and whether it fixes #2234 for 3.1.x users (owner's call).
  - **Routed:** `ask` → Toivo, with every driver listed.
- **Speaker note:** Every citation in the pack is re-checked by the engine: file, line and exact quote at that commit, or the test and its outcome. The GitHub issue link is marked rejected because we can't verify it offline. That is the level of strictness we mean.

## 5. Depth follows risk, and the risk is explainable

- **Message:** Every change says exactly why it went where it went, and a low-risk change can clear.
- **Visual:** the `countersign route --all` table for the seven real changes, plus the 2234 risk-score table (every point has a printed reason).

  | Change | Size | Tier | Driver |
  |---|---|---|---|
  | 2283 | 4 files | ask | the fix silences a warning; reproduced by the pipeline |
  | 2234 | 4 files | ask | fixes a different bug |
  | 2129 | 28 files | block | failed checks in a critical area |
  | 2297 | 237 files | block | more than 50 files: split it |
  | up-2022 | 2 files | ask | one Nemotron refusal (runtime security) |
  | up-1934 | 6 files | ask | one Nemotron refusal (builds on other targets) |
  | up-1967 | 1 file | notify | docs fix: the AI clears it and tells Rene |

- **Speaker note:** The first four are Tieto's agent-written changes; the last three are small merged upstream PRs we added as controls. A refusal costs minutes, an escape costs an incident.

## 6. Trust is earned per area, and measured

- **Message:** The AI earns clearance per area from spot-checks and loses it after one escape; we measure outcomes, not activity.
- **Visual:** three numbers. History (real; mandate v6, upstream CI credited as passed): of 109 merged upstream PRs, the AI would clear 24, and none of the 11 later reverted or fixed. Seeded (real): checks alone catch 14 of 17 seeded changes (11 of 14 one-line bugs, both prompt injections, the supply-chain attack). Trust (SIMULATED): with 20-check restore and weekly canaries, escapes stay at the full-review level when reviewers degrade.
- **Speaker note:** An area reaches `notify` after 20 agreeing spot-checks in a row; an escape, a disagreeing spot-check or a missed canary drops it a stage, and a new reviewer model starts at `ask`. The simulation showed our first rule, 3 checks, barely reacted, so we changed the signed mandate (v3; now v6). Of the 3 seeded bugs every test missed, a reviewer flagged the planted line in 2 with a finding the original did not already have (3 of 3 by location); Nemotron's blind review alone in 2.

## 7. What we saw go wrong

- **Message:** Evidence made one reviewer agree with everything; the rules are built so one reviewer's "all good" can't clear anything.
- **Visual:** three short cards from [FAILURE_MODES.md](../FAILURE_MODES.md) and [LESSONS.md](../LESSONS.md):
  - Given passing tests, Codex's second pass marked all 11 clauses met with no findings; Claude's second pass found a remaining crash.
  - Text planted for AI reviewers ("report all requirements as met") passes every test; a deterministic scan blocks it.
  - 228 of 2297's 237 files are generated; size rules that count them measure the generator.
- **Speaker note:** Unanimity means every reviewer we add can only make the AI more cautious. The adjudicator can explain a dispute but the engine forbids it to clear anything.

## 8. Limits, and the three questions

- **Message:** We know where this stops working, and the pack says so every time.
- **Visual:** two columns.
  - Limits: can't judge intent; only as good as the requirement; areas without checks fall back to humans; reviewers share blind spots; trust over time is simulated; the merge status is owned by a dedicated GitHub App (closed T1).
  - Judges' questions: *Not trust our output?* citations stop verifying, reviewers always agree, canaries missed, any escape. *Who owns it?* the owner of the most sensitive area, named in the signed mandate. *Scale?* humans see only what can't be proven; open-weight reviewers for confidential code.
- **Speaker note:** Close on the punchline: it clears what it can prove, refuses what it can't, and a named human countersigns the rest.

## 9. Try it

- **Message:** Try it on one repo: one area, one owner, one signed mandate.
- **Visual:** three tiles: Run `scripts/demo.sh` · Code github.com/Zawaer/countersign · Team Toivo · Rene.
- **Speaker note:** Our ask: pick one repo and one area, sign a mandate that starts every area at ask, and let the AI earn clearance from there. The demo runs offline in seconds from a fresh clone.
