# Countersign

**Demo:** open [site/index.html](site/index.html) in a browser (it goes on GitHub Pages once the repo is public).

> **AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it can't, and a named human countersigns the rest.**

**In numbers:** replayed on 109 real merged MessagePack-CSharp PRs (signed mandate v4, upstream CI credited as passed), the AI would have cleared 24 of them, and none of the 11 that later needed a revert or a follow-up fix. On Tieto's four agent-written changes it sent all four to a named owner, each with its reason.

**Three words used throughout:**
- **Mandate:** a signed, versioned file per repo that says, area by area, how far the AI may go alone and who owns each area.
- **Tier:** where a change goes. `silent` (the AI clears it, logged), `notify` (the AI clears it and tells the owner), `ask` (the owner must sign), `block` (fix or split first).
- **Escape:** a change that was merged and later needed a revert or a follow-up fix.

## How it works

0. **A failing check can't be argued away.** If a check the mandate requires fails, no reviewer vote or track record can clear the change. This is enforced in code.
1. **Facts first.** Build, tests, "do the new tests fail without the fix?", public API, analyzers, dependency changes and a scan for text planted to steer AI reviewers run before any model reads the diff.
2. **Independent reviewers, unanimity.** Claude and Nemotron review separately. Every claim must cite a file line, test, check or requirement clause, and the engine re-checks it. A clause is proven only if every reviewer says "met" with verified evidence and its checks pass; anything else is refused, with the reason.
3. **A rubber stamp can't clear anything.** Codex reviews too, and it is our control: given passing tests, it said every clause was met and found nothing (0 verified findings; it missed 6 verified majors the others found). Because one reviewer's "all good" never outvotes another's verified objection, that stamp cleared nothing ([R1](docs/FAILURE_MODES.md)).
4. **Bugs a reviewer claims are re-run.** A reviewer's probe test becomes a repro check that the pipeline runs on the old and new code.
5. **The change explains itself.** An evidence pack: tier and why, requirement trace, findings, refusals, what was not checked, residual risk.
6. **A named owner countersigns.** An Ed25519 signature over the pack's hash, in a hash-chained ledger.
7. **Trust is earned per area.** An area moves from ask to notify after 20 agreeing spot-checks in a row, and to silent after 40. An escape, a disagreeing spot-check or a missed seeded-bug canary drops the area one stage. A new reviewer model or prompt version starts again at ask.

One page: [docs/CONCEPT_CARD.md](docs/CONCEPT_CARD.md). Rules a team could adopt: [docs/PRINCIPLES.md](docs/PRINCIPLES.md).

## Walkthrough: change 2234

Branch `ju26-issue-2234`, written by an agent: "The analyzer does not work if `SuppressSourceGeneration = true`". 4 files, +262 −4. Requirements `REQ-2234-F1`, `F2`, `N1`, `N2` in [requirements/2234.yaml](requirements/2234.yaml).

1. **Route.** `countersign route --all` prints one line per change. 2234 goes to `ask`, owner Toivo, because of a verified finding: the issue's regression is not on this base, and the change fixes a different crash.
2. **Open the pack.** [packs/2234/pack.md](packs/2234/pack.md) ([html](packs/2234/pack.html)). The first screen is the tier, the owner and why.
3. **Read the facts.** Build passes, the 8 new analyzer tests pass, the suite passes 175 of 175. But with the fix reverted, only 4 of the 8 new tests fail, and 0 of the 4 new runtime tests fail. So clauses F1 and F2 are marked **held before**: met, but already true before this change, so the change did not achieve them ([facts.json](evidence/2234/facts.json)).
4. **What the AI found.** Claude C1 (major): the reported regression comes from upstream commit `1a74a620`, which is not in this branch's base. Claude C2 (minor): `Key(null)` on a positional record still crashes the analyzer. The pipeline ran Claude's probe test itself: it fails on the new and old code and passes on a control branch, so the crash is reproduced, not just claimed.
5. **What the AI refused to decide.** N1 ("must not crash on invalid contracts"): Claude says not met, Codex and Nemotron say met, so it is not proven (the pack labels it NOT MET). N2: Codex said met without verified evidence. Nemotron declined to judge the runtime library on other targets, and security; both name sensitive topics, so they route to the owner. Four more refusals are out of scope for this change (among them whether it fixes #2234 for 3.1.x users, where nothing was built) and sit in one folded line.
6. **What was not checked.** Other .NET targets, the runtime library's tests, benchmarks, and the mandate's standing gaps. The risk score prints every point with its reason.
7. **Sign.** `countersign sign 2234 --as Toivo --decision request-changes --note "..."`. Only the named owner's key is accepted, and signing is refused if the pack changed. Toivo's private key is not in the repo.
8. **Try to tamper.** Copy `ledger/` to `/tmp/t`, edit one line, run `countersign verify-ledger --inputs /tmp/t`: `LEDGER INVALID: line 2: content does not match its hash`.

What the owner learns from the pack: the change fixes a different bug, half its new tests prove nothing, the reviewers disagree on the no-crash clause, and a `Key(null)` crash remains. What they decide: request changes or accept that risk, under their name.

The pack does not save reading time here. On small changes (2234, 2283) it takes longer to read than the diff (47 vs 26 minutes on 2234, simulated reading model). The payoff is accountability and catching what a diff read misses: a green, fully tested change that fixes the wrong bug. Time is saved only on large changes (2129, 2297) and on changes the AI clears.

## All seven real changes

Four were written by an agent (Tieto's branches). Three are small merged upstream PRs we added as controls, to show that a low-risk change can go through.

| Change | Size | Tier | The deciding reason |
|---|---|---|---|
| [2283](packs/2283/pack.md) | 4 files, +225 −3 | `ask` | The fix silences a warning (MsgPack003) that the old code reports. Claude found it; the pipeline reproduced it. |
| [2234](packs/2234/pack.md) | 4 files, +262 −4 | `ask` | It fixes a different crash than the issue reports. |
| [2129](packs/2129/pack.md) | 28 files, +1034 −9 | `block` | New public API with no API tracking, a new analyzer warning and a project missing from the solution: two failed checks in a critical area push the risk score into the block band. |
| [2297](packs/2297/pack.md) | 237 files (228 generated), +1383 −9 | `block` | More than 50 files: split it. A reviewer also found a wrong `#if` that leaves .NET Framework and netstandard users without the attribute. |
| [up-2022](packs/up-2022/pack.md) | 2 files, +29 −0 | `ask` | All clauses proven, but Nemotron refused to judge runtime deserialization security, a topic on the mandate's list of terms that always ask. |
| [up-1934](packs/up-1934/pack.md) | 6 test files, +26 −22 | `ask` | All clauses proven, but Nemotron refused to judge the build on other target frameworks, and `build` is a mandated check. |
| [up-1967](packs/up-1967/pack.md) | 1 doc file, +1 −1 | `notify` | A one-line README anchor fix. All three reviewers agree and the anchor check passes, so the AI clears it and tells Rene. |

6 of 7 go to a human. The AI clears only the docs fix.

## Measurement

Details and definitions: [docs/MEASUREMENT.md](docs/MEASUREMENT.md).

- **History (real).** 109 merged upstream PRs, routed from their diffs by the signed mandate (v4; re-run Sat 06:05, same result as under v2; upstream CI credited as passed). 11 were later reverted or needed a follow-up fix. The AI would have cleared 24 PRs, and **0 of the 11 escapes** ([measurement/history/results.md](measurement/history/results.md)).
- **Seeded changes (real).** We seeded 17 changes: 14 one-line bugs, 2 prompt injections and 1 supply-chain attack. Checks alone catch 14 of 17 (11 of 14 bugs; both injections, caught by the planted-text scan; the supply-chain attack, caught by the dependency diff). The 16 with reviews all go to a human (the supply-chain attack has no reviews yet). Of the 3 bugs every test missed, a reviewer flagged the planted line in 2 of 3 with a finding the unmutated original did not already have at that line (3 of 3 counting any finding at that line); Nemotron alone in 2 of 3. It missed the removed `ContainsSyntaxTree` guard on 2283-mut1, the guard all three reviewers accepted (REQ-2283-F3 met) on the original.
- **Review time (simulated).** A reading model in the mandate, not a stopwatch: about 440 minutes to read all seven diffs, 185 with the packs. On small changes the pack takes longer than the diff.
- **Trust over time (simulated).** When reviewers get worse, the old rule (3 agreeing spot-checks restore clearance) let escapes rise. 20 checks plus weekly canaries brought them back to the full-review level. That result changed the signed mandate (v3; the current v4 keeps these trust stages and adds supply-chain rules).

## Limits

- It can't judge **intent**: whether this is the change the product needs.
- It is only as good as the **requirement text**.
- **Breadth equals the checks.** We have checks for a C# library on net8.0/Linux. Frontend, performance and other targets fall back to humans and are listed as not checked.
- **Reviewers share blind spots.** On the original 2283, all three reviewers said REQ-2283-F3 was met, though no test exercises the guard it depends on.
- **The merge gate can be forged in the demo.** Any GitHub Actions workflow in the demo repo can post the required status. The fix is a dedicated GitHub App ([docs/security/TRIAGE.md](docs/security/TRIAGE.md), T1).
- Gemini is wired but not run (no key), so disputes in the packs say "not adjudicated". CRACI's own SBOM and network trace are wired but skipped: no CRACI API token is set. Key rotation and revocation are out of scope.

## Run it

Python 3.11+ and git. Offline, no API keys: it reads the recorded facts and reviews.

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]'
git clone https://github.com/te-industry-tech-office/junction26-messagepack-csharp /tmp/mp
countersign route --all --repo /tmp/mp   # tier per change
countersign review 2234 --repo /tmp/mp   # rebuild packs/2234
countersign verify-ledger                # check every signature
countersign trust                        # trust stage per area
pytest -q
```

## What is real, recorded and simulated

- **Real:** branches, diffs, every build and test result in `evidence/` (with logs), repro checks, seeded bugs, verification, routing, packs, signatures, the ledger, the history replay.
- **Recorded:** Claude and Codex reviews, run in agent sessions and saved verbatim in `reviews/`. Nemotron reviews were run live by the CI job on CRACI, with the request and response saved under `reviews/<change>/raw/`.
- **Simulated, and labelled:** spot-checks, escapes and canaries over time, and every review-time number.
- **Placeholder:** the requirement sets. We derived them from each upstream issue and marked them `official: false`.

## Tech tracks

- **Codex (OpenAI):** the rubber-stamp control on all seven changes. Its second pass, given passing tests, said every clause was met and found nothing (0 verified findings, 6 verified majors missed); it shows why one reviewer can't clear a change (R1), and the rules are built so it can't ([docs/CODEX_LOG.md](docs/CODEX_LOG.md)). Codex also did a security review of our own pipeline; the triage confirmed 8 issues (4 Codex found, 4 it missed) and fixed or mitigated all but the merge-gate hole T1, which is still open ([docs/security/TRIAGE.md](docs/security/TRIAGE.md)).
- **Gemini (Google):** the adjudicator. It reads only disputed items with both sides' evidence; the engine never lets it clear anything (`decide.apply_adjudication`). Wired but not run (no key).
- **Nemotron (NVIDIA, open weights):** the second independent reviewer (with Claude), run live in CI on all seven real changes and on the 16 seeded changes that have reviews (all but the supply-chain attack). Of the 3 seeded bugs every test missed, it flagged the planted line in 2. It is the only reviewer marked self-hostable, so it is the one a repo marked confidential may use.
- **CRACI:** the pipeline and the reviewer jobs run on CRACI runners under a deny-by-default network policy. The facts job also writes `deps.delta` (a CycloneDX SBOM diff of the NuGet graph, base vs head; passes on all four changes, fails on a seeded attack on 2283) and `build.egress` (copies the build's network policy into the evidence; wired, no committed run yet). A `craci` job would add CRACI's own SBOM and network trace (`craci.sbom`, `craci.network`); no CRACI API token is set, so both are skipped. See [docs/CI.md](docs/CI.md).

More: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/PR_FLOW.md](docs/PR_FLOW.md) (GitHub flow: merge blocked until a valid countersignature), [docs/DECISIONS.md](docs/DECISIONS.md), [docs/FAILURE_MODES.md](docs/FAILURE_MODES.md), [docs/LESSONS.md](docs/LESSONS.md), [docs/COSTS.md](docs/COSTS.md).

Team: Toivo and Rene.
