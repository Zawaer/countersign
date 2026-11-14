## Countersign: change 2283 is **ASK**, owner **Toivo**

**Agent-written change for #2283: implementation for #2283**

Changes 1 source file (TypeCollector.cs), 1 test file, 2 doc files (+225 -3) on ju26-issue-2283 by Stelian Vultur. Judged against 5 requirement clauses from #2283 (placeholder requirement set, not Tieto's official one).

**Why ask**

1. Claude found a verified major issue: Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic ([evidence](#f-claude-C1))
2. 2 of 5 requirement clauses not proven. ([evidence](#chain-REQ-2283-F2)) <details><summary>more</summary>REQ-2283-F2: The tests supporting REQ-2283-F2 (the new tests its reviewers cite: ClosedGenericRecordStruct_FromMetadataReference, ClosedGenericStruct_FromMetadataReference) kill no mutant on its lines (TypeCollector.cs:239, TypeCollector.cs:985) in tests.mutation; no test kills any of the 2 mutant(s) there (+1 more)</details>
3. The adjudicator (Gemini) found the evidence on REQ-2283-N1, finding:claude:C1 disputed ([evidence](#panel))

<sub>All 15 tier drivers are under Full detail.</sub>

**Requirement trace**

| Status | Clause | Why |
|---|---|---|
| **PROVEN** | [F1](#chain-REQ-2283-F1) | All 3 reviewers say met (12 verified citations); build, tests.targeted pass |
| **REFUSED** | [F2](#chain-REQ-2283-F2) | Its tests kill none of the 2 planted mutants on its lines <details><summary>more</summary>The tests supporting REQ-2283-F2 (the new tests its reviewers cite: ClosedGenericRecordStruct_FromMetadataReference, ClosedGenericStruct_FromMetadataReference) kill no mutant on its lines (TypeCollector.cs:239, TypeCollector.cs:985) in tests.mutation; no test kills any of the 2 mutant(s) there. Whole change: tests kill 2 of 8 planted mutants; survivors at TypeCollector.cs:239, TypeCollector.cs:985, TypeCollector.cs:1429-1434.</details> |
| **PROVEN** | [F3](#chain-REQ-2283-F3) | All 3 reviewers say met (10 verified citations); build, tests.targeted pass |
| **NOT MET** | [N1](#chain-REQ-2283-N1) | Claude says not met (Codex and Nemotron: met) <details><summary>more</summary>Codex said met without verified evidence; the adjudicator disputes it</details> |
| **PROVEN** | [N2](#chain-REQ-2283-N2) | All 3 reviewers say met (8 verified citations); build, tests.fail_without_fix pass |

<details><summary>Gemini on N1: backs 1 of 2 claims for Claude's 'not met', 2 of 4 for 'met' (advisory)</summary>

The existing 170-test suite passes, but facts.json repro.claude.C1 confirms a regression on head when an in-compilation type is reached through a metadata generic member.

**Backed by the cited evidence**

- **Codex**: The existing source-generator test suite passes in full (170/170). (facts.json tests.full_suite passes with 170 passed, 0 failed, and 0 newly failing tests.)
- **Nemotron**: The full source-generator suite passes on head with no newly failing tests. (facts.json tests.full_suite confirms 170 passed, 0 failed, and no failures on head or base.)
- **Claude**: The existing test suite passes, and ReportIfLocatedInCompilation filters out diagnostics not located in a syntax tree of the current compilation, including when TypeMustBeMessagePackObject uses a metadata callerSymbol.Locations[0]. (facts.json tests.full_suite confirms 170/170 pass; verified quotes at TypeCollector.cs:1446 and 1341 show the IsInSource + ContainsSyntaxTree check and callerSymbol.Locations[0] usage, and facts.json repro.claude.C1 confirms the scenario passes on base and fails on head.)

**Not backed**

- **Codex**: All existing analyzer diagnostics for types declared in the current compilation keep working unchanged. (tests.full_suite only covers the 170 existing tests and does not cover an in-compilation type reached via a metadata generic member, where facts.json repro.claude.C1 shows behavior changed from base to head.)
- **Nemotron**: All existing analyzer diagnostics for types declared in the current compilation keep working unchanged. (tests.full_suite only verifies the existing test suite and does not rule out regressions in uncovered cases such as repro.claude.C1.)
- **Claude**: class Item<T> worked on base per the issue table. (The cited issue quote '| class Item<T> | ok |' is unverified offline and supports nothing.)

**What would settle it**

- Area owner ruling on whether REQ-2283-N1 covers uncovered cross-assembly generic scenarios (repro.claude.C1) or is scoped to the existing test suite.
- An automated test asserting whether MsgPack003 is reported when a metadata generic member (Lib.Item<T>.Content) is instantiated with an in-compilation type lacking [MessagePackObject].

</details>

**What the AI found**

- **major** [Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic](#f-claude-C1) (Claude C1) [`TypeCollector.cs:1446 @head`](#ev-6afda546ae) [`TypeCollector.cs:1341 @head`](#ev-03c1f89f96)
- **minor** [BothStringAndIntKeyAreNull is now silently suppressed for positional record properties in source](#f-claude-C2) (Claude C2) [`TypeCollector.cs:1434 @head`](#ev-532df5c2da) [`TypeCollector.cs:985 @head`](#ev-ddf4848149)
- **info** [Fix treats the symptom location; metadata struct backing fields are still walked as members](#f-claude-C3) (Claude C3) [`TypeCollector.cs:1077 @head`](#ev-cf1d452cfa)

<details><summary>Gemini on Claude C1: backs 1 of 2 of its claims (advisory)</summary>

The location-filtering behavior and base-vs-head behavioral difference are supported by TypeCollector.cs:1341,1446 and facts.json repro.claude.C1.

**Backed by the cited evidence**

- **Claude**: ReportIfLocatedInCompilation drops diagnostics whose location is not in a syntax tree of the current compilation, causing MsgPack003 (located at callerSymbol.Locations[0]) to be dropped when callerSymbol is in metadata even if the target type is in the current compilation. (Verified quotes at TypeCollector.cs:1446 and TypeCollector.cs:1341-1345 show the filter and location selection, and facts.json repro.claude.C1 reproduces the failure on head while passing on base.)

**Not backed**

- **Claude**: Roslyn permits analyzers to report Location.None and metadata locations, and the generator still emits App.R.g.cs and a formatter for Lib.Item`1 causing a runtime failure. (TypeCollector.cs:1442 confirms the doc comment text, but no Roslyn specification/test or generated-output inspection is included in the cited evidence to verify Roslyn's rules or the exact emitted code.)

**What would settle it**

- An automated test in MessagePack.SourceGenerator.Tests matching repro.claude.C1 (metadata generic class Lib.Item<T> with an in-compilation type Foo lacking [MessagePackObject]) asserting that MsgPack003 is reported at Foo's source location or Location.None rather than dropped.
- Confirmation of whether Roslyn analyzer rules in this repo permit reporting MsgPack003 at formattedType.Locations[0] (when in source) or Location.None when callerSymbol is from metadata.

</details>

<a id="refused"></a>**What the AI refused to decide, and who should**

- <a id="refusal-5"></a>**Whether the placeholder requirement set matches the upstream issue #2283 intent** *Who:* area owner or maintainer (raised by Nemotron) <details><summary>why</summary>The requirement set is marked official: false and derived from the issue; the issue body itself was not provided, so I cannot verify the requirements capture the issue fully.</details>
- Whether [F2](#chain-REQ-2283-F2), [N1](#chain-REQ-2283-N1) are met: see the trace. *Who:* Toivo

<details id="refused-peripheral"><summary>4 peripheral refusals (out of scope for this change)</summary><a id="refusal-1"></a>Whether the resolver generated for a project consuming a closed generic struct from a referenced assembly serializes it correctly at run time (and whether emitting a second formatter for Lib.Item`1 in the consuming assembly is intended) (Claude) · <a id="refusal-2"></a>Whether the documented behaviour change (diagnostics for referenced types are reported only by the defining project) is acceptable product behaviour (Claude) · <a id="refusal-3"></a>Execution-test behavior under a compiler that loads the generator (Codex) · <a id="refusal-4"></a>End-to-end execution of the generator in consumer projects (tests.execution: MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) (Nemotron)</details>

**Not checked, and why**

- `tests.execution`: SDK 8.0.402 ships Roslyn 4.11 but MessagePack.SourceGenerator references Microsoft.CodeAnalysis 4.12.0 <details><summary>more</summary>so csc refuses to load the generator (warning CS9057) and projects that consume it as an analyzer (tests/MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) fail to compile (CS0117 'GeneratedMessagePackResolver' does not contain 'Instance'). This also happens on base 32258fdb, so it is an environment/toolchain mismatch, not caused by the change. Needs an SDK with Roslyn &gt;= 4.12 (e.g. .NET SDK 9.0.1xx); swapping in a newer compiler toolset was not permitted in this run.</details>
- `tests.MessagePack.Tests`: runtime library src/MessagePack not modified by the change; suite not run
- `build.net472/netstandard`: only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks`: no runtime serialization hot path touched (generator/analyzer only)
- Standing pipeline gaps: `other-targets`, `runtime-perf`, `semantic-intent`, `provenance`

**Residual risk you accept by signing**

- Open major finding: Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic
- Not proven by the AI: REQ-2283-F2, REQ-2283-N1. Signing means you judge them yourself.
- 1 question the AI declined to decide (listed above) are yours.

<details><summary>3 more risks that do not set the tier</summary>4 peripheral refusals (out of scope for this change) are yours too. · Not run: tests.execution, tests.MessagePack.Tests, build.net472/netstandard, benchmarks · Standing pipeline gaps: other-targets, runtime-perf, semantic-intent, provenance</details>

**Toivo signs** (required; accept, reject, request-changes)

```
countersign sign 2283 --as Toivo --decision … --note "…"
```

<details><summary>And rate the 3 verified findings (full command)</summary>

One `--finding` flag each: `accepted` (real), `rejected` (a false positive) or `unsure`, optionally `:reason`. A finding without a flag is recorded as `unrated`.

- `claude:C1` (major): Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic
- `claude:C2` (minor): BothStringAndIntKeyAreNull is now silently suppressed for positional record properties in source
- `claude:C3` (info): Fix treats the symptom location; metadata struct backing fields are still walked as members

```
countersign sign 2283 --as Toivo --decision <accept|reject|request-changes> --note "..." \
  --finding claude:C1=<accepted|rejected|unsure> \
  --finding claude:C2=<accepted|rejected|unsure> \
  --finding claude:C3=<accepted|rejected|unsure>
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
- SBOMs (CycloneDX): `evidence/base/sbom.cdx.json`, `evidence/2283/sbom.cdx.json`
- `build.egress` **pass**: default deny, presets ['github'], 13 TLS host patterns; run https://github.com/Zawaer/countersign/actions/runs/43559078089; policy sha256 `31fafb855e98`
- `craci.network` **pass**: 183 connections to 13 hosts, 0 proxy violations: builds.dotnet.microsoft.com (468.2 MB), api.nuget.org (271.4 MB), github.com (19.3 MB), codeload.github.com (4.2 MB), pkgs.dev.azure.com (0.2 MB), ci.dot.net (44 kB); denied, not counted as the change's: 2904 certificate revocation lookups (CRL/OCSP over plain HTTP: crl3.digicert.com, crl4.digicert.com, ocsp.digicert.com, s.symcb.com, s.symcd.com, ts-crl.ws.symantec.com, ts-ocsp.ws.symantec.com), so package-signature revocation was not checked online; 3 request(s) during toolchain setup, before the change was built (aka.ms); 7 host(s) allowed by a preset or CRACI's own CI-service rule, not a listed TLS host (rules: github-actions-actions.githubusercontent.com, github-actions-cache-results-receiver.actions.githubusercontent.com, recorded-http-api.github.com)

</details>

<details><summary><b>Where the trust comes from</b> (per requirement clause)</summary>

<a id="chain-REQ-2283-F1"></a>
#### REQ-2283-F1: **PROVEN**

> Building a project whose [MessagePackObject] type has a member of a closed generic value type defined in a referenced assembly must not crash the source generator (no CS8785) and must produce a generated resolver.

- **Checks passed:** `build` pass, `tests.targeted` pass
- **Fails without the fix:** [`ClosedGenericRecordStruct_FromMetadataReference`](#ev-751fd9609c), [`ClosedGenericStruct_FromMetadataReference`](#ev-f073740910), [`ClosedGenericStruct_FromMetadataReference_UnkeyedMember`](#ev-72235a3098)
- **Claude** says met (5/8 citations verified): [`TypeCollector.cs:1077 @base`](#ev-600c5196b9) [`TypeCollector.cs:1077 @head`](#ev-e2b1723b1a) [`TypeCollector.cs:651 @head`](#ev-8dd72e446f) [`GenericsFormatterTests.cs:658 @head`](#ev-e27f824d96) [`test ClosedGenericRecordStruct_FromMetadataReference passed`](#ev-751fd9609c) [`test ClosedGenericRecordStruct_FromMetadataReference failed`](#ev-bf91cd8726) [`check tests.fail_without_fix`](#ev-d78b746a74) [`REQ-2283-F1 text`](#ev-19107a84ed)
- **Codex** says met (2/3 citations verified): [`test ClosedGenericStruct_FromMetadataReference passed`](#ev-f073740910) [`check tests.fail_without_fix`](#ev-d78b746a74) [`TypeCollector.cs:1446 @head`](#ev-6afda546ae)
- **Nemotron** says met (5/5 citations verified): [`test ClosedGenericStruct_FromMetadataReference passed`](#ev-f073740910) [`test ClosedGenericRecordStruct_FromMetadataReference passed`](#ev-751fd9609c) [`test ClosedGenericStruct_FromMetadataReference_UnkeyedMember passed`](#ev-72235a3098) [`TypeCollector.cs:1077 @head`](#ev-463700b774) [`check tests.fail_without_fix pass`](#ev-62faeb2508)

<a id="chain-REQ-2283-F2"></a>
#### REQ-2283-F2: **REFUSED**

> The MsgPack00x analyzer must not throw (no AD0001) for the same input.

- **Claude: met** (4/5 verified). The new tests run MsgPack00xMessagePackAnalyzer through VerifyCS expecting zero diagnostics; on base all three fail with AD0001 IndexOutOfRangeException at TypeCollector.GetObjectInfo (facts fail_without_fix errors), at head they pass. The other hard index the issue names (BothStringAndIntKeyAreNull cast) is also replaced by a null-safe helper.
- **Codex: met** (2/3 verified). The failing-without-fix evidence records AD0001 for the new metadata-reference cases on base source, while all three cases pass with the fix.
- **Nemotron: met** (4/4 verified). On base the same three tests failed with AD0001 (analyzer threw IndexOutOfRangeException); on head they pass with zero diagnostics because member-location access is now null-safe and diagnostics are filtered before reporting.
- **Checks:** `build` pass, `tests.targeted` pass
- **What would settle it:** A test that fails on a mutant of the lines this clause depends on (tests.mutation)

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

- **Claude: not met** (1/5 verified). The existing suite passes (170/170, no new failures), so the parenthetical part holds, but the clause's main statement does not: the location filter also drops diagnostics about types declared in the current compilation when the reporting location is a metadata member. My probe (scratch worktree, SDK 8, not in facts.json): metadata generic class Lib.Item<T> with [Key(0)] T Content, used as Item<Foo> where App.Foo lacks [MessagePackObject]; base reports MsgPack003 'Type must be marked with MessagePackObjectAttribute: Item.Content', head reports nothing. Item<T> as a class did not crash on base (issue table: 'class Item<T> | ok'), so this is a regression in a configuration that worked before. The existing suite does not cover it.
- **Codex: met** (0/1 verified). The source-generator test suite passes in full after the change.
- **Nemotron: met** (1/1 verified). Full suite on head: 170 passed, 0 failed, with no failures that also fail on base and no new failures, so existing analyzer diagnostics for in-compilation types are unchanged.
- **Checks:** `build` pass, `tests.full_suite` pass
- **Adjudicator (Gemini, advisory):** Supported by the cited evidence: Codex: The existing source-generator test suite passes in full (170/170). (facts.json tests.full_suite passes with 170 passed, 0 failed, and 0 newly failing tests.); Nemotron: The full source-generator suite passes on head with no newly failing tests. (facts.json tests.full_suite confirms 170 passed, 0 failed, and no failures on head or base.); Claude: The existing test suite passes, and ReportIfLocatedInCompilation filters out diagnostics not located in a syntax tree of the current compilation, including when TypeMustBeMessagePackObject uses a metadata callerSymbol.Locations[0]. (facts.json tests.full_suite confirms 170/170 pass; verified quotes at TypeCollector.cs:1446 and 1341 show the IsInSource + ContainsSyntaxTree check and callerSymbol.Locations[0] usage, and facts.json repro.claude.C1 confirms the scenario passes on base and fails on head.). Not supported: Codex: All existing analyzer diagnostics for types declared in the current compilation keep working unchanged. (tests.full_suite only covers the 170 existing tests and does not cover an in-compilation type reached via a metadata generic member, where facts.json repro.claude.C1 shows behavior changed from base to head.); Nemotron: All existing analyzer diagnostics for types declared in the current compilation keep working unchanged. (tests.full_suite only verifies the existing test suite and does not rule out regressions in uncovered cases such as repro.claude.C1.); Claude: class Item<T> worked on base per the issue table. (The cited issue quote '| class Item<T> | ok |' is unverified offline and supports nothing.). What would settle it: Area owner ruling on whether REQ-2283-N1 covers uncovered cross-assembly generic scenarios (repro.claude.C1) or is scoped to the existing test suite.; An automated test asserting whether MsgPack003 is reported when a metadata generic member (Lib.Item<T>.Content) is instantiated with an in-compilation type lacking [MessagePackObject]..
- **What would settle it:** Area owner ruling on whether REQ-2283-N1 covers uncovered cross-assembly generic scenarios (repro.claude.C1) or is scoped to the existing test suite.; An automated test asserting whether MsgPack003 is reported when a metadata generic member (Lib.Item<T>.Content) is instantiated with an in-compilation type lacking [MessagePackObject].; A fix, or evidence that refutes Claude's objection; Codex citing evidence the engine can verify

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
| REQ-2283-F2 | met | met | met | **refused** |
| REQ-2283-F3 | met | met | met | **proven** |
| REQ-2283-N1 | not met | met | met | **not met** |
| REQ-2283-N2 | met | met | met | **proven** |

- **Claude** (claude-opus-5-5, Anthropic): citations 32 verified / 2 rejected; findings 3 verified / 0 rejected; 2 refusals. Only Claude raised: [C1](#f-claude-C1) major Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic, [C2](#f-claude-C2) minor BothStringAndIntKeyAreNull is now silently suppressed for positional record properties in source, [C3](#f-claude-C3) info Fix treats the symptom location; metadata struct backing fields are still walked as members
- **Codex** (GPT-6, OpenAI): citations 12 verified / 0 rejected; findings 0 verified / 0 rejected; 1 refusals.
- **Nemotron** (nvidia/nemotron-3.5-super-vl-120b-a12b, NVIDIA): citations 18 verified / 0 rejected; findings 0 verified / 0 rejected; 2 refusals.

Adjudicator **Gemini** (gemini-4-hydrogen, adjudicate-v1), advisory only: it can add reasons, never clear.
- **REQ-2283-N1**: Supported by the cited evidence: Codex: The existing source-generator test suite passes in full (170/170). (facts.json tests.full_suite passes with 170 passed, 0 failed, and 0 newly failing tests.); Nemotron: The full source-generator suite passes on head with no newly failing tests. (facts.json tests.full_suite confirms 170 passed, 0 failed, and no failures on head or base.); Claude: The existing test suite passes, and ReportIfLocatedInCompilation filters out diagnostics not located in a syntax tree of the current compilation, including when TypeMustBeMessagePackObject uses a metadata callerSymbol.Locations[0]. (facts.json tests.full_suite confirms 170/170 pass; verified quotes at TypeCollector.cs:1446 and 1341 show the IsInSource + ContainsSyntaxTree check and callerSymbol.Locations[0] usage, and facts.json repro.claude.C1 confirms the scenario passes on base and fails on head.). Not supported: Codex: All existing analyzer diagnostics for types declared in the current compilation keep working unchanged. (tests.full_suite only covers the 170 existing tests and does not cover an in-compilation type reached via a metadata generic member, where facts.json repro.claude.C1 shows behavior changed from base to head.); Nemotron: All existing analyzer diagnostics for types declared in the current compilation keep working unchanged. (tests.full_suite only verifies the existing test suite and does not rule out regressions in uncovered cases such as repro.claude.C1.); Claude: class Item<T> worked on base per the issue table. (The cited issue quote '| class Item<T> | ok |' is unverified offline and supports nothing.). What would settle it: Area owner ruling on whether REQ-2283-N1 covers uncovered cross-assembly generic scenarios (repro.claude.C1) or is scoped to the existing test suite.; An automated test asserting whether MsgPack003 is reported when a metadata generic member (Lib.Item<T>.Content) is instantiated with an in-compilation type lacking [MessagePackObject]..
- **finding:claude:C1**: Supported by the cited evidence: Claude: ReportIfLocatedInCompilation drops diagnostics whose location is not in a syntax tree of the current compilation, causing MsgPack003 (located at callerSymbol.Locations[0]) to be dropped when callerSymbol is in metadata even if the target type is in the current compilation. (Verified quotes at TypeCollector.cs:1446 and TypeCollector.cs:1341-1345 show the filter and location selection, and facts.json repro.claude.C1 reproduces the failure on head while passing on base.). Not supported: Claude: Roslyn permits analyzers to report Location.None and metadata locations, and the generator still emits App.R.g.cs and a formatter for Lib.Item`1 causing a runtime failure. (TypeCollector.cs:1442 confirms the doc comment text, but no Roslyn specification/test or generated-output inspection is included in the cited evidence to verify Roslyn's rules or the exact emitted code.). What would settle it: An automated test in MessagePack.SourceGenerator.Tests matching repro.claude.C1 (metadata generic class Lib.Item<T> with an in-compilation type Foo lacking [MessagePackObject]) asserting that MsgPack003 is reported at Foo's source location or Location.None rather than dropped.; Confirmation of whether Roslyn analyzer rules in this repo permit reporting MsgPack003 at formattedType.Locations[0] (when in source) or Location.None when callerSymbol is from metadata..

</details>

<details><summary><b>Full detail</b>: all tier drivers, risk score, every check, areas, not checked, residual risk</summary>

Branch `ju26-issue-2283` (32258fdb..9df83c38), 4 files, +225 -3. Author Stelian Vultur (agent-written: True). Commit: implementation for #2283

Mandate `messagepack-csharp` v6 sha256 `71386aa55974f675`, signature: valid, Toivo

<a id="all-drivers"></a>
#### All tier drivers (tier = strictest)

- ask: verified finding `claude:C1`: major: Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic (reproduced by the pipeline (repro.claude.C1))
- ask: refused clause `REQ-2283-F2`: tests_kill_no_mutant: the tests supporting REQ-2283-F2 (the new tests its reviewers cite: ClosedGenericRecordStruct_FromMetadataReference, ClosedGenericStruct_FromMetadataReference) kill no mutant on its lines (TypeCollector.cs:239, TypeCollector.cs:985) in tests.mutation; no test kills any of the 2 mutant(s) there
- ask: refused clause `REQ-2283-N1`: not_met: claude: The existing suite passes (170/170, no new failures), so the parenthetical part holds, but the clause's main statement does not: the location filter also drops diagnostics about types declared in the current compilation when the reporting location is a metadata member. My probe (scratch worktree, SDK 8, not in facts.json): metadata generic class Lib.Item<T> with [Key(0)] T Content, used as Item<Foo> where App.Foo lacks [MessagePackObject]; base reports MsgPack003 'Type must be marked with MessagePackObjectAttribute: Item.Content', head reports nothing. Item<T> as a class did not crash on base (issue table: 'class Item<T> | ok'), so this is a regression in a configuration that worked before. The existing suite does not cover it.; reviewers_disagree: claude says not_met, codex says met, nemotron says met; thin_evidence: codex says met with 0 verified evidence items about the change (of 1 cited; requirement quotes and unclaimed outcomes don't count); adjudicator_dispute: gemini: supported by cited evidence: codex, nemotron, claude; not supported: codex, nemotron, claude; would settle it: Area owner ruling on whether REQ-2283-N1 covers uncovered cross-assembly generic scenarios (repro.claude.C1) or is scoped to the existing test suite.; An automated test asserting whether MsgPack003 is reported when a metadata generic member (Lib.Item<T>.Content) is instantiated with an in-compilation type lacking [MessagePackObject].
- ask: adjudicator `REQ-2283-N1`: supported by cited evidence: codex, nemotron, claude; not supported: codex, nemotron, claude; would settle it: Area owner ruling on whether REQ-2283-N1 covers uncovered cross-assembly generic scenarios (repro.claude.C1) or is scoped to the existing test suite.; An automated test asserting whether MsgPack003 is reported when a metadata generic member (Lib.Item<T>.Content) is instantiated with an in-compilation type lacking [MessagePackObject].
- ask: adjudicator `finding:claude:C1`: supported by cited evidence: claude; not supported: claude; would settle it: An automated test in MessagePack.SourceGenerator.Tests matching repro.claude.C1 (metadata generic class Lib.Item<T> with an in-compilation type Foo lacking [MessagePackObject]) asserting that MsgPack003 is reported at Foo's source location or Location.None rather than dropped.; Confirmation of whether Roslyn analyzer rules in this repo permit reporting MsgPack003 at formattedType.Locations[0] (when in source) or Location.None when callerSymbol is from metadata.
- ask: reviewer refusal `nemotron`: Whether the placeholder requirement set matches the upstream issue #2283 intent (The requirement set is marked official: false and derived from the issue; the issue body itself was not provided, so I cannot verify the requirements capture the issue fully.)
- ask: risk score `risk`: score 66.0 (notify>=15, ask>=40, block>=130); largest: failed_checks 25 + area_sensitivity 20 + lines_changed 8.7
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
| build.egress | pass | CRACI network policy (cracicorp/setup@v1) + job log scan  | built on CRACI under a deny-by-default policy: only 13 TLS host patterns on ports 443 (github.com, codeload.github.com, objects.githubusercontent.com, api.nuget.org, *.nuget.org, pkgs.dev.azure.com, ...); presets ['github']; no blocked connection in 19 logs; every NuGet feed the head declares is inside the policy |
| tests.mutation | fail | evidence/scripts/mutation.py + dotnet test (one mutant at a time, the targeted filter) 8.0.402 | 8 mutants of the changed source lines: 2 killed, 6 survived; 1 of 4 mutated hunks have a killed mutant; surviving hunks: TypeCollector.cs:239, TypeCollector.cs:985, TypeCollector.cs:1429-1434; 1 hunks not mutated |
| craci.sbom | pass | CRACI API v1preview1 (https://api.craci.com)  | CRACI's job SBOM: 0 components (none); 0 NuGet, all in our restore graph (242 NuGet packages). CRACI has no NuGet source type, so the facts job reaches NuGet through a TLS connection rule, which CRACI does not inspect for packages: the NuGet graph is recorded by deps.delta, CRACI records the connections (craci.network) |
| craci.network | pass | CRACI API v1preview1 (https://api.craci.com)  | 183 connections to 13 hosts, 0 proxy violations: builds.dotnet.microsoft.com (468.2 MB), api.nuget.org (271.4 MB), github.com (19.3 MB), codeload.github.com (4.2 MB), pkgs.dev.azure.com (0.2 MB), ci.dot.net (44 kB); denied, not counted as the change's: 2904 certificate revocation lookups (CRL/OCSP over plain HTTP: crl3.digicert.com, crl4.digicert.com, ocsp.digicert.com, s.symcb.com, s.symcd.com, ts-crl.ws.symantec.com, ts-ocsp.ws.symantec.com), so package-signature revocation was not checked online; 3 request(s) during toolchain setup, before the change was built (aka.ms); 7 host(s) allowed by a preset or CRACI's own CI-service rule, not a listed TLS host (rules: github-actions-actions.githubusercontent.com, github-actions-cache-results-receiver.actions.githubusercontent.com, recorded-http-api.github.com) |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v6 (71386aa55974)

#### Requirement trace (engine codes)

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-2283-F1 | proven | claude: met (5/8), codex: met (2/3), nemotron: met (5/5) | build: pass, tests.targeted: pass | - |
| REQ-2283-F2 | refused | claude: met (4/5), codex: met (2/3), nemotron: met (4/4) | build: pass, tests.targeted: pass | tests_kill_no_mutant |
| REQ-2283-F3 | proven | claude: met (4/4), codex: met (2/3), nemotron: met (4/4) | build: pass, tests.targeted: pass | - |
| REQ-2283-N1 | refused | claude: not_met (1/5), codex: met (0/1), nemotron: met (1/1) | build: pass, tests.full_suite: pass | not_met, reviewers_disagree, thin_evidence, adjudicator_dispute |
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

- REQ-2283-F2 not proven: tests_kill_no_mutant
- REQ-2283-N1 not proven: not_met; reviewers_disagree; thin_evidence; adjudicator_dispute
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
- Standing gaps of this pipeline: other-targets, runtime-perf, semantic-intent, provenance (see not checked)

<a id="risk"></a>
#### Risk score: 66.0 -> ask

| Factor | Points | Reason |
|---|---:|---|
| area_sensitivity | 20 | most sensitive area touched: generator-analyzer-core (high) |
| files_changed | 4.3 | 4 files (~1.1 per file while small, log-scaled past 80, cap 45) |
| lines_changed | 8.7 | 228 non-generated lines (~4 per 100 lines while small, log-scaled past 100, cap 20; files and lines together at most 45) |
| generated_files | 0.0 | 0 generated files x 0.1 (cap 10) |
| public_api_change | 0 | public_api check: no change |
| source_without_tests | 0 | tests changed alongside source |
| security_sensitive_paths | 0 | none touched |
| fail_without_fix_not_shown | 0 | tests.fail_without_fix: pass |
| reviewer_disagreement | 8 | 1 clause(s) x 8: REQ-2283-N1 |
| failed_checks | 25 | 1 failed check(s) x 25: tests.mutation |
| **total** | **66.0** | bands: {'notify': 15, 'ask': 40, 'block': 130} |

Inputs: facts `evidence/2283/facts.json`, requirements `requirements/2283.yaml`, reviews `reviews/2283/claude.json`, `reviews/2283/codex.json`, `reviews/2283/nemotron.json`

</details>
