# Countersign: concept card

> **AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it can't, and a named human countersigns the rest.**

## Recommendation

Stop asking *"did a human read every line?"* Ask *"did a named human sign for what was proven, what was refused, and the risk that is left?"*

The PR review factory should work like a delegation of authority, not like a second pair of eyes:

1. **A mandate per repo and area.** A versioned file, signed by its owner, says what the AI may clear on its own (`silent`, `notify`) and what must go to a named human (`ask`) or be refused outright (`block`, with the rule that fired). The AI never approves anything; the mandate defines how far its advice can carry.
2. **Facts before opinions.** Build, targeted tests, *"do the new tests fail without the fix?"*, full suite, public-API and analyzer checks run before any model reads the diff. Models must cite those results.
3. **Independent reviewers, verified citations.** Two or more reviewers from different vendors get the same brief and no shared context. Every claim must carry evidence a machine can check (file, line, exact quote; test name and outcome; check id; requirement clause). Unverifiable claims are dropped and counted against that reviewer.
4. **Disagreement means refusal.** A requirement clause is *proven* only when every reviewer says "met" with verified evidence and its mandated checks pass. Anything else is *refused*, with the reason (`reviewers_disagree`, `cannot_determine`, `check_failed`, `thin_evidence`...). Refusals are a first-class output, not a failure.
5. **The change explains itself.** The evidence pack opens with the tier and why, then the requirement trace, what was found, what the AI refused to decide, what wasn't checked and why, and the residual risk. The owner reads a story and questions the parts that don't add up, instead of hunting through a diff.
6. **A named owner countersigns.** The owner signs the pack (Ed25519) with a decision and note; the signature, the pack hash and the mandate hash go into an append-only, hash-chained ledger.
7. **Trust is earned per area and withdrawn after escapes.** Humans spot-check changes the AI cleared. A revert or incident traced to an AI-cleared change drops that area's clearance right at once and starts probation; agreeing spot-checks earn it back.

## Principles: how it balances the five forces

| Force | Principle | Mechanism in the reference implementation |
|---|---|---|
| **Risk** | Review depth follows risk, and the risk is explainable. | Additive risk score whose every point has a one-line reason; hard mandate rules (e.g. >50 files: split it; new public API: ask). The tier is the strictest of risk, rules, trust cap and refusals. |
| **Hallucination** | No evidence, no finding. | Every citation is re-checked against the repo, the test results and the requirement text. Rejected claims stay visible in the pack and give each reviewer a measured hallucination rate. |
| **Transparency** | Every decision names its driver. | The pack lists each tier driver, each refusal with its reason, and every check with tool and version. Packs are deterministic: the same inputs rebuild the same hash. |
| **Confidence** | Confidence is never self-reported. | It comes from independent agreement plus passing checks. A model saying "high confidence" counts for nothing; a test that fails without the fix counts for a lot. |
| **Quality** | Tests have to prove they test something. | *Fail without the fix*: revert the source, keep the new tests, run them. Seeded defects (mutants) measure what the checks actually catch. |

## What it looks like on a real change

Sample: **ju26-issue-2234**, "The analyzer does not work if `SuppressSourceGeneration = true`" (requirement set `REQ-2234-*`).

- **Found:** the agent's change is sound code that fixes a *different* bug. The reported 3.1.1 regression comes from an upstream commit that isn't in this branch's base at all. Half the new tests already pass without the change (the fail-without-fix check shows 4 of 8). What the change really fixes is a crash on duplicate or mixed keys that affects all types.
- **Refused:** whether #2234 is resolved for users (depends on which release line the change targets: the owner's call); generator behaviour on duplicate keys (established only by reading code).
- **Routed:** `ask` to Toivo, owner of the generator/analyzer area, with every driver listed. No human had to read 262 lines to learn that the change's title and its effect don't match.
- The other three changes: 2283 `ask` (the guard that keeps diagnostics inside the compilation isn't exercised by any test: deleting it breaks nothing); 2129 `block` (new public API, a failing analyzer check, a project missing from the solution); 2297 `block` (237 files: split it; reviewers also found a wrong `#if` and a build break for users who already put the attribute on their resolver).

## Trade-offs we chose

- **More refusals at first, fewer escapes.** A fresh area starts with no track record, so most changes go to humans. We accept that: a refusal costs a few minutes of review, an escape costs an incident.
- **Several reviewers cost more than one.** Disagreement between vendors is the cheapest honest uncertainty signal we know of; one model's self-confidence is not.
- **Strict citations lose some true findings.** A correct point with a sloppy citation is shown as "rejected", not silently dropped, so the owner can still read it.
- **Deterministic checks cost minutes per change.** They are also the part of the evidence that can't hallucinate.

## Limits (what this does not do)

- It cannot judge **intent**: whether this is the change the product needs. The requirement and the owner carry that.
- It is only as good as the **requirement text**. A badly written requirement can be "proven" and still be wrong. 2234 shows the subtle version: a clause can hold *before* the change, so "met" doesn't mean "achieved by this change".
- **Areas without checks** (UI, performance, other target frameworks) fall back to model judgement and therefore to humans; the pack lists them as not checked.
- Reviewer **independence is partial**: models share training data. Mixing vendors and open-weight models reduces correlated blind spots but doesn't remove them.
- Trust numbers in this demo come from **simulated** spot-checks and escapes, and are labelled as such.

## The judges' three questions

- **What would make us not trust our own output?** A reviewer whose citations stop verifying; reviewers that always agree (no independent signal left); seeded defects passing as "cleared"; any escape in an area the AI cleared. Each one is measured, and each lowers the area's clearance right automatically.
- **Who owns the decision?** The named owner of the most sensitive area the change touches, as written in the signed mandate. The AI's output is advice with evidence; only a signature merges.
- **How does it scale?** Human attention goes only to what can't be proven, and the AI earns `silent`/`notify` per area as its track record grows. The pipeline is plain files plus CI jobs (running on CRACI). For confidential codebases the mandate admits only self-hostable reviewers (Nemotron, open weights), so code never leaves the client's infrastructure.
