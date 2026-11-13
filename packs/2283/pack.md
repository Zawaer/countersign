# Evidence pack: change 2283

**Recommended tier: ASK** · owner **Toivo** · risk score 41.1

Branch `ju26-issue-2283` (32258fdb..9df83c38), 4 files, +225 -3. Author Stelian Vultur (agent-written: True). Commit: implementation for #2283

Mandate `messagepack-csharp` v2 sha256 `39cc2060685638e1`, signature: valid, Toivo

## Why this tier

- **ask** from verified finding `claude:C1`: major: Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic
- **ask** from refused clause `REQ-2283-F1`: missing_review: nemotron gave no verdict
- **ask** from refused clause `REQ-2283-F2`: missing_review: nemotron gave no verdict
- **ask** from refused clause `REQ-2283-F3`: missing_review: nemotron gave no verdict
- **ask** from refused clause `REQ-2283-N1`: missing_review: nemotron gave no verdict; not_met: claude: The existing suite passes (170/170, no new failures), so the parenthetical part holds, but the clause's main statement does not: the location filter also drops diagnostics about types declared in the current compilation when the reporting location is a metadata member. My probe (scratch worktree, SDK 8, not in facts.json): metadata generic class Lib.Item<T> with [Key(0)] T Content, used as Item<Foo> where App.Foo lacks [MessagePackObject]; base reports MsgPack003 'Type must be marked with MessagePackObjectAttribute: Item.Content', head reports nothing. Item<T> as a class did not crash on base (issue table: 'class Item<T> | ok'), so this is a regression in a configuration that worked before. The existing suite does not cover it.; reviewers_disagree: claude says not_met, codex says met
- **ask** from refused clause `REQ-2283-N2`: missing_review: nemotron gave no verdict
- **ask** from reviewer refusal `claude`: Whether the resolver generated for a project consuming a closed generic struct from a referenced assembly serializes it correctly at run time (and whether emitting a second formatter for Lib.Item`1 in the consuming assembly is intended) (tests.execution was not run for this change (SDK 8.0.402 cannot load the Roslyn 4.12 generator); the new tests skip the generated-sources check and only assert the resolver's hint name exists. I saw the generator emit Formatters.App.R.Lib.ItemFormatter`1.g.cs in my probe but did not execute it.)
- **ask** from reviewer refusal `claude`: Whether the documented behaviour change (diagnostics for referenced types are reported only by the defining project) is acceptable product behaviour (It is a policy choice for the maintainers, and it is incomplete when the defining project does not run the analyzer (e.g. a NuGet package built without it).)
- **ask** from reviewer refusal `codex`: Execution-test behavior under a compiler that loads the generator (The supplied facts mark execution tests as not run under SDK 8 because its compiler cannot load this generator; no SDK 9 execution result is supplied for this change.)
- **ask** from risk score `risk`: score 41.1 (notify>=15, ask>=40, block>=130); largest: area_sensitivity 20 + lines_changed 9.1 + reviewer_disagreement 8

<details><summary>All tier drivers</summary>

- ask: verified finding `claude:C1`: major: Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic
- ask: refused clause `REQ-2283-F1`: missing_review: nemotron gave no verdict
- ask: refused clause `REQ-2283-F2`: missing_review: nemotron gave no verdict
- ask: refused clause `REQ-2283-F3`: missing_review: nemotron gave no verdict
- ask: refused clause `REQ-2283-N1`: missing_review: nemotron gave no verdict; not_met: claude: The existing suite passes (170/170, no new failures), so the parenthetical part holds, but the clause's main statement does not: the location filter also drops diagnostics about types declared in the current compilation when the reporting location is a metadata member. My probe (scratch worktree, SDK 8, not in facts.json): metadata generic class Lib.Item<T> with [Key(0)] T Content, used as Item<Foo> where App.Foo lacks [MessagePackObject]; base reports MsgPack003 'Type must be marked with MessagePackObjectAttribute: Item.Content', head reports nothing. Item<T> as a class did not crash on base (issue table: 'class Item<T> | ok'), so this is a regression in a configuration that worked before. The existing suite does not cover it.; reviewers_disagree: claude says not_met, codex says met
- ask: refused clause `REQ-2283-N2`: missing_review: nemotron gave no verdict
- ask: reviewer refusal `claude`: Whether the resolver generated for a project consuming a closed generic struct from a referenced assembly serializes it correctly at run time (and whether emitting a second formatter for Lib.Item`1 in the consuming assembly is intended) (tests.execution was not run for this change (SDK 8.0.402 cannot load the Roslyn 4.12 generator); the new tests skip the generated-sources check and only assert the resolver's hint name exists. I saw the generator emit Formatters.App.R.Lib.ItemFormatter`1.g.cs in my probe but did not execute it.)
- ask: reviewer refusal `claude`: Whether the documented behaviour change (diagnostics for referenced types are reported only by the defining project) is acceptable product behaviour (It is a policy choice for the maintainers, and it is incomplete when the defining project does not run the analyzer (e.g. a NuGet package built without it).)
- ask: reviewer refusal `codex`: Execution-test behavior under a compiler that loads the generator (The supplied facts mark execution tests as not run under SDK 8 because its compiler cannot load this generator; no SDK 9 execution result is supplied for this change.)
- ask: risk score `risk`: score 41.1 (notify>=15, ask>=40, block>=130); largest: area_sensitivity 20 + lines_changed 9.1 + reviewer_disagreement 8
- notify: verified finding `claude:C2`: minor: BothStringAndIntKeyAreNull is now silently suppressed for positional record properties in source
- notify: trust cap `generator-analyzer-core`: generator-analyzer-core: AI may clear at most to notify (mandate clearance right)
- silent: trust cap `docs`: docs: AI may clear at most to silent (mandate clearance right)
- silent: trust cap `tests`: tests: AI may clear at most to silent (mandate clearance right)

</details>

## What the AI refused to decide, and why

- **REQ-2283-F1**: `missing_review` nemotron gave no verdict
- **REQ-2283-F2**: `missing_review` nemotron gave no verdict
- **REQ-2283-F3**: `missing_review` nemotron gave no verdict
- **REQ-2283-N1**: `missing_review` nemotron gave no verdict; `not_met` claude: The existing suite passes (170/170, no new failures), so the parenthetical part holds, but the clause's main statement does not: the location filter also drops diagnostics about types declared in the current compilation when the reporting location is a metadata member. My probe (scratch worktree, SDK 8, not in facts.json): metadata generic class Lib.Item<T> with [Key(0)] T Content, used as Item<Foo> where App.Foo lacks [MessagePackObject]; base reports MsgPack003 'Type must be marked with MessagePackObjectAttribute: Item.Content', head reports nothing. Item<T> as a class did not crash on base (issue table: 'class Item<T> | ok'), so this is a regression in a configuration that worked before. The existing suite does not cover it.; `reviewers_disagree` claude says not_met, codex says met
- **REQ-2283-N2**: `missing_review` nemotron gave no verdict
- **claude** refused: Whether the resolver generated for a project consuming a closed generic struct from a referenced assembly serializes it correctly at run time (and whether emitting a second formatter for Lib.Item`1 in the consuming assembly is intended). Why: tests.execution was not run for this change (SDK 8.0.402 cannot load the Roslyn 4.12 generator); the new tests skip the generated-sources check and only assert the resolver's hint name exists. I saw the generator emit Formatters.App.R.Lib.ItemFormatter`1.g.cs in my probe but did not execute it.. Who should decide: source-generator area owner (run the execution tests under SDK 9 or a two-project repro)
- **claude** refused: Whether the documented behaviour change (diagnostics for referenced types are reported only by the defining project) is acceptable product behaviour. Why: It is a policy choice for the maintainers, and it is incomplete when the defining project does not run the analyzer (e.g. a NuGet package built without it).. Who should decide: MessagePack-CSharp maintainers / analyzer area owner
- **codex** refused: Execution-test behavior under a compiler that loads the generator. Why: The supplied facts mark execution tests as not run under SDK 8 because its compiler cannot load this generator; no SDK 9 execution result is supplied for this change.. Who should decide: area owner

_2 disputed item(s), not adjudicated: REQ-2283-N1, finding:claude:C1_

## Who reviewed

Participating reviewers: claude, codex, nemotron. Adjudicator: gemini. Confidential: no. Rule: proven needs every participating reviewer to say met with verified evidence, and the clause's checks to pass.

## Requirement trace

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-2283-F1 | refused | claude: met (8/8 verified), codex: met (3/3 verified) | build: pass, tests.targeted: pass | missing_review |
| REQ-2283-F2 | refused | claude: met (5/5 verified), codex: met (3/3 verified) | build: pass, tests.targeted: pass | missing_review |
| REQ-2283-F3 | refused | claude: met (4/4 verified), codex: met (3/3 verified) | build: pass, tests.targeted: pass | missing_review |
| REQ-2283-N1 | refused | claude: not_met (4/5 verified), codex: met (1/1 verified) | build: pass, tests.full_suite: pass | missing_review; not_met; reviewers_disagree |
| REQ-2283-N2 | refused | claude: met (4/4 verified), codex: met (2/2 verified) | build: pass, tests.fail_without_fix: pass | missing_review |

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
| claude | claude-opus-5-5 (Anthropic) | review-v1 | 3 | 0 | 2 |
| codex | GPT-6 (OpenAI) | review-v1 | 0 | 0 | 1 |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v2 (39cc20606856)

## What the AI found (verified findings)

- **claude:C1** [major, correctness] Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic -> tier ask
  ReportIfLocatedInCompilation drops every diagnostic whose location is not a source location in this compilation, including Location.None and metadata locations, which Roslyn does allow analyzers to report. TypeMustBeMessagePackObject (MsgPack003) is located at callerSymbol.Locations[0]; when the caller is a member of a referenced generic (Lib.Item<T>.Content) and T is an app type without [MessagePackObject] (Item<Foo>), the diagnostic is about App.Foo but is now discarded. My probe: base reports MsgPack003 (metadata location), head reports nothing, while the generator still emits App.R.g.cs and a formatter for Lib.Item`1, so the missing Foo formatter would only surface at run time. This configuration (a generic class from another assembly) did not crash on base, so it is a regression. The XML doc comment's justification ('which analyzers are not permitted to do') is only true for source locations in other compilations.
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1446` @head: `if (diagnostic.Location.IsInSource && this.compilation.ContainsSyntaxTree(diagnostic.Location.SourceTree))` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1446 at head 9df83c38)
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1341` @head: `callerSymbol.Locations[0]` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1341 at head 9df83c38)
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1442` @head: `which analyzers are not permitted to do` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1442 at head 9df83c38)
    - [OK] check `tests.full_suite` (facts.json: tests.full_suite pass: tests/MessagePack.SourceGenerator.Tests: 170 tests, 170 passed, 0 failed (0 not failing on base, 0 also failing on base))
- **claude:C2** [minor, correctness] BothStringAndIntKeyAreNull is now silently suppressed for positional record properties in source -> tier notify
  GetPropertyIdentifierLocation returns null when the property's syntax is a ParameterSyntax (positional record), so with the filter the diagnostic becomes Location.None and is dropped. My probe on '[MessagePackObject] public record Cmd([property: Key(null)] string Scope)': base threw AD0001 InvalidCastException (the old hard cast), head reports no key diagnostic at all. Better than a crash, but an in-source invalid contract is no longer reported; no test covers line 985.
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1434` @head: `(property.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax() as PropertyDeclarationSyntax)?.Identifier.GetLocation()` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1434 at head 9df83c38)
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:985` @head: `BothStringAndIntKeyAreNull, GetPropertyIdentifierLocation(item)` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:985 at head 9df83c38)
- **claude:C3** [info, maintainability] Fix treats the symptom location; metadata struct backing fields are still walked as members -> tier silent
  The crash comes from Roslyn importing private (compiler-generated backing) fields of metadata structs, which GetObjectInfo then treats as unkeyed members. The change makes those diagnostics location-safe and filters them, but still builds diagnostics for compiler-generated fields; any future diagnostic path that dereferences syntax for fields of a metadata struct will crash the same way. Skipping members without source/with CompilerGeneratedAttribute for metadata types would remove the class of bug.
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1077` @head: `item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1077 at head 9df83c38)
    - [REJECTED] https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2283 (issue text cannot be verified offline (not counted as evidence))

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

- REQ-2283-F1 not proven: missing_review
- REQ-2283-F2 not proven: missing_review
- REQ-2283-F3 not proven: missing_review
- REQ-2283-N1 not proven: missing_review; not_met; reviewers_disagree
- REQ-2283-N2 not proven: missing_review
- Reviewer refusal (claude): Whether the resolver generated for a project consuming a closed generic struct from a referenced assembly serializes it correctly at run time (and whether emitting a second formatter for Lib.Item`1 in the consuming assembly is intended)
- Reviewer refusal (claude): Whether the documented behaviour change (diagnostics for referenced types are reported only by the defining project) is acceptable product behaviour
- Reviewer refusal (codex): Execution-test behavior under a compiler that loads the generator
- Open major finding claude:C1: Location filter silently drops MsgPack003 about an in-compilation type reached through a metadata generic
- tests.execution not run (SDK 8.0.402 ships Roslyn 4.11 but MessagePack.SourceGenerator references Microsoft.CodeAnalysis 4.12.0, so csc refuses to load the generator (warning CS9057) and projects that consume it as an analyzer (tests/MessagePack.SourceGenerator.ExecutionTests, MapModeExecutionTests) fail to compile (CS0117 'GeneratedMessagePackResolver' does not contain 'Instance'). This also happens on base 32258fdb, so it is an environment/toolchain mismatch, not caused by the change. Needs an SDK with Roslyn >= 4.12 (e.g. .NET SDK 9.0.1xx); swapping in a newer compiler toolset was not permitted in this run.)
- tests.MessagePack.Tests not run (runtime library src/MessagePack not modified by the change; suite not run)
- build.net472/netstandard not run (only the net8.0 slice of src/MessagePack was built (Linux container, Debug))
- benchmarks not run (no runtime serialization hot path touched (generator/analyzer only))
- 2 disputed item(s) were not adjudicated (adjudicator gemini has not run)
- Standing gaps of this pipeline: other-targets, runtime-perf, semantic-intent, provenance (see not checked)

## Risk score: 41.1 -> ask

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

## Sign-off

Owner: **Toivo** (FYI: Rene)
Sign-off required: yes; allowed decisions: accept, reject, request-changes

> I, Toivo, have read what was checked and by whom, what was not checked and why, and the residual risk listed in this pack, and I own this decision.

```
countersign sign 2283 --as Toivo --decision <accept|reject|request-changes> --note "..."
```
