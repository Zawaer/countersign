# Evidence pack: change 2234

**Recommended tier: ASK** · owner **Toivo** · risk score 67.6

Branch `ju26-issue-2234` (32258fdb..9007cee1), 4 files, +262 -4. Author Stelian Vultur (agent-written: True). Commit: Implementation for #2234 The analyzer does not work if SuppressSourceGeneration = true

Mandate `messagepack-csharp` v2 sha256 `39cc2060685638e1`, signature: valid, Toivo

## Why this tier

- **ask** from verified finding `claude:C1`: major: The issue's 3.1.1 regression is not on this base; the change fixes a different crash
- **ask** from refused clause `REQ-2234-F1`: missing_review: nemotron gave no verdict
- **ask** from refused clause `REQ-2234-F2`: missing_review: nemotron gave no verdict
- **ask** from refused clause `REQ-2234-N1`: missing_review: nemotron gave no verdict; not_met: claude: The duplicate-key and mixed-kind crashes are fixed, and the full suite passes (175/175). But not every invalid contract in such a type is crash-free. The hard cast at line 985 is untouched, and my probe (scratch worktree, SDK 8, not in facts.json) of '[MessagePackObject(SuppressSourceGeneration = true)] public record Cmd([property: Key(null)] string Scope)' still gives AD0001 InvalidCastException (ParameterSyntax to PropertyDeclarationSyntax) at this head. The generator side of the duplicate-key fix has no test in facts.json (the new analyzer tests use CSharpCodeFixVerifier, analyzer only), though my probe showed no CS8785 for duplicate keys at head.; reviewers_disagree: claude says not_met, codex says met
- **ask** from refused clause `REQ-2234-N2`: missing_review: nemotron gave no verdict
- **ask** from reviewer refusal `claude`: Whether this change resolves issue #2234 for users of the released 3.1.x packages (The facts and tests were produced against base 32258fdb (develop line), which does not contain the 3.1.1 regression. Nothing was built or tested against master/v3.1.x, so whether the change applies there and fixes the reported symptom is not established (and C1 suggests it would not on its own).)
- **ask** from reviewer refusal `claude`: Whether the README section's list of diagnostics still reported for suppressed types is complete and accurate (Not every listed diagnostic (e.g. MsgPack012 inaccessible types) is covered by a test in facts.json, and I did not verify each one.)
- **ask** from risk score `risk`: score 67.6 (notify>=15, ask>=40, block>=130); largest: failed_checks 25 + area_sensitivity 20 + lines_changed 10.6

<details><summary>All tier drivers</summary>

- ask: verified finding `claude:C1`: major: The issue's 3.1.1 regression is not on this base; the change fixes a different crash
- ask: refused clause `REQ-2234-F1`: missing_review: nemotron gave no verdict
- ask: refused clause `REQ-2234-F2`: missing_review: nemotron gave no verdict
- ask: refused clause `REQ-2234-N1`: missing_review: nemotron gave no verdict; not_met: claude: The duplicate-key and mixed-kind crashes are fixed, and the full suite passes (175/175). But not every invalid contract in such a type is crash-free. The hard cast at line 985 is untouched, and my probe (scratch worktree, SDK 8, not in facts.json) of '[MessagePackObject(SuppressSourceGeneration = true)] public record Cmd([property: Key(null)] string Scope)' still gives AD0001 InvalidCastException (ParameterSyntax to PropertyDeclarationSyntax) at this head. The generator side of the duplicate-key fix has no test in facts.json (the new analyzer tests use CSharpCodeFixVerifier, analyzer only), though my probe showed no CS8785 for duplicate keys at head.; reviewers_disagree: claude says not_met, codex says met
- ask: refused clause `REQ-2234-N2`: missing_review: nemotron gave no verdict
- ask: reviewer refusal `claude`: Whether this change resolves issue #2234 for users of the released 3.1.x packages (The facts and tests were produced against base 32258fdb (develop line), which does not contain the 3.1.1 regression. Nothing was built or tested against master/v3.1.x, so whether the change applies there and fixes the reported symptom is not established (and C1 suggests it would not on its own).)
- ask: reviewer refusal `claude`: Whether the README section's list of diagnostics still reported for suppressed types is complete and accurate (Not every listed diagnostic (e.g. MsgPack012 inaccessible types) is covered by a test in facts.json, and I did not verify each one.)
- ask: risk score `risk`: score 67.6 (notify>=15, ask>=40, block>=130); largest: failed_checks 25 + area_sensitivity 20 + lines_changed 10.6
- notify: verified finding `claude:C2`: minor: Positional-record Key(null) still crashes the analyzer for suppressed (and other) types
- notify: trust cap `generator-analyzer-core`: generator-analyzer-core: AI may clear at most to notify (mandate clearance right)
- silent: trust cap `docs`: docs: AI may clear at most to silent (mandate clearance right)
- silent: trust cap `tests`: tests: AI may clear at most to silent (mandate clearance right)

</details>

## What the AI refused to decide, and why

- **REQ-2234-F1**: `missing_review` nemotron gave no verdict
- **REQ-2234-F2**: `missing_review` nemotron gave no verdict
- **REQ-2234-N1**: `missing_review` nemotron gave no verdict; `not_met` claude: The duplicate-key and mixed-kind crashes are fixed, and the full suite passes (175/175). But not every invalid contract in such a type is crash-free. The hard cast at line 985 is untouched, and my probe (scratch worktree, SDK 8, not in facts.json) of '[MessagePackObject(SuppressSourceGeneration = true)] public record Cmd([property: Key(null)] string Scope)' still gives AD0001 InvalidCastException (ParameterSyntax to PropertyDeclarationSyntax) at this head. The generator side of the duplicate-key fix has no test in facts.json (the new analyzer tests use CSharpCodeFixVerifier, analyzer only), though my probe showed no CS8785 for duplicate keys at head.; `reviewers_disagree` claude says not_met, codex says met
- **REQ-2234-N2**: `missing_review` nemotron gave no verdict
- **claude** refused: Whether this change resolves issue #2234 for users of the released 3.1.x packages. Why: The facts and tests were produced against base 32258fdb (develop line), which does not contain the 3.1.1 regression. Nothing was built or tested against master/v3.1.x, so whether the change applies there and fixes the reported symptom is not established (and C1 suggests it would not on its own).. Who should decide: analyzer area owner / maintainers choosing the target branch
- **claude** refused: Whether the README section's list of diagnostics still reported for suppressed types is complete and accurate. Why: Not every listed diagnostic (e.g. MsgPack012 inaccessible types) is covered by a test in facts.json, and I did not verify each one.. Who should decide: docs owner

_2 disputed item(s), not adjudicated: REQ-2234-N1, finding:claude:C1_

## Who reviewed

Participating reviewers: claude, codex, nemotron. Adjudicator: gemini. Confidential: no. Rule: proven needs every participating reviewer to say met with verified evidence, and the clause's checks to pass.

## Requirement trace

| Clause | Status | Verdicts | Checks | Reasons |
|---|---|---|---|---|
| REQ-2234-F1 | refused | claude: met (9/9 verified), codex: met (4/4 verified) | build: pass, tests.targeted: pass | missing_review |
| REQ-2234-F2 | refused | claude: met (5/5 verified), codex: met (2/2 verified) | build: pass, tests.targeted: pass | missing_review |
| REQ-2234-N1 | refused | claude: not_met (4/4 verified), codex: met (2/2 verified) | build: pass, tests.full_suite: pass | missing_review; not_met; reviewers_disagree |
| REQ-2234-N2 | refused | claude: met (7/7 verified), codex: met (2/2 verified) | build: pass, tests.fail_without_fix: pass | missing_review |

## What was checked, and by whom

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

| Reviewer | Model | Prompt | Verified findings | Rejected | Refusals |
|---|---|---|---|---|---|
| claude | claude-opus-5-5 (Anthropic) | review-v1 | 4 | 0 | 2 |
| codex | GPT-6 (OpenAI) | review-v1 | 0 | 0 | 0 |

Decision engine: countersign 0.1.0 under mandate messagepack-csharp v2 (39cc20606856)

## What the AI found (verified findings)

- **claude:C1** [major, correctness] The issue's 3.1.1 regression is not on this base; the change fixes a different crash -> tier ask
  Issue #2234 says the analyzer stopped working for SuppressSourceGeneration = true in 3.1.1. The cause in history is commit 1a74a620 ('stop collect field when object marked SuppressSourceGeneration', in v3.1.1 and still in v3.1.12): it moved the 'if (suppressSourceGeneration is true) return null;' to right after the attribute is read, before any member is analyzed. Base 32258fdb is on the develop line and does not contain v3.1.0/v3.1.1 or that commit. Its early return is at line 1369, after member collection, which is why MsgPack004/003/015 tests already pass on base. So the agent fixed the duplicate/mixed-key crashes (which hit non-suppressed types too, see DuplicateKeysAreReportedWithoutAnalyzerFailureForGeneratedTypes failing on base) and wrote tests and README text as if that were #2234. Merged into the 3.1.x/master line, this change would not restore the analyzer for suppressed types; the early return would still need to move.
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:723` @8373710fb0ae4bb453737f773b930401d8500c31: `if (suppressSourceGeneration is true)` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:723 at 8373710fb0ae4bb453737f773b930401d8500c31 8373710f)
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1369` @base: `if (suppressSourceGeneration is true)` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1369 at base 32258fdb)
    - [OK] test `SuppressSourceGenerationAnalyzerTests.MemberWithoutKeyIsReported` passed (facts.json tests.fail_without_fix: passed (new test))
    - [OK] test `SuppressSourceGenerationAnalyzerTests.DuplicateKeysAreReportedWithoutAnalyzerFailureForGeneratedTypes` failed (facts.json tests.fail_without_fix: failed (new test))
    - [REJECTED] https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2234 (issue text cannot be verified offline (not counted as evidence))
- **claude:C2** [minor, correctness] Positional-record Key(null) still crashes the analyzer for suppressed (and other) types -> tier notify
  The BothStringAndIntKeyAreNull path hard-casts the property's syntax to PropertyDeclarationSyntax. For a positional record property it is a ParameterSyntax, so AD0001 InvalidCastException. Reproduced at this head with SuppressSourceGeneration = true (own probe). This is an invalid contract in such a type, so N1's 'must not crash on invalid contracts' is not fully met.
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:985` @head: `(PropertyDeclarationSyntax)item.DeclaringSyntaxReferences[0].GetSyntax()` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:985 at head 9007cee1)
- **claude:C3** [info, correctness] 'continue' on mixed key kinds skips recursive collection of that member's type -> tier silent
  After reporting DoNotMixStringAndIntKeys the new 'continue' also skips CollectCore for the member, so diagnostics about the member's own type (e.g. MsgPack003) are no longer produced for that member until the key kind is fixed. Acceptable because the type already has an error, but it hides a second problem until the first is fixed.
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1008` @head: `continue; // The key kind does not match the other members; the diagnostic is reported, so skip this member.` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1008 at head 9007cee1)
- **claude:C4** [info, correctness] Duplicate-key guard makes the generator emit a formatter that silently drops the second member -> tier silent
  For a non-suppressed type with duplicate keys, the generator (which has no diagnostic sink) used to fail with CS8785. Now it keeps the first member and emits a formatter without the second. The build still fails while MsgPack005 is an error, but if a project lowers that diagnostic's severity, it silently loses data. I saw this in my probe (formatter generated, analyzer reports MsgPack005).
    - [OK] `src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1023` @head: `if (!intMembers.ContainsKey(member.IntKey))` (quote matches src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs:1023 at head 9007cee1)
    - [OK] test `SuppressSourceGenerationAnalyzerTests.DuplicateKeysAreReportedWithoutAnalyzerFailureForGeneratedTypes` passed (facts.json tests.targeted: passed (new test))

## Rejected: unsupported claims

- None.

## What was not checked, and why

- `tests.MessagePack.Tests` (facts.json not_run): runtime library src/MessagePack not modified by the change; suite not run
- `build.net472/netstandard` (facts.json not_run): only the net8.0 slice of src/MessagePack was built (Linux container, Debug)
- `benchmarks` (facts.json not_run): no runtime serialization hot path touched (generator/analyzer only)
- `other-targets` (mandate known gap): Tests run on net8.0 only; .NET Framework, Unity and NativeAOT targets are not exercised
- `runtime-perf` (mandate known gap): No benchmarks unless a perf-sensitive path is touched; allocation and throughput regressions can slip through
- `semantic-intent` (mandate known gap): Correctness beyond what tests and cited evidence show is not established by the AI
- `provenance` (mandate known gap): Licensing and provenance of agent-written code are not checked

## Residual risk

- REQ-2234-F1 not proven: missing_review
- REQ-2234-F2 not proven: missing_review
- REQ-2234-N1 not proven: missing_review; not_met; reviewers_disagree
- REQ-2234-N2 not proven: missing_review
- Reviewer refusal (claude): Whether this change resolves issue #2234 for users of the released 3.1.x packages
- Reviewer refusal (claude): Whether the README section's list of diagnostics still reported for suppressed types is complete and accurate
- Open major finding claude:C1: The issue's 3.1.1 regression is not on this base; the change fixes a different crash
- tests.MessagePack.Tests not run (runtime library src/MessagePack not modified by the change; suite not run)
- build.net472/netstandard not run (only the net8.0 slice of src/MessagePack was built (Linux container, Debug))
- benchmarks not run (no runtime serialization hot path touched (generator/analyzer only))
- 2 disputed item(s) were not adjudicated (adjudicator gemini has not run)
- Standing gaps of this pipeline: other-targets, runtime-perf, semantic-intent, provenance (see not checked)

## Risk score: 67.6 -> ask

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

## Sign-off

Owner: **Toivo** (FYI: Rene)
Sign-off required: yes; allowed decisions: accept, reject, request-changes

> I, Toivo, have read what was checked and by whom, what was not checked and why, and the residual risk listed in this pack, and I own this decision.

```
countersign sign 2234 --as Toivo --decision <accept|reject|request-changes> --note "..."
```
