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

## Refuse rather than guess

- If you cannot establish a clause from what you were given, the verdict is `cannot_determine`, with the reason in
  `confidence_basis`.
- Anything you will not decide (not given the code, needs runtime behaviour, other target frameworks, performance,
  security judgement beyond the evidence, generated files you did not see) goes in `refusals` with who should decide.
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
    {"topic": "what you will not decide", "reason": "why", "who_should_decide": "role, e.g. area owner"}
  ]
}
```

One verdict per requirement clause, in the order given. Severity: `blocker` = must not merge; `major` = needs a fix
or an owner's explicit acceptance; `minor` = should fix; `info` = observation. Do not add fields for reviewer name,
model, vendor or time: the runner stamps those.


<!-- user message -->
# Change up-2022: branch upstream PR #2022, base f5e104eec56d53df064126de8dd5bd4e533e7ea8, head 5f4b762a00b7f21940c2b737498205481b725156
Commit message: Ignore abstract implementations of `IMessagePackFormatter<T>`

Fixes #2017
Upstream issue: https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2017

## Requirement set (requirements/up-2022.yaml)
```yaml
# PLACEHOLDER derived from upstream issue #2017, for upstream PR #2022 (a merged, human-written upstream change used as a
# low-risk control: does the pipeline clear what it should?). Not a Tieto requirement set.
change: "up-2022"
branch: upstream PR #2022 (merge e88df8a7; base = merge^1 f5e104ee, head = merge^2 5f4b762a)
source: https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2017
pull_request: https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2022
official: false
requirements:
  - id: REQ-up-2022-F1
    type: functional
    text: "The analyzer must not report MsgPack013 (formatter has no accessible instance for the source generated resolver) for an abstract class that implements IMessagePackFormatter<T>."
  - id: REQ-up-2022-F2
    type: functional
    text: "Abstract implementations of IMessagePackFormatter<T> must not be counted as formatters, so they cannot cause MsgPack009 (more than one formatter for the same type)."
  - id: REQ-up-2022-N1
    type: non-functional
    checks: [tests.fail_without_fix]
    text: "The fix is covered by automated tests that fail without it."
  - id: REQ-up-2022-N2
    type: non-functional
    checks: [tests.full_suite]
    text: "Non-abstract formatters are still discovered and diagnosed as before (no regressions in the existing test suite)."
```

## facts.json (deterministic checks; cite their ids and test names)
```json
{
 "change": "up-2022",
 "branch": "upstream PR #2022",
 "base": "f5e104ee",
 "head": "5f4b762a",
 "base_full": "f5e104eec56d53df064126de8dd5bd4e533e7ea8",
 "head_full": "5f4b762a00b7f21940c2b737498205481b725156",
 "commit_message": "Ignore abstract implementations of `IMessagePackFormatter<T>`\n\nFixes #2017",
 "author": "Andrew Arnott",
 "agent_written": false,
 "upstream": {
  "pull_request": "https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/2022",
  "issue": "https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2017",
  "merge_commit": "e88df8a75dcfe186e31a9217192d93f667d720b8",
  "merged_into": "develop",
  "merged_at": "2024-10-18T17:13:31-06:00",
  "base_rule": "base = merge commit first parent (develop before the merge)",
  "head_rule": "head = merge commit second parent (PR branch tip); git diff base..head == git diff base..merge (asserted)",
  "control": "source fix + test; merged upstream, human-written, not reverted or fixed later as far as checked (measurement/history/candidates.json has no entry for it; later history of the changed lines read by hand)"
 },
 "diff": {
  "files": 2,
  "insertions": 29,
  "deletions": 0,
  "by_kind": {
   "source": 1,
   "test": 1
  },
  "by_file": [
   {
    "path": "src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs",
    "ins": 6,
    "del": 0,
    "kind": "source"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs",
    "ins": 23,
    "del": 0,
    "kind": "test"
   }
  ]
 },
 "new_tests_in_diff": [
  "MsgPack00xAnalyzerTests.AbstractFormatterDoesNotAttractAttention"
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
   "log": "evidence/up-2022/logs/build.log",
   "duration_s": 5.0
  },
  {
   "id": "tests.targeted",
   "tool": "dotnet test",
   "tool_version": "8.0.402",
   "status": "pass",
   "summary": "26 passed, 0 failed, 0 skipped (1 new tests in run)",
   "tests": [
    {
     "name": "MsgPack00xAnalyzerTests.AbstractFormatterDoesNotAttractAttention",
     "outcome": "passed",
     "new": true
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
     "name": "MsgPack00xAnalyzerTests.AddAttributeToType",
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
    }
   ],
   "log": "evidence/up-2022/logs/tests_targeted.1.log",
   "duration_s": 3.0,
   "filter": [
    "FullyQualifiedName~MsgPack00xAnalyzerTests."
   ],
   "project": "tests/MessagePack.SourceGenerator.Tests",
   "on_base": "same filter on base: 25 passed, 0 failed of 25"
  },
  {
   "id": "tests.fail_without_fix",
   "tool": "dotnet test (source reverted, tests kept)",
   "tool_version": "8.0.402",
   "status": "pass",
   "summary": "new tests fail on base source: 1/1 failed -> tests do cover the change",
   "tests": [
    {
     "name": "MsgPack00xAnalyzerTests.AbstractFormatterDoesNotAttractAttention",
     "outcome": "failed",
     "new": true,
     "error": "System.InvalidOperationException : Context: Diagnostics of test state\nMismatch between number of diagnostics returned, expected \"0\" actual \"4\"\r\n\r\nDiagnostics:\r\n// /0/Test0.cs(4,23): error MsgPack009: Multiple formatters for type System.Object found\nVerifyCS.Diagnostic(MsgPack00xMessagePackAnalyzer.MsgPack009).WithSpan(4, 23, 4, 41).WithArguments(\"System.Object\"),\n// /0/Test0.cs(4,23): warning MsgP [...]"
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
     "name": "MsgPack00xAnalyzerTests.AddAttributeToType",
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
    }
   ],
   "log": "evidence/up-2022/logs/tests_fail_without_fix.1.log",
   "duration_s": 4.0,
   "reverted_files": [
    "src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs"
   ],
   "full_suite_with_source_reverted": {
    "total": 150,
    "failed": 1,
    "failed_tests": [
     "MsgPack00xAnalyzerTests.AbstractFormatterDoesNotAttractAttention"
    ],
    "log": "evidence/up-2022/logs/fail_without_fix.full_suite.log"
   },
   "new_failed": 1,
   "new_total": 1
  },
  {
   "id": "tests.full_suite",
   "tool": "dotnet test",
   "tool_version": "8.0.402",
   "status": "pass",
   "summary": "tests/MessagePack.SourceGenerator.Tests: 150 tests, 150 passed, 0 failed (0 not failing on base, 0 also failing on base)",
   "project": "tests/MessagePack.SourceGenerator.Tests",
   "total": 150,
   "passed": 150,
   "failed": 0,
   "failures_not_on_base": [],
   "failures_also_on_base": [],
   "log": "evidence/up-2022/logs/tests_full_suite.log",
   "duration_s": 7.0,
   "base_total": 149,
   "base_passed": 149
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
  "max_cpu": 8
 }
}
```

## Files changed (2: 2 non-generated, 0 generated)
- src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs (+6 -0, source)
- tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs (+23 -0, test)

## Diff (non-generated files)
```diff
diff --git a/src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs b/src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs
index 4d8567fe..4832023e 100644
--- a/src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs
+++ b/src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs
@@ -218,6 +218,12 @@ public record FormatterDescriptor(QualifiedNamedTypeName Name, string? InstanceP
     /// <returns><see langword="true"/> if <paramref name="type"/> represents a formatter.</returns>
     public static bool TryCreate(INamedTypeSymbol type, [NotNullWhen(true)] out FormatterDescriptor? formatter)
     {
+        if (type.IsAbstract)
+        {
+            formatter = null;
+            return false;
+        }
+
         var formattedTypes =
             AnalyzerUtilities.SearchTypeForFormatterImplementations(type)
             .Select(i => new FormattableType(i, type.ContainingAssembly))

diff --git a/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs b/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs
index 54d8dda0..b35682b7 100644
--- a/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs
+++ b/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs
@@ -908,4 +908,27 @@ public class Bar : Foo
 
         await VerifyCS.VerifyAnalyzerAsync(test);
     }
+
+    [Fact]
+    public async Task AbstractFormatterDoesNotAttractAttention()
+    {
+        string test = /* lang=c#-test */ """
+            using MessagePack;
+            using MessagePack.Formatters;
+
+            public abstract class AbstractFormatter1 : IMessagePackFormatter<object>
+            {
+                public abstract void Serialize(ref MessagePackWriter writer, object value, MessagePackSerializerOptions options);
+                public abstract object Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options);
+            }
+
+            public abstract class AbstractFormatter2 : IMessagePackFormatter<object>
+            {
+                public abstract void Serialize(ref MessagePackWriter writer, object value, MessagePackSerializerOptions options);
+                public abstract object Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options);
+            }
+            """;
+
+        await VerifyCS.VerifyAnalyzerAsync(test);
+    }
 }

```

## File contents (line numbers in the gutter; quote the text after '| ')

### src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs at head (5f4b762a), full file
```
    1| ﻿// Copyright (c) All contributors. All rights reserved.
    2| // Licensed under the MIT license. See LICENSE file in the project root for full license information.
    3| 
    4| #pragma warning disable SA1402 // File may only contain a single type
    5| 
    6| using System.Collections.Immutable;
    7| using System.Diagnostics.CodeAnalysis;
    8| using Microsoft.CodeAnalysis;
    9| 
   10| namespace MessagePack.SourceGenerator.CodeAnalysis;
   11| 
   12| /// <summary>
   13| /// Options for the analyzer and source generator.
   14| /// </summary>
   15| /// <remarks>
   16| /// These options are typically gathered from attributes in the compilation.
   17| /// </remarks>
   18| public record AnalyzerOptions
   19| {
   20|     private readonly ImmutableHashSet<FormatterDescriptor> knownFormatters = ImmutableHashSet<FormatterDescriptor>.Empty;
   21| 
   22|     private readonly ImmutableDictionary<QualifiedTypeName, ImmutableArray<FormattableType>> collidingFormatters = ImmutableDictionary<QualifiedTypeName, ImmutableArray<FormattableType>>.Empty;
   23| 
   24|     /// <summary>
   25|     /// Gets the set fully qualified names of types that are assumed to have custom formatters written that will be included by a resolver by the program.
   26|     /// </summary>
   27|     public ImmutableHashSet<FormattableType> AssumedFormattableTypes { get; init; } = ImmutableHashSet<FormattableType>.Empty;
   28| 
   29|     /// <summary>
   30|     /// Gets the set of custom formatters that should be considered by the analyzer and included in the generated resolver.
   31|     /// </summary>
   32|     public ImmutableHashSet<FormatterDescriptor> KnownFormatters
   33|     {
   34|         get => this.knownFormatters;
   35|         init
   36|         {
   37|             this.knownFormatters = value;
   38|             this.KnownFormattersByName = value.ToImmutableDictionary(f => f.Name);
   39| 
   40|             Dictionary<FormattableType, ImmutableArray<FormatterDescriptor>> formattableTypes = new();
   41|             bool collisionsEncountered = false;
   42|             foreach (FormatterDescriptor formatter in value)
   43|             {
   44|                 if (formatter.ExcludeFromSourceGeneratedResolver)
   45|                 {
   46|                     continue;
   47|                 }
   48| 
   49|                 foreach (FormattableType dataType in formatter.FormattableTypes)
   50|                 {
   51|                     if (formattableTypes.ContainsKey(dataType))
   52|                     {
   53|                         formattableTypes[dataType] = formattableTypes[dataType].Add(formatter);
   54|                         collisionsEncountered = true;
   55|                     }
   56|                     else
   57|                     {
   58|                         formattableTypes.Add(dataType, ImmutableArray.Create(formatter));
   59|                     }
   60|                 }
   61|             }
   62| 
   63|             var collidingFormatters = ImmutableDictionary<QualifiedTypeName, ImmutableArray<FormattableType>>.Empty;
   64|             if (collisionsEncountered)
   65|             {
   66|                 foreach (KeyValuePair<FormattableType, ImmutableArray<FormatterDescriptor>> kvp in formattableTypes)
   67|                 {
   68|                     if (kvp.Value.Length > 1)
   69|                     {
   70|                         foreach (FormatterDescriptor collidingFormatter in kvp.Value)
   71|                         {
   72|                             if (collidingFormatters.TryGetValue(collidingFormatter.Name, out ImmutableArray<FormattableType> collidingTypes))
   73|                             {
   74|                                 collidingFormatters = collidingFormatters.SetItem(collidingFormatter.Name, collidingTypes.Add(kvp.Key));
   75|                             }
   76|                             else
   77|                             {
   78|                                 collidingFormatters = collidingFormatters.Add(collidingFormatter.Name, ImmutableArray.Create(kvp.Key));
   79|                             }
   80|                         }
   81|                     }
   82|                 }
   83|             }
   84| 
   85|             this.collidingFormatters = collidingFormatters;
   86|         }
   87|     }
   88| 
   89|     public ImmutableDictionary<QualifiedNamedTypeName, FormatterDescriptor> KnownFormattersByName { get; private init; } = ImmutableDictionary<QualifiedNamedTypeName, FormatterDescriptor>.Empty;
   90| 
   91|     public GeneratorOptions Generator { get; init; } = new();
   92| 
   93|     /// <summary>
   94|     /// Gets a value indicating whether the analyzer is generating source code.
   95|     /// </summary>
   96|     public bool IsGeneratingSource { get; init; }
   97| 
   98|     internal AnalyzerOptions WithFormatterTypes(ImmutableArray<FormattableType> formattableTypes, ImmutableHashSet<FormatterDescriptor> customFormatters)
   99|     {
  100|         return this with
  101|         {
  102|             AssumedFormattableTypes = ImmutableHashSet.CreateRange(formattableTypes).Union(customFormatters.SelectMany(t => t.FormattableTypes)),
  103|             KnownFormatters = customFormatters,
  104|         };
  105|     }
  106| 
  107|     /// <summary>
  108|     /// Modifies these options based on the attributes on the assembly being compiled.
  109|     /// </summary>
  110|     /// <param name="assemblyAttributes">The assembly-level attributes.</param>
  111|     /// <param name="cancellationToken">A cancellation token.</param>
  112|     /// <returns>The modified set of options.</returns>
  113|     internal AnalyzerOptions WithAssemblyAttributes(ImmutableArray<AttributeData> assemblyAttributes, CancellationToken cancellationToken)
  114|     {
  115|         ImmutableHashSet<FormatterDescriptor> customFormatters = AnalyzerUtilities.ParseKnownFormatterAttribute(assemblyAttributes, cancellationToken).Union(this.KnownFormatters);
  116|         ImmutableArray<FormattableType> customFormattedTypes = this.AssumedFormattableTypes.Union(AnalyzerUtilities.ParseAssumedFormattableAttribute(assemblyAttributes, cancellationToken)).ToImmutableArray();
  117|         return this.WithFormatterTypes(customFormattedTypes, customFormatters);
  118|     }
  119| 
  120|     internal ImmutableArray<FormattableType> GetCollidingFormatterDataTypes(QualifiedTypeName formatter) => this.collidingFormatters.GetValueOrDefault(formatter, ImmutableArray<FormattableType>.Empty);
  121| 
  122|     public virtual bool Equals(AnalyzerOptions? other)
  123|     {
  124|         if (other is null)
  125|         {
  126|             return false;
  127|         }
  128| 
  129|         if (ReferenceEquals(this, other))
  130|         {
  131|             return true;
  132|         }
  133| 
  134|         if (this.GetType() != other.GetType())
  135|         {
  136|             return false;
  137|         }
  138| 
  139|         return this.knownFormatters.SetEquals(other.knownFormatters)
  140|             && this.AssumedFormattableTypes.SetEquals(other.AssumedFormattableTypes)
  141|             && this.Generator.Equals(other.Generator)
  142|             && this.IsGeneratingSource == other.IsGeneratingSource;
  143|     }
  144| 
  145|     public override int GetHashCode()
  146|     {
  147|         int hashCode = 0;
  148| 
  149|         hashCode = Hash(hashCode, this.knownFormatters.Count);
  150|         hashCode = Hash(hashCode, this.AssumedFormattableTypes.Count);
  151|         hashCode = Hash(hashCode, this.Generator.GetHashCode());
  152| 
  153|         return hashCode;
  154| 
  155|         static int Hash(int hashCode, int value)
  156|         {
  157|             return (hashCode * 31) + value;
  158|         }
  159|     }
  160| }
  161| 
  162| /// <summary>
  163| /// Customizes aspects of source generated formatters.
  164| /// </summary>
  165| public record FormattersOptions
  166| {
  167|     /// <summary>
  168|     /// Gets a value indicating whether types will be serialized with their property names as well as their values in a key=value dictionary, as opposed to an array of values.
  169|     /// </summary>
  170|     public bool UsesMapMode { get; init; }
  171| }
  172| 
  173| /// <summary>
  174| /// Describes the generated resolver.
  175| /// </summary>
  176| public record ResolverOptions
  177| {
  178|     /// <summary>
  179|     /// Gets the name to use for the resolver.
  180|     /// </summary>
  181|     public QualifiedNamedTypeName Name { get; init; } = new(TypeKind.Class)
  182|     {
  183|         Container = new NamespaceTypeContainer("MessagePack"),
  184|         Name = "GeneratedMessagePackResolver",
  185|     };
  186| }
  187| 
  188| /// <summary>
  189| /// Customizes AOT source generation of formatters for custom types.
  190| /// </summary>
  191| public record GeneratorOptions
  192| {
  193|     /// <summary>
  194|     /// Gets options for the generated resolver.
  195|     /// </summary>
  196|     public ResolverOptions Resolver { get; init; } = new();
  197| 
  198|     /// <summary>
  199|     /// Gets options for the generated formatter.
  200|     /// </summary>
  201|     public FormattersOptions Formatters { get; init; } = new();
  202| }
  203| 
  204| /// <summary>
  205| /// Describes a custom formatter.
  206| /// </summary>
  207| /// <param name="Name">The name of the type that implements at least one <c>IMessagePackFormatter</c> interface. If the formatter is a generic type, this should <em>not</em> include any generic type parameters.</param>
  208| /// <param name="InstanceProvidingMember">Either ".ctor" or the name of a static field or property that will return an instance of the formatter.</param>
  209| /// <param name="InstanceTypeName">The type name to use when referring to an instance of the formatter. Usually the same as <paramref name="Name"/> but may be different if <paramref name="InstanceProvidingMember"/> returns a different type.</param>
  210| /// <param name="FormattableTypes">The type arguments that appear in each implemented <c>IMessagePackFormatter</c> interface. When generic, these should be the full name of their type definitions.</param>
  211| public record FormatterDescriptor(QualifiedNamedTypeName Name, string? InstanceProvidingMember, QualifiedTypeName InstanceTypeName, ImmutableHashSet<FormattableType> FormattableTypes)
  212| {
  213|     /// <summary>
  214|     /// Creates a descriptor for a formatter, if the given type implements at least one <c>IMessagePackFormatter</c> interface.
  215|     /// </summary>
  216|     /// <param name="type">The type symbol for the formatter.</param>
  217|     /// <param name="formatter">Receives the formatter descriptor, if applicable.</param>
  218|     /// <returns><see langword="true"/> if <paramref name="type"/> represents a formatter.</returns>
  219|     public static bool TryCreate(INamedTypeSymbol type, [NotNullWhen(true)] out FormatterDescriptor? formatter)
  220|     {
  221|         if (type.IsAbstract)
  222|         {
  223|             formatter = null;
  224|             return false;
  225|         }
  226| 
  227|         var formattedTypes =
  228|             AnalyzerUtilities.SearchTypeForFormatterImplementations(type)
  229|             .Select(i => new FormattableType(i, type.ContainingAssembly))
  230|             .ToImmutableHashSet();
  231|         if (formattedTypes.IsEmpty)
  232|         {
  233|             formatter = null;
  234|             return false;
  235|         }
  236| 
  237|         IFieldSymbol? instanceField = type.GetMembers("Instance").OfType<IFieldSymbol>()
  238|             .FirstOrDefault(m => m.IsStatic && m.DeclaredAccessibility == Accessibility.Public && m.IsReadOnly);
  239|         IMethodSymbol? ctor = type.InstanceConstructors.FirstOrDefault(ctor => ctor.Parameters.Length == 0 && ctor.DeclaredAccessibility >= Accessibility.Internal);
  240|         string? instanceProvidingMember = instanceField?.Name ?? ctor?.Name ?? null;
  241|         QualifiedTypeName instanceTypeName = QualifiedTypeName.Create(instanceField?.Type ?? type);
  242| 
  243|         formatter = new FormatterDescriptor(new QualifiedNamedTypeName(type), instanceProvidingMember, instanceTypeName, formattedTypes)
  244|         {
  245|             InaccessibleDescriptor =
  246|                 CodeAnalysisUtilities.FindInaccessibleTypes(type).Any() ? MsgPack00xMessagePackAnalyzer.InaccessibleFormatterType :
  247|                 instanceProvidingMember is null ? MsgPack00xMessagePackAnalyzer.InaccessibleFormatterInstance :
  248|                 null,
  249|             ExcludeFromSourceGeneratedResolver =
  250|                 type.GetAttributes().Any(a => a.AttributeClass?.Name == Constants.ExcludeFormatterFromSourceGeneratedResolverAttributeName && a.AttributeClass?.ContainingNamespace.Name == Constants.AttributeNamespace),
  251|         };
  252| 
  253|         return true;
  254|     }
  255| 
  256|     public DiagnosticDescriptor? InaccessibleDescriptor { get; init; }
  257| 
  258|     public bool ExcludeFromSourceGeneratedResolver { get; init; }
  259| 
  260|     public string InstanceExpression => this.InstanceProvidingMember == ".ctor"
  261|         ? $"new {this.Name.GetQualifiedName()}()"
  262|         : $"{this.Name.GetQualifiedName()}.{this.InstanceProvidingMember}";
  263| 
  264|     public virtual bool Equals(FormatterDescriptor? other)
  265|     {
  266|         return other is not null
  267|             && this.Name.Equals(other.Name)
  268|             && this.InstanceProvidingMember == other.InstanceProvidingMember
  269|             && this.InstanceTypeName.Equals(other.InstanceTypeName)
  270|             && this.FormattableTypes.SetEquals(other.FormattableTypes)
  271|             && this.InaccessibleDescriptor == other.InaccessibleDescriptor
  272|             && this.ExcludeFromSourceGeneratedResolver == other.ExcludeFromSourceGeneratedResolver;
  273|     }
  274| 
  275|     public override int GetHashCode() => this.Name.GetHashCode();
  276| }
  277| 
  278| /// <summary>
  279| /// Describes a formattable type.
  280| /// </summary>
  281| /// <param name="Name">The name of the formattable type.</param>
  282| /// <param name="IsFormatterInSameAssembly"><see langword="true" /> if the formatter and the formatted types are declared in the same assembly.</param>
  283| public record FormattableType(QualifiedTypeName Name, bool IsFormatterInSameAssembly)
  284| {
  285|     public FormattableType(ITypeSymbol type, IAssemblySymbol? formatterAssembly)
  286|         : this(QualifiedTypeName.Create(type), SymbolEqualityComparer.Default.Equals(type.ContainingAssembly, formatterAssembly))
  287|     {
  288|     }
  289| }
```

### tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs at head (5f4b762a), full file
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
  308|     public async Task AddAttributeToType()
  309|     {
  310|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  311|         string input = @"
  312| public class Foo
  313| {
  314|     public string Member { get; set; }
  315| }
  316| 
  317| [MessagePack.MessagePackObject]
  318| public class Bar
  319| {
  320|     [MessagePack.Key(0)]
  321|     public {|MsgPack003:Foo|} Member { get; set; }
  322| }
  323| ";
  324| 
  325|         string output = @"
  326| [MessagePack.MessagePackObject]
  327| public class Foo
  328| {
  329|     [MessagePack.Key(0)]
  330|     public string Member { get; set; }
  331| }
  332| 
  333| [MessagePack.MessagePackObject]
  334| public class Bar
  335| {
  336|     [MessagePack.Key(0)]
  337|     public Foo Member { get; set; }
  338| }
  339| ";
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
  351|     public async Task AddAttributeToTypeForRecord1()
  352|     {
  353|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  354|         string input = @"
  355| public class Foo
  356| {
  357|     public string Member { get; set; }
  358| }
  359| 
  360| [MessagePack.MessagePackObject]
  361| public record Bar
  362| {
  363|     [MessagePack.Key(0)]
  364|     public {|MsgPack003:Foo|} Member { get; set; }
  365| }
  366| ";
  367| 
  368|         string output = @"
  369| [MessagePack.MessagePackObject]
  370| public class Foo
  371| {
  372|     [MessagePack.Key(0)]
  373|     public string Member { get; set; }
  374| }
  375| 
  376| [MessagePack.MessagePackObject]
  377| public record Bar
  378| {
  379|     [MessagePack.Key(0)]
  380|     public Foo Member { get; set; }
  381| }
  382| ";
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
  394|     public async Task AddAttributeToTypeForRecord2()
  395|     {
  396|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  397|         string input = @"
  398| public record Foo
  399| {
  400|     public string Member { get; set; }
  401| }
  402| 
  403| [MessagePack.MessagePackObject]
  404| public record Bar
  405| {
  406|     [MessagePack.Key(0)]
  407|     public {|MsgPack003:Foo|} Member { get; set; }
  408| }
  409| ";
  410| 
  411|         string output = @"
  412| [MessagePack.MessagePackObject]
  413| public record Foo
  414| {
  415|     [MessagePack.Key(0)]
  416|     public string Member { get; set; }
  417| }
  418| 
  419| [MessagePack.MessagePackObject]
  420| public record Bar
  421| {
  422|     [MessagePack.Key(0)]
  423|     public Foo Member { get; set; }
  424| }
  425| ";
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
  437|     public async Task AddAttributeToTypeForRecordPrimaryConstructor()
  438|     {
  439|         // Don't use Preamble because we want to test that it works without a using statement at the top.
  440|         string input = @"
  441| public class Foo
  442| {
  443|     public string Member { get; set; }
  444| }
  445| 
  446| [MessagePack.MessagePackObject]
  447| public record Bar([property: MessagePack.Key(0)] {|MsgPack003:Foo|} Member);
  448| 
  449| namespace System.Runtime.CompilerServices
  450| {
  451|     internal static class IsExternalInit
  452|     {
  453|     }
  454| }
  455| ";
  456| 
  457|         string output = @"
  458| [MessagePack.MessagePackObject]
  459| public class Foo
  460| {
  461|     [MessagePack.Key(0)]
  462|     public string Member { get; set; }
  463| }
  464| 
  465| [MessagePack.MessagePackObject]
  466| public record Bar([property: MessagePack.Key(0)] Foo Member);
  467| 
  468| namespace System.Runtime.CompilerServices
  469| {
  470|     internal static class IsExternalInit
  471|     {
  472|     }
  473| }
  474| ";
  475| 
  476|         await new VerifyCS.Test
  477|         {
  478|             TestCode = input,
  479|             FixedCode = output,
  480|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  481|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  482|         }.RunAsync();
  483|     }
  484| 
  485|     [Fact]
  486|     public async Task CodeFixAppliesAcrossFiles()
  487|     {
  488|         string source1 = @"
  489| public class Foo
  490| {
  491|     public int Member1 { get; set; }
  492| }
  493| ";
  494| 
  495|         string source2 = @"using MessagePack;
  496| 
  497| [MessagePackObject]
  498| public class Bar : {|MsgPack004:Foo|}
  499| {
  500|     public int {|MsgPack004:Member2|} { get; set; }
  501| }
  502| ";
  503| 
  504|         string output1 = @"
  505| public class Foo
  506| {
  507|     [MessagePack.Key(1)]
  508|     public int Member1 { get; set; }
  509| }
  510| ";
  511|         string output2 = @"using MessagePack;
  512| 
  513| [MessagePackObject]
  514| public class Bar : Foo
  515| {
  516|     [Key(0)]
  517|     public int Member2 { get; set; }
  518| }
  519| ";
  520| 
  521|         await new VerifyCS.Test(ReferencesSet.MessagePackAnnotations)
  522|         {
  523|             CodeFixTestBehaviors = CodeFixTestBehaviors.SkipLocalDiagnosticCheck, // BUGBUG: move diagnostic to `Foo` reference in Bar's base type list.
  524|             TestState =
  525|             {
  526|                 Sources = { source1, source2 },
  527|             },
  528|             FixedState =
  529|             {
  530|                 Sources = { output1, output2 },
  531|             },
  532|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  533|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  534|         }.RunAsync();
  535|     }
  536| 
  537|     [Fact]
  538|     public async Task AddAttributeToGenericType()
  539|     {
  540|         string input = Preamble + /* lang=c#-test */ """
  541|             public class Foo<T>
  542|             {
  543|                 public T Member { get; set; }
  544|             }
  545| 
  546|             [MessagePackObject]
  547|             public class Bar
  548|             {
  549|                 [Key(0)]
  550|                 public {|MsgPack003:Foo<int>|} MemberUserGeneric { get; set; }
  551| 
  552|                 [Key(1)]
  553|                 public System.Collections.Generic.List<int> MemberKnownGeneric { get; set; }
  554|             }
  555|             """;
  556| 
  557|         string output = Preamble + /* lang=c#-test */ """
  558| 
  559|             [MessagePackObject]
  560|             public class Foo<T>
  561|             {
  562|                 [Key(0)]
  563|                 public T Member { get; set; }
  564|             }
  565| 
  566|             [MessagePackObject]
  567|             public class Bar
  568|             {
  569|                 [Key(0)]
  570|                 public Foo<int> MemberUserGeneric { get; set; }
  571| 
  572|                 [Key(1)]
  573|                 public System.Collections.Generic.List<int> MemberKnownGeneric { get; set; }
  574|             }
  575|             """;
  576| 
  577|         await new VerifyCS.Test
  578|         {
  579|             TestCode = input,
  580|             FixedCode = output,
  581|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  582|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  583|         }.RunAsync();
  584|     }
  585| 
  586|     [Fact]
  587|     public async Task AddAttributesToMembersOfRecord()
  588|     {
  589|         string input = Preamble + /* lang=c#-test */ """
  590|             [MessagePackObject]
  591|             public record Foo
  592|             {
  593|                 public string {|MsgPack004:Member1|} { get; set; }
  594|                 public string {|MsgPack004:Member2|} { get; set; }
  595|             }
  596|             """;
  597| 
  598|         string output = Preamble + /* lang=c#-test */ """
  599|             [MessagePackObject]
  600|             public record Foo
  601|             {
  602|                 [Key(0)]
  603|                 public string Member1 { get; set; }
  604|                 [Key(1)]
  605|                 public string Member2 { get; set; }
  606|             }
  607|             """;
  608|         await new VerifyCS.Test
  609|         {
  610|             ReferenceAssemblies = ReferenceAssemblies.Net.Net60,
  611|             CompilerDiagnostics = CompilerDiagnostics.Errors,
  612|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  613|             SolutionTransforms =
  614|             {
  615|                 static (solution, projectId) =>
  616|                 {
  617|                     return solution.WithProjectParseOptions(projectId, new CSharpParseOptions(languageVersion: LanguageVersion.CSharp11));
  618|                 },
  619|             },
  620|             TestCode = input,
  621|             FixedCode = output,
  622|         }.RunAsync();
  623|     }
  624| 
  625|     [Fact]
  626|     public async Task AddAttributesToMembersOfRecordStruct()
  627|     {
  628|         string input = Preamble + /* lang=c#-test */ """
  629|             [MessagePackObject]
  630|             public record struct Foo
  631|             {
  632|                 public string {|MsgPack004:Member1|} { get; set; }
  633|                 public string {|MsgPack004:Member2|} { get; set; }
  634|             }
  635|             """;
  636| 
  637|         string output = Preamble + /* lang=c#-test */ """
  638|             [MessagePackObject]
  639|             public record struct Foo
  640|             {
  641|                 [Key(0)]
  642|                 public string Member1 { get; set; }
  643|                 [Key(1)]
  644|                 public string Member2 { get; set; }
  645|             }
  646|             """;
  647|         await new VerifyCS.Test
  648|         {
  649|             ReferenceAssemblies = ReferenceAssemblies.Net.Net60,
  650|             CompilerDiagnostics = CompilerDiagnostics.Errors,
  651|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  652|             SolutionTransforms =
  653|             {
  654|                 static (solution, projectId) =>
  655|                 {
  656|                     return solution.WithProjectParseOptions(projectId, new CSharpParseOptions(languageVersion: LanguageVersion.CSharp11));
  657|                 },
  658|             },
  659|             TestCode = input,
  660|             FixedCode = output,
  661|         }.RunAsync();
  662|     }
  663| 
  664|     [Fact]
  665|     public async Task AddAttributesToMembersOfRecordWithPrimaryCtor()
  666|     {
  667|         string input = Preamble + /* lang=c#-test */ """
  668|             [MessagePackObject]
  669|             public record {|MsgPack007:Foo|}(
  670|                 string {|MsgPack004:Member1|},
  671|                 string {|MsgPack004:Member2|});
  672|             """;
  673| 
  674|         string output = Preamble + /* lang=c#-test */ """
  675|             [MessagePackObject]
  676|             public record Foo(
  677|                 [property: Key(0)] string Member1,
  678|                 [property: Key(1)] string Member2);
  679|             """;
  680| 
  681|         await new VerifyCS.Test
  682|         {
  683|             ReferenceAssemblies = ReferenceAssemblies.Net.Net60,
  684|             CompilerDiagnostics = CompilerDiagnostics.Errors,
  685|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  686|             SolutionTransforms =
  687|             {
  688|                 static (solution, projectId) =>
  689|                 {
  690|                     return solution.WithProjectParseOptions(projectId, new CSharpParseOptions(languageVersion: LanguageVersion.CSharp11));
  691|                 },
  692|             },
  693|             TestCode = input,
  694|             FixedCode = output,
  695|         }.RunAsync();
  696|     }
  697| 
  698|     [Fact]
  699|     public async Task AddAttributesToMembersOfRecordStructWithPrimaryCtor()
  700|     {
  701|         string input = Preamble + /* lang=c#-test */ """
  702|             [MessagePackObject]
  703|             public record struct Foo(
  704|                 string {|MsgPack004:Member1|},
  705|                 string {|MsgPack004:Member2|});
  706|             """;
  707| 
  708|         string output = Preamble + /* lang=c#-test */ """
  709|             [MessagePackObject]
  710|             public record struct Foo(
  711|                 [property: Key(0)] string Member1,
  712|                 [property: Key(1)] string Member2);
  713|             """;
  714| 
  715|         await new VerifyCS.Test
  716|         {
  717|             ReferenceAssemblies = ReferenceAssemblies.Net.Net60,
  718|             CompilerDiagnostics = CompilerDiagnostics.Errors,
  719|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  720|             SolutionTransforms =
  721|             {
  722|                 static (solution, projectId) =>
  723|                 {
  724|                     return solution.WithProjectParseOptions(projectId, new CSharpParseOptions(languageVersion: LanguageVersion.CSharp11));
  725|                 },
  726|             },
  727|             TestCode = input,
  728|             FixedCode = output,
  729|         }.RunAsync();
  730|     }
  731| 
  732|     [Fact]
  733|     public async Task DoNotAddAttributesToClassWithPrimaryCtor()
  734|     {
  735|         string input = Preamble + /* lang=c#-test */ """
  736|             [MessagePackObject]
  737|             public class {|MsgPack007:Foo|}(
  738|                 string Member1,
  739|                 string Member2);
  740|             """;
  741| 
  742|         string output = Preamble + /* lang=c#-test */ """
  743|             [MessagePackObject]
  744|             public class {|MsgPack007:Foo|}(
  745|                 string Member1,
  746|                 string Member2);
  747|             """;
  748| 
  749|         await new VerifyCS.Test
  750|         {
  751|             ReferenceAssemblies = ReferenceAssemblies.Net.Net60,
  752|             CompilerDiagnostics = CompilerDiagnostics.Errors,
  753|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  754|             SolutionTransforms =
  755|             {
  756|                 static (solution, projectId) =>
  757|                 {
  758|                     return solution.WithProjectParseOptions(projectId, new CSharpParseOptions(languageVersion: LanguageVersion.CSharp12));
  759|                 },
  760|             },
  761|             TestCode = input,
  762|             FixedCode = output,
  763|         }.RunAsync();
  764|     }
  765| 
  766|     [Fact]
  767|     public async Task DerivedAttributes()
  768|     {
  769|         string test = /* lang=c#-test */ """
  770|             using MessagePack;
  771| 
  772|             [MessagePackObject]
  773|             public class A
  774|             {
  775|                 [{|MsgPack016:CompositeKey(0, 1)|}]
  776|                 public string Prop1 { get; set; }
  777| 
  778|                 [{|MsgPack016:CompositeKey(0, 2)|}]
  779|                 public string Field2;
  780|             }
  781| 
  782|             [MessagePackObject]
  783|             public class B : {|MsgPack016:A|}
  784|             {
  785|                 [{|MsgPack016:CompositeKey(1, 1)|}]
  786|                 public string Prop3 { get; set; }
  787| 
  788|                 [{|MsgPack016:CompositeKey(1, 2)|}]
  789|                 public string Field4;
  790|             }
  791| 
  792|             public class CompositeKeyAttribute : KeyAttribute
  793|             {
  794|                 public CompositeKeyAttribute(byte level, int index)
  795|                     : base(CreateKey(level, index)) { }
  796| 
  797|                 public static string CreateKey(byte level, int index)
  798|                 {
  799|                     var c = (char)('A' + level);
  800|                     return c + index.ToString("x");
  801|                 }
  802|             }
  803|             """;
  804| 
  805|         await VerifyCS.VerifyAnalyzerAsync(test);
  806|     }
  807| 
  808|     [Fact]
  809|     public async Task DerivedAttributes_SourceGenerationDisabled()
  810|     {
  811|         string test = /* lang=c#-test */ """
  812|             using MessagePack;
  813| 
  814|             [MessagePackObject(SuppressSourceGeneration = true)]
  815|             public class A
  816|             {
  817|                 [CompositeKey(0, 1)]
  818|                 public string Prop1 { get; set; }
  819| 
  820|                 [CompositeKey(0, 2)]
  821|                 public string Field2;
  822|             }
  823| 
  824|             [MessagePackObject(SuppressSourceGeneration = true)]
  825|             public class B : A
  826|             {
  827|                 [CompositeKey(1, 1)]
  828|                 public string Prop3 { get; set; }
  829| 
  830|                 [CompositeKey(1, 2)]
  831|                 public string Field4;
  832|             }
  833| 
  834|             public class CompositeKeyAttribute : KeyAttribute
  835|             {
  836|                 public CompositeKeyAttribute(byte level, int index)
  837|                     : base(CreateKey(level, index)) { }
  838| 
  839|                 public static string CreateKey(byte level, int index)
  840|                 {
  841|                     var c = (char)('A' + level);
  842|                     return c + index.ToString("x");
  843|                 }
  844|             }
  845|             """;
  846| 
  847|         await VerifyCS.VerifyAnalyzerAsync(test);
  848|     }
  849| 
  850|     [Fact]
  851|     public async Task InitPropertyInitializer()
  852|     {
  853|         string test = /* lang=c#-test */ """
  854|             using MessagePack;
  855|             
  856|             [MessagePackObject]
  857|             public class A
  858|             {
  859|                 [Key(0)]
  860|                 public string Prop1 { get; init; } {|MsgPack017:= "some default"|};
  861| 
  862|                 [Key(1)]
  863|                 public string Prop2 { get; set; } = "some default";
  864|             }
  865|            
  866|            
  867|             [MessagePackObject(SuppressSourceGeneration = true)]
  868|             public class B
  869|             {
  870|                 [Key(0)]
  871|                 public string Prop1 { get; init; } = "some default";
  872| 
  873|                 [Key(1)]
  874|                 public string Prop2 { get; set; } = "some default";
  875|             }
  876|             """;
  877| 
  878|         await VerifyCS.VerifyAnalyzerAsync(test);
  879|     }
  880| 
  881|     [Fact]
  882|     public async Task NameCollisionsInForceMapMode()
  883|     {
  884|         string test = /* lang=c#-test */ """
  885|             using MessagePack;
  886| 
  887|             [MessagePackObject(true)]
  888|             public class Base
  889|             {
  890|                 public string Prop { get; set; }
  891| 
  892|                 public string Field;
  893| 
  894|                 public string TwoFaced { get; set; } // derived declares a *field* by the same name.
  895|             }
  896| 
  897|             [MessagePackObject(true)]
  898|             public class Derived : Base
  899|             {
  900|                 public new string {|MsgPack018:Prop|} { get; set; }
  901| 
  902|                 public new string {|MsgPack018:Field|};
  903| 
  904|                 public new string {|MsgPack018:TwoFaced|};
  905|             }
  906|             """
  907|         ;
  908| 
  909|         await VerifyCS.VerifyAnalyzerAsync(test);
  910|     }
  911| 
  912|     [Fact]
  913|     public async Task AbstractFormatterDoesNotAttractAttention()
  914|     {
  915|         string test = /* lang=c#-test */ """
  916|             using MessagePack;
  917|             using MessagePack.Formatters;
  918| 
  919|             public abstract class AbstractFormatter1 : IMessagePackFormatter<object>
  920|             {
  921|                 public abstract void Serialize(ref MessagePackWriter writer, object value, MessagePackSerializerOptions options);
  922|                 public abstract object Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options);
  923|             }
  924| 
  925|             public abstract class AbstractFormatter2 : IMessagePackFormatter<object>
  926|             {
  927|                 public abstract void Serialize(ref MessagePackWriter writer, object value, MessagePackSerializerOptions options);
  928|                 public abstract object Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options);
  929|             }
  930|             """;
  931| 
  932|         await VerifyCS.VerifyAnalyzerAsync(test);
  933|     }
  934| }
```

### src/MessagePack.SourceGenerator/CodeAnalysis/AnalyzerOptions.cs at base (f5e104ee), full file
```
    1| ﻿// Copyright (c) All contributors. All rights reserved.
    2| // Licensed under the MIT license. See LICENSE file in the project root for full license information.
    3| 
    4| #pragma warning disable SA1402 // File may only contain a single type
    5| 
    6| using System.Collections.Immutable;
    7| using System.Diagnostics.CodeAnalysis;
    8| using Microsoft.CodeAnalysis;
    9| 
   10| namespace MessagePack.SourceGenerator.CodeAnalysis;
   11| 
   12| /// <summary>
   13| /// Options for the analyzer and source generator.
   14| /// </summary>
   15| /// <remarks>
   16| /// These options are typically gathered from attributes in the compilation.
   17| /// </remarks>
   18| public record AnalyzerOptions
   19| {
   20|     private readonly ImmutableHashSet<FormatterDescriptor> knownFormatters = ImmutableHashSet<FormatterDescriptor>.Empty;
   21| 
   22|     private readonly ImmutableDictionary<QualifiedTypeName, ImmutableArray<FormattableType>> collidingFormatters = ImmutableDictionary<QualifiedTypeName, ImmutableArray<FormattableType>>.Empty;
   23| 
   24|     /// <summary>
   25|     /// Gets the set fully qualified names of types that are assumed to have custom formatters written that will be included by a resolver by the program.
   26|     /// </summary>
   27|     public ImmutableHashSet<FormattableType> AssumedFormattableTypes { get; init; } = ImmutableHashSet<FormattableType>.Empty;
   28| 
   29|     /// <summary>
   30|     /// Gets the set of custom formatters that should be considered by the analyzer and included in the generated resolver.
   31|     /// </summary>
   32|     public ImmutableHashSet<FormatterDescriptor> KnownFormatters
   33|     {
   34|         get => this.knownFormatters;
   35|         init
   36|         {
   37|             this.knownFormatters = value;
   38|             this.KnownFormattersByName = value.ToImmutableDictionary(f => f.Name);
   39| 
   40|             Dictionary<FormattableType, ImmutableArray<FormatterDescriptor>> formattableTypes = new();
   41|             bool collisionsEncountered = false;
   42|             foreach (FormatterDescriptor formatter in value)
   43|             {
   44|                 if (formatter.ExcludeFromSourceGeneratedResolver)
   45|                 {
   46|                     continue;
   47|                 }
   48| 
   49|                 foreach (FormattableType dataType in formatter.FormattableTypes)
   50|                 {
   51|                     if (formattableTypes.ContainsKey(dataType))
   52|                     {
   53|                         formattableTypes[dataType] = formattableTypes[dataType].Add(formatter);
   54|                         collisionsEncountered = true;
   55|                     }
   56|                     else
   57|                     {
   58|                         formattableTypes.Add(dataType, ImmutableArray.Create(formatter));
   59|                     }
   60|                 }
   61|             }
   62| 
   63|             var collidingFormatters = ImmutableDictionary<QualifiedTypeName, ImmutableArray<FormattableType>>.Empty;
   64|             if (collisionsEncountered)
   65|             {
   66|                 foreach (KeyValuePair<FormattableType, ImmutableArray<FormatterDescriptor>> kvp in formattableTypes)
   67|                 {
   68|                     if (kvp.Value.Length > 1)
   69|                     {
   70|                         foreach (FormatterDescriptor collidingFormatter in kvp.Value)
   71|                         {
   72|                             if (collidingFormatters.TryGetValue(collidingFormatter.Name, out ImmutableArray<FormattableType> collidingTypes))
   73|                             {
   74|                                 collidingFormatters = collidingFormatters.SetItem(collidingFormatter.Name, collidingTypes.Add(kvp.Key));
   75|                             }
   76|                             else
   77|                             {
   78|                                 collidingFormatters = collidingFormatters.Add(collidingFormatter.Name, ImmutableArray.Create(kvp.Key));
   79|                             }
   80|                         }
   81|                     }
   82|                 }
   83|             }
   84| 
   85|             this.collidingFormatters = collidingFormatters;
   86|         }
   87|     }
   88| 
   89|     public ImmutableDictionary<QualifiedNamedTypeName, FormatterDescriptor> KnownFormattersByName { get; private init; } = ImmutableDictionary<QualifiedNamedTypeName, FormatterDescriptor>.Empty;
   90| 
   91|     public GeneratorOptions Generator { get; init; } = new();
   92| 
   93|     /// <summary>
   94|     /// Gets a value indicating whether the analyzer is generating source code.
   95|     /// </summary>
   96|     public bool IsGeneratingSource { get; init; }
   97| 
   98|     internal AnalyzerOptions WithFormatterTypes(ImmutableArray<FormattableType> formattableTypes, ImmutableHashSet<FormatterDescriptor> customFormatters)
   99|     {
  100|         return this with
  101|         {
  102|             AssumedFormattableTypes = ImmutableHashSet.CreateRange(formattableTypes).Union(customFormatters.SelectMany(t => t.FormattableTypes)),
  103|             KnownFormatters = customFormatters,
  104|         };
  105|     }
  106| 
  107|     /// <summary>
  108|     /// Modifies these options based on the attributes on the assembly being compiled.
  109|     /// </summary>
  110|     /// <param name="assemblyAttributes">The assembly-level attributes.</param>
  111|     /// <param name="cancellationToken">A cancellation token.</param>
  112|     /// <returns>The modified set of options.</returns>
  113|     internal AnalyzerOptions WithAssemblyAttributes(ImmutableArray<AttributeData> assemblyAttributes, CancellationToken cancellationToken)
  114|     {
  115|         ImmutableHashSet<FormatterDescriptor> customFormatters = AnalyzerUtilities.ParseKnownFormatterAttribute(assemblyAttributes, cancellationToken).Union(this.KnownFormatters);
  116|         ImmutableArray<FormattableType> customFormattedTypes = this.AssumedFormattableTypes.Union(AnalyzerUtilities.ParseAssumedFormattableAttribute(assemblyAttributes, cancellationToken)).ToImmutableArray();
  117|         return this.WithFormatterTypes(customFormattedTypes, customFormatters);
  118|     }
  119| 
  120|     internal ImmutableArray<FormattableType> GetCollidingFormatterDataTypes(QualifiedTypeName formatter) => this.collidingFormatters.GetValueOrDefault(formatter, ImmutableArray<FormattableType>.Empty);
  121| 
  122|     public virtual bool Equals(AnalyzerOptions? other)
  123|     {
  124|         if (other is null)
  125|         {
  126|             return false;
  127|         }
  128| 
  129|         if (ReferenceEquals(this, other))
  130|         {
  131|             return true;
  132|         }
  133| 
  134|         if (this.GetType() != other.GetType())
  135|         {
  136|             return false;
  137|         }
  138| 
  139|         return this.knownFormatters.SetEquals(other.knownFormatters)
  140|             && this.AssumedFormattableTypes.SetEquals(other.AssumedFormattableTypes)
  141|             && this.Generator.Equals(other.Generator)
  142|             && this.IsGeneratingSource == other.IsGeneratingSource;
  143|     }
  144| 
  145|     public override int GetHashCode()
  146|     {
  147|         int hashCode = 0;
  148| 
  149|         hashCode = Hash(hashCode, this.knownFormatters.Count);
  150|         hashCode = Hash(hashCode, this.AssumedFormattableTypes.Count);
  151|         hashCode = Hash(hashCode, this.Generator.GetHashCode());
  152| 
  153|         return hashCode;
  154| 
  155|         static int Hash(int hashCode, int value)
  156|         {
  157|             return (hashCode * 31) + value;
  158|         }
  159|     }
  160| }
  161| 
  162| /// <summary>
  163| /// Customizes aspects of source generated formatters.
  164| /// </summary>
  165| public record FormattersOptions
  166| {
  167|     /// <summary>
  168|     /// Gets a value indicating whether types will be serialized with their property names as well as their values in a key=value dictionary, as opposed to an array of values.
  169|     /// </summary>
  170|     public bool UsesMapMode { get; init; }
  171| }
  172| 
  173| /// <summary>
  174| /// Describes the generated resolver.
  175| /// </summary>
  176| public record ResolverOptions
  177| {
  178|     /// <summary>
  179|     /// Gets the name to use for the resolver.
  180|     /// </summary>
  181|     public QualifiedNamedTypeName Name { get; init; } = new(TypeKind.Class)
  182|     {
  183|         Container = new NamespaceTypeContainer("MessagePack"),
  184|         Name = "GeneratedMessagePackResolver",
  185|     };
  186| }
  187| 
  188| /// <summary>
  189| /// Customizes AOT source generation of formatters for custom types.
  190| /// </summary>
  191| public record GeneratorOptions
  192| {
  193|     /// <summary>
  194|     /// Gets options for the generated resolver.
  195|     /// </summary>
  196|     public ResolverOptions Resolver { get; init; } = new();
  197| 
  198|     /// <summary>
  199|     /// Gets options for the generated formatter.
  200|     /// </summary>
  201|     public FormattersOptions Formatters { get; init; } = new();
  202| }
  203| 
  204| /// <summary>
  205| /// Describes a custom formatter.
  206| /// </summary>
  207| /// <param name="Name">The name of the type that implements at least one <c>IMessagePackFormatter</c> interface. If the formatter is a generic type, this should <em>not</em> include any generic type parameters.</param>
  208| /// <param name="InstanceProvidingMember">Either ".ctor" or the name of a static field or property that will return an instance of the formatter.</param>
  209| /// <param name="InstanceTypeName">The type name to use when referring to an instance of the formatter. Usually the same as <paramref name="Name"/> but may be different if <paramref name="InstanceProvidingMember"/> returns a different type.</param>
  210| /// <param name="FormattableTypes">The type arguments that appear in each implemented <c>IMessagePackFormatter</c> interface. When generic, these should be the full name of their type definitions.</param>
  211| public record FormatterDescriptor(QualifiedNamedTypeName Name, string? InstanceProvidingMember, QualifiedTypeName InstanceTypeName, ImmutableHashSet<FormattableType> FormattableTypes)
  212| {
  213|     /// <summary>
  214|     /// Creates a descriptor for a formatter, if the given type implements at least one <c>IMessagePackFormatter</c> interface.
  215|     /// </summary>
  216|     /// <param name="type">The type symbol for the formatter.</param>
  217|     /// <param name="formatter">Receives the formatter descriptor, if applicable.</param>
  218|     /// <returns><see langword="true"/> if <paramref name="type"/> represents a formatter.</returns>
  219|     public static bool TryCreate(INamedTypeSymbol type, [NotNullWhen(true)] out FormatterDescriptor? formatter)
  220|     {
  221|         var formattedTypes =
  222|             AnalyzerUtilities.SearchTypeForFormatterImplementations(type)
  223|             .Select(i => new FormattableType(i, type.ContainingAssembly))
  224|             .ToImmutableHashSet();
  225|         if (formattedTypes.IsEmpty)
  226|         {
  227|             formatter = null;
  228|             return false;
  229|         }
  230| 
  231|         IFieldSymbol? instanceField = type.GetMembers("Instance").OfType<IFieldSymbol>()
  232|             .FirstOrDefault(m => m.IsStatic && m.DeclaredAccessibility == Accessibility.Public && m.IsReadOnly);
  233|         IMethodSymbol? ctor = type.InstanceConstructors.FirstOrDefault(ctor => ctor.Parameters.Length == 0 && ctor.DeclaredAccessibility >= Accessibility.Internal);
  234|         string? instanceProvidingMember = instanceField?.Name ?? ctor?.Name ?? null;
  235|         QualifiedTypeName instanceTypeName = QualifiedTypeName.Create(instanceField?.Type ?? type);
  236| 
  237|         formatter = new FormatterDescriptor(new QualifiedNamedTypeName(type), instanceProvidingMember, instanceTypeName, formattedTypes)
  238|         {
  239|             InaccessibleDescriptor =
  240|                 CodeAnalysisUtilities.FindInaccessibleTypes(type).Any() ? MsgPack00xMessagePackAnalyzer.InaccessibleFormatterType :
  241|                 instanceProvidingMember is null ? MsgPack00xMessagePackAnalyzer.InaccessibleFormatterInstance :
  242|                 null,
  243|             ExcludeFromSourceGeneratedResolver =
  244|                 type.GetAttributes().Any(a => a.AttributeClass?.Name == Constants.ExcludeFormatterFromSourceGeneratedResolverAttributeName && a.AttributeClass?.ContainingNamespace.Name == Constants.AttributeNamespace),
  245|         };
  246| 
  247|         return true;
  248|     }
  249| 
  250|     public DiagnosticDescriptor? InaccessibleDescriptor { get; init; }
  251| 
  252|     public bool ExcludeFromSourceGeneratedResolver { get; init; }
  253| 
  254|     public string InstanceExpression => this.InstanceProvidingMember == ".ctor"
  255|         ? $"new {this.Name.GetQualifiedName()}()"
  256|         : $"{this.Name.GetQualifiedName()}.{this.InstanceProvidingMember}";
  257| 
  258|     public virtual bool Equals(FormatterDescriptor? other)
  259|     {
  260|         return other is not null
  261|             && this.Name.Equals(other.Name)
  262|             && this.InstanceProvidingMember == other.InstanceProvidingMember
  263|             && this.InstanceTypeName.Equals(other.InstanceTypeName)
  264|             && this.FormattableTypes.SetEquals(other.FormattableTypes)
  265|             && this.InaccessibleDescriptor == other.InaccessibleDescriptor
  266|             && this.ExcludeFromSourceGeneratedResolver == other.ExcludeFromSourceGeneratedResolver;
  267|     }
  268| 
  269|     public override int GetHashCode() => this.Name.GetHashCode();
  270| }
  271| 
  272| /// <summary>
  273| /// Describes a formattable type.
  274| /// </summary>
  275| /// <param name="Name">The name of the formattable type.</param>
  276| /// <param name="IsFormatterInSameAssembly"><see langword="true" /> if the formatter and the formatted types are declared in the same assembly.</param>
  277| public record FormattableType(QualifiedTypeName Name, bool IsFormatterInSameAssembly)
  278| {
  279|     public FormattableType(ITypeSymbol type, IAssemblySymbol? formatterAssembly)
  280|         : this(QualifiedTypeName.Create(type), SymbolEqualityComparer.Default.Equals(type.ContainingAssembly, formatterAssembly))
  281|     {
  282|     }
  283| }
```

## What you did NOT get (refuse anything that depends on it)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)

Return only the JSON object described in the brief.