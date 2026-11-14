## Countersign: change 2297 is **BLOCK**, owner **Toivo**

**Agent-written change for #2297: Add ExcludeFromCodeCoverage attribute to generated code**

Changes 7 source files (CompositeResolverTemplate.tt, EnumTemplate.tt, FormatterTemplate.tt and 4 more), 1 test file, 1 doc file, 228 generated files (+1383 -9) on ju26-issue-2297 by Stelian Vultur. Judged against 1 requirement clause from #2297 (placeholder requirement set, not Tieto's official one).

**Why block**

1. More than 50 files changed: split the change so each part can be reviewed [237 files changed] ([evidence](#all-drivers))
2. Also routes to a human. Claude found a verified major issue: Coverage attribute is suppressed for netstandard2.0 and .NET Framework consumers based on a false premise (and 1 more finding) ([evidence](#f-claude-C1))
3. Also routes to a human. 1 of 1 requirement clauses not proven. Claude says not met (Codex and Nemotron: met) ([evidence](#chain-REQ-2297-F1))

<sub>All 16 tier drivers are under Full detail.</sub>

**Requirement trace**

| Status | Clause | Why |
|---|---|---|
| **NOT MET** | [F1](#chain-REQ-2297-F1) | Claude says not met (Codex and Nemotron: met) |

**What the AI found**

- **major** [Coverage attribute is suppressed for netstandard2.0 and .NET Framework consumers based on a false premise](#f-claude-C1) (Claude C1) [`ResolverTemplate.tt:14 @head`](#ev-8a0e2d6f3d) [`ResolverTemplate.tt:31 @head`](#ev-e39874618a)
- **major** [Attribute on the generated half of user-declared partial resolvers can break builds (CS0579) and silently hides user code](#f-claude-v1.C2) (Claude v1.C2) [`ResolverTemplate.tt:15 @head`](#ev-0cbe903c62) [`ResolverTemplate.tt:17 @head`](#ev-90a721f84c)
- **minor** [Unrelated formatting change in TransformUtilities.cs outside the requirement scope](#f-nemotron-N1) (Nemotron N1, also Claude) [`TransformUtilities.cs:58 @head`](#ev-66b5ead8c5) [`TransformUtilities.cs:58 @base`](#ev-064cb49fd0)
- +1 more under Evidence.

<a id="refused"></a>**What the AI refused to decide, and who should**

- <a id="refusal-6"></a>**runtime execution of generated formatters/resolvers (execution tests)** *Who:* area owner / maintainer, after moving to an SDK with Roslyn >= 4.12 (raised by Nemotron) <details><summary>why</summary>tests.execution was not run: SDK 8.0.402 ships Roslyn 4.11 while the generator references Microsoft.CodeAnalysis 4.12.0, so execution test projects fail to compile (CS9057/CS0117); this mismatch exists on base too and is environmental, not caused by the change.</details>
- Whether [F1](#chain-REQ-2297-F1) is met: see the trace. *Who:* Toivo

<details id="refused-peripheral"><summary>5 peripheral refusals (out of scope for this change)</summary><a id="refusal-1"></a>Whether all 228 regenerated test resource files differ from base only by the coverage attribute and the brace/newline fix (Claude) · <a id="refusal-2"></a>Effect on generated code in consumers built with older compilers or with ImplicitUsings/nullable settings (Claude) · <a id="refusal-3"></a>The TransformUtilities brace change ('{' to '{\r\n' when constraints exist): intended fix or incidental (Claude) · <a id="refusal-4"></a>Coverage of generated code not exercised by the supplied generator test fixture (Codex) · <a id="refusal-5"></a>netstandard2.0 and .NET Framework compilation of generated output (Nemotron)</details>

**Not checked, and why**

- `tests.execution`: SDK 8.0.402 ships Roslyn 4.11 but MessagePack.SourceGenerator references Microsoft.CodeAnalysis 4.12.0 <details><summary>more</summary>so csc refuses to load the generator (warning CS9057) and projects that consume it as an analyzer (tests/MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) fail to compile (CS0117 'GeneratedMessagePackResolver' does not contain 'Instance'). This also happens on base 32258fdb, so it is an environment/toolchain mismatch, not caused by the change. Needs an SDK with Roslyn &gt;= 4.12 (e.g. .NET SDK 9.0.1xx); swapping in a newer compiler toolset was not permitted in this run.</details>
- `tests.MessagePack.Tests`: runtime library src/MessagePack not modified by the change; suite not run
- `build.net472/netstandard`: only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks`: no runtime serialization hot path touched (generator/analyzer only)
- Standing pipeline gaps: `other-targets`, `runtime-perf`, `semantic-intent`, `provenance`

**Residual risk you accept by signing**

- Open major finding: Coverage attribute is suppressed for netstandard2.0 and .NET Framework consumers based on a false premise
- Open major finding: Attribute on the generated half of user-declared partial resolvers can break builds (CS0579) and silently hides user code
- Not proven by the AI: REQ-2297-F1. Signing means you judge them yourself.
- 1 question the AI declined to decide (listed above) are yours.

<details><summary>4 more risks that do not set the tier</summary>5 peripheral refusals (out of scope for this change) are yours too. · Not run: tests.execution, tests.MessagePack.Tests, build.net472/netstandard, benchmarks · 3 disputed items not adjudicated · Standing pipeline gaps: other-targets, runtime-perf, semantic-intent, provenance</details>

**Toivo signs** (required; reject, request-changes)

```
countersign sign 2297 --as Toivo --decision … --note "…"
```

<details><summary>And rate the 4 verified findings (full command)</summary>

One `--finding` flag each: `accepted` (real), `rejected` (a false positive) or `unsure`, optionally `:reason`. A finding without a flag is recorded as `unrated`.

- `claude:C1` (major): Coverage attribute is suppressed for netstandard2.0 and .NET Framework consumers based on a false premise
- `claude:C2` (info): 237-file change is dominated by regenerated test resources
- `nemotron:N1` (minor): Unrelated formatting change in TransformUtilities.cs outside the requirement scope
- `claude:v1.C2` (major): Attribute on the generated half of user-declared partial resolvers can break builds (CS0579) and silently hides user code

```
countersign sign 2297 --as Toivo --decision <reject|request-changes> --note "..." \
  --finding claude:C1=<accepted|rejected|unsure> \
  --finding claude:C2=<accepted|rejected|unsure> \
  --finding nemotron:N1=<accepted|rejected|unsure> \
  --finding claude:v1.C2=<accepted|rejected|unsure>
```

</details>

<details><summary>What your signature says</summary>

> I, Toivo, have read what was checked and by whom, what was not checked and why, and the residual risk listed in this pack, and I own this decision.

It covers the sha256 of this pack's canonical JSON, the decision, your verdict on each finding, the time and the signer, and is appended to the hash-chained ledger.

</details>

<a id="supply-chain"></a>**Supply chain (from the build):** deps.delta pass: no package added or moved, 0 new advisories (6 already on base); build.egress pass; CRACI trace pass

<details><summary>Supply-chain detail</summary>

`deps.delta` **pass**: 238 packages on head (238 on base) across 30 projects; 0 added, 0 version changes, 0 removed; 0 new vulnerability hits (6 already on base)

- Already on base (6): Microsoft.NETCore.Jit 1.0.2 high GHSA-xcvr-qv8h-m7xw, NuGet.Packaging 6.8.0 critical GHSA-68w7-72jg-6qpp, NuGet.Packaging 6.8.0 low GHSA-g4vj-cjjj-v7hg, NuGet.Protocol 6.8.0 low GHSA-g4vj-cjjj-v7hg, System.Formats.Asn1 6.0.0 high GHSA-447r-wph3-92pm, System.Text.Encodings.Web 4.5.0 critical GHSA-ghhp-997w-qr28
- SBOMs (CycloneDX): `evidence/base/sbom.cdx.json`, `evidence/2297/sbom.cdx.json`
- `build.egress` **pass**: default deny, presets ['github'], 13 TLS host patterns; run https://github.com/Zawaer/countersign/actions/runs/43559099382; policy sha256 `31fafb855e98`
- `craci.network` **pass**: 181 connections to 13 hosts, 0 proxy violations: builds.dotnet.microsoft.com (468.1 MB), api.nuget.org (271.4 MB), github.com (19.3 MB), codeload.github.com (4.2 MB), pkgs.dev.azure.com (0.2 MB), ci.dot.net (44 kB); denied, not counted as the change's: 2904 certificate revocation lookups (CRL/OCSP over plain HTTP: crl3.digicert.com, crl4.digicert.com, ocsp.digicert.com, s.symcb.com, s.symcd.com, ts-crl.ws.symantec.com, ts-ocsp.ws.symantec.com), so package-signature revocation was not checked online; 3 request(s) during toolchain setup, before the change was built (aka.ms); 7 host(s) allowed by a preset or CRACI's own CI-service rule, not a listed TLS host (rules: github-actions-actions.githubusercontent.com, github-actions-cache-results-receiver.actions.githubusercontent.com, recorded-http-api.github.com)

</details>

<details><summary><b>Where the trust comes from</b> (per requirement clause)</summary>

<a id="chain-REQ-2297-F1"></a>
#### REQ-2297-F1: **NOT MET**

> Add ExcludeFromCodeCoverage attribute to generated code.

- **Claude: not met** (5/6 verified). On net5+ consumers the attribute is emitted on every generated type (AllGeneratedTypesAreExcludedFromCodeCoverage passes at head and fails on base). But every emission is wrapped in '#if !NETSTANDARD2_0 && !NETFRAMEWORK', which is evaluated in the consumer's compilation, so consumers targeting netstandard2.0 or .NET Framework get no attribute. The stated reason ('not available on netstandard2.0 or .NET Framework') is wrong: System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverageAttribute is in the netstandard 2.0 reference assembly (I checked netstandard.library 2.0.3's netstandard.xml) and has been in .NET Framework since 4.0, with AttributeTargets.Class allowed. So for targets MessagePack supports, the requirement is not met, and a test pins the omission.
- **Codex: met** (3/4 verified). The formatter template conditionally emits ExcludeFromCodeCoverage, and tests confirm generated types receive the attribute and that its use is guarded for target frameworks lacking it.
- **Nemotron: met** (10/11 verified). All six source-generator templates emit [global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage] behind the #if !NETSTANDARD2_0 && !NETFRAMEWORK guard (e.g. ResolverTemplate.tt lines 14-16 and FormatterTemplate.tt lines 14-16; the same pattern appears in CompositeResolverTemplate, EnumTemplate, StringKeyFormatterTemplate and UnionTemplate), the checked-in generated outputs were regenerated accordingly, the new test CodeCoverageExclusionTests.AllGeneratedTypesAreExcludedFromCodeCoverage passes on head and failed on base source, and the full 169-test generator suite passes on head.
- **Checks:** `build` pass, `tests.targeted` pass
- **What would settle it:** A fix, or evidence that refutes Claude's objection

</details>

<details><summary><b>Reviewer panel</b> (who said what)</summary>
<a id="panel"></a>

> Codex and Nemotron said met to all 1 clauses; Claude raised a verified major finding they did not (claude:C1: Coverage attribute is suppressed for netstandard2.0 and .NET Framework consumers based on a false premise). Claude also did not say met on REQ-2297-F1, so that clause is refused. Unanimity is required: one verified objection is enough to send it to Toivo.
> REQ-2297-F1: Claude: not met; Codex, Nemotron: met. A split verdict is a refusal, not a vote.

| Clause | Claude | Codex | Nemotron | Result |
|---|---|---|---|---|
| REQ-2297-F1 | not met | met | met | **not met** |

- **Claude** (claude-opus-5-5, Anthropic): citations 14 verified / 0 rejected; findings 3 verified / 0 rejected; 3 refusals. Only Claude raised: [C1](#f-claude-C1) major Coverage attribute is suppressed for netstandard2.0 and .NET Framework consumers based on a false premise, [v1.C2](#f-claude-v1.C2) major Attribute on the generated half of user-declared partial resolvers can break builds (CS0579) and silently hides user code
- **Codex** (GPT-6, OpenAI): citations 4 verified / 0 rejected; findings 0 verified / 0 rejected; 1 refusals.
- **Nemotron** (nvidia/nemotron-3.5-super-vl-120b-a12b, NVIDIA): citations 13 verified / 0 rejected; findings 1 verified / 0 rejected; 2 refusals.

3 disputed item(s), not adjudicated: REQ-2297-F1, finding:claude:C1, finding:claude:v1.C2

</details>

<details><summary><b>Evidence</b> (findings, cited code, tests and checks)</summary>

<a id="f-claude-C1"></a>
#### Claude C1 [major, correctness]: Coverage attribute is suppressed for netstandard2.0 and .NET Framework consumers based on a false premise

The templates guard the attribute with '#if !NETSTANDARD2_0 && !NETFRAMEWORK'. ExcludeFromCodeCoverageAttribute exists in netstandard2.0 and in .NET Framework 4.0+, so the guard only removes the feature for Unity/.NET Framework/netstandard library consumers. The test ExcludeAttributeIsGuardedForTargetsWhereItIsUnavailable pins this behaviour, and the README claims 'All generated formatters and resolvers are decorated', which is false for those targets.

Evidence: [`ResolverTemplate.tt:14 @head`](#ev-8a0e2d6f3d) [`ResolverTemplate.tt:31 @head`](#ev-e39874618a) [`FormatterTemplate.tt:14 @head`](#ev-ad9cf8085f) [`CodeCoverageExclusionTests.cs:19 @head`](#ev-b78a93a613) [`README.md:1639 @head`](#ev-650d2b464e) [`test ExcludeAttributeIsGuardedForTargetsWhereItIsUnavailable passed`](#ev-f588e6e008)

Tier effect: ask

Suggested fix: Drop the #if guard and emit [global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage] unconditionally; replace the guard test with one that compiles generated code against a netstandard2.0 / net472 reference set.

<a id="f-claude-C2"></a>
#### Claude C2 [info, scope]: 237-file change is dominated by regenerated test resources

228 of 237 files are regenerated expected-output resources. The behavioural change is in 7 template/source files. Reviewers should read the templates and spot-check the resources, not the reverse.

Evidence: [`check tests.full_suite`](#ev-df050a6665) [`TransformUtilities.cs:58 @head`](#ev-66b5ead8c5)

Tier effect: silent

<a id="f-nemotron-N1"></a>
#### Nemotron N1 [minor, scope]: Unrelated formatting change in TransformUtilities.cs outside the requirement scope

TransformUtilities.cs line 58 changed the brace emission for nested types that carry type constraints from emitting just "{" to emitting "{\r\n", adding a newline after the opening brace in generated code. This is unrelated to REQ-2297-F1 (ExcludeFromCodeCoverage) and changes generated output beyond the requirement's scope.

Evidence: [`TransformUtilities.cs:58 @head`](#ev-66b5ead8c5) [`TransformUtilities.cs:58 @base`](#ev-064cb49fd0)

Tier effect: notify

Suggested fix: Revert TransformUtilities.cs to the base line, or move this formatting change to a separate change so this change stays limited to ExcludeFromCodeCoverage emission.

<a id="f-claude-v1.C2"></a>
#### Claude v1.C2 [major, correctness]: Attribute on the generated half of user-declared partial resolvers can break builds (CS0579) and silently hides user code

The resolver and composite resolver templates emit '[ExcludeFromCodeCoverage] partial class <ResolverName>' for a class the user declares as partial. ExcludeFromCodeCoverageAttribute has AllowMultiple = false. A user who already put [ExcludeFromCodeCoverage] on their partial resolver declaration will get error CS0579 'Duplicate attribute' after upgrading on the targets where the guard is active (I reproduced CS0579 with two partial declarations each carrying the attribute). Even without a conflict, the attribute applies to the whole type, so any hand-written members in the user's partial resolver are now excluded from coverage too.

Evidence: [`ResolverTemplate.tt:15 @head`](#ev-0cbe903c62) [`ResolverTemplate.tt:17 @head`](#ev-90a721f84c) [`CompositeResolverTemplate.tt:8 @head`](#ev-291c35f5ef) [`CompositeResolverTemplate.tt:10 @head`](#ev-5e0db9baf8)

Tier effect: ask

Suggested fix: On the user-declared partial resolver, put the attribute on the generated members (Instance field, GetFormatter method, nested FormatterCache/GetFormatterHelper classes) instead of the type, or skip it when the user's declaration already carries the attribute.

#### Cited evidence

<a id="ev-8a0e2d6f3d"></a>
**ResolverTemplate.tt:14 @head** (verified; cited by claude on REQ-2297-F1, nemotron on REQ-2297-F1, claude:C1): quote matches src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt:14 at head a0aa5ab2

```text
// src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt @ a0aa5ab2
  11 | <# using (TransformUtilities.EmitNestingTypesAndNamespaces(this.ResolverName, this.Write)) { #>
  12 | 
  13 | /// <summary>A MessagePack resolver that uses generated formatters for types in this assembly.</summary>
> 14 | #if !NETSTANDARD2_0 && !NETFRAMEWORK
  15 | [global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage]
  16 | #endif
  17 | partial class <#= ResolverName.Name #> : MsgPack::IFormatterResolver
```

<a id="ev-d81ccbccad"></a>
**CodeCoverageExclusionTests.cs:18 @head** (verified; cited by claude on REQ-2297-F1): quote matches tests/MessagePack.SourceGenerator.Tests/CodeCoverageExclusionTests.cs:18 at head a0aa5ab2

```text
// tests/MessagePack.SourceGenerator.Tests/CodeCoverageExclusionTests.cs @ a0aa5ab2
  15 | {
  16 |     private const string ExcludeAttribute = "[global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage]";
  17 | 
> 18 |     // The attribute is not available on netstandard2.0 or .NET Framework, so it is only emitted where it exists.
  19 |     private const string Guard = "#if !NETSTANDARD2_0 && !NETFRAMEWORK";
  20 | 
  21 |     private const string TestSource = """
```

<a id="ev-1ea94bff54"></a>
**test AllGeneratedTypesAreExcludedFromCodeCoverage passed** (verified; cited by claude on REQ-2297-F1, codex on REQ-2297-F1, nemotron on REQ-2297-F1): facts.json tests.targeted: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-09419f4337"></a>
**test AllGeneratedTypesAreExcludedFromCodeCoverage failed** (verified; cited by claude on REQ-2297-F1, nemotron on REQ-2297-F1): facts.json tests.fail_without_fix: failed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-f588e6e008"></a>
**test ExcludeAttributeIsGuardedForTargetsWhereItIsUnavailable passed** (verified; cited by claude on REQ-2297-F1, codex on REQ-2297-F1, claude:C1): facts.json tests.targeted: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-f03b126649"></a>
**REQ-2297-F1 text** (verified; cited by claude on REQ-2297-F1, nemotron on REQ-2297-F1): REQ-2297-F1 text contains the quote

> Add ExcludeFromCodeCoverage attribute to generated code.

<a id="ev-1de9933827"></a>
**FormatterTemplate.tt:15 @head** (verified; cited by codex on REQ-2297-F1, nemotron on REQ-2297-F1): quote matches src/MessagePack.SourceGenerator/Transforms/FormatterTemplate.tt:15 at head a0aa5ab2

```text
// src/MessagePack.SourceGenerator/Transforms/FormatterTemplate.tt @ a0aa5ab2
  12 | 
  13 | <#  bool isFormatterResolverNecessary = GeneratorUtilities.ShouldUseFormatterResolver(Info.Members);#>
  14 | #if !NETSTANDARD2_0 && !NETFRAMEWORK
> 15 | 	[global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage]
  16 | #endif
  17 | 	internal sealed class <#= Info.Formatter.GetQualifiedName(Qualifiers.None) #> : MsgPack::Formatters.IMessagePackFormatter<<#= Info.DataType.GetQualifiedName(genericStyle: GenericParameterStyle.Identifiers) #>>
  18 | <# TransformUtilities.EmitTypeConstraints(Info.Formatter, this.Write); #>
```

<a id="ev-d78b746a74"></a>
**check tests.fail_without_fix** (verified; cited by codex on REQ-2297-F1): facts.json: tests.fail_without_fix pass: new tests fail on base source: 2/2 failed -> tests do cover the change

- `tests.fail_without_fix` **pass**: new tests fail on base source: 2/2 failed -> tests do cover the change (dotnet test (source reverted, tests kept) 8.0.402)
- log: `evidence/2297/logs/tests_fail_without_fix.1.log`

<a id="ev-0cbe903c62"></a>
**ResolverTemplate.tt:15 @head** (verified; cited by nemotron on REQ-2297-F1, claude:v1.C2): quote matches src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt:15 at head a0aa5ab2

```text
// src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt @ a0aa5ab2
  12 | 
  13 | /// <summary>A MessagePack resolver that uses generated formatters for types in this assembly.</summary>
  14 | #if !NETSTANDARD2_0 && !NETFRAMEWORK
> 15 | [global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage]
  16 | #endif
  17 | partial class <#= ResolverName.Name #> : MsgPack::IFormatterResolver
  18 | {
```

<a id="ev-ad9cf8085f"></a>
**FormatterTemplate.tt:14 @head** (verified; cited by nemotron on REQ-2297-F1, claude:C1): quote matches src/MessagePack.SourceGenerator/Transforms/FormatterTemplate.tt:14 at head a0aa5ab2

```text
// src/MessagePack.SourceGenerator/Transforms/FormatterTemplate.tt @ a0aa5ab2
  11 | <# using (this.EmitNestingTypesAndNamespaces(this.Write)) { #>
  12 | 
  13 | <#  bool isFormatterResolverNecessary = GeneratorUtilities.ShouldUseFormatterResolver(Info.Members);#>
> 14 | #if !NETSTANDARD2_0 && !NETFRAMEWORK
  15 | 	[global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage]
  16 | #endif
  17 | 	internal sealed class <#= Info.Formatter.GetQualifiedName(Qualifiers.None) #> : MsgPack::Formatters.IMessagePackFormatter<<#= Info.DataType.GetQualifiedName(genericStyle: GenericParameterStyle.Identifiers) #>>
```

<a id="ev-85a77b3f18"></a>
**CompositeResolverTemplate.tt:7 @head** (verified; cited by nemotron on REQ-2297-F1): quote matches src/MessagePack.SourceGenerator/Transforms/CompositeResolverTemplate.tt:7 at head a0aa5ab2

```text
// src/MessagePack.SourceGenerator/Transforms/CompositeResolverTemplate.tt @ a0aa5ab2
   4 | 
   5 | <# using (TransformUtilities.EmitNestingTypesAndNamespaces(this.ResolverName, this.Write)) { #>
   6 | 
>  7 | #if !NETSTANDARD2_0 && !NETFRAMEWORK
   8 | [global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage]
   9 | #endif
  10 | partial class <#= ResolverName.Name #> : MsgPack::IFormatterResolver
```

<a id="ev-291c35f5ef"></a>
**CompositeResolverTemplate.tt:8 @head** (verified; cited by nemotron on REQ-2297-F1, claude:v1.C2): quote matches src/MessagePack.SourceGenerator/Transforms/CompositeResolverTemplate.tt:8 at head a0aa5ab2

```text
// src/MessagePack.SourceGenerator/Transforms/CompositeResolverTemplate.tt @ a0aa5ab2
   5 | <# using (TransformUtilities.EmitNestingTypesAndNamespaces(this.ResolverName, this.Write)) { #>
   6 | 
   7 | #if !NETSTANDARD2_0 && !NETFRAMEWORK
>  8 | [global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage]
   9 | #endif
  10 | partial class <#= ResolverName.Name #> : MsgPack::IFormatterResolver
  11 | {
```

<a id="ev-d448f979e6"></a>
**check tests.full_suite pass** (verified; cited by nemotron on REQ-2297-F1): facts.json: tests.full_suite pass: tests/MessagePack.SourceGenerator.Tests: 169 tests, 169 passed, 0 failed (0 not failing on base, 0 also failing on base)

- `tests.full_suite` **pass**: tests/MessagePack.SourceGenerator.Tests: 169 tests, 169 passed, 0 failed (0 not failing on base, 0 also failing on base) (dotnet test 8.0.402)
- log: `evidence/2297/logs/tests_full_suite.log`

<a id="ev-62faeb2508"></a>
**check tests.fail_without_fix pass** (verified; cited by nemotron on REQ-2297-F1): facts.json: tests.fail_without_fix pass: new tests fail on base source: 2/2 failed -> tests do cover the change

- `tests.fail_without_fix` **pass**: new tests fail on base source: 2/2 failed -> tests do cover the change (dotnet test (source reverted, tests kept) 8.0.402)
- log: `evidence/2297/logs/tests_fail_without_fix.1.log`

<a id="ev-e39874618a"></a>
**ResolverTemplate.tt:31 @head** (verified; cited by claude:C1): quote matches src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt:31 at head a0aa5ab2

```text
// src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt @ a0aa5ab2
  28 | 		return FormatterCache<T>.Formatter;
  29 | 	}
  30 | 
> 31 | #if !NETSTANDARD2_0 && !NETFRAMEWORK
  32 | 	[global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage]
  33 | #endif
  34 | 	private static class FormatterCache<T>
```

<a id="ev-b78a93a613"></a>
**CodeCoverageExclusionTests.cs:19 @head** (verified; cited by claude:C1): quote matches tests/MessagePack.SourceGenerator.Tests/CodeCoverageExclusionTests.cs:19 at head a0aa5ab2

```text
// tests/MessagePack.SourceGenerator.Tests/CodeCoverageExclusionTests.cs @ a0aa5ab2
  16 |     private const string ExcludeAttribute = "[global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage]";
  17 | 
  18 |     // The attribute is not available on netstandard2.0 or .NET Framework, so it is only emitted where it exists.
> 19 |     private const string Guard = "#if !NETSTANDARD2_0 && !NETFRAMEWORK";
  20 | 
  21 |     private const string TestSource = """
  22 |         using MessagePack;
```

<a id="ev-650d2b464e"></a>
**README.md:1639 @head** (verified; cited by claude:C1): quote matches README.md:1639 at head a0aa5ab2

```text
// README.md @ a0aa5ab2
  1636 | 
  1637 | Learn more about using a mix of your own custom formatters and automatically generated ones in [the Analyzer section](#analyzer).
  1638 | 
> 1639 | All generated formatters and resolvers are decorated with `[ExcludeFromCodeCoverage]`, so generated code does not skew code coverage reports.
  1640 | The attribute is only emitted for targets where it is available (not `netstandard2.0` or .NET Framework).
  1641 | 
  1642 | ### MagicOnion
```

<a id="ev-df050a6665"></a>
**check tests.full_suite** (verified; cited by claude:C2): facts.json: tests.full_suite pass: tests/MessagePack.SourceGenerator.Tests: 169 tests, 169 passed, 0 failed (0 not failing on base, 0 also failing on base)

- `tests.full_suite` **pass**: tests/MessagePack.SourceGenerator.Tests: 169 tests, 169 passed, 0 failed (0 not failing on base, 0 also failing on base) (dotnet test 8.0.402)
- log: `evidence/2297/logs/tests_full_suite.log`

<a id="ev-66b5ead8c5"></a>
**TransformUtilities.cs:58 @head** (verified; cited by claude:C2, nemotron:N1): quote matches src/MessagePack.SourceGenerator/Transforms/TransformUtilities.cs:58 at head a0aa5ab2

```text
// src/MessagePack.SourceGenerator/Transforms/TransformUtilities.cs @ a0aa5ab2
  55 |                 writer($"partial {kind} {nestingType.GetQualifiedName(Qualifiers.None, GenericParameterStyle.Identifiers)}");
  56 |                 bool anyConstraints = EmitTypeConstraints(nestingType, writer, leadingLineFeedIfAny: true);
  57 | 
> 58 |                 writer(anyConstraints ? "{\r\n" : " {\r\n");
  59 |                 reverseAction.Push(new DisposeAction(() => writer("}\r\n")));
  60 | 
  61 |                 return new DisposeAction(() =>
```

<a id="ev-064cb49fd0"></a>
**TransformUtilities.cs:58 @base** (verified; cited by nemotron:N1): quote matches src/MessagePack.SourceGenerator/Transforms/TransformUtilities.cs:58 at base 32258fdb

```text
// src/MessagePack.SourceGenerator/Transforms/TransformUtilities.cs @ 32258fdb
  55 |                 writer($"partial {kind} {nestingType.GetQualifiedName(Qualifiers.None, GenericParameterStyle.Identifiers)}");
  56 |                 bool anyConstraints = EmitTypeConstraints(nestingType, writer, leadingLineFeedIfAny: true);
  57 | 
> 58 |                 writer(anyConstraints ? "{" : " {\r\n");
  59 |                 reverseAction.Push(new DisposeAction(() => writer("}\r\n")));
  60 | 
  61 |                 return new DisposeAction(() =>
```

<a id="ev-90a721f84c"></a>
**ResolverTemplate.tt:17 @head** (verified; cited by claude:v1.C2): quote matches src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt:17 at head a0aa5ab2

```text
// src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt @ a0aa5ab2
  14 | #if !NETSTANDARD2_0 && !NETFRAMEWORK
  15 | [global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage]
  16 | #endif
> 17 | partial class <#= ResolverName.Name #> : MsgPack::IFormatterResolver
  18 | {
  19 | 	/// <summary>An instance of this resolver that only returns formatters specifically generated for types in this assembly.</summary>
  20 | 	public static readonly MsgPack::IFormatterResolver Instance = new <#= ResolverName.Name #>();
```

<a id="ev-5e0db9baf8"></a>
**CompositeResolverTemplate.tt:10 @head** (verified; cited by claude:v1.C2): quote matches src/MessagePack.SourceGenerator/Transforms/CompositeResolverTemplate.tt:10 at head a0aa5ab2

```text
// src/MessagePack.SourceGenerator/Transforms/CompositeResolverTemplate.tt @ a0aa5ab2
   7 | #if !NETSTANDARD2_0 && !NETFRAMEWORK
   8 | [global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage]
   9 | #endif
> 10 | partial class <#= ResolverName.Name #> : MsgPack::IFormatterResolver
  11 | {
  12 | 	public static readonly <#= ResolverName.Name #> Instance = new <#= ResolverName.Name #>();
  13 | 
```

</details>

<details><summary><b>Full detail</b>: all tier drivers, risk score, every check, areas, not checked, residual risk</summary>

Branch `ju26-issue-2297` (32258fdb..a0aa5ab2), 237 files, +1383 -9. Author Stelian Vultur (agent-written: True). Commit: implement issue #2297 : Add ExcludeFromCodeCoverage attribute to generated code

Mandate `messagepack-csharp` v6 sha256 `71386aa55974f675`, signature: valid, Toivo

<a id="all-drivers"></a>
#### All tier drivers (tier = strictest)

- block: mandate rule `split-large-change`: More than 50 files changed: split the change so each part can be reviewed [237 files changed]
- ask: mandate rule `generated-files`: More than 10 generated files: a human confirms the regeneration is intended [228 generated files]
- ask: verified finding `claude:C1`: major: Coverage attribute is suppressed for netstandard2.0 and .NET Framework consumers based on a false premise
- ask: verified finding `claude:v1.C2`: major: Attribute on the generated half of user-declared partial resolvers can break builds (CS0579) and silently hides user code
- ask: refused clause `REQ-2297-F1`: not_met: claude: On net5+ consumers the attribute is emitted on every generated type (AllGeneratedTypesAreExcludedFromCodeCoverage passes at head and fails on base). But every emission is wrapped in '#if !NETSTANDARD2_0 && !NETFRAMEWORK', which is evaluated in the consumer's compilation, so consumers targeting netstandard2.0 or .NET Framework get no attribute. The stated reason ('not available on netstandard2.0 or .NET Framework') is wrong: System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverageAttribute is in the netstandard 2.0 reference assembly (I checked netstandard.library 2.0.3's netstandard.xml) and has been in .NET Framework since 4.0, with AttributeTargets.Class allowed. So for targets MessagePack supports, the requirement is not met, and a test pins the omission.; reviewers_disagree: claude says not_met, codex says met, nemotron says met
- ask: reviewer refusal `nemotron`: runtime execution of generated formatters/resolvers (execution tests) (tests.execution was not run: SDK 8.0.402 ships Roslyn 4.11 while the generator references Microsoft.CodeAnalysis 4.12.0, so execution test projects fail to compile (CS9057/CS0117); this mismatch exists on base too and is environmental, not caused by the change.)
- ask: risk score `risk`: score 83.0 (notify>=15, ask>=40, block>=130); largest: files_changed 45 + area_sensitivity 20 + generated_files 10
- notify: verified finding `nemotron:N1`: minor: Unrelated formatting change in TransformUtilities.cs outside the requirement scope
- notify: reviewer refusal `claude`: Whether all 228 regenerated test resource files differ from base only by the coverage attribute and the brace/newline fix (Scoped review: not read individually. tests.full_suite passing shows they match the new generator output, not that the output is otherwise unchanged.) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: reviewer refusal `claude`: Effect on generated code in consumers built with older compilers or with ImplicitUsings/nullable settings (Execution tests not run for this change (tests.execution not run: SDK 8 cannot load the generator); no compile of generated code against net472/netstandard2.0 targets.) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: reviewer refusal `claude`: The TransformUtilities brace change ('{' to '{\r\n' when constraints exist): intended fix or incidental (Not mentioned in the issue; I did not establish what output it changes beyond the resources.) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: reviewer refusal `codex`: Coverage of generated code not exercised by the supplied generator test fixture (The supplied tests exercise the generated output represented by their fixture; I did not independently inspect every generation path or framework configuration beyond the cited template and facts.) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: reviewer refusal `nemotron`: netstandard2.0 and .NET Framework compilation of generated output (build.net472/netstandard was not run (Linux container, only net8.0 built), so the #if guard's effect for those targets was not compile-verified; only the template text was inspected.) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: trust cap `generator-analyzer-core`: generator-analyzer-core: AI may clear at most to notify (mandate clearance right)
- silent: trust cap `docs`: docs: AI may clear at most to silent (mandate clearance right)
- silent: trust cap `tests`: tests: AI may clear at most to silent (mandate clearance right)

#### Who reviewed

Participating reviewers: claude, codex, nemotron. Adjudicator: gemini. Confidential: no. Rule: proven needs every participating reviewer to say met with verified evidence, and the clause's checks to pass.

| Reviewer | Model | Prompt | Verified findings | Rejected | Refusals |
|---|---|---|---|---|---|
| claude | claude-opus-5-5 (Anthropic) | review-v1 | 2 | 0 | 3 |
| codex | GPT-6 (OpenAI) | review-v1 | 0 | 0 | 1 |
| nemotron | nvidia/nemotron-3.5-super-vl-120b-a12b (NVIDIA) | review-v1 | 1 | 0 | 2 |

#### Every check

| Check | Status | Tool | Summary |
|---|---|---|---|
| build | pass | dotnet build 8.0.402 | 0 errors, 1 unique warnings |
| tests.targeted | pass | dotnet test 8.0.402 | 2 passed, 0 failed, 0 skipped (2 new tests in run) |
| tests.fail_without_fix | pass | dotnet test (source reverted, tests kept) 8.0.402 | new tests fail on base source: 2/2 failed -> tests do cover the change |
| tests.full_suite | pass | dotnet test 8.0.402 | tests/MessagePack.SourceGenerator.Tests: 169 tests, 169 passed, 0 failed (0 not failing on base, 0 also failing on base) |
| public_api | pass | git diff of PublicAPI.*.txt + scan of added public/protected declarations in src/  | no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or removed in src/ |
| analyzers | pass | dotnet build warnings (Roslyn analyzers, StyleCop, PublicApiAnalyzers) vs base  | no new warnings |
| injection_scan | pass | countersign.injection (deterministic pattern scan) injection-v1 | no text addressed to automated reviewers in the added lines, commit message or PR text |
| deps.delta | pass | dotnet restore (every *.csproj, NuGet Audit mode=all) -> CycloneDX 1.6, base vs head 8.0.402 | 238 packages on head (238 on base) across 30 projects; 0 added, 0 version changes, 0 removed; 0 new vulnerability hits (6 already on base) |
| build.egress | pass | CRACI network policy (cracicorp/setup@v1) + job log scan  | built on CRACI under a deny-by-default policy: only 13 TLS host patterns on ports 443 (github.com, codeload.github.com, objects.githubusercontent.com, api.nuget.org, *.nuget.org, pkgs.dev.azure.com, ...); presets ['github']; no blocked connection in 13 logs; every NuGet feed the head declares is inside the policy |
| craci.sbom | pass | CRACI API v1preview1 (https://api.craci.com)  | CRACI's job SBOM: 0 components (none); 0 NuGet, all in our restore graph (242 NuGet packages). CRACI has no NuGet source type, so the facts job reaches NuGet through a TLS connection rule, which CRACI does not inspect for packages: the NuGet graph is recorded by deps.delta, CRACI records the connections (craci.network) |
| craci.network | pass | CRACI API v1preview1 (https://api.craci.com)  | 181 connections to 13 hosts, 0 proxy violations: builds.dotnet.microsoft.com (468.1 MB), api.nuget.org (271.4 MB), github.com (19.3 MB), codeload.github.com (4.2 MB), pkgs.dev.azure.com (0.2 MB), ci.dot.net (44 kB); denied, not counted as the change's: 2904 certificate revocation lookups (CRL/OCSP over plain HTTP: crl3.digicert.com, crl4.digicert.com, ocsp.digicert.com, s.symcb.com, s.symcd.com, ts-crl.ws.symantec.com, ts-ocsp.ws.symantec.com), so package-signature revocation was not checked online; 3 request(s) during toolchain setup, before the change was built (aka.ms); 7 host(s) allowed by a preset or CRACI's own CI-service rule, not a listed TLS host (rules: github-actions-actions.githubusercontent.com, github-actions-cache-results-receiver.actions.githubusercontent.com, recorded-http-api.github.com) |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v6 (71386aa55974)

#### Requirement trace (engine codes)

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-2297-F1 | refused | claude: not_met (5/6), codex: met (3/4), nemotron: met (10/11) | build: pass, tests.targeted: pass | not_met, reviewers_disagree |

#### What the AI refused to decide (every reviewer refusal)

- **claude** refused: Whether all 228 regenerated test resource files differ from base only by the coverage attribute and the brace/newline fix. Why: Scoped review: not read individually. tests.full_suite passing shows they match the new generator output, not that the output is otherwise unchanged. Who should decide: source-generator area owner (diff-filter the resources)
- **claude** refused: Effect on generated code in consumers built with older compilers or with ImplicitUsings/nullable settings. Why: Execution tests not run for this change (tests.execution not run: SDK 8 cannot load the generator); no compile of generated code against net472/netstandard2.0 targets. Who should decide: source-generator area owner
- **claude** refused: The TransformUtilities brace change ('{' to '{\r\n' when constraints exist): intended fix or incidental. Why: Not mentioned in the issue; I did not establish what output it changes beyond the resources. Who should decide: source-generator area owner
- **codex** refused: Coverage of generated code not exercised by the supplied generator test fixture. Why: The supplied tests exercise the generated output represented by their fixture; I did not independently inspect every generation path or framework configuration beyond the cited template and facts. Who should decide: area owner
- **nemotron** refused: netstandard2.0 and .NET Framework compilation of generated output. Why: build.net472/netstandard was not run (Linux container, only net8.0 built), so the #if guard's effect for those targets was not compile-verified; only the template text was inspected. Who should decide: area owner / maintainer with a multi-target build
- **nemotron** refused: runtime execution of generated formatters/resolvers (execution tests). Why: tests.execution was not run: SDK 8.0.402 ships Roslyn 4.11 while the generator references Microsoft.CodeAnalysis 4.12.0, so execution test projects fail to compile (CS9057/CS0117); this mismatch exists on base too and is environmental, not caused by the change. Who should decide: area owner / maintainer, after moving to an SDK with Roslyn >= 4.12

<a id="areas"></a>
#### Areas

| Area | Owner | Sensitivity | AI cap | Files |
|---|---|---|---|---:|
| generator-analyzer-core | Toivo | high | notify (mandate clearance right) | 13 |
| docs | Rene | low | silent (mandate clearance right) | 1 |
| tests | Toivo | low | silent (mandate clearance right) | 223 |

<a id="not-checked"></a>
#### What was not checked, and why

- `tests.execution` (facts.json not_run): SDK 8.0.402 ships Roslyn 4.11 but MessagePack.SourceGenerator references Microsoft.CodeAnalysis 4.12.0, so csc refuses to load the generator (warning CS9057) and projects that consume it as an analyzer (tests/MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) fail to compile (CS0117 'GeneratedMessagePackResolver' does not contain 'Instance'). This also happens on base 32258fdb, so it is an environment/toolchain mismatch, not caused by the change. Needs an SDK with Roslyn >= 4.12 (e.g. .NET SDK 9.0.1xx); swapping in a newer compiler toolset was not permitted in this run.
- `tests.MessagePack.Tests` (facts.json not_run): runtime library src/MessagePack not modified by the change; suite not run
- `build.net472/netstandard` (facts.json not_run): only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks` (facts.json not_run): no runtime serialization hot path touched (generator/analyzer only)
- `other-targets` (mandate known gap): Tests run on net8.0 only; .NET Framework, Unity and NativeAOT targets are not exercised
- `runtime-perf` (mandate known gap): No benchmarks unless a perf-sensitive path is touched; allocation and throughput regressions can slip through
- `semantic-intent` (mandate known gap): Correctness beyond what tests and cited evidence show is not established by the AI
- `provenance` (mandate known gap): Licensing and provenance of agent-written code are not checked

#### Residual risk (every item)

- REQ-2297-F1 not proven: not_met; reviewers_disagree
- Reviewer refusal (claude): Whether all 228 regenerated test resource files differ from base only by the coverage attribute and the brace/newline fix (out of scope: notify)
- Reviewer refusal (claude): Effect on generated code in consumers built with older compilers or with ImplicitUsings/nullable settings (out of scope: notify)
- Reviewer refusal (claude): The TransformUtilities brace change ('{' to '{\r\n' when constraints exist): intended fix or incidental (out of scope: notify)
- Reviewer refusal (codex): Coverage of generated code not exercised by the supplied generator test fixture (out of scope: notify)
- Reviewer refusal (nemotron): netstandard2.0 and .NET Framework compilation of generated output (out of scope: notify)
- Reviewer refusal (nemotron): runtime execution of generated formatters/resolvers (execution tests)
- Open major finding claude:C1: Coverage attribute is suppressed for netstandard2.0 and .NET Framework consumers based on a false premise
- Open major finding claude:v1.C2: Attribute on the generated half of user-declared partial resolvers can break builds (CS0579) and silently hides user code (carried forward from claude.v1.json)
- tests.execution not run (SDK 8.0.402 ships Roslyn 4.11 but MessagePack.SourceGenerator references Microsoft.CodeAnalysis 4.12.0, so csc refuses to load the generator (warning CS9057) and projects that consume it as an analyzer (tests/MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) fail to compile (CS0117 'GeneratedMessagePackResolver' does not contain 'Instance'). This also happens on base 32258fdb, so it is an environment/toolchain mismatch, not caused by the change. Needs an SDK with Roslyn >= 4.12 (e.g. .NET SDK 9.0.1xx); swapping in a newer compiler toolset was not permitted in this run.)
- tests.MessagePack.Tests not run (runtime library src/MessagePack not modified by the change; suite not run)
- build.net472/netstandard not run (only the net8.0 slice of src/MessagePack was built (Linux container, Debug))
- benchmarks not run (no runtime serialization hot path touched (generator/analyzer only))
- 3 disputed item(s) were not adjudicated (adjudicator gemini has not run)
- Standing gaps of this pipeline: other-targets, runtime-perf, semantic-intent, provenance (see not checked)

<a id="risk"></a>
#### Risk score: 83.0 -> ask

| Factor | Points | Reason |
|---|---:|---|
| area_sensitivity | 20 | most sensitive area touched: generator-analyzer-core (high) |
| files_changed | 45 | 237 files (~1.1 per file while small, log-scaled past 80, cap 45) |
| lines_changed | 0.0 | 162 non-generated lines (~4 per 100 lines while small, log-scaled past 100, cap 20; files and lines together at most 45) |
| generated_files | 10 | 228 generated files x 0.1 (cap 10) |
| public_api_change | 0 | public_api check: no change |
| source_without_tests | 0 | tests changed alongside source |
| security_sensitive_paths | 0 | none touched |
| fail_without_fix_not_shown | 0 | tests.fail_without_fix: pass |
| reviewer_disagreement | 8 | 1 clause(s) x 8: REQ-2297-F1 |
| failed_checks | 0 | 0 failed check(s) x 25 |
| **total** | **83.0** | bands: {'notify': 15, 'ask': 40, 'block': 130} |

Inputs: facts `evidence/2297/facts.json`, requirements `requirements/2297.yaml`, reviews `reviews/2297/claude.json`, `reviews/2297/codex.json`, `reviews/2297/nemotron.json`

</details>
