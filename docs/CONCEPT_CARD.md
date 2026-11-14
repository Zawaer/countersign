# Countersign: concept card

> **AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it can't, and a named human countersigns the rest.**

## Recommendation

Stop asking *"did a human read every line?"* Ask *"did a named human sign for what was proven, refused, and left at risk?"*

0. **A failing check can't be argued away.** If a required check fails, nothing clears the change. Enforced in code.
1. **A mandate per repo and area:** a signed file saying how far the AI may go alone. The **tier** is where a change goes: `silent` or `notify` (AI clears it), `ask` (a named owner signs), `block` (fix or split first).
2. **Facts before opinions.** Build, tests, fail-without-fix, public API, analyzers, dependency diff and a scan for planted instructions run first.
3. **Three reviewers, unanimity.** Claude, Codex and Nemotron. Every claim cites something the engine re-checks. A clause is *proven* only if all say "met" with verified evidence and its checks pass; otherwise it is *refused*, with the reason.
4. **Claims become checks.** A bug a reviewer reproduced becomes a repro test the pipeline runs on old and new code.
5. **The change explains itself.** An evidence pack: tier and why, trace, findings, refusals, gaps, residual risk.
6. **A named owner countersigns** the pack's hash (Ed25519) into a hash-chained ledger.
7. **Trust is earned per area.** ask -> notify after 20 agreeing spot-checks in a row, -> silent after 40. An **escape** (a merged change later reverted or fixed), a disagreeing spot-check or a missed canary drops one stage. A new reviewer model or prompt starts at ask.

## Principles: the five forces

| Force | Principle | Mechanism |
|---|---|---|
| Risk | Depth follows risk, explainably. | Additive score, a printed reason per point; hard rules. Tier = strictest driver. |
| Hallucination | No evidence, no finding. | Every citation re-checked; rejected claims stay visible and count against the reviewer. Planted instructions void all verdicts (R-INJECT). |
| Transparency | Every decision names its driver. | Same inputs, same pack hash. |
| Confidence | Never self-reported. | Agreement plus passing checks. |
| Quality | Tests must prove they test something. | Fail-without-fix per test; a clause whose tests already passed before is *held before*: met, not achieved by the change. |

## On a real change: ju26-issue-2234

- **Found:** sound code that fixes a *different* crash; the reported regression comes from a commit not in the base. Only 4 of 8 new tests fail without the change, so two clauses are *held before*. `Key(null)` still crashes the analyzer; the pipeline reproduced it.
- **Refused:** the no-crash clause (Claude: not met; Codex and Nemotron: met); whether #2234 is fixed for 3.1.x users (the owner's call).
- **Routed:** `ask` to Toivo, without anyone reading 262 lines.
- **Other six:** 2283 `ask` (silences a warning; reproduced); 2129 `block` (failed checks); 2297 `block` (237 files: split). Upstream controls: up-2022, up-1934 `ask` (one Nemotron refusal each); up-1967, a docs fix, `notify`: the AI clears it and tells Rene.

## Evidence it works

- **History:** of 109 real merged PRs (mandate v4, upstream CI credited as passed), the AI would clear 24, and none of the 11 escapes.
- **Seeded:** 17 seeded changes (14 one-line bugs, 2 prompt injections, 1 supply-chain attack); checks alone catch 14 of 17. Of the 3 bugs tests missed, a reviewer flagged the planted line in 2 of 3 with a finding the original did not already have (3 of 3 by location); Nemotron alone in 2 of 3.
- **Simulated:** with 20-check restore and weekly canaries, escapes stay at the full-review level when reviewers degrade. This changed the mandate (v3; now v4).

## Trade-offs we chose

More refusals for fewer escapes (a refusal costs minutes, an escape an incident). Unanimity: each added reviewer can only add caution. Strict citations lose some true findings (they stay visible as "rejected"). Trust returns slowly: 20 checks after a drop.

## Limits

- It can't judge **intent**, and is only as good as the **requirement text**.
- **Areas without checks** (UI, performance, other targets) fall back to humans.
- Reviewers **share blind spots** (all three said the clause resting on 2283's untested guard was met).
- Demo gaps: any Actions workflow can post the merge status (needs a GitHub App); trust over time is simulated; Gemini is wired but not run (no key); CRACI's own SBOM and network trace are skipped (no CRACI token).

## The judges' three questions

- **What would make us distrust our output?** Citations that stop verifying, reviewers that always agree, missed canaries, any escape in an AI-cleared area. Each is measured; the last two drop trust automatically.
- **Who owns the decision?** The owner of the most sensitive area touched, named in the signed mandate. Only a signature merges.
- **How does it scale?** Humans see only what can't be proven; areas earn clearance from their record. Plain files plus CI jobs. Confidential code goes only to self-hostable reviewers (Nemotron).
