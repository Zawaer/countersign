<!-- system prompt -->
# Countersign reviewer brief, review-v1

<!-- prompt_version: review-v1. Canonical brief for every stage-2 reviewer (Claude, Codex, Nemotron).
     Changing the wording means a new file (review-v2.md) and a new prompt_version in every review it produces. -->

You are one of several independent reviewers of an agent-written code change. Your review is **advice with evidence**,
never the approval: a decision engine checks every piece of evidence you cite, and a named human owner signs off.
Nobody will take your word for anything. A claim you cannot back with checkable evidence is worth nothing, and a
claim with evidence that does not check out counts against you.

## What you get

- The requirement set for the change (`requirements/<change>.yaml`): clause IDs such as `REQ-2283-F1` and their text.
- The upstream issue URL (you may not be able to open it; the requirement text is what you judge against).
- `facts.json`: deterministic results that already ran (build, targeted tests, "new tests fail without the fix",
  full suite, public API, analyzers), with test names and outcomes. **Use these results; do not guess what a test
  would do.** If a check is `skipped` or `error`, it did not establish anything.
- The diff between base and head, and the contents of the changed files with line numbers.
- A list of what you were **not** given. Do not reason about content you did not see.

## What to check

1. **Root cause vs the issue.** Does the change fix the cause the issue/requirement describes, or a symptom, or
   something adjacent? Was the requirement perhaps already met on base (then say so)?
2. **Each requirement clause.** `met`, `not_met` or `cannot_determine`, each tied to evidence.
3. **Scope.** Changes not needed for the requirement, unrelated files, generated files regenerated wholesale.
4. **Docs vs code.** Does documentation (README, analyzer docs, release notes) say what the code does?
5. **Tests exercise the requirement.** Do the new tests cover the clause, and do they fail without the fix
   (`tests.fail_without_fix` in facts.json)? A test that passes on base does not demonstrate the change.
6. Correctness, security (this library deserializes untrusted input), performance and maintainability problems.

## Evidence rules (machine-checked)

Every verdict and every finding needs evidence items. Allowed kinds:

```json
{"kind": "code", "file": "src/.../TypeCollector.cs", "line": 1442, "rev": "head", "quote": "exact substring of that line"}
{"kind": "test", "name": "Full.Test.Name", "outcome": "passed"}
{"kind": "test", "name": "Full.Test.Name", "outcome": "failed", "check": "tests.fail_without_fix"}
{"kind": "check", "id": "tests.fail_without_fix", "status": "pass"}
{"kind": "requirement", "req": "REQ-2283-F1", "quote": "exact words from the clause"}
{"kind": "issue", "url": "https://github.com/...", "quote": "..."}
```

- `code`: `file` is the repo path, `line` the line number shown in the listing, `rev` is `head` or `base`, and
  `quote` must be an **exact substring of that single line** (copy it; whitespace is normalised, nothing else).
  Quote the text after the `| ` line-number gutter, never the gutter itself. Short, distinctive quotes are best.
- `test`: the name and outcome exactly as in facts.json. A test name can appear in several runs (head runs and the
  source-reverted `tests.fail_without_fix` run): an outcome is checked against the head runs unless you pin the run
  with `check`.
- `check`: the `id` of a check in facts.json; if you state `status`, it must match.
- `issue` items are never counted as verified (the engine cannot read the web). Use them for context only.
- A finding with no verifiable evidence is rejected and shown as "unsupported claim". Prefer one precise citation
  to five vague ones.
- What counts towards a verdict or a finding: `code` quotes at `head` or `base` in a file the change touches, `test`
  items with an `outcome`, `check` items with a `status`. A `requirement` quote, a test without an outcome or a check
  without a status is shown but does not count, so state the outcome or status you are relying on.

## Refuse rather than guess

- If you cannot establish a clause from what you were given, the verdict is `cannot_determine`, with the reason in
  `confidence_basis`.
- Anything you will not decide (not given the code, needs runtime behaviour, other target frameworks, performance,
  security judgement beyond the evidence, generated files you did not see) goes in `refusals` with who should decide.
  If the refusal is about a requirement clause, set `req` to its id. Set `blocking: true` only if the change should
  not merge until a human has decided it; otherwise the refusal is recorded and the owner is told.
- If you reviewed this change before, your earlier findings stay open unless you raise them again or refute them:
  to close one, add `{"finding": "<earlier id>", "reason": "why it is not a defect", "evidence": [ … about the same
  code … ]}` to `refutations`. Dropping it silently keeps it open.
- Never invent file contents, line numbers, test names or check results.

## Output

Return **only** one JSON object, no prose before or after, no Markdown fences:

```json
{
  "summary": "two or three sentences: what the change does, whether it fixes the root cause, your overall view",
  "requirement_verdicts": [
    {"req": "REQ-…", "verdict": "met|not_met|cannot_determine",
     "confidence_basis": "why, in one sentence, tied to the evidence", "evidence": [ … ]}
  ],
  "findings": [
    {"id": "N1", "title": "short", "severity": "blocker|major|minor|info",
     "category": "correctness|security|performance|maintainability|docs|tests|scope",
     "claim": "what is wrong and why it matters", "evidence": [ … at least one … ], "suggested_fix": "optional"}
  ],
  "refusals": [
    {"topic": "what you will not decide", "reason": "why", "who_should_decide": "role, e.g. area owner",
     "req": "REQ-… if it is about one clause (optional)", "blocking": false}
  ],
  "refutations": []
}
```

One verdict per requirement clause, in the order given. Severity: `blocker` = must not merge; `major` = needs a fix
or an owner's explicit acceptance; `minor` = should fix; `info` = observation. Do not add fields for reviewer name,
model, vendor or time: the runner stamps those.


<!-- user message -->
# Change up-1934: branch upstream PR #1934, base 7ef21d4b6ea661cd346b5beeabfc3545106d83b6, head 2f9324f9987410677a310a633232411eb978a699
Commit message: Change default Language version of generated code to C# 7.3
Upstream issue: https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/1925

## Requirement set (requirements/up-1934.yaml)
```yaml
# PLACEHOLDER derived from upstream PR #1934 ("#1926 follow-up") and issue #1925, for upstream PR #1934 (a merged,
# human-written, test-only upstream change used as a low-risk control). Not a Tieto requirement set.
change: "up-1934"
branch: upstream PR #1934 (merge b06681ea; base = merge^1 7ef21d4b, head = merge^2 2f9324f9)
source: https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/1925
pull_request: https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1934
official: false
requirements:
  - id: REQ-up-1934-F1
    type: functional
    text: "By default, the source generator tests must compile the test input and the generated code at C# 7.3, the language version a netstandard2.0 project uses by default (issue #1925), so generated code that needs a newer language version fails the tests."
  - id: REQ-up-1934-F2
    type: functional
    text: "Tests whose input source needs a newer language feature (records, record structs) must set that language version explicitly, and only those."
  - id: REQ-up-1934-N1
    type: non-functional
    checks: [tests.full_suite]
    text: "The change touches only test code, and no existing source generator test regresses."
```

## facts.json (deterministic checks; cite their ids and test names)
```json
{
 "change": "up-1934",
 "branch": "upstream PR #1934",
 "base": "7ef21d4b",
 "head": "2f9324f9",
 "base_full": "7ef21d4b6ea661cd346b5beeabfc3545106d83b6",
 "head_full": "2f9324f9987410677a310a633232411eb978a699",
 "commit_message": "Change default Language version of generated code to C# 7.3",
 "author": "Alan Liu",
 "agent_written": false,
 "upstream": {
  "pull_request": "https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1934",
  "issue": "https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/1925",
  "merge_commit": "b06681eaafee88475f2b2c958397eb540dad9d0e",
  "merged_into": "develop",
  "merged_at": "2024-08-21T18:58:39-06:00",
  "base_rule": "base = merge commit first parent (develop before the merge)",
  "head_rule": "head = merge commit second parent (PR branch tip); git diff base..head == git diff base..merge (asserted)",
  "control": "test only; merged upstream, human-written, not reverted or fixed later as far as checked (measurement/history/candidates.json has no entry for it; later history of the changed lines read by hand)"
 },
 "diff": {
  "files": 6,
  "insertions": 26,
  "deletions": 22,
  "by_kind": {
   "test": 6
  },
  "by_file": [
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/CustomStringKeyFormatterTests.cs",
    "ins": 2,
    "del": 1,
    "kind": "test"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs",
    "ins": 2,
    "del": 1,
    "kind": "test"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs",
    "ins": 4,
    "del": 3,
    "kind": "test"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/PrivateMemberAccessTests.cs",
    "ins": 12,
    "del": 12,
    "kind": "test"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorCodeFixVerifier`2.cs",
    "ins": 1,
    "del": 1,
    "kind": "test"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorVerifier`1+Test.cs",
    "ins": 5,
    "del": 4,
    "kind": "test"
   }
  ]
 },
 "new_tests_in_diff": [],
 "checks": [
  {
   "id": "build",
   "tool": "dotnet build",
   "tool_version": "8.0.402",
   "status": "pass",
   "command": "dotnet build tests/MessagePack.SourceGenerator.Tests/MessagePack.SourceGenerator.Tests.csproj --no-incremental -m:8 -c Debug",
   "projects": [
    "src/MessagePack.SourceGenerator",
    "src/MessagePack.Analyzers.CodeFixes",
    "src/MessagePack.Analyzers",
    "src/MessagePack.Annotations",
    "src/MessagePack (net8.0)",
    "tests/MessagePack.SourceGenerator.Tests"
   ],
   "summary": "0 errors, 1 unique warnings",
   "log": "evidence/up-1934/logs/build.log",
   "duration_s": 11.0,
   "tool_version_note": "global.json at these commits pins SDK 8.0.300 with rollForward patch; only 8.0.402 is installed, so global.json was set to 8.0.402 (rollForward disable) in the scratch worktrees only and restored afterwards"
  },
  {
   "id": "tests.targeted",
   "tool": "dotnet test",
   "tool_version": "8.0.402",
   "status": "pass",
   "summary": "59 passed, 0 failed, 0 skipped (0 new tests in run)",
   "tests": [
    {
     "name": "CustomStringKeyFormatterTests.RecordWithPrimaryConstructor",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "CustomStringKeyFormatterTests.RecordWithWithInitOnlyProps",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.AdditionalAllowTypes",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.AdditionalFormatterTypes",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.AdditionalFormatterTypes_RedundantAttibute",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.ArrayTypedProperty",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.CustomFormatterViaAttributeOnProperty(usesMapMode: False)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.CustomFormatterViaAttributeOnProperty(usesMapMode: True)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.CustomFormatterWithSingletonPattern",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.DeserializingConstructorParameterMemberTypeAssignability_Incompatible",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.DeserializingConstructorParameterMemberTypeAssignability_MemberAssignsToParamType",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.EnumFormatter(container: Namespace, usesMapMode: False)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.EnumFormatter(container: Namespace, usesMapMode: True)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.EnumFormatter(container: NestingClass, usesMapMode: False)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.EnumFormatter(container: NestingClass, usesMapMode: True)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.EnumFormatter(container: None, usesMapMode: False)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.EnumFormatter(container: None, usesMapMode: True)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.EnumFormatter_CollidingTypeNames",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.ExcludeFormatterFromSourceGeneratedResolver",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.GenericType",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.GenericTypeArg",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.GenericType_CollidingTypeNames",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.ImplicitFormatterTypes",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.MixType_CollidingTypeNames",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.NestedMessagePackObjects",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.NestedMessagePackObjects_Array",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.NoGenerationForAnnotationOnly",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.NonDefaultDeserializingConstructor_Private",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.NonGenericType_CollidingTypeNames",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.SpecifyFormatterFromStockSet",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.UnionFormatter(container: Namespace)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.UnionFormatter(container: NestingClass)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.UnionFormatter(container: None)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.GenericsOfT1T2Formatter",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.GenericsOfTFormatter",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.GenericsOfTFormatter_FormatterOnly",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.GenericsOfTFormatter_WithKnownTypes",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.GenericsUnionFormatter",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.GenericsUnionFormatter_Nested",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.Generics_Constraints_Multiple",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.Generics_Constraints_NullableReferenceType",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.Generics_Constraints_ReferenceType_Nullable",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.Generics_Constraints_Struct",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.Generics_Constraints_Type",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.Generics_Defined_In_ReferencedProject",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.NestedGenericTypes",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.NullableFormatter",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.WellKnownGenericsFormatter",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "PrivateMemberAccessTests.FormatterForClassWithPrivateMembers(type: \"class\", version: CSharp7_3)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "PrivateMemberAccessTests.FormatterForClassWithPrivateMembers(type: \"record struct\", version: CSharp10)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "PrivateMemberAccessTests.FormatterForClassWithPrivateMembers(type: \"record\", version: CSharp9)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "PrivateMemberAccessTests.FormatterForClassWithPrivateMembers(type: \"struct\", version: CSharp7_3)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "PrivateMemberAccessTests.FormatterForClassWithPrivateMembers_Nested_NonPartialTypes(type: \"class\", languageVersion: CSharp7_3)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "PrivateMemberAccessTests.FormatterForClassWithPrivateMembers_Nested_NonPartialTypes(type: \"record\", languageVersion: CSharp9)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "PrivateMemberAccessTests.FormatterForClassWithPrivateMembers_Nested_NonPartialTypes(type: \"struct\", languageVersion: CSharp7_3)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "PrivateMemberAccessTests.FormatterForClassWithPrivateMembers_NonPartialTypes(type: \"class\", languageVersion: CSharp7_3)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "PrivateMemberAccessTests.FormatterForClassWithPrivateMembers_NonPartialTypes(type: \"record\", languageVersion: CSharp9)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "PrivateMemberAccessTests.FormatterForClassWithPrivateMembers_NonPartialTypes(type: \"struct\", languageVersion: CSharp7_3)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "PrivateMemberAccessTests.FormatterForClassWithPrivateMembers_WithNamespace",
     "outcome": "passed",
     "new": false
    }
   ],
   "log": "evidence/up-1934/logs/tests_targeted.1.log",
   "duration_s": 7.0,
   "filter": [
    "FullyQualifiedName~CustomStringKeyFormatterTests.|FullyQualifiedName~GenerationTests.|FullyQualifiedName~GenericsFormatterTests.|FullyQualifiedName~PrivateMemberAccessTests."
   ],
   "project": "tests/MessagePack.SourceGenerator.Tests",
   "on_base": "same filter on base: 59 passed, 0 failed of 59"
  },
  {
   "id": "tests.fail_without_fix",
   "status": "skipped",
   "summary": "not run: test-only change: no file under src/ changed, so there is no source to revert (see tests.detects_original_regression for what the new test settings catch)",
   "reason": "test-only change: no file under src/ changed, so there is no source to revert (see tests.detects_original_regression for what the new test settings catch)"
  },
  {
   "id": "tests.full_suite",
   "tool": "dotnet test",
   "tool_version": "8.0.402",
   "status": "pass",
   "summary": "tests/MessagePack.SourceGenerator.Tests: 123 tests, 123 passed, 0 failed (0 not failing on base, 0 also failing on base)",
   "project": "tests/MessagePack.SourceGenerator.Tests",
   "total": 123,
   "passed": 123,
   "failed": 0,
   "failures_not_on_base": [],
   "failures_also_on_base": [],
   "log": "evidence/up-1934/logs/tests_full_suite.log",
   "duration_s": 7.0,
   "base_total": 123,
   "base_passed": 123
  },
  {
   "id": "public_api",
   "tool": "git diff of PublicAPI.*.txt + scan of added public/protected declarations in src/",
   "status": "pass",
   "summary": "no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or removed in src/",
   "publicapi_files_changed": []
  },
  {
   "id": "analyzers",
   "tool": "dotnet build warnings (Roslyn analyzers, StyleCop, PublicApiAnalyzers) vs base",
   "status": "pass",
   "summary": "no new warnings",
   "new_warnings": [],
   "resolved_warnings": [],
   "base_warning_count": 1
  },
  {
   "id": "tests.detects_original_regression",
   "tool": "dotnet test (full SourceGenerator.Tests) on source before the #1926 fix, old vs new test files",
   "tool_version": "8.0.402",
   "tool_version_note": "global.json at these commits pins SDK 8.0.300 with rollForward patch; only 8.0.402 is installed, so global.json was set to 8.0.402 (rollForward disable) in the scratch worktrees only and restored afterwards",
   "status": "pass",
   "setup": "pre1926 = commit 3ea9234f (merge^1 of #1926, i.e. generator still emitting C# 8/9 syntax, issue #1925) with its own tests; pre1926-newtests = 3ea9234f + git diff 7ef21d4b..2f9324f9 (this PR, test files only; applies cleanly)",
   "summary": "with this PR's test changes, 61 tests fail on the pre-#1926 generator that pass with the old test files -> the new C# 7.3 default detects the #1925 regression (old tests: 0/123 failed; new tests: 63/123 failed; 0 fail either way)",
   "tests": [
    {
     "name": "CustomStringKeyFormatterTests.RecordWithWithInitOnlyProps",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.AdditionalAllowTypes",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.AdditionalFormatterTypes",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.AdditionalFormatterTypes_RedundantAttibute",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.ArrayTypedProperty",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.CustomFormatterWithSingletonPattern",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.DeserializingConstructorParameterMemberTypeAssignability_Incompatible",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"1\" actual \"4\"\r\n\r\nDiagnostics:\r\n// /0/Test0.cs(8,16): error MsgPack007: Deserializing constructor parameter type mismatch\nVerifyCS.Diagnostic(MsgPack00xMessagePackAnalyzer.MsgPack007).WithSpan(8, 16, 8, 36),\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.Generat"
    },
    {
     "name": "GenerationTests.DeserializingConstructorParameterMemberTypeAssignability_MemberAssignsToParamType",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.EnumFormatter(container: Namespace, usesMapMode: False)",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.EnumFormatter(container: Namespace, usesMapMode: True)",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.EnumFormatter(container: NestingClass, usesMapMode: False)",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.EnumFormatter(container: NestingClass, usesMapMode: True)",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.EnumFormatter(container: None, usesMapMode: False)",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.EnumFormatter(container: None, usesMapMode: True)",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.EnumFormatter_CollidingTypeNames",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.GenericType",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"6\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.GenericTypeArg",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,116): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.GenericType_CollidingTypeNames",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"6\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.ImplicitFormatterTypes",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.MixType_CollidingTypeNames",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"6\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.NestedMessagePackObjects",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.NestedMessagePackObjects_Array",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.NonDefaultDeserializingConstructor_Private",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.NonGenericType_CollidingTypeNames",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.SpecifyFormatterFromStockSet",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.UnionFormatter(container: Namespace)",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.UnionFormatter(container: NestingClass)",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenerationTests.UnionFormatter(container: None)",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenericsFormatterTests.GenericsOfT1T2Formatter",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"6\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenericsFormatterTests.GenericsOfTFormatter",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"6\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenericsFormatterTests.GenericsOfTFormatter_FormatterOnly",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,116): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenericsFormatterTests.GenericsOfTFormatter_WithKnownTypes",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"6\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenericsFormatterTests.GenericsUnionFormatter",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"6\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenericsFormatterTests.GenericsUnionFormatter_Nested",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"6\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenericsFormatterTests.Generics_Constraints_Multiple",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"1\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,116): error CS8400: Feature 'target-typed object creation' is not available in C# 8.0. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenericsFormatterTests.Generics_Constraints_Struct",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,116): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenericsFormatterTests.Generics_Constraints_Type",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,116): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenericsFormatterTests.Generics_Defined_In_ReferencedProject",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"6\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenericsFormatterTests.NestedGenericTypes",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"6\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenericsFormatterTests.NullableFormatter",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "GenericsFormatterTests.WellKnownGenericsFormatter",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "ImplicitResolverForCustomFormattersTests.MultipleFunctionalCustomFormattersForType_MultiFormatter",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"2\" actual \"5\"\r\n\r\nDiagnostics:\r\n// /0/Test0.cs(6,16): error MsgPack009: Multiple formatters for type System.Int32 found\nVerifyCS.Diagnostic(MsgPack00xMessagePackAnalyzer.MsgPack009).WithSpan(6, 16, 6, 28).WithArguments(\"System.Int32\"),\n// /0/Test0.cs(12,16): error MsgPack009: Multiple formatters for type S"
    },
    {
     "name": "ImplicitResolverForCustomFormattersTests.MultipleFunctionalCustomFormattersForType_OnlyOneNonExcluded",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "ImplicitResolverForCustomFormattersTests.OpenGenericFormatter",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,116): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "MessagePackFormatterAttributeTests.CanGenerateMessagePackFormatterAttr",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "MultipleTypesTests.TwoTypes(usesMapMode: False)",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "MultipleTypesTests.TwoTypes(usesMapMode: True)",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "PrivateMemberAccessTests.FormatterForClassWithPrivateMembers_WithNamespace",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "StringKeyedFormatterTests.PropertiesGetterOnlyDefaultValue",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "StringKeyedFormatterTests.PropertiesGetterOnlyIgnore",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "StringKeyedFormatterTests.PropertiesGetterOnlyMixed",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "StringKeyedFormatterTests.PropertiesGetterOnlyWithParameterizedConstructor",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "StringKeyedFormatterTests.PropertiesGetterOnlyWithParameterizedConstructorDefaultValue",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "StringKeyedFormatterTests.PropertiesGetterOnlyWithParameterizedConstructorPartially",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "StringKeyedFormatterTests.PropertiesGetterSetter",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "StringKeyedFormatterTests.PropertiesGetterSetterWithDefaultValue",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "StringKeyedFormatterTests.PropertiesGetterSetterWithDefaultValueInputPartially",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "StringKeyedFormatterTests.PropertiesGetterSetterWithParameterizedConstructor",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "StringKeyedFormatterTests.PropertiesGetterSetterWithParameterizedConstructorAndDefaultValue",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "StringKeyedFormatterTests.PropertiesGetterSetterWithParameterizedConstructorDoNotUseSetter",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    },
    {
     "name": "StringKeyedFormatterTests.PropertiesGetterSetterWithParameterizedConstructorPartially",
     "outcome": "failed",
     "outcome_with_old_tests": "passed",
     "error": "System.InvalidOperationException : Mismatch between number of diagnostics returned, expected \"0\" actual \"3\"\r\n\r\nDiagnostics:\r\n// MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs(42,118): error CS8370: Feature 'target-typed object creation' is not available in C# 7.3. Please use language version 9.0 or greater.\nDiagnosticResul"
    }
   ],
   "failed_either_way": [],
   "log": [
    "evidence/up-1934/logs/detects_original_regression.newtests.log",
    "evidence/up-1934/logs/detects_original_regression.oldtests.log"
   ]
  }
 ],
 "not_run": [
  {
   "id": "tests.MessagePack.Tests",
   "reason": "runtime library src/MessagePack not modified by the change; suite not run"
  },
  {
   "id": "tests.execution",
   "reason": "ExecutionTests/MapModeExecutionTests not run for this control (generator output is covered by the snapshot tests in the full suite)"
  },
  {
   "id": "build.net472/netstandard",
   "reason": "only the net8.0 slice of src/MessagePack was built (Linux container, Debug)"
  },
  {
   "id": "benchmarks",
   "reason": "no runtime serialization hot path touched"
  }
 ],
 "environment": {
  "sdk": "8.0.402",
  "os": "linux-x64 (container)",
  "configuration": "Debug",
  "max_cpu": 8,
  "sdk_note": "global.json at these commits pins SDK 8.0.300 with rollForward patch; only 8.0.402 is installed, so global.json was set to 8.0.402 (rollForward disable) in the scratch worktrees only and restored afterwards"
 }
}
```

## Files changed (6: 6 non-generated, 0 generated)
- tests/MessagePack.SourceGenerator.Tests/CustomStringKeyFormatterTests.cs (+2 -1, test)
- tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs (+2 -1, test)
- tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs (+4 -3, test)
- tests/MessagePack.SourceGenerator.Tests/PrivateMemberAccessTests.cs (+12 -12, test)
- tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorCodeFixVerifier`2.cs (+1 -1, test)
- tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorVerifier`1+Test.cs (+5 -4, test)

## Diff (non-generated files)
```diff
diff --git a/tests/MessagePack.SourceGenerator.Tests/CustomStringKeyFormatterTests.cs b/tests/MessagePack.SourceGenerator.Tests/CustomStringKeyFormatterTests.cs
index e5e2c631..a03d4f7e 100644
--- a/tests/MessagePack.SourceGenerator.Tests/CustomStringKeyFormatterTests.cs
+++ b/tests/MessagePack.SourceGenerator.Tests/CustomStringKeyFormatterTests.cs
@@ -1,6 +1,7 @@
 // Copyright (c) All contributors. All rights reserved.
 // Licensed under the MIT license. See LICENSE file in the project root for full license information.
 
+using Microsoft.CodeAnalysis.CSharp;
 using VerifyCS = CSharpSourceGeneratorVerifier<MessagePack.SourceGenerator.MessagePackGenerator>;
 
 public class CustomStringKeyFormatterTests
@@ -26,7 +27,7 @@ namespace TempProject
     public record MyMessagePackObject([property: Key("p")] string PhoneNumber, [property: Key("c")] int Count);
 }
 """;
-        await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
+        await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, languageVersion: LanguageVersion.CSharp9);
     }
 
     [Fact]

diff --git a/tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs b/tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs
index 72aa5834..a020ee6a 100644
--- a/tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs
+++ b/tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs
@@ -3,6 +3,7 @@
 
 using MessagePack.SourceGenerator.Tests;
 using Microsoft.CodeAnalysis;
+using Microsoft.CodeAnalysis.CSharp;
 using Microsoft.CodeAnalysis.Testing;
 using VerifyCS = CSharpSourceGeneratorVerifier<MessagePack.SourceGenerator.MessagePackGenerator>;
 
@@ -230,7 +231,7 @@ class UnserializableRecordFormatter : IMessagePackFormatter<UnserializableRecord
     }
 }
 """;
-        await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, options: new() { Generator = new() { Formatters = new() { UsesMapMode = usesMapMode } } }, testMethod: $"{nameof(CustomFormatterViaAttributeOnProperty)}({usesMapMode})");
+        await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, options: new() { Generator = new() { Formatters = new() { UsesMapMode = usesMapMode } } }, languageVersion: LanguageVersion.CSharp9, testMethod: $"{nameof(CustomFormatterViaAttributeOnProperty)}({usesMapMode})");
     }
 
     [Theory, PairwiseData]

diff --git a/tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs b/tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs
index 18eecf94..57ae4058 100644
--- a/tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs
+++ b/tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs
@@ -1,6 +1,7 @@
 ﻿// Copyright (c) All contributors. All rights reserved.
 // Licensed under the MIT license. See LICENSE file in the project root for full license information.
 
+using Microsoft.CodeAnalysis.CSharp;
 using VerifyCS = CSharpSourceGeneratorVerifier<MessagePack.SourceGenerator.MessagePackGenerator>;
 
 public class GenericsFormatterTests
@@ -352,7 +353,7 @@ namespace TempProject
     public interface IMyInterface {}
 }
 """;
-        await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
+        await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, languageVersion: LanguageVersion.CSharp9);
     }
 
     [Fact]
@@ -405,7 +406,7 @@ namespace TempProject
     }
 }
 """;
-        await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
+        await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, languageVersion: LanguageVersion.CSharp8);
     }
 
     [Fact]
@@ -432,7 +433,7 @@ namespace TempProject
     }
 }
 """;
-        await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
+        await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, languageVersion: LanguageVersion.CSharp9);
     }
 
     [Fact]

diff --git a/tests/MessagePack.SourceGenerator.Tests/PrivateMemberAccessTests.cs b/tests/MessagePack.SourceGenerator.Tests/PrivateMemberAccessTests.cs
index 59f99d5f..be383c60 100644
--- a/tests/MessagePack.SourceGenerator.Tests/PrivateMemberAccessTests.cs
+++ b/tests/MessagePack.SourceGenerator.Tests/PrivateMemberAccessTests.cs
@@ -7,9 +7,9 @@ using VerifyCS = CSharpSourceGeneratorVerifier<MessagePack.SourceGenerator.Messa
 public class PrivateMemberAccessTests(ITestOutputHelper logger)
 {
     [Theory]
-    [InlineData("class", LanguageVersion.CSharp9)]
+    [InlineData("class", LanguageVersion.CSharp7_3)]
     [InlineData("record", LanguageVersion.CSharp9)]
-    [InlineData("struct", LanguageVersion.CSharp9)]
+    [InlineData("struct", LanguageVersion.CSharp7_3)]
     [InlineData("record struct", LanguageVersion.CSharp10)]
     public async Task FormatterForClassWithPrivateMembers(string type, LanguageVersion version)
     {
@@ -59,10 +59,10 @@ public class PrivateMemberAccessTests(ITestOutputHelper logger)
     }
 
     [Theory]
-    [InlineData("class")]
-    [InlineData("record")]
-    [InlineData("struct")]
-    public async Task FormatterForClassWithPrivateMembers_NonPartialTypes(string type)
+    [InlineData("class", LanguageVersion.CSharp7_3)]
+    [InlineData("record", LanguageVersion.CSharp9)]
+    [InlineData("struct", LanguageVersion.CSharp7_3)]
+    public async Task FormatterForClassWithPrivateMembers_NonPartialTypes(string type, LanguageVersion languageVersion)
     {
         string testSource = $$"""
             using System;
@@ -77,14 +77,14 @@ public class PrivateMemberAccessTests(ITestOutputHelper logger)
                 public int Value { get => value; set => this.value = value; }
             }
             """;
-        await VerifyCS.Test.RunDefaultAsync(logger, testSource, testMethod: $"{nameof(FormatterForClassWithPrivateMembers_NonPartialTypes)}({type})");
+        await VerifyCS.Test.RunDefaultAsync(logger, testSource, languageVersion: languageVersion, testMethod: $"{nameof(FormatterForClassWithPrivateMembers_NonPartialTypes)}({type})");
     }
 
     [Theory]
-    [InlineData("class")]
-    [InlineData("record")]
-    [InlineData("struct")]
-    public async Task FormatterForClassWithPrivateMembers_Nested_NonPartialTypes(string type)
+    [InlineData("class", LanguageVersion.CSharp7_3)]
+    [InlineData("record", LanguageVersion.CSharp9)]
+    [InlineData("struct", LanguageVersion.CSharp7_3)]
+    public async Task FormatterForClassWithPrivateMembers_Nested_NonPartialTypes(string type, LanguageVersion languageVersion)
     {
         string testSource = $$"""
             using System;
@@ -102,6 +102,6 @@ public class PrivateMemberAccessTests(ITestOutputHelper logger)
                 }
             }
             """;
-        await VerifyCS.Test.RunDefaultAsync(logger, testSource, testMethod: $"{nameof(FormatterForClassWithPrivateMembers_Nested_NonPartialTypes)}({type})");
+        await VerifyCS.Test.RunDefaultAsync(logger, testSource, languageVersion: languageVersion, testMethod: $"{nameof(FormatterForClassWithPrivateMembers_Nested_NonPartialTypes)}({type})");
     }
 }

diff --git a/tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorCodeFixVerifier`2.cs b/tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorCodeFixVerifier`2.cs
index 5b58a1f3..56234acc 100644
--- a/tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorCodeFixVerifier`2.cs
+++ b/tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorCodeFixVerifier`2.cs
@@ -19,7 +19,7 @@ internal class CSharpSourceGeneratorCodeFixVerifier<TSourceGenerator, TCodeFix>
             this.CompilerDiagnostics = CompilerDiagnostics.Warnings;
         }
 
-        public LanguageVersion LanguageVersion { get; set; } = LanguageVersion.CSharp9;
+        public LanguageVersion LanguageVersion { get; set; } = LanguageVersion.CSharp7_3;
 
         public ReferencesSet MessagePackReferences { get; set; } = ReferencesSet.MessagePack;
 

diff --git a/tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorVerifier`1+Test.cs b/tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorVerifier`1+Test.cs
index 981bd30e..9da58b2e 100644
--- a/tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorVerifier`1+Test.cs
+++ b/tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorVerifier`1+Test.cs
@@ -43,9 +43,9 @@ internal static partial class CSharpSourceGeneratorVerifier<TSourceGenerator>
 #endif
         }
 
-        public LanguageVersion LanguageVersion { get; set; } = LanguageVersion.CSharp9;
+        public LanguageVersion LanguageVersion { get; set; } = LanguageVersion.CSharp7_3;
 
-        public static Task RunDefaultAsync(ITestOutputHelper logger, string testSource, AnalyzerOptions? options = null, [CallerFilePath] string? testFile = null, [CallerMemberName] string testMethod = null!)
+        public static Task RunDefaultAsync(ITestOutputHelper logger, string testSource, AnalyzerOptions? options = null, LanguageVersion languageVersion = LanguageVersion.CSharp7_3, [CallerFilePath] string? testFile = null, [CallerMemberName] string testMethod = null!)
         {
             options ??= new();
 
@@ -64,7 +64,7 @@ internal static partial class CSharpSourceGeneratorVerifier<TSourceGenerator>
                     partial class {{options.Generator.Resolver.Name}} { }
                 }
                 """;
-            return RunDefaultAsync(logger, testSource, resolverPartialClassSource, testFile, testMethod);
+            return RunDefaultAsync(logger, testSource, resolverPartialClassSource, languageVersion, testFile, testMethod);
         }
 
         public async Task RunDefaultAsync(ITestOutputHelper logger)
@@ -91,7 +91,7 @@ internal static partial class CSharpSourceGeneratorVerifier<TSourceGenerator>
             }
         }
 
-        private static Task RunDefaultAsync(ITestOutputHelper logger, string testSource, string resolverPartialClassSource, [CallerFilePath] string? testFile = null, [CallerMemberName] string testMethod = null!)
+        private static Task RunDefaultAsync(ITestOutputHelper logger, string testSource, string resolverPartialClassSource, LanguageVersion languageVersion, [CallerFilePath] string? testFile = null, [CallerMemberName] string testMethod = null!)
         {
             Test test = new(testFile: testFile, testMethod: testMethod)
             {
@@ -99,6 +99,7 @@ internal static partial class CSharpSourceGeneratorVerifier<TSourceGenerator>
                 {
                     Sources = { testSource, resolverPartialClassSource },
                 },
+                LanguageVersion = languageVersion,
             };
 
             return test.RunDefaultAsync(logger);

```

## File contents (line numbers in the gutter; quote the text after '| ')

### tests/MessagePack.SourceGenerator.Tests/CustomStringKeyFormatterTests.cs at head (2f9324f9), full file
```
    1| // Copyright (c) All contributors. All rights reserved.
    2| // Licensed under the MIT license. See LICENSE file in the project root for full license information.
    3| 
    4| using Microsoft.CodeAnalysis.CSharp;
    5| using VerifyCS = CSharpSourceGeneratorVerifier<MessagePack.SourceGenerator.MessagePackGenerator>;
    6| 
    7| public class CustomStringKeyFormatterTests
    8| {
    9|     private readonly ITestOutputHelper testOutputHelper;
   10| 
   11|     public CustomStringKeyFormatterTests(ITestOutputHelper testOutputHelper)
   12|     {
   13|         this.testOutputHelper = testOutputHelper;
   14|     }
   15| 
   16|     [Fact]
   17|     public async Task RecordWithPrimaryConstructor()
   18|     {
   19|         string testSource = """
   20| using System;
   21| using System.Collections.Generic;
   22| using MessagePack;
   23| 
   24| namespace TempProject
   25| {
   26|     [MessagePackObject]
   27|     public record MyMessagePackObject([property: Key("p")] string PhoneNumber, [property: Key("c")] int Count);
   28| }
   29| """;
   30|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, languageVersion: LanguageVersion.CSharp9);
   31|     }
   32| 
   33|     [Fact]
   34|     public async Task RecordWithWithInitOnlyProps()
   35|     {
   36|         string testSource = """
   37| using System;
   38| using System.Collections.Generic;
   39| using MessagePack;
   40| 
   41| namespace TempProject
   42| {
   43|     [MessagePackObject]
   44|     public class MyMessagePackObject
   45|     {
   46|         public MyMessagePackObject(string phoneNumber, int count)
   47|         {
   48|             PhoneNumber = phoneNumber;
   49|             Count = count;
   50|         }
   51| 
   52|         [Key("p")]
   53|         public string PhoneNumber { get; set; }
   54| 
   55|         [Key("c")]
   56|         public int Count { get; set; }
   57|     };
   58| }
   59| """;
   60|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
   61|     }
   62| }
```

### tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs at head (2f9324f9), full file
```
    1| // Copyright (c) All contributors. All rights reserved.
    2| // Licensed under the MIT license. See LICENSE file in the project root for full license information.
    3| 
    4| using MessagePack.SourceGenerator.Tests;
    5| using Microsoft.CodeAnalysis;
    6| using Microsoft.CodeAnalysis.CSharp;
    7| using Microsoft.CodeAnalysis.Testing;
    8| using VerifyCS = CSharpSourceGeneratorVerifier<MessagePack.SourceGenerator.MessagePackGenerator>;
    9| 
   10| public class GenerationTests
   11| {
   12|     private const string Preamble = @"
   13| using MessagePack;
   14| ";
   15| 
   16|     private readonly ITestOutputHelper testOutputHelper;
   17| 
   18|     public GenerationTests(ITestOutputHelper testOutputHelper)
   19|     {
   20|         this.testOutputHelper = testOutputHelper;
   21|     }
   22| 
   23|     [Theory, PairwiseData]
   24|     public async Task EnumFormatter(ContainerKind container, bool usesMapMode)
   25|     {
   26|         string testSource = """
   27| [MessagePackObject]
   28| internal class MyMessagePackObject
   29| {
   30|     [Key(0)]
   31|     internal MyEnum EnumValue { get; set; }
   32| }
   33| 
   34| internal enum MyEnum
   35| {
   36|     A, B, C
   37| }
   38| """;
   39|         testSource = TestUtilities.WrapTestSource(testSource, container);
   40| 
   41|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, options: new() { Generator = new() { Formatters = new() { UsesMapMode = usesMapMode } } }, testMethod: $"{nameof(EnumFormatter)}({container}, {usesMapMode})");
   42|     }
   43| 
   44|     [Fact]
   45|     public async Task EnumFormatter_CollidingTypeNames()
   46|     {
   47|         string testSource = """
   48| using MessagePack;
   49| 
   50| [MessagePackObject]
   51| internal class MyMessagePackObject
   52| {
   53|     [Key(0)]
   54|     internal NS1.MyEnum EnumValue1 { get; set; }
   55| 
   56|     [Key(1)]
   57|     internal NS2.MyEnum EnumValue2 { get; set; }
   58| }
   59| 
   60| namespace NS1 {
   61|     internal enum MyEnum
   62|     {
   63|         A, B, C
   64|     }
   65| }
   66| 
   67| namespace NS2 {
   68|     internal enum MyEnum
   69|     {
   70|         D, E
   71|     }
   72| }
   73| """;
   74| 
   75|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
   76|     }
   77| 
   78|     [Fact]
   79|     public async Task GenericType_CollidingTypeNames()
   80|     {
   81|         string testSource = """
   82| using MessagePack;
   83| 
   84| [MessagePackObject]
   85| internal class MyMessagePackObject
   86| {
   87|     [Key(0)]
   88|     internal NS1.MyType<int> Value1 { get; set; }
   89| 
   90|     [Key(1)]
   91|     internal NS2.MyType<int> Value2 { get; set; }
   92| }
   93| 
   94| namespace NS1 {
   95|     [MessagePackObject]
   96|     internal class MyType<T>
   97|     {
   98|         [Key(0)]
   99|         internal string Foo { get; set; }
  100|     }
  101| }
  102| 
  103| namespace NS2 {
  104|     [MessagePackObject]
  105|     internal class MyType<T>
  106|     {
  107|         [Key(0)]
  108|         internal string Foo { get; set; }
  109|     }
  110| }
  111| """;
  112| 
  113|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  114|     }
  115| 
  116|     [Fact]
  117|     public async Task NonGenericType_CollidingTypeNames()
  118|     {
  119|         string testSource = """
  120| using MessagePack;
  121| 
  122| [MessagePackObject]
  123| internal class MyMessagePackObject
  124| {
  125|     [Key(0)]
  126|     internal NS1.MyType Value1 { get; set; }
  127| 
  128|     [Key(1)]
  129|     internal NS2.MyType Value2 { get; set; }
  130| }
  131| 
  132| namespace NS1 {
  133|     [MessagePackObject]
  134|     internal class MyType
  135|     {
  136|         [Key(0)]
  137|         internal string Foo { get; set; }
  138|     }
  139| }
  140| 
  141| namespace NS2 {
  142|     [MessagePackObject]
  143|     internal class MyType
  144|     {
  145|         [Key(0)]
  146|         internal string Foo { get; set; }
  147|     }
  148| }
  149| """;
  150| 
  151|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  152|     }
  153| 
  154|     [Fact]
  155|     public async Task MixType_CollidingTypeNames()
  156|     {
  157|         string testSource = """
  158| using MessagePack;
  159| 
  160| [MessagePackObject]
  161| internal class MyMessagePackObject
  162| {
  163|     [Key(0)]
  164|     internal NS1.MyType Value1 { get; set; }
  165| 
  166|     [Key(1)]
  167|     internal NS2.MyType Value2 { get; set; }
  168| 
  169|     [Key(2)]
  170|     internal NS3.MyType<int> Value3 { get; set; }
  171| }
  172| 
  173| namespace NS1 {
  174|     internal enum MyType
  175|     {
  176|         A, B
  177|     }
  178| }
  179| 
  180| namespace NS2 {
  181|     [MessagePackObject]
  182|     internal class MyType
  183|     {
  184|         [Key(0)]
  185|         internal string Foo { get; set; }
  186|     }
  187| }
  188| 
  189| namespace NS3 {
  190|     [MessagePackObject]
  191|     internal class MyType<T>
  192|     {
  193|         [Key(0)]
  194|         internal string Foo { get; set; }
  195|     }
  196| }
  197| """;
  198| 
  199|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  200|     }
  201| 
  202|     [Theory, PairwiseData]
  203|     public async Task CustomFormatterViaAttributeOnProperty(bool usesMapMode)
  204|     {
  205|         string testSource = """
  206| using MessagePack;
  207| using MessagePack.Formatters;
  208| 
  209| [MessagePackObject]
  210| internal record HasPropertyWithCustomFormatterAttribute
  211| {
  212|     [Key(0), MessagePackFormatter(typeof(UnserializableRecordFormatter))]
  213|     internal UnserializableRecord CustomValue { get; set; }
  214| }
  215| 
  216| record UnserializableRecord
  217| {
  218|     internal int Value { get; set; }
  219| }
  220| 
  221| class UnserializableRecordFormatter : IMessagePackFormatter<UnserializableRecord>
  222| {
  223|     public void Serialize(ref MessagePackWriter writer, UnserializableRecord value, MessagePackSerializerOptions options)
  224|     {
  225|         writer.WriteInt32(value.Value);
  226|     }
  227| 
  228|     public UnserializableRecord Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options)
  229|     {
  230|         return new UnserializableRecord { Value = reader.ReadInt32() };
  231|     }
  232| }
  233| """;
  234|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, options: new() { Generator = new() { Formatters = new() { UsesMapMode = usesMapMode } } }, languageVersion: LanguageVersion.CSharp9, testMethod: $"{nameof(CustomFormatterViaAttributeOnProperty)}({usesMapMode})");
  235|     }
  236| 
  237|     [Theory, PairwiseData]
  238|     public async Task UnionFormatter(ContainerKind container)
  239|     {
  240|         string testSource = """
  241| [Union(0, typeof(Derived1))]
  242| [Union(1, typeof(Derived2))]
  243| internal interface IMyType
  244| {
  245| }
  246| 
  247| [MessagePackObject]
  248| internal class Derived1 : IMyType {}
  249| 
  250| [MessagePackObject]
  251| internal class Derived2 : IMyType {}
  252| 
  253| [MessagePackObject]
  254| internal class MyMessagePackObject
  255| {
  256|     [Key(0)]
  257|     internal IMyType UnionValue { get; set; }
  258| }
  259| """;
  260|         testSource = TestUtilities.WrapTestSource(testSource, container);
  261| 
  262|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, testMethod: $"{nameof(UnionFormatter)}({container})");
  263|     }
  264| 
  265|     [Fact]
  266|     public async Task ArrayTypedProperty()
  267|     {
  268|         string testSource = """
  269| using MessagePack;
  270| using System.Collections.Generic;
  271| 
  272| [MessagePackObject]
  273| internal class ContainerObject
  274| {
  275|     [Key(0)]
  276|     internal SubObject[] ArrayOfCustomObjects { get; set; }
  277| 
  278|     [Key(1)]
  279|     internal List<SubObject>[] ArrayOfCustomObjectList { get; set; }
  280| }
  281| 
  282| [MessagePackObject]
  283| internal class SubObject
  284| {
  285| }
  286| """;
  287|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  288|     }
  289| 
  290|     [Fact]
  291|     public async Task GenericType()
  292|     {
  293|         string testSource = """
  294| using MessagePack;
  295| using System;
  296| 
  297| [MessagePackObject]
  298| internal class ContainerObject
  299| {
  300|     [Key(0)]
  301|     internal MyGenericType<int> TupleProperty { get; set; }
  302| }
  303| 
  304| [MessagePackObject]
  305| internal class MyGenericType<T>
  306| {
  307|     [Key(0)]
  308|     internal T Value { get; set; }
  309| }
  310| """;
  311|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  312|     }
  313| 
  314|     [Fact]
  315|     public async Task GenericTypeArg()
  316|     {
  317|         string testSource = """
  318| using MessagePack;
  319| using System;
  320| 
  321| [MessagePackObject]
  322| public class GenericClass<T1, T2>
  323| {
  324|     [Key(0)]
  325|     public T1 MyProperty0 { get; set; }
  326| 
  327|     [Key(1)]
  328|     public T2 MyProperty1 { get; set; }
  329| }
  330| """;
  331|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  332|     }
  333| 
  334|     [Fact]
  335|     public async Task AdditionalAllowTypes()
  336|     {
  337|         string testSource = Preamble + """
  338| class MyCustomType { }
  339| 
  340| [MessagePackObject]
  341| class TypeWithAutoGeneratedFormatter
  342| {
  343|     [Key(0)]
  344|     public MyCustomType Value { get; set; }
  345| }
  346| """;
  347|         await VerifyCS.Test.RunDefaultAsync(
  348|             this.testOutputHelper,
  349|             testSource,
  350|             options: new()
  351|             {
  352|                 AssumedFormattableTypes = ImmutableHashSet<FormattableType>.Empty
  353|                     .Add(new FormattableType(new QualifiedTypeName(null, TypeKind.Class, "MyCustomType"))),
  354|             });
  355|     }
  356| 
  357|     [Fact]
  358|     public async Task AdditionalFormatterTypes()
  359|     {
  360|         string testSource = Preamble + """
  361| [assembly: MessagePackKnownFormatterAttribute(typeof(MyCustomTypeFormatter))]
  362| 
  363| [MessagePackObject]
  364| class TypeWithAutoGeneratedFormatter
  365| {
  366|     [Key(0)]
  367|     public MyCustomType Value { get; set; }
  368| }
  369| """;
  370| 
  371|         string defineSource = Preamble + """
  372|         public class MyCustomType { }
  373|         
  374|         public class MyCustomTypeFormatter : MessagePack.Formatters.IMessagePackFormatter<MyCustomType>
  375|         {
  376|             public void Serialize(ref MessagePackWriter writer, MyCustomType value, MessagePackSerializerOptions options)
  377|             {
  378|                 throw new System.NotImplementedException();
  379|             }
  380|         
  381|             public MyCustomType Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options)
  382|             {
  383|                 throw new System.NotImplementedException();
  384|             }
  385|         }
  386|         """;
  387|         await new VerifyCS.Test
  388|         {
  389|             TestState =
  390|             {
  391|                 Sources = { testSource },
  392|                 AdditionalProjects =
  393|                 {
  394|                     ["DefiningProject"] = { Sources = { defineSource } },
  395|                 },
  396|                 AdditionalProjectReferences = { "DefiningProject" },
  397|             },
  398|         }.RunAsync();
  399|     }
  400| 
  401|     [Fact]
  402|     public async Task AdditionalFormatterTypes_RedundantAttibute()
  403|     {
  404|         string testSource = Preamble + """
  405| [assembly: MessagePackKnownFormatterAttribute(typeof(MyCustomTypeFormatter))]
  406| 
  407| class MyCustomType { }
  408| 
  409| class MyCustomTypeFormatter : MessagePack.Formatters.IMessagePackFormatter<MyCustomType>
  410| {
  411|     public void Serialize(ref MessagePackWriter writer, MyCustomType value, MessagePackSerializerOptions options)
  412|     {
  413|         throw new System.NotImplementedException();
  414|     }
  415| 
  416|     public MyCustomType Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options)
  417|     {
  418|         throw new System.NotImplementedException();
  419|     }
  420| }
  421| 
  422| [MessagePackObject]
  423| class TypeWithAutoGeneratedFormatter
  424| {
  425|     [Key(0)]
  426|     public MyCustomType Value { get; set; }
  427| }
  428| """;
  429|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  430|     }
  431| 
  432|     [Fact]
  433|     public async Task ImplicitFormatterTypes()
  434|     {
  435|         string testSource = Preamble + """
  436| class MyCustomType { }
  437| 
  438| class MyCustomTypeFormatter : MessagePack.Formatters.IMessagePackFormatter<MyCustomType>
  439| {
  440|     public void Serialize(ref MessagePackWriter writer, MyCustomType value, MessagePackSerializerOptions options)
  441|     {
  442|         throw new System.NotImplementedException();
  443|     }
  444| 
  445|     public MyCustomType Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options)
  446|     {
  447|         throw new System.NotImplementedException();
  448|     }
  449| }
  450| 
  451| [MessagePackObject]
  452| class TypeWithAutoGeneratedFormatter
  453| {
  454|     [Key(0)]
  455|     public MyCustomType Value { get; set; }
  456| }
  457| """;
  458|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  459|     }
  460| 
  461|     [Fact]
  462|     public async Task NoGenerationForAnnotationOnly()
  463|     {
  464|         string testSource = """
  465| using MessagePack;
  466| using System;
  467| 
  468| [MessagePackObject]
  469| internal class ContainerObject
  470| {
  471|     [Key(0)]
  472|     internal MyGenericType<int> TupleProperty { get; set; }
  473| }
  474| 
  475| [MessagePackObject]
  476| internal class MyGenericType<T>
  477| {
  478|     [Key(0)]
  479|     internal T Value { get; set; }
  480| }
  481| """;
  482|         await new VerifyCS.Test(ReferencesSet.MessagePackAnnotations)
  483|         {
  484|             TestState =
  485|             {
  486|                 Sources = { testSource },
  487|             },
  488|         }.RunAsync();
  489|     }
  490| 
  491|     [Fact]
  492|     public async Task NestedMessagePackObjects()
  493|     {
  494|         string testSource = """
  495|             using MessagePack;
  496|             using System;
  497| 
  498|             namespace A
  499|             {
  500|                 [MessagePackObject]
  501|                 internal class B
  502|                 {
  503|                     [MessagePackObject]
  504|                     internal class C
  505|                     {
  506|                     }
  507|                 }
  508|             }
  509|             """;
  510|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  511|     }
  512| 
  513|     [Fact]
  514|     public async Task NestedMessagePackObjects_Array()
  515|     {
  516|         string testSource = """
  517|             using MessagePack;
  518|             using System;
  519| 
  520|             namespace A
  521|             {
  522|                 [MessagePackObject]
  523|                 internal class B
  524|                 {
  525|                     [MessagePackObject]
  526|                     internal class C
  527|                     {
  528|                     }
  529| 
  530|                     [Key(0)]
  531|                     internal C[] array;
  532|                 }
  533|             }
  534|             """;
  535|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  536|     }
  537| 
  538|     [Fact]
  539|     public async Task CustomFormatterWithSingletonPattern()
  540|     {
  541|         string testSource = """
  542|             using MessagePack;
  543|             using MessagePack.Formatters;
  544|             class A {}
  545|             class F : IMessagePackFormatter<A> {
  546|                 public static readonly IMessagePackFormatter<A> Instance = new F();
  547|                 private F() {}
  548|                 public void Serialize(ref MessagePackWriter writer, A value, MessagePackSerializerOptions options) {}
  549|                 public A Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options) => default;
  550|             }
  551|             [MessagePackObject]
  552|             class G {
  553|                 [Key(0), MessagePackFormatter(typeof(F))]
  554|                 internal A a;
  555|             }
  556|             """;
  557|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  558|     }
  559| 
  560|     [Fact]
  561|     public async Task SpecifyFormatterFromStockSet()
  562|     {
  563|         string testSource = """
  564|             using MessagePack;
  565|             using MessagePack.Formatters;
  566|             [MessagePackObject]
  567|             class G {
  568|                 [Key(0), MessagePackFormatter(typeof(StringInterningFormatter))]
  569|                 internal string a;
  570|             }
  571|             """;
  572|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  573|     }
  574| 
  575|     [Fact]
  576|     public async Task ExcludeFormatterFromSourceGeneratedResolver()
  577|     {
  578|         string testSource = """
  579|             using MessagePack;
  580|             using MessagePack.Formatters;
  581|             class A {}
  582|             [ExcludeFormatterFromSourceGeneratedResolver]
  583|             class F : IMessagePackFormatter<A> {
  584|                 public void Serialize(ref MessagePackWriter writer, A value, MessagePackSerializerOptions options) {}
  585|                 public A Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options) => default;
  586|             }
  587|             """;
  588| 
  589|         // This test is *not* expected to produce any generated files.
  590|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  591|     }
  592| 
  593|     [Fact]
  594|     public async Task NonDefaultDeserializingConstructor_Private()
  595|     {
  596|         string testSource = """
  597|             using MessagePack;
  598|             [MessagePackObject]
  599|             partial class A {
  600|                 [SerializationConstructor]
  601|                 A(int x) => this.X = x;
  602| 
  603|                 [Key(0)]
  604|                 internal int X { get; }
  605|             }
  606|             """;
  607| 
  608|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  609|     }
  610| 
  611|     [Fact]
  612|     public async Task DeserializingConstructorParameterMemberTypeAssignability_MemberAssignsToParamType()
  613|     {
  614|         string testSource = """
  615|             using MessagePack;
  616|             using System.Linq;
  617|             using System.Collections.Generic;
  618|             [MessagePackObject]
  619|             class A {
  620|                 [SerializationConstructor]
  621|                 internal A(IReadOnlyList<int> x) => this.X = x.ToList();
  622| 
  623|                 [Key(0)]
  624|                 internal List<int> X { get; }
  625|             }
  626|             """;
  627| 
  628|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  629|     }
  630| 
  631|     [Fact]
  632|     public async Task DeserializingConstructorParameterMemberTypeAssignability_Incompatible()
  633|     {
  634|         string testSource = """
  635|             using MessagePack;
  636|             using System.Linq;
  637|             using System.Collections.Generic;
  638|             using System.Collections.Immutable;
  639|             [MessagePackObject]
  640|             class A {
  641|                 [SerializationConstructor]
  642|                 internal A({|#0:ImmutableList<int> x|}) => this.X = x.ToList();
  643| 
  644|                 [Key(0)]
  645|                 internal List<int> X { get; }
  646|             }
  647|             """;
  648| 
  649|         await new VerifyCS.Test
  650|         {
  651|             TestState =
  652|             {
  653|                 Sources = { testSource },
  654|             },
  655|             ExpectedDiagnostics = { DiagnosticResult.CompilerError("MsgPack007").WithLocation(0) },
  656|         }.RunDefaultAsync(this.testOutputHelper);
  657|     }
  658| }
```

### tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs at head (2f9324f9), full file
```
    1| ﻿// Copyright (c) All contributors. All rights reserved.
    2| // Licensed under the MIT license. See LICENSE file in the project root for full license information.
    3| 
    4| using Microsoft.CodeAnalysis.CSharp;
    5| using VerifyCS = CSharpSourceGeneratorVerifier<MessagePack.SourceGenerator.MessagePackGenerator>;
    6| 
    7| public class GenericsFormatterTests
    8| {
    9|     private readonly ITestOutputHelper testOutputHelper;
   10| 
   11|     public GenericsFormatterTests(ITestOutputHelper testOutputHelper)
   12|     {
   13|         this.testOutputHelper = testOutputHelper;
   14|     }
   15| 
   16|     [Fact]
   17|     public async Task NullableFormatter()
   18|     {
   19|         string testSource = """
   20| using System;
   21| using System.Collections.Generic;
   22| using MessagePack;
   23| 
   24| namespace TempProject
   25| {
   26|     [MessagePackObject]
   27|     public class MyObject
   28|     {
   29|         [Key(0)]
   30|         public int? ValueNullableInt { get; set; }
   31|         [Key(1)]
   32|         public MyEnum? ValueNullableEnum { get; set; }
   33|         [Key(2)]
   34|         public ValueTuple<int, long>? ValueNullableStruct { get; set; }
   35|     }
   36| 
   37|     public enum MyEnum
   38|     {
   39|         A, B, C
   40|     }
   41| }
   42| """;
   43|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
   44|     }
   45| 
   46|     [Fact]
   47|     public async Task WellKnownGenericsFormatter()
   48|     {
   49|         string testSource = """
   50| using System;
   51| using System.Collections.Generic;
   52| using MessagePack;
   53| 
   54| namespace TempProject
   55| {
   56|     [MessagePackObject]
   57|     public class MyObject
   58|     {
   59|         [Key(0)]
   60|         public List<int> ValueList { get; set; }
   61|         [Key(1)]
   62|         public List<List<int>> ValueListNested { get; set; }
   63|         [Key(2)]
   64|         public ValueTuple<int, string, long> ValueValueTuple { get; set; }
   65|     }
   66| }
   67| """;
   68|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
   69|     }
   70| 
   71|     [Fact]
   72|     public async Task GenericsUnionFormatter()
   73|     {
   74|         string testSource = """
   75| using System;
   76| using System.Collections.Generic;
   77| using MessagePack;
   78| 
   79| namespace TempProject
   80| {
   81|     [MessagePackObject]
   82|     [Union(0, typeof(Wrapper<string>))]
   83|     [Union(1, typeof(Wrapper<int[]>))]
   84|     [Union(2, typeof(Wrapper<IEnumerable<Guid>>))]
   85|     public class Wrapper<T>
   86|     {
   87|         [Key(0)]
   88|         public T Content { get; set; }
   89|     }
   90| }
   91| """;
   92|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
   93|     }
   94| 
   95|     [Fact]
   96|     public async Task GenericsUnionFormatter_Nested()
   97|     {
   98|         string testSource = """
   99| using System;
  100| using System.Collections.Generic;
  101| using MessagePack;
  102| 
  103| namespace TempProject
  104| {
  105|     [MessagePackObject]
  106|     [Union(0, typeof(Wrapper<string>))]
  107|     [Union(1, typeof(Wrapper<int[]>))]
  108|     [Union(2, typeof(Wrapper<IEnumerable<Guid>>))]
  109|     public class Wrapper<T>
  110|     {
  111|         [Key(0)]
  112|         public List<T> Content1 { get; set; }
  113|         [Key(1)]
  114|         public MyGenericObject<T> Content2 { get; set; }
  115|     }
  116| 
  117|     [MessagePackObject]
  118|     public class MyGenericObject<T>
  119|     {
  120|         [Key(0)]
  121|         public MyInnerGenericObject<T> Content { get; set; }
  122|     }
  123| 
  124|     [MessagePackObject]
  125|     public class MyInnerGenericObject<T>
  126|     {
  127|     }
  128| }
  129| """;
  130|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  131|     }
  132| 
  133|     [Fact]
  134|     public async Task NestedGenericTypes()
  135|     {
  136|         string testSource = """
  137| using System;
  138| using System.Collections.Generic;
  139| using MessagePack;
  140| 
  141| namespace TempProject
  142| {
  143|     [MessagePackObject]
  144|     public class MyObject : Wrapper<MyObject2>
  145|     {
  146|     }
  147| 
  148|     [MessagePackObject]
  149|     public class MyObject2
  150|     {}
  151| 
  152|     [MessagePackObject]
  153|     public class Wrapper<T>
  154|     {
  155|         [Key(0)]
  156|         public List<T> Content1 { get; set; }
  157|         [Key(1)]
  158|         public MyGenericObject<T> Content2 { get; set; }
  159|     }
  160| 
  161|     [MessagePackObject]
  162|     public class MyGenericObject<T>
  163|     {
  164|         [Key(0)]
  165|         public MyInnerGenericObject<T> Content { get; set; }
  166|         [Key(1)]
  167|         public T[] Content2 { get; set; }
  168|     }
  169| 
  170|     [MessagePackObject]
  171|     public class MyInnerGenericObject<T>
  172|     {
  173|     }
  174| }
  175| """;
  176|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  177|     }
  178| 
  179|     [Fact]
  180|     public async Task GenericsOfTFormatter_WithKnownTypes()
  181|     {
  182|         string testSource = """
  183| using System;
  184| using System.Collections.Generic;
  185| using MessagePack;
  186| 
  187| namespace TempProject
  188| {
  189|     [MessagePackObject]
  190|     public class MyObject : MyGenericObject<MyObject2>
  191|     {
  192|     }
  193| 
  194|     [MessagePackObject]
  195|     public class MyObject2
  196|     { }
  197| 
  198|     [MessagePackObject]
  199|     public class MyGenericObject<T>
  200|     {
  201|         [Key(0)]
  202|         public List<T> Content1 { get; set; }
  203|         [Key(1)]
  204|         public T[] Content2 { get; set; }
  205|     }
  206| }
  207| """;
  208|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  209|     }
  210| 
  211|     [Fact]
  212|     public async Task GenericsOfTFormatter()
  213|     {
  214|         string testSource = """
  215| using System;
  216| using System.Collections.Generic;
  217| using MessagePack;
  218| 
  219| namespace TempProject
  220| {
  221|     [MessagePackObject]
  222|     public class MyGenericObject<T>
  223|     {
  224|         [Key(0)]
  225|         public T Content { get; set; }
  226|     }
  227| 
  228|     [MessagePackObject]
  229|     public class MyObject
  230|     {
  231|         [Key(0)]
  232|         public MyGenericObject<int> Value { get; set; }
  233|     }
  234| 
  235|     [MessagePackObject]
  236|     public class MyObjectNested
  237|     {
  238|         [Key(0)]
  239|         public MyGenericObject<MyGenericObject<int>> Value { get; set; }
  240|     }
  241| }
  242| """;
  243|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  244|     }
  245| 
  246|     [Fact]
  247|     public async Task GenericsOfT1T2Formatter()
  248|     {
  249|         string testSource = """
  250| using System;
  251| using System.Collections.Generic;
  252| using MessagePack;
  253| 
  254| namespace TempProject
  255| {
  256|     [MessagePackObject]
  257|     public class MyGenericObject<T1, T2>
  258|     {
  259|         [Key(0)]
  260|         public T1 ValueA { get; set; }
  261|         [Key(1)]
  262|         public T2 ValueB { get; set; }
  263|     }
  264| 
  265|     [MessagePackObject]
  266|     public class MyObject
  267|     {
  268|         [Key(0)]
  269|         public MyGenericObject<int, string> Value { get; set; }
  270|     }
  271| 
  272|     [MessagePackObject]
  273|     public class MyObjectNested
  274|     {
  275|         [Key(0)]
  276|         public MyGenericObject<MyGenericObject<int, string>, MyGenericObject<int, string>> Value { get; set; }
  277|     }
  278| }
  279| """;
  280|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  281|     }
  282| 
  283|     [Fact]
  284|     public async Task GenericsOfTFormatter_FormatterOnly()
  285|     {
  286|         string testSource = """
  287| using System;
  288| using System.Collections.Generic;
  289| using MessagePack;
  290| 
  291| namespace TempProject
  292| {
  293|     // This type is not used by the project.
  294|     // It may be referenced by other projects.
  295|     [MessagePackObject]
  296|     public class MyGenericObject<T>
  297|     {
  298|         [Key(0)]
  299|         public T Content { get; set; }
  300|     }
  301| }
  302| """;
  303|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  304|     }
  305| 
  306|     [Fact]
  307|     public async Task Generics_Constraints_Type()
  308|     {
  309|         string testSource = """
  310| using System;
  311| using System.Collections.Generic;
  312| using MessagePack;
  313| 
  314| namespace TempProject
  315| {
  316|     [MessagePackObject]
  317|     public class MyGenericObject<T>
  318|         where T : IDisposable
  319|     {
  320|         [Key(0)]
  321|         public T Content { get; set; }
  322|     }
  323| }
  324| """;
  325|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  326|     }
  327| 
  328|     [Fact]
  329|     public async Task Generics_Constraints_NullableReferenceType()
  330|     {
  331|         string testSource = """
  332| #nullable enable
  333| 
  334| using System;
  335| using System.Collections.Generic;
  336| using MessagePack;
  337| 
  338| namespace TempProject
  339| {
  340|     [MessagePackObject]
  341|     public class MyGenericObject<T1, T2, T3, T4>
  342|         where T1 : MyClass?
  343|         where T2 : MyClass
  344|         where T3 : MyGenericClass<MyGenericClass<MyClass?>?>?
  345|         where T4 : MyClass, IMyInterface?
  346|     {
  347|         [Key(0)]
  348|         public T1? Content { get; set; }
  349|     }
  350| 
  351|     public class MyClass {}
  352|     public class MyGenericClass<T> {}
  353|     public interface IMyInterface {}
  354| }
  355| """;
  356|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, languageVersion: LanguageVersion.CSharp9);
  357|     }
  358| 
  359|     [Fact]
  360|     public async Task Generics_Constraints_Struct()
  361|     {
  362|         string testSource = """
  363| using System;
  364| using System.Collections.Generic;
  365| using MessagePack;
  366| 
  367| namespace TempProject
  368| {
  369|     [MessagePackObject]
  370|     public class MyGenericObject<T>
  371|         where T : struct
  372|     {
  373|         [Key(0)]
  374|         public T Content { get; set; }
  375|     }
  376| }
  377| """;
  378|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  379|     }
  380| 
  381|     [Fact]
  382|     public async Task Generics_Constraints_Multiple()
  383|     {
  384|         string testSource = """
  385| using System;
  386| using System.Collections.Generic;
  387| using MessagePack;
  388| 
  389| namespace TempProject
  390| {
  391|     [MessagePackObject]
  392|     public class MyGenericObject<T1, T2, T3, T4>
  393|         where T1 : struct
  394|         where T2 : IDisposable, new()
  395|         where T3 : notnull
  396|         where T4 : unmanaged
  397|     {
  398|         [Key(0)]
  399|         public T1 Content1 { get; set; }
  400|         [Key(1)]
  401|         public T2 Content2 { get; set; }
  402|         [Key(2)]
  403|         public T3 Content3 { get; set; }
  404|         [Key(3)]
  405|         public T4 Content4 { get; set; }
  406|     }
  407| }
  408| """;
  409|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, languageVersion: LanguageVersion.CSharp8);
  410|     }
  411| 
  412|     [Fact]
  413|     public async Task Generics_Constraints_ReferenceType_Nullable()
  414|     {
  415|         string testSource = """
  416| #nullable enable
  417| 
  418| using System;
  419| using System.Collections.Generic;
  420| using MessagePack;
  421| 
  422| namespace TempProject
  423| {
  424|     [MessagePackObject]
  425|     public class MyGenericObject<T1, T2>
  426|         where T1 : class?
  427|         where T2 : class
  428|     {
  429|         [Key(0)]
  430|         public T1? Content1 { get; set; }
  431|         [Key(1)]
  432|         public T2? Content2 { get; set; }
  433|     }
  434| }
  435| """;
  436|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, languageVersion: LanguageVersion.CSharp9);
  437|     }
  438| 
  439|     [Fact]
  440|     public async Task Generics_Defined_In_ReferencedProject()
  441|     {
  442|         string defineSource = """
  443| using System;
  444| using System.Collections.Generic;
  445| using MessagePack;
  446| 
  447| namespace TempProject
  448| {
  449|     [MessagePackObject]
  450|     public class MyGenericObject<T>
  451|     {
  452|         [Key(0)]
  453|         public T Content { get; set; }
  454|     }
  455| 
  456|     [GeneratedMessagePackResolver]
  457|     partial class MyResolver { }
  458| }
  459| """;
  460| 
  461|         string usageSource = """
  462| using System;
  463| using System.Collections.Generic;
  464| using MessagePack;
  465| 
  466| namespace TempProject
  467| {
  468|     [MessagePackObject]
  469|     public class MyObject
  470|     {
  471|         [Key(0)]
  472|         public MyGenericObject<int> Value { get; set; }
  473|     }
  474| 
  475|     [MessagePackObject]
  476|     public class MyObjectNested
  477|     {
  478|         [Key(0)]
  479|         public MyGenericObject<MyGenericObject<int>> Value { get; set; }
  480|     }
  481| }
  482| """;
  483|         await new VerifyCS.Test
  484|         {
  485|             TestState =
  486|             {
  487|                 Sources = { usageSource },
  488|                 AdditionalProjects =
  489|                 {
  490|                     ["DefiningProject"] = { Sources = { defineSource } },
  491|                 },
  492|                 AdditionalProjectReferences = { "DefiningProject" },
  493|             },
  494|         }.RunAsync();
  495|     }
  496| }
```

### tests/MessagePack.SourceGenerator.Tests/PrivateMemberAccessTests.cs at head (2f9324f9), full file
```
    1| ﻿// Copyright (c) All contributors. All rights reserved.
    2| // Licensed under the MIT license. See LICENSE file in the project root for full license information.
    3| 
    4| using Microsoft.CodeAnalysis.CSharp;
    5| using VerifyCS = CSharpSourceGeneratorVerifier<MessagePack.SourceGenerator.MessagePackGenerator>;
    6| 
    7| public class PrivateMemberAccessTests(ITestOutputHelper logger)
    8| {
    9|     [Theory]
   10|     [InlineData("class", LanguageVersion.CSharp7_3)]
   11|     [InlineData("record", LanguageVersion.CSharp9)]
   12|     [InlineData("struct", LanguageVersion.CSharp7_3)]
   13|     [InlineData("record struct", LanguageVersion.CSharp10)]
   14|     public async Task FormatterForClassWithPrivateMembers(string type, LanguageVersion version)
   15|     {
   16|         string testSource = $$"""
   17|             using System;
   18|             using MessagePack;
   19| 
   20|             [MessagePackObject]
   21|             partial {{type}} MyObject
   22|             {
   23|                 [Key(0)]
   24|                 private int value;
   25|                 [IgnoreMember]
   26|                 public int Value { get => value; set => this.value = value; }
   27|             }
   28|             """;
   29|         await new VerifyCS.Test(testMethod: $"{nameof(FormatterForClassWithPrivateMembers)}({type})")
   30|         {
   31|             TestState =
   32|             {
   33|                 Sources = { testSource },
   34|             },
   35|             LanguageVersion = version,
   36|         }.RunDefaultAsync(logger);
   37|     }
   38| 
   39|     [Fact]
   40|     public async Task FormatterForClassWithPrivateMembers_WithNamespace()
   41|     {
   42|         string testSource = $$"""
   43|             using System;
   44|             using MessagePack;
   45| 
   46|             namespace A
   47|             {
   48|                 [MessagePackObject]
   49|                 partial class MyObject
   50|                 {
   51|                     [Key(0)]
   52|                     private int value;
   53|                     [IgnoreMember]
   54|                     public int Value { get => value; set => this.value = value; }
   55|                 }
   56|             }
   57|             """;
   58|         await VerifyCS.Test.RunDefaultAsync(logger, testSource);
   59|     }
   60| 
   61|     [Theory]
   62|     [InlineData("class", LanguageVersion.CSharp7_3)]
   63|     [InlineData("record", LanguageVersion.CSharp9)]
   64|     [InlineData("struct", LanguageVersion.CSharp7_3)]
   65|     public async Task FormatterForClassWithPrivateMembers_NonPartialTypes(string type, LanguageVersion languageVersion)
   66|     {
   67|         string testSource = $$"""
   68|             using System;
   69|             using MessagePack;
   70| 
   71|             [MessagePackObject]
   72|             {{type}} {|MsgPack011:MyObject|}
   73|             {
   74|                 [Key(0)]
   75|                 private int value;
   76|                 [IgnoreMember]
   77|                 public int Value { get => value; set => this.value = value; }
   78|             }
   79|             """;
   80|         await VerifyCS.Test.RunDefaultAsync(logger, testSource, languageVersion: languageVersion, testMethod: $"{nameof(FormatterForClassWithPrivateMembers_NonPartialTypes)}({type})");
   81|     }
   82| 
   83|     [Theory]
   84|     [InlineData("class", LanguageVersion.CSharp7_3)]
   85|     [InlineData("record", LanguageVersion.CSharp9)]
   86|     [InlineData("struct", LanguageVersion.CSharp7_3)]
   87|     public async Task FormatterForClassWithPrivateMembers_Nested_NonPartialTypes(string type, LanguageVersion languageVersion)
   88|     {
   89|         string testSource = $$"""
   90|             using System;
   91|             using MessagePack;
   92| 
   93|             {{type}} Outer
   94|             {
   95|                 [MessagePackObject]
   96|                 internal partial {{type}} {|MsgPack011:MyObject|}
   97|                 {
   98|                     [Key(0)]
   99|                     private int value;
  100|                     [IgnoreMember]
  101|                     public int Value { get => value; set => this.value = value; }
  102|                 }
  103|             }
  104|             """;
  105|         await VerifyCS.Test.RunDefaultAsync(logger, testSource, languageVersion: languageVersion, testMethod: $"{nameof(FormatterForClassWithPrivateMembers_Nested_NonPartialTypes)}({type})");
  106|     }
  107| }
```

### tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorCodeFixVerifier`2.cs at head (2f9324f9), full file
```
    1| ﻿// Copyright (c) All contributors. All rights reserved.
    2| // Licensed under the MIT license. See LICENSE file in the project root for full license information.
    3| 
    4| using Microsoft.CodeAnalysis;
    5| using Microsoft.CodeAnalysis.CodeFixes;
    6| using Microsoft.CodeAnalysis.CSharp;
    7| using Microsoft.CodeAnalysis.CSharp.Testing;
    8| using Microsoft.CodeAnalysis.Testing;
    9| using Microsoft.CodeAnalysis.Testing.Verifiers;
   10| 
   11| internal class CSharpSourceGeneratorCodeFixVerifier<TSourceGenerator, TCodeFix>
   12|     where TCodeFix : CodeFixProvider, new()
   13| {
   14|     public class Test : CSharpCodeFixTest<EmptyDiagnosticAnalyzer, TCodeFix, DefaultVerifier>
   15|     {
   16|         public Test()
   17|         {
   18|             this.ReferenceAssemblies = ReferencesHelper.DefaultTargetFrameworkReferences;
   19|             this.CompilerDiagnostics = CompilerDiagnostics.Warnings;
   20|         }
   21| 
   22|         public LanguageVersion LanguageVersion { get; set; } = LanguageVersion.CSharp7_3;
   23| 
   24|         public ReferencesSet MessagePackReferences { get; set; } = ReferencesSet.MessagePack;
   25| 
   26|         protected override CompilationOptions CreateCompilationOptions()
   27|         {
   28|             var compilationOptions = (CSharpCompilationOptions)base.CreateCompilationOptions();
   29|             return compilationOptions
   30|                .WithWarningLevel(99)
   31|                .WithSpecificDiagnosticOptions(compilationOptions.SpecificDiagnosticOptions.SetItem("CS1591", ReportDiagnostic.Suppress));
   32|         }
   33| 
   34| #pragma warning disable SA1316 // https://github.com/DotNetAnalyzers/StyleCopAnalyzers/issues/3781
   35|         protected override async Task<(Compilation compilation, ImmutableArray<Diagnostic> generatorDiagnostics)> GetProjectCompilationAsync(Project project, IVerifier verifier, CancellationToken cancellationToken)
   36| #pragma warning restore SA1316 // https://github.com/DotNetAnalyzers/StyleCopAnalyzers/issues/3781
   37|         {
   38|             var (compilation, generatorDiagnostics) = await base.GetProjectCompilationAsync(project, verifier, cancellationToken);
   39|             compilation = ReferencesHelper.AddMessagePackReferences(compilation, this.MessagePackReferences);
   40|             return (compilation, generatorDiagnostics);
   41|         }
   42| 
   43|         protected override ParseOptions CreateParseOptions()
   44|         {
   45|             return ((CSharpParseOptions)base.CreateParseOptions()).WithLanguageVersion(this.LanguageVersion);
   46|         }
   47| 
   48|         protected override IEnumerable<Type> GetSourceGenerators()
   49|         {
   50|             yield return typeof(TSourceGenerator);
   51|         }
   52|     }
   53| 
   54|     public static Task VerifyAnalyzerWithoutMessagePackReferenceAsync(string source)
   55|     {
   56|         var test = new Test { TestCode = source, MessagePackReferences = ReferencesSet.None };
   57|         return test.RunAsync();
   58|     }
   59| 
   60|     public static Task VerifyAnalyzerAsync(string source, params DiagnosticResult[] expected)
   61|     {
   62|         var test = new Test { TestCode = source };
   63|         test.ExpectedDiagnostics.AddRange(expected);
   64|         return test.RunAsync();
   65|     }
   66| 
   67|     public static Task VerifyCodeFixAsync(string source, string fixedSource)
   68|         => VerifyCodeFixAsync(source, DiagnosticResult.EmptyDiagnosticResults, fixedSource);
   69| 
   70|     public static Task VerifyCodeFixAsync(string source, DiagnosticResult expected, string fixedSource)
   71|         => VerifyCodeFixAsync(source, new[] { expected }, fixedSource);
   72| 
   73|     public static Task VerifyCodeFixAsync(string source, DiagnosticResult[] expected, string fixedSource)
   74|     {
   75|         var test = new Test
   76|         {
   77|             TestCode = source,
   78|             FixedCode = fixedSource,
   79|         };
   80| 
   81|         test.ExpectedDiagnostics.AddRange(expected);
   82|         return test.RunAsync();
   83|     }
   84| 
   85|     public static Task VerifyCodeFixAsync(string[] source, string[] fixedSource)
   86|     {
   87|         var test = new Test
   88|         {
   89|         };
   90| 
   91|         foreach (var src in source)
   92|         {
   93|             test.TestState.Sources.Add(src);
   94|         }
   95| 
   96|         foreach (var src in fixedSource)
   97|         {
   98|             test.FixedState.Sources.Add(src);
   99|         }
  100| 
  101|         return test.RunAsync();
  102|     }
  103| }
```

### tests/MessagePack.SourceGenerator.Tests/Verifiers/CSharpSourceGeneratorVerifier`1+Test.cs at head (2f9324f9), full file
```
    1| ﻿// Copyright (c) All contributors. All rights reserved.
    2| // Licensed under the MIT license. See LICENSE file in the project root for full license information.
    3| 
    4| // Uncomment the following line to write expected files to disk
    5| ////#define WRITE_EXPECTED
    6| 
    7| #if WRITE_EXPECTED
    8| #warning WRITE_EXPECTED is fine for local builds, but should not be merged to the main branch.
    9| #endif
   10| 
   11| using System.Diagnostics;
   12| using System.Reflection;
   13| using System.Runtime.CompilerServices;
   14| using System.Text;
   15| using MessagePack.SourceGenerator.Analyzers;
   16| using Microsoft.CodeAnalysis;
   17| using Microsoft.CodeAnalysis.CSharp;
   18| using Microsoft.CodeAnalysis.CSharp.Testing;
   19| using Microsoft.CodeAnalysis.Diagnostics;
   20| using Microsoft.CodeAnalysis.Testing;
   21| using Microsoft.CodeAnalysis.Text;
   22| using AnalyzerOptions = MessagePack.SourceGenerator.CodeAnalysis.AnalyzerOptions;
   23| 
   24| internal static partial class CSharpSourceGeneratorVerifier<TSourceGenerator>
   25|     where TSourceGenerator : new()
   26| {
   27|     internal class Test : CSharpSourceGeneratorTest<TSourceGenerator, DefaultVerifier>
   28|     {
   29|         private readonly string? testFile;
   30|         private readonly string testMethod;
   31| 
   32|         public Test(ReferencesSet references = ReferencesSet.MessagePack, [CallerFilePath] string? testFile = null, [CallerMemberName] string testMethod = null!)
   33|         {
   34|             this.CompilerDiagnostics = CompilerDiagnostics.Warnings;
   35|             this.ReferenceAssemblies = ReferenceAssemblies.Net.Net80;
   36|             this.TestState.AdditionalReferences.AddRange(ReferencesHelper.GetReferences(references));
   37| 
   38|             this.testFile = testFile;
   39|             this.testMethod = testMethod;
   40| 
   41| #if WRITE_EXPECTED
   42|             TestBehaviors |= TestBehaviors.SkipGeneratedSourcesCheck;
   43| #endif
   44|         }
   45| 
   46|         public LanguageVersion LanguageVersion { get; set; } = LanguageVersion.CSharp7_3;
   47| 
   48|         public static Task RunDefaultAsync(ITestOutputHelper logger, string testSource, AnalyzerOptions? options = null, LanguageVersion languageVersion = LanguageVersion.CSharp7_3, [CallerFilePath] string? testFile = null, [CallerMemberName] string testMethod = null!)
   49|         {
   50|             options ??= new();
   51| 
   52|             // TODO: throw if these attribute collections are non-empty. Tests should use the attributes themselves.
   53|             string assumedFormattable = string.Join(string.Empty, options.AssumedFormattableTypes.Select(t => $"[assembly: MessagePackAssumedFormattable(typeof({t.Name.GetQualifiedName(Qualifiers.Namespace)}))]" + Environment.NewLine));
   54|             string knownFormatters = string.Join(string.Empty, options.KnownFormatters.Select(t => $"[assembly: MessagePackKnownFormatter(typeof({t.Name.GetQualifiedName(Qualifiers.Namespace)}))]" + Environment.NewLine));
   55| 
   56|             string resolverPartialClassSource = $$"""
   57|                 using MessagePack;
   58| 
   59|                 {{assumedFormattable}}
   60|                 {{knownFormatters}}
   61| 
   62|                 namespace {{options.Generator.Resolver.Namespace}} {
   63|                     [GeneratedMessagePackResolver(UseMapMode = {{(options.Generator.Formatters.UsesMapMode ? "true" : "false")}})]
   64|                     partial class {{options.Generator.Resolver.Name}} { }
   65|                 }
   66|                 """;
   67|             return RunDefaultAsync(logger, testSource, resolverPartialClassSource, languageVersion, testFile, testMethod);
   68|         }
   69| 
   70|         public async Task RunDefaultAsync(ITestOutputHelper logger)
   71|         {
   72|             try
   73|             {
   74|                 await this.RunAsync();
   75|             }
   76|             finally
   77|             {
   78|                 foreach (var generatedSource in this.TestState.GeneratedSources)
   79|                 {
   80|                     logger.WriteLine("--------------------------------------------------------------");
   81|                     logger.WriteLine(generatedSource.filename);
   82|                     logger.WriteLine("--------------------------------------------------------------");
   83|                     int lineNumber = 0;
   84|                     foreach (TextLine line in generatedSource.content.Lines)
   85|                     {
   86|                         logger.WriteLine($"{++lineNumber,6}: {generatedSource.content.GetSubText(line.Span)}");
   87|                     }
   88| 
   89|                     logger.WriteLine("--------------------------------------------------------------");
   90|                 }
   91|             }
   92|         }
   93| 
   94|         private static Task RunDefaultAsync(ITestOutputHelper logger, string testSource, string resolverPartialClassSource, LanguageVersion languageVersion, [CallerFilePath] string? testFile = null, [CallerMemberName] string testMethod = null!)
   95|         {
   96|             Test test = new(testFile: testFile, testMethod: testMethod)
   97|             {
   98|                 TestState =
   99|                 {
  100|                     Sources = { testSource, resolverPartialClassSource },
  101|                 },
  102|                 LanguageVersion = languageVersion,
  103|             };
  104| 
  105|             return test.RunDefaultAsync(logger);
  106|         }
  107| 
  108|         public Test AddGeneratedSources()
  109|         {
  110|             static void AddGeneratedSources(ProjectState project, string testMethod, bool withPrefix)
  111|             {
  112|                 string prefix = withPrefix ? $"{project.Name}." : string.Empty;
  113|                 string expectedPrefix = $"{ThisAssembly.AssemblyName}.Resources.{testMethod}.{prefix}"
  114|                     .Replace(' ', '_')
  115|                     .Replace(',', '_')
  116|                     .Replace('(', '_')
  117|                     .Replace(')', '_');
  118| 
  119|                 foreach (var resourceName in typeof(Test).Assembly.GetManifestResourceNames())
  120|                 {
  121|                     if (!resourceName.StartsWith(expectedPrefix))
  122|                     {
  123|                         continue;
  124|                     }
  125| 
  126|                     using var resourceStream = Assembly.GetExecutingAssembly().GetManifestResourceStream(resourceName);
  127|                     if (resourceStream is null)
  128|                     {
  129|                         throw new InvalidOperationException();
  130|                     }
  131| 
  132|                     using var reader = new StreamReader(resourceStream, Encoding.UTF8, detectEncodingFromByteOrderMarks: true, bufferSize: 4096, leaveOpen: true);
  133|                     var name = resourceName.Substring(expectedPrefix.Length);
  134|                     project.GeneratedSources.Add((typeof(TSourceGenerator), name, reader.ReadToEnd()));
  135|                 }
  136|             }
  137| 
  138|             AddGeneratedSources(this.TestState, this.testMethod, this.TestState.AdditionalProjects.Count > 0);
  139|             foreach (ProjectState addlProject in this.TestState.AdditionalProjects.Values)
  140|             {
  141|                 AddGeneratedSources(addlProject, this.testMethod, true);
  142|             }
  143| 
  144|             return this;
  145|         }
  146| 
  147|         protected override Task RunImplAsync(CancellationToken cancellationToken)
  148|         {
  149|             this.AddGeneratedSources();
  150| 
  151|             foreach (ProjectState addlProject in this.TestState.AdditionalProjects.Values)
  152|             {
  153|                 addlProject.AdditionalReferences.AddRange(this.TestState.AdditionalReferences);
  154|                 addlProject.DocumentationMode = DocumentationMode.Parse;
  155|             }
  156| 
  157|             return base.RunImplAsync(cancellationToken);
  158|         }
  159| 
  160|         protected override IEnumerable<Type> GetSourceGenerators()
  161|         {
  162|             yield return typeof(TSourceGenerator);
  163|         }
  164| 
  165|         protected override IEnumerable<DiagnosticAnalyzer> GetDiagnosticAnalyzers()
  166|         {
  167|             foreach (Type analyzer in typeof(MsgPack001SpecifyOptionsAnalyzer).Assembly.GetTypes().Where(t => typeof(DiagnosticAnalyzer).IsAssignableFrom(t)))
  168|             {
  169|                 yield return (DiagnosticAnalyzer)Activator.CreateInstance(analyzer)!;
  170|             }
  171|         }
  172| 
  173|         protected override CompilationOptions CreateCompilationOptions()
  174|         {
  175|             var compilationOptions = (CSharpCompilationOptions)base.CreateCompilationOptions();
  176|             return compilationOptions
  177|                 .WithAllowUnsafe(false)
  178|                 .WithWarningLevel(99)
  179|                 .WithSpecificDiagnosticOptions(compilationOptions.SpecificDiagnosticOptions.SetItem("CS1591", ReportDiagnostic.Suppress));
  180|         }
  181| 
  182|         protected override ParseOptions CreateParseOptions()
  183|         {
  184|             return ((CSharpParseOptions)base.CreateParseOptions()).WithLanguageVersion(this.LanguageVersion);
  185|         }
  186| 
  187|         protected override async Task<(Compilation, ImmutableArray<Diagnostic>)> GetProjectCompilationAsync(Project project, IVerifier verifier, CancellationToken cancellationToken)
  188|         {
  189|             string fileNamePrefix = this.TestState.AdditionalProjects.Count > 0 ? $"{project.Name}." : string.Empty;
  190|             var resourceDirectory = Path.Combine(Path.GetDirectoryName(this.testFile)!, "Resources", this.testMethod);
  191| 
  192|             var (compilation, diagnostics) = await base.GetProjectCompilationAsync(project, verifier, cancellationToken);
  193|             var expectedNames = new HashSet<string>();
  194|             foreach (var tree in compilation.SyntaxTrees.Skip(project.DocumentIds.Count))
  195|             {
  196|                 WriteTreeToDiskIfNecessary(tree, resourceDirectory, fileNamePrefix);
  197|                 expectedNames.Add(Path.GetFileName(tree.FilePath));
  198|             }
  199| 
  200|             var currentTestPrefix = $"{ThisAssembly.AssemblyName}.Resources.{this.testMethod}.{fileNamePrefix}";
  201|             foreach (var name in this.GetType().Assembly.GetManifestResourceNames())
  202|             {
  203|                 if (!name.StartsWith(currentTestPrefix))
  204|                 {
  205|                     continue;
  206|                 }
  207| 
  208|                 if (!expectedNames.Contains(name.Substring(currentTestPrefix.Length)))
  209|                 {
  210|                     throw new InvalidOperationException($"Unexpected test resource: {name.Substring(currentTestPrefix.Length)}");
  211|                 }
  212|             }
  213| 
  214|             return (compilation, diagnostics);
  215|         }
  216| 
  217|         [Conditional("WRITE_EXPECTED")]
  218|         private static void WriteTreeToDiskIfNecessary(SyntaxTree tree, string resourceDirectory, string fileNamePrefix)
  219|         {
  220|             if (tree.Encoding is null)
  221|             {
  222|                 throw new ArgumentException("Syntax tree encoding was not specified");
  223|             }
  224| 
  225|             string name = fileNamePrefix + Path.GetFileName(tree.FilePath);
  226|             string filePath = Path.Combine(resourceDirectory, name);
  227|             Directory.CreateDirectory(resourceDirectory);
  228|             File.WriteAllText(filePath, tree.GetText().ToString(), tree.Encoding);
  229|         }
  230|     }
  231| }
```

## What you did NOT get (refuse anything that depends on it)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)

Return only the JSON object described in the brief.