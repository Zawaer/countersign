## Countersign: change up-1934 is **ASK**, owner **Toivo**

**Change for #1925: Change default Language version of generated code to C# 7.3**

Changes 6 test files (+26 -22) on upstream PR #1934 by Alan Liu. Judged against 3 requirement clauses from #1925 (placeholder requirement set, not Tieto's official one).

**Why ask**

1. The AI declined to decide 1 question, e.g. Build and test behavior on non-Linux environments or other target frameworks (net472, netstandard2.0 slices of src/MessagePack) ([evidence](#refused))

<sub>All 5 tier drivers are under Full detail.</sub>

**Requirement trace**

| Status | Clause | Why |
|---|---|---|
| **PROVEN** | [REQ-up-1934-F1](#chain-REQ-up-1934-F1) | All 3 reviewers say met (16 verified citations); build, tests.targeted pass |
| **PROVEN** | [REQ-up-1934-F2](#chain-REQ-up-1934-F2) | All 3 reviewers say met (20 verified citations); build, tests.targeted pass |
| **PROVEN** | [REQ-up-1934-N1](#chain-REQ-up-1934-N1) | All 3 reviewers say met (8 verified citations); build, tests.full_suite pass |

**What the AI found**

- **info** [Two generic-constraint tests pin C# 9 although their input uses C# 8 features](#f-claude-C1) (Claude C1) [`GenericsFormatterTests.cs:356 @head`](#ev-6e1d8dd72a) [`GenericsFormatterTests.cs:436 @head`](#ev-8f8ceb66a2)
- **info** [CSharpSourceGeneratorCodeFixVerifier default changed but the verifier is unused](#f-claude-C2) (Claude C2) [`CSharpSourceGeneratorCodeFixVerifier`2.cs:22 @head`](#ev-b661201914)
- **info** [Test name does not match its source](#f-nemotron-F1) (Nemotron F1) [`CustomStringKeyFormatterTests.cs:34 @head`](#ev-94fa3653d3) [`CustomStringKeyFormatterTests.cs:53 @head`](#ev-665e3e1cfc)

<a id="refused"></a>**What the AI refused to decide, and who should**

- <a id="refusal-3"></a>Build and test behavior on non-Linux environments or other target frameworks (net472, netstandard2.0 slices of src/MessagePack). *Why:* Only the net8.0 Debug configuration on Linux was built and tested; this test-only change modifies no src/ code, so those were not run (facts.json not_run). *Who:* CI or area owner (raised by Nemotron)

<details id="refused-peripheral"><summary>2 peripheral refusals (out of scope for this change)</summary><a id="refusal-1"></a>That C# 7.3 is the default language version of every netstandard2.0 consumer (e.g. Unity, older SDKs) (Claude) · <a id="refusal-2"></a>facts.json count mismatch in tests.detects_original_regression (summary says 61 newly failing and 63/123 failed with new tests; 61 tests are listed) (Claude)</details>

**Not checked, and why**

- `tests.MessagePack.Tests`: runtime library src/MessagePack not modified by the change; suite not run
- `tests.execution`: ExecutionTests/MapModeExecutionTests not run for this control (generator output is covered by the snapshot tests in the full suite)
- `build.net472/netstandard`: only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks`: no runtime serialization hot path touched
- `tests.fail_without_fix`: skipped: not run: test-only change: no file under src/ changed, so there is no source to revert (see tests.detects_original_regression for what the new test settings catch)
- Standing pipeline gaps: `other-targets`, `runtime-perf`, `semantic-intent`, `provenance`

**Residual risk you accept by signing**

- 1 question the AI declined to decide (listed above) are yours.

<details><summary>3 more risks that do not set the tier</summary>2 peripheral refusals (out of scope for this change) are yours too. · Not run: tests.MessagePack.Tests, tests.execution, build.net472/netstandard, benchmarks, tests.fail_without_fix · Standing pipeline gaps: other-targets, runtime-perf, semantic-intent, provenance</details>

**Toivo signs** (required; allowed: accept, reject, request-changes)

> I, Toivo, have read what was checked and by whom, what was not checked and why, and the residual risk listed in this pack, and I own this decision.

Rate each verified finding with its `--finding` flag: `accepted` (real), `rejected` (a false positive) or `unsure`, optionally `:reason`. A finding without a flag is recorded as `unrated`.

- `claude:C1` (info): Two generic-constraint tests pin C# 9 although their input uses C# 8 features
- `claude:C2` (info): CSharpSourceGeneratorCodeFixVerifier default changed but the verifier is unused
- `nemotron:F1` (info): Test name does not match its source

```
countersign sign up-1934 --as Toivo --decision <accept|reject|request-changes> --note "..." \
  --finding claude:C1=<accepted|rejected|unsure> \
  --finding claude:C2=<accepted|rejected|unsure> \
  --finding nemotron:F1=<accepted|rejected|unsure>
```

<a id="supply-chain"></a>**Supply chain (from the build):** deps.delta not run; build egress not recorded (local run, not on CRACI)

<details><summary><b>Where the trust comes from</b> (per requirement clause)</summary>

<a id="chain-REQ-up-1934-F1"></a>
#### REQ-up-1934-F1: **PROVEN**

> By default, the source generator tests must compile the test input and the generated code at C# 7.3, the language version a netstandard2.0 project uses by default (issue #1925), so generated code that needs a newer language version fails the tests.

- **Checks passed:** `build` pass, `tests.targeted` pass
- **Fails without the fix:** no cited test does
- **Claude** says met (6/7 citations verified): [`REQ-up-1934-F1 text`](#ev-71702142d9) [`CSharpSourceGeneratorVerifier`1+Test.cs:46 @head`](#ev-18f1c5974b) [`CSharpSourceGeneratorVerifier`1+Test.cs:48 @head`](#ev-cf1b2f86d3) [`CSharpSourceGeneratorVerifier`1+Test.cs:102 @head`](#ev-40da86a21d) [`CSharpSourceGeneratorVerifier`1+Test.cs:184 @head`](#ev-4c69e9ef68) [`check tests.detects_original_regression pass`](#ev-6b957d903e) [`test AdditionalAllowTypes failed`](#ev-ab60b0801e)
- **Codex** says met (3/3 citations verified): [`CSharpSourceGeneratorVerifier`1+Test.cs:48 @head`](#ev-cf1b2f86d3) [`CSharpSourceGeneratorVerifier`1+Test.cs:102 @head`](#ev-40da86a21d) [`check tests.detects_original_regression pass`](#ev-6b957d903e)
- **Nemotron** says met (7/7 citations verified): [`CSharpSourceGeneratorVerifier`1+Test.cs:46 @head`](#ev-18f1c5974b) [`CSharpSourceGeneratorCodeFixVerifier`2.cs:22 @head`](#ev-b661201914) [`CSharpSourceGeneratorVerifier`1+Test.cs:48 @head`](#ev-cf1b2f86d3) [`CSharpSourceGeneratorVerifier`1+Test.cs:102 @head`](#ev-40da86a21d) [`check tests.full_suite pass`](#ev-d448f979e6) [`check tests.detects_original_regression pass`](#ev-6b957d903e) [`test ArrayTypedProperty failed`](#ev-cfc8867214)

<a id="chain-REQ-up-1934-F2"></a>
#### REQ-up-1934-F2: **PROVEN**

> Tests whose input source needs a newer language feature (records, record structs) must set that language version explicitly, and only those.

- **Checks passed:** `build` pass, `tests.targeted` pass
- **Fails without the fix:** no cited test does
- **Claude** says met (6/7 citations verified): [`REQ-up-1934-F2 text`](#ev-ed9838ff31) [`CustomStringKeyFormatterTests.cs:30 @head`](#ev-1f6d571ea2) [`GenerationTests.cs:234 @head`](#ev-dc7a9f9b49) [`GenericsFormatterTests.cs:409 @head`](#ev-df98ec7f6f) [`PrivateMemberAccessTests.cs:10 @head`](#ev-35e3008e34) [`PrivateMemberAccessTests.cs:11 @head`](#ev-daff207533) [`check tests.full_suite pass`](#ev-d448f979e6)
- **Codex** says met (3/3 citations verified): [`CustomStringKeyFormatterTests.cs:30 @head`](#ev-1f6d571ea2) [`PrivateMemberAccessTests.cs:11 @head`](#ev-e222ed4080) [`PrivateMemberAccessTests.cs:13 @head`](#ev-8622efff68)
- **Nemotron** says met (11/11 citations verified): [`CustomStringKeyFormatterTests.cs:30 @head`](#ev-1f6d571ea2) [`CustomStringKeyFormatterTests.cs:60 @head`](#ev-723e7e3ba3) [`GenerationTests.cs:234 @head`](#ev-dc7a9f9b49) [`GenerationTests.cs:75 @head`](#ev-5d1894b000) [`GenericsFormatterTests.cs:356 @head`](#ev-6e1d8dd72a) [`GenericsFormatterTests.cs:409 @head`](#ev-df98ec7f6f) [`GenericsFormatterTests.cs:436 @head`](#ev-8f8ceb66a2) [`PrivateMemberAccessTests.cs:10 @head`](#ev-35e3008e34) [`PrivateMemberAccessTests.cs:11 @head`](#ev-daff207533) [`PrivateMemberAccessTests.cs:13 @head`](#ev-8622efff68) [`CSharpSourceGeneratorVerifier`1+Test.cs:46 @head`](#ev-18f1c5974b)

<a id="chain-REQ-up-1934-N1"></a>
#### REQ-up-1934-N1: **PROVEN**

> The change touches only test code, and no existing source generator test regresses.

- **Checks passed:** `build` pass, `tests.full_suite` pass
- **Fails without the fix:** no cited test does
- **Claude** says met (2/3 citations verified): [`REQ-up-1934-N1 text`](#ev-1dba18fed5) [`check tests.full_suite pass`](#ev-d448f979e6) [`check public_api pass`](#ev-1494dc6548)
- **Codex** says met (2/2 citations verified): [`check tests.full_suite pass`](#ev-d448f979e6) [`CSharpSourceGeneratorVerifier`1+Test.cs:48 @head`](#ev-cf1b2f86d3)
- **Nemotron** says met (4/4 citations verified): [`check tests.full_suite pass`](#ev-d448f979e6) [`check tests.targeted pass`](#ev-5ac6625579) [`check public_api pass`](#ev-1494dc6548) [`check analyzers pass`](#ev-6effd1ac04)

</details>

<details><summary><b>Reviewer panel</b> (who said what)</summary>
<a id="panel"></a>

| Clause | Claude | Codex | Nemotron | Result |
|---|---|---|---|---|
| REQ-up-1934-F1 | met | met | met | **proven** |
| REQ-up-1934-F2 | met | met | met | **proven** |
| REQ-up-1934-N1 | met | met | met | **proven** |

- **Claude** (claude-opus-5-5, Anthropic): citations 20 verified / 0 rejected; findings 2 verified / 0 rejected; 2 refusals. Only Claude raised: [C1](#f-claude-C1) info Two generic-constraint tests pin C# 9 although their input uses C# 8 features, [C2](#f-claude-C2) info CSharpSourceGeneratorCodeFixVerifier default changed but the verifier is unused
- **Codex** (GPT-6, OpenAI): citations 8 verified / 0 rejected; findings 0 verified / 0 rejected; 0 refusals.
- **Nemotron** (nvidia/nemotron-3.5-super-vl-120b-a12b, NVIDIA): citations 25 verified / 0 rejected; findings 1 verified / 0 rejected; 1 refusals. Only Nemotron raised: [F1](#f-nemotron-F1) info Test name does not match its source

</details>

<details><summary><b>Evidence</b> (findings, cited code, tests and checks)</summary>

<a id="f-claude-C1"></a>
#### Claude C1 [info, tests]: Two generic-constraint tests pin C# 9 although their input uses C# 8 features

Generics_Constraints_NullableReferenceType and Generics_Constraints_ReferenceType_Nullable use #nullable enable / nullable constraints (C# 8) but are pinned to C# 9, so C# 9-only syntax emitted by the generator for these constraint shapes would not be caught. I did not run them at C# 8, so whether 8 suffices is unverified.

Evidence: [`GenericsFormatterTests.cs:356 @head`](#ev-6e1d8dd72a) [`GenericsFormatterTests.cs:436 @head`](#ev-8f8ceb66a2)

Tier effect: silent

Suggested fix: Try LanguageVersion.CSharp8 for these two tests and keep the lowest version that compiles the input.

<a id="f-claude-C2"></a>
#### Claude C2 [info, scope]: CSharpSourceGeneratorCodeFixVerifier default changed but the verifier is unused

No test class aliases CSharpSourceGeneratorCodeFixVerifier (I checked every VerifyCS alias at head), so this one-line change has no effect today; harmless and consistent, but it is not exercised by the suite.

Evidence: [`CSharpSourceGeneratorCodeFixVerifier`2.cs:22 @head`](#ev-b661201914)

Tier effect: silent

<a id="f-nemotron-F1"></a>
#### Nemotron F1 [info, tests]: Test name does not match its source

CustomStringKeyFormatterTests.RecordWithWithInitOnlyProps is named for init-only properties (a C# 9 feature) but its source uses { get; set; } auto-properties and calls RunDefaultAsync without a language version, so it runs at the default C# 7.3 and does not exercise init-only properties.

Evidence: [`CustomStringKeyFormatterTests.cs:34 @head`](#ev-94fa3653d3) [`CustomStringKeyFormatterTests.cs:53 @head`](#ev-665e3e1cfc) [`CustomStringKeyFormatterTests.cs:60 @head`](#ev-723e7e3ba3)

Tier effect: silent

Suggested fix: Rename the test, or change the properties to `init` accessors and pass languageVersion: LanguageVersion.CSharp9 so the test actually covers the feature its name promises.

#### Cited evidence

<a id="ev-71702142d9"></a>
**REQ-up-1934-F1 text** (verified; cited by claude on REQ-up-1934-F1): REQ-up-1934-F1 text contains the quote

> By default, the source generator tests must compile the test input and the generated code at C# 7.3, the language version a netstandard2.0 project uses by default (issue #1925), so generated code that needs a newer language version fails the tests.

<a id="ev-18f1c5974b"></a>
**CSharpSourceGeneratorVerifier`1+Test.cs:46 @head** (verified; cited by claude on REQ-up-1934-F1, nemotron on REQ-up-1934-F1, nemotron on REQ-up-1934-F2): quote matches tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorVerifier`1+Test.cs:46 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorVerifier`1+Test.cs @ 2f9324f9
  43 | #endif
  44 |         }
  45 | 
> 46 |         public LanguageVersion LanguageVersion { get; set; } = LanguageVersion.CSharp7_3;
  47 | 
  48 |         public static Task RunDefaultAsync(ITestOutputHelper logger, string testSource, AnalyzerOptions? options = null, LanguageVersion languageVersion = LanguageVersion.CSharp7_3, [CallerFilePath] string? testFile = null, [CallerMemberName] string testMethod = null!)
  49 |         {
```

<a id="ev-cf1b2f86d3"></a>
**CSharpSourceGeneratorVerifier`1+Test.cs:48 @head** (verified; cited by claude on REQ-up-1934-F1, codex on REQ-up-1934-F1, nemotron on REQ-up-1934-F1, codex on REQ-up-1934-N1): quote matches tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorVerifier`1+Test.cs:48 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorVerifier`1+Test.cs @ 2f9324f9
  45 | 
  46 |         public LanguageVersion LanguageVersion { get; set; } = LanguageVersion.CSharp7_3;
  47 | 
> 48 |         public static Task RunDefaultAsync(ITestOutputHelper logger, string testSource, AnalyzerOptions? options = null, LanguageVersion languageVersion = LanguageVersion.CSharp7_3, [CallerFilePath] string? testFile = null, [CallerMemberName] string testMethod = null!)
  49 |         {
  50 |             options ??= new();
  51 | 
```

<a id="ev-40da86a21d"></a>
**CSharpSourceGeneratorVerifier`1+Test.cs:102 @head** (verified; cited by claude on REQ-up-1934-F1, codex on REQ-up-1934-F1, nemotron on REQ-up-1934-F1): quote matches tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorVerifier`1+Test.cs:102 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorVerifier`1+Test.cs @ 2f9324f9
   99 |                 {
  100 |                     Sources = { testSource, resolverPartialClassSource },
  101 |                 },
> 102 |                 LanguageVersion = languageVersion,
  103 |             };
  104 | 
  105 |             return test.RunDefaultAsync(logger);
```

<a id="ev-4c69e9ef68"></a>
**CSharpSourceGeneratorVerifier`1+Test.cs:184 @head** (verified; cited by claude on REQ-up-1934-F1): quote matches tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorVerifier`1+Test.cs:184 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorVerifier`1+Test.cs @ 2f9324f9
  181 | 
  182 |         protected override ParseOptions CreateParseOptions()
  183 |         {
> 184 |             return ((CSharpParseOptions)base.CreateParseOptions()).WithLanguageVersion(this.LanguageVersion);
  185 |         }
  186 | 
  187 |         protected override async Task<(Compilation, ImmutableArray<Diagnostic>)> GetProjectCompilationAsync(Project project, IVerifier verifier, CancellationToken cancellationToken)
```

<a id="ev-6b957d903e"></a>
**check tests.detects_original_regression pass** (verified; cited by claude on REQ-up-1934-F1, codex on REQ-up-1934-F1, nemotron on REQ-up-1934-F1): facts.json: tests.detects_original_regression pass: with this PR's test changes, 61 tests fail on the pre-#1926 generator that pass with the old test files -> the new C# 7.3 default detects the #1925 regression (old tests: 0/123 failed; new tests: 63/123 failed; 0 fail either way)

- `tests.detects_original_regression` **pass**: with this PR's test changes, 61 tests fail on the pre-#1926 generator that pass with the old test files -> the new C# 7.3 default detects the #1925 regression (old tests: 0/123 failed; new tests: 63/123 failed; 0 fail either way) (dotnet test (full SourceGenerator.Tests) on source before the #1926 fix, old vs new test files 8.0.402)
- log: `evidence/up-1934/logs/detects_original_regression.newtests.log`
- log: `evidence/up-1934/logs/detects_original_regression.oldtests.log`

<a id="ev-ab60b0801e"></a>
**test AdditionalAllowTypes failed** (verified; cited by claude on REQ-up-1934-F1): facts.json tests.detects_original_regression: failed

- change head (`tests.targeted`): **passed**
- change head (`tests.detects_original_regression`): **failed**

<a id="ev-b661201914"></a>
**CSharpSourceGeneratorCodeFixVerifier`2.cs:22 @head** (verified; cited by nemotron on REQ-up-1934-F1, claude:C2): quote matches tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorCodeFixVerifier`2.cs:22 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorCodeFixVerifier`2.cs @ 2f9324f9
  19 |             this.CompilerDiagnostics = CompilerDiagnostics.Warnings;
  20 |         }
  21 | 
> 22 |         public LanguageVersion LanguageVersion { get; set; } = LanguageVersion.CSharp7_3;
  23 | 
  24 |         public ReferencesSet MessagePackReferences { get; set; } = ReferencesSet.MessagePack;
  25 | 
```

<a id="ev-d448f979e6"></a>
**check tests.full_suite pass** (verified; cited by nemotron on REQ-up-1934-F1, claude on REQ-up-1934-F2, claude on REQ-up-1934-N1, codex on REQ-up-1934-N1, nemotron on REQ-up-1934-N1): facts.json: tests.full_suite pass: tests/MessagePack.SourceGenerator.Tests: 123 tests, 123 passed, 0 failed (0 not failing on base, 0 also failing on base)

- `tests.full_suite` **pass**: tests/MessagePack.SourceGenerator.Tests: 123 tests, 123 passed, 0 failed (0 not failing on base, 0 also failing on base) (dotnet test 8.0.402)
- log: `evidence/up-1934/logs/tests_full_suite.log`

<a id="ev-cfc8867214"></a>
**test ArrayTypedProperty failed** (verified; cited by nemotron on REQ-up-1934-F1): facts.json tests.detects_original_regression: failed

- change head (`tests.targeted`): **passed**
- change head (`tests.detects_original_regression`): **failed**

<a id="ev-ed9838ff31"></a>
**REQ-up-1934-F2 text** (verified; cited by claude on REQ-up-1934-F2): REQ-up-1934-F2 text contains the quote

> Tests whose input source needs a newer language feature (records, record structs) must set that language version explicitly, and only those.

<a id="ev-1f6d571ea2"></a>
**CustomStringKeyFormatterTests.cs:30 @head** (verified; cited by claude on REQ-up-1934-F2, codex on REQ-up-1934-F2, nemotron on REQ-up-1934-F2): quote matches tests/MessagePack.SourceGenerator.Tests/CustomStringKeyFormatterTests.cs:30 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/CustomStringKeyFormatterTests.cs @ 2f9324f9
  27 |     public record MyMessagePackObject([property: Key("p")] string PhoneNumber, [property: Key("c")] int Count);
  28 | }
  29 | """;
> 30 |         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, languageVersion: LanguageVersion.CSharp9);
  31 |     }
  32 | 
  33 |     [Fact]
```

<a id="ev-dc7a9f9b49"></a>
**GenerationTests.cs:234 @head** (verified; cited by claude on REQ-up-1934-F2, nemotron on REQ-up-1934-F2): quote matches tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs:234 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs @ 2f9324f9
  231 |     }
  232 | }
  233 | """;
> 234 |         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, options: new() { Generator = new() { Formatters = new() { UsesMapMode = usesMapMode } } }, languageVersion: LanguageVersion.CSharp9, testMethod: $"{nameof(CustomFormatterViaAttributeOnProperty)}({usesMapMode})");
  235 |     }
  236 | 
  237 |     [Theory, PairwiseData]
```

<a id="ev-df98ec7f6f"></a>
**GenericsFormatterTests.cs:409 @head** (verified; cited by claude on REQ-up-1934-F2, nemotron on REQ-up-1934-F2): quote matches tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs:409 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs @ 2f9324f9
  406 |     }
  407 | }
  408 | """;
> 409 |         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, languageVersion: LanguageVersion.CSharp8);
  410 |     }
  411 | 
  412 |     [Fact]
```

<a id="ev-35e3008e34"></a>
**PrivateMemberAccessTests.cs:10 @head** (verified; cited by claude on REQ-up-1934-F2, nemotron on REQ-up-1934-F2): quote matches tests/MessagePack.SourceGenerator.Tests/PrivateMemberAccessTests.cs:10 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/PrivateMemberAccessTests.cs @ 2f9324f9
   7 | public class PrivateMemberAccessTests(ITestOutputHelper logger)
   8 | {
   9 |     [Theory]
> 10 |     [InlineData("class", LanguageVersion.CSharp7_3)]
  11 |     [InlineData("record", LanguageVersion.CSharp9)]
  12 |     [InlineData("struct", LanguageVersion.CSharp7_3)]
  13 |     [InlineData("record struct", LanguageVersion.CSharp10)]
```

<a id="ev-daff207533"></a>
**PrivateMemberAccessTests.cs:11 @head** (verified; cited by claude on REQ-up-1934-F2, nemotron on REQ-up-1934-F2): quote matches tests/MessagePack.SourceGenerator.Tests/PrivateMemberAccessTests.cs:11 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/PrivateMemberAccessTests.cs @ 2f9324f9
   8 | {
   9 |     [Theory]
  10 |     [InlineData("class", LanguageVersion.CSharp7_3)]
> 11 |     [InlineData("record", LanguageVersion.CSharp9)]
  12 |     [InlineData("struct", LanguageVersion.CSharp7_3)]
  13 |     [InlineData("record struct", LanguageVersion.CSharp10)]
  14 |     public async Task FormatterForClassWithPrivateMembers(string type, LanguageVersion version)
```

<a id="ev-e222ed4080"></a>
**PrivateMemberAccessTests.cs:11 @head** (verified; cited by codex on REQ-up-1934-F2): quote matches tests/MessagePack.SourceGenerator.Tests/PrivateMemberAccessTests.cs:11 at head 2f9324f9 (found at line 10, 1 off)

```text
// tests/MessagePack.SourceGenerator.Tests/PrivateMemberAccessTests.cs @ 2f9324f9
   7 | public class PrivateMemberAccessTests(ITestOutputHelper logger)
   8 | {
   9 |     [Theory]
> 10 |     [InlineData("class", LanguageVersion.CSharp7_3)]
  11 |     [InlineData("record", LanguageVersion.CSharp9)]
  12 |     [InlineData("struct", LanguageVersion.CSharp7_3)]
  13 |     [InlineData("record struct", LanguageVersion.CSharp10)]
```

<a id="ev-8622efff68"></a>
**PrivateMemberAccessTests.cs:13 @head** (verified; cited by codex on REQ-up-1934-F2, nemotron on REQ-up-1934-F2): quote matches tests/MessagePack.SourceGenerator.Tests/PrivateMemberAccessTests.cs:13 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/PrivateMemberAccessTests.cs @ 2f9324f9
  10 |     [InlineData("class", LanguageVersion.CSharp7_3)]
  11 |     [InlineData("record", LanguageVersion.CSharp9)]
  12 |     [InlineData("struct", LanguageVersion.CSharp7_3)]
> 13 |     [InlineData("record struct", LanguageVersion.CSharp10)]
  14 |     public async Task FormatterForClassWithPrivateMembers(string type, LanguageVersion version)
  15 |     {
  16 |         string testSource = $$"""
```

<a id="ev-723e7e3ba3"></a>
**CustomStringKeyFormatterTests.cs:60 @head** (verified; cited by nemotron on REQ-up-1934-F2, nemotron:F1): quote matches tests/MessagePack.SourceGenerator.Tests/CustomStringKeyFormatterTests.cs:60 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/CustomStringKeyFormatterTests.cs @ 2f9324f9
  57 |     };
  58 | }
  59 | """;
> 60 |         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  61 |     }
  62 | }
```

<a id="ev-5d1894b000"></a>
**GenerationTests.cs:75 @head** (verified; cited by nemotron on REQ-up-1934-F2): quote matches tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs:75 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs @ 2f9324f9
  72 | }
  73 | """;
  74 | 
> 75 |         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  76 |     }
  77 | 
  78 |     [Fact]
```

<a id="ev-6e1d8dd72a"></a>
**GenericsFormatterTests.cs:356 @head** (verified; cited by nemotron on REQ-up-1934-F2, claude:C1): quote matches tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs:356 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs @ 2f9324f9
  353 |     public interface IMyInterface {}
  354 | }
  355 | """;
> 356 |         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, languageVersion: LanguageVersion.CSharp9);
  357 |     }
  358 | 
  359 |     [Fact]
```

<a id="ev-8f8ceb66a2"></a>
**GenericsFormatterTests.cs:436 @head** (verified; cited by nemotron on REQ-up-1934-F2, claude:C1): quote matches tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs:436 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs @ 2f9324f9
  433 |     }
  434 | }
  435 | """;
> 436 |         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, languageVersion: LanguageVersion.CSharp9);
  437 |     }
  438 | 
  439 |     [Fact]
```

<a id="ev-1dba18fed5"></a>
**REQ-up-1934-N1 text** (verified; cited by claude on REQ-up-1934-N1): REQ-up-1934-N1 text contains the quote

> The change touches only test code, and no existing source generator test regresses.

<a id="ev-1494dc6548"></a>
**check public_api pass** (verified; cited by claude on REQ-up-1934-N1, nemotron on REQ-up-1934-N1): facts.json: public_api pass: no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or removed in src/

- `public_api` **pass**: no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or removed in src/ (git diff of PublicAPI.*.txt + scan of added public/protected declarations in src/ )

<a id="ev-5ac6625579"></a>
**check tests.targeted pass** (verified; cited by nemotron on REQ-up-1934-N1): facts.json: tests.targeted pass: 59 passed, 0 failed, 0 skipped (0 new tests in run)

- `tests.targeted` **pass**: 59 passed, 0 failed, 0 skipped (0 new tests in run) (dotnet test 8.0.402)
- log: `evidence/up-1934/logs/tests_targeted.1.log`

<a id="ev-6effd1ac04"></a>
**check analyzers pass** (verified; cited by nemotron on REQ-up-1934-N1): facts.json: analyzers pass: no new warnings

- `analyzers` **pass**: no new warnings (dotnet build warnings (Roslyn analyzers, StyleCop, PublicApiAnalyzers) vs base )

<a id="ev-94fa3653d3"></a>
**CustomStringKeyFormatterTests.cs:34 @head** (verified; cited by nemotron:F1): quote matches tests/MessagePack.SourceGenerator.Tests/CustomStringKeyFormatterTests.cs:34 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/CustomStringKeyFormatterTests.cs @ 2f9324f9
  31 |     }
  32 | 
  33 |     [Fact]
> 34 |     public async Task RecordWithWithInitOnlyProps()
  35 |     {
  36 |         string testSource = """
  37 | using System;
```

<a id="ev-665e3e1cfc"></a>
**CustomStringKeyFormatterTests.cs:53 @head** (verified; cited by nemotron:F1): quote matches tests/MessagePack.SourceGenerator.Tests/CustomStringKeyFormatterTests.cs:53 at head 2f9324f9

```text
// tests/MessagePack.SourceGenerator.Tests/CustomStringKeyFormatterTests.cs @ 2f9324f9
  50 |         }
  51 | 
  52 |         [Key("p")]
> 53 |         public string PhoneNumber { get; set; }
  54 | 
  55 |         [Key("c")]
  56 |         public int Count { get; set; }
```

</details>

<details><summary><b>Full detail</b>: all tier drivers, risk score, every check, areas, not checked, residual risk</summary>

Branch `upstream PR #1934` (7ef21d4b..2f9324f9), 6 files, +26 -22. Author Alan Liu (agent-written: False). Commit: Change default Language version of generated code to C# 7.3

Mandate `messagepack-csharp` v4 sha256 `4b247d4ec39413dd`, signature: valid, Toivo

<a id="all-drivers"></a>
#### All tier drivers (tier = strictest)

- ask: reviewer refusal `nemotron`: Build and test behavior on non-Linux environments or other target frameworks (net472, netstandard2.0 slices of src/MessagePack) (Only the net8.0 Debug configuration on Linux was built and tested; this test-only change modifies no src/ code, so those were not run (facts.json not_run).)
- notify: reviewer refusal `claude`: That C# 7.3 is the default language version of every netstandard2.0 consumer (e.g. Unity, older SDKs) (Taken from the requirement text; not checkable from the evidence) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: reviewer refusal `claude`: facts.json count mismatch in tests.detects_original_regression (summary says 61 newly failing and 63/123 failed with new tests; 61 tests are listed) (Likely renamed theory cases, but the logs were not given) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- silent: trust cap `tests`: tests: AI may clear at most to silent (mandate clearance right)
- silent: risk score `risk`: score 7.9 (notify>=15, ask>=40, block>=130); largest: files_changed 6 + lines_changed 1.9

#### Who reviewed

Participating reviewers: claude, codex, nemotron. Adjudicator: gemini. Confidential: no. Rule: proven needs every participating reviewer to say met with verified evidence, and the clause's checks to pass.

| Reviewer | Model | Prompt | Verified findings | Rejected | Refusals |
|---|---|---|---|---|---|
| claude | claude-opus-5-5 (Anthropic) | review-v1 | 2 | 0 | 2 |
| codex | GPT-6 (OpenAI) | review-v1 | 0 | 0 | 0 |
| nemotron | nvidia/nemotron-3.5-super-vl-120b-a12b (NVIDIA) | review-v1 | 1 | 0 | 1 |

#### Every check

| Check | Status | Tool | Summary |
|---|---|---|---|
| build | pass | dotnet build 8.0.402 | 0 errors, 1 unique warnings |
| tests.targeted | pass | dotnet test 8.0.402 | 59 passed, 0 failed, 0 skipped (0 new tests in run) |
| tests.fail_without_fix | skipped |   | not run: test-only change: no file under src/ changed, so there is no source to revert (see tests.detects_original_regression for what the new test settings catch) |
| tests.full_suite | pass | dotnet test 8.0.402 | tests/MessagePack.SourceGenerator.Tests: 123 tests, 123 passed, 0 failed (0 not failing on base, 0 also failing on base) |
| public_api | pass | git diff of PublicAPI.*.txt + scan of added public/protected declarations in src/  | no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or removed in src/ |
| analyzers | pass | dotnet build warnings (Roslyn analyzers, StyleCop, PublicApiAnalyzers) vs base  | no new warnings |
| tests.detects_original_regression | pass | dotnet test (full SourceGenerator.Tests) on source before the #1926 fix, old vs new test files 8.0.402 | with this PR's test changes, 61 tests fail on the pre-#1926 generator that pass with the old test files -> the new C# 7.3 default detects the #1925 regression (old tests: 0/123 failed; new tests: 63/123 failed; 0 fail either way) |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v4 (4b247d4ec394)

#### Requirement trace (engine codes)

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-up-1934-F1 | proven | claude: met (6/7), codex: met (3/3), nemotron: met (7/7) | build: pass, tests.targeted: pass | - |
| REQ-up-1934-F2 | proven | claude: met (6/7), codex: met (3/3), nemotron: met (11/11) | build: pass, tests.targeted: pass | - |
| REQ-up-1934-N1 | proven | claude: met (2/3), codex: met (2/2), nemotron: met (4/4) | build: pass, tests.full_suite: pass | - |

#### What the AI refused to decide (every reviewer refusal)

- **claude** refused: That C# 7.3 is the default language version of every netstandard2.0 consumer (e.g. Unity, older SDKs). Why: Taken from the requirement text; not checkable from the evidence Who should decide: area owner
- **claude** refused: facts.json count mismatch in tests.detects_original_regression (summary says 61 newly failing and 63/123 failed with new tests; 61 tests are listed). Why: Likely renamed theory cases, but the logs were not given Who should decide: countersign evidence maintainer
- **nemotron** refused: Build and test behavior on non-Linux environments or other target frameworks (net472, netstandard2.0 slices of src/MessagePack). Why: Only the net8.0 Debug configuration on Linux was built and tested; this test-only change modifies no src/ code, so those were not run (facts.json not_run). Who should decide: CI or area owner

<a id="areas"></a>
#### Areas

| Area | Owner | Sensitivity | AI cap | Files |
|---|---|---|---|---:|
| tests | Toivo | low | silent (mandate clearance right) | 6 |

<a id="not-checked"></a>
#### What was not checked, and why

- `tests.MessagePack.Tests` (facts.json not_run): runtime library src/MessagePack not modified by the change; suite not run
- `tests.execution` (facts.json not_run): ExecutionTests/MapModeExecutionTests not run for this control (generator output is covered by the snapshot tests in the full suite)
- `build.net472/netstandard` (facts.json not_run): only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks` (facts.json not_run): no runtime serialization hot path touched
- `tests.fail_without_fix` (check did not pass or fail): skipped: not run: test-only change: no file under src/ changed, so there is no source to revert (see tests.detects_original_regression for what the new test settings catch)
- `other-targets` (mandate known gap): Tests run on net8.0 only; .NET Framework, Unity and NativeAOT targets are not exercised
- `runtime-perf` (mandate known gap): No benchmarks unless a perf-sensitive path is touched; allocation and throughput regressions can slip through
- `semantic-intent` (mandate known gap): Correctness beyond what tests and cited evidence show is not established by the AI
- `provenance` (mandate known gap): Licensing and provenance of agent-written code are not checked

#### Residual risk (every item)

- Reviewer refusal (claude): That C# 7.3 is the default language version of every netstandard2.0 consumer (e.g. Unity, older SDKs) (out of scope: notify)
- Reviewer refusal (claude): facts.json count mismatch in tests.detects_original_regression (summary says 61 newly failing and 63/123 failed with new tests; 61 tests are listed) (out of scope: notify)
- Reviewer refusal (nemotron): Build and test behavior on non-Linux environments or other target frameworks (net472, netstandard2.0 slices of src/MessagePack)
- tests.MessagePack.Tests not run (runtime library src/MessagePack not modified by the change; suite not run)
- tests.execution not run (ExecutionTests/MapModeExecutionTests not run for this control (generator output is covered by the snapshot tests in the full suite))
- build.net472/netstandard not run (only the net8.0 slice of src/MessagePack was built (Linux container, Debug))
- benchmarks not run (no runtime serialization hot path touched)
- tests.fail_without_fix not run (skipped: not run: test-only change: no file under src/ changed, so there is no source to revert (see tests.detects_original_regression for what the new test settings catch))
- Standing gaps of this pipeline: other-targets, runtime-perf, semantic-intent, provenance (see not checked)

<a id="risk"></a>
#### Risk score: 7.9 -> silent

| Factor | Points | Reason |
|---|---:|---|
| area_sensitivity | 0 | most sensitive area touched: tests (low) |
| files_changed | 6 | 6 files x 1 (cap 20) |
| lines_changed | 1.9 | 48 non-generated lines x 4/100 (cap 20) |
| generated_files | 0.0 | 0 generated files x 0.1 (cap 10) |
| public_api_change | 0 | public_api check: no change |
| source_without_tests | 0 | no source changed |
| security_sensitive_paths | 0 | none touched |
| fail_without_fix_not_shown | 0 | tests.fail_without_fix: skipped (no source changed: nothing to revert) |
| reviewer_disagreement | 0 | 0 clause(s) x 8 |
| failed_checks | 0 | 0 failed check(s) x 25 |
| **total** | **7.9** | bands: {'notify': 15, 'ask': 40, 'block': 130} |

Inputs: facts `evidence/up-1934/facts.json`, requirements `requirements/up-1934.yaml`, reviews `reviews/up-1934/claude.json`, `reviews/up-1934/codex.json`, `reviews/up-1934/nemotron.json`

</details>
