# Countersign: concept card

> **AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it can't, and a named human countersigns the rest.**

## Recommendation

Stop asking *"did a human read every line?"* Ask *"did a named human sign for what was proven, what was refused, and the risk left?"* Review becomes delegated authority, not a second pair of eyes:

1. **A mandate per repo and area.** A versioned file, signed by its owner, says what the AI may clear alone (`silent`, `notify`), what goes to a named human (`ask`) and what is refused (`block`, citing the rule). The AI never approves.
2. **Facts before opinions.** Build, tests, "do the new tests fail without the fix?", public-API and analyzer checks run first; models must cite them.
3. **Independent reviewers, checked citations.** Reviewers from different vendors, same brief, no shared context. Every claim cites something a machine re-checks (file:line + quote, test outcome, check id, requirement clause); claims that fail count against the reviewer.
4. **Disagreement means refusal.** A requirement clause is *proven* only if every reviewer says "met" with checked evidence and its checks pass. Anything else is *refused*, with the reason.
5. **The change explains itself.** The evidence pack opens with the tier and why, then the requirement trace, findings, refusals, what wasn't checked, and the residual risk.
6. **A named owner countersigns.** The owner signs the pack (Ed25519) into an append-only, hash-chained ledger.
7. **Trust is earned per area and withdrawn after escapes.** An escape (revert, incident) drops that area's clearance right at once; agreeing spot-checks earn it back.

## Principles: the five forces

| Force | Principle | Mechanism |
|---|---|---|
| Risk | Depth follows risk; the risk is explainable. | Additive score with a printed reason per point; hard rules (>50 files: split; public API: ask). Tier = strictest driver. |
| Hallucination | No evidence, no finding. | Every citation re-checked; rejected claims stay visible and count against the reviewer. |
| Transparency | Every decision names its driver. | Pack lists each driver, refusal reason and check with tool version; same inputs, same pack hash. |
| Confidence | Never self-reported. | Comes from independent agreement plus passing checks. |
| Quality | Tests must prove they test something. | Fail-without-fix: revert the source, keep the new tests, run them. Seeded defects measure the checks. |

## On a real change: ju26-issue-2234 (`REQ-2234-*`)

- **Found:** sound code that fixes a *different* bug. The reported 3.1.1 regression comes from an upstream commit that isn't in the branch's base; 4 of the 8 new tests pass without the change; one invalid contract still crashes the analyzer.
- **Refused:** whether #2234 is fixed for 3.1.x users (nothing was built on that line: the owner's call); the no-crash clause, because one reviewer says met and the other, with a reproduction, says not.
- **Routed:** `ask` to Toivo, owner of the generator/analyzer area. Nobody had to read 262 lines to learn that the title and the effect don't match.
- **The other three:** 2283 `ask` (the fix silences a warning users relied on, and a guard it needs is untested); 2129 `block` (new public API, a new analyzer warning, a project missing from the solution); 2297 `block` (237 files: split it; a reviewer also found a wrong `#if` that skips older .NET targets).

## Trade-offs we chose

- **More refusals, fewer escapes.** A new area has no track record, so most changes go to humans. A refusal costs minutes; an escape costs an incident.
- **Several reviewers cost more than one.** Cross-vendor disagreement is the cheapest honest uncertainty signal we know.
- **Strict citations lose some true findings.** They are shown as "rejected", not deleted, so the owner can still read them.
- **Checks cost minutes per change.** They are the part of the evidence that can't hallucinate.

## Limits

- It can't judge **intent**: whether this is the change the product needs.
- It is only as good as the **requirement text**. A clause can hold *before* the change (2234), so "met" isn't "achieved by this change".
- **Areas without checks** (UI, performance, other targets) fall back to humans and are listed as not checked.
- Reviewer **independence is partial**: models share training data.
- Trust numbers in this demo come from **simulated** spot-checks and escapes, and say so.

## The judges' three questions

- **What would make us distrust our output?** Citations that stop verifying, reviewers that always agree, seeded defects passing as cleared, any escape in an AI-cleared area. Each is measured; an escape lowers clearance automatically.
- **Who owns the decision?** The owner of the most sensitive area touched, named in the signed mandate. Only a signature merges.
- **How does it scale?** Humans see only what can't be proven, and the AI earns `silent`/`notify` per area from its record. Plain files plus CI jobs. For confidential code the mandate admits only self-hostable (open-weight) reviewers.
