# Evidence pack: change 2234

**Recommended tier: ASK** · owner **Toivo** · risk score 59.6

Branch `ju26-issue-2234` (32258fdb..9007cee1), 4 files, +262 -4. Author Stelian Vultur (agent-written: True). Commit: Implementation for #2234 The analyzer does not work if SuppressSourceGeneration = true

Mandate `messagepack-csharp` v1 sha256 `ef0e95521f7e364a`, signature: valid, Toivo

## Why this tier

- **ask** from verified finding `claude:C1`: major: Change does not address the regression the issue reports; it fixes a different, pre-existing crash
- **ask** from refused clause `REQ-2234-N2`: cannot_determine: claude: 4 of the 8 new analyzer tests fail on base source (AD0001), so the fix is covered. SourceGenerator.Tests passes 175/175 on head. But the execution test projects (which include the 2 new execution tests) did not build in my environment, so I cannot establish 'no regressions in the existing test suite'.; cannot_determine: codex: The added tests cover the stated scenarios, but the available repository review context contains no execution results and does not establish that the tests fail without the fix or that the full suite has no regressions.
- **ask** from reviewer refusal `claude`: Which branch this change targets, and therefore whether it resolves issue #2234 for users (The reported regression lives on master/v3.1.x, not on the base of this change. Whether the change is meant for that line, or whether a separate fix is needed there, is a release-management decision I cannot make from the code.)
- **ask** from reviewer refusal `claude`: No regressions in execution tests (including the 2 new SuppressedSourceGenerationTests) (ExecutionTests and MapModeExecutionTests failed to compile in my environment (CS0117 on GeneratedMessagePackResolver/MyGeneratedCompositeResolver 'Instance', also in pre-existing files), so I could not run them.)
- **ask** from reviewer refusal `claude`: Generator behaviour (no CS8785) on duplicate/mixed keys (Established only by code reading; the new tests run the analyzer alone (CSharpCodeFixVerifier), not the generator.)
- **ask** from reviewer refusal `codex`: Whether the new tests fail on base and whether the existing suite is regression-free (No facts.json checks or executed test outcomes were available to inspect.)
- **ask** from risk score `risk`: score 59.6 (notify>=15, ask>=40, block>=130); largest: failed_checks 25 + area_sensitivity 20 + lines_changed 10.6

<details><summary>All tier drivers</summary>

- ask: verified finding `claude:C1`: major: Change does not address the regression the issue reports; it fixes a different, pre-existing crash
- ask: refused clause `REQ-2234-N2`: cannot_determine: claude: 4 of the 8 new analyzer tests fail on base source (AD0001), so the fix is covered. SourceGenerator.Tests passes 175/175 on head. But the execution test projects (which include the 2 new execution tests) did not build in my environment, so I cannot establish 'no regressions in the existing test suite'.; cannot_determine: codex: The added tests cover the stated scenarios, but the available repository review context contains no execution results and does not establish that the tests fail without the fix or that the full suite has no regressions.
- ask: reviewer refusal `claude`: Which branch this change targets, and therefore whether it resolves issue #2234 for users (The reported regression lives on master/v3.1.x, not on the base of this change. Whether the change is meant for that line, or whether a separate fix is needed there, is a release-management decision I cannot make from the code.)
- ask: reviewer refusal `claude`: No regressions in execution tests (including the 2 new SuppressedSourceGenerationTests) (ExecutionTests and MapModeExecutionTests failed to compile in my environment (CS0117 on GeneratedMessagePackResolver/MyGeneratedCompositeResolver 'Instance', also in pre-existing files), so I could not run them.)
- ask: reviewer refusal `claude`: Generator behaviour (no CS8785) on duplicate/mixed keys (Established only by code reading; the new tests run the analyzer alone (CSharpCodeFixVerifier), not the generator.)
- ask: reviewer refusal `codex`: Whether the new tests fail on base and whether the existing suite is regression-free (No facts.json checks or executed test outcomes were available to inspect.)
- ask: risk score `risk`: score 59.6 (notify>=15, ask>=40, block>=130); largest: failed_checks 25 + area_sensitivity 20 + lines_changed 10.6
- notify: verified finding `claude:C2`: minor: Half of the new tests do not fail without the fix
- notify: verified finding `claude:C3`: minor: Generator now silently drops the duplicate/mismatched member instead of failing
- notify: trust cap `generator-analyzer-core`: generator-analyzer-core: AI may clear at most to notify (mandate clearance right)
- silent: trust cap `docs`: docs: AI may clear at most to silent (mandate clearance right)
- silent: trust cap `tests`: tests: AI may clear at most to silent (mandate clearance right)

</details>

## What the AI refused to decide, and why

- **REQ-2234-N2**: `cannot_determine` claude: 4 of the 8 new analyzer tests fail on base source (AD0001), so the fix is covered. SourceGenerator.Tests passes 175/175 on head. But the execution test projects (which include the 2 new execution tests) did not build in my environment, so I cannot establish 'no regressions in the existing test suite'.; `cannot_determine` codex: The added tests cover the stated scenarios, but the available repository review context contains no execution results and does not establish that the tests fail without the fix or that the full suite has no regressions.
- **claude** refused: Which branch this change targets, and therefore whether it resolves issue #2234 for users. Why: The reported regression lives on master/v3.1.x, not on the base of this change. Whether the change is meant for that line, or whether a separate fix is needed there, is a release-management decision I cannot make from the code.. Who should decide: maintainer / release owner
- **claude** refused: No regressions in execution tests (including the 2 new SuppressedSourceGenerationTests). Why: ExecutionTests and MapModeExecutionTests failed to compile in my environment (CS0117 on GeneratedMessagePackResolver/MyGeneratedCompositeResolver 'Instance', also in pre-existing files), so I could not run them.. Who should decide: CI / build owner (facts stage)
- **claude** refused: Generator behaviour (no CS8785) on duplicate/mixed keys. Why: Established only by code reading; the new tests run the analyzer alone (CSharpCodeFixVerifier), not the generator.. Who should decide: source generator area owner
- **codex** refused: Whether the new tests fail on base and whether the existing suite is regression-free. Why: No facts.json checks or executed test outcomes were available to inspect.. Who should decide: MessagePack source generator maintainer

## Requirement trace

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-2234-F1 | proven | claude: met (4/6 verified), codex: met (4/4 verified) | build: pass, tests.targeted: pass | - |
| REQ-2234-F2 | proven | claude: met (5/5 verified), codex: met (3/3 verified) | build: pass, tests.targeted: pass | - |
| REQ-2234-N1 | proven | claude: met (6/7 verified), codex: met (4/4 verified) | build: pass, tests.full_suite: pass | - |
| REQ-2234-N2 | refused | claude: cannot_determine (3/3 verified), codex: cannot_determine (2/2 verified) | build: pass, tests.fail_without_fix: pass | cannot_determine |

## What was checked, and by whom

| Check | Status | Tool | Summary |
|---|---|---|---|
| build | pass | dotnet build 8.0.402 | 0 errors, 1 unique warnings |
| tests.targeted | pass | dotnet test 8.0.402 | 8 passed, 0 failed, 0 skipped (8 new tests in run) |
| tests.fail_without_fix | pass | dotnet test (source reverted, tests kept) 8.0.402 | new tests fail on base source: 4/8 failed -> tests do cover the change (4 new tests pass without the fix) |
| tests.full_suite | pass | dotnet test 8.0.402 | tests/MessagePack.SourceGenerator.Tests: 175 tests, 175 passed, 0 failed (0 not failing on base, 0 also failing on base) |
| public_api | pass | git diff of PublicAPI.*.txt + scan of added public/protected declarations in src/  | no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or removed in src/ |
| analyzers | pass | dotnet build warnings (Roslyn analyzers, StyleCop, PublicApiAnalyzers) vs base  | no new warnings |
| tests.targeted.execution | pass | dotnet build + dotnet test (ExecutionTests, MapModeExecutionTests) 9.0.321 | SuppressedSourceGenerationTests: 4 passed, 0 failed (4 new test results; runtime: generator runs inside csc, no CS9057) |
| tests.execution_fail_without_fix | fail | dotnet test (source reverted, tests kept) - ExecutionTests 9.0.321 | new runtime tests pass on base source: 0/4 failed -> these runtime tests do NOT demonstrate the change (runtime behaviour they check is identical with and without the fix) |
| tests.execution_full_suite | pass | dotnet test (whole ExecutionTests, MapModeExecutionTests) vs base 9.0.321 | tests/MessagePack.SourceGenerator.ExecutionTests: 16/16 passed (base 14/14), 0 failures not on base; tests/MessagePack.SourceGenerator.MapModeExecutionTests: 22/22 passed (base 20/20), 0 failures not on base |

| Reviewer | Model | Prompt | Verified findings | Rejected | Refusals |
|---|---|---|---|---|---|
| claude | claude-opus-5-5 (Anthropic) | review-v1 | 3 | 0 | 3 |
| codex | GPT-6 Codex (OpenAI) | review-v1 | 0 | 0 | 1 |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v1 (ef0e95521f7e)

## What the AI found (verified findings)

- **claude:C1** [major, correctness] Change does not address the regression the issue reports; it fixes a different, pre-existing crash -> tier ask
  The issue says the analyzer stopped working for SuppressSourceGeneration types in 3.1.1. That regression is commit 1a74a620 ('stop collect field when object marked SuppressSourceGeneration'), which moved the 'if (suppressSourceGeneration is true) return null;' ahead of the member loop. It is on origin/master and the v3.1.x tags, but it is NOT an ancestor of base 32258fdb. In the base, the return is still after the member loop (line 1369), the same as v3.1.0, and suppressed types are already validated: MemberWithoutKeyIsReported, AllowPrivateRequiredIsReported, MemberTypeMustBeMessagePackObjectIsReported and SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed all pass against base source. The change actually fixes the analyzer crash (AD0001) on duplicate or mixed keys. That crash is not specific to suppressed types (DuplicateKeysAreReportedWithoutAnalyzerFailureForGeneratedTypes fails on base too). It also exists in v3.1.0, so it is not the 3.1.1 regression. If this change is merged into the 3.1.x line where users hit the bug, the issue stays unfixed, because the early return still skips all member checks.
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1369` @base: `if (suppressSourceGeneration is true)` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1369 at base 32258fdb)
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1022` @base: `intMembers.Add(member.IntKey, (member, item.Type));` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1022 at base 32258fdb)
    - [OK] `tests/MessagePack.SourceGenerator.Tests/SuppressSourceGenerationAnalyzerTests.cs:147` @head: `public async Task DuplicateKeysAreReportedWithoutAnalyzerFailureForGeneratedTypes()` (quote matches tests/MessagePack.SourceGenerator.Tests/SuppressSourceGenerationAnalyzerTests.cs:147 at head 9007cee1)
    - [REJECTED] https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2234 (issue text cannot be verified offline (not counted as evidence))
- **claude:C2** [minor, tests] Half of the new tests do not fail without the fix -> tier notify
  Run against base TypeCollector.cs, 4 of the 8 new analyzer tests pass: MemberWithoutKey, AllowPrivateRequired, MemberTypeMustBeMessagePackObject and SourceGenerationOnlyDiagnostics. The two new execution tests check run-time behaviour of the dynamic resolver, which the change does not touch. These tests document existing behaviour; they are not regression tests for the change.
    - [OK] `tests/MessagePack.SourceGenerator.Tests/SuppressSourceGenerationAnalyzerTests.cs:21` @head: `public async Task MemberWithoutKeyIsReported()` (quote matches tests/MessagePack.SourceGenerator.Tests/SuppressSourceGenerationAnalyzerTests.cs:21 at head 9007cee1)
    - [OK] `tests/MessagePack.SourceGenerator.Tests/SuppressSourceGenerationAnalyzerTests.cs:39` @head: `public async Task AllowPrivateRequiredIsReported()` (quote matches tests/MessagePack.SourceGenerator.Tests/SuppressSourceGenerationAnalyzerTests.cs:39 at head 9007cee1)
    - [OK] `tests/MessagePack.SourceGenerator.ExecutionTests/SuppressedSourceGenerationTests.cs:27` @head: `public void SuppressedTypeRoundTripsThroughDynamicResolver()` (quote matches tests/MessagePack.SourceGenerator.ExecutionTests/SuppressedSourceGenerationTests.cs:27 at head 9007cee1)
- **claude:C3** [minor, correctness] Generator now silently drops the duplicate/mismatched member instead of failing -> tier notify
  For non-suppressed types the generator (reportDiagnostic == null) used to throw on duplicate or mixed keys. Now it skips the offending member and emits a formatter without it. That is safe only while MsgPack005 (Error) is reported by the analyzer. If the analyzer is disabled or MsgPack005 is downgraded via .editorconfig, the build succeeds with a formatter that silently omits a member.
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1008` @head: `continue; // The key kind does not match the other members` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1008 at head 9007cee1)
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1023` @head: `if (!intMembers.ContainsKey(member.IntKey))` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1023 at head 9007cee1)
    - [OK] `src/MessagePack.SourceGenerator/Analyzers/MsgPack00xMessagePackAnalyzer.cs:43` @base: `private const DiagnosticSeverity InvalidMessagePackObjectSeverity = DiagnosticSeverity.Error;` (quote matches src/MessagePack.SourceGenerator/Analyzers/MsgPack00xMessagePackAnalyzer.cs:43 at base 32258fdb)

## Rejected: unsupported claims

- None.

## What was not checked, and why

- `tests.MessagePack.Tests` (facts.json not_run): runtime library src/MessagePack not modified by the change; suite not run
- `build.net472/netstandard` (facts.json not_run): only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks` (facts.json not_run): no runtime serialization hot path touched (generator/analyzer only)
- `other-targets` (mandate known gap): Tests run on net8.0 only; .NET Framework, Unity and NativeAOT targets are not exercised
- `runtime-perf` (mandate known gap): No benchmarks unless a perf-sensitive path is touched; allocation and throughput regressions can slip through
- `semantic-intent` (mandate known gap): Correctness beyond what tests and cited evidence show is not established by the AI
- `provenance` (mandate known gap): Licensing and provenance of agent-written code are not checked

## Residual risk

- REQ-2234-N2 not proven: cannot_determine
- Reviewer refusal (claude): Which branch this change targets, and therefore whether it resolves issue #2234 for users
- Reviewer refusal (claude): No regressions in execution tests (including the 2 new SuppressedSourceGenerationTests)
- Reviewer refusal (claude): Generator behaviour (no CS8785) on duplicate/mixed keys
- Reviewer refusal (codex): Whether the new tests fail on base and whether the existing suite is regression-free
- Open major finding claude:C1: Change does not address the regression the issue reports; it fixes a different, pre-existing crash
- tests.MessagePack.Tests not run (runtime library src/MessagePack not modified by the change; suite not run)
- build.net472/netstandard not run (only the net8.0 slice of src/MessagePack was built (Linux container, Debug))
- benchmarks not run (no runtime serialization hot path touched (generator/analyzer only))
- Standing gaps of this pipeline: other-targets, runtime-perf, semantic-intent, provenance (see not checked)

## Risk score: 59.6 -> ask

| Factor | Points | Reason |
|---|---:|---|
| area_sensitivity | 20 | most sensitive area touched: generator-analyzer-core (high) |
| files_changed | 4 | 4 files x 1 (cap 20) |
| lines_changed | 10.6 | 266 non-generated lines x 4/100 (cap 20) |
| generated_files | 0.0 | 0 generated files x 0.1 (cap 10) |
| public_api_change | 0 | public_api check: no change |
| source_without_tests | 0 | tests changed alongside source |
| security_sensitive_paths | 0 | none touched |
| fail_without_fix_not_shown | 0 | tests.fail_without_fix: pass |
| reviewer_disagreement | 0 | 0 clause(s) x 8 |
| failed_checks | 25 | 1 failed check(s) x 25: tests.execution_fail_without_fix |
| **total** | **59.6** | bands: {'notify': 15, 'ask': 40, 'block': 130} |

## Sign-off

Owner: **Toivo** (FYI: Rene)
Sign-off required: yes; allowed decisions: accept, reject, request-changes

> I, Toivo, have read what was checked and by whom, what was not checked and why, and the residual risk listed in this pack, and I own this decision.

```
countersign sign 2234 --as Toivo --decision <accept|reject|request-changes> --note "..."
```
