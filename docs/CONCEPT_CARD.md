# Countersign: concept card

> **AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it can't, and a named human countersigns the rest.**

## Recommendation

Stop asking *"did a human read every line?"* Ask *"did a named human sign for what was proven, refused, and left at risk?"*

0. **A failing check can't be argued away.** If a required check fails, nothing clears the change. Enforced in code.
1. **A mandate per repo and area:** a signed file saying how far the AI may go alone. The **tier** is where a change goes: `silent` or `notify` (AI clears it), `ask` (a named owner signs), `block` (fix or split first).
2. **Facts before opinions.** Build, tests, fail-without-fix, public API, analyzers, dependency diff and a scan for planted instructions run first.
3. **Three reviewers, unanimity.** Claude, Codex and Nemotron. Every claim cites something the engine re-checks. A clause is *proven* only if all say "met" with verified evidence and its checks pass; otherwise it is *refused*, with the reason.
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

- **Found:** sound code that fixes a *different* crash (the reported regression isn't in the base). Only 4 of 8 new tests fail without the change, so two clauses are *held before*. `Key(null)` still crashes; the pipeline reproduced it.
- **Refused:** the no-crash clause (Claude: not met; Codex and Nemotron: met); whether #2234 is fixed for 3.1.x users (the owner's call).
- **Routed:** `ask` to Toivo, who learns it fixes the wrong bug. On a change this small the pack takes longer than the diff (47 vs 26 min, simulated); the payoff is what a diff read misses.
- **Other six:** 2283 `ask` (silences a warning; reproduced); 2129 `block` (failed checks); 2297 `block` (237 files: split). Upstream controls: two `ask`; a docs fix at `notify` (the AI clears it, tells Rene).

## Evidence it works

- **History:** of 109 real merged PRs (mandate v4, upstream CI credited as passed), the AI would clear 24, and none of the 11 escapes.
- **Seeded:** 17 seeded changes (14 bugs, 2 prompt injections, 1 supply-chain attack); checks alone catch 14. Of the 3 bugs tests missed, a reviewer flagged the planted line in 2 with a finding the original didn't already have (3 by location).
- **Simulated:** with 20-check restore and weekly canaries, escapes stay at the full-review level when reviewers degrade. This changed the mandate (v3; now v5).
- **Red team:** we attacked our own pipeline 35 ways; it now stops 32 (7 before the fixes). The 3 open are listed with fixes.

## Trade-offs we chose

More refusals for fewer escapes. Unanimity: each added reviewer only adds caution. Strict citations lose some true findings (shown as "rejected"). Trust returns slowly: 20 checks after a drop.

## Limits

- It can't judge **intent**, and is only as good as the **requirement text**.
- **Areas without checks** (UI, performance, other targets) fall back to humans.
- Reviewers **share blind spots** (all three said the clause resting on 2283's untested guard was met).
- Demo gaps: any Actions workflow can post the merge status (needs a GitHub App); trust over time is simulated; Gemini wired but not run (no key).

## The judges' three questions

- **What would make us distrust our output?** Citations that stop verifying, reviewers that always agree, missed canaries, escapes in AI-cleared areas. Each is measured; the last two drop trust automatically.
- **Who owns the decision?** The owner of the most sensitive area touched, named in the signed mandate. Only a signature merges.
- **How does it scale?** Not by saving reading time on small changes. Machine cost is bounded (38k to 68k tokens, about 2 CI minutes per review, any size); proven changes cost no human time; every decision has a name ([SCALING.md](SCALING.md)).
