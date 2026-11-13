# Evidence pack: change 2129

**Recommended tier: BLOCK** · owner **Toivo** · risk score 145.2

Branch `ju26-issue-2129` (32258fdb..083afd99), 28 files, +1034 -9. Author Stelian Vultur (agent-written: True). Commit: Agentic implementation of #2129 Feature Request: Allow generation of Formatter for a type in a referenced assembly

Mandate `messagepack-csharp` v1 sha256 `ef0e95521f7e364a`, signature: valid, Toivo

## Why this tier

- **block** from risk score `risk`: score 145.2 (notify>=15, ask>=40, block>=130); largest: failed_checks 50 + area_sensitivity 35 + files_changed 20

<details><summary>All tier drivers</summary>

- block: risk score `risk`: score 145.2 (notify>=15, ask>=40, block>=130); largest: failed_checks 50 + area_sensitivity 35 + files_changed 20
- ask: mandate rule `public-api-change`: Public API changed: the owner decides on compatibility [public API added: new public class MessagePack.GeneratedMessagePackFormatterAttribute (with public Type? SurrogateType) in src/MessagePack.Annotations/Attributes.cs; MessagePack.Annotations has no PublicAPI.*.txt tracking so PublicApiAnalyzers did not flag it. Also 4 new public DiagnosticDescriptors MsgPack019-022 (analyzer assembly) and 4 rows added to AnalyzerReleases.Unshipped.md]
- ask: refused clause `REQ-2129-F1`: cannot_determine: claude: The feature is implemented: a [GeneratedMessagePackFormatter] attribute, a generator pipeline that writes the partial formatter body, and a surrogate mode. But the only tests I could run are 6 diagnostic tests. The successful path (generated formatter compiles, is registered, round-trips) is covered only by ExecutionTests, which did not build in my environment, and there is no generator snapshot test of the emitted code.; cannot_determine: codex: This scoped review did not trace the new referenced-type formatter request path end to end or establish the supported type and assembly cases.
- ask: reviewer refusal `claude`: Correctness of the generated formatter code (partial class emission in FormatterTemplate/StringKeyFormatterTemplate, structs, init-only and required members, callback receivers) (Needs the ExecutionTests to build and run; they failed to compile in my environment (CS0117 in pre-existing files too), and there is no snapshot test. I did not read the regenerated template .cs files line by line.)
- ask: reviewer refusal `claude`: Interaction with TypeCollector/analyzer when a [MessagePackObject] type has a member of the externally formatted type (MsgPack003 risk, double registration when T is in the same compilation) (The generator excludes [GeneratedMessagePackFormatter] classes from custom formatters (GeneratorUtilities) while the analyzer discovers formatters separately. Whether this yields the right diagnostics and a single registration needs a build I could not run.)
- ask: reviewer refusal `claude`: API and feature design (surrogate type, contractless default, diagnostic IDs MsgPack019-022) (Product and API design decision; the issue thread shows maintainers had not settled the design.)
- ask: reviewer refusal `claude`: Remaining files of the 28 (doc/analyzers/MsgPack019-022.md content, AnalyzerReleases.Unshipped.md, test project wiring) (Scoped review by instruction; read once for consistency but not verified against behaviour.)
- ask: reviewer refusal `codex`: Whether formatter generation for referenced-assembly types fully meets the feature request (Only the diff summary and requirement were reviewed; the implementation path, edge cases, and execution tests were not traced.)
- ask: trust cap `annotations-api`: annotations-api: AI may clear at most to ask (mandate clearance right)
- notify: verified finding `claude:C1`: minor: New diagnostics are reported by the source generator, not the analyzer, against the repo's convention
- notify: verified finding `claude:C2`: minor: Contractless mode ignores any serialization attributes already on the formatted type
- notify: verified finding `claude:C3`: minor: Successful path has no generator-level test
- notify: trust cap `generator-analyzer-core`: generator-analyzer-core: AI may clear at most to notify (mandate clearance right)
- notify: trust cap `build`: build: AI may clear at most to notify (mandate clearance right)
- silent: trust cap `docs`: docs: AI may clear at most to silent (mandate clearance right)
- silent: trust cap `tests`: tests: AI may clear at most to silent (mandate clearance right)

</details>

## What the AI refused to decide, and why

- **REQ-2129-F1**: `cannot_determine` claude: The feature is implemented: a [GeneratedMessagePackFormatter] attribute, a generator pipeline that writes the partial formatter body, and a surrogate mode. But the only tests I could run are 6 diagnostic tests. The successful path (generated formatter compiles, is registered, round-trips) is covered only by ExecutionTests, which did not build in my environment, and there is no generator snapshot test of the emitted code.; `cannot_determine` codex: This scoped review did not trace the new referenced-type formatter request path end to end or establish the supported type and assembly cases.
- **claude** refused: Correctness of the generated formatter code (partial class emission in FormatterTemplate/StringKeyFormatterTemplate, structs, init-only and required members, callback receivers). Why: Needs the ExecutionTests to build and run; they failed to compile in my environment (CS0117 in pre-existing files too), and there is no snapshot test. I did not read the regenerated template .cs files line by line.. Who should decide: source generator area owner, with CI results
- **claude** refused: Interaction with TypeCollector/analyzer when a [MessagePackObject] type has a member of the externally formatted type (MsgPack003 risk, double registration when T is in the same compilation). Why: The generator excludes [GeneratedMessagePackFormatter] classes from custom formatters (GeneratorUtilities) while the analyzer discovers formatters separately. Whether this yields the right diagnostics and a single registration needs a build I could not run.. Who should decide: source generator area owner
- **claude** refused: API and feature design (surrogate type, contractless default, diagnostic IDs MsgPack019-022). Why: Product and API design decision; the issue thread shows maintainers had not settled the design.. Who should decide: maintainer (API review)
- **claude** refused: Remaining files of the 28 (doc/analyzers/MsgPack019-022.md content, AnalyzerReleases.Unshipped.md, test project wiring). Why: Scoped review by instruction; read once for consistency but not verified against behaviour.. Who should decide: area owner
- **codex** refused: Whether formatter generation for referenced-assembly types fully meets the feature request. Why: Only the diff summary and requirement were reviewed; the implementation path, edge cases, and execution tests were not traced.. Who should decide: MessagePack source generator maintainer

## Requirement trace

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-2129-F1 | refused | claude: cannot_determine (4/6 verified), codex: cannot_determine (1/1 verified) | build: pass, tests.targeted: pass | cannot_determine |

## What was checked, and by whom

| Check | Status | Tool | Summary |
|---|---|---|---|
| build | pass | dotnet build 8.0.402 | 0 errors, 2 unique warnings |
| tests.targeted | pass | dotnet test 8.0.402 | 6 passed, 0 failed, 0 skipped (6 new tests in run) |
| tests.fail_without_fix | pass | dotnet test (source reverted, tests kept) 8.0.402 | new tests fail on base source: 6/6 failed -> tests do cover the change |
| tests.full_suite | pass | dotnet test 8.0.402 | tests/MessagePack.SourceGenerator.Tests: 173 tests, 173 passed, 0 failed (0 not failing on base, 0 also failing on base) |
| public_api | fail | git diff of PublicAPI.*.txt + scan of added public/protected declarations in src/  | public API added: new public class MessagePack.GeneratedMessagePackFormatterAttribute (with public Type? SurrogateType) in src/MessagePack.Annotations/Attributes.cs; MessagePack.Annotations has no PublicAPI.*.txt tracking so PublicApiAnalyzers did not flag it. Also 4 new public DiagnosticDescriptors MsgPack019-022 (analyzer assembly) and 4 rows added to AnalyzerReleases.Unshipped.md |
| analyzers | fail | dotnet build warnings (Roslyn analyzers, StyleCop, PublicApiAnalyzers) vs base  | 1 new warnings vs base |
| tests.targeted.execution | pass | dotnet build + dotnet test (ExecutionTests, MapModeExecutionTests) 9.0.321 | GeneratedFormatterForExternalTypesTests: 7 passed, 0 failed (7 new test results; runtime: generator runs inside csc, no CS9057); tests/MessagePack.SourceGenerator.MapModeExecutionTests: no tests match the filter (the test file is excluded from this project) |
| tests.execution_fail_without_fix | pass | dotnet test (source reverted, tests kept) - ExecutionTests 9.0.321 | new runtime tests do not compile with the source reverted (tests/MessagePack.SourceGenerator.ExecutionTests): 7 tests cannot exist without the fix; errors are the missing feature itself (see compile_failure) -> tests depend on the change |
| tests.execution_full_suite | pass | dotnet test (whole ExecutionTests, MapModeExecutionTests) vs base 9.0.321 | tests/MessagePack.SourceGenerator.ExecutionTests: 21/21 passed (base 14/14), 0 failures not on base; tests/MessagePack.SourceGenerator.MapModeExecutionTests: 20/20 passed (base 20/20), 0 failures not on base |
| solution_membership | fail | grep MessagePack.sln  | new project tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj is not added to MessagePack.sln (only referenced from ExecutionTests.csproj) |

| Reviewer | Model | Prompt | Verified findings | Rejected | Refusals |
|---|---|---|---|---|---|
| claude | claude-opus-5-5 (Anthropic) | review-v1 | 4 | 0 | 4 |
| codex | GPT-6 Codex (OpenAI) | review-v1 | 0 | 0 | 1 |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v1 (ef0e95521f7e)

## What the AI found (verified findings)

- **claude:C1** [minor, maintainability] New diagnostics are reported by the source generator, not the analyzer, against the repo's convention -> tier notify
  MsgPack019-022 are declared in MsgPack00xMessagePackAnalyzer and listed in its SupportedDiagnostics, but the analyzer never reports them. They are only reported by a separate generator pipeline. The generator also reuses analyzer descriptors (MsgPack004, MsgPack005, MsgPack010) for surrogate errors. The existing design deliberately keeps diagnostics out of the generator ('null when running in the context of a source generator so as to avoid duplicate diagnostics'). Generator diagnostics do not take part in analyzer configuration and run on every generator pass.
    - [OK] `src/MessagePack.SourceGenerator/MessagePackGenerator.cs:131` @head: `context.RegisterSourceOutput(generatedFormatterDiagnostics, static (context, diagnostic) => context.ReportDiagnostic(diagnostic));` (quote matches src/MessagePack.SourceGenerator/MessagePackGenerator.cs:131 at head 083afd99)
    - [OK] `src/MessagePack.SourceGenerator/Analyzers/MsgPack00xMessagePackAnalyzer.cs:385` @head: `SurrogateMemberNotFound);` (quote matches src/MessagePack.SourceGenerator/Analyzers/MsgPack00xMessagePackAnalyzer.cs:385 at head 083afd99)
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:218` @base: `This will be <see langword="null" /> when running in the context of a source generator so as to avoid duplicate diagnostics.` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:218 at base 32258fdb)
- **claude:C2** [minor, correctness] Contractless mode ignores any serialization attributes already on the formatted type -> tier notify
  Without a surrogate, members are chosen only by 'public read-write' and sorted by name. [IgnoreMember], [IgnoreDataMember], [DataMember]/[Key] and [MessagePackObject] on T are never consulted. The maintainer's direction in the issue was to use attributes if present and fall back to contractless otherwise. For a referenced type that does carry such attributes, the generated wire contract can differ from what the dynamic resolver produces for the same type.
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/GeneratedFormatterCollector.cs:133` @head: `List<ISymbol> targets = GetInstanceMembers(type).Where(IsPublicReadWrite).OrderBy(m => m.Name, StringComparer.Ordinal).ToList();` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/GeneratedFormatterCollector.cs:133 at head 083afd99)
    - [OK] `README.md:1655` @head: `By default the formatter serializes the type in *contractless* mode` (quote matches README.md:1655 at head 083afd99)
    - [REJECTED] https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2129 (issue text cannot be verified offline (not counted as evidence))
- **claude:C3** [minor, tests] Successful path has no generator-level test -> tier notify
  All 6 new SourceGenerator.Tests are negative diagnostic tests that hand-write the formatter members. No test snapshots or compiles the generated 'partial class' formatter body and resolver registration. The successful path is only covered by the ExecutionTests project (which also adds a new ExternalTypes project and edits MapModeExecutionTests to exclude the files).
    - [OK] `tests/MessagePack.SourceGenerator.Tests/GeneratedMessagePackFormatterTests.cs:20` @head: `// Formatter members are written by hand in the diagnostic tests, so the compiler accepts the source` (quote matches tests/MessagePack.SourceGenerator.Tests/GeneratedMessagePackFormatterTests.cs:20 at head 083afd99)
    - [OK] `tests/MessagePack.SourceGenerator.Tests/GeneratedMessagePackFormatterTests.cs:29` @head: `public async Task FormatterMustBePartial()` (quote matches tests/MessagePack.SourceGenerator.Tests/GeneratedMessagePackFormatterTests.cs:29 at head 083afd99)
- **claude:C4** [info, scope] New public API in MessagePack.Annotations -> tier silent
  The change adds a public attribute type with a public SurrogateType property to the shipped Annotations assembly. This is a permanent API commitment, and the design (surrogate vs. other options discussed in the issue) needs maintainer sign-off.
    - [OK] `src/MessagePack.Annotations/Attributes.cs:176` @head: `public Type? SurrogateType { get; set; }` (quote matches src/MessagePack.Annotations/Attributes.cs:176 at head 083afd99)

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

- REQ-2129-F1 not proven: cannot_determine
- Reviewer refusal (claude): Correctness of the generated formatter code (partial class emission in FormatterTemplate/StringKeyFormatterTemplate, structs, init-only and required members, callback receivers)
- Reviewer refusal (claude): Interaction with TypeCollector/analyzer when a [MessagePackObject] type has a member of the externally formatted type (MsgPack003 risk, double registration when T is in the same compilation)
- Reviewer refusal (claude): API and feature design (surrogate type, contractless default, diagnostic IDs MsgPack019-022)
- Reviewer refusal (claude): Remaining files of the 28 (doc/analyzers/MsgPack019-022.md content, AnalyzerReleases.Unshipped.md, test project wiring)
- Reviewer refusal (codex): Whether formatter generation for referenced-assembly types fully meets the feature request
- tests.MessagePack.Tests not run (runtime library src/MessagePack not modified by the change; suite not run)
- build.net472/netstandard not run (only the net8.0 slice of src/MessagePack was built (Linux container, Debug))
- benchmarks not run (no runtime serialization hot path touched (generator/analyzer only))
- Standing gaps of this pipeline: other-targets, runtime-perf, semantic-intent, provenance (see not checked)

## Risk score: 145.2 -> block

| Factor | Points | Reason |
|---|---:|---|
| area_sensitivity | 35 | most sensitive area touched: annotations-api (critical) |
| files_changed | 20 | 28 files x 1 (cap 20) |
| lines_changed | 20 | 1035 non-generated lines x 4/100 (cap 20) |
| generated_files | 0.2 | 2 generated files x 0.1 (cap 10) |
| public_api_change | 20 | public API changed |
| source_without_tests | 0 | tests changed alongside source |
| security_sensitive_paths | 0 | none touched |
| fail_without_fix_not_shown | 0 | tests.fail_without_fix: pass |
| reviewer_disagreement | 0 | 0 clause(s) x 8 |
| failed_checks | 50 | 2 failed check(s) x 25: analyzers, solution_membership |
| **total** | **145.2** | bands: {'notify': 15, 'ask': 40, 'block': 130} |

## Sign-off

Owner: **Toivo** (FYI: Rene)
Sign-off required: yes; allowed decisions: reject, request-changes

> I, Toivo, have read what was checked and by whom, what was not checked and why, and the residual risk listed in this pack, and I own this decision.

```
countersign sign 2129 --as Toivo --decision <accept|reject|request-changes> --note "..."
```
