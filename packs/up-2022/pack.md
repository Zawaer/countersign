## Countersign: **ASK**, owner **Toivo**

**#2017 Ignore abstract implementations of `IMessagePackFormatter<T>` Fixes #2017**

**Why:** The AI declined to decide 1 question

- ✓ All 6 checks pass
- ? Reviewers left 1 question open
- … Awaiting Toivo's countersignature

<details><summary><b>Evidence</b>: requirements, findings, checks, reviewers, how to sign</summary>

<a id="risk"></a>

<details><summary>👤 <b>Why ask</b>: 1 reason, risk score 23.4</summary>

1. The AI declined to decide 1 question, e.g. Runtime deserialization security and execution behavior ([see](#refused))

All 7 tier drivers and the risk factors are under Full detail.

</details>

**Requirements**

<a id="chain-REQ-up-2022-F1"></a>

<details><summary>✅ <b>F1</b> Proven: all 3 reviewers say met, checks pass · AnalyzerOptions.cs:221</summary>

> The analyzer must not report MsgPack013 (formatter has no accessible instance for the source generated resolver) for an abstract class that implements IMessagePackFormatter<T>.

- **Claude** met (2 of 4 cited verified), **Codex** met (2 of 2 cited verified), **Nemotron** met (4 of 5 cited verified)
- Checks: `build` pass, `tests.targeted` pass
- Fail without the fix: `AbstractFormatterDoesNotAttractAttention`
- Cited: [`AnalyzerOptions.cs:221`](#ev-cd3ad6e495)

</details>

<a id="chain-REQ-up-2022-F2"></a>

<details><summary>✅ <b>F2</b> Proven: all 3 reviewers say met, checks pass · AnalyzerOptions.cs:224</summary>

> Abstract implementations of IMessagePackFormatter<T> must not be counted as formatters, so they cannot cause MsgPack009 (more than one formatter for the same type).

- **Claude** met (3 of 4 cited verified), **Codex** met (3 of 3 cited verified), **Nemotron** met (4 of 5 cited verified)
- Checks: `build` pass, `tests.targeted` pass
- Fail without the fix: `AbstractFormatterDoesNotAttractAttention`
- Cited: [`AnalyzerOptions.cs:224`](#ev-0104897806)

</details>

<a id="chain-REQ-up-2022-N1"></a>

<details><summary>✅ <b>N1</b> Proven: all 3 reviewers say met, checks pass</summary>

> The fix is covered by automated tests that fail without it.

- **Claude** met (2 of 2 cited verified), **Codex** met (2 of 2 cited verified), **Nemotron** met (2 of 3 cited verified)
- Checks: `build` pass, `tests.fail_without_fix` pass
- Fail without the fix: `AbstractFormatterDoesNotAttractAttention`

</details>

<a id="chain-REQ-up-2022-N2"></a>

<details><summary>✅ <b>N2</b> Proven: all 3 reviewers say met, checks pass · AnalyzerOptions.cs:228</summary>

> Non-abstract formatters are still discovered and diagnosed as before (no regressions in the existing test suite).

- **Claude** met (1 of 3 cited verified), **Codex** met (1 of 1 cited verified), **Nemotron** met (1 of 2 cited verified)
- Checks: `build` pass, `tests.full_suite` pass
- Pass without the fix: `MessageFormatterAttribute`
- Cited: [`AnalyzerOptions.cs:228`](#ev-d27a42c472)

</details>

**Findings**

<details><summary>🐞 3 findings (minor, info, 1 rejected)</summary>

- <a id="f-claude-C2"></a>⚪ **info** New test covers the analyzer path only (Claude C2): The test runs VerifyAnalyzerAsync with no expected diagnostics; the generator's own scan (GeneratorUtilities) shares… [full text](https://github.com/Zawaer/countersign/blob/main/reviews/up-2022/claude.json)
- <a id="f-nemotron-I1"></a>⚪ **info** TryCreate documentation does not state that abstract types are excluded (Nemotron I1): The XML documentation for FormatterDescriptor.TryCreate (head line 218) describes the return value but does not mention… [full text](https://github.com/Zawaer/countersign/blob/main/reviews/up-2022/nemotron.json)
- <a id="f-claude-C1"></a>🟡 **minor** **rejected** Abstract type named in [MessagePackFormatter]/[MessagePackKnownFormatter] is now silently ignored (Claude C1): TryCreate is not only used for discovery: it also resolves the type in a member's [MessagePackFormatter(typeof(X))]… [full text](https://github.com/Zawaer/countersign/blob/main/reviews/up-2022/claude.json)

</details>

**Checks**

<a id="every-check"></a>

<details><summary>✅ 6 of 6 checks pass</summary>

- ✅ `build`: 0 errors, 1 unique warnings ([log](https://github.com/Zawaer/countersign/blob/main/evidence/up-2022/logs/build.log))
- ✅ `tests.targeted`: 26 passed, 0 failed, 0 skipped (1 new tests in run) ([log](https://github.com/Zawaer/countersign/blob/main/evidence/up-2022/logs/tests_targeted.1.log))
- ✅ `tests.fail_without_fix`: new tests fail on base source: 1/1 failed -> tests do cover the change ([log](https://github.com/Zawaer/countersign/blob/main/evidence/up-2022/logs/tests_fail_without_fix.1.log))
- ✅ `tests.full_suite`: tests/MessagePack.SourceGenerator.Tests: 150 tests, 150 passed, 0 failed (0 not failing on base, 0 also… [full text](https://github.com/Zawaer/countersign/blob/main/evidence/up-2022/facts.json) ([log](https://github.com/Zawaer/countersign/blob/main/evidence/up-2022/logs/tests_full_suite.log))
- ✅ `public_api`: no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or… [full text](https://github.com/Zawaer/countersign/blob/main/evidence/up-2022/facts.json)
- ✅ `analyzers`: no new warnings

[facts.json](https://github.com/Zawaer/countersign/blob/main/evidence/up-2022/facts.json)

</details>

<details><summary>❓ Supply chain: deps.delta not run</summary>

<a id="supply-chain"></a>**Supply chain (from the build):** deps.delta not run; build egress not recorded (local run, not on CRACI)


</details>

<a id="not-checked"></a>

<details><summary>❓ Not run: 8 checks, 4 standing gaps</summary>

- `tests.MessagePack.Tests` (facts.json not_run): runtime library src/MessagePack not modified by the change; suite not run
- `tests.execution` (facts.json not_run): ExecutionTests/MapModeExecutionTests not run for this control (generator output is covered by the snapshot tests in the full suite)
- `build.net472/netstandard` (facts.json not_run): only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks` (facts.json not_run): no runtime serialization hot path touched
- `other-targets` (mandate known gap): Tests run on net8.0 only; .NET Framework, Unity and NativeAOT targets are not exercised
- `runtime-perf` (mandate known gap): No benchmarks unless a perf-sensitive path is touched; allocation and throughput regressions can slip through
- `semantic-intent` (mandate known gap): Correctness beyond what tests and cited evidence show is not established by the AI
- `provenance` (mandate known gap): Licensing and provenance of agent-written code are not checked
- Standing pipeline gaps: `other-targets`, `runtime-perf`, `semantic-intent`, `provenance`

</details>

**Reviewers**

<details><summary>👤 <b>Claude</b> claude-opus-5-5: met 4 of 4 · 1 finding</summary>

- claude-opus-5-5, Anthropic, prompt review-v1. Citations: 14 verified, 3 rejected. Findings: 1 verified, 1 rejected. 2 refusals.
- Only Claude raised: [C1](#f-claude-C1), [C2](#f-claude-C2)
- [review file](https://github.com/Zawaer/countersign/blob/main/reviews/up-2022/claude.json)

</details>

<details><summary>👤 <b>Codex</b> GPT-6: met 4 of 4 · 0 findings</summary>

- GPT-6, OpenAI, prompt review-v1. Citations: 8 verified, 0 rejected. Findings: 0 verified, 0 rejected. 0 refusals.
- [review file](https://github.com/Zawaer/countersign/blob/main/reviews/up-2022/codex.json)

</details>

<details><summary>👤 <b>Nemotron</b> nemotron-3.5-super-vl-120b-a12b: met 4 of 4 · 1 finding</summary>

- nvidia/nemotron-3.5-super-vl-120b-a12b, NVIDIA, prompt review-v1. Citations: 16 verified, 1 rejected. Findings: 1 verified, 0 rejected. 2 refusals.
- Only Nemotron raised: [I1](#f-nemotron-I1)
- [review file](https://github.com/Zawaer/countersign/blob/main/reviews/up-2022/nemotron.json)

</details>

<a id="refused"></a>

<details><summary>❓ Open questions: 1 for a human (+3 out of scope)</summary>

- <a id="refusal-3"></a>**Runtime deserialization security and execution behavior** *Who:* area owner / MessagePack maintainer (raised by Nemotron). The change only touches the source-generator analyzer and its tests; the runtime deserialization code in… [full text](https://github.com/Zawaer/countersign/blob/main/reviews/up-2022/nemotron.json)

<a id="refused-peripheral"></a>3 peripheral refusals (out of scope for this change):

- <a id="refusal-1"></a>Exact behaviour (diagnostics and generated code) when an attribute names an abstract formatter type, before and after (who: source generator area owner)
- <a id="refusal-2"></a>Whether the release notes / analyzer docs should mention the change (who: area owner)
- <a id="refusal-4"></a>Behavior on non-net8.0 target frameworks (who: area owner / maintainer)

</details>

**Sign**

<details><summary>⚠️ You accept 4 residual risks by signing</summary>

- 1 question the AI declined to decide (listed above) are yours. ([see](#refused))
- 3 peripheral refusals (out of scope for this change) are yours too. ([see](#refused-peripheral))
- Not run: tests.MessagePack.Tests, tests.execution, build.net472/netstandard, benchmarks ([see](#not-checked))
- Standing pipeline gaps: other-targets, runtime-perf, semantic-intent, provenance ([see](#not-checked))

</details>

**Toivo signs** (required; accept, reject, request-changes)

```
countersign sign up-2022 --as Toivo --decision … --note "…"
```

<details><summary>And rate the 2 verified findings (full command)</summary>

One `--finding` flag each: `accepted` (real), `rejected` (a false positive) or `unsure`, optionally `:reason`. A finding without a flag is recorded as `unrated`.

- `claude:C2` (info): New test covers the analyzer path only
- `nemotron:I1` (info): TryCreate documentation does not state that abstract types are excluded

```
countersign sign up-2022 --as Toivo --decision <accept|reject|request-changes> --note "..." \
  --finding claude:C2=<accepted|rejected|unsure> \
  --finding nemotron:I1=<accepted|rejected|unsure>
```

</details>

<details><summary>What your signature says</summary>

> I, Toivo, have read what was checked and by whom, what was not checked and why, and the residual risk listed in this pack, and I own this decision.

It covers the sha256 of this pack's canonical JSON, the decision, your verdict on each finding, the time and the signer, and is appended to the hash-chained ledger.

</details>

<details><summary><b>Full detail</b>: tier drivers, risk score, engine codes, areas</summary>

Branch `upstream PR #2022` (f5e104ee..5f4b762a), 2 files, +29 -0. Author Andrew Arnott (agent-written: False). Commit: Ignore abstract implementations of `IMessagePackFormatter<T>`

Fixes #2017

Mandate `messagepack-csharp` v6 sha256 `71386aa55974f675`, signature: valid, Toivo

<a id="all-drivers"></a>
#### All tier drivers (tier = strictest)

- ask: reviewer refusal `nemotron`: Runtime deserialization security and execution behavior (The change only touches the source-generator analyzer and its tests; the runtime deserialization code in src/MessagePack is unmodified and tests.MessagePack.Tests was not run (listed in not_run), so no security claim about deserializing untrusted input is made here.)
- notify: reviewer refusal `claude`: Exact behaviour (diagnostics and generated code) when an attribute names an abstract formatter type, before and after (Not exercised by any test in facts.json; would need a run I was not given) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: reviewer refusal `claude`: Whether the release notes / analyzer docs should mention the change (Docs for MsgPack009/MsgPack013 were not in the context) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: reviewer refusal `nemotron`: Behavior on non-net8.0 target frameworks (Build and tests ran only on net8.0 Debug in a Linux container; net472/netstandard builds were not run (listed in not_run).) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: trust cap `generator-analyzer-core`: generator-analyzer-core: AI may clear at most to notify (mandate clearance right)
- notify: risk score `risk`: score 23.4 (notify>=15, ask>=40, block>=130); largest: area_sensitivity 20 + files_changed 2.2 + lines_changed 1.2
- silent: trust cap `tests`: tests: AI may clear at most to silent (mandate clearance right)

#### Who reviewed

Participating reviewers: claude, codex, nemotron. Adjudicator: gemini. Confidential: no. Rule: proven needs every participating reviewer to say met with verified evidence, and the clause's checks to pass.

| Reviewer | Model | Prompt | Verified findings | Rejected | Refusals |
|---|---|---|---|---|---|
| claude | claude-opus-5-5 (Anthropic) | review-v1 | 1 | 1 | 2 |
| codex | GPT-6 (OpenAI) | review-v1 | 0 | 0 | 0 |
| nemotron | nvidia/nemotron-3.5-super-vl-120b-a12b (NVIDIA) | review-v1 | 1 | 0 | 2 |

#### Every check

| Check | Status | Tool | Summary |
|---|---|---|---|
| build | pass | dotnet build 8.0.402 | 0 errors, 1 unique warnings |
| tests.targeted | pass | dotnet test 8.0.402 | 26 passed, 0 failed, 0 skipped (1 new tests in run) |
| tests.fail_without_fix | pass | dotnet test (source reverted, tests kept) 8.0.402 | new tests fail on base source: 1/1 failed -> tests do cover the change |
| tests.full_suite | pass | dotnet test 8.0.402 | tests/MessagePack.SourceGenerator.Tests: 150 tests, 150 passed, 0 failed (0 not failing on base, 0 also failing on base) |
| public_api | pass | git diff of PublicAPI.*.txt + scan of added public/protected declarations in src/  | no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or removed in src/ |
| analyzers | pass | dotnet build warnings (Roslyn analyzers, StyleCop, PublicApiAnalyzers) vs base  | no new warnings |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v6 (71386aa55974)

#### Requirement trace (engine codes)

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-up-2022-F1 | proven | claude: met (2/4), codex: met (2/2), nemotron: met (4/5) | build: pass, tests.targeted: pass | - |
| REQ-up-2022-F2 | proven | claude: met (3/4), codex: met (3/3), nemotron: met (4/5) | build: pass, tests.targeted: pass | - |
| REQ-up-2022-N1 | proven | claude: met (2/2), codex: met (2/2), nemotron: met (2/3) | build: pass, tests.fail_without_fix: pass | - |
| REQ-up-2022-N2 | proven | claude: met (1/3), codex: met (1/1), nemotron: met (1/2) | build: pass, tests.full_suite: pass | - |

#### What the AI refused to decide (every reviewer refusal)

- **claude** refused: Exact behaviour (diagnostics and generated code) when an attribute names an abstract formatter type, before and after. Why: Not exercised by any test in facts.json; would need a run I was not given Who should decide: source generator area owner
- **claude** refused: Whether the release notes / analyzer docs should mention the change. Why: Docs for MsgPack009/MsgPack013 were not in the context Who should decide: area owner
- **nemotron** refused: Runtime deserialization security and execution behavior. Why: The change only touches the source-generator analyzer and its tests; the runtime deserialization code in src/MessagePack is unmodified and tests.MessagePack.Tests was not run (listed in not_run), so no security claim about deserializing untrusted input is made here. Who should decide: area owner / MessagePack maintainer
- **nemotron** refused: Behavior on non-net8.0 target frameworks. Why: Build and tests ran only on net8.0 Debug in a Linux container; net472/netstandard builds were not run (listed in not_run). Who should decide: area owner / maintainer

<a id="areas"></a>
#### Areas

| Area | Owner | Sensitivity | AI cap | Files |
|---|---|---|---|---:|
| generator-analyzer-core | Toivo | high | notify (mandate clearance right) | 1 |
| tests | Toivo | low | silent (mandate clearance right) | 1 |

<a id="not-checked"></a>
#### What was not checked, and why

- `tests.MessagePack.Tests` (facts.json not_run): runtime library src/MessagePack not modified by the change; suite not run
- `tests.execution` (facts.json not_run): ExecutionTests/MapModeExecutionTests not run for this control (generator output is covered by the snapshot tests in the full suite)
- `build.net472/netstandard` (facts.json not_run): only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks` (facts.json not_run): no runtime serialization hot path touched
- `other-targets` (mandate known gap): Tests run on net8.0 only; .NET Framework, Unity and NativeAOT targets are not exercised
- `runtime-perf` (mandate known gap): No benchmarks unless a perf-sensitive path is touched; allocation and throughput regressions can slip through
- `semantic-intent` (mandate known gap): Correctness beyond what tests and cited evidence show is not established by the AI
- `provenance` (mandate known gap): Licensing and provenance of agent-written code are not checked

#### Residual risk (every item)

- Reviewer refusal (claude): Exact behaviour (diagnostics and generated code) when an attribute names an abstract formatter type, before and after (out of scope: notify)
- Reviewer refusal (claude): Whether the release notes / analyzer docs should mention the change (out of scope: notify)
- Reviewer refusal (nemotron): Runtime deserialization security and execution behavior
- Reviewer refusal (nemotron): Behavior on non-net8.0 target frameworks (out of scope: notify)
- tests.MessagePack.Tests not run (runtime library src/MessagePack not modified by the change; suite not run)
- tests.execution not run (ExecutionTests/MapModeExecutionTests not run for this control (generator output is covered by the snapshot tests in the full suite))
- build.net472/netstandard not run (only the net8.0 slice of src/MessagePack was built (Linux container, Debug))
- benchmarks not run (no runtime serialization hot path touched)
- Standing gaps of this pipeline: other-targets, runtime-perf, semantic-intent, provenance (see not checked)

<a id="risk"></a>
#### Risk score: 23.4 -> notify

| Factor | Points | Reason |
|---|---:|---|
| area_sensitivity | 20 | most sensitive area touched: generator-analyzer-core (high) |
| files_changed | 2.2 | 2 files (~1.1 per file while small, log-scaled past 80, cap 45) |
| lines_changed | 1.2 | 29 non-generated lines (~4 per 100 lines while small, log-scaled past 100, cap 20; files and lines together at most 45) |
| generated_files | 0.0 | 0 generated files x 0.1 (cap 10) |
| public_api_change | 0 | public_api check: no change |
| source_without_tests | 0 | tests changed alongside source |
| security_sensitive_paths | 0 | none touched |
| fail_without_fix_not_shown | 0 | tests.fail_without_fix: pass |
| reviewer_disagreement | 0 | 0 clause(s) x 8 |
| failed_checks | 0 | 0 failed check(s) x 25 |
| **total** | **23.4** | bands: {'notify': 15, 'ask': 40, 'block': 130} |

Inputs: facts `evidence/up-2022/facts.json`, requirements `requirements/up-2022.yaml`, reviews `reviews/up-2022/claude.json`, `reviews/up-2022/codex.json`, `reviews/up-2022/nemotron.json`

</details>

<details><summary><b>Cited evidence</b> (code excerpts, test runs, checks)</summary>

<a id="ev-b1898df7f0"></a>
**REQ-up-2022-F1 text** (verified; cited by claude on REQ-up-2022-F1, nemotron on REQ-up-2022-F1): REQ-up-2022-F1 text contains the quote

> The analyzer must not report MsgPack013 (formatter has no accessible instance for the source generated resolver) for an abstract class that implements IMessagePackFormatter<T>.

<a id="ev-cd3ad6e495"></a>
**AnalyzerOptions.cs:221 @head** (verified; cited by claude on REQ-up-2022-F1, codex on REQ-up-2022-F1, nemotron on REQ-up-2022-F1, nemotron on REQ-up-2022-F2, nemotron:I1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs:221 at head 5f4b762a

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs @ 5f4b762a
  218 |     /// <returns><see langword="true"/> if <paramref name="type"/> represents a formatter.</returns>
  219 |     public static bool TryCreate(INamedTypeSymbol type, [NotNullWhen(true)] out FormatterDescriptor? formatter)
  220 |     {
> 221 |         if (type.IsAbstract)
  222 |         {
  223 |             formatter = null;
  224 |             return false;
```

<a id="ev-bb2c0d462b"></a>
**AnalyzerOptions.cs:247 @head** (verified; cited by claude on REQ-up-2022-F1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs:247 at head 5f4b762a; context only, not counted: line 247 of src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs is not a line this change touched (added at head)

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs @ 5f4b762a
  244 |         {
  245 |             InaccessibleDescriptor =
  246 |                 CodeAnalysisUtilities.FindInaccessibleTypes(type).Any() ? MsgPack00xMessagePackAnalyzer.InaccessibleFormatterType :
> 247 |                 instanceProvidingMember is null ? MsgPack00xMessagePackAnalyzer.InaccessibleFormatterInstance :
  248 |                 null,
  249 |             ExcludeFromSourceGeneratedResolver =
  250 |                 type.GetAttributes().Any(a => a.AttributeClass?.Name == Constants.ExcludeFormatterFromSourceGeneratedResolverAttributeName && a.AttributeClass?.ContainingNamespace.Name == Constants.AttributeNamespace),
```

<a id="ev-ec490502a9"></a>
**test AbstractFormatterDoesNotAttractAttention passed** (verified; cited by claude on REQ-up-2022-F1, codex on REQ-up-2022-F1, nemotron on REQ-up-2022-F1, claude on REQ-up-2022-F2, nemotron on REQ-up-2022-F2): facts.json tests.targeted: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-4462e470a3"></a>
**AnalyzerOptions.cs:223 @head** (verified; cited by nemotron on REQ-up-2022-F1, codex on REQ-up-2022-F2): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs:223 at head 5f4b762a

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs @ 5f4b762a
  220 |     {
  221 |         if (type.IsAbstract)
  222 |         {
> 223 |             formatter = null;
  224 |             return false;
  225 |         }
  226 | 
```

<a id="ev-0104897806"></a>
**AnalyzerOptions.cs:224 @head** (verified; cited by nemotron on REQ-up-2022-F1, claude on REQ-up-2022-F2): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs:224 at head 5f4b762a

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs @ 5f4b762a
  221 |         if (type.IsAbstract)
  222 |         {
  223 |             formatter = null;
> 224 |             return false;
  225 |         }
  226 | 
  227 |         var formattedTypes =
```

<a id="ev-d6ac4eeb2e"></a>
**REQ-up-2022-F2 text** (verified; cited by claude on REQ-up-2022-F2, nemotron on REQ-up-2022-F2): REQ-up-2022-F2 text contains the quote

> Abstract implementations of IMessagePackFormatter<T> must not be counted as formatters, so they cannot cause MsgPack009 (more than one formatter for the same type).

<a id="ev-9046fbade9"></a>
**test AbstractFormatterDoesNotAttractAttention failed** (verified; cited by claude on REQ-up-2022-F2, codex on REQ-up-2022-F2, nemotron on REQ-up-2022-F2, claude on REQ-up-2022-N1, codex on REQ-up-2022-N1, nemotron on REQ-up-2022-N1): facts.json tests.fail_without_fix: failed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-197e014bda"></a>
**MsgPack00xAnalyzerTests.cs:913 @head** (verified; cited by codex on REQ-up-2022-F2): quote matches tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs:913 at head 5f4b762a

```text
// tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs @ 5f4b762a
  910 |     }
  911 | 
  912 |     [Fact]
> 913 |     public async Task AbstractFormatterDoesNotAttractAttention()
  914 |     {
  915 |         string test = /* lang=c#-test */ """
  916 |             using MessagePack;
```

<a id="ev-62faeb2508"></a>
**check tests.fail_without_fix pass** (verified; cited by nemotron on REQ-up-2022-F2, claude on REQ-up-2022-N1, codex on REQ-up-2022-N1, nemotron on REQ-up-2022-N1): facts.json: tests.fail_without_fix pass: new tests fail on base source: 1/1 failed -> tests do cover the change

- `tests.fail_without_fix` **pass**: new tests fail on base source: 1/1 failed -> tests do cover the change (dotnet test (source reverted, tests kept) 8.0.402)
- log: `evidence/up-2022/logs/tests_fail_without_fix.1.log`

<a id="ev-15d0adb4f3"></a>
**REQ-up-2022-N1 text** (verified; cited by nemotron on REQ-up-2022-N1): REQ-up-2022-N1 text contains the quote

> The fix is covered by automated tests that fail without it.

<a id="ev-d448f979e6"></a>
**check tests.full_suite pass** (verified; cited by claude on REQ-up-2022-N2, codex on REQ-up-2022-N2, nemotron on REQ-up-2022-N2): facts.json: tests.full_suite pass: tests/MessagePack.SourceGenerator.Tests: 150 tests, 150 passed, 0 failed (0 not failing on base, 0 also failing on base)

- `tests.full_suite` **pass**: tests/MessagePack.SourceGenerator.Tests: 150 tests, 150 passed, 0 failed (0 not failing on base, 0 also failing on base) (dotnet test 8.0.402)
- log: `evidence/up-2022/logs/tests_full_suite.log`

<a id="ev-5eb9a35a14"></a>
**test MessageFormatterAttribute passed** (verified; cited by claude on REQ-up-2022-N2): facts.json tests.targeted: passed; context only, not counted: test MsgPack00xAnalyzerTests.MessageFormatterAttribute is not added or edited by this change, nor listed in the clause's tests:

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **passed**
- Without the fix it **passed**: it does not show the change

<a id="ev-d27a42c472"></a>
**AnalyzerOptions.cs:228 @head** (verified; cited by claude on REQ-up-2022-N2): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs:228 at head 5f4b762a; context only, not counted: line 228 of src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs is not a line this change touched (added at head)

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs @ 5f4b762a
  225 |         }
  226 | 
  227 |         var formattedTypes =
> 228 |             AnalyzerUtilities.SearchTypeForFormatterImplementations(type)
  229 |             .Select(i => new FormattableType(i, type.ContainingAssembly))
  230 |             .ToImmutableHashSet();
  231 |         if (formattedTypes.IsEmpty)
```

<a id="ev-d3fe657f03"></a>
**REQ-up-2022-N2 text** (verified; cited by nemotron on REQ-up-2022-N2): REQ-up-2022-N2 text contains the quote

> Non-abstract formatters are still discovered and diagnosed as before (no regressions in the existing test suite).

<a id="ev-8af6858086"></a>
**TypeCollector.cs:720 @head** (NOT verified; cited by claude:C1): src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs is not in the change's diff

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 5f4b762a
  717 |             INamedTypeSymbol? name = member.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.FormatterAttribute))?.ConstructorArguments[0].Value as INamedTypeSymbol;
  718 |             if (name is not null)
  719 |             {
> 720 |                 if (FormatterDescriptor.TryCreate(name, out FormatterDescriptor? descriptor))
  721 |                 {
  722 |                     return descriptor;
  723 |                 }
```

<a id="ev-699ea72a89"></a>
**TypeCollector.cs:725 @head** (NOT verified; cited by claude:C1): src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs is not in the change's diff

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 5f4b762a
  724 |                 else
  725 |                 {
  726 |                     // Report that the named type is not a formatter.
> 727 |                     // this.reportDiagnostic();
  728 |                 }
  729 |             }
  730 | 
```

<a id="ev-c9c11752cc"></a>
**AnalyzerUtilities.cs:95 @head** (NOT verified; cited by claude:C1): src/MessagePack.SourceGenerator/Utils/AnalyzerUtilities.cs is not in the change's diff

```text
// src/MessagePack.SourceGenerator/Utils/AnalyzerUtilities.cs @ 5f4b762a
  92 |             cancellationToken.ThrowIfCancellationRequested();
  93 |             if (ad.AttributeClass?.Name == MessagePackKnownFormatterAttributeName && ad.AttributeClass?.ContainingNamespace.Name == AttributeNamespace)
  94 |             {
> 95 |                 if (ad.ConstructorArguments[0].Value is INamedTypeSymbol formatterType && FormatterDescriptor.TryCreate(formatterType, out FormatterDescriptor? formatter))
  96 |                 {
  97 |                     builder.Add(formatter);
  98 |                 }
```

<a id="ev-04a0a5893b"></a>
**MsgPack00xAnalyzerTests.cs:932 @head** (verified; cited by claude:C2): quote matches tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs:932 at head 5f4b762a

```text
// tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs @ 5f4b762a
  929 |             }
  930 |             """;
  931 | 
> 932 |         await VerifyCS.VerifyAnalyzerAsync(test);
  933 |     }
  934 | }
```

<a id="ev-302a6a0f66"></a>
**AnalyzerOptions.cs:218 @head** (NOT verified; cited by nemotron:I1): quote not on src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs:218 ±3 at head; not found anywhere in the file

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs @ 5f4b762a
  215 |     /// </summary>
  216 |     /// <param name="type">The type symbol for the formatter.</param>
  217 |     /// <param name="formatter">Receives the formatter descriptor, if applicable.</param>
  218 |     /// <returns><see langword="true"/> if <paramref name="type"/> represents a formatter.</returns>
  219 |     public static bool TryCreate(INamedTypeSymbol type, [NotNullWhen(true)] out FormatterDescriptor? formatter)
  220 |     {
  221 |         if (type.IsAbstract)
```

</details>

</details>
