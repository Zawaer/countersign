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
# Change var-2234-v1: branch cs-var/2234-v1, base 32258fdbee4bcd653c79f51b4376b5103c6f4d27, head 8c168b569767fb319606e6903db5d5d2de305135
Commit message: Add regression test: analyzer must still report for SuppressSourceGeneration types

Issue #2234 reports that the MsgPack00x analyzer stops reporting contract
diagnostics (e.g. MsgPack004 for a missing [Key]) on types annotated with
[MessagePackObject(SuppressSourceGeneration = true)]. On the 3.1.x line this was
caused by moving the SuppressSourceGeneration early return in
TypeCollector.GetObjectInfo ahead of member analysis. On develop the early
return still sits after member analysis, so diagnostics are reported; this test
locks that behavior in.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Upstream issue: https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2234

## Requirement set (requirements/var-2234-v1.yaml)
```yaml
# REUSED from requirements/2234.yaml (same clauses, same ids, unchanged text) for another fix of the same upstream issue
# #2234, so every fix of it is judged against the same clauses (docs/MEASUREMENT.md, "Same issue, several fixes").
# Still a placeholder derived from the issue, not a Tieto set.
change: "var-2234-v1"
branch: cs-var/2234-v1
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
 "change": "var-2234-v1",
 "branch": "cs-var/2234-v1",
 "base": "32258fdb",
 "head": "8c168b56",
 "base_full": "32258fdbee4bcd653c79f51b4376b5103c6f4d27",
 "head_full": "8c168b569767fb319606e6903db5d5d2de305135",
 "commit_message": "Add regression test: analyzer must still report for SuppressSourceGeneration types\n\nIssue #2234 reports that the MsgPack00x analyzer stops reporting contract\ndiagnostics (e.g. MsgPack004 for a missing [Key]) on types annotated with\n[MessagePackObject(SuppressSourceGeneration = true)]. On the 3.1.x line this was\ncaused by moving the SuppressSourceGeneration early return in\nTypeCollector.GetObjectInfo ahead of member analysis. On develop the early\nreturn still sits after member analysis, so diagnostics are reported; this test\nlocks that behavior in.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>",
 "author": "Zawaer",
 "agent_written": true,
 "diff": {
  "files": 1,
  "insertions": 18,
  "deletions": 0,
  "by_kind": {
   "test": 1
  },
  "by_file": [
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs",
    "ins": 18,
    "del": 0,
    "kind": "test"
   }
  ]
 },
 "new_tests_in_diff": [
  "MsgPack00xAnalyzerTests.MissingKeyAttribute_SourceGenerationSuppressed"
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
   "log": "evidence/var-2234-v1/logs/build.log",
   "duration_s": 5.0
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
     "name": "MsgPack00xAnalyzerTests.MissingKeyAttribute_SourceGenerationSuppressed",
     "outcome": "passed",
     "new": true
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
    }
   ],
   "log": "evidence/var-2234-v1/logs/tests_targeted.1.log",
   "duration_s": 3.0,
   "filter": [
    "FullyQualifiedName~MsgPack00xAnalyzerTests."
   ],
   "project": "tests/MessagePack.SourceGenerator.Tests"
  },
  {
   "id": "tests.fail_without_fix",
   "status": "skipped",
   "reason": "test-only change: no file under src/ changed, so there is no source to revert",
   "summary": "not run: test-only change (no file under src/ changed), so there is no source to revert"
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
   "log": "evidence/var-2234-v1/logs/tests_full_suite.log",
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
    "diff_added_lines": 18,
    "files": 1,
    "paths": 1,
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
    "diff": "git diff 32258fdb 8c168b56 (added lines and file paths)",
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
  "raw_runs": "evidence/var-scripts/runs.sh -> /data/work/var/out/var-2234-v1[-fwf] (not committed; logs copied to evidence/var-2234-v1/logs/)"
 }
}
```

## Files changed (1: 1 non-generated, 0 generated)
- tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs (+18 -0, test)

## Diff (non-generated files)
```diff
diff --git a/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs b/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs
index d39d74ef..4db3bfb7 100644
--- a/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs
+++ b/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs
@@ -124,6 +124,24 @@ public class Foo
         }.RunAsync();
     }
 
+    [Fact]
+    public async Task MissingKeyAttribute_SourceGenerationSuppressed()
+    {
+        string input = Preamble + @"
+[MessagePackObject(SuppressSourceGeneration = true)]
+public class Foo
+{
+    public string {|MsgPack004:Member1|} { get; set; }
+}
+";
+
+        await new VerifyCS.Test
+        {
+            TestCode = input,
+            MarkupOptions = MarkupOptions.UseFirstDescriptor,
+        }.RunAsync();
+    }
+
     /// <summary>
     /// Verifies that only public members require attributes (so long as no non-public member is already attributed.)
     /// </summary>

```

## File contents (line numbers in the gutter; quote the text after '| ')

### tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs at head (8c168b56), full file
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
  127|     [Fact]
  128|     public async Task MissingKeyAttribute_SourceGenerationSuppressed()
  129|     {
  130|         string input = Preamble + @"
  131| [MessagePackObject(SuppressSourceGeneration = true)]
  132| public class Foo
  133| {
  134|     public string {|MsgPack004:Member1|} { get; set; }
  135| }
  136| ";
  137| 
  138|         await new VerifyCS.Test
  139|         {
  140|             TestCode = input,
  141|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  142|         }.RunAsync();
  143|     }
  144| 
  145|     /// <summary>
  146|     /// Verifies that only public members require attributes (so long as no non-public member is already attributed.)
  147|     /// </summary>
  148|     [Fact]
  149|     public async Task AddAttributesToMembers_PublicOnly()
  150|     {
  151|         string input = Preamble + @"
  152| [MessagePackObject]
  153| public class Foo
  154| {
  155|     public string {|MsgPack004:Member1|} { get; set; }
  156|     internal string Member2 { get; set; }
  157| }
  158| ";
  159| 
  160|         string output = Preamble + @"
  161| [MessagePackObject]
  162| public class Foo
  163| {
  164|     [Key(0)]
  165|     public string Member1 { get; set; }
  166|     internal string Member2 { get; set; }
  167| }
  168| ";
  169| 
  170|         await new VerifyCS.Test
  171|         {
  172|             TestCode = input,
  173|             FixedCode = output,
  174|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  175|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  176|         }.RunAsync();
  177|     }
  178| 
  179|     /// <summary>
  180|     /// Verifies that all members require attributes if AllowPrivate = true is set on the attribute.
  181|     /// </summary>
  182|     [Fact]
  183|     public async Task AddAttributesToMembers_AllowPrivateAttribute()
  184|     {
  185|         string input = Preamble + @"
  186| [MessagePackObject(AllowPrivate = true)]
  187| public class Foo
  188| {
  189|     public string {|MsgPack004:Member1|} { get; set; }
  190|     internal string {|MsgPack004:Member2|} { get; set; }
  191| }
  192| ";
  193| 
  194|         string output = Preamble + @"
  195| [MessagePackObject(AllowPrivate = true)]
  196| public class Foo
  197| {
  198|     [Key(0)]
  199|     public string Member1 { get; set; }
  200|     [Key(1)]
  201|     internal string Member2 { get; set; }
  202| }
  203| ";
  204| 
  205|         await new VerifyCS.Test
  206|         {
  207|             TestCode = input,
  208|             FixedCode = output,
  209|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  210|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  211|         }.RunAsync();
  212|     }
  213| 
  214|     /// <summary>
  215|     /// Verifies that our annotated member analyzer automatically starts enforcing that
  216|     /// non-public members are annotated after the first non-public member is annotated.
  217|     /// </summary>
  218|     [Fact]
  219|     public async Task AddAttributesToMembers_MixedVisibility()
  220|     {
  221|         string input = Preamble + @"
  222| [{|MsgPack015:MessagePackObject|}]
  223| public class Foo
  224| {
  225|     private string {|MsgPack004:member4|};
  226|     [Key(0)]
  227|     public string Member1 { get; set; }
  228|     [Key(1)]
  229|     internal string Member2 { get; set; }
  230|     public string {|MsgPack004:Member3|} { get; set; }
  231| }
  232| ";
  233| 
  234|         string output = Preamble + @"
  235| [{|MsgPack015:MessagePackObject|}]
  236| public class {|MsgPack011:Foo|}
  237| {
  238|     [Key(2)]
  239|     private string member4;
  240|     [Key(0)]
  241|     public string Member1 { get; set; }
  242|     [Key(1)]
  243|     internal string Member2 { get; set; }
  244|     [Key(3)]
  245|     public string Member3 { get; set; }
  246| }
  247| ";
  248| 
  249|         await new VerifyCS.Test
  250|         {
  251|             TestCode = input,
  252|             FixedCode = output,
  253|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  254|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  255|         }.RunAsync();
  256|     }
  257| 
  258|     [Fact]
  259|     public async Task AddIgnoreAttributesToMembers()
  260|     {
  261|         string input = Preamble + @"
  262| [MessagePackObject]
  263| public class Foo
  264| {
  265|     public string {|MsgPack004:member1 = null|};
  266|     public string {|MsgPack004:member2 = null|};
  267|     [Key(0)]
  268|     public string Member3 { get; set; }
  269| }
  270| ";
  271| 
  272|         string output = Preamble + @"
  273| [MessagePackObject]
  274| public class Foo
  275| {
  276|     [IgnoreMember]
  277|     public string member1 = null;
  278|     [IgnoreMember]
  279|     public string member2 = null;
  280|     [Key(0)]
  281|     public string Member3 { get; set; }
  282| }
  283| ";
  284| 
  285|         await new VerifyCS.Test
  286|         {
  287|             TestCode = input,
  288|             FixedCode = output,
  289|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  290|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddIgnoreMemberAttributeEquivalenceKey,
  291|         }.RunAsync();
  292|     }
  293| 
  294|     [Fact]
  295|     public async Task AddAttributeToField_WithComment()
  296|     {
  297|         string input = Preamble + @"
  298| [MessagePackObject]
  299| public class Foo
  300| {
  301|     // comment
  302|     public string {|MsgPack004:Member1|};
  303| }
  304| ";
  305| 
  306|         string output = Preamble + @"
  307| [MessagePackObject]
  308| public class Foo
  309| {
  310|     // comment
  311|     [Key(0)]
  312|     public string Member1;
  313| }
  314| ";
  315| 
  316|         await new VerifyCS.Test
  317|         {
  318|             TestCode = input,
  319|             FixedCode = output,
  320|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  321|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  322|         }.RunAsync();
  323|     }
  324| 
  325|     [Fact]
  326|     public async Task AddAttributeToType_Properties()
  327|     {
  328|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  329|         string input = /* lang=c#-test */ """
  330|             public class Foo
  331|             {
  332|                 public string Member { get; set; }
  333|             }
  334| 
  335|             [MessagePack.MessagePackObject]
  336|             public class Bar
  337|             {
  338|                 [MessagePack.Key(0)]
  339|                 public Foo {|MsgPack003:Member|} { get; set; }
  340|             }
  341|             """;
  342| 
  343|         string output = /* lang=c#-test */ """
  344|             [MessagePack.MessagePackObject]
  345|             public class Foo
  346|             {
  347|                 [MessagePack.Key(0)]
  348|                 public string Member { get; set; }
  349|             }
  350| 
  351|             [MessagePack.MessagePackObject]
  352|             public class Bar
  353|             {
  354|                 [MessagePack.Key(0)]
  355|                 public Foo Member { get; set; }
  356|             }
  357|             """;
  358| 
  359|         await new VerifyCS.Test
  360|         {
  361|             TestCode = input,
  362|             FixedCode = output,
  363|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  364|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  365|         }.RunAsync();
  366|     }
  367| 
  368|     [Fact]
  369|     public async Task AddAttributeToType_Fields()
  370|     {
  371|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  372|         string input = /* lang=c#-test */ """
  373|             public class Foo
  374|             {
  375|                 public string Member;
  376|             }
  377| 
  378|             [MessagePack.MessagePackObject]
  379|             public class Bar
  380|             {
  381|                 [MessagePack.Key(0)]
  382|                 public Foo {|MsgPack003:Member|};
  383|             }
  384|             """;
  385| 
  386|         string output = /* lang=c#-test */ """
  387|             [MessagePack.MessagePackObject]
  388|             public class Foo
  389|             {
  390|                 [MessagePack.Key(0)]
  391|                 public string Member;
  392|             }
  393| 
  394|             [MessagePack.MessagePackObject]
  395|             public class Bar
  396|             {
  397|                 [MessagePack.Key(0)]
  398|                 public Foo Member;
  399|             }
  400|             """;
  401| 
  402|         await new VerifyCS.Test
  403|         {
  404|             TestCode = input,
  405|             FixedCode = output,
  406|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  407|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  408|         }.RunAsync();
  409|     }
  410| 
  411|     [Fact]
  412|     public async Task AddAttributeToType_Nullable()
  413|     {
  414|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  415|         string input = /* lang=c#-test */ """
  416|             public struct Foo
  417|             {
  418|                 public string Member;
  419|             }
  420| 
  421|             [MessagePack.MessagePackObject]
  422|             public class Bar
  423|             {
  424|                 [MessagePack.Key(0)]
  425|                 public Foo? {|MsgPack003:Member|};
  426|             }
  427|             """;
  428| 
  429|         string output = /* lang=c#-test */ """
  430|             [MessagePack.MessagePackObject]
  431|             public struct Foo
  432|             {
  433|                 [MessagePack.Key(0)]
  434|                 public string Member;
  435|             }
  436| 
  437|             [MessagePack.MessagePackObject]
  438|             public class Bar
  439|             {
  440|                 [MessagePack.Key(0)]
  441|                 public Foo? Member;
  442|             }
  443|             """;
  444| 
  445|         await new VerifyCS.Test
  446|         {
  447|             TestCode = input,
  448|             FixedCode = output,
  449|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  450|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  451|         }.RunAsync();
  452|     }
  453| 
  454|     [Fact]
  455|     public async Task AddAttributeToType_Generic()
  456|     {
  457|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  458|         string input = /* lang=c#-test */ """
  459|             public struct Foo
  460|             {
  461|                 public string Member;
  462|             }
  463| 
  464|             [MessagePack.MessagePackObject]
  465|             public class Bar
  466|             {
  467|                 [MessagePack.Key(0)]
  468|                 public System.Collections.Generic.List<Foo> {|MsgPack003:Member|};
  469|             }
  470|             """;
  471| 
  472|         string output = /* lang=c#-test */ """
  473|             [MessagePack.MessagePackObject]
  474|             public struct Foo
  475|             {
  476|                 [MessagePack.Key(0)]
  477|                 public string Member;
  478|             }
  479| 
  480|             [MessagePack.MessagePackObject]
  481|             public class Bar
  482|             {
  483|                 [MessagePack.Key(0)]
  484|                 public System.Collections.Generic.List<Foo> Member;
  485|             }
  486|             """;
  487| 
  488|         await new VerifyCS.Test
  489|         {
  490|             TestCode = input,
  491|             FixedCode = output,
  492|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  493|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  494|         }.RunAsync();
  495|     }
  496| 
  497|     [Fact]
  498|     public async Task AddAttributeToTypeForRecord1()
  499|     {
  500|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  501|         string input = @"
  502| public class Foo
  503| {
  504|     public string Member { get; set; }
  505| }
  506| 
  507| [MessagePack.MessagePackObject]
  508| public record Bar
  509| {
  510|     [MessagePack.Key(0)]
  511|     public Foo {|MsgPack003:Member|} { get; set; }
  512| }
  513| ";
  514| 
  515|         string output = @"
  516| [MessagePack.MessagePackObject]
  517| public class Foo
  518| {
  519|     [MessagePack.Key(0)]
  520|     public string Member { get; set; }
  521| }
  522| 
  523| [MessagePack.MessagePackObject]
  524| public record Bar
  525| {
  526|     [MessagePack.Key(0)]
  527|     public Foo Member { get; set; }
  528| }
  529| ";
  530| 
  531|         await new VerifyCS.Test
  532|         {
  533|             TestCode = input,
  534|             FixedCode = output,
  535|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  536|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  537|         }.RunAsync();
  538|     }
  539| 
  540|     [Fact]
  541|     public async Task AddAttributeToTypeForRecord2()
  542|     {
  543|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  544|         string input = @"
  545| public record Foo
  546| {
  547|     public string Member { get; set; }
  548| }
  549| 
  550| [MessagePack.MessagePackObject]
  551| public record Bar
  552| {
  553|     [MessagePack.Key(0)]
  554|     public Foo {|MsgPack003:Member|} { get; set; }
  555| }
  556| ";
  557| 
  558|         string output = @"
  559| [MessagePack.MessagePackObject]
  560| public record Foo
  561| {
  562|     [MessagePack.Key(0)]
  563|     public string Member { get; set; }
  564| }
  565| 
  566| [MessagePack.MessagePackObject]
  567| public record Bar
  568| {
  569|     [MessagePack.Key(0)]
  570|     public Foo Member { get; set; }
  571| }
  572| ";
  573| 
  574|         await new VerifyCS.Test
  575|         {
  576|             TestCode = input,
  577|             FixedCode = output,
  578|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  579|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  580|         }.RunAsync();
  581|     }
  582| 
  583|     [Fact]
  584|     public async Task AddAttributeToTypeForRecordPrimaryConstructor()
  585|     {
  586|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  587|         string input = @"
  588| public class Foo
  589| {
  590|     public string Member { get; set; }
  591| }
  592| 
  593| [MessagePack.MessagePackObject]
  594| public record Bar([property: MessagePack.Key(0)] Foo {|MsgPack003:Member|});
  595| 
  596| namespace System.Runtime.CompilerServices
  597| {
  598|     internal static class IsExternalInit
  599|     {
  600|     }
  601| }
  602| ";
  603| 
  604|         string output = @"
  605| [MessagePack.MessagePackObject]
  606| public class Foo
  607| {
  608|     [MessagePack.Key(0)]
  609|     public string Member { get; set; }
  610| }
  611| 
  612| [MessagePack.MessagePackObject]
  613| public record Bar([property: MessagePack.Key(0)] Foo Member);
  614| 
  615| namespace System.Runtime.CompilerServices
  616| {
  617|     internal static class IsExternalInit
  618|     {
  619|     }
  620| }
  621| ";
  622| 
  623|         await new VerifyCS.Test
  624|         {
  625|             TestCode = input,
  626|             FixedCode = output,
  627|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  628|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  629|         }.RunAsync();
  630|     }
  631| 
  632|     [Fact]
  633|     public async Task CodeFixAppliesAcrossFiles()
  634|     {
  635|         string source1 = @"
  636| public class Foo
  637| {
  638|     public int Member1 { get; set; }
  639| }
  640| ";
  641| 
  642|         string source2 = @"using MessagePack;
  643| 
  644| [MessagePackObject]
  645| public class Bar : {|MsgPack004:Foo|}
  646| {
  647|     public int {|MsgPack004:Member2|} { get; set; }
  648| }
  649| ";
  650| 
  651|         string output1 = @"
  652| public class Foo
  653| {
  654|     [MessagePack.Key(1)]
  655|     public int Member1 { get; set; }
  656| }
  657| ";
  658|         string output2 = @"using MessagePack;
  659| 
  660| [MessagePackObject]
  661| public class Bar : Foo
  662| {
  663|     [Key(0)]
  664|     public int Member2 { get; set; }
  665| }
  666| ";
  667| 
  668|         await new VerifyCS.Test(ReferencesSet.MessagePackAnnotations)
  669|         {
  670|             CodeFixTestBehaviors = CodeFixTestBehaviors.SkipLocalDiagnosticCheck, // BUGBUG: move diagnostic to `Foo` reference in Bar's base type list.
  671|             TestState =
  672|             {
  673|                 Sources = { source1, source2 },
  674|             },
  675|             FixedState =
  676|             {
  677|                 Sources = { output1, output2 },
  678|             },
  679|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  680|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  681|         }.RunAsync();
  682|     }
  683| 
  684|     [Fact]
  685|     public async Task AddAttributeToGenericType()
  686|     {
  687|         string input = Preamble + /* lang=c#-test */ """
  688|             public class Foo<T>
  689|             {
  690|                 public T Member { get; set; }
  691|             }
  692| 
  693|             [MessagePackObject]
  694|             public class Bar
  695|             {
  696|                 [Key(0)]
  697|                 public Foo<int> {|MsgPack003:MemberUserGeneric|} { get; set; }
  698| 
  699|                 [Key(1)]
  700|                 public System.Collections.Generic.List<int> MemberKnownGeneric { get; set; }
  701|             }
  702|             """;
  703| 
  704|         string output = Preamble + /* lang=c#-test */ """
  705| 
  706|             [MessagePackObject]
  707|             public class Foo<T>
  708|             {
  709|                 [Key(0)]
  710|                 public T Member { get; set; }
  711|             }
  712| 
  713|             [MessagePackObject]
  714|             public class Bar
  715|             {
  716|                 [Key(0)]
  717|                 public Foo<int> MemberUserGeneric { get; set; }
  718| 
  719|                 [Key(1)]
  720|                 public System.Collections.Generic.List<int> MemberKnownGeneric { get; set; }
  721|             }
  722|             """;
  723| 
  724|         await new VerifyCS.Test
  725|         {
  726|             TestCode = input,
  727|             FixedCode = output,
  728|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  729|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  730|         }.RunAsync();
  731|     }
  732| 
  733|     [Fact]
  734|     public async Task AddAttributesToMembersOfRecord()
  735|     {
  736|         string input = Preamble + /* lang=c#-test */ """
  737|             [MessagePackObject]
  738|             public record Foo
  739|             {
  740|                 public string {|MsgPack004:Member1|} { get; set; }
  741|                 public string {|MsgPack004:Member2|} { get; set; }
  742|             }
  743|             """;
  744| 
  745|         string output = Preamble + /* lang=c#-test */ """
  746|             [MessagePackObject]
  747|             public record Foo
  748|             {
  749|                 [Key(0)]
  750|                 public string Member1 { get; set; }
  751|                 [Key(1)]
  752|                 public string Member2 { get; set; }
  753|             }
  754|             """;
  755|         await new VerifyCS.Test
  756|         {
  757|             ReferenceAssemblies = ReferenceAssemblies.Net.Net60,
  758|             CompilerDiagnostics = CompilerDiagnostics.Errors,
  759|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  760|             SolutionTransforms =
  761|             {
  762|                 static (solution, projectId) =>
  763|                 {
  764|                     return solution.WithProjectParseOptions(projectId, new CSharpParseOptions(languageVersion: LanguageVersion.CSharp11));
  765|                 },
  766|             },
  767|             TestCode = input,
  768|             FixedCode = output,
  769|         }.RunAsync();
  770|     }
  771| 
  772|     [Fact]
  773|     public async Task AddAttributesToMembersOfRecordStruct()
  774|     {
  775|         string input = Preamble + /* lang=c#-test */ """
  776|             [MessagePackObject]
  777|             public record struct Foo
  778|             {
  779|                 public string {|MsgPack004:Member1|} { get; set; }
  780|                 public string {|MsgPack004:Member2|} { get; set; }
  781|             }
  782|             """;
  783| 
  784|         string output = Preamble + /* lang=c#-test */ """
  785|             [MessagePackObject]
  786|             public record struct Foo
  787|             {
  788|                 [Key(0)]
  789|                 public string Member1 { get; set; }
  790|                 [Key(1)]
  791|                 public string Member2 { get; set; }
  792|             }
  793|             """;
  794|         await new VerifyCS.Test
  795|         {
  796|             ReferenceAssemblies = ReferenceAssemblies.Net.Net60,
  797|             CompilerDiagnostics = CompilerDiagnostics.Errors,
  798|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  799|             SolutionTransforms =
  800|             {
  801|                 static (solution, projectId) =>
  802|                 {
  803|                     return solution.WithProjectParseOptions(projectId, new CSharpParseOptions(languageVersion: LanguageVersion.CSharp11));
  804|                 },
  805|             },
  806|             TestCode = input,
  807|             FixedCode = output,
  808|         }.RunAsync();
  809|     }
  810| 
  811|     [Fact]
  812|     public async Task AddAttributesToMembersOfRecordWithPrimaryCtor()
  813|     {
  814|         string input = Preamble + /* lang=c#-test */ """
  815|             [MessagePackObject]
  816|             public record {|MsgPack007:Foo|}(
  817|                 string {|MsgPack004:Member1|},
  818|                 string {|MsgPack004:Member2|});
  819|             """;
  820| 
  821|         string output = Preamble + /* lang=c#-test */ """
  822|             [MessagePackObject]
  823|             public record Foo(
  824|                 [property: Key(0)] string Member1,
  825|                 [property: Key(1)] string Member2);
  826|             """;
  827| 
  828|         await new VerifyCS.Test
  829|         {
  830|             ReferenceAssemblies = ReferenceAssemblies.Net.Net60,
  831|             CompilerDiagnostics = CompilerDiagnostics.Errors,
  832|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  833|             SolutionTransforms =
  834|             {
  835|                 static (solution, projectId) =>
  836|                 {
  837|                     return solution.WithProjectParseOptions(projectId, new CSharpParseOptions(languageVersion: LanguageVersion.CSharp11));
  838|                 },
  839|             },
  840|             TestCode = input,
  841|             FixedCode = output,
  842|         }.RunAsync();
  843|     }
  844| 
  845|     [Fact]
  846|     public async Task AddAttributesToMembersOfRecordStructWithPrimaryCtor()
  847|     {
  848|         string input = Preamble + /* lang=c#-test */ """
  849|             [MessagePackObject]
  850|             public record struct Foo(
  851|                 string {|MsgPack004:Member1|},
  852|                 string {|MsgPack004:Member2|});
  853|             """;
  854| 
  855|         string output = Preamble + /* lang=c#-test */ """
  856|             [MessagePackObject]
  857|             public record struct Foo(
  858|                 [property: Key(0)] string Member1,
  859|                 [property: Key(1)] string Member2);
  860|             """;
  861| 
  862|         await new VerifyCS.Test
  863|         {
  864|             ReferenceAssemblies = ReferenceAssemblies.Net.Net60,
  865|             CompilerDiagnostics = CompilerDiagnostics.Errors,
  866|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  867|             SolutionTransforms =
  868|             {
  869|                 static (solution, projectId) =>
  870|                 {
  871|                     return solution.WithProjectParseOptions(projectId, new CSharpParseOptions(languageVersion: LanguageVersion.CSharp11));
  872|                 },
  873|             },
  874|             TestCode = input,
  875|             FixedCode = output,
  876|         }.RunAsync();
  877|     }
  878| 
  879|     [Fact]
  880|     public async Task DoNotAddAttributesToClassWithPrimaryCtor()
  881|     {
  882|         string input = Preamble + /* lang=c#-test */ """
  883|             [MessagePackObject]
  884|             public class {|MsgPack007:Foo|}(
  885|                 string Member1,
  886|                 string Member2);
  887|             """;
  888| 
  889|         string output = Preamble + /* lang=c#-test */ """
  890|             [MessagePackObject]
  891|             public class {|MsgPack007:Foo|}(
  892|                 string Member1,
  893|                 string Member2);
  894|             """;
  895| 
  896|         await new VerifyCS.Test
  897|         {
  898|             ReferenceAssemblies = ReferenceAssemblies.Net.Net60,
  899|             CompilerDiagnostics = CompilerDiagnostics.Errors,
  900|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  901|             SolutionTransforms =
  902|             {
  903|                 static (solution, projectId) =>
  904|                 {
  905|                     return solution.WithProjectParseOptions(projectId, new CSharpParseOptions(languageVersion: LanguageVersion.CSharp12));
  906|                 },
  907|             },
  908|             TestCode = input,
  909|             FixedCode = output,
  910|         }.RunAsync();
  911|     }
  912| 
  913|     [Fact]
  914|     public async Task DerivedAttributes()
  915|     {
  916|         string test = /* lang=c#-test */ """
  917|             using MessagePack;
  918| 
  919|             [MessagePackObject]
  920|             public class A
  921|             {
  922|                 [{|MsgPack016:CompositeKey(0, 1)|}]
  923|                 public string Prop1 { get; set; }
  924| 
  925|                 [{|MsgPack016:CompositeKey(0, 2)|}]
  926|                 public string Field2;
  927|             }
  928| 
  929|             [MessagePackObject]
  930|             public class B : {|MsgPack016:A|}
  931|             {
  932|                 [{|MsgPack016:CompositeKey(1, 1)|}]
  933|                 public string Prop3 { get; set; }
  934| 
  935|                 [{|MsgPack016:CompositeKey(1, 2)|}]
  936|                 public string Field4;
  937|             }
  938| 
  939|             public class CompositeKeyAttribute : KeyAttribute
  940|             {
  941|                 public CompositeKeyAttribute(byte level, int index)
  942|                     : base(CreateKey(level, index)) { }
  943| 
  944|                 public static string CreateKey(byte level, int index)
  945|                 {
  946|                     var c = (char)('A' + level);
  947|                     return c + index.ToString("x");
  948|                 }
  949|             }
  950|             """;
  951| 
  952|         await VerifyCS.VerifyAnalyzerAsync(test);
  953|     }
  954| 
  955|     [Fact]
  956|     public async Task DerivedAttributes_SourceGenerationDisabled()
  957|     {
  958|         string test = /* lang=c#-test */ """
  959|             using MessagePack;
  960| 
  961|             [MessagePackObject(SuppressSourceGeneration = true)]
  962|             public class A
  963|             {
  964|                 [CompositeKey(0, 1)]
  965|                 public string Prop1 { get; set; }
  966| 
  967|                 [CompositeKey(0, 2)]
  968|                 public string Field2;
  969|             }
  970| 
  971|             [MessagePackObject(SuppressSourceGeneration = true)]
  972|             public class B : A
  973|             {
  974|                 [CompositeKey(1, 1)]
  975|                 public string Prop3 { get; set; }
  976| 
  977|                 [CompositeKey(1, 2)]
  978|                 public string Field4;
  979|             }
  980| 
  981|             public class CompositeKeyAttribute : KeyAttribute
  982|             {
  983|                 public CompositeKeyAttribute(byte level, int index)
  984|                     : base(CreateKey(level, index)) { }
  985| 
  986|                 public static string CreateKey(byte level, int index)
  987|                 {
  988|                     var c = (char)('A' + level);
  989|                     return c + index.ToString("x");
  990|                 }
  991|             }
  992|             """;
  993| 
  994|         await VerifyCS.VerifyAnalyzerAsync(test);
  995|     }
  996| 
  997|     [Fact]
  998|     public async Task InitPropertyInitializer()
  999|     {
 1000|         string test = /* lang=c#-test */ """
 1001|             using MessagePack;
 1002| 
 1003|             [MessagePackObject]
 1004|             public class A
 1005|             {
 1006|                 [Key(0)]
 1007|                 public string Prop1 { get; init; } {|MsgPack017:= "some default"|};
 1008| 
 1009|                 [Key(1)]
 1010|                 public string Prop2 { get; set; } = "some default";
 1011|             }
 1012| 
 1013| 
 1014|             [MessagePackObject(SuppressSourceGeneration = true)]
 1015|             public class B
 1016|             {
 1017|                 [Key(0)]
 1018|                 public string Prop1 { get; init; } = "some default";
 1019| 
 1020|                 [Key(1)]
 1021|                 public string Prop2 { get; set; } = "some default";
 1022|             }
 1023|             """;
 1024| 
 1025|         await VerifyCS.VerifyAnalyzerAsync(test);
 1026|     }
 1027| 
 1028|     [Fact]
 1029|     public async Task PrivateMembersInBaseClassNeedNoAttribution()
 1030|     {
 1031|         string test = /* lang=c#-test */ """
 1032|             using MessagePack;
 1033| 
 1034|             [MessagePackObject]
 1035|             public class A
 1036|             {
 1037|                 private int somePrivateField;
 1038| 
 1039|                 [Key(0)]
 1040|                 public int SomePublicProp { get; set; }
 1041| 
 1042|                 private int SomePrivateProp { get; set; }
 1043|             }
 1044| 
 1045|             [MessagePackObject]
 1046|             public class B : A
 1047|             {
 1048|                 [Key(1)]
 1049|                 public int SomePublicProp2 { get; set; }
 1050|             }
 1051|             """;
 1052| 
 1053|         await VerifyCS.VerifyAnalyzerAsync(test);
 1054|     }
 1055| 
 1056|     [Fact]
 1057|     public async Task NameCollisionsInForceMapMode()
 1058|     {
 1059|         string test = /* lang=c#-test */ """
 1060|             using MessagePack;
 1061| 
 1062|             [MessagePackObject(true)]
 1063|             public class Base
 1064|             {
 1065|                 public string Prop { get; set; }
 1066| 
 1067|                 public string Field;
 1068| 
 1069|                 public string TwoFaced { get; set; } // derived declares a *field* by the same name.
 1070|             }
 1071| 
 1072|             [MessagePackObject(true)]
 1073|             public class Derived : Base
 1074|             {
 1075|                 public new string {|MsgPack018:Prop|} { get; set; }
 1076| 
 1077|                 public new string {|MsgPack018:Field|};
 1078| 
 1079|                 public new string {|MsgPack018:TwoFaced|};
 1080|             }
 1081|             """;
 1082| 
 1083|         await VerifyCS.VerifyAnalyzerAsync(test);
 1084|     }
 1085| 
 1086|     [Fact]
 1087|     public async Task AbstractFormatterDoesNotAttractAttention()
 1088|     {
 1089|         string test = /* lang=c#-test */ """
 1090|             using MessagePack;
 1091|             using MessagePack.Formatters;
 1092| 
 1093|             public abstract class AbstractFormatter1 : IMessagePackFormatter<object>
 1094|             {
 1095|                 public abstract void Serialize(ref MessagePackWriter writer, object value, MessagePackSerializerOptions options);
 1096|                 public abstract object Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options);
 1097|             }
 1098| 
 1099|             public abstract class AbstractFormatter2 : IMessagePackFormatter<object>
 1100|             {
 1101|                 public abstract void Serialize(ref MessagePackWriter writer, object value, MessagePackSerializerOptions options);
 1102|                 public abstract object Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options);
 1103|             }
 1104|             """;
 1105| 
 1106|         await VerifyCS.VerifyAnalyzerAsync(test);
 1107|     }
 1108| }
```

## What you did NOT get (refuse anything that depends on it)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)

Return only the JSON object described in the brief.