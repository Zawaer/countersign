# Evidence pack: change 2297

**Recommended tier: BLOCK** · owner **Toivo** · risk score 64.5

Branch `ju26-issue-2297` (32258fdb..a0aa5ab2), 237 files, +1383 -9. Author Stelian Vultur (agent-written: True). Commit: implement issue #2297 : Add ExcludeFromCodeCoverage attribute to generated code

Mandate `messagepack-csharp` v2 sha256 `39cc2060685638e1`, signature: valid, Toivo

## Why this tier

- **block** from mandate rule `split-large-change`: More than 50 files changed: split the change so each part can be reviewed [237 files changed]

<details><summary>All tier drivers</summary>

- block: mandate rule `split-large-change`: More than 50 files changed: split the change so each part can be reviewed [237 files changed]
- ask: mandate rule `generated-files`: More than 10 generated files: a human confirms the regeneration is intended [228 generated files]
- ask: verified finding `claude:C1`: major: Coverage attribute is suppressed for netstandard2.0 and .NET Framework consumers based on a false premise
- ask: refused clause `REQ-2297-F1`: missing_review: nemotron gave no verdict; not_met: claude: On net5+ consumers the attribute is emitted on every generated type (AllGeneratedTypesAreExcludedFromCodeCoverage passes at head and fails on base). But every emission is wrapped in '#if !NETSTANDARD2_0 && !NETFRAMEWORK', which is evaluated in the consumer's compilation, so consumers targeting netstandard2.0 or .NET Framework get no attribute. The stated reason ('not available on netstandard2.0 or .NET Framework') is wrong: System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverageAttribute is in the netstandard 2.0 reference assembly (I checked netstandard.library 2.0.3's netstandard.xml) and has been in .NET Framework since 4.0, with AttributeTargets.Class allowed. So for targets MessagePack supports, the requirement is not met, and a test pins the omission.; reviewers_disagree: claude says not_met, codex says met
- ask: reviewer refusal `claude`: Whether all 228 regenerated test resource files differ from base only by the coverage attribute and the brace/newline fix (Scoped review: not read individually. tests.full_suite passing shows they match the new generator output, not that the output is otherwise unchanged.)
- ask: reviewer refusal `claude`: Effect on generated code in consumers built with older compilers or with ImplicitUsings/nullable settings (Execution tests not run for this change (tests.execution not run: SDK 8 cannot load the generator); no compile of generated code against net472/netstandard2.0 targets.)
- ask: reviewer refusal `claude`: The TransformUtilities brace change ('{' to '{\r\n' when constraints exist): intended fix or incidental (Not mentioned in the issue; I did not establish what output it changes beyond the resources.)
- ask: reviewer refusal `codex`: Coverage of generated code not exercised by the supplied generator test fixture (The supplied tests exercise the generated output represented by their fixture; I did not independently inspect every generation path or framework configuration beyond the cited template and facts.)
- ask: risk score `risk`: score 64.5 (notify>=15, ask>=40, block>=130); largest: area_sensitivity 20 + files_changed 20 + generated_files 10
- notify: trust cap `generator-analyzer-core`: generator-analyzer-core: AI may clear at most to notify (mandate clearance right)
- silent: trust cap `docs`: docs: AI may clear at most to silent (mandate clearance right)
- silent: trust cap `tests`: tests: AI may clear at most to silent (mandate clearance right)

</details>

## What the AI refused to decide, and why

- **REQ-2297-F1**: `missing_review` nemotron gave no verdict; `not_met` claude: On net5+ consumers the attribute is emitted on every generated type (AllGeneratedTypesAreExcludedFromCodeCoverage passes at head and fails on base). But every emission is wrapped in '#if !NETSTANDARD2_0 && !NETFRAMEWORK', which is evaluated in the consumer's compilation, so consumers targeting netstandard2.0 or .NET Framework get no attribute. The stated reason ('not available on netstandard2.0 or .NET Framework') is wrong: System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverageAttribute is in the netstandard 2.0 reference assembly (I checked netstandard.library 2.0.3's netstandard.xml) and has been in .NET Framework since 4.0, with AttributeTargets.Class allowed. So for targets MessagePack supports, the requirement is not met, and a test pins the omission.; `reviewers_disagree` claude says not_met, codex says met
- **claude** refused: Whether all 228 regenerated test resource files differ from base only by the coverage attribute and the brace/newline fix. Why: Scoped review: not read individually. tests.full_suite passing shows they match the new generator output, not that the output is otherwise unchanged.. Who should decide: source-generator area owner (diff-filter the resources)
- **claude** refused: Effect on generated code in consumers built with older compilers or with ImplicitUsings/nullable settings. Why: Execution tests not run for this change (tests.execution not run: SDK 8 cannot load the generator); no compile of generated code against net472/netstandard2.0 targets.. Who should decide: source-generator area owner
- **claude** refused: The TransformUtilities brace change ('{' to '{\r\n' when constraints exist): intended fix or incidental. Why: Not mentioned in the issue; I did not establish what output it changes beyond the resources.. Who should decide: source-generator area owner
- **codex** refused: Coverage of generated code not exercised by the supplied generator test fixture. Why: The supplied tests exercise the generated output represented by their fixture; I did not independently inspect every generation path or framework configuration beyond the cited template and facts.. Who should decide: area owner

_2 disputed item(s), not adjudicated: REQ-2297-F1, finding:claude:C1_

## Who reviewed

Participating reviewers: claude, codex, nemotron. Adjudicator: gemini. Confidential: no. Rule: proven needs every participating reviewer to say met with verified evidence, and the clause's checks to pass.

## Requirement trace

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-2297-F1 | refused | claude: not_met (6/6 verified), codex: met (4/4 verified) | build: pass, tests.targeted: pass | missing_review; not_met; reviewers_disagree |

## What was checked, and by whom

| Check | Status | Tool | Summary |
|---|---|---|---|
| build | pass | dotnet build 8.0.402 | 0 errors, 1 unique warnings |
| tests.targeted | pass | dotnet test 8.0.402 | 2 passed, 0 failed, 0 skipped (2 new tests in run) |
| tests.fail_without_fix | pass | dotnet test (source reverted, tests kept) 8.0.402 | new tests fail on base source: 2/2 failed -> tests do cover the change |
| tests.full_suite | pass | dotnet test 8.0.402 | tests/MessagePack.SourceGenerator.Tests: 169 tests, 169 passed, 0 failed (0 not failing on base, 0 also failing on base) |
| public_api | pass | git diff of PublicAPI.*.txt + scan of added public/protected declarations in src/  | no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or removed in src/ |
| analyzers | pass | dotnet build warnings (Roslyn analyzers, StyleCop, PublicApiAnalyzers) vs base  | no new warnings |

| Reviewer | Model | Prompt | Verified findings | Rejected | Refusals |
|---|---|---|---|---|---|
| claude | claude-opus-5-5 (Anthropic) | review-v1 | 2 | 0 | 3 |
| codex | GPT-6 (OpenAI) | review-v1 | 0 | 0 | 1 |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v2 (39cc20606856)

## What the AI found (verified findings)

- **claude:C1** [major, correctness] Coverage attribute is suppressed for netstandard2.0 and .NET Framework consumers based on a false premise -> tier ask
  The templates guard the attribute with '#if !NETSTANDARD2_0 && !NETFRAMEWORK'. ExcludeFromCodeCoverageAttribute exists in netstandard2.0 and in .NET Framework 4.0+, so the guard only removes the feature for Unity/.NET Framework/netstandard library consumers. The test ExcludeAttributeIsGuardedForTargetsWhereItIsUnavailable pins this behaviour, and the README claims 'All generated formatters and resolvers are decorated', which is false for those targets.
    - [OK] `src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt:14` @head: `#if !NETSTANDARD2_0 && !NETFRAMEWORK` (quote matches src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt:14 at head a0aa5ab2)
    - [OK] `src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt:31` @head: `#if !NETSTANDARD2_0 && !NETFRAMEWORK` (quote matches src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt:31 at head a0aa5ab2)
    - [OK] `src/MessagePack.SourceGenerator/Transforms/FormatterTemplate.tt:14` @head: `#if !NETSTANDARD2_0 && !NETFRAMEWORK` (quote matches src/MessagePack.SourceGenerator/Transforms/FormatterTemplate.tt:14 at head a0aa5ab2)
    - [OK] `tests/MessagePack.SourceGenerator.Tests/CodeCoverageExclusionTests.cs:19` @head: `private const string Guard = "#if !NETSTANDARD2_0 && !NETFRAMEWORK";` (quote matches tests/MessagePack.SourceGenerator.Tests/CodeCoverageExclusionTests.cs:19 at head a0aa5ab2)
    - [OK] `README.md:1639` @head: `All generated formatters and resolvers are decorated with `[ExcludeFromCodeCoverage]`` (quote matches README.md:1639 at head a0aa5ab2)
    - [OK] test `CodeCoverageExclusionTests.ExcludeAttributeIsGuardedForTargetsWhereItIsUnavailable` passed (facts.json tests.targeted: passed (new test))
- **claude:C2** [info, scope] 237-file change is dominated by regenerated test resources -> tier silent
  228 of 237 files are regenerated expected-output resources. The behavioural change is in 7 template/source files. Reviewers should read the templates and spot-check the resources, not the reverse.
    - [OK] check `tests.full_suite` (facts.json: tests.full_suite pass: tests/MessagePack.SourceGenerator.Tests: 169 tests, 169 passed, 0 failed (0 not failing on base, 0 also failing on base))
    - [OK] `src/MessagePack.SourceGenerator/Transforms/TransformUtilities.cs:58` @head: `writer(anyConstraints ? "{\r\n" : " {\r\n");` (quote matches src/MessagePack.SourceGenerator/Transforms/TransformUtilities.cs:58 at head a0aa5ab2)

## Rejected: unsupported claims

- None.

## What was not checked, and why

- `tests.execution` (facts.json not_run): SDK 8.0.402 ships Roslyn 4.11 but MessagePack.SourceGenerator references Microsoft.CodeAnalysis 4.12.0, so csc refuses to load the generator (warning CS9057) and projects that consume it as an analyzer (tests/MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) fail to compile (CS0117 'GeneratedMessagePackResolver' does not contain 'Instance'). This also happens on base 32258fdb, so it is an environment/toolchain mismatch, not caused by the change. Needs an SDK with Roslyn >= 4.12 (e.g. .NET SDK 9.0.1xx); swapping in a newer compiler toolset was not permitted in this run.
- `tests.MessagePack.Tests` (facts.json not_run): runtime library src/MessagePack not modified by the change; suite not run
- `build.net472/netstandard` (facts.json not_run): only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks` (facts.json not_run): no runtime serialization hot path touched (generator/analyzer only)
- `other-targets` (mandate known gap): Tests run on net8.0 only; .NET Framework, Unity and NativeAOT targets are not exercised
- `runtime-perf` (mandate known gap): No benchmarks unless a perf-sensitive path is touched; allocation and throughput regressions can slip through
- `semantic-intent` (mandate known gap): Correctness beyond what tests and cited evidence show is not established by the AI
- `provenance` (mandate known gap): Licensing and provenance of agent-written code are not checked

## Residual risk

- REQ-2297-F1 not proven: missing_review; not_met; reviewers_disagree
- Reviewer refusal (claude): Whether all 228 regenerated test resource files differ from base only by the coverage attribute and the brace/newline fix
- Reviewer refusal (claude): Effect on generated code in consumers built with older compilers or with ImplicitUsings/nullable settings
- Reviewer refusal (claude): The TransformUtilities brace change ('{' to '{\r\n' when constraints exist): intended fix or incidental
- Reviewer refusal (codex): Coverage of generated code not exercised by the supplied generator test fixture
- Open major finding claude:C1: Coverage attribute is suppressed for netstandard2.0 and .NET Framework consumers based on a false premise
- tests.execution not run (SDK 8.0.402 ships Roslyn 4.11 but MessagePack.SourceGenerator references Microsoft.CodeAnalysis 4.12.0, so csc refuses to load the generator (warning CS9057) and projects that consume it as an analyzer (tests/MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) fail to compile (CS0117 'GeneratedMessagePackResolver' does not contain 'Instance'). This also happens on base 32258fdb, so it is an environment/toolchain mismatch, not caused by the change. Needs an SDK with Roslyn >= 4.12 (e.g. .NET SDK 9.0.1xx); swapping in a newer compiler toolset was not permitted in this run.)
- tests.MessagePack.Tests not run (runtime library src/MessagePack not modified by the change; suite not run)
- build.net472/netstandard not run (only the net8.0 slice of src/MessagePack was built (Linux container, Debug))
- benchmarks not run (no runtime serialization hot path touched (generator/analyzer only))
- 2 disputed item(s) were not adjudicated (adjudicator gemini has not run)
- Standing gaps of this pipeline: other-targets, runtime-perf, semantic-intent, provenance (see not checked)

## Risk score: 64.5 -> ask

| Factor | Points | Reason |
|---|---:|---|
| area_sensitivity | 20 | most sensitive area touched: generator-analyzer-core (high) |
| files_changed | 20 | 237 files x 1 (cap 20) |
| lines_changed | 6.5 | 162 non-generated lines x 4/100 (cap 20) |
| generated_files | 10 | 228 generated files x 0.1 (cap 10) |
| public_api_change | 0 | public_api check: no change |
| source_without_tests | 0 | tests changed alongside source |
| security_sensitive_paths | 0 | none touched |
| fail_without_fix_not_shown | 0 | tests.fail_without_fix: pass |
| reviewer_disagreement | 8 | 1 clause(s) x 8: REQ-2297-F1 |
| failed_checks | 0 | 0 failed check(s) x 25 |
| **total** | **64.5** | bands: {'notify': 15, 'ask': 40, 'block': 130} |

## Sign-off

Owner: **Toivo** (FYI: Rene)
Sign-off required: yes; allowed decisions: reject, request-changes

> I, Toivo, have read what was checked and by whom, what was not checked and why, and the residual risk listed in this pack, and I own this decision.

```
countersign sign 2297 --as Toivo --decision <accept|reject|request-changes> --note "..."
```
