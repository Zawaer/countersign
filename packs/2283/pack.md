# Evidence pack: change 2283

**Recommended tier: ASK** · owner **Toivo** · risk score 57.1

Branch `ju26-issue-2283` (32258fdb..9df83c38), 4 files, +225 -3. Author Stelian Vultur (agent-written: True). Commit: implementation for #2283

Mandate `messagepack-csharp` v1 sha256 `ef0e95521f7e364a`, signature: valid, Toivo

## Why this tier

- **ask** from refused clause `REQ-2283-F1`: reviewers_disagree: claude says met, codex says cannot_determine; cannot_determine: codex: The added test file has generic formatter tests, but the inspected test inputs do not establish the required referenced-assembly case or verify a generated resolver for it.
- **ask** from refused clause `REQ-2283-F2`: reviewers_disagree: claude says met, codex says cannot_determine; cannot_determine: codex: The reviewed test input does not exercise the same type from a referenced assembly through the MsgPack00x analyzer.
- **ask** from refused clause `REQ-2283-N1`: cannot_determine: claude: MessagePack.SourceGenerator.Tests (net8.0) passes on head with 170/170, but the execution test projects did not build in my environment (a pre-existing file fails too), I did not run net472, and the new global location filter can in principle drop an existing diagnostic whose location is null (finding C2).; cannot_determine: codex: The changed diagnostic forwarding and location handling plausibly preserve current-compilation diagnostics, but no suite results or regression-test outcomes are available here.
- **ask** from refused clause `REQ-2283-N2`: reviewers_disagree: claude says met, codex says cannot_determine; cannot_determine: codex: The inspected added tests do not establish that the required referenced-assembly scenario is covered or that those tests fail without the fix, and no deterministic test-check results were available.
- **ask** from reviewer refusal `claude`: No regressions across the full test suite (execution tests, net472 target, MessagePack.Tests) (MessagePack.SourceGenerator.ExecutionTests and MapModeExecutionTests failed to compile in my environment with CS0117 in a pre-existing file (GeneratedCompositeResolverTests.cs, 'MyGeneratedCompositeResolver' does not contain a definition for 'Instance'), which points to an environment/build-order issue, not this change. I only ran SourceGenerator.Tests on net8.0.)
- **ask** from reviewer refusal `claude`: Behaviour in the IDE with project-to-project references (CompilationReference symbols) (Needs runtime behaviour in a workspace host; no test covers it and I did not build such a scenario.)
- **ask** from reviewer refusal `claude`: Whether the MsgPack018 null-location path (C2) is reachable in practice (Depends on member enumeration order over metadata base types; I would have to construct and run a scenario I did not run.)
- **ask** from reviewer refusal `codex`: Referenced-assembly generic value type reproduction, analyzer behavior, and whether tests fail without the fix (The inspected test cases do not demonstrate this issue-specific scenario, and no facts.json or test run results were available to establish runtime/build behavior.)
- **ask** from risk score `risk`: score 57.1 (notify>=15, ask>=40, block>=130); largest: reviewer_disagreement 24 + area_sensitivity 20 + lines_changed 9.1

<details><summary>All tier drivers</summary>

- ask: refused clause `REQ-2283-F1`: reviewers_disagree: claude says met, codex says cannot_determine; cannot_determine: codex: The added test file has generic formatter tests, but the inspected test inputs do not establish the required referenced-assembly case or verify a generated resolver for it.
- ask: refused clause `REQ-2283-F2`: reviewers_disagree: claude says met, codex says cannot_determine; cannot_determine: codex: The reviewed test input does not exercise the same type from a referenced assembly through the MsgPack00x analyzer.
- ask: refused clause `REQ-2283-N1`: cannot_determine: claude: MessagePack.SourceGenerator.Tests (net8.0) passes on head with 170/170, but the execution test projects did not build in my environment (a pre-existing file fails too), I did not run net472, and the new global location filter can in principle drop an existing diagnostic whose location is null (finding C2).; cannot_determine: codex: The changed diagnostic forwarding and location handling plausibly preserve current-compilation diagnostics, but no suite results or regression-test outcomes are available here.
- ask: refused clause `REQ-2283-N2`: reviewers_disagree: claude says met, codex says cannot_determine; cannot_determine: codex: The inspected added tests do not establish that the required referenced-assembly scenario is covered or that those tests fail without the fix, and no deterministic test-check results were available.
- ask: reviewer refusal `claude`: No regressions across the full test suite (execution tests, net472 target, MessagePack.Tests) (MessagePack.SourceGenerator.ExecutionTests and MapModeExecutionTests failed to compile in my environment with CS0117 in a pre-existing file (GeneratedCompositeResolverTests.cs, 'MyGeneratedCompositeResolver' does not contain a definition for 'Instance'), which points to an environment/build-order issue, not this change. I only ran SourceGenerator.Tests on net8.0.)
- ask: reviewer refusal `claude`: Behaviour in the IDE with project-to-project references (CompilationReference symbols) (Needs runtime behaviour in a workspace host; no test covers it and I did not build such a scenario.)
- ask: reviewer refusal `claude`: Whether the MsgPack018 null-location path (C2) is reachable in practice (Depends on member enumeration order over metadata base types; I would have to construct and run a scenario I did not run.)
- ask: reviewer refusal `codex`: Referenced-assembly generic value type reproduction, analyzer behavior, and whether tests fail without the fix (The inspected test cases do not demonstrate this issue-specific scenario, and no facts.json or test run results were available to establish runtime/build behavior.)
- ask: risk score `risk`: score 57.1 (notify>=15, ask>=40, block>=130); largest: reviewer_disagreement 24 + area_sensitivity 20 + lines_changed 9.1
- notify: verified finding `claude:C1`: minor: Location filter is not tested for source-backed symbols from another compilation
- notify: verified finding `claude:C2`: minor: Global filter also drops Location.None diagnostics for types in the current compilation
- notify: trust cap `generator-analyzer-core`: generator-analyzer-core: AI may clear at most to notify (mandate clearance right)
- silent: trust cap `docs`: docs: AI may clear at most to silent (mandate clearance right)
- silent: trust cap `tests`: tests: AI may clear at most to silent (mandate clearance right)

</details>

## What the AI refused to decide, and why

- **REQ-2283-F1**: `reviewers_disagree` claude says met, codex says cannot_determine; `cannot_determine` codex: The added test file has generic formatter tests, but the inspected test inputs do not establish the required referenced-assembly case or verify a generated resolver for it.
- **REQ-2283-F2**: `reviewers_disagree` claude says met, codex says cannot_determine; `cannot_determine` codex: The reviewed test input does not exercise the same type from a referenced assembly through the MsgPack00x analyzer.
- **REQ-2283-N1**: `cannot_determine` claude: MessagePack.SourceGenerator.Tests (net8.0) passes on head with 170/170, but the execution test projects did not build in my environment (a pre-existing file fails too), I did not run net472, and the new global location filter can in principle drop an existing diagnostic whose location is null (finding C2).; `cannot_determine` codex: The changed diagnostic forwarding and location handling plausibly preserve current-compilation diagnostics, but no suite results or regression-test outcomes are available here.
- **REQ-2283-N2**: `reviewers_disagree` claude says met, codex says cannot_determine; `cannot_determine` codex: The inspected added tests do not establish that the required referenced-assembly scenario is covered or that those tests fail without the fix, and no deterministic test-check results were available.
- **claude** refused: No regressions across the full test suite (execution tests, net472 target, MessagePack.Tests). Why: MessagePack.SourceGenerator.ExecutionTests and MapModeExecutionTests failed to compile in my environment with CS0117 in a pre-existing file (GeneratedCompositeResolverTests.cs, 'MyGeneratedCompositeResolver' does not contain a definition for 'Instance'), which points to an environment/build-order issue, not this change. I only ran SourceGenerator.Tests on net8.0.. Who should decide: CI / build owner (facts stage)
- **claude** refused: Behaviour in the IDE with project-to-project references (CompilationReference symbols). Why: Needs runtime behaviour in a workspace host; no test covers it and I did not build such a scenario.. Who should decide: source generator / analyzer area owner
- **claude** refused: Whether the MsgPack018 null-location path (C2) is reachable in practice. Why: Depends on member enumeration order over metadata base types; I would have to construct and run a scenario I did not run.. Who should decide: analyzer area owner
- **codex** refused: Referenced-assembly generic value type reproduction, analyzer behavior, and whether tests fail without the fix. Why: The inspected test cases do not demonstrate this issue-specific scenario, and no facts.json or test run results were available to establish runtime/build behavior.. Who should decide: MessagePack source generator maintainer

## Requirement trace

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-2283-F1 | refused | claude: met (5/8 verified), codex: cannot_determine (2/2 verified) | build: pass, tests.targeted: pass | reviewers_disagree; cannot_determine |
| REQ-2283-F2 | refused | claude: met (3/4 verified), codex: cannot_determine (2/2 verified) | build: pass, tests.targeted: pass | reviewers_disagree; cannot_determine |
| REQ-2283-F3 | proven | claude: met (4/4 verified), codex: met (2/2 verified) | build: pass, tests.targeted: pass | - |
| REQ-2283-N1 | refused | claude: cannot_determine (3/3 verified), codex: cannot_determine (2/2 verified) | build: pass, tests.full_suite: pass | cannot_determine |
| REQ-2283-N2 | refused | claude: met (3/6 verified), codex: cannot_determine (2/2 verified) | build: pass, tests.fail_without_fix: pass | reviewers_disagree; cannot_determine |

## What was checked, and by whom

| Check | Status | Tool | Summary |
|---|---|---|---|
| build | pass | dotnet build 8.0.402 | 0 errors, 1 unique warnings |
| tests.targeted | pass | dotnet test 8.0.402 | 19 passed, 0 failed, 0 skipped (3 new tests in run) |
| tests.fail_without_fix | pass | dotnet test (source reverted, tests kept) 8.0.402 | new tests fail on base source: 3/3 failed -> tests do cover the change |
| tests.full_suite | pass | dotnet test 8.0.402 | tests/MessagePack.SourceGenerator.Tests: 170 tests, 170 passed, 0 failed (0 not failing on base, 0 also failing on base) |
| public_api | pass | git diff of PublicAPI.*.txt + scan of added public/protected declarations in src/  | no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or removed in src/ |
| analyzers | pass | dotnet build warnings (Roslyn analyzers, StyleCop, PublicApiAnalyzers) vs base  | no new warnings |

| Reviewer | Model | Prompt | Verified findings | Rejected | Refusals |
|---|---|---|---|---|---|
| claude | claude-opus-5-5 (Anthropic) | review-v1 | 3 | 0 | 3 |
| codex | GPT-6 Codex (OpenAI) | review-v1 | 0 | 0 | 1 |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v1 (ef0e95521f7e)

## What the AI found (verified findings)

- **claude:C1** [minor, tests] Location filter is not tested for source-backed symbols from another compilation -> tier notify
  The new tests only reference the defining assembly as a metadata image, where referenced symbols have no syntax at all. The branch of ReportIfLocatedInCompilation that matters for REQ-2283-F3 (a referenced symbol that has syntax in a tree outside the compilation, e.g. a CompilationReference as used for project-to-project references in the IDE) is not exercised. The code looks correct, but no test pins this down.
    - [OK] `tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs:673` @head: `MetadataReference.CreateFromImage(stream.ToArray())` (quote matches tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs:673 at head 9df83c38)
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1446` @head: `this.compilation.ContainsSyntaxTree(diagnostic.Location.SourceTree)` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1446 at head 9df83c38)
- **claude:C2** [minor, correctness] Global filter also drops Location.None diagnostics for types in the current compilation -> tier notify
  The filter drops every diagnostic whose location is not in source, not only diagnostics about referenced types. At least one existing site (MsgPack018 CollidingMemberNamesInForceMapMode) computes a null location when the colliding member has no syntax, for example when it comes from a base class in metadata. Before this change that Error diagnostic was reported without a location; now it is silently dropped. I did not confirm by running that this path is reachable, so this is a risk and not a demonstrated regression.
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:786` @head: `_ => null,` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:786 at head 9df83c38)
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:789` @head: `reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.CollidingMemberNamesInForceMapMode, location));` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:789 at head 9df83c38)
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1446` @head: `if (diagnostic.Location.IsInSource && this.compilation.ContainsSyntaxTree(diagnostic.Location.SourceTree))` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1446 at head 9df83c38)
- **claude:C3** [info, docs] Docs promise the defining project reports the diagnostics, which only holds if that project runs the MessagePack analyzer -> tier silent
  README and MsgPack004.md state that problems in a referenced type are reported by the defining project. That only happens if the defining project itself references the MessagePack analyzer. Otherwise the consuming build now silently ignores, for example, unkeyed members of the referenced type.
    - [OK] `README.md:1642` @head: `Diagnostics about the members of such a type are reported by the assembly that defines it rather than by the consuming project` (quote matches README.md:1642 at head 9df83c38)
    - [OK] `doc/analyzers/MsgPack004.md:51` @head: `This analyzer only reports on members declared in the project being compiled.` (quote matches doc/analyzers/MsgPack004.md:51 at head 9df83c38)

## Rejected: unsupported claims

- None.

## What was not checked, and why

- `tests.execution` (facts.json not_run): SDK 8.0.402 ships Roslyn 4.11 but MessagePack.SourceGenerator references Microsoft.CodeAnalysis 4.12.0, so csc refuses to load the generator (warning CS9057) and projects that consume it as an analyzer (tests/MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) fail to compile (CS0117 'GeneratedMessagePackResolver' does not contain 'Instance'). This also happens on base 32258fdb, so it is an environment/toolchain mismatch, not caused by the change. Needs an SDK with Roslyn >= 4.12 (e.g. .NET SDK 9.0.1xx); swapping in a newer compiler toolset was not permitted in this run.
- `tests.MessagePack.Tests` (facts.json not_run): runtime library src/MessagePack not modified by the change; suite not run
- `build.net472/netstandard` (facts.json not_run): only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks` (facts.json not_run): no runtime serialization hot path touched (generator/analyzer only)
- `other-targets` (mandate known gap): Tests run on net8.0 only; .NET Framework, Unity and NativeAOT targets are not exercised
- `runtime-perf` (mandate known gap): No benchmarks unless a perf-sensitive path is touched; allocation and throughput regressions can slip through
- `semantic-intent` (mandate known gap): Correctness beyond what tests and cited evidence show is not established by the AI
- `provenance` (mandate known gap): Licensing and provenance of agent-written code are not checked

## Residual risk

- REQ-2283-F1 not proven: reviewers_disagree; cannot_determine
- REQ-2283-F2 not proven: reviewers_disagree; cannot_determine
- REQ-2283-N1 not proven: cannot_determine
- REQ-2283-N2 not proven: reviewers_disagree; cannot_determine
- Reviewer refusal (claude): No regressions across the full test suite (execution tests, net472 target, MessagePack.Tests)
- Reviewer refusal (claude): Behaviour in the IDE with project-to-project references (CompilationReference symbols)
- Reviewer refusal (claude): Whether the MsgPack018 null-location path (C2) is reachable in practice
- Reviewer refusal (codex): Referenced-assembly generic value type reproduction, analyzer behavior, and whether tests fail without the fix
- tests.execution not run (SDK 8.0.402 ships Roslyn 4.11 but MessagePack.SourceGenerator references Microsoft.CodeAnalysis 4.12.0, so csc refuses to load the generator (warning CS9057) and projects that consume it as an analyzer (tests/MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) fail to compile (CS0117 'GeneratedMessagePackResolver' does not contain 'Instance'). This also happens on base 32258fdb, so it is an environment/toolchain mismatch, not caused by the change. Needs an SDK with Roslyn >= 4.12 (e.g. .NET SDK 9.0.1xx); swapping in a newer compiler toolset was not permitted in this run.)
- tests.MessagePack.Tests not run (runtime library src/MessagePack not modified by the change; suite not run)
- build.net472/netstandard not run (only the net8.0 slice of src/MessagePack was built (Linux container, Debug))
- benchmarks not run (no runtime serialization hot path touched (generator/analyzer only))
- Standing gaps of this pipeline: other-targets, runtime-perf, semantic-intent, provenance (see not checked)

## Risk score: 57.1 -> ask

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
| reviewer_disagreement | 24 | 3 clause(s) x 8: REQ-2283-F1, REQ-2283-F2, REQ-2283-N2 |
| failed_checks | 0 | 0 failed check(s) x 25 |
| **total** | **57.1** | bands: {'notify': 15, 'ask': 40, 'block': 130} |

## Sign-off

Owner: **Toivo** (FYI: Rene)
Sign-off required: yes; allowed decisions: accept, reject, request-changes

> I, Toivo, have read what was checked and by whom, what was not checked and why, and the residual risk listed in this pack, and I own this decision.

```
countersign sign 2283 --as Toivo --decision <accept|reject|request-changes> --note "..."
```
