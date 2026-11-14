# Countersign: concept card

> **AI reviews agent-written code under a mandate: it clears what it can prove, refuses what it can't, and a named human countersigns the rest.**

## Recommendation

Replace *"did a human read every line?"* with *"did a named human sign for what was proven, refused and left at risk?"*

0. **A failing required check can't be argued away** (enforced in code).
1. **A signed mandate per repo and area** sets how far the AI may go alone. **Tiers:** `silent`/`notify` (AI clears), `ask` (named owner signs), `block` (fix or split first).
2. **Facts first:** build, tests, fail-without-fix, public API, analyzers, dependency diff and planted-instruction scan run before reviewers.
3. **Three reviewers, unanimity.** Claude, Codex and Nemotron cite evidence the engine re-checks. A clause is *proven* only on a unanimous, verified "met" plus passing checks; else *refused*, with a reason. No single reviewer clears: Codex once called all <!--n:codex_v2_met-->11<!--/n--> clauses met with <!--n:codex_verified-->0<!--/n--> verified findings. Gemini adjudicates disputes, never clears.
4. **Claims become checks:** a reproduced bug becomes a test on old and new code.
5. **An evidence pack explains the change; a named owner countersigns** its hash (Ed25519) into a hash-chained ledger, rating each AI finding.
6. **Trust is earned per area:** ask -> notify after 20 agreeing spot-checks in a row, silent after 40. An **escape** (merged, then reverted or fixed), disagreeing spot-check or missed canary drops a stage; a new model or prompt restarts at ask.

## Principles: the five forces

| Force | Principle | Mechanism |
|---|---|---|
| Risk | Depth follows risk, explainably. | Additive score, a reason per point; hard rules; tier = strictest driver. |
| Hallucination | No evidence, no finding. | Citations re-checked; rejected claims stay visible, counting against the reviewer. Planted instructions void all verdicts (R-INJECT). |
| Transparency, confidence | Every decision names its driver; confidence is never self-reported. | Same inputs, same pack hash; agreement plus passing checks. |
| Quality | Tests must prove they test something. | Fail-without-fix per test; a clause whose tests pass pre-change is *held before* (met, not by the change). |

## On a real change: ju26-issue-2234

- **Found:** sound code fixing a *different* crash (the reported regression isn't in the base). Only <!--n:t2234_fail_without_fix-->4<!--/n--> of <!--n:t2234_new_tests-->8<!--/n--> new tests fail without it (two clauses *held before*); mutation testing agrees (<!--n:t2234_mutants_killed-->5<!--/n--> of <!--n:t2234_mutants-->8<!--/n--> mutants killed, none by F1's or F2's tests). `Key(null)` still crashes (reproduced).
- **Refused:** the no-crash clause (reviewers split; Gemini backed Claude); whether #2234 is fixed for 3.1.x users (owner's call).
- **Routed:** `ask` to Toivo, who learns it's the wrong bug and signs *request changes*; on the real PR the gate blocks the merge ([demo PR #2](https://github.com/Zawaer/countersign-messagepack-demo/pull/2)). The pack takes longer than this small diff (<!--n:pack_min_2234-->47<!--/n--> vs <!--n:read_min_2234-->26<!--/n--> min, simulated) but catches what reading misses.
- **Other seven:** 2283 `ask` (silences a warning; reproduced); 2129 `block` (failed checks); 2297 `block` (237 files: split). Upstream controls: two `ask`, a docs fix `notify` (AI clears, tells Rene). An agent-written docs fix, demo-docs1: `notify`, merged through the gate in 40 s with no human asked ([demo PR #11](https://github.com/Zawaer/countersign-messagepack-demo/pull/11)).

## Evidence it works

- **History:** of <!--n:history_prs-->109<!--/n--> merged PRs (mandate v<!--n:history_mandate-->6<!--/n-->, upstream CI counted as passed), the AI would clear <!--n:history_cleared-->24<!--/n-->, and <!--n:history_escapes_cleared-->0<!--/n--> of the <!--n:history_escapes-->11<!--/n--> escapes.
- **Seeded:** <!--n:seeded_total-->18<!--/n--> changes (<!--n:seeded_bugs-->14<!--/n--> bugs, <!--n:seeded_injections-->2<!--/n--> prompt injections, 1 supply-chain attack, 1 security downgrade); checks catch <!--n:seeded_caught_by_checks-->14<!--/n--> of <!--n:seeded_total-->18<!--/n-->. Of the <!--n:seeded_survivors-->4<!--/n--> past every check, reviewers flagged the planted line in <!--n:seeded_survivors_flagged_new-->3<!--/n--> with a new finding.
- **Simulated:** with 20-check restore and weekly canaries, escapes stay at full-review level when reviewers degrade (drove mandate v3; now v<!--n:mandate_version-->6<!--/n-->).
- **Red team:** <!--n:redteam_total-->35<!--/n--> attacks on our pipeline; it now stops <!--n:redteam_stopped-->35<!--/n--> of <!--n:redteam_total-->35<!--/n--> (7 before fixes).
- **Owner:** Toivo signed <!--n:signoffs-->4<!--/n--> changes; accepted findings: Claude <!--n:claude_accepted-->9<!--/n--> of <!--n:claude_rated-->13<!--/n-->, Nemotron <!--n:nemotron_accepted-->8<!--/n--> of <!--n:nemotron_rated-->10<!--/n-->.

## Trade-offs we chose

More refusals for fewer escapes. Each added reviewer only adds caution. Strict citations lose some true findings (shown "rejected"). Trust returns slowly (20 checks after a drop).

## Limits

- No judging **intent**; only as good as the **requirement text**. **Areas without checks** (UI, performance, other targets) fall back to humans.
- Reviewers **share blind spots** (all three passed the clause resting on 2283's untested guard).
- **Confidential code** gets a weaker panel: a self-hosted 30B matched <!--n:selfhost_clauses_agree-->31<!--/n--> of <!--n:selfhost_clauses-->34<!--/n--> verdicts but found <!--n:selfhost_findings-->2<!--/n--> issues vs the hosted 120B's <!--n:selfhost_hosted_findings-->17<!--/n-->; checks and owner weigh more.
- Simulated in the demo: trust over time, review minutes.

## The judges' three questions

- **What would make us distrust our output?** Citations that stop verifying, reviewers always agreeing, missed canaries, escapes in AI-cleared areas. All measured; the last two auto-drop trust.
- **Who owns the decision?** The owner of the most sensitive area touched, named in the mandate. Only a signature merges.
- **How does it scale?** Not by faster reading of small changes. Machine cost is bounded (<!--n:nemotron_call_min_k-->38<!--/n-->k–<!--n:nemotron_call_max_k-->71<!--/n-->k tokens, ~2 CI minutes, any size); proven changes cost no human time; every decision is named ([SCALING.md](SCALING.md)).
