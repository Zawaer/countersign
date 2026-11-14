## Countersign: **NOTIFY**, owner **Rene**

**Agent-written change for https://github.com/Zawaer/countersign-messagepack-demo/tree/ju26-demo-docs1: docs: fix broken README anchor for migration notes The table of contents linked to #migration-notes-from-v1x, but the section is headed "Migration notes from prior versions", so the link went nowhere. Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>**

**Why:** The AI declined to decide 2 questions

- ✓ All 3 checks pass
- ? Reviewers left 2 questions open
- ✓ No signature needed: Rene is told

<details><summary><b>Evidence</b>: requirements, findings, refusals, checks, risk, how to sign</summary>

#### Sign-off card: change demo-docs1 is NOTIFY, owner Rene

**Agent-written change for https://github.com/Zawaer/countersign-messagepack-demo/tree/ju26-demo-docs1: docs: fix broken README anchor for migration notes The table of contents linked to #migration-notes-from-v1x, but the section is headed "Migration notes from prior versions", so the link went nowhere. Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>**

Changes 1 doc file (+1 -1) on ju26-demo-docs1 by Zawaer. Judged against 2 requirement clauses from https://github.com/Zawaer/countersign-messagepack-demo/tree/ju26-demo-docs1 (placeholder requirement set, not Tieto's official one).

**Why notify**

1. The AI declined to decide 2 questions, e.g. How GitHub actually renders and scrolls to the new anchor ([evidence](#refused))

<sub>All 4 tier drivers are under Full detail.</sub>

**Requirement trace**

| Status | Clause | Why |
|---|---|---|
| **PROVEN** | [F1](#chain-REQ-demo-docs1-F1) | All 3 reviewers say met (7 verified citations); docs.anchors pass |
| **PROVEN** | [N1](#chain-REQ-demo-docs1-N1) | All 3 reviewers say met (7 verified citations); docs.anchors pass |

**What the AI found**

- **info** [TOC entry text still says "v1.x"; heading says "prior versions"](#f-claude-C1) (Claude C1) [`README.md:22 @head`](#ev-b3299a2245) [`README.md:101 @head`](#ev-9ff1cbd8ec)
- **info** [Two other broken README anchors remain (#rpc, #author-info)](#f-claude-C2) (Claude C2) [`check docs.anchors pass`](#ev-889510bd31)

<a id="refused"></a>**What the AI refused to decide, and who should**

- <a id="refusal-1"></a>**How GitHub actually renders and scrolls to the new anchor** *Who:* docs owner (raised by Claude) <details><summary>why</summary>docs.rendering was not run; resolution relies on re-implemented slug rules plus the heading I read</details>
- <a id="refusal-2"></a>**Whether README.md renders correctly in the GitHub UI** *Who:* docs/area owner (raised by Nemotron) <details><summary>why</summary>docs.rendering was not run: Markdown was not rendered; anchors were resolved with GitHub slug rules re-implemented in upfacts.py, so visual rendering was not verified.</details>

**Not checked, and why**

- `docs.rendering`: Markdown was not rendered <details><summary>more</summary>anchors were resolved with GitHub slug rules re-implemented in upfacts.py</details>
- `docs.external_links`: links to other files or URLs were not followed (offline)
- `build`: skipped: not run: docs-only change <details><summary>more</summary>no compiled or test file changed (only README.md), so nothing was built or run</details>
- `tests.targeted`: skipped: not run: docs-only change <details><summary>more</summary>no compiled or test file changed (only README.md), so nothing was built or run</details>
- `tests.fail_without_fix`: skipped: not run: docs-only change <details><summary>more</summary>no compiled or test file changed (only README.md), so nothing was built or run</details>
- `tests.full_suite`: skipped: not run: docs-only change <details><summary>more</summary>no compiled or test file changed (only README.md), so nothing was built or run</details>
- `analyzers`: skipped: not run: docs-only change <details><summary>more</summary>no compiled or test file changed (only README.md), so nothing was built or run</details>
- Standing pipeline gaps: `other-targets`, `runtime-perf`, `semantic-intent`, `provenance`

**Residual risk you accept by signing**

- 2 questions the AI declined to decide (listed above) are yours.

<details><summary>2 more risks that do not set the tier</summary>Not run: docs.rendering, docs.external_links, build, tests.targeted, tests.fail_without_fix, tests.full_suite, analyzers · Standing pipeline gaps: other-targets, runtime-perf, semantic-intent, provenance</details>

**Rene signs** (not required: AI-cleared, spot-checks apply; accept, reject, request-changes)

```
countersign sign demo-docs1 --as Rene --decision … --note "…"
```

<details><summary>And rate the 2 verified findings (full command)</summary>

One `--finding` flag each: `accepted` (real), `rejected` (a false positive) or `unsure`, optionally `:reason`. A finding without a flag is recorded as `unrated`.

- `claude:C1` (info): TOC entry text still says "v1.x"; heading says "prior versions"
- `claude:C2` (info): Two other broken README anchors remain (#rpc, #author-info)

```
countersign sign demo-docs1 --as Rene --decision <accept|reject|request-changes> --note "..." \
  --finding claude:C1=<accepted|rejected|unsure> \
  --finding claude:C2=<accepted|rejected|unsure>
```

</details>

<details><summary>What your signature says</summary>

> I, Rene, have read what was checked and by whom, what was not checked and why, and the residual risk listed in this pack, and I own this decision.

It covers the sha256 of this pack's canonical JSON, the decision, your verdict on each finding, the time and the signer, and is appended to the hash-chained ledger.

</details>

<a id="supply-chain"></a>**Supply chain (from the build):** deps.delta not run; build egress not recorded (local run, not on CRACI)

<details><summary><b>Where the trust comes from</b> (per requirement clause)</summary>

<a id="chain-REQ-demo-docs1-F1"></a>
#### REQ-demo-docs1-F1: **PROVEN**

> The README table-of-contents entry "Migration notes from v1.x" must link to an anchor that exists in README.md and resolves to the intended section ("Migration notes from prior versions", under Installation).

- **Checks passed:** `docs.anchors` pass
- **Fails without the fix:** no cited test does
- **Claude** says met (3/5 citations verified): [`REQ-demo-docs1-F1 text`](#ev-f329bfeb4b) [`README.md:22 @head`](#ev-ed83d70a20) [`README.md:101 @head`](#ev-7ee09de8c5) [`README.md:22 @base`](#ev-fc29488a6a) [`check docs.anchors pass`](#ev-889510bd31)
- **Codex** says met (2/3 citations verified): [`README.md:22 @head`](#ev-f315fb38c4) [`README.md:101 @head`](#ev-7ee09de8c5) [`check docs.anchors pass`](#ev-889510bd31)
- **Nemotron** says met (2/2 citations verified): [`README.md:22 @head`](#ev-ed83d70a20) [`check docs.anchors pass`](#ev-889510bd31)

<a id="chain-REQ-demo-docs1-N1"></a>
#### REQ-demo-docs1-N1: **PROVEN**

> Only that link changes; no other README content and no other file is altered.

- **Checks passed:** `docs.anchors` pass
- **Fails without the fix:** no cited test does
- **Claude** says met (2/3 citations verified): [`REQ-demo-docs1-N1 text`](#ev-d71cae5f53) [`check public_api pass`](#ev-1494dc6548) [`README.md:22 @head`](#ev-f91e270150)
- **Codex** says met (2/2 citations verified): [`README.md:22 @base`](#ev-50cd6358cd) [`README.md:22 @head`](#ev-f315fb38c4)
- **Nemotron** says met (3/3 citations verified): [`README.md:22 @base`](#ev-5c6c2d8ab9) [`README.md:22 @head`](#ev-ed83d70a20) [`check docs.anchors pass`](#ev-889510bd31)

</details>

<details><summary><b>Reviewer panel</b> (who said what)</summary>
<a id="panel"></a>

| Clause | Claude | Codex | Nemotron | Result |
|---|---|---|---|---|
| REQ-demo-docs1-F1 | met | met | met | **proven** |
| REQ-demo-docs1-N1 | met | met | met | **proven** |

- **Claude** (claude-opus-5-5, Anthropic): citations 11 verified / 0 rejected; findings 2 verified / 0 rejected; 1 refusals. Only Claude raised: [C1](#f-claude-C1) info TOC entry text still says "v1.x"; heading says "prior versions", [C2](#f-claude-C2) info Two other broken README anchors remain (#rpc, #author-info)
- **Codex** (GPT-6, OpenAI): citations 5 verified / 0 rejected; findings 0 verified / 0 rejected; 0 refusals.
- **Nemotron** (nvidia/nemotron-3.5-super-vl-120b-a12b, NVIDIA): citations 5 verified / 0 rejected; findings 0 verified / 0 rejected; 1 refusals.

</details>

<details><summary><b>Evidence</b> (findings, cited code, tests and checks)</summary>

<a id="f-claude-C1"></a>
#### Claude C1 [info, docs]: TOC entry text still says "v1.x"; heading says "prior versions"

The link now reaches the right section, but its label differs from the heading it points to. Harmless; renaming the label would be a separate wording change outside this fix's scope.

Evidence: [`README.md:22 @head`](#ev-b3299a2245) [`README.md:101 @head`](#ev-9ff1cbd8ec)

Tier effect: silent

<a id="f-claude-C2"></a>
#### Claude C2 [info, docs]: Two other broken README anchors remain (#rpc, #author-info)

docs.anchors still reports #rpc and #author-info unresolved on lines the change did not touch. Outside this change's scope; a follow-up.

Evidence: [`check docs.anchors pass`](#ev-889510bd31)

Tier effect: silent

#### Cited evidence

<a id="ev-f329bfeb4b"></a>
**REQ-demo-docs1-F1 text** (verified; cited by claude on REQ-demo-docs1-F1): REQ-demo-docs1-F1 text contains the quote

> The README table-of-contents entry "Migration notes from v1.x" must link to an anchor that exists in README.md and resolves to the intended section ("Migration notes from prior versions", under Installation).

<a id="ev-ed83d70a20"></a>
**README.md:22 @head** (verified; cited by claude on REQ-demo-docs1-F1, nemotron on REQ-demo-docs1-F1, nemotron on REQ-demo-docs1-N1): quote matches README.md:22 at head 6e9b25c5

```text
// README.md @ 6e9b25c5
  19 | - [Installation](#installation)
  20 |     - [NuGet packages](#nuget-packages)
  21 |     - [Unity](#unity)
> 22 |     - [Migration notes from v1.x](#migration-notes-from-prior-versions)
  23 | - [Quick Start](#quick-start)
  24 | - [Analyzer](#analyzer)
  25 | - [Built-in supported types](#built-in-supported-types)
```

<a id="ev-7ee09de8c5"></a>
**README.md:101 @head** (verified; cited by claude on REQ-demo-docs1-F1, codex on REQ-demo-docs1-F1): quote matches README.md:101 at head 6e9b25c5; context only, not counted: line 101 of README.md is not a line this change touched (added at head)

```text
// README.md @ 6e9b25c5
   98 | 
   99 | For Unity projects, please read the [Unity Support](#unity-support) section to install.
  100 | 
> 101 | ### Migration notes from prior versions
  102 | 
  103 | Migrating from a prior major version of MessagePack to the latest?
  104 | Check out [these instructions](doc/migration.md).
```

<a id="ev-fc29488a6a"></a>
**README.md:22 @base** (verified; cited by claude on REQ-demo-docs1-F1): quote matches README.md:22 at base 32258fdb

```text
// README.md @ 32258fdb
  19 | - [Installation](#installation)
  20 |     - [NuGet packages](#nuget-packages)
  21 |     - [Unity](#unity)
> 22 |     - [Migration notes from v1.x](#migration-notes-from-v1x)
  23 | - [Quick Start](#quick-start)
  24 | - [Analyzer](#analyzer)
  25 | - [Built-in supported types](#built-in-supported-types)
```

<a id="ev-889510bd31"></a>
**check docs.anchors pass** (verified; cited by claude on REQ-demo-docs1-F1, codex on REQ-demo-docs1-F1, nemotron on REQ-demo-docs1-F1, nemotron on REQ-demo-docs1-N1, claude:C2): facts.json: docs.anchors pass: 1 intra-document link(s) on lines the change touched, 0 unresolved at head; README.md: base had 3 unresolved of 63, head has 2 unresolved on lines the change did not touch (#author-info, #rpc)

- `docs.anchors` **pass**: 1 intra-document link(s) on lines the change touched, 0 unresolved at head; README.md: base had 3 unresolved of 63, head has 2 unresolved on lines the change did not touch (#author-info, #rpc) (evidence/up-scripts/upfacts.py docs_anchors (GitHub heading slugs + <a name/id>) )

<a id="ev-f315fb38c4"></a>
**README.md:22 @head** (verified; cited by codex on REQ-demo-docs1-F1, codex on REQ-demo-docs1-N1): quote matches README.md:22 at head 6e9b25c5

```text
// README.md @ 6e9b25c5
  19 | - [Installation](#installation)
  20 |     - [NuGet packages](#nuget-packages)
  21 |     - [Unity](#unity)
> 22 |     - [Migration notes from v1.x](#migration-notes-from-prior-versions)
  23 | - [Quick Start](#quick-start)
  24 | - [Analyzer](#analyzer)
  25 | - [Built-in supported types](#built-in-supported-types)
```

<a id="ev-d71cae5f53"></a>
**REQ-demo-docs1-N1 text** (verified; cited by claude on REQ-demo-docs1-N1): REQ-demo-docs1-N1 text contains the quote

> Only that link changes; no other README content and no other file is altered.

<a id="ev-1494dc6548"></a>
**check public_api pass** (verified; cited by claude on REQ-demo-docs1-N1): facts.json: public_api pass: no public API changes: the change touches no file under src/ and no PublicAPI.*.txt

- `public_api` **pass**: no public API changes: the change touches no file under src/ and no PublicAPI.*.txt (git diff --name-only (no file under src/ changed) )

<a id="ev-f91e270150"></a>
**README.md:22 @head** (verified; cited by claude on REQ-demo-docs1-N1): quote matches README.md:22 at head 6e9b25c5

```text
// README.md @ 6e9b25c5
  19 | - [Installation](#installation)
  20 |     - [NuGet packages](#nuget-packages)
  21 |     - [Unity](#unity)
> 22 |     - [Migration notes from v1.x](#migration-notes-from-prior-versions)
  23 | - [Quick Start](#quick-start)
  24 | - [Analyzer](#analyzer)
  25 | - [Built-in supported types](#built-in-supported-types)
```

<a id="ev-50cd6358cd"></a>
**README.md:22 @base** (verified; cited by codex on REQ-demo-docs1-N1): quote matches README.md:22 at base 32258fdb

```text
// README.md @ 32258fdb
  19 | - [Installation](#installation)
  20 |     - [NuGet packages](#nuget-packages)
  21 |     - [Unity](#unity)
> 22 |     - [Migration notes from v1.x](#migration-notes-from-v1x)
  23 | - [Quick Start](#quick-start)
  24 | - [Analyzer](#analyzer)
  25 | - [Built-in supported types](#built-in-supported-types)
```

<a id="ev-5c6c2d8ab9"></a>
**README.md:22 @base** (verified; cited by nemotron on REQ-demo-docs1-N1): quote matches README.md:22 at base 32258fdb

```text
// README.md @ 32258fdb
  19 | - [Installation](#installation)
  20 |     - [NuGet packages](#nuget-packages)
  21 |     - [Unity](#unity)
> 22 |     - [Migration notes from v1.x](#migration-notes-from-v1x)
  23 | - [Quick Start](#quick-start)
  24 | - [Analyzer](#analyzer)
  25 | - [Built-in supported types](#built-in-supported-types)
```

<a id="ev-b3299a2245"></a>
**README.md:22 @head** (verified; cited by claude:C1): quote matches README.md:22 at head 6e9b25c5

```text
// README.md @ 6e9b25c5
  19 | - [Installation](#installation)
  20 |     - [NuGet packages](#nuget-packages)
  21 |     - [Unity](#unity)
> 22 |     - [Migration notes from v1.x](#migration-notes-from-prior-versions)
  23 | - [Quick Start](#quick-start)
  24 | - [Analyzer](#analyzer)
  25 | - [Built-in supported types](#built-in-supported-types)
```

<a id="ev-9ff1cbd8ec"></a>
**README.md:101 @head** (verified; cited by claude:C1): quote matches README.md:101 at head 6e9b25c5

```text
// README.md @ 6e9b25c5
   98 | 
   99 | For Unity projects, please read the [Unity Support](#unity-support) section to install.
  100 | 
> 101 | ### Migration notes from prior versions
  102 | 
  103 | Migrating from a prior major version of MessagePack to the latest?
  104 | Check out [these instructions](doc/migration.md).
```

</details>

<details><summary><b>Full detail</b>: all tier drivers, risk score, every check, areas, not checked, residual risk</summary>

Branch `ju26-demo-docs1` (32258fdb..6e9b25c5), 1 files, +1 -1. Author Zawaer (agent-written: True). Commit: docs: fix broken README anchor for migration notes

The table of contents linked to #migration-notes-from-v1x, but the section
is headed "Migration notes from prior versions", so the link went nowhere.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

Mandate `messagepack-csharp` v6 sha256 `71386aa55974f675`, signature: valid, Toivo

<a id="all-drivers"></a>
#### All tier drivers (tier = strictest)

- notify: reviewer refusal `claude`: How GitHub actually renders and scrolls to the new anchor (docs.rendering was not run; resolution relies on re-implemented slug rules plus the heading I read) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: reviewer refusal `nemotron`: Whether README.md renders correctly in the GitHub UI (docs.rendering was not run: Markdown was not rendered; anchors were resolved with GitHub slug rules re-implemented in upfacts.py, so visual rendering was not verified.) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- silent: trust cap `docs`: docs: AI may clear at most to silent (mandate clearance right)
- silent: risk score `risk`: score 1.2 (notify>=15, ask>=40, block>=130); largest: files_changed 1.1 + lines_changed 0.1

#### Who reviewed

Participating reviewers: claude, codex, nemotron. Adjudicator: gemini. Confidential: no. Rule: proven needs every participating reviewer to say met with verified evidence, and the clause's checks to pass.

| Reviewer | Model | Prompt | Verified findings | Rejected | Refusals |
|---|---|---|---|---|---|
| claude | claude-opus-5-5 (Anthropic) | review-v1 | 2 | 0 | 1 |
| codex | GPT-6 (OpenAI) | review-v1 | 0 | 0 | 0 |
| nemotron | nvidia/nemotron-3.5-super-vl-120b-a12b (NVIDIA) | review-v1 | 0 | 0 | 1 |

#### Every check

| Check | Status | Tool | Summary |
|---|---|---|---|
| build | skipped |   | not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run |
| tests.targeted | skipped |   | not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run |
| tests.fail_without_fix | skipped |   | not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run |
| tests.full_suite | skipped |   | not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run |
| public_api | pass | git diff --name-only (no file under src/ changed)  | no public API changes: the change touches no file under src/ and no PublicAPI.*.txt |
| analyzers | skipped |   | not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run |
| docs.anchors | pass | evidence/up-scripts/upfacts.py docs_anchors (GitHub heading slugs + <a name/id>)  | 1 intra-document link(s) on lines the change touched, 0 unresolved at head; README.md: base had 3 unresolved of 63, head has 2 unresolved on lines the change did not touch (#author-info, #rpc) |
| injection_scan | pass | countersign.injection (deterministic pattern scan) injection-v2 | no text addressed to automated reviewers in the added lines, file paths, branch, commit message or PR text |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v6 (71386aa55974)

#### Requirement trace (engine codes)

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-demo-docs1-F1 | proven | claude: met (3/5), codex: met (2/3), nemotron: met (2/2) | docs.anchors: pass | - |
| REQ-demo-docs1-N1 | proven | claude: met (2/3), codex: met (2/2), nemotron: met (3/3) | docs.anchors: pass | - |

#### What the AI refused to decide (every reviewer refusal)

- **claude** refused: How GitHub actually renders and scrolls to the new anchor. Why: docs.rendering was not run; resolution relies on re-implemented slug rules plus the heading I read Who should decide: docs owner
- **nemotron** refused: Whether README.md renders correctly in the GitHub UI. Why: docs.rendering was not run: Markdown was not rendered; anchors were resolved with GitHub slug rules re-implemented in upfacts.py, so visual rendering was not verified. Who should decide: docs/area owner

<a id="areas"></a>
#### Areas

| Area | Owner | Sensitivity | AI cap | Files |
|---|---|---|---|---:|
| docs | Rene | low | silent (mandate clearance right) | 1 |

<a id="not-checked"></a>
#### What was not checked, and why

- `docs.rendering` (facts.json not_run): Markdown was not rendered; anchors were resolved with GitHub slug rules re-implemented in upfacts.py
- `docs.external_links` (facts.json not_run): links to other files or URLs were not followed (offline)
- `build` (check did not pass or fail): skipped: not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run
- `tests.targeted` (check did not pass or fail): skipped: not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run
- `tests.fail_without_fix` (check did not pass or fail): skipped: not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run
- `tests.full_suite` (check did not pass or fail): skipped: not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run
- `analyzers` (check did not pass or fail): skipped: not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run
- `other-targets` (mandate known gap): Tests run on net8.0 only; .NET Framework, Unity and NativeAOT targets are not exercised
- `runtime-perf` (mandate known gap): No benchmarks unless a perf-sensitive path is touched; allocation and throughput regressions can slip through
- `semantic-intent` (mandate known gap): Correctness beyond what tests and cited evidence show is not established by the AI
- `provenance` (mandate known gap): Licensing and provenance of agent-written code are not checked

#### Residual risk (every item)

- Reviewer refusal (claude): How GitHub actually renders and scrolls to the new anchor (out of scope: notify)
- Reviewer refusal (nemotron): Whether README.md renders correctly in the GitHub UI (out of scope: notify)
- docs.rendering not run (Markdown was not rendered; anchors were resolved with GitHub slug rules re-implemented in upfacts.py)
- docs.external_links not run (links to other files or URLs were not followed (offline))
- build not run (skipped: not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run)
- tests.targeted not run (skipped: not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run)
- tests.fail_without_fix not run (skipped: not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run)
- tests.full_suite not run (skipped: not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run)
- analyzers not run (skipped: not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run)
- Standing gaps of this pipeline: other-targets, runtime-perf, semantic-intent, provenance (see not checked)

<a id="risk"></a>
#### Risk score: 1.2 -> silent

| Factor | Points | Reason |
|---|---:|---|
| area_sensitivity | 0 | most sensitive area touched: docs (low) |
| files_changed | 1.1 | 1 files (~1.1 per file while small, log-scaled past 80, cap 45) |
| lines_changed | 0.1 | 2 non-generated lines (~4 per 100 lines while small, log-scaled past 100, cap 20; files and lines together at most 45) |
| generated_files | 0.0 | 0 generated files x 0.1 (cap 10) |
| public_api_change | 0 | public_api check: no change |
| source_without_tests | 0 | no source changed |
| security_sensitive_paths | 0 | none touched |
| fail_without_fix_not_shown | 0 | tests.fail_without_fix: skipped (no source changed: nothing to revert) |
| reviewer_disagreement | 0 | 0 clause(s) x 8 |
| failed_checks | 0 | 0 failed check(s) x 25 |
| **total** | **1.2** | bands: {'notify': 15, 'ask': 40, 'block': 130} |

Inputs: facts `evidence/demo-docs1/facts.json`, requirements `requirements/demo-docs1.yaml`, reviews `reviews/demo-docs1/claude.json`, `reviews/demo-docs1/codex.json`, `reviews/demo-docs1/nemotron.json`

</details>

</details>
