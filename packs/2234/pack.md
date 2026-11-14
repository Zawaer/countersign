## Countersign: **ASK**, owner **Toivo**

**#2234 The analyzer does not work if SuppressSourceGeneration = true**

**Why:** The change fixes a different crash

- ! Builds, tests pass; 2 other checks fail
- ✕ Reviewers found a major issue
- ✕ Signed by Toivo: request changes

<details><summary><b>Evidence</b>: requirements, findings, refusals, checks, risk, how to sign</summary>

#### Sign-off card: change 2234 is ASK, owner Toivo

**Agent-written change for #2234: The analyzer does not work if SuppressSourceGeneration = true**

Changes 1 source file (TypeCollector.cs), 2 test files, 1 doc file (+262 -4) on ju26-issue-2234 by Stelian Vultur. Judged against 4 requirement clauses from #2234 (placeholder requirement set, not Tieto's official one).

**Why ask**

1. Claude found a verified major issue: The issue's 3.1.1 regression is not on this base; the change fixes a different crash ([evidence](#f-claude-C1))
2. 2 of 4 requirement clauses not proven. ([evidence](#chain-REQ-2234-N1)) <details><summary>more</summary>REQ-2234-N1: Claude says not met (Codex and Nemotron: met); Gemini: Claude's objection is supported (+1 more)</details>
3. The AI declined to decide 3 questions ([evidence](#refused)) <details><summary>more</summary>e.g. Whether this change resolves issue #2234 for users of the released 3.1.x packages</details>

<sub>All 19 tier drivers are under Full detail.</sub>

**Requirement trace**

| Status | Clause | Why |
|---|---|---|
| **HELD BEFORE** | [F1](#chain-REQ-2234-F1) | Met, but already true before this change <details><summary>more</summary>all 3 of the clause's tests that were run without the fix pass there too: AllowPrivateRequiredIsReported, MemberTypeMustBeMessagePackObjectIsReported, MemberWithoutKeyIsReported</details> |
| **HELD BEFORE** | [F2](#chain-REQ-2234-F2) | Met, but already true before this change <details><summary>more</summary>all 1 of the clause's tests that were run without the fix pass there too: SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed</details> |
| **NOT MET** | [N1](#chain-REQ-2234-N1) | Claude says not met (Codex and Nemotron: met); Gemini: Claude's objection is supported |
| **REFUSED** | [N2](#chain-REQ-2234-N2) | Codex said met without verified evidence |

<details><summary>Gemini on N1: Claude's objection is supported; backs 2 of 3 claims for Claude's 'not met', 2 of 4 for 'met' (advisory)</summary>

Duplicate-key analyzer tests pass on head, while repro.claude.C2 fails on both head and base and TypeCollector.cs:985 retains an unguarded PropertyDeclarationSyntax cast.

**Backed by the cited evidence**

- **Claude**: Duplicate-string-key analyzer crash is fixed and the 175-test source-generator suite passes (Verified test SuppressSourceGenerationAnalyzerTests.DuplicateStringKeysAreReportedWithoutAnalyzerFailure passes in tests.targeted and tests.full_suite passes (175/175))
- **Claude**: An unguarded cast to PropertyDeclarationSyntax remains at TypeCollector.cs:985 when both int and string keys are null (Verified code quote at src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:985 shows ((PropertyDeclarationSyntax)item.DeclaringSyntaxReferences[0].GetSyntax()).Identifier.GetLocation())
- **Codex**: Duplicate-string-key contracts no longer crash the analyzer and the existing source-generator suite passes (Verified test SuppressSourceGenerationAnalyzerTests.DuplicateStringKeysAreReportedWithoutAnalyzerFailure passes in tests.targeted and tests.full_suite passes (175/175))
- **Nemotron**: Duplicate-int-key analyzer crash is fixed on head and the pipeline repro repro.claude.C2 still fails on head and base while passing on control (Verified test SuppressSourceGenerationAnalyzerTests.DuplicateIntKeysAreReportedWithoutAnalyzerFailure passes in tests.targeted and fails in tests.fail_without_fix, and facts.json repro.claude.C2 confirms failed on head, failed on base, passed on control)

**Not backed**

- **Claude**: Scratch-worktree probe triggers AD0001 InvalidCastException at head and generator probe shows no CS8785 for duplicate keys (Neither scratch-worktree probe nor a generator-side duplicate-key test is in facts.json)
- **Codex**: Invalid contracts generally satisfy REQ-2234-N1 without analyzer or generator crashes (Cited evidence only covers DuplicateStringKeysAreReportedWithoutAnalyzerFailure and tests.full_suite; it does not cover null-key positional records (repro.claude.C2 fails on head) or a generator-side invalid-contract test)
- **Nemotron**: Named test ReproClaude2234C2Tests.PositionalRecordWithNullKeyDoesNotCrashAnalyzerForSuppressedType fails with AD0001 InvalidCastException and passes on origin/ju26-issue-2283 due to a null-safe lookup (The cited test name is engine_verified: false (not in facts.json), and the specific exception type and control-branch diff are not in the verified evidence)

**What would settle it**

- Area-owner ruling on whether REQ-2234-N1 requires fixing the pre-existing TypeCollector.cs:985 cast for positional records with [property: Key(null)] in this change
- A test in facts.json covering [MessagePackObject(SuppressSourceGeneration = true)] on a positional record with [property: Key(null)] asserting no AD0001 analyzer crash
- A source-generator test in facts.json exercising invalid contracts (e.g. duplicate keys) in a SuppressSourceGeneration = true type and asserting no generator crash (CS8785)

</details>

**What the AI found**

- **major** [The issue's 3.1.1 regression is not on this base; the change fixes a different crash](#f-claude-C1) (Claude C1) [`TypeCollector.cs:1369 @base`](#ev-f51a2a7c26) [`test MemberWithoutKeyIsReported passed`](#ev-7f46834b36)
- **minor** [Positional-record Key(null) still crashes the analyzer for suppressed (and other) types](#f-claude-C2) (Claude C2) [`TypeCollector.cs:985 @head`](#ev-ea86c4a3d1)
- **minor** [Duplicate-key diagnostic reports only one diagnostic although two members share the key](#f-nemotron-N1) (Nemotron N1, also Claude) [`TypeCollector.cs:1014 @head`](#ev-16adc56b18) [`TypeCollector.cs:1016 @head`](#ev-9b063a4faf)
- +6 more under Evidence.

<a id="refused"></a>**What the AI refused to decide, and who should**

- <a id="refusal-1"></a>**Whether this change resolves issue #2234 for users of the released 3.1.x packages** *Who:* analyzer area owner / maintainers choosing the target branch (raised by Claude) <details><summary>why</summary>The facts and tests were produced against base 32258fdb (develop line), which does not contain the 3.1.1 regression. Nothing was built or tested against master/v3.1.x, so whether the change applies there and fixes the reported symptom is not established (and C1 suggests it would not on its own).</details>
- <a id="refusal-5"></a>**Runtime library behavior (src/MessagePack) and net472/netstandard builds** *Who:* Area owner (raised by Nemotron) <details><summary>why</summary>Not run; the runtime library was not modified and only net8.0 was built.</details>
- <a id="refusal-6"></a>**Security review of analyzer deserializing untrusted input** *Who:* Security reviewer (raised by Nemotron) <details><summary>why</summary>No security-specific evidence was provided and no security analysis was performed.</details>
- Whether [N1](#chain-REQ-2234-N1), [N2](#chain-REQ-2234-N2) are met: see the trace. *Who:* Toivo

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

<details><summary>4 more risks that do not set the tier</summary>REQ-2234-F1, REQ-2234-F2 already held before this change: met, but not achieved by it. · 3 peripheral refusals (out of scope for this change) are yours too. · Not run: tests.MessagePack.Tests, build.net472/netstandard, benchmarks · Standing pipeline gaps: other-targets, runtime-perf, semantic-intent, provenance</details>

**Toivo signs** (required; accept, reject, request-changes)

```
countersign sign 2234 --as Toivo --decision … --note "…"
```

<details><summary>And rate the 9 verified findings (full command)</summary>

One `--finding` flag each: `accepted` (real), `rejected` (a false positive) or `unsure`, optionally `:reason`. A finding without a flag is recorded as `unrated`.

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

</details>

<details><summary>What your signature says</summary>

> I, Toivo, have read what was checked and by whom, what was not checked and why, and the residual risk listed in this pack, and I own this decision.

It covers the sha256 of this pack's canonical JSON, the decision, your verdict on each finding, the time and the signer, and is appended to the hash-chained ledger.

</details>

<a id="supply-chain"></a>**Supply chain (from the build):** deps.delta pass: no package added or moved, 0 new advisories (6 already on base); build.egress pass; CRACI trace pass

<details><summary>Supply-chain detail</summary>

`deps.delta` **pass**: 238 packages on head (238 on base) across 30 projects; 0 added, 0 version changes, 0 removed; 0 new vulnerability hits (6 already on base)

- Already on base (6): Microsoft.NETCore.Jit 1.0.2 high GHSA-xcvr-qv8h-m7xw, NuGet.Packaging 6.8.0 critical GHSA-68w7-72jg-6qpp, NuGet.Packaging 6.8.0 low GHSA-g4vj-cjjj-v7hg, NuGet.Protocol 6.8.0 low GHSA-g4vj-cjjj-v7hg, System.Formats.Asn1 6.0.0 high GHSA-447r-wph3-92pm, System.Text.Encodings.Web 4.5.0 critical GHSA-ghhp-997w-qr28
- SBOMs (CycloneDX): `evidence/base/sbom.cdx.json`, `evidence/2234/sbom.cdx.json`
- `build.egress` **pass**: default deny, presets ['github'], 13 TLS host patterns; run https://github.com/Zawaer/countersign/actions/runs/43559084959; policy sha256 `31fafb855e98`
- `craci.network` **pass**: 220 connections to 13 hosts, 0 proxy violations: builds.dotnet.microsoft.com (468.2 MB), api.nuget.org (283.5 MB), github.com (19.3 MB), codeload.github.com (4.2 MB), pkgs.dev.azure.com (0.4 MB), ci.dot.net (44 kB); denied, not counted as the change's: 2928 certificate revocation lookups (CRL/OCSP over plain HTTP: crl3.digicert.com, crl4.digicert.com, ocsp.digicert.com, s.symcb.com, s.symcd.com, ts-crl.ws.symantec.com, ts-ocsp.ws.symantec.com), so package-signature revocation was not checked online; 3 request(s) during toolchain setup, before the change was built (aka.ms); 7 host(s) allowed by a preset or CRACI's own CI-service rule, not a listed TLS host (rules: github-actions-actions.githubusercontent.com, github-actions-cache-results-receiver.actions.githubusercontent.com, recorded-http-api.github.com)

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
- **Claude** says met (2/5 citations verified): [`test SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed passed`](#ev-165dc4a6ea) [`test SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed passed`](#ev-097f9caee8) [`TypeCollector.cs:1383 @head`](#ev-6768fd1ae3) [`TypeCollector.cs:1407 @head`](#ev-337b4ac064) [`TypeCollector.cs:989 @head`](#ev-e5721f8767)
- **Codex** says met (1/2 citations verified): [`test SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed passed`](#ev-097f9caee8) [`check tests.fail_without_fix`](#ev-d78b746a74)
- **Nemotron** says met (2/5 citations verified): [`REQ-2234-F2 text`](#ev-d3c4dd6a49) [`TypeCollector.cs:1383 @head`](#ev-6768fd1ae3) [`TypeCollector.cs:1386 @head`](#ev-76656896d1) [`test SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed passed`](#ev-097f9caee8) [`test SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed passed`](#ev-165dc4a6ea)

<a id="chain-REQ-2234-N1"></a>
#### REQ-2234-N1: **NOT MET**

> The analyzer and generator must not crash on invalid contracts (e.g. duplicate keys) in such types.

- **Claude: not met** (1/4 verified). The duplicate-key and mixed-kind crashes are fixed, and the full suite passes (175/175). But not every invalid contract in such a type is crash-free. The hard cast at line 985 is untouched, and my probe (scratch worktree, SDK 8, not in facts.json) of '[MessagePackObject(SuppressSourceGeneration = true)] public record Cmd([property: Key(null)] string Scope)' still gives AD0001 InvalidCastException (ParameterSyntax to PropertyDeclarationSyntax) at this head. The generator side of the duplicate-key fix has no test in facts.json (the new analyzer tests use CSharpCodeFixVerifier, analyzer only), though my probe showed no CS8785 for duplicate keys at head.
- **Codex: met** (1/2 verified). The full source-generator suite passes, and duplicate-key tests demonstrate that invalid contracts no longer trigger analyzer failure.
- **Nemotron: met** (4/5 verified). The full suite passes with 0 failures on head, and the previously crashing duplicate-key and mixed-key tests now pass instead of throwing analyzer exceptions.
- **Checks:** `build` pass, `tests.full_suite` pass
- **Adjudicator (Gemini, advisory):** Supported by the cited evidence: Claude: Duplicate-string-key analyzer crash is fixed and the 175-test source-generator suite passes (Verified test SuppressSourceGenerationAnalyzerTests.DuplicateStringKeysAreReportedWithoutAnalyzerFailure passes in tests.targeted and tests.full_suite passes (175/175)); Claude: An unguarded cast to PropertyDeclarationSyntax remains at TypeCollector.cs:985 when both int and string keys are null (Verified code quote at src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:985 shows ((PropertyDeclarationSyntax)item.DeclaringSyntaxReferences[0].GetSyntax()).Identifier.GetLocation()); Codex: Duplicate-string-key contracts no longer crash the analyzer and the existing source-generator suite passes (Verified test SuppressSourceGenerationAnalyzerTests.DuplicateStringKeysAreReportedWithoutAnalyzerFailure passes in tests.targeted and tests.full_suite passes (175/175)); Nemotron: Duplicate-int-key analyzer crash is fixed on head and the pipeline repro repro.claude.C2 still fails on head and base while passing on control (Verified test SuppressSourceGenerationAnalyzerTests.DuplicateIntKeysAreReportedWithoutAnalyzerFailure passes in tests.targeted and fails in tests.fail_without_fix, and facts.json repro.claude.C2 confirms failed on head, failed on base, passed on control). Not supported: Claude: Scratch-worktree probe triggers AD0001 InvalidCastException at head and generator probe shows no CS8785 for duplicate keys (Neither scratch-worktree probe nor a generator-side duplicate-key test is in facts.json); Codex: Invalid contracts generally satisfy REQ-2234-N1 without analyzer or generator crashes (Cited evidence only covers DuplicateStringKeysAreReportedWithoutAnalyzerFailure and tests.full_suite; it does not cover null-key positional records (repro.claude.C2 fails on head) or a generator-side invalid-contract test); Nemotron: Named test ReproClaude2234C2Tests.PositionalRecordWithNullKeyDoesNotCrashAnalyzerForSuppressedType fails with AD0001 InvalidCastException and passes on origin/ju26-issue-2283 due to a null-safe lookup (The cited test name is engine_verified: false (not in facts.json), and the specific exception type and control-branch diff are not in the verified evidence). What would settle it: Area-owner ruling on whether REQ-2234-N1 requires fixing the pre-existing TypeCollector.cs:985 cast for positional records with [property: Key(null)] in this change; A test in facts.json covering [MessagePackObject(SuppressSourceGeneration = true)] on a positional record with [property: Key(null)] asserting no AD0001 analyzer crash; A source-generator test in facts.json exercising invalid contracts (e.g. duplicate keys) in a SuppressSourceGeneration = true type and asserting no generator crash (CS8785).
- **What would settle it:** Area-owner ruling on whether REQ-2234-N1 requires fixing the pre-existing TypeCollector.cs:985 cast for positional records with [property: Key(null)] in this change; A test in facts.json covering [MessagePackObject(SuppressSourceGeneration = true)] on a positional record with [property: Key(null)] asserting no AD0001 analyzer crash; A source-generator test in facts.json exercising invalid contracts (e.g. duplicate keys) in a SuppressSourceGeneration = true type and asserting no generator crash (CS8785); A fix, or evidence that refutes Claude's objection

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

Adjudicator **Gemini** (gemini-4-hydrogen, adjudicate-v1), advisory only: it can add reasons, never clear.
- **REQ-2234-N1**: Supported by the cited evidence: Claude: Duplicate-string-key analyzer crash is fixed and the 175-test source-generator suite passes (Verified test SuppressSourceGenerationAnalyzerTests.DuplicateStringKeysAreReportedWithoutAnalyzerFailure passes in tests.targeted and tests.full_suite passes (175/175)); Claude: An unguarded cast to PropertyDeclarationSyntax remains at TypeCollector.cs:985 when both int and string keys are null (Verified code quote at src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:985 shows ((PropertyDeclarationSyntax)item.DeclaringSyntaxReferences[0].GetSyntax()).Identifier.GetLocation()); Codex: Duplicate-string-key contracts no longer crash the analyzer and the existing source-generator suite passes (Verified test SuppressSourceGenerationAnalyzerTests.DuplicateStringKeysAreReportedWithoutAnalyzerFailure passes in tests.targeted and tests.full_suite passes (175/175)); Nemotron: Duplicate-int-key analyzer crash is fixed on head and the pipeline repro repro.claude.C2 still fails on head and base while passing on control (Verified test SuppressSourceGenerationAnalyzerTests.DuplicateIntKeysAreReportedWithoutAnalyzerFailure passes in tests.targeted and fails in tests.fail_without_fix, and facts.json repro.claude.C2 confirms failed on head, failed on base, passed on control). Not supported: Claude: Scratch-worktree probe triggers AD0001 InvalidCastException at head and generator probe shows no CS8785 for duplicate keys (Neither scratch-worktree probe nor a generator-side duplicate-key test is in facts.json); Codex: Invalid contracts generally satisfy REQ-2234-N1 without analyzer or generator crashes (Cited evidence only covers DuplicateStringKeysAreReportedWithoutAnalyzerFailure and tests.full_suite; it does not cover null-key positional records (repro.claude.C2 fails on head) or a generator-side invalid-contract test); Nemotron: Named test ReproClaude2234C2Tests.PositionalRecordWithNullKeyDoesNotCrashAnalyzerForSuppressedType fails with AD0001 InvalidCastException and passes on origin/ju26-issue-2283 due to a null-safe lookup (The cited test name is engine_verified: false (not in facts.json), and the specific exception type and control-branch diff are not in the verified evidence). What would settle it: Area-owner ruling on whether REQ-2234-N1 requires fixing the pre-existing TypeCollector.cs:985 cast for positional records with [property: Key(null)] in this change; A test in facts.json covering [MessagePackObject(SuppressSourceGeneration = true)] on a positional record with [property: Key(null)] asserting no AD0001 analyzer crash; A source-generator test in facts.json exercising invalid contracts (e.g. duplicate keys) in a SuppressSourceGeneration = true type and asserting no generator crash (CS8785).

</details>

<details><summary><b>Full detail</b>: all tier drivers, risk score, every check, areas, not checked, residual risk</summary>

Branch `ju26-issue-2234` (32258fdb..9007cee1), 4 files, +262 -4. Author Stelian Vultur (agent-written: True). Commit: Implementation for #2234 The analyzer does not work if SuppressSourceGeneration = true

Mandate `messagepack-csharp` v6 sha256 `71386aa55974f675`, signature: valid, Toivo

<a id="all-drivers"></a>
#### All tier drivers (tier = strictest)

- ask: verified finding `claude:C1`: major: The issue's 3.1.1 regression is not on this base; the change fixes a different crash
- ask: refused clause `REQ-2234-N1`: not_met: claude: The duplicate-key and mixed-kind crashes are fixed, and the full suite passes (175/175). But not every invalid contract in such a type is crash-free. The hard cast at line 985 is untouched, and my probe (scratch worktree, SDK 8, not in facts.json) of '[MessagePackObject(SuppressSourceGeneration = true)] public record Cmd([property: Key(null)] string Scope)' still gives AD0001 InvalidCastException (ParameterSyntax to PropertyDeclarationSyntax) at this head. The generator side of the duplicate-key fix has no test in facts.json (the new analyzer tests use CSharpCodeFixVerifier, analyzer only), though my probe showed no CS8785 for duplicate keys at head.; reviewers_disagree: claude says not_met, codex says met, nemotron says met; adjudicator_dispute: gemini: supported by cited evidence: claude, claude, codex, nemotron; not supported: claude, codex, nemotron; would settle it: Area-owner ruling on whether REQ-2234-N1 requires fixing the pre-existing TypeCollector.cs:985 cast for positional records with [property: Key(null)] in this change; A test in facts.json covering [MessagePackObject(SuppressSourceGeneration = true)] on a positional record with [property: Key(null)] asserting no AD0001 analyzer crash
- ask: refused clause `REQ-2234-N2`: thin_evidence: codex says met with 0 verified evidence items about the change (of 2 cited; requirement quotes and unclaimed outcomes don't count)
- ask: adjudicator `REQ-2234-N1`: supported by cited evidence: claude, claude, codex, nemotron; not supported: claude, codex, nemotron; would settle it: Area-owner ruling on whether REQ-2234-N1 requires fixing the pre-existing TypeCollector.cs:985 cast for positional records with [property: Key(null)] in this change; A test in facts.json covering [MessagePackObject(SuppressSourceGeneration = true)] on a positional record with [property: Key(null)] asserting no AD0001 analyzer crash
- ask: reviewer refusal `claude`: Whether this change resolves issue #2234 for users of the released 3.1.x packages (The facts and tests were produced against base 32258fdb (develop line), which does not contain the 3.1.1 regression. Nothing was built or tested against master/v3.1.x, so whether the change applies there and fixes the reported symptom is not established (and C1 suggests it would not on its own).)
- ask: reviewer refusal `nemotron`: Runtime library behavior (src/MessagePack) and net472/netstandard builds (Not run; the runtime library was not modified and only net8.0 was built.)
- ask: reviewer refusal `nemotron`: Security review of analyzer deserializing untrusted input (No security-specific evidence was provided and no security analysis was performed.)
- ask: risk score `risk`: score 92.4 (notify>=15, ask>=40, block>=130); largest: failed_checks 50 + area_sensitivity 20 + lines_changed 10.1
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
| tests.mutation | fail | evidence/scripts/mutation.py + dotnet test (one mutant at a time, the targeted filter) 8.0.402 | 8 mutants of the changed source lines: 5 killed, 3 survived; 3 of 6 mutated hunks have a killed mutant; surviving hunks: TypeCollector.cs:1148, TypeCollector.cs:1163-1166, TypeCollector.cs:1179-1182 |
| craci.sbom | pass | CRACI API v1preview1 (https://api.craci.com)  | CRACI's job SBOM: 0 components (none); 0 NuGet, all in our restore graph (242 NuGet packages). CRACI has no NuGet source type, so the facts job reaches NuGet through a TLS connection rule, which CRACI does not inspect for packages: the NuGet graph is recorded by deps.delta, CRACI records the connections (craci.network) |
| craci.network | pass | CRACI API v1preview1 (https://api.craci.com)  | 220 connections to 13 hosts, 0 proxy violations: builds.dotnet.microsoft.com (468.2 MB), api.nuget.org (283.5 MB), github.com (19.3 MB), codeload.github.com (4.2 MB), pkgs.dev.azure.com (0.4 MB), ci.dot.net (44 kB); denied, not counted as the change's: 2928 certificate revocation lookups (CRL/OCSP over plain HTTP: crl3.digicert.com, crl4.digicert.com, ocsp.digicert.com, s.symcb.com, s.symcd.com, ts-crl.ws.symantec.com, ts-ocsp.ws.symantec.com), so package-signature revocation was not checked online; 3 request(s) during toolchain setup, before the change was built (aka.ms); 7 host(s) allowed by a preset or CRACI's own CI-service rule, not a listed TLS host (rules: github-actions-actions.githubusercontent.com, github-actions-cache-results-receiver.actions.githubusercontent.com, recorded-http-api.github.com) |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v6 (71386aa55974)

#### Requirement trace (engine codes)

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-2234-F1 | held_before | claude: met (8/9), codex: met (3/4), nemotron: met (12/13) | build: pass, tests.targeted: pass | held_before |
| REQ-2234-F2 | held_before | claude: met (2/5), codex: met (1/2), nemotron: met (2/5) | build: pass, tests.targeted: pass | held_before |
| REQ-2234-N1 | refused | claude: not_met (1/4), codex: met (1/2), nemotron: met (4/5) | build: pass, tests.full_suite: pass | not_met, reviewers_disagree, adjudicator_dispute |
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

- REQ-2234-N1 not proven: not_met; reviewers_disagree; adjudicator_dispute
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
- Standing gaps of this pipeline: other-targets, runtime-perf, semantic-intent, provenance (see not checked)

<a id="risk"></a>
#### Risk score: 92.4 -> ask

| Factor | Points | Reason |
|---|---:|---|
| area_sensitivity | 20 | most sensitive area touched: generator-analyzer-core (high) |
| files_changed | 4.3 | 4 files (~1.1 per file while small, log-scaled past 80, cap 45) |
| lines_changed | 10.1 | 266 non-generated lines (~4 per 100 lines while small, log-scaled past 100, cap 20; files and lines together at most 45) |
| generated_files | 0.0 | 0 generated files x 0.1 (cap 10) |
| public_api_change | 0 | public_api check: no change |
| source_without_tests | 0 | tests changed alongside source |
| security_sensitive_paths | 0 | none touched |
| fail_without_fix_not_shown | 0 | tests.fail_without_fix: pass |
| reviewer_disagreement | 8 | 1 clause(s) x 8: REQ-2234-N1 |
| failed_checks | 50 | 2 failed check(s) x 25: tests.execution_fail_without_fix, tests.mutation |
| **total** | **92.4** | bands: {'notify': 15, 'ask': 40, 'block': 130} |

Inputs: facts `evidence/2234/facts.json`, requirements `requirements/2234.yaml`, reviews `reviews/2234/claude.json`, `reviews/2234/codex.json`, `reviews/2234/nemotron.json`

</details>

</details>
