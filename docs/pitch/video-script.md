# Demo video script (2:00 hard limit)

About 230 spoken words, which leaves room for pauses at a calm pace (~130 words per minute). Every frame is a capture of a real artifact in this repo; nothing is mocked up except the title cards. Record the voice-over first, then cut the captures to it.

| Time | On screen | Voice-over |
|---|---|---|
| 0:00–0:10 | GitHub PR page: "Implementation for #2234", author is an agent, 4 files, +262 −4. Zoom on the approver field: **Toivo**. | Friday afternoon. An agent opens a pull request. Two hundred and sixty lines, and your name is on the approval. |
| 0:10–0:22 | The Countersign PR comment on that PR (tier `ASK`, owner Toivo, link to the pack). Tap the link: [packs/2234/pack.html](../../packs/2234/pack.html) on a phone, 390 px wide, first screen: **ASK · owner Toivo · Why this tier**. TODO(numbers): capture the PR comment from the PR-flow demo once it exists. | With Countersign, the change opens with its own explanation: where it goes, who owns it, and why. |
| 0:22–0:34 | Pack, "What was checked": highlight `tests.fail_without_fix ... 4/8 failed` and `tests.execution_fail_without_fix: fail ... 0/4`. | First, facts. We revert the fix and keep the new tests. Half of them still pass. They don't test this change. |
| 0:34–0:50 | Pack, "What the AI found": finding **claude:C1** with its `[OK]` citations (TypeCollector.cs at base, line 1369). Brief split screen with [reviews/2234/codex.md](../../reviews/2234/codex.md). | Then reviewers from different vendors read it separately, and every claim must cite a line, a test or a check that we re-verify. One of them found it: this is sound code that fixes the wrong bug. |
| 0:50–1:05 | Pack, "Requirement trace": row **REQ-2234-N1 refused — not_met; reviewers_disagree**. Then the refusal: "whether this resolves #2234 for 3.1.x users". | What it can't prove, it refuses, and says why. One reviewer says the no-crash requirement is met; the other reproduced a crash. Disagreement means refusal. Which release this fixes is the owner's call. |
| 1:05–1:18 | Desktop pack: scroll "What was not checked", "Residual risk", the sign-off statement. Terminal: `countersign sign 2234 --as Toivo --decision request-changes --note "..."`, then the new ledger line. | Toivo reads what was checked, what wasn't, and the risk that's left, and countersigns. His signature and the pack's hash go into a hash-chained ledger. |
| 1:18–1:26 | Terminal: `countersign verify-ledger` → OK. `sed` edits one entry in a copy. `verify-ledger --inputs /tmp/t` → **LEDGER INVALID: line 2**. | Change one byte, and verification fails. |
| 1:26–1:42 | Terminal: `countersign route --all` (2283 ask, 2234 ask, 2129 block, 2297 block). Then `countersign trust` table; TODO(numbers): the simulated escape dropping `generator-analyzer-core` to `ask`, labelled SIMULATED on screen. | Review depth follows risk. The 237-file change is blocked until it's split. The AI earns clearance per area from spot-checks, and loses it after a single escape. |
| 1:42–1:52 | `measurement/results.md`: share routed to humans, seeded defects caught, findings verified per reviewer. Simulated numbers carry the SIMULATED label on screen. TODO(numbers): capture once the replay is committed. | And we measure outcomes: what reaches humans, which findings hold up, and which planted bugs get caught. |
| 1:52–2:00 | Title card: **Countersign** and the punchline. github.com/Zawaer/countersign | Countersign. AI reviews under a mandate. It clears what it can prove, refuses what it can't, and a named human countersigns the rest. |

## Capture list

1. PR page for the 2234 change, and the Countersign PR comment (from the PR-flow demo). TODO(numbers): PR URL.
2. `packs/2234/pack.html` at 390 px (phone): top card, "Why this tier".
3. `packs/2234/pack.html` on desktop: "What was checked", "What the AI found", "Requirement trace", "Not checked", "Residual risk", "Sign-off".
4. Terminal, large font, dark theme: `countersign route --all`, `countersign sign ...`, `countersign verify-ledger` before and after the tamper, `countersign trust`.
5. `measurement/results.md` (once committed).
6. Title card.

## Rules for the edit

- Every number on screen must be readable for at least two seconds and must come from a file in the repo.
- Anything simulated (trust events, review minutes) shows a SIMULATED label on screen.
- If the cut runs long, drop the 1:42 measurement shot first, not the refusal shot: refusals are what the brief asks for.
