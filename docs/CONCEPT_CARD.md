# Countersign: concept card

> **AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it can't, and a named human countersigns the rest.**

## Recommendation

Stop asking *"did a human read every line?"* Ask *"did a named human sign for what was proven, refused, and left at risk?"*

0. **A failing check can't be argued away.** If a required check fails, nothing clears the change. Enforced in code.
1. **A mandate per repo and area:** a signed file saying how far the AI may go alone. The **tier** is where a change goes: `silent` or `notify` (AI clears it), `ask` (a named owner signs), `block` (fix or split first).
2. **Facts before opinions.** Build, tests, fail-without-fix, public API, analyzers, dependency diff and a scan for planted instructions run first.
3. **Three reviewers, unanimity.** Claude, Codex and Nemotron. Every claim cites something the engine re-checks. A clause is *proven* only if all say "met" with verified evidence and its checks pass; otherwise it is *refused*, with the reason. One reviewer can never clear: Codex once called all <!--n:codex_v2_met-->11<!--/n--> clauses met with <!--n:codex_verified-->0<!--/n--> verified findings. Gemini adjudicates disputes and can never clear.
4. **Claims become checks.** A bug a reviewer reproduced becomes a repro test the pipeline runs on old and new code.
5. **The change explains itself** in an evidence pack; **a named owner countersigns** its hash (Ed25519) into a hash-chained ledger, rating each AI finding.
6. **Trust is earned per area.** ask -> notify after 20 agreeing spot-checks in a row, -> silent after 40. An **escape** (a merged change later reverted or fixed), a disagreeing spot-check or a missed canary drops one stage. A new reviewer model or prompt starts at ask.

## Principles: the five forces

| Force | Principle | Mechanism |
|---|---|---|
| Risk | Depth follows risk, explainably. | Additive score with a reason per point; hard rules; tier = strictest driver. |
| Hallucination | No evidence, no finding. | Every citation re-checked; rejected claims stay visible and count against the reviewer. Planted instructions void all verdicts (R-INJECT). |
| Transparency, confidence | Every decision names its driver; confidence is never self-reported. | Same inputs, same pack hash; agreement plus passing checks. |
| Quality | Tests must prove they test something. | Fail-without-fix per test; a clause whose tests already passed before is *held before*: met, not achieved by the change. |

## On a real change: ju26-issue-2234

- **Found:** sound code that fixes a *different* crash (the reported regression isn't in the base). Only <!--n:t2234_fail_without_fix-->4<!--/n--> of <!--n:t2234_new_tests-->8<!--/n--> new tests fail without the change, so two clauses are *held before*; mutation testing agrees (<!--n:t2234_mutants_killed-->5<!--/n--> of <!--n:t2234_mutants-->8<!--/n--> mutants killed, none by F1's or F2's tests). `Key(null)` still crashes; the pipeline reproduced it.
- **Refused:** the no-crash clause (reviewers split; Gemini found Claude's objection supported); whether #2234 is fixed for 3.1.x users (the owner's call).
- **Routed:** `ask` to Toivo, who learns it fixes the wrong bug. On a change this small the pack takes longer than the diff (<!--n:pack_min_2234-->47<!--/n--> vs <!--n:read_min_2234-->26<!--/n--> min, simulated); the payoff is what a diff read misses.
- **Other six:** 2283 `ask` (silences a warning; reproduced); 2129 `block` (failed checks); 2297 `block` (237 files: split). Upstream controls: two `ask`; a docs fix at `notify` (the AI clears it, tells Rene).

## Evidence it works

- **History:** of <!--n:history_prs-->109<!--/n--> real merged PRs (mandate v<!--n:history_mandate-->6<!--/n-->, upstream CI credited as passed), the AI would clear <!--n:history_cleared-->24<!--/n-->, and <!--n:history_escapes_cleared-->0<!--/n--> of the <!--n:history_escapes-->11<!--/n--> escapes.
- **Seeded:** <!--n:seeded_total-->18<!--/n--> seeded changes (<!--n:seeded_bugs-->14<!--/n--> bugs, <!--n:seeded_injections-->2<!--/n--> prompt injections, 1 supply-chain attack, 1 security downgrade); checks alone catch <!--n:seeded_caught_by_checks-->14<!--/n--> of <!--n:seeded_total-->18<!--/n-->. Of the <!--n:seeded_survivors-->4<!--/n--> that got past every check, a reviewer flagged the planted line in <!--n:seeded_survivors_flagged_new-->3<!--/n--> with a finding the original didn't already have.
- **Simulated:** with 20-check restore and weekly canaries, escapes stay at the full-review level when reviewers degrade. This changed the mandate (v3; now v<!--n:mandate_version-->6<!--/n-->).
- **Red team:** we attacked our own pipeline <!--n:redteam_total-->35<!--/n--> ways; it now stops <!--n:redteam_stopped-->35<!--/n--> of <!--n:redteam_total-->35<!--/n--> (7 before the fixes).
- **Owner:** Toivo signed <!--n:signoffs-->4<!--/n--> changes and rated each AI finding (Claude's accepted <!--n:claude_accepted-->9<!--/n--> of <!--n:claude_rated-->13<!--/n-->, Nemotron's <!--n:nemotron_accepted-->8<!--/n--> of <!--n:nemotron_rated-->10<!--/n-->).

## Trade-offs we chose

More refusals for fewer escapes. Unanimity: each added reviewer only adds caution. Strict citations lose some true findings (shown as "rejected"). Trust returns slowly: 20 checks after a drop.

## Limits

- It can't judge **intent**, and is only as good as the **requirement text**.
- **Areas without checks** (UI, performance, other targets) fall back to humans.
- Reviewers **share blind spots** (all three said the clause resting on 2283's untested guard was met).
- **Confidential code** gets a weaker panel: a self-hosted 30B matched <!--n:selfhost_clauses_agree-->31<!--/n--> of <!--n:selfhost_clauses-->34<!--/n--> verdicts but wrote <!--n:selfhost_findings-->2<!--/n--> findings to the hosted 120B's <!--n:selfhost_hosted_findings-->17<!--/n-->, so checks and the owner carry more weight there.
- Demo gaps: trust over time and review minutes are simulated.

## The judges' three questions

- **What would make us distrust our output?** Citations that stop verifying, reviewers that always agree, missed canaries, escapes in AI-cleared areas. Each is measured; the last two drop trust automatically.
- **Who owns the decision?** The owner of the most sensitive area touched, named in the signed mandate. Only a signature merges.
- **How does it scale?** Not by saving reading time on small changes. Machine cost is bounded (<!--n:nemotron_call_min_k-->38<!--/n-->k to <!--n:nemotron_call_max_k-->71<!--/n-->k tokens, about 2 CI minutes per review, any size); proven changes cost no human time; every decision has a name ([SCALING.md](SCALING.md)).
