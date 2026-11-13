# Evidence pack: change 2297

**Recommended tier: BLOCK** · owner **Toivo** · risk score 64.5

Branch `ju26-issue-2297` (32258fdb..a0aa5ab2), 237 files, +1383 -9. Author Stelian Vultur (agent-written: True). Commit: implement issue #2297 : Add ExcludeFromCodeCoverage attribute to generated code

Mandate `messagepack-csharp` v1 sha256 `ef0e95521f7e364a`, signature: valid, Toivo

## Why this tier

- **block** from mandate rule `split-large-change`: More than 50 files changed: split the change so each part can be reviewed [237 files changed]

<details><summary>All tier drivers</summary>

- block: mandate rule `split-large-change`: More than 50 files changed: split the change so each part can be reviewed [237 files changed]
- ask: mandate rule `generated-files`: More than 10 generated files: a human confirms the regeneration is intended [228 generated files]
- ask: verified finding `claude:C1`: major: Preprocessor guard excludes netstandard2.0 and .NET Framework based on a false premise
- ask: verified finding `claude:C2`: major: Attribute on the generated half of user-declared partial resolvers can break builds (CS0579) and silently hides user code
- ask: refused clause `REQ-2297-F1`: not_met: claude: The attribute is added to every generated formatter and resolver type (new test passes on head, fails on base), but every occurrence is wrapped in '#if !NETSTANDARD2_0 && !NETFRAMEWORK' on the false premise that the attribute does not exist there. It does exist in netstandard2.0 and .NET Framework 4.0+, so consumers on those targets still get no exclusion, while the issue asks for all generated code to be decorated.; reviewers_disagree: claude says not_met, codex says cannot_determine; cannot_determine: codex: This scoped review did not inspect generated outputs across all formatter, resolver, and template paths to establish complete coverage of the requested attribute.
- ask: reviewer refusal `claude`: Line-by-line review of the 222 regenerated *.g.cs snapshot files (Mechanically generated; I relied on the SourceGenerator.Tests snapshot comparison (169/169 pass on head) instead of reading each file, so I make no claim about individual snapshot contents.)
- ask: reviewer refusal `claude`: Whether [GeneratedCode] should be emitted as well, and whether the maintainers want this at all vs. coverage-tool configuration (Product decision; the issue thread asks the maintainer and has no answer.)
- ask: reviewer refusal `claude`: Behaviour with specific coverage tools (coverlet, dotnet-coverage) on consumer projects (Needs runtime coverage runs I did not perform.)
- ask: reviewer refusal `codex`: Whether all generated code receives ExcludeFromCodeCoverage (The change touches many templates and checked-in generated snapshots; this scoped review did not verify every generation path or the associated tests.)
- ask: risk score `risk`: score 64.5 (notify>=15, ask>=40, block>=130); largest: area_sensitivity 20 + files_changed 20 + generated_files 10
- notify: trust cap `generator-analyzer-core`: generator-analyzer-core: AI may clear at most to notify (mandate clearance right)
- silent: trust cap `docs`: docs: AI may clear at most to silent (mandate clearance right)
- silent: trust cap `tests`: tests: AI may clear at most to silent (mandate clearance right)

</details>

## What the AI refused to decide, and why

- **REQ-2297-F1**: `not_met` claude: The attribute is added to every generated formatter and resolver type (new test passes on head, fails on base), but every occurrence is wrapped in '#if !NETSTANDARD2_0 && !NETFRAMEWORK' on the false premise that the attribute does not exist there. It does exist in netstandard2.0 and .NET Framework 4.0+, so consumers on those targets still get no exclusion, while the issue asks for all generated code to be decorated.; `reviewers_disagree` claude says not_met, codex says cannot_determine; `cannot_determine` codex: This scoped review did not inspect generated outputs across all formatter, resolver, and template paths to establish complete coverage of the requested attribute.
- **claude** refused: Line-by-line review of the 222 regenerated *.g.cs snapshot files. Why: Mechanically generated; I relied on the SourceGenerator.Tests snapshot comparison (169/169 pass on head) instead of reading each file, so I make no claim about individual snapshot contents.. Who should decide: source generator area owner
- **claude** refused: Whether [GeneratedCode] should be emitted as well, and whether the maintainers want this at all vs. coverage-tool configuration. Why: Product decision; the issue thread asks the maintainer and has no answer.. Who should decide: maintainer
- **claude** refused: Behaviour with specific coverage tools (coverlet, dotnet-coverage) on consumer projects. Why: Needs runtime coverage runs I did not perform.. Who should decide: area owner / QA
- **codex** refused: Whether all generated code receives ExcludeFromCodeCoverage. Why: The change touches many templates and checked-in generated snapshots; this scoped review did not verify every generation path or the associated tests.. Who should decide: MessagePack source generator maintainer

## Requirement trace

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-2297-F1 | refused | claude: not_met (4/6 verified), codex: cannot_determine (1/1 verified) | build: pass, tests.targeted: pass | not_met; reviewers_disagree; cannot_determine |

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
| claude | claude-opus-5-5 (Anthropic) | review-v1 | 3 | 0 | 3 |
| codex | GPT-6 Codex (OpenAI) | review-v1 | 0 | 0 | 1 |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v1 (ef0e95521f7e)

## What the AI found (verified findings)

- **claude:C1** [major, correctness] Preprocessor guard excludes netstandard2.0 and .NET Framework based on a false premise -> tier ask
  System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverageAttribute ships in .NET Framework 4.0+ (System.dll) and in netstandard2.0 (netstandard.dll). I confirmed it in the reference assemblies on this machine and by compiling a netstandard2.0 project that uses it. The guard means consumers targeting netstandard2.0 or any .NET Framework, which includes many library and Unity-adjacent consumers, get no exclusion. The README and test comment state the false premise as fact, and the second new test locks the guard in.
    - [OK] `src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt:14` @head: `#if !NETSTANDARD2_0 && !NETFRAMEWORK` (quote matches src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt:14 at head a0aa5ab2)
    - [OK] `tests/MessagePack.SourceGenerator.Tests/CodeCoverageExclusionTests.cs:19` @head: `private const string Guard = "#if !NETSTANDARD2_0 && !NETFRAMEWORK";` (quote matches tests/MessagePack.SourceGenerator.Tests/CodeCoverageExclusionTests.cs:19 at head a0aa5ab2)
    - [OK] `README.md:1640` @head: `(not `netstandard2.0` or .NET Framework)` (quote matches README.md:1640 at head a0aa5ab2)
- **claude:C2** [major, correctness] Attribute on the generated half of user-declared partial resolvers can break builds (CS0579) and silently hides user code -> tier ask
  The resolver and composite resolver templates emit '[ExcludeFromCodeCoverage] partial class <ResolverName>' for a class the user declares as partial. ExcludeFromCodeCoverageAttribute has AllowMultiple = false. A user who already put [ExcludeFromCodeCoverage] on their partial resolver declaration will get error CS0579 'Duplicate attribute' after upgrading on the targets where the guard is active (I reproduced CS0579 with two partial declarations each carrying the attribute). Even without a conflict, the attribute applies to the whole type, so any hand-written members in the user's partial resolver are now excluded from coverage too.
    - [OK] `src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt:15` @head: `[global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage]` (quote matches src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt:15 at head a0aa5ab2)
    - [OK] `src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt:17` @head: `partial class <#= ResolverName.Name #> : MsgPack::IFormatterResolver` (quote matches src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt:17 at head a0aa5ab2)
    - [OK] `src/MessagePack.SourceGenerator/Transforms/CompositeResolverTemplate.tt:8` @head: `[global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage]` (quote matches src/MessagePack.SourceGenerator/Transforms/CompositeResolverTemplate.tt:8 at head a0aa5ab2)
    - [OK] `src/MessagePack.SourceGenerator/Transforms/CompositeResolverTemplate.tt:10` @head: `partial class <#= ResolverName.Name #> : MsgPack::IFormatterResolver` (quote matches src/MessagePack.SourceGenerator/Transforms/CompositeResolverTemplate.tt:10 at head a0aa5ab2)
- **claude:C3** [info, scope] Unrelated-looking whitespace change in TransformUtilities is required by the change but widens the snapshot churn -> tier silent
  The brace emitted after a nesting type with constraints now ends with a newline. This is needed because a '#if' directive must start its own line, but it also changes generated output for nested generic types independently of the attribute. Covered by snapshot tests that pass.
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

- REQ-2297-F1 not proven: not_met; reviewers_disagree; cannot_determine
- Reviewer refusal (claude): Line-by-line review of the 222 regenerated *.g.cs snapshot files
- Reviewer refusal (claude): Whether [GeneratedCode] should be emitted as well, and whether the maintainers want this at all vs. coverage-tool configuration
- Reviewer refusal (claude): Behaviour with specific coverage tools (coverlet, dotnet-coverage) on consumer projects
- Reviewer refusal (codex): Whether all generated code receives ExcludeFromCodeCoverage
- Open major finding claude:C1: Preprocessor guard excludes netstandard2.0 and .NET Framework based on a false premise
- Open major finding claude:C2: Attribute on the generated half of user-declared partial resolvers can break builds (CS0579) and silently hides user code
- tests.execution not run (SDK 8.0.402 ships Roslyn 4.11 but MessagePack.SourceGenerator references Microsoft.CodeAnalysis 4.12.0, so csc refuses to load the generator (warning CS9057) and projects that consume it as an analyzer (tests/MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) fail to compile (CS0117 'GeneratedMessagePackResolver' does not contain 'Instance'). This also happens on base 32258fdb, so it is an environment/toolchain mismatch, not caused by the change. Needs an SDK with Roslyn >= 4.12 (e.g. .NET SDK 9.0.1xx); swapping in a newer compiler toolset was not permitted in this run.)
- tests.MessagePack.Tests not run (runtime library src/MessagePack not modified by the change; suite not run)
- build.net472/netstandard not run (only the net8.0 slice of src/MessagePack was built (Linux container, Debug))
- benchmarks not run (no runtime serialization hot path touched (generator/analyzer only))
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
