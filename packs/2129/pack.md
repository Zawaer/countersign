## Countersign: change 2129 is **BLOCK**, owner **Toivo**

**Agent-written change for #2129: Agentic implementation of #2129 Feature Request: Allow generation of Formatter for a type in a referenced assembly**

Changes 10 source files (Attributes.cs, MsgPack00xMessagePackAnalyzer.cs, GeneratedFormatterCollector.cs and 7 more), 6 test files, 6 doc files, 4 build files, 2 generated files (+1034 -9) on ju26-issue-2129 by Stelian Vultur. Judged against 1 requirement clause from #2129 (placeholder requirement set, not Tieto's official one).

**Why block**

1. Risk score 145.2 reaches the block band (>= 130), mostly 2 failed check(s) x 25: analyzers, solution_membership (50) and most sensitive area touched: annotations-api (critical) (35) ([evidence](#risk))
2. Also routes to a human. Claude found a verified major issue: New public API in MessagePack.Annotations is not tracked by any PublicAPI file ([evidence](#f-claude-C1))
3. Also routes to a human. 1 of 1 requirement clauses not proven. No verdict from Nemotron (2 of 3 reviewers answered) ([evidence](#chain-REQ-2129-F1))

<sub>All 15 tier drivers are under Full detail.</sub>

**Requirement trace**

| Status | Clause | Why |
|---|---|---|
| **REFUSED** | [REQ-2129-F1](#chain-REQ-2129-F1) | No verdict from Nemotron (2 of 3 reviewers answered) |

**What the AI found**

- **major** [New public API in MessagePack.Annotations is not tracked by any PublicAPI file](#f-claude-C1) (Claude C1) [`check public_api`](#ev-351e9825c5) [`Attributes.cs:166 @head`](#ev-75f4296476)
- **minor** [New test-support project is not in MessagePack.sln](#f-claude-C2) (Claude C2) [`check solution_membership`](#ev-7db6dc26a1)
- **minor** [New StyleCop warning SA1203 in the new test file](#f-claude-C3) (Claude C3) [`check analyzers`](#ev-4c0f1d94ae) [`GeneratedMessagePackFormatterTests.cs:22 @head`](#ev-e94831e6af)
- +1 more under Evidence.

<a id="refused"></a>**What the AI refused to decide, and who should**

- <a id="refusal-1"></a>Correctness of GeneratedFormatterCollector.cs and the MessagePackGenerator.cs pipeline changes beyond what the 7 execution and 6 generator tests exercise (generic formatters, nested/abstract types, interaction with existing [MessagePackObject] collection, incremental-generator caching). *Why:* Scoped review: I did not read these 300+ lines line by line. Tests show only the happy paths and the 4 diagnostics. *Who:* source-generator area owner (raised by Claude)
- <a id="refusal-2"></a>Whether the API design (SurrogateType, contractless default for external types) is the right answer to the issue, which also asks for Union and other attribute-driven settings. *Why:* Product/API design decision with permanent public surface; the issue proposes three alternatives and the change picks a fourth (surrogate type). *Who:* MessagePack-CSharp maintainers (raised by Claude)
- <a id="refusal-3"></a>Security/trust implications of generating formatters that access members of external types (e.g. non-public members). *Why:* Not examined in this scoped review. *Who:* security champion (raised by Claude)
- <a id="refusal-4"></a>Full acceptance and compatibility review of the external formatter feature. *Why:* This is a scoped review. The placeholder requirement contains only a broad feature statement; I did not comprehensively review all generator paths, API compatibility, or serialization contracts. The supplied facts also record a public API check failure, analyzer warning, and missing solution membership for the new test project. *Who:* area owner (raised by Codex)
- Whether [REQ-2129-F1](#chain-REQ-2129-F1) is met: see the trace. *Who:* Toivo

**Not checked, and why**

- `tests.MessagePack.Tests`: runtime library src/MessagePack not modified by the change; suite not run
- `build.net472/netstandard`: only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks`: no runtime serialization hot path touched (generator/analyzer only)
- Standing pipeline gaps: `other-targets`, `runtime-perf`, `semantic-intent`, `provenance`

**Residual risk you accept by signing**

- Open major finding: New public API in MessagePack.Annotations is not tracked by any PublicAPI file
- Not proven by the AI: REQ-2129-F1. Signing means you judge them yourself.
- 4 questions the AI declined to decide (listed above) are yours.
- Not run: tests.MessagePack.Tests, build.net472/netstandard, benchmarks
- 1 disputed item not adjudicated
- Standing pipeline gaps: other-targets, runtime-perf, semantic-intent, provenance

**Toivo signs** (required; allowed: reject, request-changes)

> I, Toivo, have read what was checked and by whom, what was not checked and why, and the residual risk listed in this pack, and I own this decision.

```
countersign sign 2129 --as Toivo --decision <accept|reject|request-changes> --note "..."
```

<details><summary><b>Where the trust comes from</b> (per requirement clause)</summary>

<a id="chain-REQ-2129-F1"></a>
#### REQ-2129-F1: **REFUSED**

> Feature Request: Allow generation of Formatter for a type in a referenced assembly

- **Claude: met** (9/9 verified). The feature is new and absent on base (the runtime tests don't compile with the source reverted; tests.execution_fail_without_fix pass). Under SDK 9 the 7 execution tests pass: a consuming assembly declares [GeneratedMessagePackFormatter] partial formatters for types in a test assembly that deliberately doesn't reference MessagePack (the issue's Project A scenario), and they round-trip and register in the generated resolver. This covers the clause as written. It does not cover everything the issue discusses (Union and other attribute-driven settings for external types), which I refuse below.
- **Codex: met** (3/3 verified). The supplied execution tests show generated formatters for external types pass, and those tests depend on the new feature according to the fail-without-fix result.
- **Nemotron**: no verdict
- **Checks:** `build` pass, `tests.targeted` pass
- **What would settle it:** A verdict from Nemotron with verified evidence

</details>

<details><summary><b>Reviewer panel</b> (who said what)</summary>
<a id="panel"></a>

> Codex said met to all 1 clauses; Claude raised a verified major finding they did not (claude:C1: New public API in MessagePack.Annotations is not tracked by any PublicAPI file). The finding alone routes the change to a human. Unanimity is required: one verified objection is enough to send it to Toivo.
> Nemotron is on the panel but has no review yet, so no clause can be proven until it answers.

| Clause | Claude | Codex | Nemotron | Result |
|---|---|---|---|---|
| REQ-2129-F1 | met | met | no review | **refused** |

- **Claude** (claude-opus-5-5, Anthropic): citations 16 verified / 0 rejected; findings 4 verified / 0 rejected; 3 refusals. Only Claude raised: [C1](#f-claude-C1) major New public API in MessagePack.Annotations is not tracked by any PublicAPI file, [C2](#f-claude-C2) minor New test-support project is not in MessagePack.sln, [C3](#f-claude-C3) minor New StyleCop warning SA1203 in the new test file, [C4](#f-claude-C4) info External-type execution tests are excluded from the MapMode execution suite
- **Codex** (GPT-6, OpenAI): citations 3 verified / 0 rejected; findings 0 verified / 0 rejected; 1 refusals.
- **Nemotron**: no review on file

1 disputed item(s), not adjudicated: finding:claude:C1

</details>

<details><summary><b>Evidence</b> (findings, cited code, tests and checks)</summary>

<a id="f-claude-C1"></a>
#### Claude C1 [major, maintainability]: New public API in MessagePack.Annotations is not tracked by any PublicAPI file

The change adds a public GeneratedMessagePackFormatterAttribute (with a public SurrogateType property) to a shipping assembly, plus public analyzer descriptors MsgPack019-022. MessagePack.Annotations has no PublicAPI.*.txt, so the PublicApiAnalyzers gate never saw it (public_api check = fail). Once shipped, this API is permanent, so a maintainer has to approve its name and shape explicitly.

Evidence: [`check public_api`](#ev-351e9825c5) [`Attributes.cs:166 @head`](#ev-75f4296476)

Tier effect: ask

Suggested fix: Get maintainer sign-off on the API shape; consider adding PublicAPI tracking to MessagePack.Annotations.

<a id="f-claude-C2"></a>
#### Claude C2 [minor, maintainability]: New test-support project is not in MessagePack.sln

tests/MessagePack.SourceGenerator.ExternalTypes is only reachable through a ProjectReference from ExecutionTests. It is missing from the solution (solution_membership = fail), so IDE and solution-level builds don't show or build it directly.

Evidence: [`check solution_membership`](#ev-7db6dc26a1)

Tier effect: notify

Suggested fix: dotnet sln MessagePack.sln add tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj

<a id="f-claude-C3"></a>
#### Claude C3 [minor, maintainability]: New StyleCop warning SA1203 in the new test file

GeneratedMessagePackFormatterTests declares a const field after an instance field, adding 1 build warning vs base (analyzers = fail).

Evidence: [`check analyzers`](#ev-4c0f1d94ae) [`GeneratedMessagePackFormatterTests.cs:22 @head`](#ev-e94831e6af)

Tier effect: notify

<a id="f-claude-C4"></a>
#### Claude C4 [info, tests]: External-type execution tests are excluded from the MapMode execution suite

MapModeExecutionTests now excludes GeneratedFormatterForExternalTypes*.cs, so the new feature is never tested with map mode (tests.targeted.execution reports no matching tests there).

Evidence: [`MessagePack.SourceGenerator.MapModeExecutionTests.csproj:14 @head`](#ev-e546376f1a) [`check tests.targeted.execution`](#ev-ee60fb1113)

Tier effect: silent

#### Cited evidence

<a id="ev-75f4296476"></a>
**Attributes.cs:166 @head** (verified; cited by claude on REQ-2129-F1, claude:C1): quote matches src/MessagePack.Annotations/Attributes.cs:166 at head 083afd99

```text
// src/MessagePack.Annotations/Attributes.cs @ 083afd99
  163 |     /// </code>
  164 |     /// </example>
  165 |     [AttributeUsage(AttributeTargets.Class, AllowMultiple = false, Inherited = false)]
> 166 |     public class GeneratedMessagePackFormatterAttribute : Attribute
  167 |     {
  168 |         /// <summary>
  169 |         /// Gets or sets a type whose <see cref="KeyAttribute"/> members define the keys and membership of the formatted type.
```

<a id="ev-922578020e"></a>
**MessagePack.SourceGenerator.ExternalTypes.csproj:4 @head** (verified; cited by claude on REQ-2129-F1): quote matches tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj:4 at head 083afd99

```text
// tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj @ 083afd99
  1 | <Project Sdk="Microsoft.NET.Sdk">
  2 | 
  3 |   <!--
> 4 |     This assembly deliberately does NOT reference MessagePack.
  5 |     It models a dependency-free library (Project A in https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2129)
  6 |     whose types are serialized by generated formatters declared in a consuming assembly.
  7 |   -->
```

<a id="ev-cbd24f9115"></a>
**GeneratedFormatterForExternalTypes.cs:9 @head** (verified; cited by claude on REQ-2129-F1): quote matches tests/MessagePack.SourceGenerator.ExecutionTests/GeneratedFormatterForExternalTypes.cs:9 at head 083afd99

```text
// tests/MessagePack.SourceGenerator.ExecutionTests/GeneratedFormatterForExternalTypes.cs @ 083afd99
   6 | 
   7 | // Formatter bodies for types from ExternalTypes that carry no MessagePack attributes.
   8 | // The source generator writes the members of each partial class (https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2129).
>  9 | [GeneratedMessagePackFormatter]
  10 | public partial class ExternalPersonFormatter : IMessagePackFormatter<ExternalPerson>
  11 | {
  12 | }
```

<a id="ev-0b4fbdae24"></a>
**test ContractlessClassRoundTrips passed** (verified; cited by claude on REQ-2129-F1): facts.json tests.targeted.execution: passed (new test)

- change head (`tests.targeted.execution`, tests/MessagePack.SourceGenerator.ExecutionTests): **passed**

<a id="ev-3d8a67cf2e"></a>
**test GeneratedFormattersAreRegisteredInGeneratedResolver passed** (verified; cited by claude on REQ-2129-F1): facts.json tests.targeted.execution: passed (new test)

- change head (`tests.targeted.execution`, tests/MessagePack.SourceGenerator.ExecutionTests): **passed**

<a id="ev-0ecf09dcfa"></a>
**test SurrogateControlsKeysAndMembership passed** (verified; cited by claude on REQ-2129-F1): facts.json tests.targeted.execution: passed (new test)

- change head (`tests.targeted.execution`, tests/MessagePack.SourceGenerator.ExecutionTests): **passed**

<a id="ev-05862d94ce"></a>
**check tests.execution_fail_without_fix** (verified; cited by claude on REQ-2129-F1): facts.json: tests.execution_fail_without_fix pass: new runtime tests do not compile with the source reverted (tests/MessagePack.SourceGenerator.ExecutionTests): 7 tests cannot exist without the fix; errors are the missing feature itself (see compile_failure) -> tests depend on the change

- `tests.execution_fail_without_fix` **pass**: new runtime tests do not compile with the source reverted (tests/MessagePack.SourceGenerator.ExecutionTests): 7 tests cannot exist without the fix; errors are the missing feature itself (see compile_failure) -> tests depend on the change (dotnet test (source reverted, tests kept) - ExecutionTests 9.0.321)
- log: `evidence/2129/logs/execution_fail_without_fix.ExecutionTests.build.log`
- log: `evidence/2129/logs/execution_fail_without_fix.MapModeExecutionTests.build.log`
- log: `evidence/2129/logs/execution_fail_without_fix.MapModeExecutionTests.targeted.log`
- log: `evidence/2129/logs/execution_fail_without_fix.MapModeExecutionTests.full.log`

<a id="ev-fbc74f77d6"></a>
**check tests.execution_full_suite** (verified; cited by claude on REQ-2129-F1, codex on REQ-2129-F1): facts.json: tests.execution_full_suite pass: tests/MessagePack.SourceGenerator.ExecutionTests: 21/21 passed (base 14/14), 0 failures not on base; tests/MessagePack.SourceGenerator.MapModeExecutionTests: 20/20 passed (base 20/20), 0 failures not on base

- `tests.execution_full_suite` **pass**: tests/MessagePack.SourceGenerator.ExecutionTests: 21/21 passed (base 14/14), 0 failures not on base; tests/MessagePack.SourceGenerator.MapModeExecutionTests: 20/20 passed (base 20/20), 0 failures not on base (dotnet test (whole ExecutionTests, MapModeExecutionTests) vs base 9.0.321)
- log: `evidence/2129/logs/execution.ExecutionTests.full.log`
- log: `evidence/2129/logs/execution.MapModeExecutionTests.full.log`

<a id="ev-d78b746a74"></a>
**check tests.fail_without_fix** (verified; cited by claude on REQ-2129-F1): facts.json: tests.fail_without_fix pass: new tests fail on base source: 6/6 failed -> tests do cover the change

- `tests.fail_without_fix` **pass**: new tests fail on base source: 6/6 failed -> tests do cover the change (dotnet test (source reverted, tests kept) 8.0.402)
- log: `evidence/2129/logs/tests_fail_without_fix.1.log`

<a id="ev-648e85e32d"></a>
**test MessagePackObjectCanContainExternalTypes passed** (verified; cited by codex on REQ-2129-F1): facts.json tests.targeted.execution: passed (new test)

- change head (`tests.targeted.execution`, tests/MessagePack.SourceGenerator.ExecutionTests): **passed**

<a id="ev-fc2d818fd3"></a>
**test GeneratedFormattersAreRegisteredInGeneratedResolver passed** (verified; cited by codex on REQ-2129-F1): facts.json tests.targeted.execution: passed (new test)

- change head (`tests.targeted.execution`, tests/MessagePack.SourceGenerator.ExecutionTests): **passed**

<a id="ev-351e9825c5"></a>
**check public_api** (verified; cited by claude:C1): facts.json: public_api fail: public API added: new public class MessagePack.GeneratedMessagePackFormatterAttribute (with public Type? SurrogateType) in src/MessagePack.Annotations/Attributes.cs; MessagePack.Annotations has no PublicAPI.*.txt tracking so PublicApiAnalyzers did not flag it. Also 4 new public DiagnosticDescriptors MsgPack019-022 (analyzer assembly) and 4 rows added to AnalyzerReleases.Unshipped.md

- `public_api` **fail**: public API added: new public class MessagePack.GeneratedMessagePackFormatterAttribute (with public Type? SurrogateType) in src/MessagePack.Annotations/Attributes.cs; MessagePack.Annotations has no PublicAPI.*.txt tracking so PublicApiAnalyzers did not flag it. Also 4 new public DiagnosticDescriptors MsgPack019-022 (analyzer assembly) and 4 rows added to AnalyzerReleases.Unshipped.md (git diff of PublicAPI.*.txt + scan of added public/protected declarations in src/ )

<a id="ev-7db6dc26a1"></a>
**check solution_membership** (verified; cited by claude:C2): facts.json: solution_membership fail: new project tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj is not added to MessagePack.sln (only referenced from ExecutionTests.csproj)

- `solution_membership` **fail**: new project tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj is not added to MessagePack.sln (only referenced from ExecutionTests.csproj) (grep MessagePack.sln )

<a id="ev-4c0f1d94ae"></a>
**check analyzers** (verified; cited by claude:C3): facts.json: analyzers fail: 1 new warnings vs base

- `analyzers` **fail**: 1 new warnings vs base (dotnet build warnings (Roslyn analyzers, StyleCop, PublicApiAnalyzers) vs base )

<a id="ev-e94831e6af"></a>
**GeneratedMessagePackFormatterTests.cs:22 @head** (verified; cited by claude:C3): quote matches tests/MessagePack.SourceGenerator.Tests/GeneratedMessagePackFormatterTests.cs:22 at head 083afd99

```text
// tests/MessagePack.SourceGenerator.Tests/GeneratedMessagePackFormatterTests.cs @ 083afd99
  19 | 
  20 |     // Formatter members are written by hand in the diagnostic tests, so the compiler accepts the source
  21 |     // even when the generator declines to write them.
> 22 |     private const string Members = """
  23 |             public void Serialize(ref MessagePackWriter writer, MyType value, MessagePackSerializerOptions options) => throw new System.NotImplementedException();
  24 | 
  25 |             public MyType Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options) => throw new System.NotImplementedException();
```

<a id="ev-e546376f1a"></a>
**MessagePack.SourceGenerator.MapModeExecutionTests.csproj:14 @head** (verified; cited by claude:C4): quote matches tests/MessagePack.SourceGenerator.MapModeExecutionTests/MessagePack.SourceGenerator.MapModeExecutionTests.csproj:14 at head 083afd99

```text
// tests/MessagePack.SourceGenerator.MapModeExecutionTests/MessagePack.SourceGenerator.MapModeExecutionTests.csproj @ 083afd99
  11 | 
  12 |   <ItemGroup>
  13 |     <!-- GeneratedFormatterForExternalTypes*.cs need the ExternalTypes assembly, which this project does not reference. -->
> 14 |     <Compile Include="..\MessagePack.SourceGenerator.ExecutionTests\**\*.cs" Exclude="..\MessagePack.SourceGenerator.ExecutionTests\**\GeneratedMessagePackResolver.cs;..\MessagePack.SourceGenerator.ExecutionTests\**\GeneratedFormatterForExternalTypes*.cs" />
  15 |   </ItemGroup>
  16 | 
  17 |   <ItemGroup>
```

<a id="ev-ee60fb1113"></a>
**check tests.targeted.execution** (verified; cited by claude:C4): facts.json: tests.targeted.execution pass: GeneratedFormatterForExternalTypesTests: 7 passed, 0 failed (7 new test results; runtime: generator runs inside csc, no CS9057); tests/MessagePack.SourceGenerator.MapModeExecutionTests: no tests match the filter (the test file is excluded from this project)

- `tests.targeted.execution` **pass**: GeneratedFormatterForExternalTypesTests: 7 passed, 0 failed (7 new test results; runtime: generator runs inside csc, no CS9057); tests/MessagePack.SourceGenerator.MapModeExecutionTests: no tests match the filter (the test file is excluded from this project) (dotnet build + dotnet test (ExecutionTests, MapModeExecutionTests) 9.0.321)
- log: `evidence/2129/logs/execution.ExecutionTests.build.log`
- log: `evidence/2129/logs/execution.ExecutionTests.targeted.log`
- log: `evidence/2129/logs/execution.ExecutionTests.full.log`
- log: `evidence/2129/logs/execution.MapModeExecutionTests.build.log`
- log: `evidence/2129/logs/execution.MapModeExecutionTests.targeted.log`
- log: `evidence/2129/logs/execution.MapModeExecutionTests.full.log`

</details>

<details><summary><b>Full detail</b>: all tier drivers, risk score, every check, areas, not checked, residual risk</summary>

Branch `ju26-issue-2129` (32258fdb..083afd99), 28 files, +1034 -9. Author Stelian Vultur (agent-written: True). Commit: Agentic implementation of #2129 Feature Request: Allow generation of Formatter for a type in a referenced assembly

Mandate `messagepack-csharp` v2 sha256 `39cc2060685638e1`, signature: valid, Toivo

<a id="all-drivers"></a>
#### All tier drivers (tier = strictest)

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

#### Who reviewed

Participating reviewers: claude, codex, nemotron. Adjudicator: gemini. Confidential: no. Rule: proven needs every participating reviewer to say met with verified evidence, and the clause's checks to pass.

| Reviewer | Model | Prompt | Verified findings | Rejected | Refusals |
|---|---|---|---|---|---|
| claude | claude-opus-5-5 (Anthropic) | review-v1 | 4 | 0 | 3 |
| codex | GPT-6 (OpenAI) | review-v1 | 0 | 0 | 1 |

#### Every check

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

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v2 (39cc20606856)

#### Requirement trace (engine codes)

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-2129-F1 | refused | claude: met (9/9), codex: met (3/3) | build: pass, tests.targeted: pass | missing_review |

#### What the AI refused to decide (every reviewer refusal)

- **claude** refused: Correctness of GeneratedFormatterCollector.cs and the MessagePackGenerator.cs pipeline changes beyond what the 7 execution and 6 generator tests exercise (generic formatters, nested/abstract types, interaction with existing [MessagePackObject] collection, incremental-generator caching). Why: Scoped review: I did not read these 300+ lines line by line. Tests show only the happy paths and the 4 diagnostics. Who should decide: source-generator area owner
- **claude** refused: Whether the API design (SurrogateType, contractless default for external types) is the right answer to the issue, which also asks for Union and other attribute-driven settings. Why: Product/API design decision with permanent public surface; the issue proposes three alternatives and the change picks a fourth (surrogate type). Who should decide: MessagePack-CSharp maintainers
- **claude** refused: Security/trust implications of generating formatters that access members of external types (e.g. non-public members). Why: Not examined in this scoped review. Who should decide: security champion
- **codex** refused: Full acceptance and compatibility review of the external formatter feature. Why: This is a scoped review. The placeholder requirement contains only a broad feature statement; I did not comprehensively review all generator paths, API compatibility, or serialization contracts. The supplied facts also record a public API check failure, analyzer warning, and missing solution membership for the new test project. Who should decide: area owner

<a id="areas"></a>
#### Areas

| Area | Owner | Sensitivity | AI cap | Files |
|---|---|---|---|---:|
| annotations-api | Toivo | critical | ask (mandate clearance right) | 1 |
| generator-analyzer-core | Toivo | high | notify (mandate clearance right) | 12 |
| build | Rene | medium | notify (mandate clearance right) | 3 |
| docs | Rene | low | silent (mandate clearance right) | 6 |
| tests | Toivo | low | silent (mandate clearance right) | 6 |

<a id="not-checked"></a>
#### What was not checked, and why

- `tests.MessagePack.Tests` (facts.json not_run): runtime library src/MessagePack not modified by the change; suite not run
- `build.net472/netstandard` (facts.json not_run): only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks` (facts.json not_run): no runtime serialization hot path touched (generator/analyzer only)
- `other-targets` (mandate known gap): Tests run on net8.0 only; .NET Framework, Unity and NativeAOT targets are not exercised
- `runtime-perf` (mandate known gap): No benchmarks unless a perf-sensitive path is touched; allocation and throughput regressions can slip through
- `semantic-intent` (mandate known gap): Correctness beyond what tests and cited evidence show is not established by the AI
- `provenance` (mandate known gap): Licensing and provenance of agent-written code are not checked

#### Residual risk (every item)

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

<a id="risk"></a>
#### Risk score: 145.2 -> block

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

Inputs: facts `evidence/2129/facts.json`, requirements `requirements/2129.yaml`, reviews `reviews/2129/claude.json`, `reviews/2129/codex.json`

</details>
