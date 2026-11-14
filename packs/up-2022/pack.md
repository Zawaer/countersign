## Countersign: change up-2022 is **ASK**, owner **Toivo**

**Change for #2017: Ignore abstract implementations of `IMessagePackFormatter<T>` Fixes #2017**

Changes 1 source file (AnalyzerOptions.cs), 1 test file (+29 -0) on upstream PR #2022 by Andrew Arnott. Judged against 4 requirement clauses from #2017 (placeholder requirement set, not Tieto's official one).

**Why ask**

1. The AI declined to decide 1 question, e.g. Runtime deserialization security and execution behavior ([evidence](#refused))

<sub>All 7 tier drivers are under Full detail.</sub>

**Requirement trace**

| Status | Clause | Why |
|---|---|---|
| **PROVEN** | [REQ-up-2022-F1](#chain-REQ-up-2022-F1) | All 3 reviewers say met (8 verified citations); build, tests.targeted pass |
| **PROVEN** | [REQ-up-2022-F2](#chain-REQ-up-2022-F2) | All 3 reviewers say met (10 verified citations); build, tests.targeted pass |
| **PROVEN** | [REQ-up-2022-N1](#chain-REQ-up-2022-N1) | All 3 reviewers say met (6 verified citations); build, tests.fail_without_fix pass |
| **PROVEN** | [REQ-up-2022-N2](#chain-REQ-up-2022-N2) | All 3 reviewers say met (3 verified citations); build, tests.full_suite pass |

**What the AI found**

- **info** [New test covers the analyzer path only](#f-claude-C2) (Claude C2) [`MsgPack00xAnalyzerTests.cs:932 @head`](#ev-04a0a5893b)
- **info** [TryCreate documentation does not state that abstract types are excluded](#f-nemotron-I1) (Nemotron I1) [`AnalyzerOptions.cs:221 @head`](#ev-cd3ad6e495)

<a id="refused"></a>**What the AI refused to decide, and who should**

- <a id="refusal-3"></a>Runtime deserialization security and execution behavior. *Why:* The change only touches the source-generator analyzer and its tests; the runtime deserialization code in src/MessagePack is unmodified and tests.MessagePack.Tests was not run (listed in not_run), so no security claim about deserializing untrusted input is made here. *Who:* area owner / MessagePack maintainer (raised by Nemotron)

<details id="refused-peripheral"><summary>3 peripheral refusals (out of scope for this change)</summary><a id="refusal-1"></a>Exact behaviour (diagnostics and generated code) when an attribute names an abstract formatter type, before and after (Claude) · <a id="refusal-2"></a>Whether the release notes / analyzer docs should mention the change (Claude) · <a id="refusal-4"></a>Behavior on non-net8.0 target frameworks (Nemotron)</details>

**Not checked, and why**

- `tests.MessagePack.Tests`: runtime library src/MessagePack not modified by the change; suite not run
- `tests.execution`: ExecutionTests/MapModeExecutionTests not run for this control (generator output is covered by the snapshot tests in the full suite)
- `build.net472/netstandard`: only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks`: no runtime serialization hot path touched
- Standing pipeline gaps: `other-targets`, `runtime-perf`, `semantic-intent`, `provenance`

**Residual risk you accept by signing**

- 1 question the AI declined to decide (listed above) are yours.

<details><summary>3 more risks that do not set the tier</summary>3 peripheral refusals (out of scope for this change) are yours too. · Not run: tests.MessagePack.Tests, tests.execution, build.net472/netstandard, benchmarks · Standing pipeline gaps: other-targets, runtime-perf, semantic-intent, provenance</details>

**Toivo signs** (required; allowed: accept, reject, request-changes)

> I, Toivo, have read what was checked and by whom, what was not checked and why, and the residual risk listed in this pack, and I own this decision.

Rate each verified finding with its `--finding` flag: `accepted` (real), `rejected` (a false positive) or `unsure`, optionally `:reason`. A finding without a flag is recorded as `unrated`.

- `claude:C2` (info): New test covers the analyzer path only
- `nemotron:I1` (info): TryCreate documentation does not state that abstract types are excluded

```
countersign sign up-2022 --as Toivo --decision <accept|reject|request-changes> --note "..." \
  --finding claude:C2=<accepted|rejected|unsure> \
  --finding nemotron:I1=<accepted|rejected|unsure>
```

<a id="supply-chain"></a>**Supply chain (from the build):** deps.delta not run; build egress not recorded (local run, not on CRACI)

<details><summary><b>Where the trust comes from</b> (per requirement clause)</summary>

<a id="chain-REQ-up-2022-F1"></a>
#### REQ-up-2022-F1: **PROVEN**

> The analyzer must not report MsgPack013 (formatter has no accessible instance for the source generated resolver) for an abstract class that implements IMessagePackFormatter<T>.

- **Checks passed:** `build` pass, `tests.targeted` pass
- **Fails without the fix:** [`AbstractFormatterDoesNotAttractAttention`](#ev-ec490502a9)
- **Claude** says met (2/4 citations verified): [`REQ-up-2022-F1 text`](#ev-b1898df7f0) [`AnalyzerOptions.cs:221 @head`](#ev-cd3ad6e495) [`AnalyzerOptions.cs:247 @head`](#ev-bb2c0d462b) [`test AbstractFormatterDoesNotAttractAttention passed`](#ev-ec490502a9)
- **Codex** says met (2/2 citations verified): [`AnalyzerOptions.cs:221 @head`](#ev-cd3ad6e495) [`test AbstractFormatterDoesNotAttractAttention passed`](#ev-ec490502a9)
- **Nemotron** says met (4/5 citations verified): [`AnalyzerOptions.cs:221 @head`](#ev-cd3ad6e495) [`AnalyzerOptions.cs:223 @head`](#ev-4462e470a3) [`AnalyzerOptions.cs:224 @head`](#ev-0104897806) [`test AbstractFormatterDoesNotAttractAttention passed`](#ev-ec490502a9) [`REQ-up-2022-F1 text`](#ev-b1898df7f0)

<a id="chain-REQ-up-2022-F2"></a>
#### REQ-up-2022-F2: **PROVEN**

> Abstract implementations of IMessagePackFormatter<T> must not be counted as formatters, so they cannot cause MsgPack009 (more than one formatter for the same type).

- **Checks passed:** `build` pass, `tests.targeted` pass
- **Fails without the fix:** [`AbstractFormatterDoesNotAttractAttention`](#ev-9046fbade9)
- **Claude** says met (3/4 citations verified): [`REQ-up-2022-F2 text`](#ev-d6ac4eeb2e) [`AnalyzerOptions.cs:224 @head`](#ev-0104897806) [`test AbstractFormatterDoesNotAttractAttention failed`](#ev-9046fbade9) [`test AbstractFormatterDoesNotAttractAttention passed`](#ev-ec490502a9)
- **Codex** says met (3/3 citations verified): [`AnalyzerOptions.cs:223 @head`](#ev-4462e470a3) [`MsgPack00xAnalyzerTests.cs:913 @head`](#ev-197e014bda) [`test AbstractFormatterDoesNotAttractAttention failed`](#ev-9046fbade9)
- **Nemotron** says met (4/5 citations verified): [`AnalyzerOptions.cs:221 @head`](#ev-cd3ad6e495) [`test AbstractFormatterDoesNotAttractAttention failed`](#ev-9046fbade9) [`check tests.fail_without_fix pass`](#ev-62faeb2508) [`test AbstractFormatterDoesNotAttractAttention passed`](#ev-ec490502a9) [`REQ-up-2022-F2 text`](#ev-d6ac4eeb2e)

<a id="chain-REQ-up-2022-N1"></a>
#### REQ-up-2022-N1: **PROVEN**

> The fix is covered by automated tests that fail without it.

- **Checks passed:** `build` pass, `tests.fail_without_fix` pass
- **Fails without the fix:** [`AbstractFormatterDoesNotAttractAttention`](#ev-9046fbade9)
- **Claude** says met (2/2 citations verified): [`check tests.fail_without_fix pass`](#ev-62faeb2508) [`test AbstractFormatterDoesNotAttractAttention failed`](#ev-9046fbade9)
- **Codex** says met (2/2 citations verified): [`check tests.fail_without_fix pass`](#ev-62faeb2508) [`test AbstractFormatterDoesNotAttractAttention failed`](#ev-9046fbade9)
- **Nemotron** says met (2/3 citations verified): [`check tests.fail_without_fix pass`](#ev-62faeb2508) [`test AbstractFormatterDoesNotAttractAttention failed`](#ev-9046fbade9) [`REQ-up-2022-N1 text`](#ev-15d0adb4f3)

<a id="chain-REQ-up-2022-N2"></a>
#### REQ-up-2022-N2: **PROVEN**

> Non-abstract formatters are still discovered and diagnosed as before (no regressions in the existing test suite).

- **Checks passed:** `build` pass, `tests.full_suite` pass
- **Fails without the fix:** no cited test does
- **Passes without the fix too:** [`MessageFormatterAttribute`](#ev-5eb9a35a14)
- **Claude** says met (1/3 citations verified): [`check tests.full_suite pass`](#ev-d448f979e6) [`test MessageFormatterAttribute passed`](#ev-5eb9a35a14) [`AnalyzerOptions.cs:228 @head`](#ev-d27a42c472)
- **Codex** says met (1/1 citations verified): [`check tests.full_suite pass`](#ev-d448f979e6)
- **Nemotron** says met (1/2 citations verified): [`check tests.full_suite pass`](#ev-d448f979e6) [`REQ-up-2022-N2 text`](#ev-d3fe657f03)

</details>

<details><summary><b>Reviewer panel</b> (who said what)</summary>
<a id="panel"></a>

| Clause | Claude | Codex | Nemotron | Result |
|---|---|---|---|---|
| REQ-up-2022-F1 | met | met | met | **proven** |
| REQ-up-2022-F2 | met | met | met | **proven** |
| REQ-up-2022-N1 | met | met | met | **proven** |
| REQ-up-2022-N2 | met | met | met | **proven** |

- **Claude** (claude-opus-5-5, Anthropic): citations 14 verified / 3 rejected; findings 1 verified / 1 rejected; 2 refusals. Only Claude raised: [C1](#f-claude-C1) minor Abstract type named in [MessagePackFormatter]/[MessagePackKnownFormatter] is now silently ignored (rejected), [C2](#f-claude-C2) info New test covers the analyzer path only
- **Codex** (GPT-6, OpenAI): citations 8 verified / 0 rejected; findings 0 verified / 0 rejected; 0 refusals.
- **Nemotron** (nvidia/nemotron-3.5-super-vl-120b-a12b, NVIDIA): citations 16 verified / 1 rejected; findings 1 verified / 0 rejected; 2 refusals. Only Nemotron raised: [I1](#f-nemotron-I1) info TryCreate documentation does not state that abstract types are excluded

</details>

<details><summary><b>Evidence</b> (findings, cited code, tests and checks)</summary>

<a id="f-claude-C2"></a>
#### Claude C2 [info, tests]: New test covers the analyzer path only

The test runs VerifyAnalyzerAsync with no expected diagnostics; the generator's own scan (GeneratorUtilities) shares the same TryCreate, so it is covered by construction, but no generator snapshot test pins that abstract formatters stay out of the generated resolver.

Evidence: [`MsgPack00xAnalyzerTests.cs:932 @head`](#ev-04a0a5893b)

Tier effect: silent

<a id="f-nemotron-I1"></a>
#### Nemotron I1 [info, maintainability]: TryCreate documentation does not state that abstract types are excluded

The XML documentation for FormatterDescriptor.TryCreate (head line 218) describes the return value but does not mention that abstract types return false and are not treated as formatters, even though the new guard at head lines 221-225 does exactly that; the intent may be unclear to future maintainers.

Evidence: [`AnalyzerOptions.cs:218 @head`](#ev-302a6a0f66) (not verified) [`AnalyzerOptions.cs:221 @head`](#ev-cd3ad6e495)

Tier effect: silent

Suggested fix: Add a sentence to the &lt;returns&gt; documentation noting that abstract types return false and are not treated as formatters.

<a id="f-claude-C1"></a>
#### REJECTED: Claude C1 [minor, correctness]: Abstract type named in [MessagePackFormatter]/[MessagePackKnownFormatter] is now silently ignored

TryCreate is not only used for discovery: it also resolves the type in a member's [MessagePackFormatter(typeof(X))] (TypeCollector.GetSpecialFormatter) and in [MessagePackKnownFormatter(typeof(X))]. For an abstract X these now return 'not a formatter', and the else branch that should report it is commented out, so a user who points an attribute at an abstract formatter gets no diagnostic (on base the KnownFormatter path would have produced MsgPack013 for the missing instance) and the generator falls back to treating the member as if it had no custom formatter. Nothing in the diff tests these paths; I did not run them, so the exact downstream diagnostics/codegen are unverified.

Evidence: [`TypeCollector.cs:720 @head`](#ev-8af6858086) (not verified) [`TypeCollector.cs:725 @head`](#ev-699ea72a89) (not verified) [`AnalyzerUtilities.cs:95 @head`](#ev-c9c11752cc) (not verified)

Rejected: no cited evidence about the change could be verified: src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs is not in the change's diff; src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs is not in the change's diff; src/MessagePack.SourceGenerator/Utils/AnalyzerUtilities.cs is not in the change's diff

Suggested fix: Apply the abstract filter only in the discovery paths (compilation scan / SearchForFormatters), or report a diagnostic when an attribute names an abstract formatter type; add a test for [MessagePackFormatter(typeof(AbstractFormatter))].

#### Cited evidence

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

<details><summary><b>Full detail</b>: all tier drivers, risk score, every check, areas, not checked, residual risk</summary>

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
