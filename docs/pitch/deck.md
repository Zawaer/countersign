# Deck outline (10 slides)

One idea per slide: one scene, a few labels. The slides follow the demo video's story: green CI but the wrong bug, the signed mandate, the line the fix never touches, the owner signs and the merge is blocked, a low-risk fix that clears, the tamper-proof ledger, the numbers, the limits. The slides are built from the repo's records by `site/build.py` (`site/pitch.html`); `docs/pitch/export_pdf.py` exports them to `deck.pdf`. Speaker notes are what to say if the deck is presented live; the PDF leaves them out.

---

## 1. Title

- **Message:** Countersign. AI reviews agent-written code under a signed mandate. It clears what it can prove, refuses what it can't, and a named human countersigns the rest.
- **Visual:** the Countersign mark and name, the punchline, the demo (countersign.toivo.dev) and the code (github.com/Zawaer/countersign); small line: "Junction 2026 · Tieto: Earned Trust in AI Code".
- **Speaker note:** We are not proposing a better AI reviewer. We are proposing a way to delegate review authority to AI that a named person can still sign for.

## 2. Green CI, wrong bug

- **Message:** An AI agent wrote this fix for issue #2234. It builds, all <!--n:t2234_suite_passed-->175<!--/n--> tests pass, and an AI reviewer says every requirement is met. It fixes the wrong bug.
- **Visual:** the landing page's first screen: three green ticks (builds, <!--n:t2234_suite_passed-->175<!--/n-->/<!--n:t2234_suite_total-->175<!--/n--> tests pass, AI reviewer: requirements met), then in red "It fixes the wrong bug."
- **Speaker note:** Agent output outgrew line-by-line review, and "the AI said it was fine" is not acceptable either. Every signal a team trusts today is green here.

## 3. The concept: authority is written down

- **Message:** A signed mandate per repo and area decides what the AI may clear alone; everything else goes to a named owner with an evidence pack.
- **Visual (diagram):** facts → three reviewers → citations re-checked → decide → owner signs. Under it, the four tiers: `silent` · `notify` (the AI may clear) | `ask` · `block` (a named human).
- **Speaker note:** Facts come first: the build, the tests, and whether each new test fails without the fix. Then three AI reviewers from three vendors (Claude, Codex, Nemotron). Every citation is re-checked at the commit: file, line and exact quote. A requirement counts as proven only when all three agree with verified evidence, so one reviewer's "all good" clears nothing: given passing tests, Codex marked all <!--n:codex_v2_met-->11<!--/n--> clauses met with no findings. Anything else is refused with a reason.

## 4. The line the fix never touches

- **Message:** The bug the issue reports is on a line the fix never touches. Undo the fix and <!--n:t2234_pass_without_fix-->4<!--/n--> of its <!--n:t2234_new_tests-->8<!--/n--> new tests still pass. A reviewer found a crash the fix leaves in, and the pipeline reproduced it. So the AI won't clear it: ask → Toivo.
- **Visual:** the cited hunk of `TypeCollector.cs` with the pin "Untouched by the fix"; two labels under it; the pill `ASK → Toivo`.
- **Speaker note:** Claude found it and cited the exact line; the engine verified the quote at that commit. The Key(null) crash was claimed by a reviewer and re-run by the pipeline as a test: it fails on head and base, passes on the control. The owner's question is no longer "did you read 262 lines?" but "do you accept this evidence and this risk?"

## 5. Depth follows risk

- **Message:** Every change says why it went where it went, and a low-risk change can clear. A docs fix (demo-docs1, tier `notify`) was cleared by the AI alone and merged through the gate in 40 s (demo PR #11, times from the GitHub API).
- **Visual:** the tier of every real change as chips; under them, the docs fix that merged in 40 s.
- **Speaker note:** The four numbered changes are Tieto's agent-written ones; the up- changes are small merged upstream PRs we added as controls; demo-docs1 is an agent-written docs fix run through the real GitHub gate. A refusal costs minutes, an escape costs an incident.

## 6. The owner signs on GitHub

- **Message:** Toivo signed a request for changes. The required check `countersign/tier` fails, and the merge is blocked.
- **Visual:** the demo PR as GitHub shows it (captured from the demo repo): `countersign/tier` failing with "changes requested by Toivo", Required; "Merging is blocked".
- **Speaker note:** The status is posted by a dedicated GitHub App; branch protection requires it from that App, enforced for admins. An agent can post a green status from a workflow, but not as the App.

## 7. A record no one can quietly edit

- **Message:** Every sign-off goes into a signed, hash-chained ledger. Edit one line and the check fails; recompute the hash and the signature fails.
- **Visual:** three steps: ledger OK (<!--n:ledger_entries-->14<!--/n--> entries) → edit one line: invalid → recompute the hash: signature does not verify.
- **Speaker note:** Only the signer's private key can sign a new hash, and that key is not in the repo. Try it live on the tour, step 6.

## 8. Measured, not claimed

- **Message:** <!--n:history_escapes-->11<!--/n--> of <!--n:history_escapes-->11<!--/n--> later-reverted real PRs were sent to a human (replay of <!--n:history_prs-->109<!--/n--> merged PRs; the AI would clear <!--n:history_cleared-->24<!--/n-->, <!--n:history_escapes_cleared-->0<!--/n--> of the escapes). Tests and checks caught <!--n:seeded_caught_by_checks-->14<!--/n--> of <!--n:seeded_total-->18<!--/n--> planted bugs. <!--n:redteam_stopped-->35<!--/n--> of <!--n:redteam_total-->35<!--/n--> attacks on our own pipeline were stopped.
- **Visual:** three big numbers: <!--n:history_escapes-->11<!--/n-->/<!--n:history_escapes-->11<!--/n-->, <!--n:seeded_caught_by_checks-->14<!--/n-->/<!--n:seeded_total-->18<!--/n-->, <!--n:redteam_stopped-->35<!--/n-->/<!--n:redteam_total-->35<!--/n-->.
- **Speaker note:** The replay is real (mandate v<!--n:history_mandate-->6<!--/n-->, upstream CI credited as passed). On the <!--n:seeded_survivors-->4<!--/n--> planted bugs every check missed, a reviewer pointed at the planted line in <!--n:seeded_survivors_flagged_new-->3<!--/n--> with a finding the original did not already have. Trust over time (an area earns `notify` from agreeing spot-checks and loses it after one escape) is simulated, and marked so.

## 9. It says where it stops

- **Message:** We know where this stops working, and the pack says so every time.
- **Visual:** four labels: can't judge intent · only as good as the requirement · net8.0 / Linux only · trust over time is simulated.
- **Speaker note:** Judges' questions: *Not trust our output?* citations stop verifying, reviewers always agree, canaries missed, any escape. *Who owns it?* the owner of the most sensitive area, named in the signed mandate. *Scale?* humans see only what can't be proven; open-weight reviewers for confidential code.

## 10. Try it

- **Message:** Try it on one repo: one area, one owner, one signed mandate.
- **Visual:** the mark; the demo (countersign.toivo.dev) and the code (github.com/Zawaer/countersign) in large type; under them, Run `scripts/demo.sh` · Team Toivo · Rene.
- **Speaker note:** Our ask: pick one repo and one area, sign a mandate that starts every area at ask, and let the AI earn clearance from there. The demo runs offline in seconds from a fresh clone. Close on the punchline: it clears what it can prove, refuses what it can't, and a named human countersigns the rest.
