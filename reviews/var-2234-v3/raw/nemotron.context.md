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
# Change var-2234-v3: branch cs-var/2234-v3, base 32258fdbee4bcd653c79f51b4376b5103c6f4d27, head 4f1f99880396814d809c5ef373a9632e27ac01ee
Commit message: Add regression test: analyzer reports diagnostics for SuppressSourceGeneration types (#2234)

The analyzer must keep reporting contract diagnostics (MsgPack003/004, ...)
for [MessagePackObject(SuppressSourceGeneration = true)] types. Document
that the opt-out early return in TypeCollector.GetObjectInfo must remain
after the analysis, and lock the behavior in with a test.
Upstream issue: https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2234

## Requirement set (requirements/var-2234-v3.yaml)
```yaml
# REUSED from requirements/2234.yaml (same clauses, same ids, unchanged text) for another fix of the same upstream issue
# #2234, so every fix of it is judged against the same clauses (docs/MEASUREMENT.md, "Same issue, several fixes").
# Still a placeholder derived from the issue, not a Tieto set.
change: "var-2234-v3"
branch: cs-var/2234-v3
reused_from: requirements/2234.yaml
source: https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2234
official: false
requirements:
  - id: REQ-2234-F1
    type: functional
    # tests: the tests that exercise this clause; held_before is judged on their fail-without-fix outcomes.
    # The four *WithoutAnalyzerFailure tests belong to N1 (no crash): without the fix they still report the
    # contract diagnostic (MsgPack005) and fail only on the extra AD0001 analyzer crash (evidence/2234/facts.json).
    tests:
      - SuppressSourceGenerationAnalyzerTests.MemberWithoutKeyIsReported
      - SuppressSourceGenerationAnalyzerTests.MemberTypeMustBeMessagePackObjectIsReported
      - SuppressSourceGenerationAnalyzerTests.AllowPrivateRequiredIsReported
    text: "The analyzer must report contract diagnostics (e.g. missing [Key], duplicate keys, mixed key kinds) for [MessagePackObject(SuppressSourceGeneration = true)] types, as it did in version 3.1.0."
  - id: REQ-2234-F2
    type: functional
    tests: [SuppressSourceGenerationAnalyzerTests.SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed]
    text: "Diagnostics that only apply when a formatter is generated (partial-class requirement, AOT-only checks) must not be reported for types with SuppressSourceGeneration = true."
  - id: REQ-2234-N1
    type: non-functional
    checks: [tests.full_suite]
    text: "The analyzer and generator must not crash on invalid contracts (e.g. duplicate keys) in such types."
  - id: REQ-2234-N2
    type: non-functional
    checks: [tests.fail_without_fix]
    text: "The fix is covered by automated tests that fail without it; no regressions in the existing test suite."
```

## facts.json (deterministic checks; cite their ids and test names)
```json
{
 "change": "var-2234-v3",
 "branch": "cs-var/2234-v3",
 "base": "32258fdb",
 "head": "4f1f9988",
 "base_full": "32258fdbee4bcd653c79f51b4376b5103c6f4d27",
 "head_full": "4f1f99880396814d809c5ef373a9632e27ac01ee",
 "commit_message": "Add regression test: analyzer reports diagnostics for SuppressSourceGeneration types (#2234)\n\nThe analyzer must keep reporting contract diagnostics (MsgPack003/004, ...)\nfor [MessagePackObject(SuppressSourceGeneration = true)] types. Document\nthat the opt-out early return in TypeCollector.GetObjectInfo must remain\nafter the analysis, and lock the behavior in with a test.",
 "author": "Zawaer",
 "agent_written": true,
 "diff": {
  "files": 2,
  "insertions": 74,
  "deletions": 0,
  "by_kind": {
   "source": 1,
   "test": 1
  },
  "by_file": [
   {
    "path": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
    "ins": 2,
    "del": 0,
    "kind": "source"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs",
    "ins": 72,
    "del": 0,
    "kind": "test"
   }
  ]
 },
 "new_tests_in_diff": [
  "MsgPack00xAnalyzerTests.SourceGenerationDisabled_AnalyzerStillReportsDiagnostics"
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
   "summary": "0 errors, 1 unique warnings",
   "log": "evidence/var-2234-v3/logs/build.log",
   "duration_s": 6.0
  },
  {
   "id": "tests.targeted",
   "tool": "dotnet test",
   "tool_version": "8.0.402",
   "status": "pass",
   "summary": "31 passed, 0 failed, 0 skipped (1 new tests in run)",
   "tests": [
    {
     "name": "MsgPack00xAnalyzerTests.AbstractFormatterDoesNotAttractAttention",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToField_WithComment",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToGenericType",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToTypeForRecord1",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToTypeForRecord2",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToTypeForRecordPrimaryConstructor",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToType_Fields",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToType_Generic",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToType_Nullable",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToType_Properties",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributesToMembers",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributesToMembersOfRecord",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributesToMembersOfRecordStruct",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributesToMembersOfRecordStructWithPrimaryCtor",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributesToMembersOfRecordWithPrimaryCtor",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributesToMembers_AllowPrivateAttribute",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributesToMembers_MixedVisibility",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributesToMembers_PublicOnly",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddIgnoreAttributesToMembers",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.CodeFixAppliesAcrossFiles",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.DerivedAttributes",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.DerivedAttributes_SourceGenerationDisabled",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.DoNotAddAttributesToClassWithPrimaryCtor",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.InitPropertyInitializer",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.InvalidMessageFormatterType",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.MessageFormatterAttribute",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.NameCollisionsInForceMapMode",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.NoMessagePackReference",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.NullStringKey",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.PrivateMembersInBaseClassNeedNoAttribution",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.SourceGenerationDisabled_AnalyzerStillReportsDiagnostics",
     "outcome": "passed",
     "new": true
    }
   ],
   "log": "evidence/var-2234-v3/logs/tests_targeted.1.log",
   "duration_s": 3.0,
   "filter": [
    "FullyQualifiedName~MsgPack00xAnalyzerTests."
   ],
   "project": "tests/MessagePack.SourceGenerator.Tests"
  },
  {
   "id": "tests.fail_without_fix",
   "tool": "dotnet test (source reverted, tests kept)",
   "tool_version": "8.0.402",
   "status": "fail",
   "summary": "new tests pass on base source: 0/1 failed -> tests do NOT demonstrate the change",
   "tests": [
    {
     "name": "MsgPack00xAnalyzerTests.AbstractFormatterDoesNotAttractAttention",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToField_WithComment",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToGenericType",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToTypeForRecord1",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToTypeForRecord2",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToTypeForRecordPrimaryConstructor",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToType_Fields",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToType_Generic",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToType_Nullable",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributeToType_Properties",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributesToMembers",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributesToMembersOfRecord",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributesToMembersOfRecordStruct",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributesToMembersOfRecordStructWithPrimaryCtor",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributesToMembersOfRecordWithPrimaryCtor",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributesToMembers_AllowPrivateAttribute",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributesToMembers_MixedVisibility",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddAttributesToMembers_PublicOnly",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.AddIgnoreAttributesToMembers",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.CodeFixAppliesAcrossFiles",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.DerivedAttributes",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.DerivedAttributes_SourceGenerationDisabled",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.DoNotAddAttributesToClassWithPrimaryCtor",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.InitPropertyInitializer",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.InvalidMessageFormatterType",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.MessageFormatterAttribute",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.NameCollisionsInForceMapMode",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.NoMessagePackReference",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.NullStringKey",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.PrivateMembersInBaseClassNeedNoAttribution",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "MsgPack00xAnalyzerTests.SourceGenerationDisabled_AnalyzerStillReportsDiagnostics",
     "outcome": "passed",
     "new": true
    }
   ],
   "log": "evidence/var-2234-v3/logs/tests_fail_without_fix.1.log",
   "duration_s": 3.0,
   "reverted_files": [
    "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs"
   ],
   "full_suite_with_source_reverted": {
    "total": 168,
    "failed": 0,
    "failed_tests": [],
    "log": "evidence/var-2234-v3/logs/fail_without_fix.full_suite.log"
   },
   "new_failed": 0,
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
   "log": "evidence/var-2234-v3/logs/tests_full_suite.log",
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
   "status": "pass",
   "summary": "no new warnings",
   "new_warnings": [],
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
    "diff_added_lines": 74,
    "files": 2,
    "paths": 2,
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
    "diff": "git diff 32258fdb 4f1f9988 (added lines and file paths)",
    "branch": "facts.branch",
    "commit_message": "facts.commit_message",
    "pr_text": "none: the change has no pull request text"
   }
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
  "raw_runs": "evidence/var-scripts/runs.sh -> /data/work/var/out/var-2234-v3[-fwf] (not committed; logs copied to evidence/var-2234-v3/logs/)"
 }
}
```

## Files changed (2: 2 non-generated, 0 generated)
- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs (+2 -0, source)
- tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs (+72 -0, test)

## Diff (non-generated files)
```diff
diff --git a/src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs b/src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs
index e121773d..2bbc0dbf 100644
--- a/src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs
+++ b/src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs
@@ -1366,6 +1366,8 @@ public class TypeCollector
         }
 
         // Do not source generate the formatter for this type if the attribute opted out.
+        // This check must stay *after* all the analysis above, so that the analyzer keeps reporting
+        // diagnostics (e.g. missing [Key] attributes) for types that opt out of source generation (#2234).
         if (suppressSourceGeneration is true)
         {
             // Skip any source generation

diff --git a/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs b/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs
index d39d74ef..29acc6cc 100644
--- a/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs
+++ b/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs
@@ -976,6 +976,78 @@ public class Bar : Foo
         await VerifyCS.VerifyAnalyzerAsync(test);
     }
 
+    /// <summary>
+    /// Verifies that the analyzer keeps reporting contract diagnostics for types that opt out of source generation.
+    /// See https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2234.
+    /// </summary>
+    [Fact]
+    public async Task SourceGenerationDisabled_AnalyzerStillReportsDiagnostics()
+    {
+        string test = /* lang=c#-test */ """
+            using MessagePack;
+
+            [MessagePackObject(SuppressSourceGeneration = true)]
+            public class Foo
+            {
+                [Key(0)]
+                public string Member0 { get; set; }
+
+                public string {|MsgPack004:Member1|} { get; set; }
+            }
+
+            public class NotAttributed { }
+
+            [MessagePackObject(SuppressSourceGeneration = true)]
+            public class Bar
+            {
+                [Key(0)]
+                public NotAttributed {|MsgPack003:Member0|} { get; set; }
+            }
+
+            [MessagePackObject(SuppressSourceGeneration = true)]
+            public struct Baz
+            {
+                [Key(0)]
+                public int A { get; set; }
+
+                public int {|MsgPack004:B|} { get; set; }
+            }
+
+            [MessagePackObject(SuppressSourceGeneration = true)]
+            public class Generic<T>
+            {
+                [Key(0)]
+                public T A { get; set; }
+
+                public int {|MsgPack004:B|} { get; set; }
+            }
+
+            public class Outer
+            {
+                [MessagePackObject(SuppressSourceGeneration = true)]
+                public class Nested
+                {
+                    public int {|MsgPack004:B|} { get; set; }
+                }
+            }
+
+            [MessagePackObject(SuppressSourceGeneration = true)]
+            public class Derived : {|MsgPack004:Foo|}
+            {
+                [Key(5)]
+                public int C { get; set; }
+
+                public int {|MsgPack004:D|} { get; set; }
+            }
+            """;
+
+        await new VerifyCS.Test
+        {
+            TestCode = test,
+            MarkupOptions = MarkupOptions.UseFirstDescriptor,
+        }.RunAsync();
+    }
+
     [Fact]
     public async Task InitPropertyInitializer()
     {

```

## File contents (line numbers in the gutter; quote the text after '| ')

### src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at head (4f1f9988), full file
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
 1369|         // This check must stay *after* all the analysis above, so that the analyzer keeps reporting
 1370|         // diagnostics (e.g. missing [Key] attributes) for types that opt out of source generation (#2234).
 1371|         if (suppressSourceGeneration is true)
 1372|         {
 1373|             // Skip any source generation
 1374|             return null;
 1375|         }
 1376| 
 1377|         // If any property had a private setter and does not appear in the deserializing constructor signature,
 1378|         // we'll need a nested formatter.
 1379|         foreach (IPropertySymbol property in nestedFormatterRequiredIfPropertyIsNotSetByDeserializingCtor)
 1380|         {
 1381|             nestedFormatterRequired |= !constructorParameters.Any(m => m.Name == property.Name);
 1382|         }
 1383| 
 1384|         if (nestedFormatterRequired && nonPublicMembersAreSerialized)
 1385|         {
 1386|             // If the data type or any nesting types are not declared with partial, we cannot emit the formatter as a nested type within the data type
 1387|             // as required in order to access the private members.
 1388|             bool anyNonPartialTypesFound = false;
 1389|             BaseTypeDeclarationSyntax[] nonPartialTypes = FindNonPartialTypes(formattedType).ToArray();
 1390|             if (nonPartialTypes.Length > 0)
 1391|             {
 1392|                 BaseTypeDeclarationSyntax? targetType = formattedType.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax() as BaseTypeDeclarationSyntax;
 1393|                 Location? primaryLocation = targetType?.Identifier.GetLocation();
 1394|                 Location[]? addlLocations = nonPartialTypes.Where(t => t != targetType).Select(t => t.Identifier.GetLocation()).ToArray();
 1395|                 this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.PartialTypeRequired, primaryLocation, (IEnumerable<Location>?)addlLocations));
 1396|                 anyNonPartialTypesFound = true;
 1397|             }
 1398| 
 1399|             if (anyNonPartialTypesFound)
 1400|             {
 1401|                 return null;
 1402|             }
 1403|         }
 1404| 
 1405|         INamedTypeSymbol? formattedTypeDefinition = formattedType.IsGenericType ? formattedType.ConstructUnboundGenericType() : null;
 1406|         ObjectSerializationInfo info = ObjectSerializationInfo.Create(
 1407|             formattedType,
 1408|             isClass: isClass,
 1409|             nestedFormatterRequired: nestedFormatterRequired,
 1410|             genericTypeParameters: formattedType.IsGenericType ? formattedType.TypeParameters.Select(t => GenericTypeParameterInfo.Create(t)).ToArray() : Array.Empty<GenericTypeParameterInfo>(),
 1411|             constructorParameters: constructorParameters.ToArray(),
 1412|             isIntKey: isIntKey,
 1413|             members: isIntKey ? intMembers.Values.Select(v => v.Info).ToArray() : stringMembers.Values.Select(v => v.Info).ToArray(),
 1414|             hasIMessagePackSerializationCallbackReceiver: hasSerializationConstructor,
 1415|             needsCastOnAfter: needsCastOnAfter,
 1416|             needsCastOnBefore: needsCastOnBefore,
 1417|             this.options.Generator.Resolver);
 1418| 
 1419|         return info;
 1420|     }
 1421| 
 1422|     private static IEnumerable<BaseTypeDeclarationSyntax> FindNonPartialTypes(ITypeSymbol target)
 1423|     {
 1424|         return from x in CodeAnalysisUtilities.EnumerateTypeAndContainingTypes(target)
 1425|                where x.FirstDeclaration?.Modifiers.Any(SyntaxKind.PartialKeyword) is false
 1426|                select x.FirstDeclaration;
 1427|     }
 1428| 
 1429|     private static Location? GetIdentifierLocation(INamedTypeSymbol type) => ((BaseTypeDeclarationSyntax?)type.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax())?.Identifier.GetLocation();
 1430| 
 1431|     private static Location? GetLocation(IParameterSymbol parameter) => parameter.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation();
 1432| 
 1433|     private static Location? GetParameterListLocation(IMethodSymbol? method) => ((BaseMethodDeclarationSyntax?)method?.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax())?.ParameterList.GetLocation();
 1434| 
 1435|     private static string GetGenericFormatterClassName(INamedTypeSymbol type)
 1436|     {
 1437|         return type.Name;
 1438|     }
 1439| 
 1440|     private static string GetMinimallyQualifiedClassName(INamedTypeSymbol type)
 1441|     {
 1442|         var name = type.ContainingType is object ? GetMinimallyQualifiedClassName(type.ContainingType) + "_" : string.Empty;
 1443|         name += type.ToDisplayString(SymbolDisplayFormat.MinimallyQualifiedFormat);
 1444|         name = name.Replace('.', '_');
 1445|         name = name.Replace('<', '_');
 1446|         name = name.Replace('>', '_');
 1447|         name = Regex.Replace(name, @"\[([,])*\]", match => $"Array{match.Length - 1}");
 1448|         name = name.Replace("?", string.Empty);
 1449|         return name;
 1450|     }
 1451| 
 1452|     private static bool TryGetNextConstructor(IEnumerator<IMethodSymbol>? ctorEnumerator, ref IMethodSymbol? ctor)
 1453|     {
 1454|         if (ctorEnumerator == null || ctor != null)
 1455|         {
 1456|             return false;
 1457|         }
 1458| 
 1459|         if (ctorEnumerator.MoveNext())
 1460|         {
 1461|             ctor = ctorEnumerator.Current;
 1462|             return true;
 1463|         }
 1464|         else
 1465|         {
 1466|             ctor = null;
 1467|             return false;
 1468|         }
 1469|     }
 1470| 
 1471|     private static bool IsPartialTypeRequired(Accessibility accessibility) => accessibility is not (Accessibility.Public or Accessibility.Internal or Accessibility.ProtectedOrInternal);
 1472| 
 1473|     private static bool IsAllowAccessibility(ITypeSymbol symbol)
 1474|     {
 1475|         do
 1476|         {
 1477|             if (symbol.DeclaredAccessibility is not (Accessibility.Public or Accessibility.Internal))
 1478|             {
 1479|                 return false;
 1480|             }
 1481| 
 1482|             symbol = symbol.ContainingType;
 1483|         }
 1484|         while (symbol is not null);
 1485| 
 1486|         return true;
 1487|     }
 1488| 
 1489|     private static bool IsOpenGenericTypeRecursively(INamedTypeSymbol type)
 1490|     {
 1491|         return type.IsGenericType && type.TypeArguments.Any(x => x is ITypeParameterSymbol || (x is INamedTypeSymbol symbol && IsOpenGenericTypeRecursively(symbol)));
 1492|     }
 1493| }
```

### tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs at head (4f1f9988), full file
```
    1| ﻿// Copyright (c) All contributors. All rights reserved.
    2| // Licensed under the MIT license. See LICENSE file in the project root for full license information.
    3| 
    4| using MessagePack.Analyzers.CodeFixes;
    5| using MessagePack.SourceGenerator.Analyzers;
    6| using Microsoft.CodeAnalysis.CSharp;
    7| using Microsoft.CodeAnalysis.Testing;
    8| using VerifyCS = CSharpCodeFixVerifier<MessagePack.SourceGenerator.Analyzers.MsgPack00xMessagePackAnalyzer, MessagePack.Analyzers.CodeFixes.MessagePackCodeFixProvider>;
    9| 
   10| public class MsgPack00xAnalyzerTests
   11| {
   12|     private const string Preamble = @"
   13| using MessagePack;
   14| ";
   15| 
   16|     [Fact]
   17|     public async Task NoMessagePackReference()
   18|     {
   19|         string input = @"
   20| public class Foo
   21| {
   22| }
   23| ";
   24| 
   25|         await VerifyCS.VerifyAnalyzerWithoutMessagePackReferenceAsync(input);
   26|     }
   27| 
   28|     [Fact]
   29|     public async Task MessageFormatterAttribute()
   30|     {
   31|         string input = Preamble + @"using MessagePack.Formatters;
   32| 
   33| public class FooFormatter : IMessagePackFormatter<Foo> {
   34|     public void Serialize(ref MessagePackWriter writer, Foo value, MessagePackSerializerOptions options) {}
   35|     public Foo Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options) => default;
   36| }
   37| 
   38| 
   39| [MessagePackFormatter(typeof(FooFormatter))]
   40| public struct Foo
   41| {
   42| }
   43| 
   44| [MessagePackObject]
   45| public class SomeClass {
   46|     [Key(0)]
   47|     public Foo SomeFoo { get; set; }
   48| }
   49| ";
   50| 
   51|         await VerifyCS.VerifyAnalyzerAsync(input);
   52|     }
   53| 
   54|     [Fact]
   55|     public async Task InvalidMessageFormatterType()
   56|     {
   57|         string input = Preamble + @"using MessagePack.Formatters;
   58| 
   59| public class InvalidMessageFormatter { }
   60| 
   61| [MessagePackFormatter({|MsgPack006:typeof(InvalidMessageFormatter)|})]
   62| public struct Foo
   63| {
   64| }
   65| 
   66| [MessagePackObject]
   67| public class SomeClass {
   68|     [Key(0)]
   69|     public Foo SomeFoo { get; set; }
   70| }
   71| ";
   72| 
   73|         await VerifyCS.VerifyAnalyzerAsync(input);
   74|     }
   75| 
   76|     [Fact]
   77|     public async Task NullStringKey()
   78|     {
   79|         string input = Preamble + @"
   80| [MessagePackObject]
   81| public class Foo
   82| {
   83|     [Key(null)]
   84|     public string {|MsgPack005:Member|} { get; set; }
   85| }
   86| ";
   87| 
   88|         await new VerifyCS.Test
   89|         {
   90|             TestCode = input,
   91|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
   92|         }.RunAsync();
   93|     }
   94| 
   95|     [Fact]
   96|     public async Task AddAttributesToMembers()
   97|     {
   98|         string input = Preamble + @"
   99| [MessagePackObject]
  100| public class Foo
  101| {
  102|     public string {|MsgPack004:Member1|} { get; set; }
  103|     public string {|MsgPack004:Member2|} { get; set; }
  104| }
  105| ";
  106| 
  107|         string output = Preamble + @"
  108| [MessagePackObject]
  109| public class Foo
  110| {
  111|     [Key(0)]
  112|     public string Member1 { get; set; }
  113|     [Key(1)]
  114|     public string Member2 { get; set; }
  115| }
  116| ";
  117| 
  118|         await new VerifyCS.Test
  119|         {
  120|             TestCode = input,
  121|             FixedCode = output,
  122|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  123|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  124|         }.RunAsync();
  125|     }
  126| 
  127|     /// <summary>
  128|     /// Verifies that only public members require attributes (so long as no non-public member is already attributed.)
  129|     /// </summary>
  130|     [Fact]
  131|     public async Task AddAttributesToMembers_PublicOnly()
  132|     {
  133|         string input = Preamble + @"
  134| [MessagePackObject]
  135| public class Foo
  136| {
  137|     public string {|MsgPack004:Member1|} { get; set; }
  138|     internal string Member2 { get; set; }
  139| }
  140| ";
  141| 
  142|         string output = Preamble + @"
  143| [MessagePackObject]
  144| public class Foo
  145| {
  146|     [Key(0)]
  147|     public string Member1 { get; set; }
  148|     internal string Member2 { get; set; }
  149| }
  150| ";
  151| 
  152|         await new VerifyCS.Test
  153|         {
  154|             TestCode = input,
  155|             FixedCode = output,
  156|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  157|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  158|         }.RunAsync();
  159|     }
  160| 
  161|     /// <summary>
  162|     /// Verifies that all members require attributes if AllowPrivate = true is set on the attribute.
  163|     /// </summary>
  164|     [Fact]
  165|     public async Task AddAttributesToMembers_AllowPrivateAttribute()
  166|     {
  167|         string input = Preamble + @"
  168| [MessagePackObject(AllowPrivate = true)]
  169| public class Foo
  170| {
  171|     public string {|MsgPack004:Member1|} { get; set; }
  172|     internal string {|MsgPack004:Member2|} { get; set; }
  173| }
  174| ";
  175| 
  176|         string output = Preamble + @"
  177| [MessagePackObject(AllowPrivate = true)]
  178| public class Foo
  179| {
  180|     [Key(0)]
  181|     public string Member1 { get; set; }
  182|     [Key(1)]
  183|     internal string Member2 { get; set; }
  184| }
  185| ";
  186| 
  187|         await new VerifyCS.Test
  188|         {
  189|             TestCode = input,
  190|             FixedCode = output,
  191|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  192|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  193|         }.RunAsync();
  194|     }
  195| 
  196|     /// <summary>
  197|     /// Verifies that our annotated member analyzer automatically starts enforcing that
  198|     /// non-public members are annotated after the first non-public member is annotated.
  199|     /// </summary>
  200|     [Fact]
  201|     public async Task AddAttributesToMembers_MixedVisibility()
  202|     {
  203|         string input = Preamble + @"
  204| [{|MsgPack015:MessagePackObject|}]
  205| public class Foo
  206| {
  207|     private string {|MsgPack004:member4|};
  208|     [Key(0)]
  209|     public string Member1 { get; set; }
  210|     [Key(1)]
  211|     internal string Member2 { get; set; }
  212|     public string {|MsgPack004:Member3|} { get; set; }
  213| }
  214| ";
  215| 
  216|         string output = Preamble + @"
  217| [{|MsgPack015:MessagePackObject|}]
  218| public class {|MsgPack011:Foo|}
  219| {
  220|     [Key(2)]
  221|     private string member4;
  222|     [Key(0)]
  223|     public string Member1 { get; set; }
  224|     [Key(1)]
  225|     internal string Member2 { get; set; }
  226|     [Key(3)]
  227|     public string Member3 { get; set; }
  228| }
  229| ";
  230| 
  231|         await new VerifyCS.Test
  232|         {
  233|             TestCode = input,
  234|             FixedCode = output,
  235|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  236|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  237|         }.RunAsync();
  238|     }
  239| 
  240|     [Fact]
  241|     public async Task AddIgnoreAttributesToMembers()
  242|     {
  243|         string input = Preamble + @"
  244| [MessagePackObject]
  245| public class Foo
  246| {
  247|     public string {|MsgPack004:member1 = null|};
  248|     public string {|MsgPack004:member2 = null|};
  249|     [Key(0)]
  250|     public string Member3 { get; set; }
  251| }
  252| ";
  253| 
  254|         string output = Preamble + @"
  255| [MessagePackObject]
  256| public class Foo
  257| {
  258|     [IgnoreMember]
  259|     public string member1 = null;
  260|     [IgnoreMember]
  261|     public string member2 = null;
  262|     [Key(0)]
  263|     public string Member3 { get; set; }
  264| }
  265| ";
  266| 
  267|         await new VerifyCS.Test
  268|         {
  269|             TestCode = input,
  270|             FixedCode = output,
  271|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  272|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddIgnoreMemberAttributeEquivalenceKey,
  273|         }.RunAsync();
  274|     }
  275| 
  276|     [Fact]
  277|     public async Task AddAttributeToField_WithComment()
  278|     {
  279|         string input = Preamble + @"
  280| [MessagePackObject]
  281| public class Foo
  282| {
  283|     // comment
  284|     public string {|MsgPack004:Member1|};
  285| }
  286| ";
  287| 
  288|         string output = Preamble + @"
  289| [MessagePackObject]
  290| public class Foo
  291| {
  292|     // comment
  293|     [Key(0)]
  294|     public string Member1;
  295| }
  296| ";
  297| 
  298|         await new VerifyCS.Test
  299|         {
  300|             TestCode = input,
  301|             FixedCode = output,
  302|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  303|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  304|         }.RunAsync();
  305|     }
  306| 
  307|     [Fact]
  308|     public async Task AddAttributeToType_Properties()
  309|     {
  310|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  311|         string input = /* lang=c#-test */ """
  312|             public class Foo
  313|             {
  314|                 public string Member { get; set; }
  315|             }
  316| 
  317|             [MessagePack.MessagePackObject]
  318|             public class Bar
  319|             {
  320|                 [MessagePack.Key(0)]
  321|                 public Foo {|MsgPack003:Member|} { get; set; }
  322|             }
  323|             """;
  324| 
  325|         string output = /* lang=c#-test */ """
  326|             [MessagePack.MessagePackObject]
  327|             public class Foo
  328|             {
  329|                 [MessagePack.Key(0)]
  330|                 public string Member { get; set; }
  331|             }
  332| 
  333|             [MessagePack.MessagePackObject]
  334|             public class Bar
  335|             {
  336|                 [MessagePack.Key(0)]
  337|                 public Foo Member { get; set; }
  338|             }
  339|             """;
  340| 
  341|         await new VerifyCS.Test
  342|         {
  343|             TestCode = input,
  344|             FixedCode = output,
  345|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  346|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  347|         }.RunAsync();
  348|     }
  349| 
  350|     [Fact]
  351|     public async Task AddAttributeToType_Fields()
  352|     {
  353|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  354|         string input = /* lang=c#-test */ """
  355|             public class Foo
  356|             {
  357|                 public string Member;
  358|             }
  359| 
  360|             [MessagePack.MessagePackObject]
  361|             public class Bar
  362|             {
  363|                 [MessagePack.Key(0)]
  364|                 public Foo {|MsgPack003:Member|};
  365|             }
  366|             """;
  367| 
  368|         string output = /* lang=c#-test */ """
  369|             [MessagePack.MessagePackObject]
  370|             public class Foo
  371|             {
  372|                 [MessagePack.Key(0)]
  373|                 public string Member;
  374|             }
  375| 
  376|             [MessagePack.MessagePackObject]
  377|             public class Bar
  378|             {
  379|                 [MessagePack.Key(0)]
  380|                 public Foo Member;
  381|             }
  382|             """;
  383| 
  384|         await new VerifyCS.Test
  385|         {
  386|             TestCode = input,
  387|             FixedCode = output,
  388|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  389|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  390|         }.RunAsync();
  391|     }
  392| 
  393|     [Fact]
  394|     public async Task AddAttributeToType_Nullable()
  395|     {
  396|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  397|         string input = /* lang=c#-test */ """
  398|             public struct Foo
  399|             {
  400|                 public string Member;
  401|             }
  402| 
  403|             [MessagePack.MessagePackObject]
  404|             public class Bar
  405|             {
  406|                 [MessagePack.Key(0)]
  407|                 public Foo? {|MsgPack003:Member|};
  408|             }
  409|             """;
  410| 
  411|         string output = /* lang=c#-test */ """
  412|             [MessagePack.MessagePackObject]
  413|             public struct Foo
  414|             {
  415|                 [MessagePack.Key(0)]
  416|                 public string Member;
  417|             }
  418| 
  419|             [MessagePack.MessagePackObject]
  420|             public class Bar
  421|             {
  422|                 [MessagePack.Key(0)]
  423|                 public Foo? Member;
  424|             }
  425|             """;
  426| 
  427|         await new VerifyCS.Test
  428|         {
  429|             TestCode = input,
  430|             FixedCode = output,
  431|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  432|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  433|         }.RunAsync();
  434|     }
  435| 
  436|     [Fact]
  437|     public async Task AddAttributeToType_Generic()
  438|     {
  439|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  440|         string input = /* lang=c#-test */ """
  441|             public struct Foo
  442|             {
  443|                 public string Member;
  444|             }
  445| 
  446|             [MessagePack.MessagePackObject]
  447|             public class Bar
  448|             {
  449|                 [MessagePack.Key(0)]
  450|                 public System.Collections.Generic.List<Foo> {|MsgPack003:Member|};
  451|             }
  452|             """;
  453| 
  454|         string output = /* lang=c#-test */ """
  455|             [MessagePack.MessagePackObject]
  456|             public struct Foo
  457|             {
  458|                 [MessagePack.Key(0)]
  459|                 public string Member;
  460|             }
  461| 
  462|             [MessagePack.MessagePackObject]
  463|             public class Bar
  464|             {
  465|                 [MessagePack.Key(0)]
  466|                 public System.Collections.Generic.List<Foo> Member;
  467|             }
  468|             """;
  469| 
  470|         await new VerifyCS.Test
  471|         {
  472|             TestCode = input,
  473|             FixedCode = output,
  474|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  475|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  476|         }.RunAsync();
  477|     }
  478| 
  479|     [Fact]
  480|     public async Task AddAttributeToTypeForRecord1()
  481|     {
  482|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  483|         string input = @"
  484| public class Foo
  485| {
  486|     public string Member { get; set; }
  487| }
  488| 
  489| [MessagePack.MessagePackObject]
  490| public record Bar
  491| {
  492|     [MessagePack.Key(0)]
  493|     public Foo {|MsgPack003:Member|} { get; set; }
  494| }
  495| ";
  496| 
  497|         string output = @"
  498| [MessagePack.MessagePackObject]
  499| public class Foo
  500| {
  501|     [MessagePack.Key(0)]
  502|     public string Member { get; set; }
  503| }
  504| 
  505| [MessagePack.MessagePackObject]
  506| public record Bar
  507| {
  508|     [MessagePack.Key(0)]
  509|     public Foo Member { get; set; }
  510| }
  511| ";
  512| 
  513|         await new VerifyCS.Test
  514|         {
  515|             TestCode = input,
  516|             FixedCode = output,
  517|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  518|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  519|         }.RunAsync();
  520|     }
  521| 
  522|     [Fact]
  523|     public async Task AddAttributeToTypeForRecord2()
  524|     {
  525|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  526|         string input = @"
  527| public record Foo
  528| {
  529|     public string Member { get; set; }
  530| }
  531| 
  532| [MessagePack.MessagePackObject]
  533| public record Bar
  534| {
  535|     [MessagePack.Key(0)]
  536|     public Foo {|MsgPack003:Member|} { get; set; }
  537| }
  538| ";
  539| 
  540|         string output = @"
  541| [MessagePack.MessagePackObject]
  542| public record Foo
  543| {
  544|     [MessagePack.Key(0)]
  545|     public string Member { get; set; }
  546| }
  547| 
  548| [MessagePack.MessagePackObject]
  549| public record Bar
  550| {
  551|     [MessagePack.Key(0)]
  552|     public Foo Member { get; set; }
  553| }
  554| ";
  555| 
  556|         await new VerifyCS.Test
  557|         {
  558|             TestCode = input,
  559|             FixedCode = output,
  560|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  561|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  562|         }.RunAsync();
  563|     }
  564| 
  565|     [Fact]
  566|     public async Task AddAttributeToTypeForRecordPrimaryConstructor()
  567|     {
  568|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  569|         string input = @"
  570| public class Foo
  571| {
  572|     public string Member { get; set; }
  573| }
  574| 
  575| [MessagePack.MessagePackObject]
  576| public record Bar([property: MessagePack.Key(0)] Foo {|MsgPack003:Member|});
  577| 
  578| namespace System.Runtime.CompilerServices
  579| {
  580|     internal static class IsExternalInit
  581|     {
  582|     }
  583| }
  584| ";
  585| 
  586|         string output = @"
  587| [MessagePack.MessagePackObject]
  588| public class Foo
  589| {
  590|     [MessagePack.Key(0)]
  591|     public string Member { get; set; }
  592| }
  593| 
  594| [MessagePack.MessagePackObject]
  595| public record Bar([property: MessagePack.Key(0)] Foo Member);
  596| 
  597| namespace System.Runtime.CompilerServices
  598| {
  599|     internal static class IsExternalInit
  600|     {
  601|     }
  602| }
  603| ";
  604| 
  605|         await new VerifyCS.Test
  606|         {
  607|             TestCode = input,
  608|             FixedCode = output,
  609|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  610|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  611|         }.RunAsync();
  612|     }
  613| 
  614|     [Fact]
  615|     public async Task CodeFixAppliesAcrossFiles()
  616|     {
  617|         string source1 = @"
  618| public class Foo
  619| {
  620|     public int Member1 { get; set; }
  621| }
  622| ";
  623| 
  624|         string source2 = @"using MessagePack;
  625| 
  626| [MessagePackObject]
  627| public class Bar : {|MsgPack004:Foo|}
  628| {
  629|     public int {|MsgPack004:Member2|} { get; set; }
  630| }
  631| ";
  632| 
  633|         string output1 = @"
  634| public class Foo
  635| {
  636|     [MessagePack.Key(1)]
  637|     public int Member1 { get; set; }
  638| }
  639| ";
  640|         string output2 = @"using MessagePack;
  641| 
  642| [MessagePackObject]
  643| public class Bar : Foo
  644| {
  645|     [Key(0)]
  646|     public int Member2 { get; set; }
  647| }
  648| ";
  649| 
  650|         await new VerifyCS.Test(ReferencesSet.MessagePackAnnotations)
  651|         {
  652|             CodeFixTestBehaviors = CodeFixTestBehaviors.SkipLocalDiagnosticCheck, // BUGBUG: move diagnostic to `Foo` reference in Bar's base type list.
  653|             TestState =
  654|             {
  655|                 Sources = { source1, source2 },
  656|             },
  657|             FixedState =
  658|             {
  659|                 Sources = { output1, output2 },
  660|             },
  661|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  662|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  663|         }.RunAsync();
  664|     }
  665| 
  666|     [Fact]
  667|     public async Task AddAttributeToGenericType()
  668|     {
  669|         string input = Preamble + /* lang=c#-test */ """
  670|             public class Foo<T>
  671|             {
  672|                 public T Member { get; set; }
  673|             }
  674| 
  675|             [MessagePackObject]
  676|             public class Bar
  677|             {
  678|                 [Key(0)]
  679|                 public Foo<int> {|MsgPack003:MemberUserGeneric|} { get; set; }
  680| 
  681|                 [Key(1)]
  682|                 public System.Collections.Generic.List<int> MemberKnownGeneric { get; set; }
  683|             }
  684|             """;
  685| 
  686|         string output = Preamble + /* lang=c#-test */ """
  687| 
  688|             [MessagePackObject]
  689|             public class Foo<T>
  690|             {
  691|                 [Key(0)]
  692|                 public T Member { get; set; }
  693|             }
  694| 
  695|             [MessagePackObject]
  696|             public class Bar
  697|             {
  698|                 [Key(0)]
  699|                 public Foo<int> MemberUserGeneric { get; set; }
  700| 
  701|                 [Key(1)]
  702|                 public System.Collections.Generic.List<int> MemberKnownGeneric { get; set; }
  703|             }
  704|             """;
  705| 
  706|         await new VerifyCS.Test
  707|         {
  708|             TestCode = input,
  709|             FixedCode = output,
  710|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  711|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  712|         }.RunAsync();
  713|     }
  714| 
  715|     [Fact]
  716|     public async Task AddAttributesToMembersOfRecord()
  717|     {
  718|         string input = Preamble + /* lang=c#-test */ """
  719|             [MessagePackObject]
  720|             public record Foo
  721|             {
  722|                 public string {|MsgPack004:Member1|} { get; set; }
  723|                 public string {|MsgPack004:Member2|} { get; set; }
  724|             }
  725|             """;
  726| 
  727|         string output = Preamble + /* lang=c#-test */ """
  728|             [MessagePackObject]
  729|             public record Foo
  730|             {
  731|                 [Key(0)]
  732|                 public string Member1 { get; set; }
  733|                 [Key(1)]
  734|                 public string Member2 { get; set; }
  735|             }
  736|             """;
  737|         await new VerifyCS.Test
  738|         {
  739|             ReferenceAssemblies = ReferenceAssemblies.Net.Net60,
  740|             CompilerDiagnostics = CompilerDiagnostics.Errors,
  741|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  742|             SolutionTransforms =
  743|             {
  744|                 static (solution, projectId) =>
  745|                 {
  746|                     return solution.WithProjectParseOptions(projectId, new CSharpParseOptions(languageVersion: LanguageVersion.CSharp11));
  747|                 },
  748|             },
  749|             TestCode = input,
  750|             FixedCode = output,
  751|         }.RunAsync();
  752|     }
  753| 
  754|     [Fact]
  755|     public async Task AddAttributesToMembersOfRecordStruct()
  756|     {
  757|         string input = Preamble + /* lang=c#-test */ """
  758|             [MessagePackObject]
  759|             public record struct Foo
  760|             {
  761|                 public string {|MsgPack004:Member1|} { get; set; }
  762|                 public string {|MsgPack004:Member2|} { get; set; }
  763|             }
  764|             """;
  765| 
  766|         string output = Preamble + /* lang=c#-test */ """
  767|             [MessagePackObject]
  768|             public record struct Foo
  769|             {
  770|                 [Key(0)]
  771|                 public string Member1 { get; set; }
  772|                 [Key(1)]
  773|                 public string Member2 { get; set; }
  774|             }
  775|             """;
  776|         await new VerifyCS.Test
  777|         {
  778|             ReferenceAssemblies = ReferenceAssemblies.Net.Net60,
  779|             CompilerDiagnostics = CompilerDiagnostics.Errors,
  780|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  781|             SolutionTransforms =
  782|             {
  783|                 static (solution, projectId) =>
  784|                 {
  785|                     return solution.WithProjectParseOptions(projectId, new CSharpParseOptions(languageVersion: LanguageVersion.CSharp11));
  786|                 },
  787|             },
  788|             TestCode = input,
  789|             FixedCode = output,
  790|         }.RunAsync();
  791|     }
  792| 
  793|     [Fact]
  794|     public async Task AddAttributesToMembersOfRecordWithPrimaryCtor()
  795|     {
  796|         string input = Preamble + /* lang=c#-test */ """
  797|             [MessagePackObject]
  798|             public record {|MsgPack007:Foo|}(
  799|                 string {|MsgPack004:Member1|},
  800|                 string {|MsgPack004:Member2|});
  801|             """;
  802| 
  803|         string output = Preamble + /* lang=c#-test */ """
  804|             [MessagePackObject]
  805|             public record Foo(
  806|                 [property: Key(0)] string Member1,
  807|                 [property: Key(1)] string Member2);
  808|             """;
  809| 
  810|         await new VerifyCS.Test
  811|         {
  812|             ReferenceAssemblies = ReferenceAssemblies.Net.Net60,
  813|             CompilerDiagnostics = CompilerDiagnostics.Errors,
  814|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  815|             SolutionTransforms =
  816|             {
  817|                 static (solution, projectId) =>
  818|                 {
  819|                     return solution.WithProjectParseOptions(projectId, new CSharpParseOptions(languageVersion: LanguageVersion.CSharp11));
  820|                 },
  821|             },
  822|             TestCode = input,
  823|             FixedCode = output,
  824|         }.RunAsync();
  825|     }
  826| 
  827|     [Fact]
  828|     public async Task AddAttributesToMembersOfRecordStructWithPrimaryCtor()
  829|     {
  830|         string input = Preamble + /* lang=c#-test */ """
  831|             [MessagePackObject]
  832|             public record struct Foo(
  833|                 string {|MsgPack004:Member1|},
  834|                 string {|MsgPack004:Member2|});
  835|             """;
  836| 
  837|         string output = Preamble + /* lang=c#-test */ """
  838|             [MessagePackObject]
  839|             public record struct Foo(
  840|                 [property: Key(0)] string Member1,
  841|                 [property: Key(1)] string Member2);
  842|             """;
  843| 
  844|         await new VerifyCS.Test
  845|         {
  846|             ReferenceAssemblies = ReferenceAssemblies.Net.Net60,
  847|             CompilerDiagnostics = CompilerDiagnostics.Errors,
  848|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  849|             SolutionTransforms =
  850|             {
  851|                 static (solution, projectId) =>
  852|                 {
  853|                     return solution.WithProjectParseOptions(projectId, new CSharpParseOptions(languageVersion: LanguageVersion.CSharp11));
  854|                 },
  855|             },
  856|             TestCode = input,
  857|             FixedCode = output,
  858|         }.RunAsync();
  859|     }
  860| 
  861|     [Fact]
  862|     public async Task DoNotAddAttributesToClassWithPrimaryCtor()
  863|     {
  864|         string input = Preamble + /* lang=c#-test */ """
  865|             [MessagePackObject]
  866|             public class {|MsgPack007:Foo|}(
  867|                 string Member1,
  868|                 string Member2);
  869|             """;
  870| 
  871|         string output = Preamble + /* lang=c#-test */ """
  872|             [MessagePackObject]
  873|             public class {|MsgPack007:Foo|}(
  874|                 string Member1,
  875|                 string Member2);
  876|             """;
  877| 
  878|         await new VerifyCS.Test
  879|         {
  880|             ReferenceAssemblies = ReferenceAssemblies.Net.Net60,
  881|             CompilerDiagnostics = CompilerDiagnostics.Errors,
  882|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  883|             SolutionTransforms =
  884|             {
  885|                 static (solution, projectId) =>
  886|                 {
  887|                     return solution.WithProjectParseOptions(projectId, new CSharpParseOptions(languageVersion: LanguageVersion.CSharp12));
  888|                 },
  889|             },
  890|             TestCode = input,
  891|             FixedCode = output,
  892|         }.RunAsync();
  893|     }
  894| 
  895|     [Fact]
  896|     public async Task DerivedAttributes()
  897|     {
  898|         string test = /* lang=c#-test */ """
  899|             using MessagePack;
  900| 
  901|             [MessagePackObject]
  902|             public class A
  903|             {
  904|                 [{|MsgPack016:CompositeKey(0, 1)|}]
  905|                 public string Prop1 { get; set; }
  906| 
  907|                 [{|MsgPack016:CompositeKey(0, 2)|}]
  908|                 public string Field2;
  909|             }
  910| 
  911|             [MessagePackObject]
  912|             public class B : {|MsgPack016:A|}
  913|             {
  914|                 [{|MsgPack016:CompositeKey(1, 1)|}]
  915|                 public string Prop3 { get; set; }
  916| 
  917|                 [{|MsgPack016:CompositeKey(1, 2)|}]
  918|                 public string Field4;
  919|             }
  920| 
  921|             public class CompositeKeyAttribute : KeyAttribute
  922|             {
  923|                 public CompositeKeyAttribute(byte level, int index)
  924|                     : base(CreateKey(level, index)) { }
  925| 
  926|                 public static string CreateKey(byte level, int index)
  927|                 {
  928|                     var c = (char)('A' + level);
  929|                     return c + index.ToString("x");
  930|                 }
  931|             }
  932|             """;
  933| 
  934|         await VerifyCS.VerifyAnalyzerAsync(test);
  935|     }
  936| 
  937|     [Fact]
  938|     public async Task DerivedAttributes_SourceGenerationDisabled()
  939|     {
  940|         string test = /* lang=c#-test */ """
  941|             using MessagePack;
  942| 
  943|             [MessagePackObject(SuppressSourceGeneration = true)]
  944|             public class A
  945|             {
  946|                 [CompositeKey(0, 1)]
  947|                 public string Prop1 { get; set; }
  948| 
  949|                 [CompositeKey(0, 2)]
  950|                 public string Field2;
  951|             }
  952| 
  953|             [MessagePackObject(SuppressSourceGeneration = true)]
  954|             public class B : A
  955|             {
  956|                 [CompositeKey(1, 1)]
  957|                 public string Prop3 { get; set; }
  958| 
  959|                 [CompositeKey(1, 2)]
  960|                 public string Field4;
  961|             }
  962| 
  963|             public class CompositeKeyAttribute : KeyAttribute
  964|             {
  965|                 public CompositeKeyAttribute(byte level, int index)
  966|                     : base(CreateKey(level, index)) { }
  967| 
  968|                 public static string CreateKey(byte level, int index)
  969|                 {
  970|                     var c = (char)('A' + level);
  971|                     return c + index.ToString("x");
  972|                 }
  973|             }
  974|             """;
  975| 
  976|         await VerifyCS.VerifyAnalyzerAsync(test);
  977|     }
  978| 
  979|     /// <summary>
  980|     /// Verifies that the analyzer keeps reporting contract diagnostics for types that opt out of source generation.
  981|     /// See https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2234.
  982|     /// </summary>
  983|     [Fact]
  984|     public async Task SourceGenerationDisabled_AnalyzerStillReportsDiagnostics()
  985|     {
  986|         string test = /* lang=c#-test */ """
  987|             using MessagePack;
  988| 
  989|             [MessagePackObject(SuppressSourceGeneration = true)]
  990|             public class Foo
  991|             {
  992|                 [Key(0)]
  993|                 public string Member0 { get; set; }
  994| 
  995|                 public string {|MsgPack004:Member1|} { get; set; }
  996|             }
  997| 
  998|             public class NotAttributed { }
  999| 
 1000|             [MessagePackObject(SuppressSourceGeneration = true)]
 1001|             public class Bar
 1002|             {
 1003|                 [Key(0)]
 1004|                 public NotAttributed {|MsgPack003:Member0|} { get; set; }
 1005|             }
 1006| 
 1007|             [MessagePackObject(SuppressSourceGeneration = true)]
 1008|             public struct Baz
 1009|             {
 1010|                 [Key(0)]
 1011|                 public int A { get; set; }
 1012| 
 1013|                 public int {|MsgPack004:B|} { get; set; }
 1014|             }
 1015| 
 1016|             [MessagePackObject(SuppressSourceGeneration = true)]
 1017|             public class Generic<T>
 1018|             {
 1019|                 [Key(0)]
 1020|                 public T A { get; set; }
 1021| 
 1022|                 public int {|MsgPack004:B|} { get; set; }
 1023|             }
 1024| 
 1025|             public class Outer
 1026|             {
 1027|                 [MessagePackObject(SuppressSourceGeneration = true)]
 1028|                 public class Nested
 1029|                 {
 1030|                     public int {|MsgPack004:B|} { get; set; }
 1031|                 }
 1032|             }
 1033| 
 1034|             [MessagePackObject(SuppressSourceGeneration = true)]
 1035|             public class Derived : {|MsgPack004:Foo|}
 1036|             {
 1037|                 [Key(5)]
 1038|                 public int C { get; set; }
 1039| 
 1040|                 public int {|MsgPack004:D|} { get; set; }
 1041|             }
 1042|             """;
 1043| 
 1044|         await new VerifyCS.Test
 1045|         {
 1046|             TestCode = test,
 1047|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
 1048|         }.RunAsync();
 1049|     }
 1050| 
 1051|     [Fact]
 1052|     public async Task InitPropertyInitializer()
 1053|     {
 1054|         string test = /* lang=c#-test */ """
 1055|             using MessagePack;
 1056| 
 1057|             [MessagePackObject]
 1058|             public class A
 1059|             {
 1060|                 [Key(0)]
 1061|                 public string Prop1 { get; init; } {|MsgPack017:= "some default"|};
 1062| 
 1063|                 [Key(1)]
 1064|                 public string Prop2 { get; set; } = "some default";
 1065|             }
 1066| 
 1067| 
 1068|             [MessagePackObject(SuppressSourceGeneration = true)]
 1069|             public class B
 1070|             {
 1071|                 [Key(0)]
 1072|                 public string Prop1 { get; init; } = "some default";
 1073| 
 1074|                 [Key(1)]
 1075|                 public string Prop2 { get; set; } = "some default";
 1076|             }
 1077|             """;
 1078| 
 1079|         await VerifyCS.VerifyAnalyzerAsync(test);
 1080|     }
 1081| 
 1082|     [Fact]
 1083|     public async Task PrivateMembersInBaseClassNeedNoAttribution()
 1084|     {
 1085|         string test = /* lang=c#-test */ """
 1086|             using MessagePack;
 1087| 
 1088|             [MessagePackObject]
 1089|             public class A
 1090|             {
 1091|                 private int somePrivateField;
 1092| 
 1093|                 [Key(0)]
 1094|                 public int SomePublicProp { get; set; }
 1095| 
 1096|                 private int SomePrivateProp { get; set; }
 1097|             }
 1098| 
 1099|             [MessagePackObject]
 1100|             public class B : A
 1101|             {
 1102|                 [Key(1)]
 1103|                 public int SomePublicProp2 { get; set; }
 1104|             }
 1105|             """;
 1106| 
 1107|         await VerifyCS.VerifyAnalyzerAsync(test);
 1108|     }
 1109| 
 1110|     [Fact]
 1111|     public async Task NameCollisionsInForceMapMode()
 1112|     {
 1113|         string test = /* lang=c#-test */ """
 1114|             using MessagePack;
 1115| 
 1116|             [MessagePackObject(true)]
 1117|             public class Base
 1118|             {
 1119|                 public string Prop { get; set; }
 1120| 
 1121|                 public string Field;
 1122| 
 1123|                 public string TwoFaced { get; set; } // derived declares a *field* by the same name.
 1124|             }
 1125| 
 1126|             [MessagePackObject(true)]
 1127|             public class Derived : Base
 1128|             {
 1129|                 public new string {|MsgPack018:Prop|} { get; set; }
 1130| 
 1131|                 public new string {|MsgPack018:Field|};
 1132| 
 1133|                 public new string {|MsgPack018:TwoFaced|};
 1134|             }
 1135|             """;
 1136| 
 1137|         await VerifyCS.VerifyAnalyzerAsync(test);
 1138|     }
 1139| 
 1140|     [Fact]
 1141|     public async Task AbstractFormatterDoesNotAttractAttention()
 1142|     {
 1143|         string test = /* lang=c#-test */ """
 1144|             using MessagePack;
 1145|             using MessagePack.Formatters;
 1146| 
 1147|             public abstract class AbstractFormatter1 : IMessagePackFormatter<object>
 1148|             {
 1149|                 public abstract void Serialize(ref MessagePackWriter writer, object value, MessagePackSerializerOptions options);
 1150|                 public abstract object Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options);
 1151|             }
 1152| 
 1153|             public abstract class AbstractFormatter2 : IMessagePackFormatter<object>
 1154|             {
 1155|                 public abstract void Serialize(ref MessagePackWriter writer, object value, MessagePackSerializerOptions options);
 1156|                 public abstract object Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options);
 1157|             }
 1158|             """;
 1159| 
 1160|         await VerifyCS.VerifyAnalyzerAsync(test);
 1161|     }
 1162| }
```

### src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base (32258fdb), around the changed lines
```
  ... lines 1-1335 not shown ...
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
  ... lines 1402-1491 not shown ...
```

## What you did NOT get (refuse anything that depends on it)
- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)

Return only the JSON object described in the brief.