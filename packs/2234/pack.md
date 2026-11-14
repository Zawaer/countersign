## Countersign: change 2234 is **ASK**, owner **Toivo**

**Agent-written change for #2234: The analyzer does not work if SuppressSourceGeneration = true**

Changes 1 source file (TypeCollector.cs), 2 test files, 1 doc file (+262 -4) on ju26-issue-2234 by Stelian Vultur. Judged against 4 requirement clauses from #2234 (placeholder requirement set, not Tieto's official one).

**Why ask**

1. Claude found a verified major issue: The issue's 3.1.1 regression is not on this base; the change fixes a different crash ([evidence](#f-claude-C1))
2. 2 of 4 requirement clauses not proven. REQ-2234-N1: Claude says not met (Codex and Nemotron: met) (+1 more) ([evidence](#chain-REQ-2234-N1))
3. The AI declined to decide 3 questions, e.g. Whether this change resolves issue #2234 for users of the released 3.1.x packages ([evidence](#refused))

<sub>All 18 tier drivers are under Full detail.</sub>

**Requirement trace**

| Status | Clause | Why |
|---|---|---|
| **HELD BEFORE** | [REQ-2234-F1](#chain-REQ-2234-F1) | Met, but already true before this change: all 3 of the clause's tests that were run without the fix pass there too: AllowPrivateRequiredIsReported, MemberTypeMustBeMessagePackObjectIsReported, MemberWithoutKeyIsReported |
| **HELD BEFORE** | [REQ-2234-F2](#chain-REQ-2234-F2) | Met, but already true before this change: all 1 of the clause's tests that were run without the fix pass there too: SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed |
| **NOT MET** | [REQ-2234-N1](#chain-REQ-2234-N1) | Claude says not met (Codex and Nemotron: met) |
| **REFUSED** | [REQ-2234-N2](#chain-REQ-2234-N2) | Codex said met without verified evidence |

**What the AI found**

- **major** [The issue's 3.1.1 regression is not on this base; the change fixes a different crash](#f-claude-C1) (Claude C1) [`TypeCollector.cs:1369 @base`](#ev-f51a2a7c26) [`test MemberWithoutKeyIsReported passed`](#ev-7f46834b36)
- **minor** [Positional-record Key(null) still crashes the analyzer for suppressed (and other) types](#f-claude-C2) (Claude C2) [`TypeCollector.cs:985 @head`](#ev-ea86c4a3d1)
- **minor** [Duplicate-key diagnostic reports only one diagnostic although two members share the key](#f-nemotron-N1) (Nemotron N1, also Claude) [`TypeCollector.cs:1014 @head`](#ev-16adc56b18) [`TypeCollector.cs:1016 @head`](#ev-9b063a4faf)
- +6 more under Evidence.

<a id="refused"></a>**What the AI refused to decide, and who should**

- <a id="refusal-1"></a>Whether this change resolves issue #2234 for users of the released 3.1.x packages. *Why:* The facts and tests were produced against base 32258fdb (develop line), which does not contain the 3.1.1 regression. Nothing was built or tested against master/v3.1.x, so whether the change applies there and fixes the reported symptom is not established (and C1 suggests it would not on its own). *Who:* analyzer area owner / maintainers choosing the target branch (raised by Claude)
- <a id="refusal-5"></a>Runtime library behavior (src/MessagePack) and net472/netstandard builds. *Why:* Not run; the runtime library was not modified and only net8.0 was built. *Who:* Area owner (raised by Nemotron)
- <a id="refusal-6"></a>Security review of analyzer deserializing untrusted input. *Why:* No security-specific evidence was provided and no security analysis was performed. *Who:* Security reviewer (raised by Nemotron)
- Whether [REQ-2234-N1](#chain-REQ-2234-N1), [REQ-2234-N2](#chain-REQ-2234-N2) are met: see the trace. *Who:* Toivo

<details id="refused-peripheral"><summary>3 peripheral refusals (out of scope for this change)</summary><a id="refusal-2"></a>Whether the README section's list of diagnostics still reported for suppressed types is complete and accurate (Claude) · <a id="refusal-3"></a>Parity with analyzer behavior in version 3.1.0 (Nemotron) · <a id="refusal-4"></a>Whether generation-only diagnostics (MsgPack011, MsgPack016, MsgPack017) are truly unreported on base for suppressed types (Nemotron)</details>

**Not checked, and why**

- `tests.MessagePack.Tests`: runtime library src/MessagePack not modified by the change; suite not run
- `build.net472/netstandard`: only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks`: no runtime serialization hot path touched (generator/analyzer only)
- Standing pipeline gaps: `other-targets`, `runtime-perf`, `semantic-intent`, `provenance`

**Residual risk you accept by signing**

- Open major finding: The issue's 3.1.1 regression is not on this base; the change fixes a different crash
- Not proven by the AI: REQ-2234-N1, REQ-2234-N2. Signing means you judge them yourself.
- 3 questions the AI declined to decide (listed above) are yours.

<details><summary>5 more risks that do not set the tier</summary>REQ-2234-F1, REQ-2234-F2 already held before this change: met, but not achieved by it. · 3 peripheral refusals (out of scope for this change) are yours too. · Not run: tests.MessagePack.Tests, build.net472/netstandard, benchmarks · 2 disputed items not adjudicated · Standing pipeline gaps: other-targets, runtime-perf, semantic-intent, provenance</details>

**Toivo signs** (required; allowed: accept, reject, request-changes)

> I, Toivo, have read what was checked and by whom, what was not checked and why, and the residual risk listed in this pack, and I own this decision.

Rate each verified finding with its `--finding` flag: `accepted` (real), `rejected` (a false positive) or `unsure`, optionally `:reason`. A finding without a flag is recorded as `unrated`.

- `claude:C1` (major): The issue's 3.1.1 regression is not on this base; the change fixes a different crash
- `claude:C2` (minor): Positional-record Key(null) still crashes the analyzer for suppressed (and other) types
- `claude:C3` (info): 'continue' on mixed key kinds skips recursive collection of that member's type
- `claude:C4` (info): Duplicate-key guard makes the generator emit a formatter that silently drops the second member
- `nemotron:N1` (minor): Duplicate-key diagnostic reports only one diagnostic although two members share the key
- `nemotron:N2` (minor): New test file triggers StyleCop SA1649 warning
- `nemotron:N3` (info): Runtime execution tests do not demonstrate the fix
- `nemotron:N4` (info): README documents behavior accurately
- `nemotron:N5` (info): Execution tests required SDK 9 override

```
countersign sign 2234 --as Toivo --decision <accept|reject|request-changes> --note "..." \
  --finding claude:C1=<accepted|rejected|unsure> \
  --finding claude:C2=<accepted|rejected|unsure> \
  --finding claude:C3=<accepted|rejected|unsure> \
  --finding claude:C4=<accepted|rejected|unsure> \
  --finding nemotron:N1=<accepted|rejected|unsure> \
  --finding nemotron:N2=<accepted|rejected|unsure> \
  --finding nemotron:N3=<accepted|rejected|unsure> \
  --finding nemotron:N4=<accepted|rejected|unsure> \
  --finding nemotron:N5=<accepted|rejected|unsure>
```

<a id="supply-chain"></a>**Supply chain (from the build):** deps.delta pass: no package added or moved, 0 new advisories (6 already on base); build.egress pass

<details><summary>Supply-chain detail</summary>

`deps.delta` **pass**: 238 packages on head (238 on base) across 30 projects; 0 added, 0 version changes, 0 removed; 0 new vulnerability hits (6 already on base)

- Already on base (6): Microsoft.NETCore.Jit 1.0.2 high GHSA-xcvr-qv8h-m7xw, NuGet.Packaging 6.8.0 critical GHSA-68w7-72jg-6qpp, NuGet.Packaging 6.8.0 low GHSA-g4vj-cjjj-v7hg, NuGet.Protocol 6.8.0 low GHSA-g4vj-cjjj-v7hg, System.Formats.Asn1 6.0.0 high GHSA-447r-wph3-92pm, System.Text.Encodings.Web 4.5.0 critical GHSA-ghhp-997w-qr28
- SBOMs (CycloneDX): `evidence/base/sbom.cdx.json`, `evidence/2234/sbom.cdx.json`
- `build.egress` **pass**: default deny, presets ['github'], 13 TLS host patterns; run https://github.com/Zawaer/countersign/actions/runs/43559084959; policy sha256 `31fafb855e98`

</details>

<details><summary><b>Where the trust comes from</b> (per requirement clause)</summary>

<a id="chain-REQ-2234-F1"></a>
#### REQ-2234-F1: **HELD BEFORE**

> The analyzer must report contract diagnostics (e.g. missing [Key], duplicate keys, mixed key kinds) for [MessagePackObject(SuppressSourceGeneration = true)] types, as it did in version 3.1.0.

- **Checks passed:** `build` pass, `tests.targeted` pass
- **Fails without the fix:** [`DuplicateIntKeysAreReportedWithoutAnalyzerFailure`](#ev-283a17c90c), [`MixedKeyKindsAreReportedWithoutAnalyzerFailure`](#ev-25ded34e20), [`DuplicateStringKeysAreReportedWithoutAnalyzerFailure`](#ev-bb565b0d63)
- **Passes without the fix too:** [`MemberWithoutKeyIsReported`](#ev-7f46834b36), [`MemberTypeMustBeMessagePackObjectIsReported`](#ev-ab5dfeec65), [`AllowPrivateRequiredIsReported`](#ev-0cdf78bf54)
- **Claude** says met (8/9 citations verified): [`test MemberWithoutKeyIsReported passed`](#ev-7f46834b36) [`test MemberTypeMustBeMessagePackObjectIsReported passed`](#ev-ab5dfeec65) [`test AllowPrivateRequiredIsReported passed`](#ev-0cdf78bf54) [`test DuplicateIntKeysAreReportedWithoutAnalyzerFailure failed`](#ev-283a17c90c) [`test DuplicateIntKeysAreReportedWithoutAnalyzerFailure passed`](#ev-8fd1a8fc46) [`test MixedKeyKindsAreReportedWithoutAnalyzerFailure passed`](#ev-25ded34e20) [`TypeCollector.cs:1023 @head`](#ev-bc6b3dd3fa) [`TypeCollector.cs:1008 @head`](#ev-a0957ebdbe) [`check tests.fail_without_fix`](#ev-d78b746a74)
- **Codex** says met (3/4 citations verified): [`test DuplicateIntKeysAreReportedWithoutAnalyzerFailure passed`](#ev-8fd1a8fc46) [`test MixedKeyKindsAreReportedWithoutAnalyzerFailure passed`](#ev-25ded34e20) [`check tests.fail_without_fix`](#ev-d78b746a74) [`TypeCollector.cs:1023 @head`](#ev-bc6b3dd3fa)
- **Nemotron** says met (12/13 citations verified): [`REQ-2234-F1 text`](#ev-dffe050cec) [`TypeCollector.cs:1008 @head`](#ev-eeb0b47f0a) [`TypeCollector.cs:1023 @head`](#ev-bc6b3dd3fa) [`TypeCollector.cs:1039 @head`](#ev-1d23e816db) [`test MemberWithoutKeyIsReported passed`](#ev-02bb823660) [`test AllowPrivateRequiredIsReported passed`](#ev-d0aaf0ddcf) [`test MemberTypeMustBeMessagePackObjectIsReported passed`](#ev-0fc5c1ea52) [`test DuplicateIntKeysAreReportedWithoutAnalyzerFailure passed`](#ev-8fd1a8fc46) [`test DuplicateStringKeysAreReportedWithoutAnalyzerFailure passed`](#ev-bb565b0d63) [`test MixedKeyKindsAreReportedWithoutAnalyzerFailure passed`](#ev-25ded34e20) [`check tests.fail_without_fix pass`](#ev-62faeb2508) [`test DuplicateIntKeysAreReportedWithoutAnalyzerFailure failed`](#ev-283a17c90c) [`test MixedKeyKindsAreReportedWithoutAnalyzerFailure failed`](#ev-99a149a316)

<a id="chain-REQ-2234-F2"></a>
#### REQ-2234-F2: **HELD BEFORE**

> Diagnostics that only apply when a formatter is generated (partial-class requirement, AOT-only checks) must not be reported for types with SuppressSourceGeneration = true.

- **Checks passed:** `build` pass, `tests.targeted` pass
- **Fails without the fix:** no cited test does
- **Passes without the fix too:** [`SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed`](#ev-165dc4a6ea)
- **Claude** says met (5/5 citations verified): [`test SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed passed`](#ev-165dc4a6ea) [`test SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed passed`](#ev-097f9caee8) [`TypeCollector.cs:1383 @head`](#ev-6768fd1ae3) [`TypeCollector.cs:1407 @head`](#ev-337b4ac064) [`TypeCollector.cs:989 @head`](#ev-e5721f8767)
- **Codex** says met (1/2 citations verified): [`test SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed passed`](#ev-097f9caee8) [`check tests.fail_without_fix`](#ev-d78b746a74)
- **Nemotron** says met (4/5 citations verified): [`REQ-2234-F2 text`](#ev-d3c4dd6a49) [`TypeCollector.cs:1383 @head`](#ev-6768fd1ae3) [`TypeCollector.cs:1386 @head`](#ev-76656896d1) [`test SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed passed`](#ev-097f9caee8) [`test SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed passed`](#ev-165dc4a6ea)

<a id="chain-REQ-2234-N1"></a>
#### REQ-2234-N1: **NOT MET**

> The analyzer and generator must not crash on invalid contracts (e.g. duplicate keys) in such types.

- **Claude: not met** (2/4 verified). The duplicate-key and mixed-kind crashes are fixed, and the full suite passes (175/175). But not every invalid contract in such a type is crash-free. The hard cast at line 985 is untouched, and my probe (scratch worktree, SDK 8, not in facts.json) of '[MessagePackObject(SuppressSourceGeneration = true)] public record Cmd([property: Key(null)] string Scope)' still gives AD0001 InvalidCastException (ParameterSyntax to PropertyDeclarationSyntax) at this head. The generator side of the duplicate-key fix has no test in facts.json (the new analyzer tests use CSharpCodeFixVerifier, analyzer only), though my probe showed no CS8785 for duplicate keys at head.
- **Codex: met** (1/2 verified). The full source-generator suite passes, and duplicate-key tests demonstrate that invalid contracts no longer trigger analyzer failure.
- **Nemotron: met** (4/5 verified). The full suite passes with 0 failures on head, and the previously crashing duplicate-key and mixed-key tests now pass instead of throwing analyzer exceptions.
- **Checks:** `build` pass, `tests.full_suite` pass
- **What would settle it:** A fix, or evidence that refutes Claude's objection

<a id="chain-REQ-2234-N2"></a>
#### REQ-2234-N2: **REFUSED**

> The fix is covered by automated tests that fail without it; no regressions in the existing test suite.

- **Claude: met** (3/7 verified). tests.fail_without_fix passes on the 4 analyzer tests that cover what the change does (duplicate int/string keys, mixed kinds, duplicate keys on a non-suppressed type): they fail on base with AD0001 and pass at head. The other 4 new analyzer tests and all 4 new execution test results pass on base too (tests.execution_fail_without_fix = fail), so they are regression guards, not proof of the fix. No regressions: tests.full_suite and tests.execution_full_suite pass.
- **Codex: met** (0/2 verified). Four of the eight new analyzer tests fail on base source and all eight pass with the change; the full suite passes.
- **Nemotron: met** (6/7 verified). 4 of 8 new analyzer tests fail on base source (analyzer exceptions AD0001), while all pass on head; the full suite shows no regressions. The two runtime execution tests do not demonstrate the change, but the analyzer tests alone satisfy the coverage requirement.
- **Checks:** `build` pass, `tests.fail_without_fix` pass
- **What would settle it:** Codex citing evidence the engine can verify

</details>

<details><summary><b>Reviewer panel</b> (who said what)</summary>
<a id="panel"></a>

> Codex and Nemotron said met to all 4 clauses; Claude raised a verified major finding they did not (claude:C1: The issue's 3.1.1 regression is not on this base; the change fixes a different crash). Claude also did not say met on REQ-2234-N1, so that clause is refused. Unanimity is required: one verified objection is enough to send it to Toivo.
> REQ-2234-N1: Claude: not met; Codex, Nemotron: met. A split verdict is a refusal, not a vote.

| Clause | Claude | Codex | Nemotron | Result |
|---|---|---|---|---|
| REQ-2234-F1 | met | met | met | **held before** |
| REQ-2234-F2 | met | met | met | **held before** |
| REQ-2234-N1 | not met | met | met | **not met** |
| REQ-2234-N2 | met | met | met | **refused** |

- **Claude** (claude-opus-5-5, Anthropic): citations 32 verified / 2 rejected; findings 4 verified / 0 rejected; 2 refusals. Only Claude raised: [C1](#f-claude-C1) major The issue's 3.1.1 regression is not on this base; the change fixes a different crash, [C2](#f-claude-C2) minor Positional-record Key(null) still crashes the analyzer for suppressed (and other) types
- **Codex** (GPT-6, OpenAI): citations 10 verified / 0 rejected; findings 0 verified / 0 rejected; 0 refusals.
- **Nemotron** (nvidia/nemotron-3.5-super-vl-120b-a12b, NVIDIA): citations 41 verified / 1 rejected; findings 5 verified / 0 rejected; 4 refusals. Only Nemotron raised: [N2](#f-nemotron-N2) minor New test file triggers StyleCop SA1649 warning, [N3](#f-nemotron-N3) info Runtime execution tests do not demonstrate the fix, [N4](#f-nemotron-N4) info README documents behavior accurately, [N5](#f-nemotron-N5) info Execution tests required SDK 9 override

2 disputed item(s), not adjudicated: REQ-2234-N1, finding:claude:C1

</details>

<details><summary><b>Evidence</b> (findings, cited code, tests and checks)</summary>

<a id="f-claude-C1"></a>
#### Claude C1 [major, correctness]: The issue's 3.1.1 regression is not on this base; the change fixes a different crash

Issue #2234 says the analyzer stopped working for SuppressSourceGeneration = true in 3.1.1. The cause in history is commit 1a74a620 ('stop collect field when object marked SuppressSourceGeneration', in v3.1.1 and still in v3.1.12): it moved the 'if (suppressSourceGeneration is true) return null;' to right after the attribute is read, before any member is analyzed. Base 32258fdb is on the develop line and does not contain v3.1.0/v3.1.1 or that commit. Its early return is at line 1369, after member collection, which is why MsgPack004/003/015 tests already pass on base. So the agent fixed the duplicate/mixed-key crashes (which hit non-suppressed types too, see DuplicateKeysAreReportedWithoutAnalyzerFailureForGeneratedTypes failing on base) and wrote tests and README text as if that were #2234. Merged into the 3.1.x/master line, this change would not restore the analyzer for suppressed types; the early return would still need to move.

Evidence: [`TypeCollector.cs:723 @8373710f`](#ev-1f3bd1cf2e) (not verified) [`TypeCollector.cs:1369 @base`](#ev-f51a2a7c26) [`test MemberWithoutKeyIsReported passed`](#ev-7f46834b36) [`test DuplicateKeysAreReportedWithoutAnalyzerFailureForGeneratedTypes failed`](#ev-141f235580) [`issue 2234`](#ev-50efcd84fe) (not verified)

Tier effect: ask

Suggested fix: Retarget the fix to master: move the suppressSourceGeneration early return back below member analysis, as on develop, keep the ContainsKey guards and 'continue' (they are needed once member analysis runs again for suppressed types), and run the 8 analyzer tests on master, where the MsgPack004/003/015 ones should then fail without the fix.

<a id="f-claude-C2"></a>
#### Claude C2 [minor, correctness]: Positional-record Key(null) still crashes the analyzer for suppressed (and other) types

The BothStringAndIntKeyAreNull path hard-casts the property's syntax to PropertyDeclarationSyntax. For a positional record property it is a ParameterSyntax, so AD0001 InvalidCastException. Reproduced at this head with SuppressSourceGeneration = true (own probe). This is an invalid contract in such a type, so N1's 'must not crash on invalid contracts' is not fully met.

Evidence: [`TypeCollector.cs:985 @head`](#ev-ea86c4a3d1)

Tier effect: notify (reproduced by the pipeline (repro.claude.C2))

Suggested fix: Use (syntax as PropertyDeclarationSyntax)?.Identifier ?? (syntax as ParameterSyntax)?.Identifier, as the MemberNeedsKey path already does, and add a test.

<a id="f-claude-C3"></a>
#### Claude C3 [info, correctness]: 'continue' on mixed key kinds skips recursive collection of that member's type

After reporting DoNotMixStringAndIntKeys the new 'continue' also skips CollectCore for the member, so diagnostics about the member's own type (e.g. MsgPack003) are no longer produced for that member until the key kind is fixed. Acceptable because the type already has an error, but it hides a second problem until the first is fixed.

Evidence: [`TypeCollector.cs:1008 @head`](#ev-eeb0b47f0a)

Tier effect: silent

<a id="f-claude-C4"></a>
#### Claude C4 [info, correctness]: Duplicate-key guard makes the generator emit a formatter that silently drops the second member

For a non-suppressed type with duplicate keys, the generator (which has no diagnostic sink) used to fail with CS8785. Now it keeps the first member and emits a formatter without the second. The build still fails while MsgPack005 is an error, but if a project lowers that diagnostic's severity, it silently loses data. I saw this in my probe (formatter generated, analyzer reports MsgPack005).

Evidence: [`TypeCollector.cs:1023 @head`](#ev-bc6b3dd3fa) [`test DuplicateKeysAreReportedWithoutAnalyzerFailureForGeneratedTypes passed`](#ev-2935d06d6d)

Tier effect: silent

Suggested fix: When a key collision is detected, have GetObjectInfo return null (no formatter) instead of dropping the member.

<a id="f-nemotron-N1"></a>
#### Nemotron N1 [minor, correctness]: Duplicate-key diagnostic reports only one diagnostic although two members share the key

For duplicate keys the code reports KeysMustBeUnique only on the second member and then skips adding it, so the first member remains in the dictionary; users see one diagnostic instead of being told both members collide. This matches the tests' expectations but may under-report the contract problem.

Evidence: [`TypeCollector.cs:1014 @head`](#ev-16adc56b18) [`TypeCollector.cs:1016 @head`](#ev-9b063a4faf) [`test DuplicateIntKeysAreReportedWithoutAnalyzerFailure passed`](#ev-8fd1a8fc46)

Tier effect: notify

Suggested fix: Consider whether both members should be flagged; no code change required unless the product owner wants the first member reported too.

<a id="f-nemotron-N2"></a>
#### Nemotron N2 [minor, maintainability]: New test file triggers StyleCop SA1649 warning

SuppressedSourceGenerationTests.cs contains two public types but the file name matches neither, producing warning SA1649 in both ExecutionTests projects.

Evidence: [`check tests.execution_full_suite pass`](#ev-98002ca52b) [`SuppressedSourceGenerationTests.cs:9 @head`](#ev-64de3fafa7) [`SuppressedSourceGenerationTests.cs:18 @head`](#ev-328bd9d246)

Tier effect: notify

Suggested fix: Rename the file to SuppressedSourceGenerationType.cs or split the types into separate files.

<a id="f-nemotron-N3"></a>
#### Nemotron N3 [info, tests]: Runtime execution tests do not demonstrate the fix

SuppressedSourceGenerationTests round-trip and formatter-absence tests pass on base source as well, so they add regression coverage but not fix coverage; REQ-2234-N2 is satisfied by the analyzer tests instead.

Evidence: [`check tests.execution_fail_without_fix fail`](#ev-2f84e19b68) [`test NoFormatterIsGeneratedForSuppressedType passed`](#ev-f66e73f956)

Tier effect: silent

<a id="f-nemotron-N4"></a>
#### Nemotron N4 [info, docs]: README documents behavior accurately

README additions describe which diagnostics are and are not reported for suppressed types, matching the code's early-return behavior.

Evidence: [`README.md:1620 @head`](#ev-c204937ed1) (not verified) [`README.md:1634 @head`](#ev-f94a653f7f)

Tier effect: silent

<a id="f-nemotron-N5"></a>
#### Nemotron N5 [info, maintainability]: Execution tests required SDK 9 override

The generator references Microsoft.CodeAnalysis 4.12, so ExecutionTests cannot build with the repo-pinned SDK 8.0.402; CI on SDK 8 would fail to run these tests.

Evidence: [`check tests.execution_fail_without_fix fail`](#ev-2f84e19b68) [`SuppressedSourceGenerationTests.cs:1 @head`](#ev-f77df3c0b5)

Tier effect: silent

Suggested fix: Area owner should decide whether to pin the generator to Roslyn 4.11 or update global.json/CI to SDK 9.

#### Cited evidence

<a id="ev-7f46834b36"></a>
**test MemberWithoutKeyIsReported passed** (verified; cited by claude on REQ-2234-F1, claude:C1): facts.json tests.fail_without_fix: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **passed**
- Without the fix it **passed**: it does not show the change

<a id="ev-ab5dfeec65"></a>
**test MemberTypeMustBeMessagePackObjectIsReported passed** (verified; cited by claude on REQ-2234-F1): facts.json tests.fail_without_fix: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **passed**
- Without the fix it **passed**: it does not show the change

<a id="ev-0cdf78bf54"></a>
**test AllowPrivateRequiredIsReported passed** (verified; cited by claude on REQ-2234-F1): facts.json tests.fail_without_fix: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **passed**
- Without the fix it **passed**: it does not show the change

<a id="ev-283a17c90c"></a>
**test DuplicateIntKeysAreReportedWithoutAnalyzerFailure failed** (verified; cited by claude on REQ-2234-F1, nemotron on REQ-2234-F1, nemotron on REQ-2234-N2): facts.json tests.fail_without_fix: failed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-8fd1a8fc46"></a>
**test DuplicateIntKeysAreReportedWithoutAnalyzerFailure passed** (verified; cited by claude on REQ-2234-F1, codex on REQ-2234-F1, nemotron on REQ-2234-F1, nemotron on REQ-2234-N1, nemotron:N1): facts.json tests.targeted: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-25ded34e20"></a>
**test MixedKeyKindsAreReportedWithoutAnalyzerFailure passed** (verified; cited by claude on REQ-2234-F1, codex on REQ-2234-F1, nemotron on REQ-2234-F1, nemotron on REQ-2234-N1): facts.json tests.targeted: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-bc6b3dd3fa"></a>
**TypeCollector.cs:1023 @head** (verified; cited by claude on REQ-2234-F1, codex on REQ-2234-F1, nemotron on REQ-2234-F1, claude:C4): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1023 at head 9007cee1

`if (!intMembers.ContainsKey(member.IntKey))`

<a id="ev-a0957ebdbe"></a>
**TypeCollector.cs:1008 @head** (verified; cited by claude on REQ-2234-F1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1008 at head 9007cee1

`continue; // The key kind does not match the other members`

<a id="ev-d78b746a74"></a>
**check tests.fail_without_fix** (verified; cited by claude on REQ-2234-F1, codex on REQ-2234-F1, codex on REQ-2234-F2, claude on REQ-2234-N2, codex on REQ-2234-N2): facts.json: tests.fail_without_fix pass: new tests fail on base source: 4/8 failed -> tests do cover the change (4 new tests pass without the fix)

- `tests.fail_without_fix` **pass**: new tests fail on base source: 4/8 failed -> tests do cover the change (4 new tests pass without the fix) (dotnet test (source reverted, tests kept) 8.0.402)
- log: `evidence/2234/logs/tests_fail_without_fix.1.log`

<a id="ev-dffe050cec"></a>
**REQ-2234-F1 text** (verified; cited by nemotron on REQ-2234-F1): REQ-2234-F1 text contains the quote

> The analyzer must report contract diagnostics (e.g. missing [Key], duplicate keys, mixed key kinds) for [MessagePackObject(SuppressSourceGeneration = true)] types, as it did in version 3.1.0.

<a id="ev-eeb0b47f0a"></a>
**TypeCollector.cs:1008 @head** (verified; cited by nemotron on REQ-2234-F1, claude:C3): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1008 at head 9007cee1

`continue; // The key kind does not match the other members; the diagnostic is reported, so skip this member.`

<a id="ev-1d23e816db"></a>
**TypeCollector.cs:1039 @head** (verified; cited by nemotron on REQ-2234-F1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1039 at head 9007cee1

`if (!stringMembers.ContainsKey(member.StringKey))`

<a id="ev-02bb823660"></a>
**test MemberWithoutKeyIsReported passed** (verified; cited by nemotron on REQ-2234-F1): facts.json tests.targeted: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **passed**
- Without the fix it **passed**: it does not show the change

<a id="ev-d0aaf0ddcf"></a>
**test AllowPrivateRequiredIsReported passed** (verified; cited by nemotron on REQ-2234-F1): facts.json tests.targeted: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **passed**
- Without the fix it **passed**: it does not show the change

<a id="ev-0fc5c1ea52"></a>
**test MemberTypeMustBeMessagePackObjectIsReported passed** (verified; cited by nemotron on REQ-2234-F1): facts.json tests.targeted: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **passed**
- Without the fix it **passed**: it does not show the change

<a id="ev-bb565b0d63"></a>
**test DuplicateStringKeysAreReportedWithoutAnalyzerFailure passed** (verified; cited by nemotron on REQ-2234-F1, claude on REQ-2234-N1, codex on REQ-2234-N1, nemotron on REQ-2234-N1): facts.json tests.targeted: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-62faeb2508"></a>
**check tests.fail_without_fix pass** (verified; cited by nemotron on REQ-2234-F1, nemotron on REQ-2234-N2): facts.json: tests.fail_without_fix pass: new tests fail on base source: 4/8 failed -> tests do cover the change (4 new tests pass without the fix)

- `tests.fail_without_fix` **pass**: new tests fail on base source: 4/8 failed -> tests do cover the change (4 new tests pass without the fix) (dotnet test (source reverted, tests kept) 8.0.402)
- log: `evidence/2234/logs/tests_fail_without_fix.1.log`

<a id="ev-99a149a316"></a>
**test MixedKeyKindsAreReportedWithoutAnalyzerFailure failed** (verified; cited by nemotron on REQ-2234-F1, claude on REQ-2234-N2, nemotron on REQ-2234-N2): facts.json tests.fail_without_fix: failed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-165dc4a6ea"></a>
**test SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed passed** (verified; cited by claude on REQ-2234-F2, nemotron on REQ-2234-F2): facts.json tests.fail_without_fix: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **passed**
- Without the fix it **passed**: it does not show the change

<a id="ev-097f9caee8"></a>
**test SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed passed** (verified; cited by claude on REQ-2234-F2, codex on REQ-2234-F2, nemotron on REQ-2234-F2): facts.json tests.targeted: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **passed**
- Without the fix it **passed**: it does not show the change

<a id="ev-6768fd1ae3"></a>
**TypeCollector.cs:1383 @head** (verified; cited by claude on REQ-2234-F2, nemotron on REQ-2234-F2): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1383 at head 9007cee1

`if (suppressSourceGeneration is true)`

<a id="ev-337b4ac064"></a>
**TypeCollector.cs:1407 @head** (verified; cited by claude on REQ-2234-F2): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1407 at head 9007cee1

`MsgPack00xMessagePackAnalyzer.PartialTypeRequired, primaryLocation`

<a id="ev-e5721f8767"></a>
**TypeCollector.cs:989 @head** (verified; cited by claude on REQ-2234-F2): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:989 at head 9007cee1

`if (suppressSourceGeneration is not true && isInitOnly)`

<a id="ev-d3c4dd6a49"></a>
**REQ-2234-F2 text** (verified; cited by nemotron on REQ-2234-F2): REQ-2234-F2 text contains the quote

> Diagnostics that only apply when a formatter is generated (partial-class requirement, AOT-only checks) must not be reported for types with SuppressSourceGeneration = true.

<a id="ev-76656896d1"></a>
**TypeCollector.cs:1386 @head** (verified; cited by nemotron on REQ-2234-F2): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1386 at head 9007cee1

`return null;`

<a id="ev-4c693214ba"></a>
**TypeCollector.cs:985 @head** (verified; cited by claude on REQ-2234-N1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:985 at head 9007cee1

`((PropertyDeclarationSyntax)item.DeclaringSyntaxReferences[0].GetSyntax()).Identifier.GetLocation()`

<a id="ev-df050a6665"></a>
**check tests.full_suite** (verified; cited by claude on REQ-2234-N1, codex on REQ-2234-N1, claude on REQ-2234-N2, codex on REQ-2234-N2): facts.json: tests.full_suite pass: tests/MessagePack.SourceGenerator.Tests: 175 tests, 175 passed, 0 failed (0 not failing on base, 0 also failing on base)

- `tests.full_suite` **pass**: tests/MessagePack.SourceGenerator.Tests: 175 tests, 175 passed, 0 failed (0 not failing on base, 0 also failing on base) (dotnet test 8.0.402)
- log: `evidence/2234/logs/tests_full_suite.log`

<a id="ev-1ddd8d4fc0"></a>
**REQ-2234-N1 text** (verified; cited by claude on REQ-2234-N1): REQ-2234-N1 text contains the quote

> The analyzer and generator must not crash on invalid contracts (e.g. duplicate keys) in such types.

<a id="ev-ca3c3dd4f0"></a>
**REQ-2234-N1 text** (verified; cited by nemotron on REQ-2234-N1): REQ-2234-N1 text contains the quote

> The analyzer and generator must not crash on invalid contracts (e.g. duplicate keys) in such types.

<a id="ev-d448f979e6"></a>
**check tests.full_suite pass** (verified; cited by nemotron on REQ-2234-N1, nemotron on REQ-2234-N2): facts.json: tests.full_suite pass: tests/MessagePack.SourceGenerator.Tests: 175 tests, 175 passed, 0 failed (0 not failing on base, 0 also failing on base)

- `tests.full_suite` **pass**: tests/MessagePack.SourceGenerator.Tests: 175 tests, 175 passed, 0 failed (0 not failing on base, 0 also failing on base) (dotnet test 8.0.402)
- log: `evidence/2234/logs/tests_full_suite.log`

<a id="ev-fbc74f77d6"></a>
**check tests.execution_full_suite** (verified; cited by claude on REQ-2234-N2): facts.json: tests.execution_full_suite pass: tests/MessagePack.SourceGenerator.ExecutionTests: 16/16 passed (base 14/14), 0 failures not on base; tests/MessagePack.SourceGenerator.MapModeExecutionTests: 22/22 passed (base 20/20), 0 failures not on base

- `tests.execution_full_suite` **pass**: tests/MessagePack.SourceGenerator.ExecutionTests: 16/16 passed (base 14/14), 0 failures not on base; tests/MessagePack.SourceGenerator.MapModeExecutionTests: 22/22 passed (base 20/20), 0 failures not on base (dotnet test (whole ExecutionTests, MapModeExecutionTests) vs base 9.0.321)
- log: `evidence/2234/logs/execution.ExecutionTests.full.log`
- log: `evidence/2234/logs/execution.MapModeExecutionTests.full.log`

<a id="ev-05862d94ce"></a>
**check tests.execution_fail_without_fix** (verified; cited by claude on REQ-2234-N2): facts.json: tests.execution_fail_without_fix fail: new runtime tests pass on base source: 0/4 failed -> these runtime tests do NOT demonstrate the change (runtime behaviour they check is identical with and without the fix)

- `tests.execution_fail_without_fix` **fail**: new runtime tests pass on base source: 0/4 failed -> these runtime tests do NOT demonstrate the change (runtime behaviour they check is identical with and without the fix) (dotnet test (source reverted, tests kept) - ExecutionTests 9.0.321)
- log: `evidence/2234/logs/execution_fail_without_fix.ExecutionTests.build.log`
- log: `evidence/2234/logs/execution_fail_without_fix.ExecutionTests.targeted.log`
- log: `evidence/2234/logs/execution_fail_without_fix.ExecutionTests.full.log`
- log: `evidence/2234/logs/execution_fail_without_fix.MapModeExecutionTests.build.log`
- log: `evidence/2234/logs/execution_fail_without_fix.MapModeExecutionTests.targeted.log`
- log: `evidence/2234/logs/execution_fail_without_fix.MapModeExecutionTests.full.log`

<a id="ev-987c65a3c2"></a>
**test DuplicateStringKeysAreReportedWithoutAnalyzerFailure failed** (verified; cited by claude on REQ-2234-N2, nemotron on REQ-2234-N2): facts.json tests.fail_without_fix: failed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-f7ce6ac392"></a>
**test SuppressedTypeRoundTripsThroughDynamicResolver passed** (verified; cited by claude on REQ-2234-N2): facts.json tests.execution_fail_without_fix: passed (new test)

- change head (`tests.targeted.execution`, tests/MessagePack.SourceGenerator.ExecutionTests): **passed**
- change head (`tests.targeted.execution`, tests/MessagePack.SourceGenerator.MapModeExecutionTests): **passed**
- source reverted, tests kept (without the fix) (`tests.execution_fail_without_fix`, tests/MessagePack.SourceGenerator.ExecutionTests): **passed**
- source reverted, tests kept (without the fix) (`tests.execution_fail_without_fix`, tests/MessagePack.SourceGenerator.MapModeExecutionTests): **passed**
- Without the fix it **passed**: it does not show the change

<a id="ev-86204fae15"></a>
**REQ-2234-N2 text** (verified; cited by nemotron on REQ-2234-N2): REQ-2234-N2 text contains the quote

> The fix is covered by automated tests that fail without it; no regressions in the existing test suite.

<a id="ev-141f235580"></a>
**test DuplicateKeysAreReportedWithoutAnalyzerFailureForGeneratedTypes failed** (verified; cited by nemotron on REQ-2234-N2, claude:C1): facts.json tests.fail_without_fix: failed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-1f3bd1cf2e"></a>
**TypeCollector.cs:723 @8373710f** (NOT verified; cited by claude:C1): evidence must cite head or base, not '8373710fb0ae4bb453737f773b930401d8500c31'

`if (suppressSourceGeneration is true)`

<a id="ev-f51a2a7c26"></a>
**TypeCollector.cs:1369 @base** (verified; cited by claude:C1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1369 at base 32258fdb

`if (suppressSourceGeneration is true)`

<a id="ev-50efcd84fe"></a>
**issue 2234** (NOT verified; cited by claude:C1): issue text cannot be verified offline (not counted as evidence)

<a id="ev-ea86c4a3d1"></a>
**TypeCollector.cs:985 @head** (verified; cited by claude:C2): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:985 at head 9007cee1

`(PropertyDeclarationSyntax)item.DeclaringSyntaxReferences[0].GetSyntax()`

<a id="ev-2935d06d6d"></a>
**test DuplicateKeysAreReportedWithoutAnalyzerFailureForGeneratedTypes passed** (verified; cited by claude:C4): facts.json tests.targeted: passed (new test)

- change head (`tests.targeted`): **passed**
- source reverted, tests kept (without the fix) (`tests.fail_without_fix`): **failed**
- Without the fix it **failed**: it tests the change

<a id="ev-16adc56b18"></a>
**TypeCollector.cs:1014 @head** (verified; cited by nemotron:N1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1014 at head 9007cee1

`if (intMembers.ContainsKey(intKey!.Value))`

<a id="ev-9b063a4faf"></a>
**TypeCollector.cs:1016 @head** (verified; cited by nemotron:N1): quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1016 at head 9007cee1

`this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.KeysMustBeUnique, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));`

<a id="ev-98002ca52b"></a>
**check tests.execution_full_suite pass** (verified; cited by nemotron:N2): facts.json: tests.execution_full_suite pass: tests/MessagePack.SourceGenerator.ExecutionTests: 16/16 passed (base 14/14), 0 failures not on base; tests/MessagePack.SourceGenerator.MapModeExecutionTests: 22/22 passed (base 20/20), 0 failures not on base

- `tests.execution_full_suite` **pass**: tests/MessagePack.SourceGenerator.ExecutionTests: 16/16 passed (base 14/14), 0 failures not on base; tests/MessagePack.SourceGenerator.MapModeExecutionTests: 22/22 passed (base 20/20), 0 failures not on base (dotnet test (whole ExecutionTests, MapModeExecutionTests) vs base 9.0.321)
- log: `evidence/2234/logs/execution.ExecutionTests.full.log`
- log: `evidence/2234/logs/execution.MapModeExecutionTests.full.log`

<a id="ev-64de3fafa7"></a>
**SuppressedSourceGenerationTests.cs:9 @head** (verified; cited by nemotron:N2): quote matches tests/MessagePack.SourceGenerator.ExecutionTests/SuppressedSourceGenerationTests.cs:9 at head 9007cee1

`public class SuppressedSourceGenerationType`

<a id="ev-328bd9d246"></a>
**SuppressedSourceGenerationTests.cs:18 @head** (verified; cited by nemotron:N2): quote matches tests/MessagePack.SourceGenerator.ExecutionTests/SuppressedSourceGenerationTests.cs:18 at head 9007cee1

`public class SuppressedSourceGenerationTests`

<a id="ev-2f84e19b68"></a>
**check tests.execution_fail_without_fix fail** (verified; cited by nemotron:N3, nemotron:N5): facts.json: tests.execution_fail_without_fix fail: new runtime tests pass on base source: 0/4 failed -> these runtime tests do NOT demonstrate the change (runtime behaviour they check is identical with and without the fix)

- `tests.execution_fail_without_fix` **fail**: new runtime tests pass on base source: 0/4 failed -> these runtime tests do NOT demonstrate the change (runtime behaviour they check is identical with and without the fix) (dotnet test (source reverted, tests kept) - ExecutionTests 9.0.321)
- log: `evidence/2234/logs/execution_fail_without_fix.ExecutionTests.build.log`
- log: `evidence/2234/logs/execution_fail_without_fix.ExecutionTests.targeted.log`
- log: `evidence/2234/logs/execution_fail_without_fix.ExecutionTests.full.log`
- log: `evidence/2234/logs/execution_fail_without_fix.MapModeExecutionTests.build.log`
- log: `evidence/2234/logs/execution_fail_without_fix.MapModeExecutionTests.targeted.log`
- log: `evidence/2234/logs/execution_fail_without_fix.MapModeExecutionTests.full.log`

<a id="ev-f66e73f956"></a>
**test NoFormatterIsGeneratedForSuppressedType passed** (verified; cited by nemotron:N3): facts.json tests.execution_fail_without_fix: passed (new test)

- change head (`tests.targeted.execution`, tests/MessagePack.SourceGenerator.ExecutionTests): **passed**
- change head (`tests.targeted.execution`, tests/MessagePack.SourceGenerator.MapModeExecutionTests): **passed**
- source reverted, tests kept (without the fix) (`tests.execution_fail_without_fix`, tests/MessagePack.SourceGenerator.ExecutionTests): **passed**
- source reverted, tests kept (without the fix) (`tests.execution_fail_without_fix`, tests/MessagePack.SourceGenerator.MapModeExecutionTests): **passed**
- Without the fix it **passed**: it does not show the change

<a id="ev-c204937ed1"></a>
**README.md:1620 @head** (NOT verified; cited by nemotron:N4): quote not on README.md:1620 ±3 at head; it does occur at line 1625, outside tolerance

`The analyzer still validates these types, because they are serialized at run time and must still have a valid contract:`

<a id="ev-f94a653f7f"></a>
**README.md:1634 @head** (verified; cited by nemotron:N4): quote matches README.md:1634 at head 9007cee1 (found at line 1632, 2 off)

`The analyzer does not report the partial-class requirement ([MsgPack011](doc/analyzers/MsgPack011.md)) or the AOT-only checks ([MsgPack016](doc/analyzers/MsgPack016.md) and [MsgPack017](doc/analyzers/MsgPack017.md)) for these types, because they only apply when a formatter is generated.`

<a id="ev-f77df3c0b5"></a>
**SuppressedSourceGenerationTests.cs:1 @head** (verified; cited by nemotron:N5): quote matches tests/MessagePack.SourceGenerator.ExecutionTests/SuppressedSourceGenerationTests.cs:1 at head 9007cee1

`// Copyright (c) All contributors. All rights reserved.`

</details>

<details><summary><b>Full detail</b>: all tier drivers, risk score, every check, areas, not checked, residual risk</summary>

Branch `ju26-issue-2234` (32258fdb..9007cee1), 4 files, +262 -4. Author Stelian Vultur (agent-written: True). Commit: Implementation for #2234 The analyzer does not work if SuppressSourceGeneration = true

Mandate `messagepack-csharp` v4 sha256 `4b247d4ec39413dd`, signature: valid, Toivo

<a id="all-drivers"></a>
#### All tier drivers (tier = strictest)

- ask: verified finding `claude:C1`: major: The issue's 3.1.1 regression is not on this base; the change fixes a different crash
- ask: refused clause `REQ-2234-N1`: not_met: claude: The duplicate-key and mixed-kind crashes are fixed, and the full suite passes (175/175). But not every invalid contract in such a type is crash-free. The hard cast at line 985 is untouched, and my probe (scratch worktree, SDK 8, not in facts.json) of '[MessagePackObject(SuppressSourceGeneration = true)] public record Cmd([property: Key(null)] string Scope)' still gives AD0001 InvalidCastException (ParameterSyntax to PropertyDeclarationSyntax) at this head. The generator side of the duplicate-key fix has no test in facts.json (the new analyzer tests use CSharpCodeFixVerifier, analyzer only), though my probe showed no CS8785 for duplicate keys at head.; reviewers_disagree: claude says not_met, codex says met, nemotron says met
- ask: refused clause `REQ-2234-N2`: thin_evidence: codex says met with 0 verified evidence items about the change (of 2 cited; requirement quotes and unclaimed outcomes don't count)
- ask: reviewer refusal `claude`: Whether this change resolves issue #2234 for users of the released 3.1.x packages (The facts and tests were produced against base 32258fdb (develop line), which does not contain the 3.1.1 regression. Nothing was built or tested against master/v3.1.x, so whether the change applies there and fixes the reported symptom is not established (and C1 suggests it would not on its own).)
- ask: reviewer refusal `nemotron`: Runtime library behavior (src/MessagePack) and net472/netstandard builds (Not run; the runtime library was not modified and only net8.0 was built.)
- ask: reviewer refusal `nemotron`: Security review of analyzer deserializing untrusted input (No security-specific evidence was provided and no security analysis was performed.)
- ask: risk score `risk`: score 67.6 (notify>=15, ask>=40, block>=130); largest: failed_checks 25 + area_sensitivity 20 + lines_changed 10.6
- notify: verified finding `claude:C2`: minor: Positional-record Key(null) still crashes the analyzer for suppressed (and other) types (reproduced by the pipeline (repro.claude.C2))
- notify: verified finding `nemotron:N1`: minor: Duplicate-key diagnostic reports only one diagnostic although two members share the key
- notify: verified finding `nemotron:N2`: minor: New test file triggers StyleCop SA1649 warning
- notify: reviewer refusal `claude`: Whether the README section's list of diagnostics still reported for suppressed types is complete and accurate (Not every listed diagnostic (e.g. MsgPack012 inaccessible types) is covered by a test in facts.json, and I did not verify each one.) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: reviewer refusal `nemotron`: Parity with analyzer behavior in version 3.1.0 (No evidence about version 3.1.0 behavior was provided; cannot determine whether contract diagnostics match that release.) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: reviewer refusal `nemotron`: Whether generation-only diagnostics (MsgPack011, MsgPack016, MsgPack017) are truly unreported on base for suppressed types (The fail_without_fix run only covers four analyzer tests; no base-source evidence exists for SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed.) [out of scope: names no clause, not marked blocking, touches no mandated check or sensitive term]
- notify: held before `REQ-2234-F1`: met, but not achieved by this change: all 3 of the clause's tests that were run without the fix pass there too: AllowPrivateRequiredIsReported, MemberTypeMustBeMessagePackObjectIsReported, MemberWithoutKeyIsReported
- notify: held before `REQ-2234-F2`: met, but not achieved by this change: all 1 of the clause's tests that were run without the fix pass there too: SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed
- notify: trust cap `generator-analyzer-core`: generator-analyzer-core: AI may clear at most to notify (mandate clearance right)
- silent: trust cap `docs`: docs: AI may clear at most to silent (mandate clearance right)
- silent: trust cap `tests`: tests: AI may clear at most to silent (mandate clearance right)

#### Who reviewed

Participating reviewers: claude, codex, nemotron. Adjudicator: gemini. Confidential: no. Rule: proven needs every participating reviewer to say met with verified evidence, and the clause's checks to pass.

| Reviewer | Model | Prompt | Verified findings | Rejected | Refusals |
|---|---|---|---|---|---|
| claude | claude-opus-5-5 (Anthropic) | review-v1 | 4 | 0 | 2 |
| codex | GPT-6 (OpenAI) | review-v1 | 0 | 0 | 0 |
| nemotron | nvidia/nemotron-3.5-super-vl-120b-a12b (NVIDIA) | review-v1 | 5 | 0 | 4 |

#### Every check

| Check | Status | Tool | Summary |
|---|---|---|---|
| build | pass | dotnet build 8.0.402 | 0 errors, 1 unique warnings |
| tests.targeted | pass | dotnet test 8.0.402 | 8 passed, 0 failed, 0 skipped (8 new tests in run) |
| tests.fail_without_fix | pass | dotnet test (source reverted, tests kept) 8.0.402 | new tests fail on base source: 4/8 failed -> tests do cover the change (4 new tests pass without the fix) |
| tests.full_suite | pass | dotnet test 8.0.402 | tests/MessagePack.SourceGenerator.Tests: 175 tests, 175 passed, 0 failed (0 not failing on base, 0 also failing on base) |
| public_api | pass | git diff of PublicAPI.*.txt + scan of added public/protected declarations in src/  | no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or removed in src/ |
| analyzers | pass | dotnet build warnings (Roslyn analyzers, StyleCop, PublicApiAnalyzers) vs base  | no new warnings |
| tests.targeted.execution | pass | dotnet build + dotnet test (ExecutionTests, MapModeExecutionTests) 9.0.321 | SuppressedSourceGenerationTests: 4 passed, 0 failed (4 new test results; runtime: generator runs inside csc, no CS9057) |
| tests.execution_fail_without_fix | fail | dotnet test (source reverted, tests kept) - ExecutionTests 9.0.321 | new runtime tests pass on base source: 0/4 failed -> these runtime tests do NOT demonstrate the change (runtime behaviour they check is identical with and without the fix) |
| tests.execution_full_suite | pass | dotnet test (whole ExecutionTests, MapModeExecutionTests) vs base 9.0.321 | tests/MessagePack.SourceGenerator.ExecutionTests: 16/16 passed (base 14/14), 0 failures not on base; tests/MessagePack.SourceGenerator.MapModeExecutionTests: 22/22 passed (base 20/20), 0 failures not on base |
| repro.claude.C2 | pass | dotnet test (reviewer repro test copied into tests/MessagePack.SourceGenerator.Tests/CountersignRepro) 8.0.402 | reproduced by the pipeline: failed on head (claim: failed), failed on base (claim: failed), passed on control (claim: passed) |
| injection_scan | pass | countersign.injection (deterministic pattern scan) injection-v1 | no text addressed to automated reviewers in the added lines, commit message or PR text |
| deps.delta | pass | dotnet restore (every *.csproj, NuGet Audit mode=all) -> CycloneDX 1.6, base vs head 8.0.402 | 238 packages on head (238 on base) across 30 projects; 0 added, 0 version changes, 0 removed; 0 new vulnerability hits (6 already on base) |
| build.egress | pass | CRACI network policy (cracicorp/setup@v1) + job log scan  | built on CRACI under a deny-by-default policy: only 13 TLS host patterns on ports 443 (github.com, codeload.github.com, objects.githubusercontent.com, api.nuget.org, *.nuget.org, pkgs.dev.azure.com, ...); presets ['github']; no blocked connection in 40 logs; every NuGet feed the head declares is inside the policy |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v4 (4b247d4ec394)

#### Requirement trace (engine codes)

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-2234-F1 | held_before | claude: met (8/9), codex: met (3/4), nemotron: met (12/13) | build: pass, tests.targeted: pass | held_before |
| REQ-2234-F2 | held_before | claude: met (5/5), codex: met (1/2), nemotron: met (4/5) | build: pass, tests.targeted: pass | held_before |
| REQ-2234-N1 | refused | claude: not_met (2/4), codex: met (1/2), nemotron: met (4/5) | build: pass, tests.full_suite: pass | not_met, reviewers_disagree |
| REQ-2234-N2 | refused | claude: met (3/7), codex: met (0/2), nemotron: met (6/7) | build: pass, tests.fail_without_fix: pass | thin_evidence |

#### What the AI refused to decide (every reviewer refusal)

- **claude** refused: Whether this change resolves issue #2234 for users of the released 3.1.x packages. Why: The facts and tests were produced against base 32258fdb (develop line), which does not contain the 3.1.1 regression. Nothing was built or tested against master/v3.1.x, so whether the change applies there and fixes the reported symptom is not established (and C1 suggests it would not on its own). Who should decide: analyzer area owner / maintainers choosing the target branch
- **claude** refused: Whether the README section's list of diagnostics still reported for suppressed types is complete and accurate. Why: Not every listed diagnostic (e.g. MsgPack012 inaccessible types) is covered by a test in facts.json, and I did not verify each one. Who should decide: docs owner
- **nemotron** refused: Parity with analyzer behavior in version 3.1.0. Why: No evidence about version 3.1.0 behavior was provided; cannot determine whether contract diagnostics match that release. Who should decide: Area owner or maintainer with access to the 3.1.0 release
- **nemotron** refused: Whether generation-only diagnostics (MsgPack011, MsgPack016, MsgPack017) are truly unreported on base for suppressed types. Why: The fail_without_fix run only covers four analyzer tests; no base-source evidence exists for SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed. Who should decide: Area owner
- **nemotron** refused: Runtime library behavior (src/MessagePack) and net472/netstandard builds. Why: Not run; the runtime library was not modified and only net8.0 was built. Who should decide: Area owner
- **nemotron** refused: Security review of analyzer deserializing untrusted input. Why: No security-specific evidence was provided and no security analysis was performed. Who should decide: Security reviewer

<a id="areas"></a>
#### Areas

| Area | Owner | Sensitivity | AI cap | Files |
|---|---|---|---|---:|
| generator-analyzer-core | Toivo | high | notify (mandate clearance right) | 1 |
| docs | Rene | low | silent (mandate clearance right) | 1 |
| tests | Toivo | low | silent (mandate clearance right) | 2 |

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

- REQ-2234-N1 not proven: not_met; reviewers_disagree
- REQ-2234-N2 not proven: thin_evidence
- REQ-2234-F1 held before this change (met, but not achieved by it)
- REQ-2234-F2 held before this change (met, but not achieved by it)
- Reviewer refusal (claude): Whether this change resolves issue #2234 for users of the released 3.1.x packages
- Reviewer refusal (claude): Whether the README section's list of diagnostics still reported for suppressed types is complete and accurate (out of scope: notify)
- Reviewer refusal (nemotron): Parity with analyzer behavior in version 3.1.0 (out of scope: notify)
- Reviewer refusal (nemotron): Whether generation-only diagnostics (MsgPack011, MsgPack016, MsgPack017) are truly unreported on base for suppressed types (out of scope: notify)
- Reviewer refusal (nemotron): Runtime library behavior (src/MessagePack) and net472/netstandard builds
- Reviewer refusal (nemotron): Security review of analyzer deserializing untrusted input
- Open major finding claude:C1: The issue's 3.1.1 regression is not on this base; the change fixes a different crash
- tests.MessagePack.Tests not run (runtime library src/MessagePack not modified by the change; suite not run)
- build.net472/netstandard not run (only the net8.0 slice of src/MessagePack was built (Linux container, Debug))
- benchmarks not run (no runtime serialization hot path touched (generator/analyzer only))
- 2 disputed item(s) were not adjudicated (adjudicator gemini has not run)
- Standing gaps of this pipeline: other-targets, runtime-perf, semantic-intent, provenance (see not checked)

<a id="risk"></a>
#### Risk score: 67.6 -> ask

| Factor | Points | Reason |
|---|---:|---|
| area_sensitivity | 20 | most sensitive area touched: generator-analyzer-core (high) |
| files_changed | 4 | 4 files x 1 (cap 20) |
| lines_changed | 10.6 | 266 non-generated lines x 4/100 (cap 20) |
| generated_files | 0.0 | 0 generated files x 0.1 (cap 10) |
| public_api_change | 0 | public_api check: no change |
| source_without_tests | 0 | tests changed alongside source |
| security_sensitive_paths | 0 | none touched |
| fail_without_fix_not_shown | 0 | tests.fail_without_fix: pass |
| reviewer_disagreement | 8 | 1 clause(s) x 8: REQ-2234-N1 |
| failed_checks | 25 | 1 failed check(s) x 25: tests.execution_fail_without_fix |
| **total** | **67.6** | bands: {'notify': 15, 'ask': 40, 'block': 130} |

Inputs: facts `evidence/2234/facts.json`, requirements `requirements/2234.yaml`, reviews `reviews/2234/claude.json`, `reviews/2234/codex.json`, `reviews/2234/nemotron.json`

</details>
