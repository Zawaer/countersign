# Evidence pack: change 2129

**Recommended tier: BLOCK** · owner **Toivo** · risk score 145.2

Branch `ju26-issue-2129` (32258fdb..083afd99), 28 files, +1034 -9. Author Stelian Vultur (agent-written: True). Commit: Agentic implementation of #2129 Feature Request: Allow generation of Formatter for a type in a referenced assembly

Mandate `messagepack-csharp` v2 sha256 `39cc2060685638e1`, signature: valid, Toivo

## Why this tier

- **block** from risk score `risk`: score 145.2 (notify>=15, ask>=40, block>=130); largest: failed_checks 50 + area_sensitivity 35 + files_changed 20

<details><summary>All tier drivers</summary>

- block: risk score `risk`: score 145.2 (notify>=15, ask>=40, block>=130); largest: failed_checks 50 + area_sensitivity 35 + files_changed 20
- ask: mandate rule `public-api-change`: Public API changed: the owner decides on compatibility [public API added: new public class MessagePack.GeneratedMessagePackFormatterAttribute (with public Type? SurrogateType) in src/MessagePack.Annotations/Attributes.cs; MessagePack.Annotations has no PublicAPI.*.txt tracking so PublicApiAnalyzers did not flag it. Also 4 new public DiagnosticDescriptors MsgPack019-022 (analyzer assembly) and 4 rows added to AnalyzerReleases.Unshipped.md]
- ask: verified finding `claude:C1`: major: New public API in MessagePack.Annotations is not tracked by any PublicAPI file
- ask: refused clause `REQ-2129-F1`: missing_review: nemotron gave no verdict
- ask: reviewer refusal `claude`: Correctness of GeneratedFormatterCollector.cs and the MessagePackGenerator.cs pipeline changes beyond what the 7 execution and 6 generator tests exercise (generic formatters, nested/abstract types, interaction with existing [MessagePackObject] collection, incremental-generator caching) (Scoped review: I did not read these 300+ lines line by line. Tests show only the happy paths and the 4 diagnostics.)
- ask: reviewer refusal `claude`: Whether the API design (SurrogateType, contractless default for external types) is the right answer to the issue, which also asks for Union and other attribute-driven settings (Product/API design decision with permanent public surface; the issue proposes three alternatives and the change picks a fourth (surrogate type).)
- ask: reviewer refusal `claude`: Security/trust implications of generating formatters that access members of external types (e.g. non-public members) (Not examined in this scoped review.)
- ask: reviewer refusal `codex`: Full acceptance and compatibility review of the external formatter feature (This is a scoped review. The placeholder requirement contains only a broad feature statement; I did not comprehensively review all generator paths, API compatibility, or serialization contracts. The supplied facts also record a public API check failure, analyzer warning, and missing solution membership for the new test project.)
- ask: trust cap `annotations-api`: annotations-api: AI may clear at most to ask (mandate clearance right)
- notify: verified finding `claude:C2`: minor: New test-support project is not in MessagePack.sln
- notify: verified finding `claude:C3`: minor: New StyleCop warning SA1203 in the new test file
- notify: trust cap `generator-analyzer-core`: generator-analyzer-core: AI may clear at most to notify (mandate clearance right)
- notify: trust cap `build`: build: AI may clear at most to notify (mandate clearance right)
- silent: trust cap `docs`: docs: AI may clear at most to silent (mandate clearance right)
- silent: trust cap `tests`: tests: AI may clear at most to silent (mandate clearance right)

</details>

## What the AI refused to decide, and why

- **REQ-2129-F1**: `missing_review` nemotron gave no verdict
- **claude** refused: Correctness of GeneratedFormatterCollector.cs and the MessagePackGenerator.cs pipeline changes beyond what the 7 execution and 6 generator tests exercise (generic formatters, nested/abstract types, interaction with existing [MessagePackObject] collection, incremental-generator caching). Why: Scoped review: I did not read these 300+ lines line by line. Tests show only the happy paths and the 4 diagnostics.. Who should decide: source-generator area owner
- **claude** refused: Whether the API design (SurrogateType, contractless default for external types) is the right answer to the issue, which also asks for Union and other attribute-driven settings. Why: Product/API design decision with permanent public surface; the issue proposes three alternatives and the change picks a fourth (surrogate type).. Who should decide: MessagePack-CSharp maintainers
- **claude** refused: Security/trust implications of generating formatters that access members of external types (e.g. non-public members). Why: Not examined in this scoped review.. Who should decide: security champion
- **codex** refused: Full acceptance and compatibility review of the external formatter feature. Why: This is a scoped review. The placeholder requirement contains only a broad feature statement; I did not comprehensively review all generator paths, API compatibility, or serialization contracts. The supplied facts also record a public API check failure, analyzer warning, and missing solution membership for the new test project.. Who should decide: area owner

_1 disputed item(s), not adjudicated: finding:claude:C1_

## Who reviewed

Participating reviewers: claude, codex, nemotron. Adjudicator: gemini. Confidential: no. Rule: proven needs every participating reviewer to say met with verified evidence, and the clause's checks to pass.

## Requirement trace

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-2129-F1 | refused | claude: met (9/9 verified), codex: met (3/3 verified) | build: pass, tests.targeted: pass | missing_review |

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
| claude | claude-opus-5-5 (Anthropic) | review-v1 | 4 | 0 | 3 |
| codex | GPT-6 (OpenAI) | review-v1 | 0 | 0 | 1 |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v2 (39cc20606856)

## What the AI found (verified findings)

- **claude:C1** [major, maintainability] New public API in MessagePack.Annotations is not tracked by any PublicAPI file -> tier ask
  The change adds a public GeneratedMessagePackFormatterAttribute (with a public SurrogateType property) to a shipping assembly, plus public analyzer descriptors MsgPack019-022. MessagePack.Annotations has no PublicAPI.*.txt, so the PublicApiAnalyzers gate never saw it (public_api check = fail). Once shipped, this API is permanent, so a maintainer has to approve its name and shape explicitly.
    - [OK] check `public_api` (facts.json: public_api fail: public API added: new public class MessagePack.GeneratedMessagePackFormatterAttribute (with public Type? SurrogateType) in src/MessagePack.Annotations/Attributes.cs; MessagePack.Annotations has no PublicAPI.*.txt tracking so PublicApiAnalyzers did not flag it. Also 4 new public DiagnosticDescriptors MsgPack019-022 (analyzer assembly) and 4 rows added to AnalyzerReleases.Unshipped.md)
    - [OK] `src/MessagePack.Annotations/Attributes.cs:166` @head: `public class GeneratedMessagePackFormatterAttribute : Attribute` (quote matches src/MessagePack.Annotations/Attributes.cs:166 at head 083afd99)
- **claude:C2** [minor, maintainability] New test-support project is not in MessagePack.sln -> tier notify
  tests/MessagePack.SourceGenerator.ExternalTypes is only reachable through a ProjectReference from ExecutionTests. It is missing from the solution (solution_membership = fail), so IDE and solution-level builds don't show or build it directly.
    - [OK] check `solution_membership` (facts.json: solution_membership fail: new project tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj is not added to MessagePack.sln (only referenced from ExecutionTests.csproj))
- **claude:C3** [minor, maintainability] New StyleCop warning SA1203 in the new test file -> tier notify
  GeneratedMessagePackFormatterTests declares a const field after an instance field, adding 1 build warning vs base (analyzers = fail).
    - [OK] check `analyzers` (facts.json: analyzers fail: 1 new warnings vs base)
    - [OK] `tests/MessagePack.SourceGenerator.Tests/GeneratedMessagePackFormatterTests.cs:22` @head: `private const string Members = """` (quote matches tests/MessagePack.SourceGenerator.Tests/GeneratedMessagePackFormatterTests.cs:22 at head 083afd99)
- **claude:C4** [info, tests] External-type execution tests are excluded from the MapMode execution suite -> tier silent
  MapModeExecutionTests now excludes GeneratedFormatterForExternalTypes*.cs, so the new feature is never tested with map mode (tests.targeted.execution reports no matching tests there).
    - [OK] `tests/MessagePack.SourceGenerator.MapModeExecutionTests/MessagePack.SourceGenerator.MapModeExecutionTests.csproj:14` @head: `GeneratedFormatterForExternalTypes*.cs` (quote matches tests/MessagePack.SourceGenerator.MapModeExecutionTests/MessagePack.SourceGenerator.MapModeExecutionTests.csproj:14 at head 083afd99)
    - [OK] check `tests.targeted.execution` (facts.json: tests.targeted.execution pass: GeneratedFormatterForExternalTypesTests: 7 passed, 0 failed (7 new test results; runtime: generator runs inside csc, no CS9057); tests/MessagePack.SourceGenerator.MapModeExecutionTests: no tests match the filter (the test file is excluded from this project))

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

- REQ-2129-F1 not proven: missing_review
- Reviewer refusal (claude): Correctness of GeneratedFormatterCollector.cs and the MessagePackGenerator.cs pipeline changes beyond what the 7 execution and 6 generator tests exercise (generic formatters, nested/abstract types, interaction with existing [MessagePackObject] collection, incremental-generator caching)
- Reviewer refusal (claude): Whether the API design (SurrogateType, contractless default for external types) is the right answer to the issue, which also asks for Union and other attribute-driven settings
- Reviewer refusal (claude): Security/trust implications of generating formatters that access members of external types (e.g. non-public members)
- Reviewer refusal (codex): Full acceptance and compatibility review of the external formatter feature
- Open major finding claude:C1: New public API in MessagePack.Annotations is not tracked by any PublicAPI file
- tests.MessagePack.Tests not run (runtime library src/MessagePack not modified by the change; suite not run)
- build.net472/netstandard not run (only the net8.0 slice of src/MessagePack was built (Linux container, Debug))
- benchmarks not run (no runtime serialization hot path touched (generator/analyzer only))
- 1 disputed item(s) were not adjudicated (adjudicator gemini has not run)
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
