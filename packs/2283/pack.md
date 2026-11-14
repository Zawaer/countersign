## Countersign: change 2283 is **ASK**, owner **Toivo**

**Agent-written change for #2283: implementation for #2283**

Changes 1 source file (TypeCollector.cs), 1 test file, 2 doc files (+225 -3) on ju26-issue-2283 by Stelian Vultur. Judged against 5 requirement clauses from #2283 (placeholder requirement set, not Tieto's official one).

**Why ask**

1. Claude found a verified major issue: Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic ([evidence](#f-claude-C1))
2. 1 of 5 requirement clauses not proven. Claude says not met (Codex and Nemotron: met); Codex said met without verified evidence ([evidence](#chain-REQ-2283-N1))
3. The AI declined to decide 1 question, e.g. Whether the placeholder requirement set matches the upstream issue #2283 intent ([evidence](#refused))

<sub>All 12 tier drivers are under Full detail.</sub>

**Requirement trace**

| Status | Clause | Why |
|---|---|---|
| **PROVEN** | [REQ-2283-F1](#chain-REQ-2283-F1) | All 3 reviewers say met (13 verified citations); build, tests.targeted pass |
| **PROVEN** | [REQ-2283-F2](#chain-REQ-2283-F2) | All 3 reviewers say met (10 verified citations); build, tests.targeted pass |
| **PROVEN** | [REQ-2283-F3](#chain-REQ-2283-F3) | All 3 reviewers say met (10 verified citations); build, tests.targeted pass |
| **NOT MET** | [REQ-2283-N1](#chain-REQ-2283-N1) | Claude says not met (Codex and Nemotron: met); Codex said met without verified evidence |
| **PROVEN** | [REQ-2283-N2](#chain-REQ-2283-N2) | All 3 reviewers say met (8 verified citations); build, tests.fail_without_fix pass |

**What the AI found**

- **major** [Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic](#f-claude-C1) (Claude C1) [`TypeCollector.cs:1446 @head`](#ev-6afda546ae) [`TypeCollector.cs:1341 @head`](#ev-03c1f89f96)
- **minor** [BothStringAndIntKeyAreNull is now silently suppressed for positional record properties in source](#f-claude-C2) (Claude C2) [`TypeCollector.cs:1434 @head`](#ev-532df5c2da) [`TypeCollector.cs:985 @head`](#ev-ddf4848149)
- **info** [Fix treats the symptom location; metadata struct backing fields are still walked as members](#f-claude-C3) (Claude C3) [`TypeCollector.cs:1077 @head`](#ev-cf1d452cfa)

<a id="refused"></a>**What the AI refused to decide, and who should**

- <a id="refusal-5"></a>Whether the placeholder requirement set matches the upstream issue #2283 intent. *Why:* The requirement set is marked official: false and derived from the issue; the issue body itself was not provided, so I cannot verify the requirements capture the issue fully. *Who:* area owner or maintainer (raised by Nemotron)
- Whether [REQ-2283-N1](#chain-REQ-2283-N1) is met: see the trace. *Who:* Toivo

<details id="refused-peripheral"><summary>4 peripheral refusals (out of scope for this change)</summary><a id="refusal-1"></a>Whether the resolver generated for a project consuming a closed generic struct from a referenced assembly serializes it correctly at run time (and whether emitting a second formatter for Lib.Item`1 in the consuming assembly is intended) (Claude) · <a id="refusal-2"></a>Whether the documented behaviour change (diagnostics for referenced types are reported only by the defining project) is acceptable product behaviour (Claude) · <a id="refusal-3"></a>Execution-test behavior under a compiler that loads the generator (Codex) · <a id="refusal-4"></a>End-to-end execution of the generator in consumer projects (tests.execution: MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) (Nemotron)</details>

**Not checked, and why**

- `tests.execution`: SDK 8.0.402 ships Roslyn 4.11 but MessagePack.SourceGenerator references Microsoft.CodeAnalysis 4.12.0, so csc refuses to load the generator (warning CS9057) and projects that consume it as an analyzer (tests/MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) fail to compile (CS0117 'GeneratedMessagePackResolver' does not contain 'Instance'). This also happens on base 32258fdb, so it is an environment/toolchain mismatch, not caused by the change. Needs an SDK with Roslyn >= 4.12 (e.g. .NET SDK 9.0.1xx); swapping in a newer compiler toolset was not permitted in this run.
- `tests.MessagePack.Tests`: runtime library src/MessagePack not modified by the change; suite not run
- `build.net472/netstandard`: only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks`: no runtime serialization hot path touched (generator/analyzer only)
- Standing pipeline gaps: `other-targets`, `runtime-perf`, `semantic-intent`, `provenance`

**Residual risk you accept by signing**

- Open major finding: Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic
- Not proven by the AI: REQ-2283-N1. Signing means you judge them yourself.
- 1 question the AI declined to decide (listed above) are yours.

<details><summary>4 more risks that do not set the tier</summary>4 peripheral refusals (out of scope for this change) are yours too. · Not run: tests.execution, tests.MessagePack.Tests, build.net472/netstandard, benchmarks · 2 disputed items not adjudicated · Standing pipeline gaps: other-targets, runtime-perf, semantic-intent, provenance</details>

**Toivo signs** (required; allowed: accept, reject, request-changes)

> I, Toivo, have read what was checked and by whom, what was not checked and why, and the residual risk listed in this pack, and I own this decision.

Rate each verified finding with its `--finding` flag: `accepted` (real), `rejected` (a false positive) or `unsure`, optionally `:reason`. A finding without a flag is recorded as `unrated`.

- `claude:C1` (major): Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic
- `claude:C2` (minor): BothStringAndIntKeyAreNull is now silently suppressed for positional record properties in source
- `claude:C3` (info): Fix treats the symptom location; metadata struct backing fields are still walked as members

```
countersign sign 2283 --as Toivo --decision <accept|reject|request-changes> --note "..." \
  --finding claude:C1=<accepted|rejected|unsure> \
  --finding claude:C2=<accepted|rejected|unsure> \
  --finding claude:C3=<accepted|rejected|unsure>
```

<a id="supply-chain"></a>**Supply chain (from the build):** deps.delta pass: no package added or moved, 0 new advisories (6 already on base); build egress not recorded (local run, not on CRACI)

<details><summary>Supply-chain detail</summary>

`deps.delta` **pass**: 238 packages on head (238 on base) across 30 projects; 0 added, 0 version changes, 0 removed; 0 new vulnerability hits (6 already on base)

- Already on base (6): Microsoft.NETCore.Jit 1.0.2 high GHSA-xcvr-qv8h-m7xw, NuGet.Packaging 6.8.0 critical GHSA-68w7-72jg-6qpp, NuGet.Packaging 6.8.0 low GHSA-g4vj-cjjj-v7hg, NuGet.Protocol 6.8.0 low GHSA-g4vj-cjjj-v7hg, System.Formats.Asn1 6.0.0 high GHSA-447r-wph3-92pm, System.Text.Encodings.Web 4.5.0 critical GHSA-ghhp-997w-qr28
- SBOMs (CycloneDX): `evidence/base/sbom.cdx.json`, `evidence/2283/sbom.cdx.json`

</details>

<details><summary><b>Where the trust comes from</b> (per requirement clause)</summary>

<a id="chain-REQ-2283-F1"></a>
#### REQ-2283-F1: **PROVEN**

> Building a project whose [MessagePackObject] type has a member of a closed generic value type defined in a referenced assembly must not crash the source generator (no CS8785) and must produce a generated resolver.

- **Checks passed:** `build` pass, `tests.targeted` pass
- **Fails without the fix:** [`ClosedGenericRecordStruct_FromMetadataReference`](#ev-751fd9609c), [`ClosedGenericStruct_FromMetadataReference`](#ev-f073740910), [`ClosedGenericStruct_FromMetadataReference_UnkeyedMember`](#ev-72235a3098)
- **Claude** says met (6/8 citations verified): [`TypeCollector.cs:1077 @base`](#ev-600c5196b9) [`TypeCollector.cs:1077 @head`](#ev-e2b1723b1a) [`TypeCollector.cs:651 @head`](#ev-8dd72e446f) [`GenericsFormatterTests.cs:658 @head`](#ev-e27f824d96) [`test ClosedGenericRecordStruct_FromMetadataReference passed`](#ev-751fd9609c) [`test ClosedGenericRecordStruct_FromMetadataReference failed`](#ev-bf91cd8726) [`check tests.fail_without_fix`](#ev-d78b746a74) [`REQ-2283-F1 text`](#ev-19107a84ed)
- **Codex** says met (2/3 citations verified): [`test ClosedGenericStruct_FromMetadataReference passed`](#ev-f073740910) [`check tests.fail_without_fix`](#ev-d78b746a74) [`TypeCollector.cs:1446 @head`](#ev-6afda546ae)
- **Nemotron** says met (5/5 citations verified): [`test ClosedGenericStruct_FromMetadataReference passed`](#ev-f073740910) [`test ClosedGenericRecordStruct_FromMetadataReference passed`](#ev-751fd9609c) [`test ClosedGenericStruct_FromMetadataReference_UnkeyedMember passed`](#ev-72235a3098) [`TypeCollector.cs:1077 @head`](#ev-463700b774) [`check tests.fail_without_fix pass`](#ev-62faeb2508)

<a id="chain-REQ-2283-F2"></a>
#### REQ-2283-F2: **PROVEN**

> The MsgPack00x analyzer must not throw (no AD0001) for the same input.

- **Checks passed:** `build` pass, `tests.targeted` pass
- **Fails without the fix:** [`ClosedGenericStruct_FromMetadataReference`](#ev-cb2de557cf), [`ClosedGenericRecordStruct_FromMetadataReference`](#ev-751fd9609c)
- **Claude** says met (4/5 citations verified): [`test ClosedGenericStruct_FromMetadataReference failed`](#ev-cb2de557cf) [`test ClosedGenericStruct_FromMetadataReference passed`](#ev-f073740910) [`TypeCollector.cs:985 @head`](#ev-46dc7a6309) [`TypeCollector.cs:985 @base`](#ev-73cd23393f) [`check tests.fail_without_fix`](#ev-d78b746a74)
- **Codex** says met (2/3 citations verified): [`test ClosedGenericRecordStruct_FromMetadataReference passed`](#ev-751fd9609c) [`check tests.fail_without_fix`](#ev-d78b746a74) [`TypeCollector.cs:239 @head`](#ev-ce1eecc974)
- **Nemotron** says met (4/4 citations verified): [`test ClosedGenericStruct_FromMetadataReference failed`](#ev-cb2de557cf) [`test ClosedGenericStruct_FromMetadataReference passed`](#ev-f073740910) [`TypeCollector.cs:239 @head`](#ev-ce1eecc974) [`check tests.fail_without_fix pass`](#ev-62faeb2508)

<a id="chain-REQ-2283-F3"></a>
#### REQ-2283-F3: **PROVEN**

> Diagnostics about members of a type declared in a referenced assembly must not be reported at locations outside the compilation being analyzed.

- **Checks passed:** `build` pass, `tests.targeted` pass
- **Fails without the fix:** [`ClosedGenericStruct_FromMetadataReference_UnkeyedMember`](#ev-72235a3098)
- **Claude** says met (4/4 citations verified): [`TypeCollector.cs:239 @head`](#ev-7876fdb7f1) [`TypeCollector.cs:1446 @head`](#ev-6afda546ae) [`test ClosedGenericStruct_FromMetadataReference_UnkeyedMember passed`](#ev-72235a3098) [`test ClosedGenericStruct_FromMetadataReference_UnkeyedMember failed`](#ev-9b34c726e9)
- **Codex** says met (2/3 citations verified): [`TypeCollector.cs:1446 @head`](#ev-6afda546ae) [`TypeCollector.cs:1434 @head`](#ev-a7d205a394) [`check tests.fail_without_fix`](#ev-d78b746a74)
- **Nemotron** says met (4/4 citations verified): [`TypeCollector.cs:1446 @head`](#ev-6afda546ae) [`TypeCollector.cs:1434 @head`](#ev-a7d205a394) [`test ClosedGenericStruct_FromMetadataReference_UnkeyedMember passed`](#ev-72235a3098) [`test ClosedGenericStruct_FromMetadataReference_UnkeyedMember failed`](#ev-9b34c726e9)

<a id="chain-REQ-2283-N1"></a>
#### REQ-2283-N1: **NOT MET**

> Existing analyzer diagnostics for types declared in the current compilation keep working unchanged (no regressions in the existing test suite).

- **Claude: not met** (2/5 verified). The existing suite passes (170/170, no new failures), so the parenthetical part holds, but the clause's main statement does not: the location filter also drops diagnostics about types declared in the current compilation when the reporting location is a metadata member. My probe (scratch worktree, SDK 8, not in facts.json): metadata generic class Lib.Item<T> with [Key(0)] T Content, used as Item<Foo> where App.Foo lacks [MessagePackObject]; base reports MsgPack003 'Type must be marked with MessagePackObjectAttribute: Item.Content', head reports nothing. Item<T> as a class did not crash on base (issue table: 'class Item<T> | ok'), so this is a regression in a configuration that worked before. The existing suite does not cover it.
- **Codex: met** (0/1 verified). The source-generator test suite passes in full after the change.
- **Nemotron: met** (1/1 verified). Full suite on head: 170 passed, 0 failed, with no failures that also fail on base and no new failures, so existing analyzer diagnostics for in-compilation types are unchanged.
- **Checks:** `build` pass, `tests.full_suite` pass
- **What would settle it:** A fix, or evidence that refutes Claude's objection; Codex citing evidence the engine can verify

<a id="chain-REQ-2283-N2"></a>
#### REQ-2283-N2: **PROVEN**

> The fix is covered by automated tests that fail without it.

- **Checks passed:** `build` pass, `tests.fail_without_fix` pass
- **Fails without the fix:** [`ClosedGenericStruct_FromMetadataReference_UnkeyedMember`](#ev-9b34c726e9), [`ClosedGenericRecordStruct_FromMetadataReference`](#ev-bf91cd8726), [`ClosedGenericStruct_FromMetadataReference`](#ev-cb2de557cf)
- **Claude** says met (3/4 citations verified): [`check tests.fail_without_fix`](#ev-d78b746a74) [`test ClosedGenericStruct_FromMetadataReference_UnkeyedMember failed`](#ev-9b34c726e9) [`test ClosedGenericRecordStruct_FromMetadataReference failed`](#ev-bf91cd8726) [`test ClosedGenericStruct_FromMetadataReference failed`](#ev-cb2de557cf)
- **Codex** says met (1/2 citations verified): [`check tests.fail_without_fix`](#ev-d78b746a74) [`test ClosedGenericStruct_FromMetadataReference_UnkeyedMember passed`](#ev-72235a3098)
- **Nemotron** says met (4/4 citations verified): [`check tests.fail_without_fix pass`](#ev-62faeb2508) [`test ClosedGenericRecordStruct_FromMetadataReference failed`](#ev-bf91cd8726) [`test ClosedGenericStruct_FromMetadataReference failed`](#ev-cb2de557cf) [`test ClosedGenericStruct_FromMetadataReference_UnkeyedMember failed`](#ev-9b34c726e9)

</details>

<details><summary><b>Reviewer panel</b> (who said what)</summary>
<a id="panel"></a>

> Codex and Nemotron said met to all 5 clauses; Claude raised a verified major finding they did not (claude:C1: Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic). Claude also did not say met on REQ-2283-N1, so that clause is refused. Unanimity is required: one verified objection is enough to send it to Toivo.
> REQ-2283-N1: Claude: not met; Codex, Nemotron: met. A split verdict is a refusal, not a vote.

| Clause | Claude | Codex | Nemotron | Result |
|---|---|---|---|---|
| REQ-2283-F1 | met | met | met | **proven** |
| REQ-2283-F2 | met | met | met | **proven** |
| REQ-2283-F3 | met | met | met | **proven** |
| REQ-2283-N1 | not met | met | met | **not met** |
| REQ-2283-N2 | met | met | met | **proven** |

- **Claude** (claude-opus-5-5, Anthropic): citations 32 verified / 2 rejected; findings 3 verified / 0 rejected; 2 refusals. Only Claude raised: [C1](#f-claude-C1) major Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic, [C2](#f-claude-C2) minor BothStringAndIntKeyAreNull is now silently suppressed for positional record properties in source, [C3](#f-claude-C3) info Fix treats the symptom location; metadata struct backing fields are still walked as members
- **Codex** (GPT-6, OpenAI): citations 12 verified / 0 rejected; findings 0 verified / 0 rejected; 1 refusals.
- **Nemotron** (nvidia/nemotron-3.5-super-vl-120b-a12b, NVIDIA): citations 18 verified / 0 rejected; findings 0 verified / 0 rejected; 2 refusals.

2 disputed item(s), not adjudicated: REQ-2283-N1, finding:claude:C1

</details>

<details><summary><b>Evidence</b> (findings, cited code, tests and checks)</summary>

<a id="f-claude-C1"></a>
#### Claude C1 [major, correctness]: Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic

ReportIfLocatedInCompilation drops every diagnostic whose location is not a source location in this compilation, including Location.None and metadata locations, which Roslyn does allow analyzers to report. TypeMustBeMessagePackObject (MsgPack003) is located at callerSymbol.Locations[0]; when the caller is a member of a referenced generic (Lib.Item<T>.Content) and T is an app type without [MessagePackObject] (Item<Foo>), the diagnostic is about App.Foo but is now discarded. My probe: base reports MsgPack003 (metadata location), head reports nothing, while the generator still emits App.R.g.cs and a formatter for Lib.Item`1, so the missing Foo formatter would only surface at run time. This configuration (a generic class from another assembly) did not crash on base, so it is a regression. The XML doc comment's justification ('which analyzers are not permitted to do') is only true for source locations in other compilations.

Evidence: [`TypeCollector.cs:1446 @head`](#ev-6afda546ae) [`TypeCollector.cs:1341 @head`](#ev-03c1f89f96) [`TypeCollector.cs:1442 @head`](#ev-5a604cf84d) [`check tests.full_suite`](#ev-df050a6665)

Tier effect: ask (reproduced by the pipeline (repro.claude.C1))

Suggested fix: Instead of dropping, relocate: when a diagnostic's location is not in this compilation, re-report it at the nearest in-compilation location (the member of the type being analyzed that led to the metadata type, i.e. the outermost callerSymbol), or keep dropping only diagnostics about the metadata type's own members (MsgPack004/005) and let MsgPack003 for in-compilation types through. Add a test with a metadata generic class and an unattributed app type argument.

<a id="f-claude-C2"></a>
#### Claude C2 [minor, correctness]: BothStringAndIntKeyAreNull is now silently suppressed for positional record properties in source

GetPropertyIdentifierLocation returns null when the property's syntax is a ParameterSyntax (positional record), so with the filter the diagnostic becomes Location.None and is dropped. My probe on '[MessagePackObject] public record Cmd([property: Key(null)] string Scope)': base threw AD0001 InvalidCastException (the old hard cast), head reports no key diagnostic at all. Better than a crash, but an in-source invalid contract is no longer reported; no test covers line 985.

Evidence: [`TypeCollector.cs:1434 @head`](#ev-532df5c2da) [`TypeCollector.cs:985 @head`](#ev-ddf4848149)

Tier effect: notify

Suggested fix: Fall back to ParameterSyntax.Identifier (as the MemberNeedsKey path at line 926 already does) and add a test for a positional record with Key(null).

<a id="f-claude-C3"></a>
#### Claude C3 [info, maintainability]: Fix treats the symptom location; metadata struct backing fields are still walked as members

The crash comes from Roslyn importing private (compiler-generated backing) fields of metadata structs, which GetObjectInfo then treats as unkeyed members. The change makes those diagnostics location-safe and filters them, but still builds diagnostics for compiler-generated fields; any future diagnostic path that dereferences syntax for fields of a metadata struct will crash the same way. Skipping members without source/with CompilerGeneratedAttribute for metadata types would remove the class of bug.

Evidence: [`TypeCollector.cs:1077 @head`](#ev-cf1d452cfa) [`issue 2283`](#ev-c6793f8043) (not verified)

Tier effect: silent

#### Cited evidence

<a id="ev-600c5196b9"></a>
**TypeCollector.cs:1077 @base** (verified; cited by claude on REQ-2283-F1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1077 at base 32258fdb

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 32258fdb
  1074 |                             {
  1075 |                                 Diagnostic diagnostic = derivedKeyAttribute is not null && suppressSourceGeneration is not true
  1076 |                                     ? Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AOTDerivedKeyAttribute, derivedKeyAttribute.GetSyntax(this.cancellationToken).GetLocation())
> 1077 |                                     : Diagnostic.Create(MsgPack00xMessagePackAnalyzer.MemberNeedsKey, item.DeclaringSyntaxReferences[0].GetSyntax().GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name);
  1078 |                                 if (nonPublicMembersAreSerialized || (item.DeclaredAccessibility & Accessibility.Public) == Accessibility.Public)
  1079 |                                 {
  1080 |                                     this.reportDiagnostic?.Invoke(diagnostic);
```

<a id="ev-e2b1723b1a"></a>
**TypeCollector.cs:1077 @head** (verified; cited by claude on REQ-2283-F1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1077 at head 9df83c38

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 9df83c38
  1074 |                             {
  1075 |                                 Diagnostic diagnostic = derivedKeyAttribute is not null && suppressSourceGeneration is not true
  1076 |                                     ? Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AOTDerivedKeyAttribute, derivedKeyAttribute.GetSyntax(this.cancellationToken).GetLocation())
> 1077 |                                     : Diagnostic.Create(MsgPack00xMessagePackAnalyzer.MemberNeedsKey, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name);
  1078 |                                 if (nonPublicMembersAreSerialized || (item.DeclaredAccessibility & Accessibility.Public) == Accessibility.Public)
  1079 |                                 {
  1080 |                                     this.reportDiagnostic?.Invoke(diagnostic);
```

<a id="ev-8dd72e446f"></a>
**TypeCollector.cs:651 @head** (verified; cited by claude on REQ-2283-F1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:651 at head 9df83c38

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 9df83c38
  648 |             // Collect substituted types for the properties and fields.
  649 |             // NOTE: It is used to register formatters from nested generic type.
  650 |             //       However, closed generic types such as `Foo<string>` are not registered as a formatter.
> 651 |             this.GetObjectInfo(type, callerSymbol);
  652 | 
  653 |             // Collect generic type definition, that is not collected when it is defined outside target project.
  654 |             this.CollectCore(type.OriginalDefinition, callerSymbol);
```

<a id="ev-e27f824d96"></a>
**GenericsFormatterTests.cs:658 @head** (verified; cited by claude on REQ-2283-F1): quote matches tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs:658 at head 9df83c38

```text
// tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs @ 9df83c38
  655 |             .GetRunResult();
  656 |         Assert.Empty(runResult.Diagnostics.Where(d => d.Severity >= DiagnosticSeverity.Warning));
  657 |         var hintNames = runResult.Results.SelectMany(r => r.GeneratedSources).Select(s => s.HintName).ToList();
> 658 |         Assert.Contains(expectedResolverHintName, hintNames);
  659 |     }
  660 | 
  661 |     private static async Task<MetadataReference> CompileToMetadataReferenceAsync(string assemblyName, string source, LanguageVersion languageVersion)
```

<a id="ev-751fd9609c"></a>
**test ClosedGenericRecordStruct_FromMetadataReference passed** (verified; cited by claude on REQ-2283-F1, nemotron on REQ-2283-F1, codex on REQ-2283-F2): facts.json tests.targeted: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-bf91cd8726"></a>
**test ClosedGenericRecordStruct_FromMetadataReference failed** (verified; cited by claude on REQ-2283-F1, claude on REQ-2283-N2, nemotron on REQ-2283-N2): facts.json tests.fail_without_fix: failed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-d78b746a74"></a>
**check tests.fail_without_fix** (verified; cited by claude on REQ-2283-F1, codex on REQ-2283-F1, claude on REQ-2283-F2, codex on REQ-2283-F2, codex on REQ-2283-F3, claude on REQ-2283-N2, codex on REQ-2283-N2): facts.json: tests.fail_without_fix pass: new tests fail on base source: 3/3 failed -> tests do cover the change

- `tests.fail_without_fix` **pass**: new tests fail on base source: 3/3 failed -> tests do cover the change (dotnet test (source reverted, tests kept) 8.0.402)
- log: `evidence/2283/logs/tests_fail_without_fix.1.log`

<a id="ev-19107a84ed"></a>
**REQ-2283-F1 text** (verified; cited by claude on REQ-2283-F1): REQ-2283-F1 text contains the quote

> Building a project whose [MessagePackObject] type has a member of a closed generic value type defined in a referenced assembly must not crash the source generator (no CS8785) and must produce a generated resolver.

<a id="ev-f073740910"></a>
**test ClosedGenericStruct_FromMetadataReference passed** (verified; cited by codex on REQ-2283-F1, nemotron on REQ-2283-F1, claude on REQ-2283-F2, nemotron on REQ-2283-F2): facts.json tests.targeted: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-6afda546ae"></a>
**TypeCollector.cs:1446 @head** (verified; cited by codex on REQ-2283-F1, claude on REQ-2283-F3, codex on REQ-2283-F3, nemotron on REQ-2283-F3, claude:C1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1446 at head 9df83c38

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 9df83c38
  1443 |     /// </remarks>
  1444 |     private void ReportIfLocatedInCompilation(Action<Diagnostic> report, Diagnostic diagnostic)
  1445 |     {
> 1446 |         if (diagnostic.Location.IsInSource && this.compilation.ContainsSyntaxTree(diagnostic.Location.SourceTree))
  1447 |         {
  1448 |             report(diagnostic);
  1449 |         }
```

<a id="ev-72235a3098"></a>
**test ClosedGenericStruct_FromMetadataReference_UnkeyedMember passed** (verified; cited by nemotron on REQ-2283-F1, claude on REQ-2283-F3, nemotron on REQ-2283-F3, codex on REQ-2283-N2): facts.json tests.targeted: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-463700b774"></a>
**TypeCollector.cs:1077 @head** (verified; cited by nemotron on REQ-2283-F1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1077 at head 9df83c38

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 9df83c38
  1074 |                             {
  1075 |                                 Diagnostic diagnostic = derivedKeyAttribute is not null && suppressSourceGeneration is not true
  1076 |                                     ? Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AOTDerivedKeyAttribute, derivedKeyAttribute.GetSyntax(this.cancellationToken).GetLocation())
> 1077 |                                     : Diagnostic.Create(MsgPack00xMessagePackAnalyzer.MemberNeedsKey, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name);
  1078 |                                 if (nonPublicMembersAreSerialized || (item.DeclaredAccessibility & Accessibility.Public) == Accessibility.Public)
  1079 |                                 {
  1080 |                                     this.reportDiagnostic?.Invoke(diagnostic);
```

<a id="ev-62faeb2508"></a>
**check tests.fail_without_fix pass** (verified; cited by nemotron on REQ-2283-F1, nemotron on REQ-2283-F2, nemotron on REQ-2283-N2): facts.json: tests.fail_without_fix pass: new tests fail on base source: 3/3 failed -> tests do cover the change

- `tests.fail_without_fix` **pass**: new tests fail on base source: 3/3 failed -> tests do cover the change (dotnet test (source reverted, tests kept) 8.0.402)
- log: `evidence/2283/logs/tests_fail_without_fix.1.log`

<a id="ev-cb2de557cf"></a>
**test ClosedGenericStruct_FromMetadataReference failed** (verified; cited by claude on REQ-2283-F2, nemotron on REQ-2283-F2, claude on REQ-2283-N2, nemotron on REQ-2283-N2): facts.json tests.fail_without_fix: failed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-46dc7a6309"></a>
**TypeCollector.cs:985 @head** (verified; cited by claude on REQ-2283-F2): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:985 at head 9df83c38

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 9df83c38
  982 |                     var stringKey = key is { Value: string stringKeyValue } ? stringKeyValue : default;
  983 |                     if (intKey == null && stringKey == null)
  984 |                     {
> 985 |                         this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.BothStringAndIntKeyAreNull, GetPropertyIdentifierLocation(item), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name));
  986 |                     }
  987 | 
  988 |                     // A property with an init accessor and an initializer has a default that will be discarded by the deserializer.
```

<a id="ev-73cd23393f"></a>
**TypeCollector.cs:985 @base** (verified; cited by claude on REQ-2283-F2): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:985 at base 32258fdb

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 32258fdb
  982 |                     var stringKey = key is { Value: string stringKeyValue } ? stringKeyValue : default;
  983 |                     if (intKey == null && stringKey == null)
  984 |                     {
> 985 |                         this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.BothStringAndIntKeyAreNull, ((PropertyDeclarationSyntax)item.DeclaringSyntaxReferences[0].GetSyntax()).Identifier.GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name));
  986 |                     }
  987 | 
  988 |                     // A property with an init accessor and an initializer has a default that will be discarded by the deserializer.
```

<a id="ev-ce1eecc974"></a>
**TypeCollector.cs:239 @head** (verified; cited by codex on REQ-2283-F2, nemotron on REQ-2283-F2): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:239 at head 9df83c38

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 9df83c38
  236 |     private TypeCollector(Compilation compilation, AnalyzerOptions options, ReferenceSymbols referenceSymbols, ITypeSymbol targetType, Action<Diagnostic>? reportAnalyzerDiagnostic, CancellationToken cancellationToken)
  237 |     {
  238 |         this.typeReferences = referenceSymbols;
> 239 |         this.reportDiagnostic = reportAnalyzerDiagnostic is null ? null : diagnostic => ReportIfLocatedInCompilation(reportAnalyzerDiagnostic, diagnostic);
  240 |         this.options = options;
  241 |         this.compilation = compilation;
  242 |         this.cancellationToken = cancellationToken;
```

<a id="ev-7876fdb7f1"></a>
**TypeCollector.cs:239 @head** (verified; cited by claude on REQ-2283-F3): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:239 at head 9df83c38

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 9df83c38
  236 |     private TypeCollector(Compilation compilation, AnalyzerOptions options, ReferenceSymbols referenceSymbols, ITypeSymbol targetType, Action<Diagnostic>? reportAnalyzerDiagnostic, CancellationToken cancellationToken)
  237 |     {
  238 |         this.typeReferences = referenceSymbols;
> 239 |         this.reportDiagnostic = reportAnalyzerDiagnostic is null ? null : diagnostic => ReportIfLocatedInCompilation(reportAnalyzerDiagnostic, diagnostic);
  240 |         this.options = options;
  241 |         this.compilation = compilation;
  242 |         this.cancellationToken = cancellationToken;
```

<a id="ev-9b34c726e9"></a>
**test ClosedGenericStruct_FromMetadataReference_UnkeyedMember failed** (verified; cited by claude on REQ-2283-F3, nemotron on REQ-2283-F3, claude on REQ-2283-N2, nemotron on REQ-2283-N2): facts.json tests.fail_without_fix: failed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-a7d205a394"></a>
**TypeCollector.cs:1434 @head** (verified; cited by codex on REQ-2283-F3, nemotron on REQ-2283-F3): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1434 at head 9df83c38

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 9df83c38
  1431 |     /// </summary>
  1432 |     /// <param name="property">The property symbol. It may be declared in metadata, in which case <see langword="null" /> is returned.</param>
  1433 |     /// <returns>The location of the identifier, or <see langword="null" /> if the property has no declaration in source.</returns>
> 1434 |     private static Location? GetPropertyIdentifierLocation(IPropertySymbol property) => (property.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax() as PropertyDeclarationSyntax)?.Identifier.GetLocation();
  1435 | 
  1436 |     /// <summary>
  1437 |     /// Reports a diagnostic only when its location belongs to the compilation being analyzed.
```

<a id="ev-d1a7e0fbac"></a>
**TypeCollector.cs:1341 @head** (verified; cited by claude on REQ-2283-N1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1341 at head 9df83c38

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 9df83c38
  1338 |         {
  1339 |             if (formattedType.IsDefinition)
  1340 |             {
> 1341 |                 Location location = callerSymbol is not null ? callerSymbol.Locations[0] : formattedType.Locations[0];
  1342 |                 var targetName = callerSymbol is not null ? callerSymbol.ContainingType.Name + "." + callerSymbol.Name : formattedType.Name;
  1343 | 
  1344 |                 ImmutableDictionary<string, string?> typeInfo = ImmutableDictionary.Create<string, string?>().Add("type", formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat));
```

<a id="ev-94826533c2"></a>
**TypeCollector.cs:1446 @head** (verified; cited by claude on REQ-2283-N1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1446 at head 9df83c38

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 9df83c38
  1443 |     /// </remarks>
  1444 |     private void ReportIfLocatedInCompilation(Action<Diagnostic> report, Diagnostic diagnostic)
  1445 |     {
> 1446 |         if (diagnostic.Location.IsInSource && this.compilation.ContainsSyntaxTree(diagnostic.Location.SourceTree))
  1447 |         {
  1448 |             report(diagnostic);
  1449 |         }
```

<a id="ev-df050a6665"></a>
**check tests.full_suite** (verified; cited by claude on REQ-2283-N1, codex on REQ-2283-N1, claude:C1): facts.json: tests.full_suite pass: tests/MessagePack.SourceGenerator.Tests: 170 tests, 170 passed, 0 failed (0 not failing on base, 0 also failing on base)

- `tests.full_suite` **pass**: tests/MessagePack.SourceGenerator.Tests: 170 tests, 170 passed, 0 failed (0 not failing on base, 0 also failing on base) (dotnet test 8.0.402)
- log: `evidence/2283/logs/tests_full_suite.log`

<a id="ev-6d378cb38b"></a>
**REQ-2283-N1 text** (verified; cited by claude on REQ-2283-N1): REQ-2283-N1 text contains the quote

> Existing analyzer diagnostics for types declared in the current compilation keep working unchanged (no regressions in the existing test suite).

<a id="ev-23c90ec85d"></a>
**issue 2283** (NOT verified; cited by claude on REQ-2283-N1): issue text cannot be verified offline (not counted as evidence)

<a id="ev-d448f979e6"></a>
**check tests.full_suite pass** (verified; cited by nemotron on REQ-2283-N1): facts.json: tests.full_suite pass: tests/MessagePack.SourceGenerator.Tests: 170 tests, 170 passed, 0 failed (0 not failing on base, 0 also failing on base)

- `tests.full_suite` **pass**: tests/MessagePack.SourceGenerator.Tests: 170 tests, 170 passed, 0 failed (0 not failing on base, 0 also failing on base) (dotnet test 8.0.402)
- log: `evidence/2283/logs/tests_full_suite.log`

<a id="ev-03c1f89f96"></a>
**TypeCollector.cs:1341 @head** (verified; cited by claude:C1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1341 at head 9df83c38

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 9df83c38
  1338 |         {
  1339 |             if (formattedType.IsDefinition)
  1340 |             {
> 1341 |                 Location location = callerSymbol is not null ? callerSymbol.Locations[0] : formattedType.Locations[0];
  1342 |                 var targetName = callerSymbol is not null ? callerSymbol.ContainingType.Name + "." + callerSymbol.Name : formattedType.Name;
  1343 | 
  1344 |                 ImmutableDictionary<string, string?> typeInfo = ImmutableDictionary.Create<string, string?>().Add("type", formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat));
```

<a id="ev-5a604cf84d"></a>
**TypeCollector.cs:1442 @head** (verified; cited by claude:C1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1442 at head 9df83c38

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 9df83c38
  1439 |     /// <remarks>
  1440 |     /// Types and members that come from metadata (or from another compilation) have no location in the compilation being analyzed.
  1441 |     /// Their problems are reported by the compilation that defines them, so they are dropped here rather than being reported
> 1442 |     /// against a location that does not exist, which analyzers are not permitted to do.
  1443 |     /// </remarks>
  1444 |     private void ReportIfLocatedInCompilation(Action<Diagnostic> report, Diagnostic diagnostic)
  1445 |     {
```

<a id="ev-532df5c2da"></a>
**TypeCollector.cs:1434 @head** (verified; cited by claude:C2): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1434 at head 9df83c38

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 9df83c38
  1431 |     /// </summary>
  1432 |     /// <param name="property">The property symbol. It may be declared in metadata, in which case <see langword="null" /> is returned.</param>
  1433 |     /// <returns>The location of the identifier, or <see langword="null" /> if the property has no declaration in source.</returns>
> 1434 |     private static Location? GetPropertyIdentifierLocation(IPropertySymbol property) => (property.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax() as PropertyDeclarationSyntax)?.Identifier.GetLocation();
  1435 | 
  1436 |     /// <summary>
  1437 |     /// Reports a diagnostic only when its location belongs to the compilation being analyzed.
```

<a id="ev-ddf4848149"></a>
**TypeCollector.cs:985 @head** (verified; cited by claude:C2): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:985 at head 9df83c38

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 9df83c38
  982 |                     var stringKey = key is { Value: string stringKeyValue } ? stringKeyValue : default;
  983 |                     if (intKey == null && stringKey == null)
  984 |                     {
> 985 |                         this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.BothStringAndIntKeyAreNull, GetPropertyIdentifierLocation(item), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name));
  986 |                     }
  987 | 
  988 |                     // A property with an init accessor and an initializer has a default that will be discarded by the deserializer.
```

<a id="ev-cf1d452cfa"></a>
**TypeCollector.cs:1077 @head** (verified; cited by claude:C3): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1077 at head 9df83c38

```text
// src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs @ 9df83c38
  1074 |                             {
  1075 |                                 Diagnostic diagnostic = derivedKeyAttribute is not null && suppressSourceGeneration is not true
  1076 |                                     ? Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AOTDerivedKeyAttribute, derivedKeyAttribute.GetSyntax(this.cancellationToken).GetLocation())
> 1077 |                                     : Diagnostic.Create(MsgPack00xMessagePackAnalyzer.MemberNeedsKey, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name);
  1078 |                                 if (nonPublicMembersAreSerialized || (item.DeclaredAccessibility & Accessibility.Public) == Accessibility.Public)
  1079 |                                 {
  1080 |                                     this.reportDiagnostic?.Invoke(diagnostic);
```

<a id="ev-c6793f8043"></a>
**issue 2283** (NOT verified; cited by claude:C3): issue text cannot be verified offline (not counted as evidence)

</details>

<details><summary><b>Full detail</b>: all tier drivers, risk score, every check, areas, not checked, residual risk</summary>

Branch `ju26-issue-2283` (32258fdb..9df83c38), 4 files, +225 -3. Author Stelian Vultur (agent-written: True). Commit: implementation for #2283

Mandate `messagepack-csharp` v4 sha256 `4b247d4ec39413dd`, signature: valid, Toivo

<a id="all-drivers"></a>
#### All tier drivers (tier = strictest)

- ask: verified finding `claude:C1`: major: Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic (reproduced by the pipeline (repro.claude.C1))
- ask: refused clause `REQ-2283-N1`: not_met: claude: The existing suite passes (170/170, no new failures), so the parenthetical part holds, but the clause's main statement does not: the location filter also drops diagnostics about types declared in the current compilation when the reporting location is a metadata member. My probe (scratch worktree, SDK 8, not in facts.json): metadata generic class Lib.Item<T> with [Key(0)] T Content, used as Item<Foo> where App.Foo lacks [MessagePackObject]; base reports MsgPack003 'Type must be marked with MessagePackObjectAttribute: Item.Content', head reports nothing. Item<T> as a class did not crash on base (issue table: 'class Item<T> | ok'), so this is a regression in a configuration that worked before. The existing suite does not cover it.; reviewers_disagree: claude says not_met, codex says met, nemotron says met; thin_evidence: codex says met with 0 verified evidence items about the change (of 1 cited; requirement quotes and unclaimed outcomes don't count)
- ask: reviewer refusal `nemotron`: Whether the placeholder requirement set matches the upstream issue #2283 intent (The requirement set is marked official: false and derived from the issue; the issue body itself was not provided, so I cannot verify the requirements capture the issue fully.)
- ask: risk score `risk`: score 41.1 (notify>=15, ask>=40, block>=130); largest: area_sensitivity 20 + lines_changed 9.1 + reviewer_disagreement 8
- notify: verified finding `claude:C2`: minor: BothStringAndIntKeyAreNull is now silently suppressed for positional record properties in source
- notify: reviewer refusal `claude`: Whether the resolver generated for a project consuming a closed generic struct from a referenced assembly serializes it correctly at run time (and whether emitting a second formatter for Lib.Item`1 in the consuming assembly is intended) (tests.execution was not run for this change (SDK 8.0.402 cannot load the Roslyn 4.12 generator); the new tests skip the generated-sources check and only assert the resolver's hint name exists. I saw the generator emit Formatters.App.R.Lib.ItemFormatter`1.g.cs in my probe but did not execute it.) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: reviewer refusal `claude`: Whether the documented behaviour change (diagnostics for referenced types are reported only by the defining project) is acceptable product behaviour (It is a policy choice for the maintainers, and it is incomplete when the defining project does not run the analyzer (e.g. a NuGet package built without it).) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: reviewer refusal `codex`: Execution-test behavior under a compiler that loads the generator (The supplied facts mark execution tests as not run under SDK 8 because its compiler cannot load this generator; no SDK 9 execution result is supplied for this change.) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: reviewer refusal `nemotron`: End-to-end execution of the generator in consumer projects (tests.execution: MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) (Not run: SDK 8.0.402 ships Roslyn 4.11 while MessagePack.SourceGenerator references Microsoft.CodeAnalysis 4.12.0, so csc refuses to load the generator (CS9057) and consumer projects fail to compile (CS0117). The mismatch also occurs on base, so it is pre-existing and not caused by the change. In-process generator/analyzer tests were used instead.) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: trust cap `generator-analyzer-core`: generator-analyzer-core: AI may clear at most to notify (mandate clearance right)
- silent: trust cap `docs`: docs: AI may clear at most to silent (mandate clearance right)
- silent: trust cap `tests`: tests: AI may clear at most to silent (mandate clearance right)

#### Who reviewed

Participating reviewers: claude, codex, nemotron. Adjudicator: gemini. Confidential: no. Rule: proven needs every participating reviewer to say met with verified evidence, and the clause's checks to pass.

| Reviewer | Model | Prompt | Verified findings | Rejected | Refusals |
|---|---|---|---|---|---|
| claude | claude-opus-5-5 (Anthropic) | review-v1 | 3 | 0 | 2 |
| codex | GPT-6 (OpenAI) | review-v1 | 0 | 0 | 1 |
| nemotron | nvidia/nemotron-3.5-super-vl-120b-a12b (NVIDIA) | review-v1 | 0 | 0 | 2 |

#### Every check

| Check | Status | Tool | Summary |
|---|---|---|---|
| build | pass | dotnet build 8.0.402 | 0 errors, 1 unique warnings |
| tests.targeted | pass | dotnet test 8.0.402 | 19 passed, 0 failed, 0 skipped (3 new tests in run) |
| tests.fail_without_fix | pass | dotnet test (source reverted, tests kept) 8.0.402 | new tests fail on base source: 3/3 failed -> tests do cover the change |
| tests.full_suite | pass | dotnet test 8.0.402 | tests/MessagePack.SourceGenerator.Tests: 170 tests, 170 passed, 0 failed (0 not failing on base, 0 also failing on base) |
| public_api | pass | git diff of PublicAPI.*.txt + scan of added public/protected declarations in src/  | no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or removed in src/ |
| analyzers | pass | dotnet build warnings (Roslyn analyzers, StyleCop, PublicApiAnalyzers) vs base  | no new warnings |
| repro.claude.C1 | pass | dotnet test (reviewer repro test copied into tests/MessagePack.SourceGenerator.Tests/CountersignRepro) 8.0.402 | reproduced by the pipeline: failed on head (claim: failed), passed on base (claim: passed) |
| injection_scan | pass | countersign.injection (deterministic pattern scan) injection-v1 | no text addressed to automated reviewers in the added lines, commit message or PR text |
| deps.delta | pass | dotnet restore (every *.csproj, NuGet Audit mode=all) -> CycloneDX 1.6, base vs head 8.0.402 | 238 packages on head (238 on base) across 30 projects; 0 added, 0 version changes, 0 removed; 0 new vulnerability hits (6 already on base) |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v4 (4b247d4ec394)

#### Requirement trace (engine codes)

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-2283-F1 | proven | claude: met (6/8), codex: met (2/3), nemotron: met (5/5) | build: pass, tests.targeted: pass | - |
| REQ-2283-F2 | proven | claude: met (4/5), codex: met (2/3), nemotron: met (4/4) | build: pass, tests.targeted: pass | - |
| REQ-2283-F3 | proven | claude: met (4/4), codex: met (2/3), nemotron: met (4/4) | build: pass, tests.targeted: pass | - |
| REQ-2283-N1 | refused | claude: not_met (2/5), codex: met (0/1), nemotron: met (1/1) | build: pass, tests.full_suite: pass | not_met, reviewers_disagree, thin_evidence |
| REQ-2283-N2 | proven | claude: met (3/4), codex: met (1/2), nemotron: met (4/4) | build: pass, tests.fail_without_fix: pass | - |

#### What the AI refused to decide (every reviewer refusal)

- **claude** refused: Whether the resolver generated for a project consuming a closed generic struct from a referenced assembly serializes it correctly at run time (and whether emitting a second formatter for Lib.Item`1 in the consuming assembly is intended). Why: tests.execution was not run for this change (SDK 8.0.402 cannot load the Roslyn 4.12 generator); the new tests skip the generated-sources check and only assert the resolver's hint name exists. I saw the generator emit Formatters.App.R.Lib.ItemFormatter`1.g.cs in my probe but did not execute it. Who should decide: source-generator area owner (run the execution tests under SDK 9 or a two-project repro)
- **claude** refused: Whether the documented behaviour change (diagnostics for referenced types are reported only by the defining project) is acceptable product behaviour. Why: It is a policy choice for the maintainers, and it is incomplete when the defining project does not run the analyzer (e.g. a NuGet package built without it). Who should decide: MessagePack-CSharp maintainers / analyzer area owner
- **codex** refused: Execution-test behavior under a compiler that loads the generator. Why: The supplied facts mark execution tests as not run under SDK 8 because its compiler cannot load this generator; no SDK 9 execution result is supplied for this change. Who should decide: area owner
- **nemotron** refused: End-to-end execution of the generator in consumer projects (tests.execution: MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests). Why: Not run: SDK 8.0.402 ships Roslyn 4.11 while MessagePack.SourceGenerator references Microsoft.CodeAnalysis 4.12.0, so csc refuses to load the generator (CS9057) and consumer projects fail to compile (CS0117). The mismatch also occurs on base, so it is pre-existing and not caused by the change. In-process generator/analyzer tests were used instead. Who should decide: area owner or maintainer, with an SDK that ships Roslyn >= 4.12 (e.g. .NET SDK 9.0.1xx)
- **nemotron** refused: Whether the placeholder requirement set matches the upstream issue #2283 intent. Why: The requirement set is marked official: false and derived from the issue; the issue body itself was not provided, so I cannot verify the requirements capture the issue fully. Who should decide: area owner or maintainer

<a id="areas"></a>
#### Areas

| Area | Owner | Sensitivity | AI cap | Files |
|---|---|---|---|---:|
| generator-analyzer-core | Toivo | high | notify (mandate clearance right) | 1 |
| docs | Rene | low | silent (mandate clearance right) | 2 |
| tests | Toivo | low | silent (mandate clearance right) | 1 |

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

- REQ-2283-N1 not proven: not_met; reviewers_disagree; thin_evidence
- Reviewer refusal (claude): Whether the resolver generated for a project consuming a closed generic struct from a referenced assembly serializes it correctly at run time (and whether emitting a second formatter for Lib.Item`1 in the consuming assembly is intended) (out of scope: notify)
- Reviewer refusal (claude): Whether the documented behaviour change (diagnostics for referenced types are reported only by the defining project) is acceptable product behaviour (out of scope: notify)
- Reviewer refusal (codex): Execution-test behavior under a compiler that loads the generator (out of scope: notify)
- Reviewer refusal (nemotron): End-to-end execution of the generator in consumer projects (tests.execution: MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) (out of scope: notify)
- Reviewer refusal (nemotron): Whether the placeholder requirement set matches the upstream issue #2283 intent
- Open major finding claude:C1: Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic (reproduced)
- tests.execution not run (SDK 8.0.402 ships Roslyn 4.11 but MessagePack.SourceGenerator references Microsoft.CodeAnalysis 4.12.0, so csc refuses to load the generator (warning CS9057) and projects that consume it as an analyzer (tests/MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) fail to compile (CS0117 'GeneratedMessagePackResolver' does not contain 'Instance'). This also happens on base 32258fdb, so it is an environment/toolchain mismatch, not caused by the change. Needs an SDK with Roslyn >= 4.12 (e.g. .NET SDK 9.0.1xx); swapping in a newer compiler toolset was not permitted in this run.)
- tests.MessagePack.Tests not run (runtime library src/MessagePack not modified by the change; suite not run)
- build.net472/netstandard not run (only the net8.0 slice of src/MessagePack was built (Linux container, Debug))
- benchmarks not run (no runtime serialization hot path touched (generator/analyzer only))
- 2 disputed item(s) were not adjudicated (adjudicator gemini has not run)
- Standing gaps of this pipeline: other-targets, runtime-perf, semantic-intent, provenance (see not checked)

<a id="risk"></a>
#### Risk score: 41.1 -> ask

| Factor | Points | Reason |
|---|---:|---|
| area_sensitivity | 20 | most sensitive area touched: generator-analyzer-core (high) |
| files_changed | 4 | 4 files x 1 (cap 20) |
| lines_changed | 9.1 | 228 non-generated lines x 4/100 (cap 20) |
| generated_files | 0.0 | 0 generated files x 0.1 (cap 10) |
| public_api_change | 0 | public_api check: no change |
| source_without_tests | 0 | tests changed alongside source |
| security_sensitive_paths | 0 | none touched |
| fail_without_fix_not_shown | 0 | tests.fail_without_fix: pass |
| reviewer_disagreement | 8 | 1 clause(s) x 8: REQ-2283-N1 |
| failed_checks | 0 | 0 failed check(s) x 25 |
| **total** | **41.1** | bands: {'notify': 15, 'ask': 40, 'block': 130} |

Inputs: facts `evidence/2283/facts.json`, requirements `requirements/2283.yaml`, reviews `reviews/2283/claude.json`, `reviews/2283/codex.json`, `reviews/2283/nemotron.json`

</details>
