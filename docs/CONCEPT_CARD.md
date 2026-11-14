# Countersign: concept card

> **AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it can't, and a named human countersigns the rest.**

## Recommendation

Stop asking *"did a human read every line?"* Ask *"did a named human sign for what was proven, what was refused, and the risk left?"*

0. **A failing check can't be argued away.** If a required check fails, nothing clears the change. Enforced in code.
1. **A mandate per repo and area.** A signed, versioned file says how far the AI may go alone. The **tier** is where a change goes: `silent` or `notify` (AI clears it), `ask` (a named owner signs), `block` (fix or split first).
2. **Facts before opinions.** Build, tests, "do the new tests fail without the fix?", public API, analyzers, dependency diff and a scan for text planted for AI reviewers run first.
3. **Three reviewers, unanimity.** Claude, Codex and Nemotron, no shared context. Every claim cites something the engine re-checks. A clause is *proven* only if all say "met" with verified evidence and its checks pass. Otherwise it is *refused*, with the reason.
4. **Claims become checks.** A bug a reviewer reproduced becomes a repro test the pipeline runs on old and new code.
5. **The change explains itself.** The pack: tier and why, requirement trace, findings, refusals, what wasn't checked, residual risk.
6. **A named owner countersigns** the pack's hash (Ed25519) into a hash-chained ledger.
7. **Trust is earned per area.** ask -> notify -> silent after 20 agreeing spot-checks. An **escape** (a merged change later reverted or fixed), a disagreeing spot-check or a missed canary drops one stage. A new reviewer model or prompt starts at ask.

## Principles: the five forces

| Force | Principle | Mechanism |
|---|---|---|
| Risk | Depth follows risk; the risk is explainable. | Additive score, one printed reason per point; hard rules (>50 files: split; failed check: block). Tier = strictest driver. |
| Hallucination | No evidence, no finding. | Every citation re-checked; rejected claims stay visible and count against the reviewer. Planted instructions void all verdicts (R-INJECT). |
| Transparency | Every decision names its driver. | Pack lists each driver, refusal and check; same inputs, same pack hash. |
| Confidence | Never self-reported. | Independent agreement plus passing checks; reviewers' bugs re-run by the pipeline. |
| Quality | Tests must prove they test something. | Fail-without-fix per test; a clause whose tests already passed before is *held before*: met, not achieved by the change. |

## On a real change: ju26-issue-2234

- **Found:** sound code that fixes a *different* crash. The reported regression comes from an upstream commit not in the branch's base. Only 4 of 8 new tests fail without the change, so two clauses are *held before*. One invalid contract (`Key(null)`) still crashes the analyzer; the pipeline reproduced it.
- **Refused:** the no-crash clause (Claude: not met; Codex and Nemotron: met); whether #2234 is fixed for 3.1.x users (the owner's call).
- **Routed:** `ask` to Toivo. Nobody read 262 lines to learn that the title and the effect don't match.
- **The other six real changes:** 2283 `ask` (the fix silences a warning; reproduced by the pipeline); 2129 `block` (failed checks in a critical area); 2297 `block` (237 files: split it); upstream controls up-2022 and up-1934 `ask` (one Nemotron refusal each); up-1967, a one-line docs fix, `notify`: the AI clears it and tells Rene.

## Evidence it works

- **History:** on 109 real merged PRs, the AI would have cleared 24 and none of the 11 escapes.
- **Seeded:** checks alone catch 13 of 16 (11 of 14 bugs and both injections). Of the 3 bugs tests missed, Nemotron's blind review points at the planted line in 2.
- **Simulated:** with 20-check restore and weekly canaries, escapes stay at the full-review level when reviewers degrade. This changed the signed mandate (v3).

## Trade-offs we chose

- **More refusals, fewer escapes.** A refusal costs minutes; an escape costs an incident.
- **Unanimity costs clearances.** Each added reviewer can only add caution.
- **Strict citations lose some true findings.** They stay visible as "rejected".
- **Slow to regain trust.** 20 checks after a drop, by design.

## Limits

- It can't judge **intent**, and it is only as good as the **requirement text**.
- **Areas without checks** (UI, performance, other targets) fall back to humans.
- Reviewers **share blind spots**: Claude and Codex both read the untested 2283 guard as fine.
- In the demo, any Actions workflow can post the merge status; a dedicated GitHub App fixes that.
- Trust over time is **simulated** here, and says so. Gemini adjudication is wired but not yet run.

## The judges' three questions

- **What would make us distrust our output?** Citations that stop verifying, reviewers that always agree, canaries passing as cleared, any escape in an AI-cleared area. Each is measured, and each drops trust automatically.
- **Who owns the decision?** The owner of the most sensitive area touched, named in the signed mandate. Only a signature merges.
- **How does it scale?** Humans see only what can't be proven, and areas earn `notify`/`silent` from their record. Plain files plus CI jobs. Confidential code goes only to self-hostable reviewers (Nemotron).
