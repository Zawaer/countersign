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
# Change var-2283-v1: branch cs-var/2283-v1, base 32258fdbee4bcd653c79f51b4376b5103c6f4d27, head 60d651e8f7d049ab6ab078f98c578cd79fda4544
Commit message: Fix generator/analyzer crash on closed generic value type from a referenced assembly

TypeCollector.GetObjectInfo runs against closed generic types defined in
referenced assemblies, whose symbols have no syntax. For value types, the
metadata import includes private compiler-generated backing fields, which
hit the MemberNeedsKey diagnostic path that indexed
DeclaringSyntaxReferences[0] and threw IndexOutOfRangeException.

Use FirstOrDefault() for the location in the MemberNeedsKey and
BothStringAndIntKeyAreNull diagnostics, as the neighbouring diagnostics do.

Fixes #2283

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Upstream issue: https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2283

## Requirement set (requirements/var-2283-v1.yaml)
```yaml
# REUSED from requirements/2283.yaml (same clauses, same ids, unchanged text) for another fix of the same upstream issue
# #2283, so every fix of it is judged against the same clauses (docs/MEASUREMENT.md, "Same issue, several fixes").
# Still a placeholder derived from the issue, not a Tieto set.
change: "var-2283-v1"
branch: cs-var/2283-v1
reused_from: requirements/2283.yaml
source: https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2283
official: false
requirements:
  - id: REQ-2283-F1
    type: functional
    text: "Building a project whose [MessagePackObject] type has a member of a closed generic value type defined in a referenced assembly must not crash the source generator (no CS8785) and must produce a generated resolver."
  - id: REQ-2283-F2
    type: functional
    text: "The MsgPack00x analyzer must not throw (no AD0001) for the same input."
  - id: REQ-2283-F3
    type: functional
    text: "Diagnostics about members of a type declared in a referenced assembly must not be reported at locations outside the compilation being analyzed."
  - id: REQ-2283-N1
    type: non-functional
    checks: [tests.full_suite]
    text: "Existing analyzer diagnostics for types declared in the current compilation keep working unchanged (no regressions in the existing test suite)."
  - id: REQ-2283-N2
    type: non-functional
    checks: [tests.fail_without_fix]
    text: "The fix is covered by automated tests that fail without it."
```

## facts.json (deterministic checks; cite their ids and test names)
```json
{
 "change": "var-2283-v1",
 "branch": "cs-var/2283-v1",
 "base": "32258fdb",
 "head": "60d651e8",
 "base_full": "32258fdbee4bcd653c79f51b4376b5103c6f4d27",
 "head_full": "60d651e8f7d049ab6ab078f98c578cd79fda4544",
 "commit_message": "Fix generator/analyzer crash on closed generic value type from a referenced assembly\n\nTypeCollector.GetObjectInfo runs against closed generic types defined in\nreferenced assemblies, whose symbols have no syntax. For value types, the\nmetadata import includes private compiler-generated backing fields, which\nhit the MemberNeedsKey diagnostic path that indexed\nDeclaringSyntaxReferences[0] and threw IndexOutOfRangeException.\n\nUse FirstOrDefault() for the location in the MemberNeedsKey and\nBothStringAndIntKeyAreNull diagnostics, as the neighbouring diagnostics do.\n\nFixes #2283\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>",
 "author": "Zawaer",
 "agent_written": true,
 "diff": {
  "files": 5,
  "insertions": 248,
  "deletions": 2,
  "by_kind": {
   "source": 1,
   "test": 1,
   "generated": 3
  },
  "by_file": [
   {
    "path": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
    "ins": 2,
    "del": 2,
    "kind": "source"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs",
    "ins": 55,
    "del": 0,
    "kind": "test"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/Resources/Generics_ValueType_Defined_In_ReferencedProject/Formatters.MessagePack.GeneratedMessagePackResolver.TempProject.MyGenericStructFormatter`1.g.cs",
    "ins": 54,
    "del": 0,
    "kind": "generated"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/Resources/Generics_ValueType_Defined_In_ReferencedProject/Formatters.MessagePack.GeneratedMessagePackResolver.TempProject.MyObjectFormatter.g.cs",
    "ins": 60,
    "del": 0,
    "kind": "generated"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/Resources/Generics_ValueType_Defined_In_ReferencedProject/MessagePack.GeneratedMessagePackResolver.g.cs",
    "ins": 77,
    "del": 0,
    "kind": "generated"
   }
  ]
 },
 "new_tests_in_diff": [
  "GenericsFormatterTests.Generics_ValueType_Defined_In_ReferencedProject"
 ],
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
   "summary": "0 errors, 2 unique warnings",
   "log": "evidence/var-2283-v1/logs/build.log",
   "duration_s": 5.0
  },
  {
   "id": "tests.targeted",
   "tool": "dotnet test",
   "tool_version": "8.0.402",
   "status": "pass",
   "summary": "17 passed, 0 failed, 0 skipped (1 new tests in run)",
   "tests": [
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
     "name": "GenericsFormatterTests.Generics_ValueType_Defined_In_ReferencedProject",
     "outcome": "passed",
     "new": true
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
     "name": "GenericsFormatterTests.RecursiveGenerics_Direct",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.WellKnownGenericsFormatter",
     "outcome": "passed",
     "new": false
    }
   ],
   "log": "evidence/var-2283-v1/logs/tests_targeted.1.log",
   "duration_s": 3.0,
   "filter": [
    "FullyQualifiedName~GenericsFormatterTests."
   ],
   "project": "tests/MessagePack.SourceGenerator.Tests"
  },
  {
   "id": "tests.fail_without_fix",
   "tool": "dotnet test (source reverted, tests kept)",
   "tool_version": "8.0.402",
   "status": "pass",
   "summary": "new tests fail on base source: 1/1 failed -> tests do cover the change",
   "tests": [
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
     "name": "GenericsFormatterTests.Generics_ValueType_Defined_In_ReferencedProject",
     "outcome": "failed",
     "new": true,
     "error": "System.InvalidOperationException : Context: Source generator application\nContext: Verifying source generated files\nExpected source file list to match\n-MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/Formatters.MessagePack.GeneratedMessagePackResolver.TempProject.MyGenericStructFormatter`1.g.cs\n-MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerato [...]"
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
     "name": "GenericsFormatterTests.RecursiveGenerics_Direct",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenericsFormatterTests.WellKnownGenericsFormatter",
     "outcome": "passed",
     "new": false
    }
   ],
   "log": "evidence/var-2283-v1/logs/tests_fail_without_fix.1.log",
   "duration_s": 3.0,
   "reverted_files": [
    "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs"
   ],
   "full_suite_with_source_reverted": {
    "total": 168,
    "failed": 1,
    "failed_tests": [
     "GenericsFormatterTests.Generics_ValueType_Defined_In_ReferencedProject"
    ],
    "log": "evidence/var-2283-v1/logs/fail_without_fix.full_suite.log"
   },
   "new_failed": 1,
   "new_total": 1
  },
  {
   "id": "tests.full_suite",
   "tool": "dotnet test",
   "tool_version": "8.0.402",
   "status": "pass",
   "summary": "tests/MessagePack.SourceGenerator.Tests: 168 tests, 168 passed, 0 failed (0 not failing on base, 0 also failing on base)",
   "project": "tests/MessagePack.SourceGenerator.Tests",
   "total": 168,
   "passed": 168,
   "failed": 0,
   "failures_not_on_base": [],
   "failures_also_on_base": [],
   "log": "evidence/var-2283-v1/logs/tests_full_suite.log",
   "duration_s": 5.0,
   "base_total": 167,
   "base_passed": 167
  },
  {
   "id": "public_api",
   "tool": "git diff of PublicAPI.*.txt + scan of added/removed public/protected declarations in src/",
   "status": "pass",
   "summary": "no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or removed in src/",
   "publicapi_files_changed": []
  },
  {
   "id": "analyzers",
   "tool": "dotnet build warnings (Roslyn analyzers, StyleCop, PublicApiAnalyzers) vs base",
   "status": "fail",
   "summary": "1 new warnings vs base",
   "new_warnings": [
    "tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs: warning SA1515: Single-line comment should be preceded by blank line (https://github.com/DotNetAnalyzers/StyleCopAnalyzers/blob/master/documentation/SA1515.md) [tests/MessagePack.SourceGenerator.Tests/MessagePack.SourceGenerator.Tests.csproj]"
   ],
   "resolved_warnings": [],
   "base_warning_count": 1
  },
  {
   "id": "injection_scan",
   "tool": "countersign.injection (deterministic pattern scan)",
   "tool_version": "injection-v2",
   "status": "pass",
   "summary": "no text addressed to automated reviewers in the added lines, file paths, branch, commit message or PR text",
   "scanned": {
    "diff_added_lines": 248,
    "files": 5,
    "paths": 5,
    "binary_files": 0,
    "branch": true,
    "commit_message": true,
    "pr_text": false
   },
   "patterns": [
    "addressed_to_ai",
    "override_instructions",
    "verdict_steering",
    "claimed_approval",
    "role_play",
    "lgtm",
    "hidden_unicode",
    "mixed_script",
    "unscannable"
   ],
   "matches": [],
   "sources": {
    "diff": "git diff 32258fdb 60d651e8 (added lines and file paths)",
    "branch": "facts.branch",
    "commit_message": "facts.commit_message",
    "pr_text": "none: the change has no pull request text"
   }
  },
  {
   "id": "tests.mutation",
   "tool": "evidence/scripts/mutation.py + dotnet test (one mutant at a time, the targeted filter)",
   "tool_version": "8.0.402",
   "status": "fail",
   "summary": "1 mutants of the changed source lines: 0 killed, 1 survived; 0 of 1 mutated hunks have a killed mutant; surviving hunks: TypeCollector.cs:985; 1 hunks not mutated",
   "rule": "killed = at least one new test (new: true in tests.fail_without_fix) fails on the mutant and passed on head; pass = every mutated hunk has a killed mutant",
   "operators": [
    "negate_condition",
    "drop_statement",
    "drop_guard",
    "swap_logical",
    "drop_guard_conjunct",
    "return_default",
    "remove_call"
   ],
   "max_mutants": 8,
   "project": "tests/MessagePack.SourceGenerator.Tests",
   "filter": [
    "FullyQualifiedName~GenericsFormatterTests."
   ],
   "tests_judged": [
    "GenericsFormatterTests.Generics_ValueType_Defined_In_ReferencedProject"
   ],
   "not_covered": "ExecutionTests/MapModeExecutionTests (SDK 9) are not run against the mutants; files that are not C# are not mutated",
   "hunks": [
    {
     "id": "H1",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      985,
      985
     ],
     "code_lines": [
      985
     ],
     "mutants": [
      "M1"
     ],
     "status": "survived"
    },
    {
     "id": "H2",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1077,
      1077
     ],
     "code_lines": [
      1077
     ],
     "mutants": [],
     "status": "not_mutated",
     "why": "no operator applies to its lines"
    }
   ],
   "surviving_hunks": [
    "H1"
   ],
   "mutants": [
    {
     "id": "M1",
     "hunk": "H1",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "line": 985,
     "operator": "remove_call",
     "before": "                        this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.BothStringAndIntKeyAreNull, (item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax() as PropertyDeclarationSyntax)?.Identifier.GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name));",
     "after": "                        { }",
     "log": [
      "evidence/var-2283-v1/logs/mutation/M1.build.log",
      "evidence/var-2283-v1/logs/mutation/M1.test.1.log"
     ],
     "diff": "evidence/var-2283-v1/logs/mutation/M1.diff",
     "killed_by": [],
     "existing_tests_failed": [],
     "outcome": "survived",
     "tests_run": 17
    }
   ],
   "kills_by_test": [
    {
     "name": "GenericsFormatterTests.Generics_ValueType_Defined_In_ReferencedProject",
     "killed": []
    }
   ],
   "log": "evidence/var-2283-v1/logs/mutation/"
  }
 ],
 "not_run": [
  {
   "id": "deps.delta",
   "reason": "no *.csproj, *.props, *.targets, nuget.config, global.json or tool manifest changed, so the restored package graph is the base graph; the restore was not re-run"
  },
  {
   "id": "tests.execution",
   "reason": "ExecutionTests/MapModeExecutionTests (SDK 9) not run for this change"
  },
  {
   "id": "build.net472/netstandard",
   "reason": "only the net8.0 slice of src/MessagePack was built (Linux container, Debug)"
  },
  {
   "id": "tests.MessagePack.Tests",
   "reason": "runtime library src/MessagePack not modified by the change; suite not run"
  }
 ],
 "environment": {
  "sdk": "8.0.402",
  "os": "linux-x64 (container)",
  "configuration": "Debug",
  "max_cpu": 8,
  "raw_runs": "evidence/var-scripts/runs.sh -> /data/work/var/out/var-2283-v1[-fwf] (not committed; logs copied to evidence/var-2283-v1/logs/)"
 }
}
```

## Files changed (5: 2 non-generated, 3 generated)
- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs (+2 -2, source)
- tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs (+55 -0, test)

Generated files (3; contents and diffs NOT provided):
- tests/MessagePack.SourceGenerator.Tests/Resources/Generics_ValueType_Defined_In_ReferencedProject/Formatters.MessagePack.GeneratedMessagePackResolver.TempProject.MyGenericStructFormatter`1.g.cs (+54 -0)
- tests/MessagePack.SourceGenerator.Tests/Resources/Generics_ValueType_Defined_In_ReferencedProject/Formatters.MessagePack.GeneratedMessagePackResolver.TempProject.MyObjectFormatter.g.cs (+60 -0)
- tests/MessagePack.SourceGenerator.Tests/Resources/Generics_ValueType_Defined_In_ReferencedProject/MessagePack.GeneratedMessagePackResolver.g.cs (+77 -0)

## Diff (non-generated files)
```diff
diff --git a/src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs b/src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs
index e121773d..fba52be0 100644
--- a/src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs
+++ b/src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs
@@ -982,7 +982,7 @@ public class TypeCollector
                     var stringKey = key is { Value: string stringKeyValue } ? stringKeyValue : default;
                     if (intKey == null && stringKey == null)
                     {
-                        this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.BothStringAndIntKeyAreNull, ((PropertyDeclarationSyntax)item.DeclaringSyntaxReferences[0].GetSyntax()).Identifier.GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name));
+                        this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.BothStringAndIntKeyAreNull, (item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax() as PropertyDeclarationSyntax)?.Identifier.GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name));
                     }
 
                     // A property with an init accessor and an initializer has a default that will be discarded by the deserializer.
@@ -1074,7 +1074,7 @@ public class TypeCollector
                             {
                                 Diagnostic diagnostic = derivedKeyAttribute is not null && suppressSourceGeneration is not true
                                     ? Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AOTDerivedKeyAttribute, derivedKeyAttribute.GetSyntax(this.cancellationToken).GetLocation())
-                                    : Diagnostic.Create(MsgPack00xMessagePackAnalyzer.MemberNeedsKey, item.DeclaringSyntaxReferences[0].GetSyntax().GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name);
+                                    : Diagnostic.Create(MsgPack00xMessagePackAnalyzer.MemberNeedsKey, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name);
                                 if (nonPublicMembersAreSerialized || (item.DeclaredAccessibility & Accessibility.Public) == Accessibility.Public)
                                 {
                                     this.reportDiagnostic?.Invoke(diagnostic);

diff --git a/tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs b/tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs
index 283622c5..093db49f 100644
--- a/tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs
+++ b/tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs
@@ -1,6 +1,7 @@
 ﻿// Copyright (c) All contributors. All rights reserved.
 // Licensed under the MIT license. See LICENSE file in the project root for full license information.
 
+using Microsoft.CodeAnalysis;
 using Microsoft.CodeAnalysis.CSharp;
 using VerifyCS = CSharpSourceGeneratorVerifier<MessagePack.SourceGenerator.MessagePackGenerator>;
 
@@ -494,6 +495,60 @@ namespace TempProject
         }.RunAsync();
     }
 
+    /// <summary>
+    /// Regression test for a closed generic value type defined in a referenced assembly,
+    /// whose compiler-generated backing fields have no syntax (https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2283).
+    /// </summary>
+    [Fact]
+    public async Task Generics_ValueType_Defined_In_ReferencedProject()
+    {
+        string defineSource = """
+using MessagePack;
+
+namespace TempProject
+{
+    [MessagePackObject]
+    public struct MyGenericStruct<T>
+    {
+        [Key(0)]
+        public string Key { get; set; }
+    }
+}
+""";
+
+        string usageSource = """
+using MessagePack;
+
+namespace TempProject
+{
+    [MessagePackObject]
+    public class MyObject
+    {
+        [Key(0)]
+        public MyGenericStruct<int> Value { get; set; }
+    }
+}
+""";
+        // Reference the defining assembly as metadata (not as a project) so its symbols have no syntax.
+        CSharpCompilation definingCompilation = CSharpCompilation.Create(
+            "DefiningAssembly",
+            [CSharpSyntaxTree.ParseText(defineSource)],
+            (await ReferencesHelper.DefaultTargetFrameworkReferences.ResolveAsync(LanguageNames.CSharp, default)).AddRange(ReferencesHelper.GetReferences(ReferencesSet.MessagePack)),
+            new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary));
+        using MemoryStream definingImage = new();
+        Microsoft.CodeAnalysis.Emit.EmitResult emitResult = definingCompilation.Emit(definingImage);
+        Assert.True(emitResult.Success, string.Join(Environment.NewLine, emitResult.Diagnostics));
+
+        await new VerifyCS.Test
+        {
+            TestState =
+            {
+                Sources = { usageSource },
+                AdditionalReferences = { MetadataReference.CreateFromImage(definingImage.ToArray()) },
+            },
+        }.RunAsync();
+    }
+
     /// <summary>
     /// Asserts that the generator can handle directly recursive generic constraints.
     /// </summary>

```

## File contents (line numbers in the gutter; quote the text after '| ')

### src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at head (60d651e8), full file
```
    1| // Copyright (c) All contributors. All rights reserved.
    2| // Licensed under the MIT license. See LICENSE file in the project root for full license information.
    3| 
    4| #pragma warning disable SA1402 // File may only contain a single type
    5| #pragma warning disable SA1649 // File name should match first type name
    6| 
    7| using System.Collections.Immutable;
    8| using System.Reflection;
    9| using System.Text.RegularExpressions;
   10| using Microsoft.CodeAnalysis;
   11| using Microsoft.CodeAnalysis.CSharp;
   12| using Microsoft.CodeAnalysis.CSharp.Syntax;
   13| 
   14| namespace MessagePack.SourceGenerator.CodeAnalysis;
   15| 
   16| public class MessagePackGeneratorResolveFailedException : Exception
   17| {
   18|     public MessagePackGeneratorResolveFailedException(string message)
   19|         : base(message)
   20|     {
   21|     }
   22| }
   23| 
   24| public class TypeCollector
   25| {
   26|     private static readonly SymbolDisplayFormat BinaryWriteFormat = new SymbolDisplayFormat(
   27|         genericsOptions: SymbolDisplayGenericsOptions.IncludeTypeParameters,
   28|         miscellaneousOptions: SymbolDisplayMiscellaneousOptions.ExpandNullable,
   29|         typeQualificationStyle: SymbolDisplayTypeQualificationStyle.NameOnly);
   30| 
   31|     private static readonly SymbolDisplayFormat ShortTypeNameFormat = new SymbolDisplayFormat(
   32|             typeQualificationStyle: SymbolDisplayTypeQualificationStyle.NameAndContainingTypes);
   33| 
   34|     private static readonly HashSet<string> EmbeddedTypes = new(new[]
   35|     {
   36|         "short",
   37|         "int",
   38|         "long",
   39|         "ushort",
   40|         "uint",
   41|         "ulong",
   42|         "float",
   43|         "double",
   44|         "bool",
   45|         "byte",
   46|         "sbyte",
   47|         "decimal",
   48|         "char",
   49|         "string",
   50|         "object",
   51|         "System.Guid",
   52|         "System.TimeSpan",
   53|         "System.DateTime",
   54|         "System.DateTimeOffset",
   55| 
   56|         "MessagePack.Nil",
   57| 
   58|         // and arrays
   59|         "short[]",
   60|         "int[]",
   61|         "long[]",
   62|         "ushort[]",
   63|         "uint[]",
   64|         "ulong[]",
   65|         "float[]",
   66|         "double[]",
   67|         "bool[]",
   68|         "byte[]",
   69|         "sbyte[]",
   70|         "decimal[]",
   71|         "char[]",
   72|         "string[]",
   73|         "object[]",
   74|         "System.DateTime[]",
   75|         "System.ArraySegment<byte>",
   76|         "System.Memory<byte>",
   77|         "System.ReadOnlyMemory<byte>",
   78|         "System.Buffers.ReadOnlySequence<byte>",
   79| 
   80|         // List
   81|         "System.Collections.Generic.List<short>",
   82|         "System.Collections.Generic.List<int>",
   83|         "System.Collections.Generic.List<long>",
   84|         "System.Collections.Generic.List<ushort>",
   85|         "System.Collections.Generic.List<uint>",
   86|         "System.Collections.Generic.List<ulong>",
   87|         "System.Collections.Generic.List<float>",
   88|         "System.Collections.Generic.List<double>",
   89|         "System.Collections.Generic.List<bool>",
   90|         "System.Collections.Generic.List<byte>",
   91|         "System.Collections.Generic.List<sbyte>",
   92|         "System.Collections.Generic.List<char>",
   93|         "System.Collections.Generic.List<string>",
   94|         "System.Collections.Generic.List<object>",
   95|         "System.Collections.Generic.List<System.DateTime>",
   96| 
   97|         // extensions
   98|         "UnityEngine.Vector2",
   99|         "UnityEngine.Vector3",
  100|         "UnityEngine.Vector4",
  101|         "UnityEngine.Quaternion",
  102|         "UnityEngine.Color",
  103|         "UnityEngine.Bounds",
  104|         "UnityEngine.Rect",
  105|         "UnityEngine.AnimationCurve",
  106|         "UnityEngine.RectOffset",
  107|         "UnityEngine.Gradient",
  108|         "UnityEngine.WrapMode",
  109|         "UnityEngine.GradientMode",
  110|         "UnityEngine.Keyframe",
  111|         "UnityEngine.Matrix4x4",
  112|         "UnityEngine.GradientColorKey",
  113|         "UnityEngine.GradientAlphaKey",
  114|         "UnityEngine.Color32",
  115|         "UnityEngine.LayerMask",
  116|         "UnityEngine.Vector2Int",
  117|         "UnityEngine.Vector3Int",
  118|         "UnityEngine.RangeInt",
  119|         "UnityEngine.RectInt",
  120|         "UnityEngine.BoundsInt",
  121| 
  122|         "System.Reactive.Unit",
  123| 
  124|         "System.Numerics.BigInteger",
  125|         "System.Numerics.Complex",
  126|         "System.Numerics.Vector2",
  127|         "System.Numerics.Vector3",
  128|         "System.Numerics.Vector4",
  129|         "System.Numerics.Quaternion",
  130|         "System.Numerics.Matrix3x2",
  131|         "System.Numerics.Matrix4x4",
  132|     });
  133| 
  134|     private static readonly Dictionary<string, string> KnownGenericTypes = new()
  135|     {
  136| #pragma warning disable SA1509 // Opening braces should not be preceded by blank line
  137|         { "System.Collections.Generic.List<>", "MsgPack::Formatters.ListFormatter" },
  138|         { "System.Collections.Generic.LinkedList<>", "MsgPack::Formatters.LinkedListFormatter" },
  139|         { "System.Collections.Generic.Queue<>", "MsgPack::Formatters.QueueFormatter" },
  140|         { "System.Collections.Generic.Stack<>", "MsgPack::Formatters.StackFormatter" },
  141|         { "System.Collections.Generic.HashSet<>", "MsgPack::Formatters.HashSetFormatter" },
  142|         { "System.Collections.ObjectModel.ReadOnlyCollection<>", "MsgPack::Formatters.ReadOnlyCollectionFormatter" },
  143|         { "System.Collections.Generic.IList<>", "MsgPack::Formatters.InterfaceListFormatter2" },
  144|         { "System.Collections.Generic.ICollection<>", "MsgPack::Formatters.InterfaceCollectionFormatter2" },
  145|         { "System.Collections.Generic.IEnumerable<>", "MsgPack::Formatters.InterfaceEnumerableFormatter" },
  146|         { "System.Collections.Generic.Dictionary<,>", "MsgPack::Formatters.DictionaryFormatter" },
  147|         { "System.Collections.Generic.IDictionary<,>", "MsgPack::Formatters.InterfaceDictionaryFormatter" },
  148|         { "System.Collections.Generic.SortedDictionary<,>", "MsgPack::Formatters.SortedDictionaryFormatter" },
  149|         { "System.Collections.Generic.SortedList<,>", "MsgPack::Formatters.SortedListFormatter" },
  150|         { "System.Linq.ILookup<,>", "MsgPack::Formatters.InterfaceLookupFormatter" },
  151|         { "System.Linq.IGrouping<,>", "MsgPack::Formatters.InterfaceGroupingFormatter" },
  152|         { "System.Collections.ObjectModel.ObservableCollection<>", "MsgPack::Formatters.ObservableCollectionFormatter" },
  153|         { "System.Collections.ObjectModel.ReadOnlyObservableCollection<>", "MsgPack::Formatters.ReadOnlyObservableCollectionFormatter" },
  154|         { "System.Collections.Generic.IReadOnlyList<>", "MsgPack::Formatters.InterfaceReadOnlyListFormatter" },
  155|         { "System.Collections.Generic.IReadOnlyCollection<>", "MsgPack::Formatters.InterfaceReadOnlyCollectionFormatter" },
  156|         { "System.Collections.Generic.ISet<>", "MsgPack::Formatters.InterfaceSetFormatter" },
  157|         { "System.Collections.Concurrent.ConcurrentBag<>", "MsgPack::Formatters.ConcurrentBagFormatter" },
  158|         { "System.Collections.Concurrent.ConcurrentQueue<>", "MsgPack::Formatters.ConcurrentQueueFormatter" },
  159|         { "System.Collections.Concurrent.ConcurrentStack<>", "MsgPack::Formatters.ConcurrentStackFormatter" },
  160|         { "System.Collections.ObjectModel.ReadOnlyDictionary<,>", "MsgPack::Formatters.ReadOnlyDictionaryFormatter" },
  161|         { "System.Collections.Generic.IReadOnlyDictionary<,>", "MsgPack::Formatters.InterfaceReadOnlyDictionaryFormatter" },
  162|         { "System.Collections.Concurrent.ConcurrentDictionary<,>", "MsgPack::Formatters.ConcurrentDictionaryFormatter" },
  163|         { "System.Lazy<>", "MsgPack::Formatters.LazyFormatter" },
  164|         { "System.Threading.Tasks<>", "MsgPack::Formatters.TaskValueFormatter" },
  165| 
  166|         { "System.Tuple<>", "MsgPack::Formatters.TupleFormatter" },
  167|         { "System.Tuple<,>", "MsgPack::Formatters.TupleFormatter" },
  168|         { "System.Tuple<,,>", "MsgPack::Formatters.TupleFormatter" },
  169|         { "System.Tuple<,,,>", "MsgPack::Formatters.TupleFormatter" },
  170|         { "System.Tuple<,,,,>", "MsgPack::Formatters.TupleFormatter" },
  171|         { "System.Tuple<,,,,,>", "MsgPack::Formatters.TupleFormatter" },
  172|         { "System.Tuple<,,,,,,>", "MsgPack::Formatters.TupleFormatter" },
  173|         { "System.Tuple<,,,,,,,>", "MsgPack::Formatters.TupleFormatter" },
  174| 
  175|         { "System.ValueTuple<>", "MsgPack::Formatters.ValueTupleFormatter" },
  176|         { "System.ValueTuple<,>", "MsgPack::Formatters.ValueTupleFormatter" },
  177|         { "System.ValueTuple<,,>", "MsgPack::Formatters.ValueTupleFormatter" },
  178|         { "System.ValueTuple<,,,>", "MsgPack::Formatters.ValueTupleFormatter" },
  179|         { "System.ValueTuple<,,,,>", "MsgPack::Formatters.ValueTupleFormatter" },
  180|         { "System.ValueTuple<,,,,,>", "MsgPack::Formatters.ValueTupleFormatter" },
  181|         { "System.ValueTuple<,,,,,,>", "MsgPack::Formatters.ValueTupleFormatter" },
  182|         { "System.ValueTuple<,,,,,,,>", "MsgPack::Formatters.ValueTupleFormatter" },
  183| 
  184|         { "System.Collections.Generic.KeyValuePair<,>", "MsgPack::Formatters.KeyValuePairFormatter" },
  185|         { "System.Threading.Tasks.ValueTask<>", "MsgPack::Formatters.KeyValuePairFormatter" },
  186|         { "System.ArraySegment<>", "MsgPack::Formatters.ArraySegmentFormatter" },
  187|         { "System.Memory<>", "MsgPack::Formatters.MemoryFormatter" },
  188|         { "System.ReadOnlyMemory<>", "MsgPack::Formatters.ReadOnlyMemoryFormatter" },
  189|         { "System.Buffers.ReadOnlySequence<>", "MsgPack::Formatters.ReadOnlySequenceFormatter" },
  190| 
  191|         // extensions
  192|         { "System.Collections.Immutable.ImmutableArray<>", "MsgPack::ImmutableCollection.ImmutableArrayFormatter" },
  193|         { "System.Collections.Immutable.ImmutableList<>", "MsgPack::ImmutableCollection.ImmutableListFormatter" },
  194|         { "System.Collections.Immutable.ImmutableDictionary<,>", "MsgPack::ImmutableCollection.ImmutableDictionaryFormatter" },
  195|         { "System.Collections.Immutable.ImmutableHashSet<>", "MsgPack::ImmutableCollection.ImmutableHashSetFormatter" },
  196|         { "System.Collections.Immutable.ImmutableSortedDictionary<,>", "MsgPack::ImmutableCollection.ImmutableSortedDictionaryFormatter" },
  197|         { "System.Collections.Immutable.ImmutableSortedSet<>", "MsgPack::ImmutableCollection.ImmutableSortedSetFormatter" },
  198|         { "System.Collections.Immutable.ImmutableQueue<>", "MsgPack::ImmutableCollection.ImmutableQueueFormatter" },
  199|         { "System.Collections.Immutable.ImmutableStack<>", "MsgPack::ImmutableCollection.ImmutableStackFormatter" },
  200|         { "System.Collections.Immutable.IImmutableList<>", "MsgPack::ImmutableCollection.InterfaceImmutableListFormatter" },
  201|         { "System.Collections.Immutable.IImmutableDictionary<,>", "MsgPack::ImmutableCollection.InterfaceImmutableDictionaryFormatter" },
  202|         { "System.Collections.Immutable.IImmutableQueue<>", "MsgPack::ImmutableCollection.InterfaceImmutableQueueFormatter" },
  203|         { "System.Collections.Immutable.IImmutableSet<>", "MsgPack::ImmutableCollection.InterfaceImmutableSetFormatter" },
  204|         { "System.Collections.Immutable.IImmutableStack<>", "MsgPack::ImmutableCollection.InterfaceImmutableStackFormatter" },
  205| 
  206|         { "Reactive.Bindings.ReactiveProperty<>", "MsgPack::ReactivePropertyExtension.ReactivePropertyFormatter" },
  207|         { "Reactive.Bindings.IReactiveProperty<>", "MsgPack::ReactivePropertyExtension.InterfaceReactivePropertyFormatter" },
  208|         { "Reactive.Bindings.IReadOnlyReactiveProperty<>", "MsgPack::ReactivePropertyExtension.InterfaceReadOnlyReactivePropertyFormatter" },
  209|         { "Reactive.Bindings.ReactiveCollection<>", "MsgPack::ReactivePropertyExtension.ReactiveCollectionFormatter" },
  210| #pragma warning restore SA1509 // Opening braces should not be preceded by blank line
  211|     };
  212| 
  213|     private readonly AnalyzerOptions options;
  214|     private readonly ReferenceSymbols typeReferences;
  215| 
  216|     /// <summary>
  217|     /// The means of reporting diagnostics to the analyzer.
  218|     /// This will be <see langword="null" /> when running in the context of a source generator so as to avoid duplicate diagnostics.
  219|     /// </summary>
  220|     private readonly Action<Diagnostic>? reportDiagnostic;
  221| 
  222|     private readonly ITypeSymbol? targetType;
  223| 
  224|     // visitor workspace:
  225|     private readonly HashSet<ITypeSymbol> alreadyCollected = new(SymbolEqualityComparer.Default);
  226|     private readonly ImmutableSortedSet<ObjectSerializationInfo>.Builder collectedObjectInfo = ImmutableSortedSet.CreateBuilder<ObjectSerializationInfo>(ResolverRegisterInfoComparer.Default);
  227|     private readonly ImmutableSortedSet<EnumSerializationInfo>.Builder collectedEnumInfo = ImmutableSortedSet.CreateBuilder<EnumSerializationInfo>(ResolverRegisterInfoComparer.Default);
  228|     private readonly ImmutableSortedSet<GenericSerializationInfo>.Builder collectedGenericInfo = ImmutableSortedSet.CreateBuilder<GenericSerializationInfo>(ResolverRegisterInfoComparer.Default);
  229|     private readonly ImmutableSortedSet<UnionSerializationInfo>.Builder collectedUnionInfo = ImmutableSortedSet.CreateBuilder<UnionSerializationInfo>(ResolverRegisterInfoComparer.Default);
  230|     private readonly ImmutableSortedSet<ResolverRegisterInfo>.Builder collectedArrayInfo = ImmutableSortedSet.CreateBuilder<ResolverRegisterInfo>(ResolverRegisterInfoComparer.Default);
  231| 
  232|     private readonly Compilation compilation;
  233| 
  234|     private readonly CancellationToken cancellationToken;
  235| 
  236|     private TypeCollector(Compilation compilation, AnalyzerOptions options, ReferenceSymbols referenceSymbols, ITypeSymbol targetType, Action<Diagnostic>? reportAnalyzerDiagnostic, CancellationToken cancellationToken)
  237|     {
  238|         this.typeReferences = referenceSymbols;
  239|         this.reportDiagnostic = reportAnalyzerDiagnostic;
  240|         this.options = options;
  241|         this.compilation = compilation;
  242|         this.cancellationToken = cancellationToken;
  243| 
  244|         bool isInaccessible = false;
  245|         foreach (BaseTypeDeclarationSyntax? decl in CodeAnalysisUtilities.FindInaccessibleTypes(targetType))
  246|         {
  247|             isInaccessible = true;
  248|             reportAnalyzerDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.InaccessibleDataType, decl.Identifier.GetLocation()));
  249|         }
  250| 
  251|         if (!isInaccessible)
  252|         {
  253|             if (((targetType.TypeKind == TypeKind.Interface) && targetType.GetAttributes().Any(x2 => x2.AttributeClass.ApproximatelyEqual(this.typeReferences.UnionAttribute)))
  254|                 || ((targetType.TypeKind == TypeKind.Class && targetType.IsAbstract) && targetType.GetAttributes().Any(x2 => x2.AttributeClass.ApproximatelyEqual(this.typeReferences.UnionAttribute)))
  255|                 || ((targetType.TypeKind == TypeKind.Class) && targetType.GetAttributes().Any(x2 => x2.AttributeClass.ApproximatelyEqual(this.typeReferences.MessagePackObjectAttribute)))
  256|                 || ((targetType.TypeKind == TypeKind.Struct) && targetType.GetAttributes().Any(x2 => x2.AttributeClass.ApproximatelyEqual(this.typeReferences.MessagePackObjectAttribute))))
  257|             {
  258|                 this.targetType = targetType;
  259|             }
  260|         }
  261|     }
  262| 
  263|     public static FullModel? Collect(Compilation compilation, AnalyzerOptions options, ReferenceSymbols referenceSymbols, Action<Diagnostic>? reportAnalyzerDiagnostic, ITypeSymbol targetType, CancellationToken cancellationToken)
  264|     {
  265|         TypeCollector collector = new(compilation, options, referenceSymbols, targetType, reportAnalyzerDiagnostic, cancellationToken);
  266|         if (collector.targetType is null)
  267|         {
  268|             return null;
  269|         }
  270| 
  271|         FullModel model = collector.Collect();
  272|         return model;
  273|     }
  274| 
  275|     private void ResetWorkspace()
  276|     {
  277|         this.alreadyCollected.Clear();
  278|         this.collectedObjectInfo.Clear();
  279|         this.collectedEnumInfo.Clear();
  280|         this.collectedGenericInfo.Clear();
  281|         this.collectedUnionInfo.Clear();
  282|         this.collectedArrayInfo.Clear();
  283|     }
  284| 
  285|     // EntryPoint
  286|     public FullModel Collect()
  287|     {
  288|         this.ResetWorkspace();
  289| 
  290|         if (this.targetType is not null)
  291|         {
  292|             this.CollectCore(this.targetType);
  293|         }
  294| 
  295|         return new FullModel(
  296|             this.collectedObjectInfo.ToImmutable(),
  297|             this.collectedEnumInfo.ToImmutable(),
  298|             this.collectedGenericInfo.ToImmutable(),
  299|             this.collectedUnionInfo.ToImmutable(),
  300|             ImmutableSortedSet<CustomFormatterRegisterInfo>.Empty,
  301|             this.collectedArrayInfo.ToImmutable(),
  302|             this.options);
  303|     }
  304| 
  305|     // Gate of recursive collect
  306|     private void CollectCore(ITypeSymbol typeSymbol, ISymbol? callerSymbol = null)
  307|     {
  308|         this.cancellationToken.ThrowIfCancellationRequested();
  309| 
  310|         if (!this.alreadyCollected.Add(typeSymbol))
  311|         {
  312|             return;
  313|         }
  314| 
  315|         var typeSymbolString = typeSymbol.WithNullableAnnotation(NullableAnnotation.NotAnnotated).ToString();
  316|         if (!string.IsNullOrEmpty(typeSymbolString) && EmbeddedTypes.Contains(typeSymbolString))
  317|         {
  318|             return;
  319|         }
  320| 
  321|         FormattableType formattableType = new(typeSymbol, null);
  322|         if (this.options.AssumedFormattableTypes.Contains(formattableType) || this.options.AssumedFormattableTypes.Contains(formattableType with { IsFormatterInSameAssembly = true }))
  323|         {
  324|             return;
  325|         }
  326| 
  327|         if (typeSymbol is IArrayTypeSymbol arrayTypeSymbol)
  328|         {
  329|             this.CollectArray((IArrayTypeSymbol)this.ToTupleUnderlyingType(arrayTypeSymbol), callerSymbol);
  330|             return;
  331|         }
  332| 
  333|         if (typeSymbol is ITypeParameterSymbol)
  334|         {
  335|             return;
  336|         }
  337| 
  338|         if (!IsAllowAccessibility(typeSymbol))
  339|         {
  340|             return;
  341|         }
  342| 
  343|         if (!(typeSymbol is INamedTypeSymbol type))
  344|         {
  345|             return;
  346|         }
  347| 
  348|         var customFormatterAttr = typeSymbol.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.FormatterAttribute));
  349|         if (customFormatterAttr != null)
  350|         {
  351|             this.CheckValidMessagePackFormatterAttribute(customFormatterAttr);
  352|             return;
  353|         }
  354| 
  355|         if (type.EnumUnderlyingType != null)
  356|         {
  357|             this.CollectEnum(type, type.EnumUnderlyingType);
  358|             return;
  359|         }
  360| 
  361|         if (type.IsGenericType)
  362|         {
  363|             this.CollectGeneric((INamedTypeSymbol)this.ToTupleUnderlyingType(type), callerSymbol);
  364|             return;
  365|         }
  366| 
  367|         if (type.Locations[0].IsInMetadata)
  368|         {
  369|             return;
  370|         }
  371| 
  372|         if (type.TypeKind == TypeKind.Interface || (type.TypeKind == TypeKind.Class && type.IsAbstract))
  373|         {
  374|             this.CollectUnion(type);
  375|             return;
  376|         }
  377| 
  378|         this.CollectObject(type, callerSymbol);
  379|     }
  380| 
  381|     private void CollectEnum(INamedTypeSymbol type, ISymbol enumUnderlyingType)
  382|     {
  383|         this.collectedEnumInfo.Add(EnumSerializationInfo.Create(type, enumUnderlyingType, this.options.Generator.Resolver));
  384|     }
  385| 
  386|     private void CollectUnion(INamedTypeSymbol type)
  387|     {
  388|         if (!options.IsGeneratingSource)
  389|         {
  390|             // In analyzer-only mode, this method doesn't work.
  391|             return;
  392|         }
  393| 
  394|         ImmutableArray<TypedConstant>[] unionAttrs = type.GetAttributes().Where(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.UnionAttribute)).Select(x => x.ConstructorArguments).ToArray();
  395|         if (unionAttrs.Length == 0)
  396|         {
  397|             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.UnionAttributeRequired, type.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
  398|         }
  399| 
  400|         // 0, Int  1, SubType
  401|         UnionSubTypeInfo? UnionSubTypeInfoSelector(ImmutableArray<TypedConstant> x)
  402|         {
  403|             if (!(x[0] is { Value: int key }) || !(x[1] is { Value: ITypeSymbol typeSymbol }))
  404|             {
  405|                 this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AotUnionAttributeRequiresTypeArg, GetIdentifierLocation(type)));
  406|                 return null;
  407|             }
  408| 
  409|             CollectCore(typeSymbol);
  410| 
  411|             var typeName = typeSymbol.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat);
  412|             return new UnionSubTypeInfo(key, typeName);
  413|         }
  414| 
  415|         var info = UnionSerializationInfo.Create(
  416|             type,
  417|             unionAttrs.Select(UnionSubTypeInfoSelector).Where(i => i is not null).OrderBy(x => x!.Key).ToImmutableArray()!,
  418|             this.options.Generator.Resolver);
  419| 
  420|         this.collectedUnionInfo.Add(info);
  421|     }
  422| 
  423|     private void CollectGenericUnion(INamedTypeSymbol type)
  424|     {
  425|         var unionAttrs = type.GetAttributes().Where(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.UnionAttribute)).Select(x => x.ConstructorArguments);
  426|         using var enumerator = unionAttrs.GetEnumerator();
  427|         if (!enumerator.MoveNext())
  428|         {
  429|             return;
  430|         }
  431| 
  432|         do
  433|         {
  434|             var x = enumerator.Current;
  435|             if (x[1] is { Value: INamedTypeSymbol unionType } && !this.alreadyCollected.Contains(unionType))
  436|             {
  437|                 this.CollectCore(unionType);
  438|             }
  439|         }
  440|         while (enumerator.MoveNext());
  441|     }
  442| 
  443|     private void CollectArray(IArrayTypeSymbol array, ISymbol? callerSymbol)
  444|     {
  445|         ITypeSymbol elemType = array.ElementType;
  446| 
  447|         this.CollectCore(elemType, callerSymbol);
  448| 
  449|         if (elemType is ITypeParameterSymbol || (elemType is INamedTypeSymbol symbol && IsOpenGenericTypeRecursively(symbol)))
  450|         {
  451|             return;
  452|         }
  453| 
  454|         QualifiedTypeName elementTypeName = QualifiedTypeName.Create(elemType);
  455|         string? formatterName = array.Rank switch
  456|         {
  457|             1 => "ArrayFormatter",
  458|             2 => "TwoDimensionalArrayFormatter",
  459|             3 => "ThreeDimensionalArrayFormatter",
  460|             4 => "FourDimensionalArrayFormatter",
  461|             _ => null,
  462|         };
  463|         if (formatterName is null)
  464|         {
  465|             ////this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AotArrayRankTooHigh));
  466|             return;
  467|         }
  468| 
  469|         var info = ResolverRegisterInfo.CreateArray(array, this.options.Generator.Resolver) with
  470|         {
  471|             Formatter = new QualifiedNamedTypeName(TypeKind.Class)
  472|             {
  473|                 Container = new NamespaceTypeContainer("MsgPack::Formatters"),
  474|                 Name = formatterName,
  475|                 TypeParameters = ImmutableArray.Create(new GenericTypeParameterInfo("T")),
  476|                 TypeArguments = ImmutableArray.Create(elementTypeName),
  477|             },
  478|         };
  479|         this.collectedArrayInfo.Add(info);
  480|     }
  481| 
  482|     private ITypeSymbol ToTupleUnderlyingType(ITypeSymbol typeSymbol)
  483|     {
  484|         if (typeSymbol is IArrayTypeSymbol array)
  485|         {
  486|             return this.compilation.CreateArrayTypeSymbol(this.ToTupleUnderlyingType(array.ElementType), array.Rank);
  487|         }
  488| 
  489|         if (typeSymbol is not INamedTypeSymbol namedType || !namedType.IsGenericType)
  490|         {
  491|             return typeSymbol;
  492|         }
  493| 
  494|         namedType = namedType.TupleUnderlyingType ?? namedType;
  495|         var newTypeArguments = namedType.TypeArguments.Select(this.ToTupleUnderlyingType).ToArray();
  496|         if (!namedType.TypeArguments.SequenceEqual(newTypeArguments))
  497|         {
  498|             return namedType.ConstructedFrom.Construct(newTypeArguments);
  499|         }
  500| 
  501|         return namedType;
  502|     }
  503| 
  504|     private void CollectGeneric(INamedTypeSymbol type, ISymbol? callerSymbol)
  505|     {
  506|         INamedTypeSymbol typeDefinition = type.ConstructUnboundGenericType();
  507|         var genericTypeDefinitionString = typeDefinition.ToDisplayString();
  508|         string? genericTypeNamespace = type.ContainingNamespace?.ToDisplayString(SymbolDisplayFormat.MinimallyQualifiedFormat);
  509|         var fullName = type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat);
  510|         var isOpenGenericType = IsOpenGenericTypeRecursively(type);
  511|         string formattedTypeFullName = type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat);
  512|         string? formatterName;
  513| 
  514|         // nullable
  515|         if (genericTypeDefinitionString == "T?")
  516|         {
  517|             var firstTypeArgument = type.TypeArguments[0];
  518| 
  519|             if (EmbeddedTypes.Contains(firstTypeArgument.ToString()!))
  520|             {
  521|                 return;
  522|             }
  523| 
  524|             this.CollectCore(firstTypeArgument, callerSymbol);
  525| 
  526|             if (!isOpenGenericType)
  527|             {
  528|                 formatterName = $"NullableFormatter<{firstTypeArgument.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat)}>";
  529|                 var info = GenericSerializationInfo.Create(type, this.options.Generator.Resolver) with
  530|                 {
  531|                     Formatter = new QualifiedNamedTypeName(TypeKind.Class)
  532|                     {
  533|                         Name = formatterName,
  534|                         Container = new NamespaceTypeContainer("MsgPack::Formatters"),
  535|                     },
  536|                 };
  537|                 this.collectedGenericInfo.Add(info);
  538|             }
  539| 
  540|             return;
  541|         }
  542| 
  543|         // collection
  544|         string? formatterFullName;
  545|         if (KnownGenericTypes.TryGetValue(genericTypeDefinitionString, out formatterFullName))
  546|         {
  547|             foreach (ITypeSymbol item in type.TypeArguments)
  548|             {
  549|                 this.CollectCore(item, callerSymbol);
  550|             }
  551| 
  552|             GenericSerializationInfo info;
  553| 
  554|             if (isOpenGenericType)
  555|             {
  556|                 return;
  557|             }
  558|             else
  559|             {
  560|                 info = GenericSerializationInfo.Create(type, this.options.Generator.Resolver);
  561|                 int indexOfLastPeriod = formatterFullName.LastIndexOf('.');
  562|                 info = info with
  563|                 {
  564|                     Formatter = new(TypeKind.Class)
  565|                     {
  566|                         Container = new NamespaceTypeContainer(formatterFullName.Substring(0, indexOfLastPeriod)),
  567|                         Name = formatterFullName.Substring(indexOfLastPeriod + 1),
  568|                         TypeParameters = GetTypeParameters(info.DataType),
  569|                         TypeArguments = GetTypeArguments(info.DataType),
  570|                     },
  571|                 };
  572| 
  573|                 this.collectedGenericInfo.Add(info);
  574|             }
  575| 
  576|             if (genericTypeDefinitionString != "System.Linq.ILookup<,>")
  577|             {
  578|                 return;
  579|             }
  580| 
  581|             formatterName = KnownGenericTypes["System.Linq.IGrouping<,>"];
  582| 
  583|             var groupingInfo = GenericSerializationInfo.Create(type, this.options.Generator.Resolver);
  584|             groupingInfo = groupingInfo with
  585|             {
  586|                 DataType = new QualifiedNamedTypeName(TypeKind.Interface)
  587|                 {
  588|                     Container = new NamespaceTypeContainer("global::System.Linq"),
  589|                     Name = "IGrouping",
  590|                     TypeParameters = GetTypeParameters(info.DataType),
  591|                 },
  592|                 Formatter = groupingInfo.Formatter with { Name = formatterName },
  593|             };
  594|             this.collectedGenericInfo.Add(groupingInfo);
  595| 
  596|             formatterName = KnownGenericTypes["System.Collections.Generic.IEnumerable<>"];
  597| 
  598|             GenericSerializationInfo enumerableInfo = GenericSerializationInfo.Create(type, this.options.Generator.Resolver);
  599|             enumerableInfo = enumerableInfo with
  600|             {
  601|                 DataType = new QualifiedNamedTypeName(TypeKind.Interface)
  602|                 {
  603|                     Container = new NamespaceTypeContainer("System.Collections.Generic"),
  604|                     Name = "IEnumerable",
  605|                     TypeParameters = ImmutableArray.Create(GetTypeParameters(info.DataType)[1]),
  606|                 },
  607|                 Formatter = enumerableInfo.Formatter with { Name = formatterName },
  608|             };
  609|             this.collectedGenericInfo.Add(enumerableInfo);
  610|             return;
  611|         }
  612| 
  613|         if (type.AllInterfaces.FirstOrDefault(x => !x.IsUnboundGenericType && x.ConstructUnboundGenericType() is { Name: nameof(ICollection<int>) }) is INamedTypeSymbol collectionIface
  614|             && type.InstanceConstructors.Any(ctor => ctor.Parameters.Length == 0))
  615|         {
  616|             this.CollectCore(collectionIface.TypeArguments[0], callerSymbol);
  617| 
  618|             if (isOpenGenericType)
  619|             {
  620|                 return;
  621|             }
  622|             else
  623|             {
  624|                 GenericSerializationInfo info = GenericSerializationInfo.Create(type, this.options.Generator.Resolver) with
  625|                 {
  626|                     Formatter = new(TypeKind.Class)
  627|                     {
  628|                         Container = new NamespaceTypeContainer("MsgPack::Formatters"),
  629|                         Name = "GenericCollectionFormatter",
  630|                         TypeParameters = ImmutableArray.Create<GenericTypeParameterInfo>(new("TElement"), new("TCollection")),
  631|                         TypeArguments = ImmutableArray.Create<QualifiedTypeName>(QualifiedTypeName.Create(collectionIface.TypeArguments[0]), QualifiedTypeName.Create(type)),
  632|                     },
  633|                 };
  634| 
  635|                 this.collectedGenericInfo.Add(info);
  636|                 return;
  637|             }
  638|         }
  639| 
  640|         // Generic types
  641|         if (type.IsDefinition)
  642|         {
  643|             this.CollectGenericUnion(type);
  644|             this.CollectObject(type, callerSymbol);
  645|         }
  646|         else
  647|         {
  648|             // Collect substituted types for the properties and fields.
  649|             // NOTE: It is used to register formatters from nested generic type.
  650|             //       However, closed generic types such as `Foo<string>` are not registered as a formatter.
  651|             this.GetObjectInfo(type, callerSymbol);
  652| 
  653|             // Collect generic type definition, that is not collected when it is defined outside target project.
  654|             this.CollectCore(type.OriginalDefinition, callerSymbol);
  655|         }
  656| 
  657|         // Collect substituted types for the type parameters (e.g. Bar in Foo<Bar>)
  658|         foreach (var item in type.TypeArguments)
  659|         {
  660|             this.CollectCore(item, callerSymbol);
  661|         }
  662| 
  663|         if (!isOpenGenericType)
  664|         {
  665|             GenericSerializationInfo genericSerializationInfo = GenericSerializationInfo.Create(type, this.options.Generator.Resolver);
  666|             this.collectedGenericInfo.Add(genericSerializationInfo);
  667|         }
  668| 
  669|         static ImmutableArray<GenericTypeParameterInfo> GetTypeParameters(QualifiedTypeName qtn)
  670|             => qtn is QualifiedNamedTypeName named ? named.TypeParameters : ImmutableArray<GenericTypeParameterInfo>.Empty;
  671| 
  672|         static ImmutableArray<QualifiedTypeName> GetTypeArguments(QualifiedTypeName qtn)
  673|             => qtn is QualifiedNamedTypeName named ? named.TypeArguments : ImmutableArray<QualifiedTypeName>.Empty;
  674|     }
  675| 
  676|     private void CollectObject(INamedTypeSymbol type, ISymbol? callerSymbol)
  677|     {
  678|         ObjectSerializationInfo? info = this.GetObjectInfo(type, callerSymbol);
  679|         if (info is not null)
  680|         {
  681|             this.collectedObjectInfo.Add(info);
  682|         }
  683|     }
  684| 
  685|     private void CheckValidMessagePackFormatterAttribute(AttributeData formatterAttribute)
  686|     {
  687|         if (formatterAttribute.ConstructorArguments[0].Value is ITypeSymbol formatterType)
  688|         {
  689|             // Validate that the typed formatter is actually of `IMessagePackFormatter`
  690|             bool isMessagePackFormatter = formatterType.AllInterfaces.Any(x => SymbolEqualityComparer.Default.Equals(x, this.typeReferences.MessagePackFormatter));
  691|             if (!isMessagePackFormatter)
  692|             {
  693|                 Location? location = ((AttributeSyntax?)formatterAttribute.ApplicationSyntaxReference?.GetSyntax())?.ArgumentList?.Arguments[0].GetLocation();
  694|                 ImmutableDictionary<string, string?> typeInfo = ImmutableDictionary.Create<string, string?>().Add("type", formatterType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat));
  695|                 this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.MessageFormatterMustBeMessagePackFormatter, location, typeInfo));
  696|             }
  697|         }
  698|     }
  699| 
  700|     private ObjectSerializationInfo? GetObjectInfo(INamedTypeSymbol formattedType, ISymbol? callerSymbol)
  701|     {
  702|         var isClass = !formattedType.IsValueType;
  703|         bool nestedFormatterRequired = false;
  704|         List<IPropertySymbol> nestedFormatterRequiredIfPropertyIsNotSetByDeserializingCtor = new();
  705| 
  706|         AttributeData? contractAttr = formattedType.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.MessagePackObjectAttribute));
  707| 
  708|         // Examine properties set on the attribute such that we can discern whether they were explicitly set or not.
  709|         // This is useful when we have assembly-level attributes or other environmentally-controlled defaults that the attribute may override either direction.
  710|         bool? suppressSourceGeneration = (bool?)contractAttr?.NamedArguments.FirstOrDefault(kvp => kvp.Key == Constants.SuppressSourceGenerationPropertyName).Value.Value;
  711|         bool? allowPrivateAttribute = (bool?)contractAttr?.NamedArguments.FirstOrDefault(kvp => kvp.Key == Constants.AllowPrivatePropertyName).Value.Value;
  712| 
  713|         if (contractAttr is null)
  714|         {
  715|             ////this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.TypeMustBeMessagePackObject, ((BaseTypeDeclarationSyntax)type.DeclaringSyntaxReferences[0].GetSyntax()).Identifier.GetLocation(), type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat)));
  716|         }
  717| 
  718|         bool isIntKey = true;
  719|         Dictionary<int, (MemberSerializationInfo Info, ITypeSymbol TypeSymbol)> intMembers = new();
  720|         Dictionary<string, (MemberSerializationInfo Info, ITypeSymbol TypeSymbol)> stringMembers = new();
  721| 
  722|         // We default to not requiring non-public members to be attributed,
  723|         // but as soon as the first non-public member *is* attributed,
  724|         // we'll require all non-public members to be attributed.
  725|         // Historically, only public members were able to be serialized by default,
  726|         // so the analyzer only highlighted missing attributes on public members.
  727|         // But once it's clear that the developer is serializing non-public members,
  728|         // we need to raise the bar for all non-public members.
  729|         bool nonPublicMembersAreSerialized = false;
  730|         List<Diagnostic> deferredDiagnosticsForNonPublicMembers = new();
  731| 
  732|         FormatterDescriptor? GetSpecialFormatter(ISymbol member)
  733|         {
  734|             INamedTypeSymbol? name = member.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.FormatterAttribute))?.ConstructorArguments[0].Value as INamedTypeSymbol;
  735|             if (name is not null)
  736|             {
  737|                 if (FormatterDescriptor.TryCreate(name, out FormatterDescriptor? descriptor))
  738|                 {
  739|                     return descriptor;
  740|                 }
  741|                 else
  742|                 {
  743|                     // Report that the named type is not a formatter.
  744|                     // this.reportDiagnostic();
  745|                 }
  746|             }
  747| 
  748|             return null;
  749|         }
  750| 
  751|         HashSet<Diagnostic> reportedDiagnostics = new();
  752|         IEnumerable<ISymbol> instanceMembers = formattedType.GetAllMembers()
  753|             .Where(m => m is IFieldSymbol or IPropertySymbol && !(m.IsStatic || m.IsOverride || m.IsImplicitlyDeclared));
  754| 
  755|         // The actual member identifiers of each serializable member,
  756|         // such that we'll recognize collisions as we enumerate members in base types
  757|         // and record that that happened so that the emitted source generator can apply the necessary casts.
  758|         // In particular this does NOT store substitute names given by KeyAttribute.Name.
  759|         // Members should be added to this set after they are verified to be accessible, instance, non-override properties,
  760|         // whether or not those members are serialized.
  761|         HashSet<string> collidingMemberNames = new(StringComparer.Ordinal);
  762|         HashSet<string> observedMemberNames = new(StringComparer.Ordinal);
  763|         foreach (ISymbol member in instanceMembers)
  764|         {
  765|             if (!observedMemberNames.Add(member.Name))
  766|             {
  767|                 collidingMemberNames.Add(member.Name);
  768|             }
  769|         }
  770| 
  771|         QualifiedNamedTypeName? GetDeclaringTypeIfColliding(ISymbol symbol) => collidingMemberNames.Contains(symbol.Name) && !SymbolEqualityComparer.Default.Equals(symbol.ContainingType, formattedType) ? new(symbol.ContainingType) : null;
  772| 
  773|         if (this.options.Generator.Formatters.UsesMapMode || (contractAttr?.ConstructorArguments[0] is { Value: true }))
  774|         {
  775|             Dictionary<string, ISymbol> claimedKeys = new(StringComparer.Ordinal);
  776|             void ReportNonUniqueNameIfApplicable(ISymbol item, string stringKey)
  777|             {
  778|                 if (claimedKeys.TryGetValue(stringKey, out ISymbol newSymbol))
  779|                 {
  780|                     SyntaxNode? syntax = newSymbol.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax(this.cancellationToken);
  781|                     var location = syntax switch
  782|                     {
  783|                         PropertyDeclarationSyntax { Identifier: SyntaxToken propertyId } => propertyId.GetLocation(),
  784|                         VariableDeclaratorSyntax { Identifier: SyntaxToken fieldId } => fieldId.GetLocation(),
  785|                         not null => syntax.GetLocation(),
  786|                         _ => null,
  787|                     };
  788| 
  789|                     reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.CollidingMemberNamesInForceMapMode, location));
  790|                 }
  791| 
  792|                 claimedKeys[stringKey] = item;
  793|             }
  794| 
  795|             // All public members are serialize target except [Ignore] member.
  796|             // Include private members if the type opted into that.
  797|             Accessibility minimumAccessibility = allowPrivateAttribute is true ? Accessibility.Private : Accessibility.Public;
  798|             isIntKey = false;
  799| 
  800|             var hiddenIntKey = 0;
  801| 
  802|             foreach (ISymbol baseItem in instanceMembers)
  803|             {
  804|                 switch (baseItem)
  805|                 {
  806|                     case IPropertySymbol item:
  807|                         {
  808|                             ImmutableArray<AttributeData> attributes = item.GetAttributes();
  809|                             if (attributes.Any(x => (x.AttributeClass.ApproximatelyEqual(this.typeReferences.IgnoreAttribute) || x.AttributeClass?.Name == this.typeReferences.IgnoreDataMemberAttribute?.Name)) ||
  810|                                 item.DeclaredAccessibility < minimumAccessibility)
  811|                             {
  812|                                 continue;
  813|                             }
  814| 
  815|                             bool isReadable = item.GetMethod is not null;
  816|                             bool isWritable = item.SetMethod is not null;
  817|                             if (!isReadable && !isWritable)
  818|                             {
  819|                                 continue;
  820|                             }
  821| 
  822|                             bool isInitOnly = item.SetMethod?.IsInitOnly is true;
  823|                             AttributeData? keyAttribute = attributes.FirstOrDefault(attributes => attributes.AttributeClass.ApproximatelyEqual(this.typeReferences.KeyAttribute));
  824|                             string stringKey = keyAttribute?.ConstructorArguments.Length == 1 && keyAttribute.ConstructorArguments[0].Value is string name ? name : item.Name;
  825|                             ReportNonUniqueNameIfApplicable(item, stringKey);
  826| 
  827|                             nestedFormatterRequired |= item.GetMethod is not null && IsPartialTypeRequired(item.GetMethod.DeclaredAccessibility);
  828|                             nestedFormatterRequired |= item.SetMethod is not null && IsPartialTypeRequired(item.SetMethod.DeclaredAccessibility);
  829|                             FormatterDescriptor? specialFormatter = GetSpecialFormatter(item);
  830|                             MemberSerializationInfo member = new(true, isWritable, isReadable, isInitOnly, item.IsRequired, hiddenIntKey++, stringKey, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
  831|                             {
  832|                                 DeclaringType = GetDeclaringTypeIfColliding(item),
  833|                             };
  834|                             if (!stringMembers.ContainsKey(member.StringKey))
  835|                             {
  836|                                 stringMembers.Add(member.StringKey, (member, item.Type));
  837|                             }
  838| 
  839|                             if (specialFormatter is null)
  840|                             {
  841|                                 this.CollectCore(item.Type, item); // recursive collect
  842|                             }
  843|                         }
  844| 
  845|                         break;
  846|                     case IFieldSymbol item:
  847|                         {
  848|                             ImmutableArray<AttributeData> attributes = item.GetAttributes();
  849|                             if (attributes.Any(x => (x.AttributeClass.ApproximatelyEqual(this.typeReferences.IgnoreAttribute) || x.AttributeClass?.Name == this.typeReferences.IgnoreDataMemberAttribute?.Name)) ||
  850|                                 item.DeclaredAccessibility < minimumAccessibility)
  851|                             {
  852|                                 continue;
  853|                             }
  854| 
  855|                             AttributeData? keyAttribute = attributes.FirstOrDefault(attributes => attributes.AttributeClass.ApproximatelyEqual(this.typeReferences.KeyAttribute));
  856|                             string stringKey = keyAttribute?.ConstructorArguments.Length == 1 && keyAttribute.ConstructorArguments[0].Value is string name ? name : item.Name;
  857|                             ReportNonUniqueNameIfApplicable(item, stringKey);
  858| 
  859|                             nestedFormatterRequired |= IsPartialTypeRequired(item.DeclaredAccessibility);
  860|                             FormatterDescriptor? specialFormatter = GetSpecialFormatter(item);
  861|                             MemberSerializationInfo member = new(false, IsWritable: !item.IsReadOnly, IsReadable: true, IsInitOnly: false, item.IsRequired, hiddenIntKey++, stringKey, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
  862|                             {
  863|                                 DeclaringType = GetDeclaringTypeIfColliding(item),
  864|                             };
  865|                             if (!stringMembers.ContainsKey(member.StringKey))
  866|                             {
  867|                                 stringMembers.Add(member.StringKey, (member, item.Type));
  868|                             }
  869| 
  870|                             if (specialFormatter is null)
  871|                             {
  872|                                 this.CollectCore(item.Type, item); // recursive collect
  873|                             }
  874|                         }
  875| 
  876|                         break;
  877|                 }
  878|             }
  879|         }
  880|         else
  881|         {
  882|             // Only KeyAttribute members
  883|             var searchFirst = true;
  884|             var hiddenIntKey = 0;
  885| 
  886|             foreach (IPropertySymbol item in instanceMembers.OfType<IPropertySymbol>())
  887|             {
  888|                 if (item.IsIndexer)
  889|                 {
  890|                     continue; // .tt files don't generate good code for this yet: https://github.com/neuecc/MessagePack-CSharp/issues/390
  891|                 }
  892| 
  893|                 if (item.GetAttributes().Any(x =>
  894|                 {
  895|                     var typeReferencesIgnoreDataMemberAttribute = this.typeReferences.IgnoreDataMemberAttribute;
  896|                     return typeReferencesIgnoreDataMemberAttribute != null && (x.AttributeClass.ApproximatelyEqual(this.typeReferences.IgnoreAttribute) || x.AttributeClass.ApproximatelyEqual(typeReferencesIgnoreDataMemberAttribute));
  897|                 }))
  898|                 {
  899|                     nonPublicMembersAreSerialized |= (item.DeclaredAccessibility & Accessibility.Public) != Accessibility.Public;
  900|                     continue;
  901|                 }
  902| 
  903|                 bool isReadable = item.GetMethod is not null;
  904|                 bool isWritable = item.SetMethod is not null;
  905|                 bool isInitOnly = item.SetMethod?.IsInitOnly is true;
  906|                 if (!isReadable && !isWritable)
  907|                 {
  908|                     continue;
  909|                 }
  910| 
  911|                 FormatterDescriptor? specialFormatter = GetSpecialFormatter(item);
  912|                 TypedConstant? key = item.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.KeyAttribute))?.ConstructorArguments[0];
  913|                 if (key is null)
  914|                 {
  915|                     if (contractAttr is not null)
  916|                     {
  917|                         // If the member is attributed with a type derived from KeyAttribute, that's incompatible with source generation
  918|                         // since we cannot know what the key is using only C# syntax and the semantic model.
  919|                         SyntaxReference? derivedKeyAttribute = item.GetAttributes().FirstOrDefault(att => att.AttributeClass.IsApproximatelyEqualOrDerivedFrom(this.typeReferences.KeyAttribute) == RoslynAnalyzerExtensions.EqualityMatch.LeftDerivesFromRight)?.ApplicationSyntaxReference;
  920| 
  921|                         if (derivedKeyAttribute is null || suppressSourceGeneration is not true)
  922|                         {
  923|                             if (SymbolEqualityComparer.Default.Equals(item.ContainingType, formattedType))
  924|                             {
  925|                                 var syntax = item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax();
  926|                                 var identifier = (syntax as PropertyDeclarationSyntax)?.Identifier ?? (syntax as ParameterSyntax)?.Identifier;
  927| 
  928|                                 Diagnostic diagnostic = derivedKeyAttribute is not null && suppressSourceGeneration is not true
  929|                                     ? Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AOTDerivedKeyAttribute, derivedKeyAttribute.GetSyntax(this.cancellationToken).GetLocation())
  930|                                     : Diagnostic.Create(MsgPack00xMessagePackAnalyzer.MemberNeedsKey, identifier?.GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name);
  931|                                 if (nonPublicMembersAreSerialized || (item.DeclaredAccessibility & Accessibility.Public) == Accessibility.Public)
  932|                                 {
  933|                                     this.reportDiagnostic?.Invoke(diagnostic);
  934|                                 }
  935|                                 else
  936|                                 {
  937|                                     deferredDiagnosticsForNonPublicMembers.Add(diagnostic);
  938|                                 }
  939|                             }
  940|                             else if (formattedType.BaseType is not null)
  941|                             {
  942|                                 // The member was inherited, so we raise a special error at the location of the base type reference.
  943|                                 BaseTypeSyntax? baseSyntax = formattedType.DeclaringSyntaxReferences.SelectMany(sr => (IEnumerable<BaseTypeSyntax>?)((BaseTypeDeclarationSyntax)sr.GetSyntax()).BaseList?.Types ?? Array.Empty<BaseTypeSyntax>())
  944|                                     .FirstOrDefault(bt => SymbolEqualityComparer.Default.Equals(this.compilation.GetSemanticModel(bt.SyntaxTree).GetTypeInfo(bt.Type).Type, item.ContainingType));
  945|                                 if (baseSyntax is not null)
  946|                                 {
  947|                                     Diagnostic diagnostic = derivedKeyAttribute is not null && suppressSourceGeneration is not true
  948|                                         ? Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AOTDerivedKeyAttribute, baseSyntax.GetLocation())
  949|                                         : Diagnostic.Create(
  950|                                             MsgPack00xMessagePackAnalyzer.BaseTypeContainsUnattributedPublicMembers,
  951|                                             baseSyntax.GetLocation(),
  952|                                             item.ContainingType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat),
  953|                                             item.Name);
  954|                                     if (reportedDiagnostics.Add(diagnostic))
  955|                                     {
  956|                                         if (nonPublicMembersAreSerialized || (item.DeclaredAccessibility & Accessibility.Public) == Accessibility.Public)
  957|                                         {
  958|                                             this.reportDiagnostic?.Invoke(diagnostic);
  959|                                         }
  960|                                         else
  961|                                         {
  962|                                             deferredDiagnosticsForNonPublicMembers.Add(diagnostic);
  963|                                         }
  964|                                     }
  965|                                 }
  966|                             }
  967|                         }
  968|                     }
  969|                 }
  970|                 else
  971|                 {
  972|                     // If this attributed member is non-public, then all non-public members should be attributed.
  973|                     nonPublicMembersAreSerialized |= (item.DeclaredAccessibility & Accessibility.Public) != Accessibility.Public;
  974| 
  975|                     nestedFormatterRequired |= item.GetMethod is not null && IsPartialTypeRequired(item.GetMethod.DeclaredAccessibility);
  976|                     if (item.SetMethod is not null && IsPartialTypeRequired(item.SetMethod.DeclaredAccessibility))
  977|                     {
  978|                         nestedFormatterRequiredIfPropertyIsNotSetByDeserializingCtor.Add(item);
  979|                     }
  980| 
  981|                     var intKey = key is { Value: int intKeyValue } ? intKeyValue : default(int?);
  982|                     var stringKey = key is { Value: string stringKeyValue } ? stringKeyValue : default;
  983|                     if (intKey == null && stringKey == null)
  984|                     {
  985|                         this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.BothStringAndIntKeyAreNull, (item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax() as PropertyDeclarationSyntax)?.Identifier.GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name));
  986|                     }
  987| 
  988|                     // A property with an init accessor and an initializer has a default that will be discarded by the deserializer.
  989|                     if (suppressSourceGeneration is not true && isInitOnly)
  990|                     {
  991|                         EqualsValueClauseSyntax? initializer = item.DeclaringSyntaxReferences.Select(s => (s.GetSyntax(this.cancellationToken) as PropertyDeclarationSyntax)?.Initializer).FirstOrDefault(i => i is not null);
  992|                         if (initializer is not null)
  993|                         {
  994|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AOTInitProperty, initializer.GetLocation()));
  995|                         }
  996|                     }
  997| 
  998|                     if (searchFirst)
  999|                     {
 1000|                         searchFirst = false;
 1001|                         isIntKey = intKey != null;
 1002|                     }
 1003|                     else
 1004|                     {
 1005|                         if ((isIntKey && intKey == null) || (!isIntKey && stringKey == null))
 1006|                         {
 1007|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.DoNotMixStringAndIntKeys, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
 1008|                         }
 1009|                     }
 1010| 
 1011|                     if (isIntKey)
 1012|                     {
 1013|                         if (intMembers.ContainsKey(intKey!.Value))
 1014|                         {
 1015|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.KeysMustBeUnique, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
 1016|                         }
 1017| 
 1018|                         var member = new MemberSerializationInfo(true, isWritable, isReadable, isInitOnly, item.IsRequired, intKey!.Value, item.Name, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
 1019|                         {
 1020|                             DeclaringType = GetDeclaringTypeIfColliding(item),
 1021|                         };
 1022|                         intMembers.Add(member.IntKey, (member, item.Type));
 1023|                     }
 1024|                     else if (stringKey is not null)
 1025|                     {
 1026|                         if (stringMembers.ContainsKey(stringKey!))
 1027|                         {
 1028|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.KeysMustBeUnique, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
 1029|                         }
 1030| 
 1031|                         var member = new MemberSerializationInfo(true, isWritable, isReadable, isInitOnly, item.IsRequired, hiddenIntKey++, stringKey!, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
 1032|                         {
 1033|                             DeclaringType = GetDeclaringTypeIfColliding(item),
 1034|                         };
 1035|                         stringMembers.Add(member.StringKey, (member, item.Type));
 1036|                     }
 1037| 
 1038|                     var messagePackFormatter = item.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.FormatterAttribute))?.ConstructorArguments[0];
 1039| 
 1040|                     if (messagePackFormatter == null)
 1041|                     {
 1042|                         // recursive collect
 1043|                         this.CollectCore(item.Type, item);
 1044|                     }
 1045|                 }
 1046|             }
 1047| 
 1048|             foreach (IFieldSymbol item in formattedType.GetAllMembers().OfType<IFieldSymbol>())
 1049|             {
 1050|                 if (item.IsImplicitlyDeclared || item.IsStatic)
 1051|                 {
 1052|                     continue;
 1053|                 }
 1054| 
 1055|                 if (item.GetAttributes().Any(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.IgnoreAttribute)))
 1056|                 {
 1057|                     nonPublicMembersAreSerialized |= (item.DeclaredAccessibility & Accessibility.Public) != Accessibility.Public;
 1058|                     continue;
 1059|                 }
 1060| 
 1061|                 FormatterDescriptor? specialFormatter = GetSpecialFormatter(item);
 1062|                 TypedConstant? key = item.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.KeyAttribute))?.ConstructorArguments[0];
 1063|                 if (key is null)
 1064|                 {
 1065|                     if (contractAttr is not null)
 1066|                     {
 1067|                         // If the member is attributed with a type derived from KeyAttribute, that's incompatible with source generation
 1068|                         // since we cannot know what the key is using only C# syntax and the semantic model.
 1069|                         SyntaxReference? derivedKeyAttribute = item.GetAttributes().FirstOrDefault(att => att.AttributeClass.IsApproximatelyEqualOrDerivedFrom(this.typeReferences.KeyAttribute) == RoslynAnalyzerExtensions.EqualityMatch.LeftDerivesFromRight)?.ApplicationSyntaxReference;
 1070| 
 1071|                         if (derivedKeyAttribute is null || suppressSourceGeneration is not true)
 1072|                         {
 1073|                             if (SymbolEqualityComparer.Default.Equals(item.ContainingType, formattedType))
 1074|                             {
 1075|                                 Diagnostic diagnostic = derivedKeyAttribute is not null && suppressSourceGeneration is not true
 1076|                                     ? Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AOTDerivedKeyAttribute, derivedKeyAttribute.GetSyntax(this.cancellationToken).GetLocation())
 1077|                                     : Diagnostic.Create(MsgPack00xMessagePackAnalyzer.MemberNeedsKey, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name);
 1078|                                 if (nonPublicMembersAreSerialized || (item.DeclaredAccessibility & Accessibility.Public) == Accessibility.Public)
 1079|                                 {
 1080|                                     this.reportDiagnostic?.Invoke(diagnostic);
 1081|                                 }
 1082|                                 else
 1083|                                 {
 1084|                                     deferredDiagnosticsForNonPublicMembers.Add(diagnostic);
 1085|                                 }
 1086|                             }
 1087|                             else if (formattedType.BaseType is not null)
 1088|                             {
 1089|                                 // The member was inherited, so we raise a special error at the location of the base type reference.
 1090|                                 BaseTypeSyntax? baseSyntax = formattedType.DeclaringSyntaxReferences.SelectMany(sr => (IEnumerable<BaseTypeSyntax>?)((BaseTypeDeclarationSyntax)sr.GetSyntax()).BaseList?.Types ?? Array.Empty<BaseTypeSyntax>())
 1091|                                     .FirstOrDefault(bt => SymbolEqualityComparer.Default.Equals(this.compilation.GetSemanticModel(bt.SyntaxTree).GetTypeInfo(bt.Type).Type, item.ContainingType));
 1092|                                 if (baseSyntax is not null)
 1093|                                 {
 1094|                                     Diagnostic diagnostic = derivedKeyAttribute is not null && suppressSourceGeneration is not true
 1095|                                         ? Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AOTDerivedKeyAttribute, baseSyntax.GetLocation())
 1096|                                         : Diagnostic.Create(
 1097|                                             MsgPack00xMessagePackAnalyzer.BaseTypeContainsUnattributedPublicMembers,
 1098|                                             baseSyntax.GetLocation(),
 1099|                                             item.ContainingType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat),
 1100|                                             item.Name);
 1101|                                     if (reportedDiagnostics.Add(diagnostic))
 1102|                                     {
 1103|                                         if (nonPublicMembersAreSerialized || (item.DeclaredAccessibility & Accessibility.Public) == Accessibility.Public)
 1104|                                         {
 1105|                                             this.reportDiagnostic?.Invoke(diagnostic);
 1106|                                         }
 1107|                                         else
 1108|                                         {
 1109|                                             deferredDiagnosticsForNonPublicMembers.Add(diagnostic);
 1110|                                         }
 1111|                                     }
 1112|                                 }
 1113|                             }
 1114|                         }
 1115|                     }
 1116|                 }
 1117|                 else
 1118|                 {
 1119|                     // If this attributed member is non-public, then all non-public members should be attributed.
 1120|                     nonPublicMembersAreSerialized |= (item.DeclaredAccessibility & Accessibility.Public) != Accessibility.Public;
 1121| 
 1122|                     nestedFormatterRequired |= IsPartialTypeRequired(item.DeclaredAccessibility);
 1123| 
 1124|                     var intKey = key is { Value: int intKeyValue } ? intKeyValue : default(int?);
 1125|                     var stringKey = key is { Value: string stringKeyValue } ? stringKeyValue : default;
 1126|                     if (intKey == null && stringKey == null)
 1127|                     {
 1128|                         this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.BothStringAndIntKeyAreNull, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
 1129|                     }
 1130| 
 1131|                     if (searchFirst)
 1132|                     {
 1133|                         searchFirst = false;
 1134|                         isIntKey = intKey != null;
 1135|                     }
 1136|                     else
 1137|                     {
 1138|                         if ((isIntKey && intKey == null) || (!isIntKey && stringKey == null))
 1139|                         {
 1140|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.DoNotMixStringAndIntKeys, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
 1141|                         }
 1142|                     }
 1143| 
 1144|                     if (isIntKey)
 1145|                     {
 1146|                         if (intMembers.ContainsKey(intKey!.Value))
 1147|                         {
 1148|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.KeysMustBeUnique, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
 1149|                         }
 1150| 
 1151|                         var member = new MemberSerializationInfo(true, IsWritable: !item.IsReadOnly, IsReadable: true, IsInitOnly: false, item.IsRequired, intKey!.Value, item.Name, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
 1152|                         {
 1153|                             DeclaringType = GetDeclaringTypeIfColliding(item),
 1154|                         };
 1155|                         intMembers.Add(member.IntKey, (member, item.Type));
 1156|                     }
 1157|                     else
 1158|                     {
 1159|                         if (stringMembers.ContainsKey(stringKey!))
 1160|                         {
 1161|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.KeysMustBeUnique, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
 1162|                         }
 1163| 
 1164|                         var member = new MemberSerializationInfo(true, IsWritable: !item.IsReadOnly, IsReadable: true, IsInitOnly: false, item.IsRequired, hiddenIntKey++, stringKey!, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
 1165|                         {
 1166|                             DeclaringType = GetDeclaringTypeIfColliding(item),
 1167|                         };
 1168|                         stringMembers.Add(member.StringKey, (member, item.Type));
 1169|                     }
 1170| 
 1171|                     var messagePackFormatter = item.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.FormatterAttribute))?.ConstructorArguments[0];
 1172| 
 1173|                     if (messagePackFormatter == null)
 1174|                     {
 1175|                         // recursive collect
 1176|                         this.CollectCore(item.Type, item);
 1177|                     }
 1178|                 }
 1179|             }
 1180|         }
 1181| 
 1182|         // If we discovered midway through that we should be reporting diagnostics for non-public members,
 1183|         // report the ones we missed along the way.
 1184|         if ((nonPublicMembersAreSerialized || allowPrivateAttribute is true) && this.reportDiagnostic is not null)
 1185|         {
 1186|             foreach (Diagnostic deferred in deferredDiagnosticsForNonPublicMembers)
 1187|             {
 1188|                 this.reportDiagnostic(deferred);
 1189|             }
 1190|         }
 1191| 
 1192|         // GetConstructor
 1193|         var ctorEnumerator = default(IEnumerator<IMethodSymbol>);
 1194|         var ctor = formattedType.Constructors.SingleOrDefault(x => x.GetAttributes().Any(y => y.AttributeClass != null && y.AttributeClass.ApproximatelyEqual(this.typeReferences.SerializationConstructorAttribute)));
 1195|         if (ctor is null)
 1196|         {
 1197|             ctorEnumerator = formattedType.Constructors
 1198|                 .OrderByDescending(x => x.DeclaredAccessibility)
 1199|                 .ThenByDescending(x => x.Parameters.Length)
 1200|                 .GetEnumerator();
 1201| 
 1202|             if (ctorEnumerator.MoveNext())
 1203|             {
 1204|                 ctor = ctorEnumerator.Current;
 1205|             }
 1206|         }
 1207| 
 1208|         // struct allows null ctor
 1209|         if (ctor is null && isClass)
 1210|         {
 1211|             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.NoDeserializingConstructor, GetIdentifierLocation(formattedType)));
 1212|             return null;
 1213|         }
 1214| 
 1215|         var constructorParameters = new List<MemberSerializationInfo>();
 1216|         if (ctor is not null)
 1217|         {
 1218|             nestedFormatterRequired |= IsPartialTypeRequired(ctor.DeclaredAccessibility);
 1219| 
 1220|             var constructorLookupDictionary = stringMembers.ToLookup(x => x.Value.Info.Name, x => x, StringComparer.OrdinalIgnoreCase);
 1221|             IReadOnlyDictionary<int, (MemberSerializationInfo Info, ITypeSymbol TypeSymbol)> ctorParamIndexIntMembersDictionary = intMembers
 1222|                 .OrderBy(x => x.Key).Select((x, i) => (Key: x.Value, Index: i))
 1223|                 .ToDictionary(x => x.Index, x => x.Key);
 1224|             do
 1225|             {
 1226|                 constructorParameters.Clear();
 1227|                 var ctorParamIndex = 0;
 1228|                 foreach (IParameterSymbol item in ctor!.Parameters)
 1229|                 {
 1230|                     if (isIntKey)
 1231|                     {
 1232|                         if (ctorParamIndexIntMembersDictionary.TryGetValue(ctorParamIndex, out (MemberSerializationInfo Info, ITypeSymbol TypeSymbol) member))
 1233|                         {
 1234|                             if (this.compilation.ClassifyConversion(member.TypeSymbol, item.Type) is { IsImplicit: true } && member.Info.IsReadable)
 1235|                             {
 1236|                                 constructorParameters.Add(member.Info);
 1237|                             }
 1238|                             else
 1239|                             {
 1240|                                 if (ctorEnumerator != null)
 1241|                                 {
 1242|                                     ctor = null;
 1243|                                     continue;
 1244|                                 }
 1245|                                 else
 1246|                                 {
 1247|                                     this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.DeserializingConstructorParameterTypeMismatch, GetLocation(item)));
 1248|                                     return null;
 1249|                                 }
 1250|                             }
 1251|                         }
 1252|                         else
 1253|                         {
 1254|                             if (ctorEnumerator != null)
 1255|                             {
 1256|                                 ctor = null;
 1257|                                 continue;
 1258|                             }
 1259|                             else
 1260|                             {
 1261|                                 this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.DeserializingConstructorParameterIndexMissing, GetParameterListLocation(ctor)));
 1262|                                 return null;
 1263|                             }
 1264|                         }
 1265|                     }
 1266|                     else
 1267|                     {
 1268|                         IEnumerable<KeyValuePair<string, (MemberSerializationInfo Info, ITypeSymbol TypeSymbol)>> hasKey = constructorLookupDictionary[item.Name];
 1269|                         using var enumerator = hasKey.GetEnumerator();
 1270| 
 1271|                         // hasKey.Count() == 0
 1272|                         if (!enumerator.MoveNext())
 1273|                         {
 1274|                             if (ctorEnumerator == null)
 1275|                             {
 1276|                                 this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.DeserializingConstructorParameterNameMissing, GetParameterListLocation(ctor)));
 1277|                                 return null;
 1278|                             }
 1279| 
 1280|                             ctor = null;
 1281|                             continue;
 1282|                         }
 1283| 
 1284|                         var first = enumerator.Current.Value;
 1285| 
 1286|                         // hasKey.Count() != 1
 1287|                         if (enumerator.MoveNext())
 1288|                         {
 1289|                             if (ctorEnumerator == null)
 1290|                             {
 1291|                                 this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.DeserializingConstructorParameterNameDuplicate, GetLocation(item)));
 1292|                                 return null;
 1293|                             }
 1294| 
 1295|                             ctor = null;
 1296|                             continue;
 1297|                         }
 1298| 
 1299|                         MemberSerializationInfo paramMember = first.Info;
 1300|                         if (item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat) == paramMember.Type && paramMember.IsReadable)
 1301|                         {
 1302|                             constructorParameters.Add(paramMember);
 1303|                         }
 1304|                         else
 1305|                         {
 1306|                             if (ctorEnumerator == null)
 1307|                             {
 1308|                                 this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.DeserializingConstructorParameterTypeMismatch, GetLocation(item)));
 1309|                                 return null;
 1310|                             }
 1311| 
 1312|                             ctor = null;
 1313|                             continue;
 1314|                         }
 1315|                     }
 1316| 
 1317|                     ctorParamIndex++;
 1318|                 }
 1319|             }
 1320|             while (TryGetNextConstructor(ctorEnumerator, ref ctor));
 1321| 
 1322|             if (ctor == null)
 1323|             {
 1324|                 this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.NoDeserializingConstructor, GetIdentifierLocation(formattedType)));
 1325|             }
 1326|         }
 1327| 
 1328|         var hasSerializationConstructor = formattedType.AllInterfaces.Any(x => x.ApproximatelyEqual(this.typeReferences.IMessagePackSerializationCallbackReceiver));
 1329|         var needsCastOnBefore = true;
 1330|         var needsCastOnAfter = true;
 1331|         if (hasSerializationConstructor)
 1332|         {
 1333|             needsCastOnBefore = !formattedType.GetMembers("OnBeforeSerialize").Any();
 1334|             needsCastOnAfter = !formattedType.GetMembers("OnAfterDeserialize").Any();
 1335|         }
 1336| 
 1337|         if (contractAttr is null)
 1338|         {
 1339|             if (formattedType.IsDefinition)
 1340|             {
 1341|                 Location location = callerSymbol is not null ? callerSymbol.Locations[0] : formattedType.Locations[0];
 1342|                 var targetName = callerSymbol is not null ? callerSymbol.ContainingType.Name + "." + callerSymbol.Name : formattedType.Name;
 1343| 
 1344|                 ImmutableDictionary<string, string?> typeInfo = ImmutableDictionary.Create<string, string?>().Add("type", formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat));
 1345|                 this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.TypeMustBeMessagePackObject, location, typeInfo, targetName));
 1346|             }
 1347| 
 1348|             // Indicate to our caller that we don't have a valid object.
 1349|             return null;
 1350|         }
 1351| 
 1352|         if (allowPrivateAttribute is not true && (nonPublicMembersAreSerialized || ctor is { DeclaredAccessibility: not Accessibility.Public } || formattedType.GetEffectiveAccessibility() is not Accessibility.Public))
 1353|         {
 1354|             if (contractAttr.ApplicationSyntaxReference?.GetSyntax(this.cancellationToken) is AttributeSyntax attSyntax)
 1355|             {
 1356|                 Location location = attSyntax.GetLocation();
 1357| 
 1358|                 // If the user is explicitly setting AllowPrivate = false, set the location more precisely.
 1359|                 if (allowPrivateAttribute is false)
 1360|                 {
 1361|                     location = attSyntax.ArgumentList?.Arguments.First(a => a.NameEquals?.Name.Identifier.ValueText == Constants.AllowPrivatePropertyName)?.Expression.GetLocation() ?? location;
 1362|                 }
 1363| 
 1364|                 this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.MessagePackObjectAllowPrivateRequired, location));
 1365|             }
 1366|         }
 1367| 
 1368|         // Do not source generate the formatter for this type if the attribute opted out.
 1369|         if (suppressSourceGeneration is true)
 1370|         {
 1371|             // Skip any source generation
 1372|             return null;
 1373|         }
 1374| 
 1375|         // If any property had a private setter and does not appear in the deserializing constructor signature,
 1376|         // we'll need a nested formatter.
 1377|         foreach (IPropertySymbol property in nestedFormatterRequiredIfPropertyIsNotSetByDeserializingCtor)
 1378|         {
 1379|             nestedFormatterRequired |= !constructorParameters.Any(m => m.Name == property.Name);
 1380|         }
 1381| 
 1382|         if (nestedFormatterRequired && nonPublicMembersAreSerialized)
 1383|         {
 1384|             // If the data type or any nesting types are not declared with partial, we cannot emit the formatter as a nested type within the data type
 1385|             // as required in order to access the private members.
 1386|             bool anyNonPartialTypesFound = false;
 1387|             BaseTypeDeclarationSyntax[] nonPartialTypes = FindNonPartialTypes(formattedType).ToArray();
 1388|             if (nonPartialTypes.Length > 0)
 1389|             {
 1390|                 BaseTypeDeclarationSyntax? targetType = formattedType.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax() as BaseTypeDeclarationSyntax;
 1391|                 Location? primaryLocation = targetType?.Identifier.GetLocation();
 1392|                 Location[]? addlLocations = nonPartialTypes.Where(t => t != targetType).Select(t => t.Identifier.GetLocation()).ToArray();
 1393|                 this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.PartialTypeRequired, primaryLocation, (IEnumerable<Location>?)addlLocations));
 1394|                 anyNonPartialTypesFound = true;
 1395|             }
 1396| 
 1397|             if (anyNonPartialTypesFound)
 1398|             {
 1399|                 return null;
 1400|             }
 1401|         }
 1402| 
 1403|         INamedTypeSymbol? formattedTypeDefinition = formattedType.IsGenericType ? formattedType.ConstructUnboundGenericType() : null;
 1404|         ObjectSerializationInfo info = ObjectSerializationInfo.Create(
 1405|             formattedType,
 1406|             isClass: isClass,
 1407|             nestedFormatterRequired: nestedFormatterRequired,
 1408|             genericTypeParameters: formattedType.IsGenericType ? formattedType.TypeParameters.Select(t => GenericTypeParameterInfo.Create(t)).ToArray() : Array.Empty<GenericTypeParameterInfo>(),
 1409|             constructorParameters: constructorParameters.ToArray(),
 1410|             isIntKey: isIntKey,
 1411|             members: isIntKey ? intMembers.Values.Select(v => v.Info).ToArray() : stringMembers.Values.Select(v => v.Info).ToArray(),
 1412|             hasIMessagePackSerializationCallbackReceiver: hasSerializationConstructor,
 1413|             needsCastOnAfter: needsCastOnAfter,
 1414|             needsCastOnBefore: needsCastOnBefore,
 1415|             this.options.Generator.Resolver);
 1416| 
 1417|         return info;
 1418|     }
 1419| 
 1420|     private static IEnumerable<BaseTypeDeclarationSyntax> FindNonPartialTypes(ITypeSymbol target)
 1421|     {
 1422|         return from x in CodeAnalysisUtilities.EnumerateTypeAndContainingTypes(target)
 1423|                where x.FirstDeclaration?.Modifiers.Any(SyntaxKind.PartialKeyword) is false
 1424|                select x.FirstDeclaration;
 1425|     }
 1426| 
 1427|     private static Location? GetIdentifierLocation(INamedTypeSymbol type) => ((BaseTypeDeclarationSyntax?)type.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax())?.Identifier.GetLocation();
 1428| 
 1429|     private static Location? GetLocation(IParameterSymbol parameter) => parameter.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation();
 1430| 
 1431|     private static Location? GetParameterListLocation(IMethodSymbol? method) => ((BaseMethodDeclarationSyntax?)method?.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax())?.ParameterList.GetLocation();
 1432| 
 1433|     private static string GetGenericFormatterClassName(INamedTypeSymbol type)
 1434|     {
 1435|         return type.Name;
 1436|     }
 1437| 
 1438|     private static string GetMinimallyQualifiedClassName(INamedTypeSymbol type)
 1439|     {
 1440|         var name = type.ContainingType is object ? GetMinimallyQualifiedClassName(type.ContainingType) + "_" : string.Empty;
 1441|         name += type.ToDisplayString(SymbolDisplayFormat.MinimallyQualifiedFormat);
 1442|         name = name.Replace('.', '_');
 1443|         name = name.Replace('<', '_');
 1444|         name = name.Replace('>', '_');
 1445|         name = Regex.Replace(name, @"\[([,])*\]", match => $"Array{match.Length - 1}");
 1446|         name = name.Replace("?", string.Empty);
 1447|         return name;
 1448|     }
 1449| 
 1450|     private static bool TryGetNextConstructor(IEnumerator<IMethodSymbol>? ctorEnumerator, ref IMethodSymbol? ctor)
 1451|     {
 1452|         if (ctorEnumerator == null || ctor != null)
 1453|         {
 1454|             return false;
 1455|         }
 1456| 
 1457|         if (ctorEnumerator.MoveNext())
 1458|         {
 1459|             ctor = ctorEnumerator.Current;
 1460|             return true;
 1461|         }
 1462|         else
 1463|         {
 1464|             ctor = null;
 1465|             return false;
 1466|         }
 1467|     }
 1468| 
 1469|     private static bool IsPartialTypeRequired(Accessibility accessibility) => accessibility is not (Accessibility.Public or Accessibility.Internal or Accessibility.ProtectedOrInternal);
 1470| 
 1471|     private static bool IsAllowAccessibility(ITypeSymbol symbol)
 1472|     {
 1473|         do
 1474|         {
 1475|             if (symbol.DeclaredAccessibility is not (Accessibility.Public or Accessibility.Internal))
 1476|             {
 1477|                 return false;
 1478|             }
 1479| 
 1480|             symbol = symbol.ContainingType;
 1481|         }
 1482|         while (symbol is not null);
 1483| 
 1484|         return true;
 1485|     }
 1486| 
 1487|     private static bool IsOpenGenericTypeRecursively(INamedTypeSymbol type)
 1488|     {
 1489|         return type.IsGenericType && type.TypeArguments.Any(x => x is ITypeParameterSymbol || (x is INamedTypeSymbol symbol && IsOpenGenericTypeRecursively(symbol)));
 1490|     }
 1491| }
```

### tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs at head (60d651e8), full file
```
    1| ﻿// Copyright (c) All contributors. All rights reserved.
    2| // Licensed under the MIT license. See LICENSE file in the project root for full license information.
    3| 
    4| using Microsoft.CodeAnalysis;
    5| using Microsoft.CodeAnalysis.CSharp;
    6| using VerifyCS = CSharpSourceGeneratorVerifier<MessagePack.SourceGenerator.MessagePackGenerator>;
    7| 
    8| public class GenericsFormatterTests
    9| {
   10|     private readonly ITestOutputHelper testOutputHelper;
   11| 
   12|     public GenericsFormatterTests(ITestOutputHelper testOutputHelper)
   13|     {
   14|         this.testOutputHelper = testOutputHelper;
   15|     }
   16| 
   17|     [Fact]
   18|     public async Task NullableFormatter()
   19|     {
   20|         string testSource = """
   21| using System;
   22| using System.Collections.Generic;
   23| using MessagePack;
   24| 
   25| namespace TempProject
   26| {
   27|     [MessagePackObject]
   28|     public class MyObject
   29|     {
   30|         [Key(0)]
   31|         public int? ValueNullableInt { get; set; }
   32|         [Key(1)]
   33|         public MyEnum? ValueNullableEnum { get; set; }
   34|         [Key(2)]
   35|         public ValueTuple<int, long>? ValueNullableStruct { get; set; }
   36|     }
   37| 
   38|     public enum MyEnum
   39|     {
   40|         A, B, C
   41|     }
   42| }
   43| """;
   44|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
   45|     }
   46| 
   47|     [Fact]
   48|     public async Task WellKnownGenericsFormatter()
   49|     {
   50|         string testSource = """
   51| using System;
   52| using System.Collections.Generic;
   53| using MessagePack;
   54| 
   55| namespace TempProject
   56| {
   57|     [MessagePackObject]
   58|     public class MyObject
   59|     {
   60|         [Key(0)]
   61|         public List<int> ValueList { get; set; }
   62|         [Key(1)]
   63|         public List<List<int>> ValueListNested { get; set; }
   64|         [Key(2)]
   65|         public ValueTuple<int, string, long> ValueValueTuple { get; set; }
   66|     }
   67| }
   68| """;
   69|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
   70|     }
   71| 
   72|     [Fact]
   73|     public async Task GenericsUnionFormatter()
   74|     {
   75|         string testSource = """
   76| using System;
   77| using System.Collections.Generic;
   78| using MessagePack;
   79| 
   80| namespace TempProject
   81| {
   82|     [MessagePackObject]
   83|     [Union(0, typeof(Wrapper<string>))]
   84|     [Union(1, typeof(Wrapper<int[]>))]
   85|     [Union(2, typeof(Wrapper<IEnumerable<Guid>>))]
   86|     public class Wrapper<T>
   87|     {
   88|         [Key(0)]
   89|         public T Content { get; set; }
   90|     }
   91| }
   92| """;
   93|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
   94|     }
   95| 
   96|     [Fact]
   97|     public async Task GenericsUnionFormatter_Nested()
   98|     {
   99|         string testSource = """
  100| using System;
  101| using System.Collections.Generic;
  102| using MessagePack;
  103| 
  104| namespace TempProject
  105| {
  106|     [MessagePackObject]
  107|     [Union(0, typeof(Wrapper<string>))]
  108|     [Union(1, typeof(Wrapper<int[]>))]
  109|     [Union(2, typeof(Wrapper<IEnumerable<Guid>>))]
  110|     public class Wrapper<T>
  111|     {
  112|         [Key(0)]
  113|         public List<T> Content1 { get; set; }
  114|         [Key(1)]
  115|         public MyGenericObject<T> Content2 { get; set; }
  116|     }
  117| 
  118|     [MessagePackObject]
  119|     public class MyGenericObject<T>
  120|     {
  121|         [Key(0)]
  122|         public MyInnerGenericObject<T> Content { get; set; }
  123|     }
  124| 
  125|     [MessagePackObject]
  126|     public class MyInnerGenericObject<T>
  127|     {
  128|     }
  129| }
  130| """;
  131|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  132|     }
  133| 
  134|     [Fact]
  135|     public async Task NestedGenericTypes()
  136|     {
  137|         string testSource = """
  138| using System;
  139| using System.Collections.Generic;
  140| using MessagePack;
  141| 
  142| namespace TempProject
  143| {
  144|     [MessagePackObject]
  145|     public class MyObject : Wrapper<MyObject2>
  146|     {
  147|     }
  148| 
  149|     [MessagePackObject]
  150|     public class MyObject2
  151|     {}
  152| 
  153|     [MessagePackObject]
  154|     public class Wrapper<T>
  155|     {
  156|         [Key(0)]
  157|         public List<T> Content1 { get; set; }
  158|         [Key(1)]
  159|         public MyGenericObject<T> Content2 { get; set; }
  160|     }
  161| 
  162|     [MessagePackObject]
  163|     public class MyGenericObject<T>
  164|     {
  165|         [Key(0)]
  166|         public MyInnerGenericObject<T> Content { get; set; }
  167|         [Key(1)]
  168|         public T[] Content2 { get; set; }
  169|     }
  170| 
  171|     [MessagePackObject]
  172|     public class MyInnerGenericObject<T>
  173|     {
  174|     }
  175| }
  176| """;
  177|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  178|     }
  179| 
  180|     [Fact]
  181|     public async Task GenericsOfTFormatter_WithKnownTypes()
  182|     {
  183|         string testSource = """
  184| using System;
  185| using System.Collections.Generic;
  186| using MessagePack;
  187| 
  188| namespace TempProject
  189| {
  190|     [MessagePackObject]
  191|     public class MyObject : MyGenericObject<MyObject2>
  192|     {
  193|     }
  194| 
  195|     [MessagePackObject]
  196|     public class MyObject2
  197|     { }
  198| 
  199|     [MessagePackObject]
  200|     public class MyGenericObject<T>
  201|     {
  202|         [Key(0)]
  203|         public List<T> Content1 { get; set; }
  204|         [Key(1)]
  205|         public T[] Content2 { get; set; }
  206|     }
  207| }
  208| """;
  209|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  210|     }
  211| 
  212|     [Fact]
  213|     public async Task GenericsOfTFormatter()
  214|     {
  215|         string testSource = """
  216| using System;
  217| using System.Collections.Generic;
  218| using MessagePack;
  219| 
  220| namespace TempProject
  221| {
  222|     [MessagePackObject]
  223|     public class MyGenericObject<T>
  224|     {
  225|         [Key(0)]
  226|         public T Content { get; set; }
  227|     }
  228| 
  229|     [MessagePackObject]
  230|     public class MyObject
  231|     {
  232|         [Key(0)]
  233|         public MyGenericObject<int> Value { get; set; }
  234|     }
  235| 
  236|     [MessagePackObject]
  237|     public class MyObjectNested
  238|     {
  239|         [Key(0)]
  240|         public MyGenericObject<MyGenericObject<int>> Value { get; set; }
  241|     }
  242| }
  243| """;
  244|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  245|     }
  246| 
  247|     [Fact]
  248|     public async Task GenericsOfT1T2Formatter()
  249|     {
  250|         string testSource = """
  251| using System;
  252| using System.Collections.Generic;
  253| using MessagePack;
  254| 
  255| namespace TempProject
  256| {
  257|     [MessagePackObject]
  258|     public class MyGenericObject<T1, T2>
  259|     {
  260|         [Key(0)]
  261|         public T1 ValueA { get; set; }
  262|         [Key(1)]
  263|         public T2 ValueB { get; set; }
  264|     }
  265| 
  266|     [MessagePackObject]
  267|     public class MyObject
  268|     {
  269|         [Key(0)]
  270|         public MyGenericObject<int, string> Value { get; set; }
  271|     }
  272| 
  273|     [MessagePackObject]
  274|     public class MyObjectNested
  275|     {
  276|         [Key(0)]
  277|         public MyGenericObject<MyGenericObject<int, string>, MyGenericObject<int, string>> Value { get; set; }
  278|     }
  279| }
  280| """;
  281|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  282|     }
  283| 
  284|     [Fact]
  285|     public async Task GenericsOfTFormatter_FormatterOnly()
  286|     {
  287|         string testSource = """
  288| using System;
  289| using System.Collections.Generic;
  290| using MessagePack;
  291| 
  292| namespace TempProject
  293| {
  294|     // This type is not used by the project.
  295|     // It may be referenced by other projects.
  296|     [MessagePackObject]
  297|     public class MyGenericObject<T>
  298|     {
  299|         [Key(0)]
  300|         public T Content { get; set; }
  301|     }
  302| }
  303| """;
  304|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  305|     }
  306| 
  307|     [Fact]
  308|     public async Task Generics_Constraints_Type()
  309|     {
  310|         string testSource = """
  311| using System;
  312| using System.Collections.Generic;
  313| using MessagePack;
  314| 
  315| namespace TempProject
  316| {
  317|     [MessagePackObject]
  318|     public class MyGenericObject<T>
  319|         where T : IDisposable
  320|     {
  321|         [Key(0)]
  322|         public T Content { get; set; }
  323|     }
  324| }
  325| """;
  326|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  327|     }
  328| 
  329|     [Fact]
  330|     public async Task Generics_Constraints_NullableReferenceType()
  331|     {
  332|         string testSource = """
  333| #nullable enable
  334| 
  335| using System;
  336| using System.Collections.Generic;
  337| using MessagePack;
  338| 
  339| namespace TempProject
  340| {
  341|     [MessagePackObject]
  342|     public class MyGenericObject<T1, T2, T3, T4>
  343|         where T1 : MyClass?
  344|         where T2 : MyClass
  345|         where T3 : MyGenericClass<MyGenericClass<MyClass?>?>?
  346|         where T4 : MyClass, IMyInterface?
  347|     {
  348|         [Key(0)]
  349|         public T1? Content { get; set; }
  350|     }
  351| 
  352|     public class MyClass {}
  353|     public class MyGenericClass<T> {}
  354|     public interface IMyInterface {}
  355| }
  356| """;
  357|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, languageVersion: LanguageVersion.CSharp9);
  358|     }
  359| 
  360|     [Fact]
  361|     public async Task Generics_Constraints_Struct()
  362|     {
  363|         string testSource = """
  364| using System;
  365| using System.Collections.Generic;
  366| using MessagePack;
  367| 
  368| namespace TempProject
  369| {
  370|     [MessagePackObject]
  371|     public class MyGenericObject<T>
  372|         where T : struct
  373|     {
  374|         [Key(0)]
  375|         public T Content { get; set; }
  376|     }
  377| }
  378| """;
  379|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  380|     }
  381| 
  382|     [Fact]
  383|     public async Task Generics_Constraints_Multiple()
  384|     {
  385|         string testSource = """
  386| using System;
  387| using System.Collections.Generic;
  388| using MessagePack;
  389| 
  390| namespace TempProject
  391| {
  392|     [MessagePackObject]
  393|     public class MyGenericObject<T1, T2, T3, T4>
  394|         where T1 : struct
  395|         where T2 : IDisposable, new()
  396|         where T3 : notnull
  397|         where T4 : unmanaged
  398|     {
  399|         [Key(0)]
  400|         public T1 Content1 { get; set; }
  401|         [Key(1)]
  402|         public T2 Content2 { get; set; }
  403|         [Key(2)]
  404|         public T3 Content3 { get; set; }
  405|         [Key(3)]
  406|         public T4 Content4 { get; set; }
  407|     }
  408| }
  409| """;
  410|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, languageVersion: LanguageVersion.CSharp8);
  411|     }
  412| 
  413|     [Fact]
  414|     public async Task Generics_Constraints_ReferenceType_Nullable()
  415|     {
  416|         string testSource = """
  417| #nullable enable
  418| 
  419| using System;
  420| using System.Collections.Generic;
  421| using MessagePack;
  422| 
  423| namespace TempProject
  424| {
  425|     [MessagePackObject]
  426|     public class MyGenericObject<T1, T2>
  427|         where T1 : class?
  428|         where T2 : class
  429|     {
  430|         [Key(0)]
  431|         public T1? Content1 { get; set; }
  432|         [Key(1)]
  433|         public T2? Content2 { get; set; }
  434|     }
  435| }
  436| """;
  437|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, languageVersion: LanguageVersion.CSharp9);
  438|     }
  439| 
  440|     [Fact]
  441|     public async Task Generics_Defined_In_ReferencedProject()
  442|     {
  443|         string defineSource = """
  444| using System;
  445| using System.Collections.Generic;
  446| using MessagePack;
  447| 
  448| namespace TempProject
  449| {
  450|     [MessagePackObject]
  451|     public class MyGenericObject<T>
  452|     {
  453|         [Key(0)]
  454|         public T Content { get; set; }
  455|     }
  456| 
  457|     [GeneratedMessagePackResolver]
  458|     partial class MyResolver { }
  459| }
  460| """;
  461| 
  462|         string usageSource = """
  463| using System;
  464| using System.Collections.Generic;
  465| using MessagePack;
  466| 
  467| namespace TempProject
  468| {
  469|     [MessagePackObject]
  470|     public class MyObject
  471|     {
  472|         [Key(0)]
  473|         public MyGenericObject<int> Value { get; set; }
  474|     }
  475| 
  476|     [MessagePackObject]
  477|     public class MyObjectNested
  478|     {
  479|         [Key(0)]
  480|         public MyGenericObject<MyGenericObject<int>> Value { get; set; }
  481|     }
  482| }
  483| """;
  484|         await new VerifyCS.Test
  485|         {
  486|             TestState =
  487|             {
  488|                 Sources = { usageSource },
  489|                 AdditionalProjects =
  490|                 {
  491|                     ["DefiningProject"] = { Sources = { defineSource } },
  492|                 },
  493|                 AdditionalProjectReferences = { "DefiningProject" },
  494|             },
  495|         }.RunAsync();
  496|     }
  497| 
  498|     /// <summary>
  499|     /// Regression test for a closed generic value type defined in a referenced assembly,
  500|     /// whose compiler-generated backing fields have no syntax (https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2283).
  501|     /// </summary>
  502|     [Fact]
  503|     public async Task Generics_ValueType_Defined_In_ReferencedProject()
  504|     {
  505|         string defineSource = """
  506| using MessagePack;
  507| 
  508| namespace TempProject
  509| {
  510|     [MessagePackObject]
  511|     public struct MyGenericStruct<T>
  512|     {
  513|         [Key(0)]
  514|         public string Key { get; set; }
  515|     }
  516| }
  517| """;
  518| 
  519|         string usageSource = """
  520| using MessagePack;
  521| 
  522| namespace TempProject
  523| {
  524|     [MessagePackObject]
  525|     public class MyObject
  526|     {
  527|         [Key(0)]
  528|         public MyGenericStruct<int> Value { get; set; }
  529|     }
  530| }
  531| """;
  532|         // Reference the defining assembly as metadata (not as a project) so its symbols have no syntax.
  533|         CSharpCompilation definingCompilation = CSharpCompilation.Create(
  534|             "DefiningAssembly",
  535|             [CSharpSyntaxTree.ParseText(defineSource)],
  536|             (await ReferencesHelper.DefaultTargetFrameworkReferences.ResolveAsync(LanguageNames.CSharp, default)).AddRange(ReferencesHelper.GetReferences(ReferencesSet.MessagePack)),
  537|             new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary));
  538|         using MemoryStream definingImage = new();
  539|         Microsoft.CodeAnalysis.Emit.EmitResult emitResult = definingCompilation.Emit(definingImage);
  540|         Assert.True(emitResult.Success, string.Join(Environment.NewLine, emitResult.Diagnostics));
  541| 
  542|         await new VerifyCS.Test
  543|         {
  544|             TestState =
  545|             {
  546|                 Sources = { usageSource },
  547|                 AdditionalReferences = { MetadataReference.CreateFromImage(definingImage.ToArray()) },
  548|             },
  549|         }.RunAsync();
  550|     }
  551| 
  552|     /// <summary>
  553|     /// Asserts that the generator can handle directly recursive generic constraints.
  554|     /// </summary>
  555|     [Fact]
  556|     public async Task RecursiveGenerics_Direct()
  557|     {
  558|         string testSource = /* lang=c#-test */ """
  559|             using System;
  560|             using MessagePack;
  561| 
  562|             [MessagePackObject]
  563|             public class A<T>
  564|                 where T : IEquatable<A<T>>
  565|             {
  566|             }
  567|             """;
  568| 
  569|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
  570|     }
  571| }
```

### src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base (32258fdb), around the changed lines
```
  ... lines 1-951 not shown ...
  952|                                             item.ContainingType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat),
  953|                                             item.Name);
  954|                                     if (reportedDiagnostics.Add(diagnostic))
  955|                                     {
  956|                                         if (nonPublicMembersAreSerialized || (item.DeclaredAccessibility & Accessibility.Public) == Accessibility.Public)
  957|                                         {
  958|                                             this.reportDiagnostic?.Invoke(diagnostic);
  959|                                         }
  960|                                         else
  961|                                         {
  962|                                             deferredDiagnosticsForNonPublicMembers.Add(diagnostic);
  963|                                         }
  964|                                     }
  965|                                 }
  966|                             }
  967|                         }
  968|                     }
  969|                 }
  970|                 else
  971|                 {
  972|                     // If this attributed member is non-public, then all non-public members should be attributed.
  973|                     nonPublicMembersAreSerialized |= (item.DeclaredAccessibility & Accessibility.Public) != Accessibility.Public;
  974| 
  975|                     nestedFormatterRequired |= item.GetMethod is not null && IsPartialTypeRequired(item.GetMethod.DeclaredAccessibility);
  976|                     if (item.SetMethod is not null && IsPartialTypeRequired(item.SetMethod.DeclaredAccessibility))
  977|                     {
  978|                         nestedFormatterRequiredIfPropertyIsNotSetByDeserializingCtor.Add(item);
  979|                     }
  980| 
  981|                     var intKey = key is { Value: int intKeyValue } ? intKeyValue : default(int?);
  982|                     var stringKey = key is { Value: string stringKeyValue } ? stringKeyValue : default;
  983|                     if (intKey == null && stringKey == null)
  984|                     {
  985|                         this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.BothStringAndIntKeyAreNull, ((PropertyDeclarationSyntax)item.DeclaringSyntaxReferences[0].GetSyntax()).Identifier.GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name));
  986|                     }
  987| 
  988|                     // A property with an init accessor and an initializer has a default that will be discarded by the deserializer.
  989|                     if (suppressSourceGeneration is not true && isInitOnly)
  990|                     {
  991|                         EqualsValueClauseSyntax? initializer = item.DeclaringSyntaxReferences.Select(s => (s.GetSyntax(this.cancellationToken) as PropertyDeclarationSyntax)?.Initializer).FirstOrDefault(i => i is not null);
  992|                         if (initializer is not null)
  993|                         {
  994|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AOTInitProperty, initializer.GetLocation()));
  995|                         }
  996|                     }
  997| 
  998|                     if (searchFirst)
  999|                     {
 1000|                         searchFirst = false;
 1001|                         isIntKey = intKey != null;
 1002|                     }
 1003|                     else
 1004|                     {
 1005|                         if ((isIntKey && intKey == null) || (!isIntKey && stringKey == null))
 1006|                         {
 1007|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.DoNotMixStringAndIntKeys, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
 1008|                         }
 1009|                     }
 1010| 
 1011|                     if (isIntKey)
 1012|                     {
 1013|                         if (intMembers.ContainsKey(intKey!.Value))
 1014|                         {
 1015|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.KeysMustBeUnique, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
 1016|                         }
 1017| 
 1018|                         var member = new MemberSerializationInfo(true, isWritable, isReadable, isInitOnly, item.IsRequired, intKey!.Value, item.Name, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
  ... lines 1019-1043 not shown ...
 1044|                     }
 1045|                 }
 1046|             }
 1047| 
 1048|             foreach (IFieldSymbol item in formattedType.GetAllMembers().OfType<IFieldSymbol>())
 1049|             {
 1050|                 if (item.IsImplicitlyDeclared || item.IsStatic)
 1051|                 {
 1052|                     continue;
 1053|                 }
 1054| 
 1055|                 if (item.GetAttributes().Any(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.IgnoreAttribute)))
 1056|                 {
 1057|                     nonPublicMembersAreSerialized |= (item.DeclaredAccessibility & Accessibility.Public) != Accessibility.Public;
 1058|                     continue;
 1059|                 }
 1060| 
 1061|                 FormatterDescriptor? specialFormatter = GetSpecialFormatter(item);
 1062|                 TypedConstant? key = item.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.KeyAttribute))?.ConstructorArguments[0];
 1063|                 if (key is null)
 1064|                 {
 1065|                     if (contractAttr is not null)
 1066|                     {
 1067|                         // If the member is attributed with a type derived from KeyAttribute, that's incompatible with source generation
 1068|                         // since we cannot know what the key is using only C# syntax and the semantic model.
 1069|                         SyntaxReference? derivedKeyAttribute = item.GetAttributes().FirstOrDefault(att => att.AttributeClass.IsApproximatelyEqualOrDerivedFrom(this.typeReferences.KeyAttribute) == RoslynAnalyzerExtensions.EqualityMatch.LeftDerivesFromRight)?.ApplicationSyntaxReference;
 1070| 
 1071|                         if (derivedKeyAttribute is null || suppressSourceGeneration is not true)
 1072|                         {
 1073|                             if (SymbolEqualityComparer.Default.Equals(item.ContainingType, formattedType))
 1074|                             {
 1075|                                 Diagnostic diagnostic = derivedKeyAttribute is not null && suppressSourceGeneration is not true
 1076|                                     ? Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AOTDerivedKeyAttribute, derivedKeyAttribute.GetSyntax(this.cancellationToken).GetLocation())
 1077|                                     : Diagnostic.Create(MsgPack00xMessagePackAnalyzer.MemberNeedsKey, item.DeclaringSyntaxReferences[0].GetSyntax().GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name);
 1078|                                 if (nonPublicMembersAreSerialized || (item.DeclaredAccessibility & Accessibility.Public) == Accessibility.Public)
 1079|                                 {
 1080|                                     this.reportDiagnostic?.Invoke(diagnostic);
 1081|                                 }
 1082|                                 else
 1083|                                 {
 1084|                                     deferredDiagnosticsForNonPublicMembers.Add(diagnostic);
 1085|                                 }
 1086|                             }
 1087|                             else if (formattedType.BaseType is not null)
 1088|                             {
 1089|                                 // The member was inherited, so we raise a special error at the location of the base type reference.
 1090|                                 BaseTypeSyntax? baseSyntax = formattedType.DeclaringSyntaxReferences.SelectMany(sr => (IEnumerable<BaseTypeSyntax>?)((BaseTypeDeclarationSyntax)sr.GetSyntax()).BaseList?.Types ?? Array.Empty<BaseTypeSyntax>())
 1091|                                     .FirstOrDefault(bt => SymbolEqualityComparer.Default.Equals(this.compilation.GetSemanticModel(bt.SyntaxTree).GetTypeInfo(bt.Type).Type, item.ContainingType));
 1092|                                 if (baseSyntax is not null)
 1093|                                 {
 1094|                                     Diagnostic diagnostic = derivedKeyAttribute is not null && suppressSourceGeneration is not true
 1095|                                         ? Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AOTDerivedKeyAttribute, baseSyntax.GetLocation())
 1096|                                         : Diagnostic.Create(
 1097|                                             MsgPack00xMessagePackAnalyzer.BaseTypeContainsUnattributedPublicMembers,
 1098|                                             baseSyntax.GetLocation(),
 1099|                                             item.ContainingType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat),
 1100|                                             item.Name);
 1101|                                     if (reportedDiagnostics.Add(diagnostic))
 1102|                                     {
 1103|                                         if (nonPublicMembersAreSerialized || (item.DeclaredAccessibility & Accessibility.Public) == Accessibility.Public)
 1104|                                         {
 1105|                                             this.reportDiagnostic?.Invoke(diagnostic);
 1106|                                         }
 1107|                                         else
 1108|                                         {
 1109|                                             deferredDiagnosticsForNonPublicMembers.Add(diagnostic);
 1110|                                         }
  ... lines 1111-1491 not shown ...
```

## What you did NOT get (refuse anything that depends on it)
- the contents and diffs of 3 generated files (listed above by name only)
- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)

Return only the JSON object described in the brief.