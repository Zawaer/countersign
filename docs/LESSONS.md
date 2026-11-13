# Lessons log

What we learned building Countersign and running it on the four agent-written MessagePack-CSharp changes. Oldest first. Each entry is dated by the commit that recorded its evidence (Europe/Helsinki time, commit id in brackets). Each entry links to the artifact it comes from; the failure-mode codes (A1, R1, E2...) refer to [FAILURE_MODES.md](FAILURE_MODES.md) and the D-codes to [DECISIONS.md](DECISIONS.md).

---

### L1. Sat 14 Nov 01:23 (38f7014): Fail-without-fix is the single most informative check

Revert the source, keep the new tests, run them. The result per change ([facts.json](../evidence/2234/facts.json) for each):

| Change | New tests that fail without the fix |
|---|---|
| 2283 | 3 of 3 |
| 2129 | 6 of 6 (the runtime tests can't compile without the fix) |
| 2297 | 2 of 2 |
| 2234 | 4 of 8 analyzer tests; 0 of 4 runtime tests |

Three changes passed it cleanly. On 2234 it independently pointed at the same problem the root-cause review found: half the "coverage" documents behaviour the base already had.

**Lesson:** cheap, deterministic, and it can't hallucinate. It turns "the PR has tests" into "the PR has tests that test this change". We made it a mandated check for the generator/analyzer area (A4).


### L2. Sat 14 Nov 01:23 (38f7014): Tests and reviewers share blind spots; seeded defects find them

We seeded four single-line defects into the 2283 and 2234 fixes ([evidence/README.md](../evidence/README.md)). Two were caught by the tests. Two survived the whole suite: removing the `ContainsSyntaxTree` guard on 2283 (the line REQ-2283-F3 depends on) and removing a `continue` in the field loop on 2234 ([evidence/2283-mut1/facts.json](../evidence/2283-mut1/facts.json), [evidence/2234-mut2/facts.json](../evidence/2234-mut2/facts.json)). Both reviewers had read the 2283 guard as correct.

**Lesson:** mixing vendors doesn't remove correlated misses. Where models agree, deterministic checks have to do the work, and seeded defects are how you find out which lines nothing protects (A3, R5). TODO(numbers): add the replay's catch rate (`catch_rate`, `catch_rate_attributable`) for the four mutants once `measurement/results.md` is committed.


### L3. Sat 14 Nov 01:23 (38f7014): Generated files distort size rules

2297 changes 237 files, and 228 of them are generated (`diff.by_kind` in [evidence/2297/facts.json](../evidence/2297/facts.json)). The "more than 50 files: split" rule counts all of them, so it blocks a change whose source part is small.

We kept the block: the generated snapshots hid an unrelated whitespace edit in a generator utility (A5), and a reviewer found two major problems in the source part (A6, A7). But a size rule that counts generated output measures the generator, not the change.

**Lesson:** size rules should count source and generated separately, and say which one fired. The pack already shows the split; the rule itself is an open question for the mandate owner (E2).


### L4. Sat 14 Nov 01:23 (38f7014): Every pack has a "not checked" list, and it is the same list

Every check ran on net8.0 on Linux. .NET Framework and netstandard paths were never built or tested. The 2297 `#if` problem (A6) lives exactly there, and no test could have caught it.

**Lesson:** a standing gap belongs in the mandate (`known_gaps`), printed in every pack, so the owner signs for it knowingly. If the same gap keeps hiding real findings, it is the next check to build (E3).

### L5. Sat 14 Nov 01:24 (a4b6b18, 1efada0): Reviewers refuse for environment reasons

Both first-pass reviews (Claude v1 and Codex v1) refused clauses because test projects didn't compile in *their* sandbox, not because of anything in the change ([reviews/2234/claude.v1.md](../reviews/2234/claude.v1.md), [reviews/2283/codex.v1.json](../reviews/2283/codex.v1.json)). Codex v1 gave `cannot_determine` on 7 of the 11 requirement clauses across the four changes.

**Lesson:** don't let each reviewer build its own facts. Build and test results come from one controlled run (stage 1), and reviewers cite that. A refusal is only useful if its reason is about the change (R2, D2).


### L6. Sat 14 Nov 01:24 (a4b6b18): A sound change can fix the wrong bug

On 2234 the agent's code is correct and tested, and it fixes a real crash on duplicate or mixed keys. But the regression issue #2234 reports comes from an upstream commit that isn't an ancestor of the branch's base. Merged into the 3.1.x line where users hit the bug, the issue would stay open ([pack 2234, finding claude:C1](../packs/2234/pack.md)).

**Lesson:** "is this code good?" is the wrong first question. The first question is "does this change do what its requirement says, for the users who reported it?". That needs root-cause work against the issue and the git history, not a line-by-line read. Only one of our two reviewers did that work (A1).


### L7. Sat 14 Nov 01:30 (9a32848): A test can fail for the toolchain, not the change

The repo pins .NET SDK 8.0.402, but the source generator references Roslyn 4.12, which only ships with SDK 9. The execution tests therefore don't compile **on the base commit either**. Had we recorded that as `fail`, every change would have looked broken.

**Lesson:** a check needs a fourth state. Ours are `pass`, `fail`, `skipped` (deliberately not run, with a reason) and `error` (the check itself broke). `error` and `skipped` never count as a pass, and never as a fail of the change. We re-ran the execution tests under SDK 9 and wrote down why ([evidence/README.md](../evidence/README.md), E1).


### L8. Sat 14 Nov 01:40 (aa4645b): A requirement can be met without being achieved

REQ-2234-F1 and F2 are "met" on the head. They were also met on the base: the tests for them pass without the change. Our engine still marks such a clause `proven`, because every reviewer says `met` and its checks pass.

**Lesson:** "met" and "achieved by this change" are different statements, and a requirement trace that doesn't separate them overstates what the change did. The fix is a `held_before` status from fail-without-fix per test. Both second-pass reviewers noticed it in prose (Codex: "that clause was already satisfied before this change", [reviews/2234/codex.md](../reviews/2234/codex.md); Claude: F2 "already held on base", [reviews/2234/claude.md](../reviews/2234/claude.md)) and both still said `met`, because the verdict vocabulary has no word for it (A2). TODO(numbers): note here whether `held_before` landed in the engine before the freeze.


### L9. Sat 14 Nov 01:40 (aa4645b): Evidence makes reviewers agreeable

Codex's second pass got the deterministic facts. It turned every `cannot_determine` into `met`: all 11 clauses across the four changes, with zero findings ([reviews/*/codex.json](../reviews/2234/codex.json)). It missed what the other reviewer found: the wrong bug on 2234 (A1), the wrong `#if` on 2297 (A6), and the build break for existing users on 2297 (A7).

**Lesson:** passing tests are strong evidence that the tests pass, and weak evidence of anything else. A reviewer handed green checks tends to read them as "done". This is why a clause is proven only when **every** reviewer agrees, and why any verified major finding routes to a human: one reviewer's "all good" can't clear anything (R1, D3, D8).


### L10. Sat 14 Nov 01:40 (aa4645b): Self-reported metadata is not evidence

Codex returned a placeholder `reviewed_at` and a model name the tool can't confirm ([CODEX_LOG.md](CODEX_LOG.md)).

**Lesson:** the runner stamps time, model and prompt version; the model's own claims about itself are ignored (R3).


### L11. Sat 14 Nov 01:41 (bf77100): Our own verifier can be the hallucination

8 correct Codex test citations were marked unverified, because the same test is `passed` on the change and `failed` in the fail-without-fix run, and our verifier matched the wrong run.

**Lesson:** the pipeline that checks reviewers needs checking too. Because unverified items are shown in the pack and not deleted, the error was visible and we fixed it (commit bf77100). If we had silently dropped unverified claims, we would have measured a false hallucination rate for Codex (R4).


### L12. Sat 14 Nov 01:43 (bf6ec76): More reviewers must never make clearing easier

With a 2-of-3 majority, adding a reviewer lets two outvote a third reviewer's verified objection. We chose unanimity among participating reviewers, and a reviewer that didn't run counts as `missing_review`.

**Lesson:** decide which direction each added model pushes. Under unanimity each one can only add caution. For the same reason the adjudicator (Gemini) may explain a dispute but can never turn a refused clause into proven, and the engine asserts that (D8, D9).


### L13. Sat 14 Nov 01:46 (c35e853): Evidence doesn't make every reviewer agreeable, which is why we need more than one

Claude's second pass got the same facts as Codex's (L9). It went the other way: on 2234 it kept the wrong-bug finding, and moved REQ-2234-N1 ("must not crash on invalid contracts") from `met` to `not_met`, because a probe it ran found one invalid contract that still crashes the analyzer (finding claude:C2, [reviews/2234/claude.md](../reviews/2234/claude.md)). Codex says `met` on the same clause, so the pack refuses it with `not_met` and `reviewers_disagree` ([pack 2234](../packs/2234/pack.md), requirement trace).

**Lesson:** the same evidence made one reviewer settle and the other dig. We can't know in advance which reviewer will drift on which change, so the rule can't depend on it: one `not_met` with verified evidence is enough to refuse. The disagreement itself is the useful output: it tells the owner exactly which clause to look at. Note the probe ran in the reviewer's scratch worktree and is not in facts.json; the finding verifies because it cites the line it is about, but the reproduction itself is the reviewer's word until a check reruns it.

### L14. Sat 14 Nov 01:47 (5f9b5b4): A re-review can silently erase a true finding

Claude's first pass reproduced a build break on 2297 (CS0579 for users who already put the attribute on their resolver). Its second pass dropped it as "not re-checked in this pass", and 2129's first-pass findings disappeared the same way (R6). The same second pass also found new problems by writing probes: a regression in 2283 (a warning users relied on is now silenced) and the remaining crash in 2234 (A10, A11).

**Lesson:** a review pass is not a fresh start. Open findings have to carry forward: a later pass must confirm them, refute them with evidence, or leave them open; they can't just vanish. Until the engine enforces that, the pack keeps earlier passes (`*.v1.*`) beside the current one so a drop is visible.

---

## Pending entries

- **Nemotron as a third reviewer.** TODO(numbers): verified vs rejected citations per change, and whether it sided with Claude or Codex on REQ-2234-N1.
- **Gemini adjudication.** TODO(numbers): how many disputes it was given, and whether its rulings pointed at the side whose citations verified.
- **Measurement replay.** TODO(numbers): share routed to humans, simulated minutes with and without the pack.
