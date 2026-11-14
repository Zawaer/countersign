# Countersign principles

Thirteen rules (0 to 12) a team could adopt on Monday. Each says what the rule is, why we hold it, how the reference implementation enforces it (file or command you can check), and what it costs. The reference implementation is a Python CLI over plain files; see [ARCHITECTURE.md](ARCHITECTURE.md) for the full contract.

The short version: **the AI gathers and checks evidence, the mandate says how far that evidence may carry, and a named human signs for the rest.**

---

## 0. A failing check can't be argued away

- **Rule.** When a check the mandate requires fails or errors, no combination of reviewer verdicts, adjudication or earned trust can prove the clause it covers or clear the change.
- **How it's enforced.** `decide.principle_zero` lists every mandated check (an area's `checks`, a clause's checks) whose status is `fail` or `error`, adds a driver at `ask` that nothing can lower, and asserts no such clause is `proven` or `held_before`; the signed mandate's `mandated-check-failed` rule raises a failure to `block`. The floor is in code, so it holds even if the mandate's rules are edited. Tested over every verdict combination, with and without adjudication, with every area's trust cap at `silent` (`tests/test_engine_rules.py`).

## 1. Every change has one named owner, and only that person can sign it

- **Why.** "Someone on the team approved it" is an unowned merge. A name makes the decision answerable.
- **How it's enforced.** Each area in [`mandate/messagepack.mandate.yaml`](../mandate/messagepack.mandate.yaml) has an `owner`. A change's owner is the owner of the most sensitive area it touches; other area owners get an FYI. `countersign sign` refuses anyone but the pack's named owner, and checks the signature against `keys/<owner>.pub`.
- **What it costs.** Someone has to own every area, including the dull ones. A change across many areas lands on the owner of the riskiest one, who may not know the rest.

## 2. The AI advises; only a signature merges

- **Why.** Tieto: "The AI said it was fine" is not accepted. The AI can be wrong in confident language, so its output must never be the approval.
- **How it's enforced.** The AI's output is a tier recommendation (`silent`, `notify`, `ask`, `block`) inside an evidence pack. `silent`/`notify` are clearance rights the *owner* delegated in the signed mandate, logged and spot-checked (rule 11). `ask` needs a signature. A `block` pack only accepts `reject` or `request-changes`.
- **What it costs.** Owners sign more often than they would under "AI approves small stuff". That is the point, but it is time.

## 3. Write the AI's authority down: a signed, versioned mandate per repo and area

- **Why.** Who may clear what is a policy decision with an owner, not a property of a script. A written mandate can be reviewed, versioned and audited.
- **How it's enforced.** The mandate holds areas (paths, sensitivity, `max_ai_tier`, required checks), hard rules, risk weights, the reviewer panel and confidentiality. The owner signs it (`countersign sign-mandate --as Toivo`, logged as a `mandate_change` ledger entry). Every pack records the mandate's sha256. If the file changes after signing, the `mandate-not-signed` rule fires and nothing clears below `ask`.
- **What it costs.** Someone writes and maintains the mandate. A new repo starts with no track record, so its mandate should start strict.

## 4. Facts before opinions

- **Why.** Tool output can't hallucinate; model output can. Running checks first lets the models argue about evidence instead of inventing it.
- **How it's enforced.** Stage 1 writes `evidence/<change>/facts.json`: diff (source / test / generated split), build, targeted tests, fail-without-fix, full suite, public-API and analyzer checks, `deps.delta` (SBOM diff of the NuGet graph, base vs head) and `injection_scan` (text planted for AI reviewers, including invisible Unicode), with tool versions and logs. If `injection_scan` fails, the R-INJECT rule blocks the change and no reviewer verdict counts: the reviewers read the planted text. Both seeded injection changes (2283-inject, 2234-inject) are blocked this way. Reviewers get the facts and must cite them. A check that errored or was skipped is never treated as a pass.
- **What it costs.** Builds and test runs take minutes per change, and some areas (UI, performance, other target frameworks) have no check yet.

## 5. New tests must fail without the fix

- **Why.** A test that passes on the old code doesn't test the change. This was the single most informative check we ran (see [LESSONS.md](LESSONS.md)).
- **How it's enforced.** `tests.fail_without_fix`: revert the source files to base, keep the new tests, run them, and report per test. It is a mandated check in the generator/analyzer area. On 2234 it showed 4 of 8 new analyzer tests and 4 of 4 new runtime tests pass without the change ([facts.json](../evidence/2234/facts.json)). A clause that is met but whose tests already pass without the fix is `held_before`: met, but not achieved by this change. It is not proven, routes at least `notify` and appears in residual risk (2234 F1 and F2).
- **What it costs.** A second build and test run per change; for changes that add files (2129), reverting needs care.

## 6. No evidence, no finding

- **Why.** Tieto does not accept "confidence without evidence". A claim a machine can't check is a claim nobody can own.
- **How it's enforced.** Every reviewer claim carries evidence items: `code` (file, line, exact quote at head or base), `test` (name and outcome, matched against facts.json), `check` (id), `requirement` (quote from the clause). The engine re-checks each one (`countersign/verify.py`). A finding with zero verified items is rejected, kept in the pack under "Rejected: unsupported claims", and counted against that reviewer. An issue-page quote is never counted, because the pipeline runs offline and can't confirm it. Review JSON is treated as untrusted input: only substantive evidence counts (code at head or base in a file the change touches, a test or check with a matching outcome), so a reviewer can't prove a clause by quoting the clause. A bug a reviewer claims to have reproduced becomes an executable repro, `repro.<reviewer>.<finding>`, run by the pipeline on head and base (2283 C1 and 2234 C2 are both reproduced). Verified major findings carry forward to the next review pass unless re-raised or refuted with verified evidence.
- **What it costs.** A true finding with a sloppy citation is lost from the verdict. It stays visible as rejected so the owner can still read it.

## 7. A clause is proven only when every reviewer agrees with verified evidence; anything else is a refusal with a reason

- **Why.** Self-reported confidence is worthless; independent agreement plus passing checks is a signal. With unanimity, every reviewer we add can only make the AI more cautious. A majority vote would let two reviewers outvote a third reviewer's verified objection.
- **How it's enforced.** Per requirement clause: `proven` only if every participating reviewer says `met` with at least one verified item and the clause's checks pass. Otherwise `refused`, with every reason that applies: `not_met`, `reviewers_disagree`, `cannot_determine`, `thin_evidence`, `check_failed`, `check_not_run`, `missing_review`, `adjudicator_dispute`. A reviewer that didn't run is `missing_review`; it can't silently drop out. Any refused clause routes to at least `ask`. A reviewer refusal (a question it declined to decide) routes `ask` if it names a clause, is marked blocking, or touches a mandated check or a sensitive term such as security or runtime; otherwise it routes `notify`, so the owner is still told. Without that split, every change would ask, because every reviewer declines something peripheral.
- **What it costs.** More refusals, so more human routing, especially early. One failed API call refuses every clause of that change until it is re-run.

## 8. A second opinion can explain a dispute, never settle it in favour of clearing

- **Why.** A tie-breaker that can clear is a single model approving the change.
- **How it's enforced.** The adjudicator (Gemini in the mandate's reviewer registry) reads only disputed items, with both sides' cited evidence and the engine's verification results, and says which claims the evidence supports. `decide.apply_adjudication` can only add reasons and `ask` drivers; it asserts that no refused clause becomes proven.
- **What it costs.** A third vendor's cost and latency on disputed changes, for advice that never lowers a tier. Run in CI on the disputes in 2234 and 2283 (it backed Claude's objection on 2234 N1, so the clause stayed refused and went to the owner).

## 9. Review depth follows risk, and the risk can be explained line by line

- **Why.** Tieto: low-risk changes get light checks, high-risk ones a full read, and no "risk score nobody can explain".
- **How it's enforced.** The risk score is additive; every factor prints its points and a one-line reason, including zeros (pack section "Risk score"). Weights live in the mandate, not in code. Hard rules sit on top (more than 50 files: `block`, split it; public API changed: `ask`; a mandated check failed: `block`). The tier is the strictest of the risk band, fired rules, the area's trust cap and refusals, and the pack lists every driver.
- **What it costs.** Weights are judgement calls. Size rules count generated files today, which made 2297 look bigger than its source change (see [LESSONS.md](LESSONS.md)).

## 10. The pack says what was not checked, and why

- **Why.** The owner signs for the gaps too. A gap nobody wrote down is a risk nobody accepted.
- **How it's enforced.** Every pack has "What was not checked, and why" (checks deliberately not run, from facts.json) and the mandate's standing `known_gaps` (other target frameworks, performance, semantic intent, provenance). Both feed "Residual risk", which is what the owner's sign-off statement names.
- **What it costs.** Honest packs are longer, and the list of standing gaps is uncomfortable to read.

## 11. Trust is earned per area and withdrawn after an escape

- **Why.** Tieto: humans spot-check the AI reviewer, track what it misses, and trust is earned per area and withdrawn after escapes.
- **How it's enforced.** Trust stages in the signed mandate (since v3; unchanged in the current v6): ask -> notify -> silent, never above the area's cap. Climbing to `notify` takes 20 agreeing spot-checks in a row, 95% agreement over the last 40 and no escape in the last 50 changes; `silent` takes 40, 98% of 80 and 100. One stage is lost on an escape on an AI-cleared change (`countersign escape`), a disagreeing spot-check (`countersign spotcheck`) or a canary run where the reviewers missed a seeded bug. A reviewer model or prompt version that is not released holds every area at `ask`. `countersign trust` shows each area's stage and why. We moved from 3 to 20 checks because a simulation showed 3 restored clearance within days after reviewers degraded ([MEASUREMENT.md](MEASUREMENT.md), decision D13).
- **What it costs.** Someone has to spot-check changes nobody would otherwise look at, an escape has to be traced back to a change, and canaries cost model calls every week. Clearance comes back slowly. In this demo the spot-checks, escapes and canaries over time are simulated and labelled.

## 12. Every signature is bound to the exact evidence it covers

- **Why.** A signature on "the PR" is vague. A signature on a pack hash says exactly what the owner saw.
- **How it's enforced.** pack.json is deterministic (same inputs, same sha256). `countersign sign` rebuilds the pack first and refuses if it no longer matches ("out of date: re-run review"). The ledger entry holds the pack hash, the mandate hash, the decision and note, and an Ed25519 signature; entries are hash-chained. `countersign verify-ledger` re-checks every hash and signature and exits non-zero on the first edited line.
- **What it costs.** Key management. Rotation and revocation are out of scope here.

---

## Two policies that sit next to the rules

- **Measure outcomes, not activity.** The replay (`countersign replay`) reports the share routed to humans, findings verified and rejected per reviewer, seeded defects caught, escapes and spot-check agreement. Review-time savings come from a reading model in the mandate and are always marked `simulated`. Results: [measurement/results.md](../measurement/results.md) and [MEASUREMENT.md](MEASUREMENT.md).
- **Code only goes where the mandate allows.** `confidential: true` (repo or area) admits only `self_hostable` reviewers (Nemotron, open weights) and the runner refuses to send code to a vendor-hosted endpoint. MessagePack-CSharp is open source, so it is not confidential here.

---

## Mapping to Tieto's brief

### "How humans build trust they can stand behind"

| Tieto's statement | Countersign mechanism | Rule |
|---|---|---|
| A named engineer owns each change and signs off on it. | Area owners in the signed mandate; change owner = owner of the most sensitive touched area; only that person's Ed25519 key can sign the pack; the signature goes into the ledger. | 1, 12 |
| The AI review is advice with evidence, never the approval itself. | Output is a tier recommendation in an evidence pack; `ask` needs a signature; `block` can't be accepted; the adjudicator can never clear. | 2, 8 |
| Evidence is traceable to a requirement, so the owner can check it quickly. | Requirement trace table per clause (`REQ-2234-F1`...), with each reviewer's verdict, how many of its citations verified, the clause's checks, and the refusal reasons. | 6, 7 |
| Depth of human review follows risk. | Explainable additive score + hard rules + area caps; four tiers from `silent` (logged) to `block` (split or fix first). | 9 |
| Humans spot-check the AI reviewer, and track what it misses. | `spotcheck` events grade the AI's own recommendation; rejected claims and refusals are counted per reviewer; seeded defects measure what checks and reviewers miss. | 6, 11 |
| Trust is earned per area, from track record, and withdrawn after escapes. | `max_ai_tier` per area in the mandate; an escape, a disagreeing spot-check or a missed canary drops one stage; 20 agreeing spot-checks in a row climb back to `notify`. | 11 |

### "What the owner signs"

| Tieto's item | Where it is in the pack |
|---|---|
| What was checked, and by whom or what | "What was checked, and by whom": each check with status, tool and version; reviewer table with model, vendor, prompt version, verified and rejected findings, refusals. |
| What was not checked, and why | "What was not checked, and why": checks not run (from facts.json) and the mandate's standing gaps. |
| The residual risk they accept | "Residual risk": every refused clause, reviewer refusal, open finding and gap. The sign-off statement names all three items, and the ledger entry binds it to the pack hash. |

### "Not accepted"

| Tieto's item | What stops it |
|---|---|
| "The AI said it was fine." | The AI can't sign; `silent`/`notify` exist only where the owner delegated them in a signed mandate, and are spot-checked. |
| An unowned merge. | Every pack names an owner; `sign` refuses anyone else; the ledger records who signed what. |
| Confidence without evidence. | Every claim is citation-checked; unverified findings are rejected and don't move the tier; confidence comes from agreement plus checks, never from the model's own words. |
| A risk score nobody can explain. | Additive score, one printed reason per factor, weights in the signed mandate. |

### "What major vendors recommend"

| Recommendation | How we follow it |
|---|---|
| Route human attention by risk. | Tiers from the risk score, hard rules and area caps (rule 9). |
| Keep reviews fast and low-noise. | Minor findings only `notify`; rejected claims never move the tier; the pack leads with "why this tier". |
| Review with full repo context. | Reviewers get the diff, head and base files, requirements and facts; the 2234 finding came from checking git history against the issue. |
| Verify findings before posting. | Stage 3 re-checks every citation before anything reaches the pack (rule 6). |
| Measure outcomes (reverts, incidents), not review activity. | Escapes drive the trust ledger; the replay reports routing share, seeded-defect catch rate and spot-check agreement. |
