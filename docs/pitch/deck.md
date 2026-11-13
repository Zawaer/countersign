# Deck outline (8 slides)

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
- **Visual (diagram):** the pipeline left to right: facts → independent reviewers → citation check → decide → pack → owner signs → ledger → trust per area. Under it, the four tiers: `silent` · `notify` (AI may clear, if the mandate allows) | `ask` · `block` (human).
- **Speaker note:** Facts come first, so models argue about evidence instead of inventing it. A clause is proven only when every reviewer agrees with verified evidence. Anything else is refused with a reason, and a refusal is an output, not a failure.

## 4. Where the trust comes from: change 2234

- **Message:** Nobody read 262 lines, and the owner still learned the change fixes the wrong bug.
- **Visual:** the 2234 pack at 390 px (phone) beside three callouts:
  - **Found:** the reported regression comes from an upstream commit not in this base; the agent fixed a different crash. Fail-without-fix: only 4 of 8 new tests fail without the change.
  - **Refused:** REQ-2234-N1, because one reviewer says met and the other reproduced a crash; and whether it fixes #2234 for 3.1.x users (owner's call).
  - **Routed:** `ask` → Toivo, with every driver listed.
- **Speaker note:** Every citation in the pack is re-checked by the engine: file, line and exact quote at that commit, or the test and its outcome. The GitHub issue link is marked rejected because we can't verify it offline. That is the level of strictness we mean.

## 5. Depth follows risk, and the risk is explainable

- **Message:** All four changes went to a human, and each one says exactly why.
- **Visual:** the `countersign route --all` table, plus the 2234 risk-score table (every point has a printed reason).

  | Change | Size | Tier | Driver |
  |---|---|---|---|
  | 2283 | 4 files | ask | the fix silences a warning users relied on; a guard it needs is untested |
  | 2234 | 4 files | ask | fixes a different bug; reviewers disagree |
  | 2129 | 28 files | block | new public API, failed checks in a critical area |
  | 2297 | 237 files | block | more than 50 files: split it |

- **Speaker note:** A new repo has no track record, so the mandate starts strict and most changes go to humans. That is a trade-off we chose: a refusal costs minutes, an escape costs an incident.

## 6. Trust is earned per area, and measured

- **Message:** The AI earns clearance per area from spot-checks and loses it after one escape; we measure outcomes, not activity.
- **Visual:** `countersign trust` table before and after a simulated escape (labelled SIMULATED), and the replay metrics. TODO(numbers): share routed to humans, seeded-defect catch rate, findings verified/rejected per reviewer, simulated review minutes, from `measurement/results.md`.
- **Speaker note:** Spot-checks grade the AI's own recommendation; three agreeing in a row restore an area's clearance. Seeded defects tell us what the checks miss: two of the first four we planted survived the whole test suite, and both reviewers had read one of those lines as correct.

## 7. What we saw go wrong

- **Message:** Evidence made one reviewer agree with everything; the rules are built so one reviewer's "all good" can't clear anything.
- **Visual:** three short cards from [FAILURE_MODES.md](../FAILURE_MODES.md) and [LESSONS.md](../LESSONS.md):
  - Given passing tests, Codex's second pass marked all 11 clauses met with no findings; Claude's second pass found a remaining crash.
  - A requirement can be met before the change, so "met" isn't "achieved".
  - 228 of 2297's 237 files are generated; size rules that count them measure the generator.
- **Speaker note:** Unanimity means every reviewer we add can only make the AI more cautious. The adjudicator can explain a dispute but the engine forbids it to clear anything.

## 8. Limits, and the three questions

- **Message:** We know where this stops working, and the pack says so every time.
- **Visual:** two columns.
  - Limits: can't judge intent; only as good as the requirement; areas without checks fall back to humans; reviewers share training data; trust numbers here are simulated.
  - Judges' questions: *Not trust our output?* citations stop verifying, reviewers always agree, seeded defects pass, any escape. *Who owns it?* the owner of the most sensitive area, named in the signed mandate. *Scale?* humans see only what can't be proven; open-weight reviewers for confidential code.
- **Speaker note:** Close on the punchline: it clears what it can prove, refuses what it can't, and a named human countersigns the rest.
