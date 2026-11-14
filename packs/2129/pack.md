## Countersign: change 2129 is **BLOCK**, owner **Toivo**

**Agent-written change for #2129: Agentic implementation of #2129 Feature Request: Allow generation of Formatter for a type in a referenced assembly**

Changes 10 source files (Attributes.cs, MsgPack00xMessagePackAnalyzer.cs, GeneratedFormatterCollector.cs and 7 more), 6 test files, 6 doc files, 4 build files, 2 generated files (+1034 -9) on ju26-issue-2129 by Stelian Vultur. Judged against 1 requirement clause from #2129 (placeholder requirement set, not Tieto's official one).

**Why block**

1. Risk score 175.2 reaches the block band (>= 130), mostly 3 failed check(s) x 25: analyzers, solution_membership, tests.mutation (75) and most sensitive area touched: annotations-api (critical) (35) ([evidence](#risk))
2. Also routes to a human. Claude found a verified major issue: New public API in MessagePack.Annotations is not tracked by any PublicAPI file (and 1 more finding) ([evidence](#f-claude-C1))
3. Also routes to a human. The AI declined to decide 2 questions, e.g. Security/trust implications of generating formatters that access members of external types (e.g. non-public members) ([evidence](#refused))

<sub>All 19 tier drivers are under Full detail.</sub>

**Requirement trace**

| Status | Clause | Why |
|---|---|---|
| **PROVEN** | [REQ-2129-F1](#chain-REQ-2129-F1) | All 3 reviewers say met (17 verified citations); build, tests.targeted pass |

**What the AI found**

- **major** [New public API in MessagePack.Annotations is not tracked by any PublicAPI file](#f-claude-C1) (Claude C1, also Nemotron) [`check public_api`](#ev-351e9825c5) [`Attributes.cs:166 @head`](#ev-75f4296476)
- **major** [Execution tests require SDK 9 / Roslyn 4.12 but the repo pins SDK 8.0.402](#f-nemotron-N2) (Nemotron N2, also Claude) [`check tests.targeted.execution pass`](#ev-b644d3bd4a)
- **minor** [New StyleCop warning SA1203 in the new test file](#f-claude-C3) (Claude C3, also Nemotron) [`check analyzers`](#ev-4c0f1d94ae) [`GeneratedMessagePackFormatterTests.cs:22 @head`](#ev-e94831e6af)
- +4 more under Evidence.

<a id="refused"></a>**What the AI refused to decide, and who should**

- <a id="refusal-3"></a>Security/trust implications of generating formatters that access members of external types (e.g. non-public members). *Why:* Not examined in this scoped review. *Who:* security champion (raised by Claude)
- <a id="refusal-6"></a>Security review of serializing externally defined types via generated formatters. *Why:* No runtime deserialization code was changed by this branch, but the library deserializes untrusted input and this feature lets formats be generated for types the reviewer cannot inspect; a formal security judgement is beyond the provided evidence. *Who:* area owner / security reviewer (raised by Nemotron)

<details id="refused-peripheral"><summary>4 peripheral refusals (out of scope for this change)</summary><a id="refusal-1"></a>Correctness of GeneratedFormatterCollector.cs and the MessagePackGenerator.cs pipeline changes beyond what the 7 execution and 6 generator tests exercise (generic formatters, nested/abstract types, interaction with existing [MessagePackObject] collection, incremental-generator caching) (Claude) · <a id="refusal-2"></a>Whether the API design (SurrogateType, contractless default for external types) is the right answer to the issue, which also asks for Union and other attribute-driven settings (Claude) · <a id="refusal-4"></a>Full acceptance and compatibility review of the external formatter feature (Codex) · <a id="refusal-5"></a>Generated output of FormatterTemplate.cs and StringKeyFormatterTemplate.cs (Nemotron)</details>

**Not checked, and why**

- `tests.MessagePack.Tests`: runtime library src/MessagePack not modified by the change; suite not run
- `build.net472/netstandard`: only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks`: no runtime serialization hot path touched (generator/analyzer only)
- Standing pipeline gaps: `other-targets`, `runtime-perf`, `semantic-intent`, `provenance`

**Residual risk you accept by signing**

- Open major finding: New public API in MessagePack.Annotations is not tracked by any PublicAPI file
- Open major finding: Execution tests require SDK 9 / Roslyn 4.12 but the repo pins SDK 8.0.402
- 2 questions the AI declined to decide (listed above) are yours.

<details><summary>3 more risks that do not set the tier</summary>4 peripheral refusals (out of scope for this change) are yours too. · Not run: tests.MessagePack.Tests, build.net472/netstandard, benchmarks · Standing pipeline gaps: other-targets, runtime-perf, semantic-intent, provenance</details>

**Toivo signs** (required; allowed: reject, request-changes)

> I, Toivo, have read what was checked and by whom, what was not checked and why, and the residual risk listed in this pack, and I own this decision.

Rate each verified finding with its `--finding` flag: `accepted` (real), `rejected` (a false positive) or `unsure`, optionally `:reason`. A finding without a flag is recorded as `unrated`.

- `claude:C1` (major): New public API in MessagePack.Annotations is not tracked by any PublicAPI file
- `claude:C3` (minor): New StyleCop warning SA1203 in the new test file
- `claude:C4` (info): External-type execution tests are excluded from the MapMode execution suite
- `nemotron:N1` (minor): New ExternalTypes test project is not added to the solution file
- `nemotron:N2` (major): Execution tests require SDK 9 / Roslyn 4.12 but the repo pins SDK 8.0.402
- `nemotron:N3` (minor): New public API added without PublicAPI tracking in MessagePack.Annotations
- `nemotron:N4` (minor): New StyleCop SA1203 warning in GeneratedMessagePackFormatterTests.cs

```
countersign sign 2129 --as Toivo --decision <reject|request-changes> --note "..." \
  --finding claude:C1=<accepted|rejected|unsure> \
  --finding claude:C3=<accepted|rejected|unsure> \
  --finding claude:C4=<accepted|rejected|unsure> \
  --finding nemotron:N1=<accepted|rejected|unsure> \
  --finding nemotron:N2=<accepted|rejected|unsure> \
  --finding nemotron:N3=<accepted|rejected|unsure> \
  --finding nemotron:N4=<accepted|rejected|unsure>
```

<a id="supply-chain"></a>**Supply chain (from the build):** deps.delta pass: no package added or moved, 1 new project, 0 new advisories (6 already on base); build.egress pass

<details><summary>Supply-chain detail</summary>

`deps.delta` **pass**: 238 packages on head (238 on base) across 31 projects; 0 added, 0 version changes, 0 removed; new project(s): tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj; 4 new direct reference(s) to packages already in the graph; 0 new vulnerability hits (6 already on base)

- New project: `tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj`
- New project reference: `tests/MessagePack.SourceGenerator.ExecutionTests/MessagePack.SourceGenerator.ExecutionTests.csproj` -> `tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj`
- Already on base (6): Microsoft.NETCore.Jit 1.0.2 high GHSA-xcvr-qv8h-m7xw, NuGet.Packaging 6.8.0 critical GHSA-68w7-72jg-6qpp, NuGet.Packaging 6.8.0 low GHSA-g4vj-cjjj-v7hg, NuGet.Protocol 6.8.0 low GHSA-g4vj-cjjj-v7hg, System.Formats.Asn1 6.0.0 high GHSA-447r-wph3-92pm, System.Text.Encodings.Web 4.5.0 critical GHSA-ghhp-997w-qr28
- SBOMs (CycloneDX): `evidence/base/sbom.cdx.json`, `evidence/2129/sbom.cdx.json`
- `build.egress` **pass**: default deny, presets ['github'], 13 TLS host patterns; run https://github.com/Zawaer/countersign/actions/runs/43559092226; policy sha256 `31fafb855e98`

</details>

<details><summary><b>Where the trust comes from</b> (per requirement clause)</summary>

<a id="chain-REQ-2129-F1"></a>
#### REQ-2129-F1: **PROVEN**

> Feature Request: Allow generation of Formatter for a type in a referenced assembly

- **Checks passed:** `build` pass, `tests.targeted` pass
- **Fails without the fix:** [`FormatterMustBePartial`](#ev-cabf78af9d)
- **Claude** says met (6/9 citations verified): [`Attributes.cs:166 @head`](#ev-75f4296476) [`MessagePack.SourceGenerator.ExternalTypes.csproj:4 @head`](#ev-922578020e) [`GeneratedFormatterForExternalTypes.cs:9 @head`](#ev-cbd24f9115) [`test ContractlessClassRoundTrips passed`](#ev-0b4fbdae24) [`test GeneratedFormattersAreRegisteredInGeneratedResolver passed`](#ev-3d8a67cf2e) [`test SurrogateControlsKeysAndMembership passed`](#ev-0ecf09dcfa) [`check tests.execution_fail_without_fix`](#ev-05862d94ce) [`check tests.execution_full_suite`](#ev-fbc74f77d6) [`check tests.fail_without_fix`](#ev-d78b746a74)
- **Codex** says met (2/3 citations verified): [`check tests.execution_full_suite`](#ev-fbc74f77d6) [`test MessagePackObjectCanContainExternalTypes passed`](#ev-648e85e32d) [`test GeneratedFormattersAreRegisteredInGeneratedResolver passed`](#ev-fc2d818fd3)
- **Nemotron** says met (9/10 citations verified): [`Attributes.cs:166 @head`](#ev-75f4296476) [`MessagePackGenerator.cs:30 @head`](#ev-3c55828f31) [`test ContractlessClassRoundTrips passed`](#ev-494a53650c) [`test SurrogateControlsKeysAndMembership passed`](#ev-7019ece62f) [`test FormatterMustBePartial failed`](#ev-cabf78af9d) [`check tests.fail_without_fix pass`](#ev-62faeb2508) [`check tests.execution_fail_without_fix pass`](#ev-dfdcb008d6) [`check tests.full_suite pass`](#ev-d448f979e6) [`check tests.execution_full_suite pass`](#ev-98002ca52b)

</details>

<details><summary><b>Reviewer panel</b> (who said what)</summary>
<a id="panel"></a>

| Clause | Claude | Codex | Nemotron | Result |
|---|---|---|---|---|
| REQ-2129-F1 | met | met | met | **proven** |

- **Claude** (claude-opus-5-5, Anthropic): citations 16 verified / 0 rejected; findings 3 verified / 1 rejected; 3 refusals. Only Claude raised: [C2](#f-claude-C2) minor New test-support project is not in MessagePack.sln (rejected)
- **Codex** (GPT-6, OpenAI): citations 3 verified / 0 rejected; findings 0 verified / 0 rejected; 1 refusals.
- **Nemotron** (nvidia/nemotron-3.5-super-vl-120b-a12b, NVIDIA): citations 13 verified / 1 rejected; findings 4 verified / 0 rejected; 2 refusals. Only Nemotron raised: [N1](#f-nemotron-N1) minor New ExternalTypes test project is not added to the solution file

</details>

<details><summary><b>Evidence</b> (findings, cited code, tests and checks)</summary>

<a id="f-claude-C1"></a>
#### Claude C1 [major, maintainability]: New public API in MessagePack.Annotations is not tracked by any PublicAPI file

The change adds a public GeneratedMessagePackFormatterAttribute (with a public SurrogateType property) to a shipping assembly, plus public analyzer descriptors MsgPack019-022. MessagePack.Annotations has no PublicAPI.*.txt, so the PublicApiAnalyzers gate never saw it (public_api check = fail). Once shipped, this API is permanent, so a maintainer has to approve its name and shape explicitly.

Evidence: [`check public_api`](#ev-351e9825c5) [`Attributes.cs:166 @head`](#ev-75f4296476)

Tier effect: ask

Suggested fix: Get maintainer sign-off on the API shape; consider adding PublicAPI tracking to MessagePack.Annotations.

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

<a id="f-nemotron-N1"></a>
#### Nemotron N1 [minor, build]: New ExternalTypes test project is not added to the solution file

The new project tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj is not added to MessagePack.sln; it is only referenced from ExecutionTests.csproj, so solution-level builds may not include or build it consistently.

Evidence: [`check solution_membership fail`](#ev-4e1de141f2)

Tier effect: notify

Suggested fix: Add the ExternalTypes project to MessagePack.sln and verify it builds in solution context.

<a id="f-nemotron-N2"></a>
#### Nemotron N2 [major, build]: Execution tests require SDK 9 / Roslyn 4.12 but the repo pins SDK 8.0.402

Building tests/MessagePack.SourceGenerator.ExecutionTests with SDK 8.0.402 fails with CS9057 because the source generator references Microsoft.CodeAnalysis 4.12 while SDK 8 ships Roslyn 4.11; the SDK 9 override existed only in the scratch worktree, so builds on the pinned SDK cannot compile these new tests (the targeted run passes only under SDK 9).

Evidence: [`check tests.targeted.execution pass`](#ev-b644d3bd4a)

Tier effect: ask

Suggested fix: Align global.json/CI to SDK 9 for these projects, or align the generator's Roslyn dependency with the pinned SDK; area owner to decide.

<a id="f-nemotron-N3"></a>
#### Nemotron N3 [minor, maintainability]: New public API added without PublicAPI tracking in MessagePack.Annotations

MessagePack.Annotations gains public class GeneratedMessagePackFormatterAttribute with public Type? SurrogateType, and the analyzer gains four public DiagnosticDescriptors (MsgPack019–022), but MessagePack.Annotations has no PublicAPI.*.txt so PublicApiAnalyzers did not flag the addition; future breaking changes to this surface will not be caught by that analyzer.

Evidence: [`check public_api fail`](#ev-e0387b49a2)

Tier effect: notify

Suggested fix: Add PublicAPI tracking for MessagePack.Annotations or review the new surface as intentional public API.

<a id="f-nemotron-N4"></a>
#### Nemotron N4 [minor, maintainability]: New StyleCop SA1203 warning in GeneratedMessagePackFormatterTests.cs

A new warning SA1203 (constant fields should appear before non-constant fields) appears versus base, because the const string Members is declared after the non-constant testOutputHelper field.

Evidence: [`check analyzers fail`](#ev-b8090ba411)

Tier effect: notify

Suggested fix: Reorder fields so constants precede non-constant fields, or justify a suppression.

<a id="f-claude-C2"></a>
#### REJECTED: Claude C2 [minor, maintainability]: New test-support project is not in MessagePack.sln

tests/MessagePack.SourceGenerator.ExternalTypes is only reachable through a ProjectReference from ExecutionTests. It is missing from the solution (solution_membership = fail), so IDE and solution-level builds don't show or build it directly.

Evidence: [`check solution_membership`](#ev-7db6dc26a1)

Rejected: no cited evidence about the change could be verified: facts.json: solution_membership fail: new project tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj is not added to MessagePack.sln (only referenced from ExecutionTests.csproj)

Suggested fix: dotnet sln MessagePack.sln add tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj

#### Cited evidence

<a id="ev-75f4296476"></a>
**Attributes.cs:166 @head** (verified; cited by claude on REQ-2129-F1, nemotron on REQ-2129-F1, claude:C1): quote matches src/MessagePack.Annotations/Attributes.cs:166 at head 083afd99

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

<a id="ev-3c55828f31"></a>
**MessagePackGenerator.cs:30 @head** (verified; cited by nemotron on REQ-2129-F1): quote matches src/MessagePack.SourceGenerator/MessagePackGenerator.cs:30 at head 083afd99

```text
// src/MessagePack.SourceGenerator/MessagePackGenerator.cs @ 083afd99
  27 |             transform: static (context, _) => (ITypeSymbol)context.TargetSymbol);
  28 | 
  29 |         var generatedFormatters = context.SyntaxProvider.ForAttributeWithMetadataName(
> 30 |             $"{AttributeNamespace}.{GeneratedMessagePackFormatterAttributeName}",
  31 |             predicate: static (node, _) => node is ClassDeclarationSyntax,
  32 |             transform: static (context, _) => new GeneratedFormatterRequest(
  33 |                 (INamedTypeSymbol)context.TargetSymbol,
```

<a id="ev-3e30bdc09c"></a>
**GeneratedFormatterCollector.cs:72 @head** (NOT verified; cited by nemotron on REQ-2129-F1): quote not on src/MessagePack.SourceGenerator/CodeAnalysis/GeneratedFormatterCollector.cs:72 ±3 at head; not found anywhere in the file

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/GeneratedFormatterCollector.cs @ 083afd99
  69 |                 MsgPack00xMessagePackAnalyzer.GeneratedFormatterDataTypeNotSupported,
  70 |                 location,
  71 |                 formatterName,
  72 |                 dataTypeSymbol.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat)));
  73 |             return null;
  74 |         }
  75 | 
```

<a id="ev-494a53650c"></a>
**test ContractlessClassRoundTrips passed** (verified; cited by nemotron on REQ-2129-F1): facts.json tests.targeted.execution: passed (new test)

- change head (`tests.targeted.execution`, tests/MessagePack.SourceGenerator.ExecutionTests): **passed**

<a id="ev-7019ece62f"></a>
**test SurrogateControlsKeysAndMembership passed** (verified; cited by nemotron on REQ-2129-F1): facts.json tests.targeted.execution: passed (new test)

- change head (`tests.targeted.execution`, tests/MessagePack.SourceGenerator.ExecutionTests): **passed**

<a id="ev-cabf78af9d"></a>
**test FormatterMustBePartial failed** (verified; cited by nemotron on REQ-2129-F1): facts.json tests.fail_without_fix: failed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-62faeb2508"></a>
**check tests.fail_without_fix pass** (verified; cited by nemotron on REQ-2129-F1): facts.json: tests.fail_without_fix pass: new tests fail on base source: 6/6 failed -> tests do cover the change

- `tests.fail_without_fix` **pass**: new tests fail on base source: 6/6 failed -> tests do cover the change (dotnet test (source reverted, tests kept) 8.0.402)
- log: `evidence/2129/logs/tests_fail_without_fix.1.log`

<a id="ev-dfdcb008d6"></a>
**check tests.execution_fail_without_fix pass** (verified; cited by nemotron on REQ-2129-F1): facts.json: tests.execution_fail_without_fix pass: new runtime tests do not compile with the source reverted (tests/MessagePack.SourceGenerator.ExecutionTests): 7 tests cannot exist without the fix; errors are the missing feature itself (see compile_failure) -> tests depend on the change

- `tests.execution_fail_without_fix` **pass**: new runtime tests do not compile with the source reverted (tests/MessagePack.SourceGenerator.ExecutionTests): 7 tests cannot exist without the fix; errors are the missing feature itself (see compile_failure) -> tests depend on the change (dotnet test (source reverted, tests kept) - ExecutionTests 9.0.321)
- log: `evidence/2129/logs/execution_fail_without_fix.ExecutionTests.build.log`
- log: `evidence/2129/logs/execution_fail_without_fix.MapModeExecutionTests.build.log`
- log: `evidence/2129/logs/execution_fail_without_fix.MapModeExecutionTests.targeted.log`
- log: `evidence/2129/logs/execution_fail_without_fix.MapModeExecutionTests.full.log`

<a id="ev-d448f979e6"></a>
**check tests.full_suite pass** (verified; cited by nemotron on REQ-2129-F1): facts.json: tests.full_suite pass: tests/MessagePack.SourceGenerator.Tests: 173 tests, 173 passed, 0 failed (0 not failing on base, 0 also failing on base)

- `tests.full_suite` **pass**: tests/MessagePack.SourceGenerator.Tests: 173 tests, 173 passed, 0 failed (0 not failing on base, 0 also failing on base) (dotnet test 8.0.402)
- log: `evidence/2129/logs/tests_full_suite.log`

<a id="ev-98002ca52b"></a>
**check tests.execution_full_suite pass** (verified; cited by nemotron on REQ-2129-F1): facts.json: tests.execution_full_suite pass: tests/MessagePack.SourceGenerator.ExecutionTests: 21/21 passed (base 14/14), 0 failures not on base; tests/MessagePack.SourceGenerator.MapModeExecutionTests: 20/20 passed (base 20/20), 0 failures not on base

- `tests.execution_full_suite` **pass**: tests/MessagePack.SourceGenerator.ExecutionTests: 21/21 passed (base 14/14), 0 failures not on base; tests/MessagePack.SourceGenerator.MapModeExecutionTests: 20/20 passed (base 20/20), 0 failures not on base (dotnet test (whole ExecutionTests, MapModeExecutionTests) vs base 9.0.321)
- log: `evidence/2129/logs/execution.ExecutionTests.full.log`
- log: `evidence/2129/logs/execution.MapModeExecutionTests.full.log`

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

<a id="ev-4e1de141f2"></a>
**check solution_membership fail** (verified; cited by nemotron:N1): facts.json: solution_membership fail: new project tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj is not added to MessagePack.sln (only referenced from ExecutionTests.csproj)

- `solution_membership` **fail**: new project tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj is not added to MessagePack.sln (only referenced from ExecutionTests.csproj) (grep MessagePack.sln )

<a id="ev-b644d3bd4a"></a>
**check tests.targeted.execution pass** (verified; cited by nemotron:N2): facts.json: tests.targeted.execution pass: GeneratedFormatterForExternalTypesTests: 7 passed, 0 failed (7 new test results; runtime: generator runs inside csc, no CS9057); tests/MessagePack.SourceGenerator.MapModeExecutionTests: no tests match the filter (the test file is excluded from this project)

- `tests.targeted.execution` **pass**: GeneratedFormatterForExternalTypesTests: 7 passed, 0 failed (7 new test results; runtime: generator runs inside csc, no CS9057); tests/MessagePack.SourceGenerator.MapModeExecutionTests: no tests match the filter (the test file is excluded from this project) (dotnet build + dotnet test (ExecutionTests, MapModeExecutionTests) 9.0.321)
- log: `evidence/2129/logs/execution.ExecutionTests.build.log`
- log: `evidence/2129/logs/execution.ExecutionTests.targeted.log`
- log: `evidence/2129/logs/execution.ExecutionTests.full.log`
- log: `evidence/2129/logs/execution.MapModeExecutionTests.build.log`
- log: `evidence/2129/logs/execution.MapModeExecutionTests.targeted.log`
- log: `evidence/2129/logs/execution.MapModeExecutionTests.full.log`

<a id="ev-e0387b49a2"></a>
**check public_api fail** (verified; cited by nemotron:N3): facts.json: public_api fail: public API added: new public class MessagePack.GeneratedMessagePackFormatterAttribute (with public Type? SurrogateType) in src/MessagePack.Annotations/Attributes.cs; MessagePack.Annotations has no PublicAPI.*.txt tracking so PublicApiAnalyzers did not flag it. Also 4 new public DiagnosticDescriptors MsgPack019-022 (analyzer assembly) and 4 rows added to AnalyzerReleases.Unshipped.md

- `public_api` **fail**: public API added: new public class MessagePack.GeneratedMessagePackFormatterAttribute (with public Type? SurrogateType) in src/MessagePack.Annotations/Attributes.cs; MessagePack.Annotations has no PublicAPI.*.txt tracking so PublicApiAnalyzers did not flag it. Also 4 new public DiagnosticDescriptors MsgPack019-022 (analyzer assembly) and 4 rows added to AnalyzerReleases.Unshipped.md (git diff of PublicAPI.*.txt + scan of added public/protected declarations in src/ )

<a id="ev-b8090ba411"></a>
**check analyzers fail** (verified; cited by nemotron:N4): facts.json: analyzers fail: 1 new warnings vs base

- `analyzers` **fail**: 1 new warnings vs base (dotnet build warnings (Roslyn analyzers, StyleCop, PublicApiAnalyzers) vs base )

</details>

<details><summary><b>Full detail</b>: all tier drivers, risk score, every check, areas, not checked, residual risk</summary>

Branch `ju26-issue-2129` (32258fdb..083afd99), 28 files, +1034 -9. Author Stelian Vultur (agent-written: True). Commit: Agentic implementation of #2129 Feature Request: Allow generation of Formatter for a type in a referenced assembly

Mandate `messagepack-csharp` v6 sha256 `71386aa55974f675`, signature: valid, Toivo

<a id="all-drivers"></a>
#### All tier drivers (tier = strictest)

- block: risk score `risk`: score 175.2 (notify>=15, ask>=40, block>=130); largest: failed_checks 75 + area_sensitivity 35 + files_changed 26.1
- ask: mandate rule `public-api-change`: Public API changed: the owner decides on compatibility [public API added: new public class MessagePack.GeneratedMessagePackFormatterAttribute (with public Type? SurrogateType) in src/MessagePack.Annotations/Attributes.cs; MessagePack.Annotations has no PublicAPI.*.txt tracking so PublicApiAnalyzers did not flag it. Also 4 new public DiagnosticDescriptors MsgPack019-022 (analyzer assembly) and 4 rows added to AnalyzerReleases.Unshipped.md]
- ask: verified finding `claude:C1`: major: New public API in MessagePack.Annotations is not tracked by any PublicAPI file
- ask: verified finding `nemotron:N2`: major: Execution tests require SDK 9 / Roslyn 4.12 but the repo pins SDK 8.0.402
- ask: reviewer refusal `claude`: Security/trust implications of generating formatters that access members of external types (e.g. non-public members) (Not examined in this scoped review.)
- ask: reviewer refusal `nemotron`: Security review of serializing externally defined types via generated formatters (No runtime deserialization code was changed by this branch, but the library deserializes untrusted input and this feature lets formats be generated for types the reviewer cannot inspect; a formal security judgement is beyond the provided evidence.)
- ask: trust cap `annotations-api`: annotations-api: AI may clear at most to ask (mandate clearance right)
- notify: verified finding `claude:C3`: minor: New StyleCop warning SA1203 in the new test file
- notify: verified finding `nemotron:N1`: minor: New ExternalTypes test project is not added to the solution file
- notify: verified finding `nemotron:N3`: minor: New public API added without PublicAPI tracking in MessagePack.Annotations
- notify: verified finding `nemotron:N4`: minor: New StyleCop SA1203 warning in GeneratedMessagePackFormatterTests.cs
- notify: reviewer refusal `claude`: Correctness of GeneratedFormatterCollector.cs and the MessagePackGenerator.cs pipeline changes beyond what the 7 execution and 6 generator tests exercise (generic formatters, nested/abstract types, interaction with existing [MessagePackObject] collection, incremental-generator caching) (Scoped review: I did not read these 300+ lines line by line. Tests show only the happy paths and the 4 diagnostics.) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: reviewer refusal `claude`: Whether the API design (SurrogateType, contractless default for external types) is the right answer to the issue, which also asks for Union and other attribute-driven settings (Product/API design decision with permanent public surface; the issue proposes three alternatives and the change picks a fourth (surrogate type).) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: reviewer refusal `codex`: Full acceptance and compatibility review of the external formatter feature (This is a scoped review. The placeholder requirement contains only a broad feature statement; I did not comprehensively review all generator paths, API compatibility, or serialization contracts. The supplied facts also record a public API check failure, analyzer warning, and missing solution membership for the new test project.) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: reviewer refusal `nemotron`: Generated output of FormatterTemplate.cs and StringKeyFormatterTemplate.cs (The two generated template .cs files were listed as changed but their contents/diffs were not provided, so the exact generated formatter class text could not be inspected directly; behavior was verified through the passing execution tests instead.) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: trust cap `generator-analyzer-core`: generator-analyzer-core: AI may clear at most to notify (mandate clearance right)
- notify: trust cap `build`: build: AI may clear at most to notify (mandate clearance right)
- silent: trust cap `docs`: docs: AI may clear at most to silent (mandate clearance right)
- silent: trust cap `tests`: tests: AI may clear at most to silent (mandate clearance right)

#### Who reviewed

Participating reviewers: claude, codex, nemotron. Adjudicator: gemini. Confidential: no. Rule: proven needs every participating reviewer to say met with verified evidence, and the clause's checks to pass.

| Reviewer | Model | Prompt | Verified findings | Rejected | Refusals |
|---|---|---|---|---|---|
| claude | claude-opus-5-5 (Anthropic) | review-v1 | 3 | 1 | 3 |
| codex | GPT-6 (OpenAI) | review-v1 | 0 | 0 | 1 |
| nemotron | nvidia/nemotron-3.5-super-vl-120b-a12b (NVIDIA) | review-v1 | 4 | 0 | 2 |

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
| injection_scan | pass | countersign.injection (deterministic pattern scan) injection-v1 | no text addressed to automated reviewers in the added lines, commit message or PR text |
| deps.delta | pass | dotnet restore (every *.csproj, NuGet Audit mode=all) -> CycloneDX 1.6, base vs head 8.0.402 | 238 packages on head (238 on base) across 31 projects; 0 added, 0 version changes, 0 removed; new project(s): tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj; 4 new direct reference(s) to packages already in the graph; 0 new vulnerability hits (6 already on base) |
| build.egress | pass | CRACI network policy (cracicorp/setup@v1) + job log scan  | built on CRACI under a deny-by-default policy: only 13 TLS host patterns on ports 443 (github.com, codeload.github.com, objects.githubusercontent.com, api.nuget.org, *.nuget.org, pkgs.dev.azure.com, ...); presets ['github']; no blocked connection in 29 logs; every NuGet feed the head declares is inside the policy |
| tests.mutation | fail | evidence/scripts/mutation.py + dotnet test (one mutant at a time, the targeted filter) 8.0.402 | 8 mutants of the changed source lines: 6 killed, 1 survived, 1 not judged; 6 of 7 mutated hunks have a killed mutant; surviving hunks: GeneratedFormatterCollector.cs:277-284; 47 hunks not mutated |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v6 (71386aa55974)

#### Requirement trace (engine codes)

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-2129-F1 | proven | claude: met (6/9), codex: met (2/3), nemotron: met (9/10) | build: pass, tests.targeted: pass | - |

#### What the AI refused to decide (every reviewer refusal)

- **claude** refused: Correctness of GeneratedFormatterCollector.cs and the MessagePackGenerator.cs pipeline changes beyond what the 7 execution and 6 generator tests exercise (generic formatters, nested/abstract types, interaction with existing [MessagePackObject] collection, incremental-generator caching). Why: Scoped review: I did not read these 300+ lines line by line. Tests show only the happy paths and the 4 diagnostics. Who should decide: source-generator area owner
- **claude** refused: Whether the API design (SurrogateType, contractless default for external types) is the right answer to the issue, which also asks for Union and other attribute-driven settings. Why: Product/API design decision with permanent public surface; the issue proposes three alternatives and the change picks a fourth (surrogate type). Who should decide: MessagePack-CSharp maintainers
- **claude** refused: Security/trust implications of generating formatters that access members of external types (e.g. non-public members). Why: Not examined in this scoped review. Who should decide: security champion
- **codex** refused: Full acceptance and compatibility review of the external formatter feature. Why: This is a scoped review. The placeholder requirement contains only a broad feature statement; I did not comprehensively review all generator paths, API compatibility, or serialization contracts. The supplied facts also record a public API check failure, analyzer warning, and missing solution membership for the new test project. Who should decide: area owner
- **nemotron** refused: Generated output of FormatterTemplate.cs and StringKeyFormatterTemplate.cs. Why: The two generated template .cs files were listed as changed but their contents/diffs were not provided, so the exact generated formatter class text could not be inspected directly; behavior was verified through the passing execution tests instead. Who should decide: area owner (or re-run this review with the generated file contents)
- **nemotron** refused: Security review of serializing externally defined types via generated formatters. Why: No runtime deserialization code was changed by this branch, but the library deserializes untrusted input and this feature lets formats be generated for types the reviewer cannot inspect; a formal security judgement is beyond the provided evidence. Who should decide: area owner / security reviewer

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

- Reviewer refusal (claude): Correctness of GeneratedFormatterCollector.cs and the MessagePackGenerator.cs pipeline changes beyond what the 7 execution and 6 generator tests exercise (generic formatters, nested/abstract types, interaction with existing [MessagePackObject] collection, incremental-generator caching) (out of scope: notify)
- Reviewer refusal (claude): Whether the API design (SurrogateType, contractless default for external types) is the right answer to the issue, which also asks for Union and other attribute-driven settings (out of scope: notify)
- Reviewer refusal (claude): Security/trust implications of generating formatters that access members of external types (e.g. non-public members)
- Reviewer refusal (codex): Full acceptance and compatibility review of the external formatter feature (out of scope: notify)
- Reviewer refusal (nemotron): Generated output of FormatterTemplate.cs and StringKeyFormatterTemplate.cs (out of scope: notify)
- Reviewer refusal (nemotron): Security review of serializing externally defined types via generated formatters
- Open major finding claude:C1: New public API in MessagePack.Annotations is not tracked by any PublicAPI file
- Open major finding nemotron:N2: Execution tests require SDK 9 / Roslyn 4.12 but the repo pins SDK 8.0.402
- tests.MessagePack.Tests not run (runtime library src/MessagePack not modified by the change; suite not run)
- build.net472/netstandard not run (only the net8.0 slice of src/MessagePack was built (Linux container, Debug))
- benchmarks not run (no runtime serialization hot path touched (generator/analyzer only))
- Standing gaps of this pipeline: other-targets, runtime-perf, semantic-intent, provenance (see not checked)

<a id="risk"></a>
#### Risk score: 175.2 -> block

| Factor | Points | Reason |
|---|---:|---|
| area_sensitivity | 35 | most sensitive area touched: annotations-api (critical) |
| files_changed | 26.1 | 28 files (~1.1 per file while small, log-scaled past 80, cap 45) |
| lines_changed | 18.9 | 1035 non-generated lines (~4 per 100 lines while small, log-scaled past 100, cap 20; files and lines together at most 45) |
| generated_files | 0.2 | 2 generated files x 0.1 (cap 10) |
| public_api_change | 20 | public API changed |
| source_without_tests | 0 | tests changed alongside source |
| security_sensitive_paths | 0 | none touched |
| fail_without_fix_not_shown | 0 | tests.fail_without_fix: pass |
| reviewer_disagreement | 0 | 0 clause(s) x 8 |
| failed_checks | 75 | 3 failed check(s) x 25: analyzers, solution_membership, tests.mutation |
| **total** | **175.2** | bands: {'notify': 15, 'ask': 40, 'block': 130} |

Inputs: facts `evidence/2129/facts.json`, requirements `requirements/2129.yaml`, reviews `reviews/2129/claude.json`, `reviews/2129/codex.json`, `reviews/2129/nemotron.json`

</details>
