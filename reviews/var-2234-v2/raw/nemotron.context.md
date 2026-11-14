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
# Change var-2234-v2: branch cs-var/2234-v2, base 32258fdbee4bcd653c79f51b4376b5103c6f4d27, head 6a3d2cb02e208e17287142c06a064ffcaa0ff615
Commit message: Keep analyzing SuppressSourceGeneration types; only skip source generation

Types attributed with [MessagePackObject(SuppressSourceGeneration = true)]
must still be validated by the MsgPack00x analyzer (#2234). Returning early
from TypeCollector.GetObjectInfo for such types (as done in 3.1.1 to stop
collecting their member types) silences every member diagnostic, because the
analyzer and the generator share that code path.

Instead, the type's members are always validated, and suppression only affects
what the generator collects:
- member types of a suppressed type are no longer recursively collected when
  generating source, so no formatters (e.g. an empty union formatter for a
  non-[Union] interface member) are emitted just because a suppressed type
  references them;
- a closed generic type whose definition is suppressed is no longer registered
  in the generated resolver, which referenced a formatter that was never
  generated (CS0426).

Also stop the analyzer from crashing (AD0001) on duplicate keys and on mixed
int/string keys: the colliding member is reported with MsgPack005 and skipped
instead of being added to the member map.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Upstream issue: https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2234

## Requirement set (requirements/var-2234-v2.yaml)
```yaml
# REUSED from requirements/2234.yaml (same clauses, same ids, unchanged text) for another fix of the same upstream issue
# #2234, so every fix of it is judged against the same clauses (docs/MEASUREMENT.md, "Same issue, several fixes").
# Still a placeholder derived from the issue, not a Tieto set.
change: "var-2234-v2"
branch: cs-var/2234-v2
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
 "change": "var-2234-v2",
 "branch": "cs-var/2234-v2",
 "base": "32258fdb",
 "head": "6a3d2cb0",
 "base_full": "32258fdbee4bcd653c79f51b4376b5103c6f4d27",
 "head_full": "6a3d2cb02e208e17287142c06a064ffcaa0ff615",
 "commit_message": "Keep analyzing SuppressSourceGeneration types; only skip source generation\n\nTypes attributed with [MessagePackObject(SuppressSourceGeneration = true)]\nmust still be validated by the MsgPack00x analyzer (#2234). Returning early\nfrom TypeCollector.GetObjectInfo for such types (as done in 3.1.1 to stop\ncollecting their member types) silences every member diagnostic, because the\nanalyzer and the generator share that code path.\n\nInstead, the type's members are always validated, and suppression only affects\nwhat the generator collects:\n- member types of a suppressed type are no longer recursively collected when\n  generating source, so no formatters (e.g. an empty union formatter for a\n  non-[Union] interface member) are emitted just because a suppressed type\n  references them;\n- a closed generic type whose definition is suppressed is no longer registered\n  in the generated resolver, which referenced a formatter that was never\n  generated (CS0426).\n\nAlso stop the analyzer from crashing (AD0001) on duplicate keys and on mixed\nint/string keys: the colliding member is reported with MsgPack005 and skipped\ninstead of being added to the member map.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>",
 "author": "Zawaer",
 "agent_written": true,
 "diff": {
  "files": 9,
  "insertions": 841,
  "deletions": 28,
  "by_kind": {
   "source": 1,
   "test": 2,
   "generated": 6
  },
  "by_file": [
   {
    "path": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
    "ins": 60,
    "del": 28,
    "kind": "source"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs",
    "ins": 97,
    "del": 0,
    "kind": "test"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs",
    "ins": 319,
    "del": 0,
    "kind": "test"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/Resources/SuppressSourceGeneration_ClosedGenericIsNotRegistered/Formatters.MessagePack.GeneratedMessagePackResolver.HolderFormatter.g.cs",
    "ins": 58,
    "del": 0,
    "kind": "generated"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/Resources/SuppressSourceGeneration_ClosedGenericIsNotRegistered/MessagePack.GeneratedMessagePackResolver.g.cs",
    "ins": 63,
    "del": 0,
    "kind": "generated"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/Resources/SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(False)/Formatters.MessagePack.GeneratedMessagePackResolver.BFormatter.g.cs",
    "ins": 56,
    "del": 0,
    "kind": "generated"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/Resources/SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(False)/MessagePack.GeneratedMessagePackResolver.g.cs",
    "ins": 63,
    "del": 0,
    "kind": "generated"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/Resources/SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(True)/Formatters.MessagePack.GeneratedMessagePackResolver.BFormatter.g.cs",
    "ins": 62,
    "del": 0,
    "kind": "generated"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/Resources/SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(True)/MessagePack.GeneratedMessagePackResolver.g.cs",
    "ins": 63,
    "del": 0,
    "kind": "generated"
   }
  ]
 },
 "new_tests_in_diff": [
  "GenerationTests.SuppressSourceGeneration_ClosedGenericIsNotRegistered",
  "GenerationTests.SuppressSourceGeneration_MemberTypesAreNotCollected",
  "GenerationTests.SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated",
  "MsgPack00xAnalyzerTests.DuplicateKeysAreReportedWithoutCrashing",
  "MsgPack00xAnalyzerTests.MixedKeysAreReportedWithoutCrashing",
  "MsgPack00xAnalyzerTests.SuppressSourceGeneration_AllowPrivateRequired",
  "MsgPack00xAnalyzerTests.SuppressSourceGeneration_GenericTypeWithoutIssues",
  "MsgPack00xAnalyzerTests.SuppressSourceGeneration_KeyValidation",
  "MsgPack00xAnalyzerTests.SuppressSourceGeneration_KeyValidationOnFields",
  "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MapMode",
  "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MemberTypeNotSerializable",
  "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MissingKeyInBaseType",
  "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MissingKeyOnField",
  "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MissingKeyOnProperty",
  "MsgPack00xAnalyzerTests.SuppressSourceGeneration_ValidTypeHasNoDiagnostics"
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
   "log": "evidence/var-2234-v2/logs/build.log",
   "duration_s": 5.0
  },
  {
   "id": "tests.targeted",
   "tool": "dotnet test",
   "tool_version": "8.0.402",
   "status": "pass",
   "summary": "92 passed, 0 failed, 0 skipped (16 new tests in run)",
   "tests": [
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
     "name": "GenerationTests.AdditionalFormatterTypes_RedundantAttribute",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.Array2DJaggedProperty",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.ArrayTypedProperty",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.CustomFormatterForGenericWithConstraints",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.CustomFormatterViaAttributeOnField(usesMapMode: False)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.CustomFormatterViaAttributeOnField(usesMapMode: True)",
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
     "name": "GenerationTests.EmbeddedTypes",
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
     "name": "GenerationTests.GenericCustomFormatter",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.GenericDataTypeWithPrivateMember",
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
     "name": "GenerationTests.GenericWithConstraintsThatReferenceTypeParameter",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.ImplicitFormatterTypes",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.InterfaceUnionUsedWithNullableRefAnnotation",
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
     "name": "GenerationTests.NoFieldWithCustomFormatterCollected",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.NoGenerationForAnnotationOnly",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.NoPrivateAccessNeeded",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.NoPrivateMemberCollected",
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
     "name": "GenerationTests.SimplifiedNameForKeywordsAndSyntaxSugar",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.SpecifyFormatterFromStockSet",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.SuppressSourceGeneration_ClosedGenericIsNotRegistered",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "GenerationTests.SuppressSourceGeneration_MemberTypesAreNotCollected",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "GenerationTests.SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(usesMapMode: False)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "GenerationTests.SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(usesMapMode: True)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "GenerationTests.SystemCollectionsObjectModelCollection",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.SystemMemoryTypes",
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
     "name": "MsgPack00xAnalyzerTests.DuplicateKeysAreReportedWithoutCrashing",
     "outcome": "passed",
     "new": true
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
     "name": "MsgPack00xAnalyzerTests.MixedKeysAreReportedWithoutCrashing",
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
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_AllowPrivateRequired",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_GenericTypeWithoutIssues",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_KeyValidation",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_KeyValidationOnFields",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MapMode",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MemberTypeNotSerializable",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MissingKeyInBaseType",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MissingKeyOnField",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MissingKeyOnProperty",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_ValidTypeHasNoDiagnostics",
     "outcome": "passed",
     "new": true
    }
   ],
   "log": "evidence/var-2234-v2/logs/tests_targeted.1.log",
   "duration_s": 5.0,
   "filter": [
    "FullyQualifiedName~MsgPack00xAnalyzerTests.|FullyQualifiedName~GenerationTests."
   ],
   "project": "tests/MessagePack.SourceGenerator.Tests"
  },
  {
   "id": "tests.fail_without_fix",
   "tool": "dotnet test (source reverted, tests kept)",
   "tool_version": "8.0.402",
   "status": "pass",
   "summary": "new tests fail on base source: 8/16 failed -> tests do cover the change (8 new tests pass without the fix)",
   "tests": [
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
     "name": "GenerationTests.AdditionalFormatterTypes_RedundantAttribute",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.Array2DJaggedProperty",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.ArrayTypedProperty",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.CustomFormatterForGenericWithConstraints",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.CustomFormatterViaAttributeOnField(usesMapMode: False)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.CustomFormatterViaAttributeOnField(usesMapMode: True)",
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
     "name": "GenerationTests.EmbeddedTypes",
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
     "name": "GenerationTests.GenericCustomFormatter",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.GenericDataTypeWithPrivateMember",
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
     "name": "GenerationTests.GenericWithConstraintsThatReferenceTypeParameter",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.ImplicitFormatterTypes",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.InterfaceUnionUsedWithNullableRefAnnotation",
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
     "name": "GenerationTests.NoFieldWithCustomFormatterCollected",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.NoGenerationForAnnotationOnly",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.NoPrivateAccessNeeded",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.NoPrivateMemberCollected",
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
     "name": "GenerationTests.SimplifiedNameForKeywordsAndSyntaxSugar",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.SpecifyFormatterFromStockSet",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.SuppressSourceGeneration_ClosedGenericIsNotRegistered",
     "outcome": "failed",
     "new": true,
     "error": "System.InvalidOperationException : Context: Source generator application\nContext: Verifying source generated files\nExpected source file list to match\n+MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs\n MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/Formatters.MessagePack.GeneratedMessagePackResol [...]"
    },
    {
     "name": "GenerationTests.SuppressSourceGeneration_MemberTypesAreNotCollected",
     "outcome": "failed",
     "new": true,
     "error": "System.InvalidOperationException : Context: Source generator application\nContext: Verifying source generated files\nExpected source file list to match\n-\n-\n-\n+MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs\n+MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/Formatters.MessagePack.GeneratedMessagePac [...]"
    },
    {
     "name": "GenerationTests.SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(usesMapMode: False)",
     "outcome": "failed",
     "new": true,
     "error": "System.InvalidOperationException : Context: Source generator application\nContext: Verifying source generated files\nExpected source file list to match\n+MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs\n MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/Formatters.MessagePack.GeneratedMessagePackResol [...]"
    },
    {
     "name": "GenerationTests.SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(usesMapMode: True)",
     "outcome": "failed",
     "new": true,
     "error": "System.InvalidOperationException : Context: Source generator application\nContext: Verifying source generated files\nExpected source file list to match\n+MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/MessagePack.GeneratedMessagePackResolver.g.cs\n MessagePack.SourceGenerator/MessagePack.SourceGenerator.MessagePackGenerator/Formatters.MessagePack.GeneratedMessagePackResol [...]"
    },
    {
     "name": "GenerationTests.SystemCollectionsObjectModelCollection",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "GenerationTests.SystemMemoryTypes",
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
     "name": "MsgPack00xAnalyzerTests.DuplicateKeysAreReportedWithoutCrashing",
     "outcome": "failed",
     "new": true,
     "error": "System.InvalidOperationException : Context: Diagnostics of test state\nExpected diagnostic to be in file \"/0/Test0.cs\" was actually in file \"\"\n\nExpected diagnostic:\n    // /0/Test0.cs(9,5,10,35): error MsgPack005\nVerifyCS.Diagnostic(MsgPack00xMessagePackAnalyzer.MsgPack005).WithSpan(9, 5, 10, 35),\n\nActual diagnostic:\n    // error AD0001: Analyzer 'MessagePack.SourceGenerator.Analyzers.MsgPack00xMes [...]"
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
     "name": "MsgPack00xAnalyzerTests.MixedKeysAreReportedWithoutCrashing",
     "outcome": "failed",
     "new": true,
     "error": "System.InvalidOperationException : Context: Diagnostics of test state\nMismatch between number of diagnostics returned, expected \"4\" actual \"5\"\r\n\r\nDiagnostics:\r\n// error AD0001: Analyzer 'MessagePack.SourceGenerator.Analyzers.MsgPack00xMessagePackAnalyzer' threw an exception of type 'System.ArgumentNullException' with message 'Value cannot be null. (Parameter 'key')'.\r\nException occurred with follo [...]"
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
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_AllowPrivateRequired",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_GenericTypeWithoutIssues",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_KeyValidation",
     "outcome": "failed",
     "new": true,
     "error": "System.InvalidOperationException : Context: Diagnostics of test state\nExpected diagnostic to be in file \"/0/Test0.cs\" was actually in file \"\"\n\nExpected diagnostic:\n    // /0/Test0.cs(9,5,10,35): error MsgPack005\nVerifyCS.Diagnostic(MsgPack00xMessagePackAnalyzer.MsgPack005).WithSpan(9, 5, 10, 35),\n\nActual diagnostic:\n    // error AD0001: Analyzer 'MessagePack.SourceGenerator.Analyzers.MsgPack00xMes [...]"
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_KeyValidationOnFields",
     "outcome": "failed",
     "new": true,
     "error": "System.InvalidOperationException : Context: Diagnostics of test state\nExpected diagnostic to be in file \"/0/Test0.cs\" was actually in file \"\"\n\nExpected diagnostic:\n    // /0/Test0.cs(10,16,10,22): error MsgPack005\nVerifyCS.Diagnostic(MsgPack00xMessagePackAnalyzer.MsgPack005).WithSpan(10, 16, 10, 22),\n\nActual diagnostic:\n    // error AD0001: Analyzer 'MessagePack.SourceGenerator.Analyzers.MsgPack00 [...]"
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MapMode",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MemberTypeNotSerializable",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MissingKeyInBaseType",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MissingKeyOnField",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MissingKeyOnProperty",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_ValidTypeHasNoDiagnostics",
     "outcome": "passed",
     "new": true
    }
   ],
   "log": "evidence/var-2234-v2/logs/tests_fail_without_fix.1.log",
   "duration_s": 5.0,
   "reverted_files": [
    "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs"
   ],
   "full_suite_with_source_reverted": {
    "total": 183,
    "failed": 8,
    "failed_tests": [
     "GenerationTests.SuppressSourceGeneration_ClosedGenericIsNotRegistered",
     "GenerationTests.SuppressSourceGeneration_MemberTypesAreNotCollected",
     "GenerationTests.SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(usesMapMode: False)",
     "GenerationTests.SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(usesMapMode: True)",
     "MsgPack00xAnalyzerTests.DuplicateKeysAreReportedWithoutCrashing",
     "MsgPack00xAnalyzerTests.MixedKeysAreReportedWithoutCrashing",
     "MsgPack00xAnalyzerTests.SuppressSourceGeneration_KeyValidation",
     "MsgPack00xAnalyzerTests.SuppressSourceGeneration_KeyValidationOnFields"
    ],
    "log": "evidence/var-2234-v2/logs/fail_without_fix.full_suite.log"
   },
   "new_failed": 8,
   "new_total": 16
  },
  {
   "id": "tests.full_suite",
   "tool": "dotnet test",
   "tool_version": "8.0.402",
   "status": "pass",
   "summary": "tests/MessagePack.SourceGenerator.Tests: 183 tests, 183 passed, 0 failed (0 not failing on base, 0 also failing on base)",
   "project": "tests/MessagePack.SourceGenerator.Tests",
   "total": 183,
   "passed": 183,
   "failed": 0,
   "failures_not_on_base": [],
   "failures_also_on_base": [],
   "log": "evidence/var-2234-v2/logs/tests_full_suite.log",
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
    "diff_added_lines": 841,
    "files": 9,
    "paths": 9,
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
    "diff": "git diff 32258fdb 6a3d2cb0 (added lines and file paths)",
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
   "summary": "8 mutants of the changed source lines: 7 killed, 1 survived; 7 of 8 mutated hunks have a killed mutant; surviving hunks: TypeCollector.cs:857; 11 hunks not mutated",
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
    "FullyQualifiedName~MsgPack00xAnalyzerTests.|FullyQualifiedName~GenerationTests."
   ],
   "tests_judged": [
    "GenerationTests.SuppressSourceGeneration_ClosedGenericIsNotRegistered",
    "GenerationTests.SuppressSourceGeneration_MemberTypesAreNotCollected",
    "GenerationTests.SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(usesMapMode: False)",
    "GenerationTests.SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(usesMapMode: True)",
    "MsgPack00xAnalyzerTests.DuplicateKeysAreReportedWithoutCrashing",
    "MsgPack00xAnalyzerTests.MixedKeysAreReportedWithoutCrashing",
    "MsgPack00xAnalyzerTests.SuppressSourceGeneration_AllowPrivateRequired",
    "MsgPack00xAnalyzerTests.SuppressSourceGeneration_GenericTypeWithoutIssues",
    "MsgPack00xAnalyzerTests.SuppressSourceGeneration_KeyValidation",
    "MsgPack00xAnalyzerTests.SuppressSourceGeneration_KeyValidationOnFields",
    "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MapMode",
    "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MemberTypeNotSerializable",
    "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MissingKeyInBaseType",
    "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MissingKeyOnField",
    "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MissingKeyOnProperty",
    "MsgPack00xAnalyzerTests.SuppressSourceGeneration_ValidTypeHasNoDiagnostics"
   ],
   "not_covered": "ExecutionTests/MapModeExecutionTests (SDK 9) are not run against the mutants; files that are not C# are not mutated",
   "hunks": [
    {
     "id": "H1",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      640,
      645
     ],
     "code_lines": [
      642,
      644
     ],
     "mutants": [
      "M1"
     ],
     "status": "killed"
    },
    {
     "id": "H2",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      692,
      696
     ],
     "code_lines": [
      692,
      694,
      695
     ],
     "mutants": [
      "M2"
     ],
     "status": "killed"
    },
    {
     "id": "H3",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      726,
      729
     ],
     "code_lines": [
      729
     ],
     "mutants": [],
     "status": "not_mutated",
     "why": "left out by the budget (1 candidates; at most 8 mutants per change)"
    },
    {
     "id": "H4",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      857,
      857
     ],
     "code_lines": [
      857
     ],
     "mutants": [
      "M3"
     ],
     "status": "survived"
    },
    {
     "id": "H5",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      888,
      888
     ],
     "code_lines": [
      888
     ],
     "mutants": [],
     "status": "not_mutated",
     "why": "left out by the budget (4 candidates; at most 8 mutants per change)"
    },
    {
     "id": "H6",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1029,
      1030
     ],
     "code_lines": [
      1030
     ],
     "mutants": [
      "M4"
     ],
     "status": "killed"
    },
    {
     "id": "H7",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1037,
      1037
     ],
     "code_lines": [
      1037
     ],
     "mutants": [],
     "status": "not_mutated",
     "why": "no operator applies to its lines"
    },
    {
     "id": "H8",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1039,
      1044
     ],
     "code_lines": [
      1039,
      1041,
      1043
     ],
     "mutants": [],
     "status": "not_mutated",
     "why": "left out by the budget (1 candidates; at most 8 mutants per change)"
    },
    {
     "id": "H9",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1046,
      1046
     ],
     "code_lines": [
      1046
     ],
     "mutants": [
      "M5"
     ],
     "status": "killed"
    },
    {
     "id": "H10",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1053,
      1053
     ],
     "code_lines": [
      1053
     ],
     "mutants": [],
     "status": "not_mutated",
     "why": "no operator applies to its lines"
    },
    {
     "id": "H11",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1055,
      1060
     ],
     "code_lines": [
      1055,
      1057,
      1059
     ],
     "mutants": [],
     "status": "not_mutated",
     "why": "left out by the budget (1 candidates; at most 8 mutants per change)"
    },
    {
     "id": "H12",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1065,
      1065
     ],
     "code_lines": [
      1065
     ],
     "mutants": [
      "M6"
     ],
     "status": "killed"
    },
    {
     "id": "H13",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1169,
      1170
     ],
     "code_lines": [
      1170
     ],
     "mutants": [],
     "status": "not_mutated",
     "why": "left out by the budget (4 candidates; at most 8 mutants per change)"
    },
    {
     "id": "H14",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1177,
      1177
     ],
     "code_lines": [
      1177
     ],
     "mutants": [],
     "status": "not_mutated",
     "why": "no operator applies to its lines"
    },
    {
     "id": "H15",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1179,
      1184
     ],
     "code_lines": [
      1179,
      1181,
      1183
     ],
     "mutants": [
      "M7"
     ],
     "status": "killed"
    },
    {
     "id": "H16",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1186,
      1186
     ],
     "code_lines": [
      1186
     ],
     "mutants": [],
     "status": "not_mutated",
     "why": "left out by the budget (4 candidates; at most 8 mutants per change)"
    },
    {
     "id": "H17",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1193,
      1193
     ],
     "code_lines": [
      1193
     ],
     "mutants": [],
     "status": "not_mutated",
     "why": "no operator applies to its lines"
    },
    {
     "id": "H18",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1195,
      1200
     ],
     "code_lines": [
      1195,
      1197,
      1199
     ],
     "mutants": [
      "M8"
     ],
     "status": "killed"
    },
    {
     "id": "H19",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1205,
      1205
     ],
     "code_lines": [
      1205
     ],
     "mutants": [],
     "status": "not_mutated",
     "why": "left out by the budget (4 candidates; at most 8 mutants per change)"
    }
   ],
   "surviving_hunks": [
    "H4"
   ],
   "mutants": [
    {
     "id": "M1",
     "hunk": "H1",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "line": 642,
     "operator": "negate_condition",
     "before": "        if (this.options.IsGeneratingSource && !type.IsDefinition && this.IsSourceGenerationSuppressed(type.OriginalDefinition))",
     "after": "        if (!(this.options.IsGeneratingSource && !type.IsDefinition && this.IsSourceGenerationSuppressed(type.OriginalDefinition)))",
     "log": [
      "evidence/var-2234-v2/logs/mutation/M1.build.log",
      "evidence/var-2234-v2/logs/mutation/M1.test.1.log"
     ],
     "diff": "evidence/var-2234-v2/logs/mutation/M1.diff",
     "killed_by": [
      "GenerationTests.SuppressSourceGeneration_ClosedGenericIsNotRegistered"
     ],
     "existing_tests_failed": [
      "GenerationTests.GenericDataTypeWithPrivateMember",
      "GenerationTests.GenericType",
      "GenerationTests.GenericTypeArg",
      "GenerationTests.GenericType_CollidingTypeNames",
      "GenerationTests.GenericWithConstraintsThatReferenceTypeParameter",
      "GenerationTests.MixType_CollidingTypeNames",
      "MsgPack00xAnalyzerTests.AddAttributeToGenericType"
     ],
     "outcome": "killed",
     "tests_run": 92
    },
    {
     "id": "M2",
     "hunk": "H2",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "line": 695,
     "operator": "return_default",
     "before": "        return contractAttr?.NamedArguments.FirstOrDefault(kvp => kvp.Key == Constants.SuppressSourceGenerationPropertyName).Value.Value is true;",
     "after": "        return default;",
     "log": [
      "evidence/var-2234-v2/logs/mutation/M2.build.log",
      "evidence/var-2234-v2/logs/mutation/M2.test.1.log"
     ],
     "diff": "evidence/var-2234-v2/logs/mutation/M2.diff",
     "killed_by": [
      "GenerationTests.SuppressSourceGeneration_ClosedGenericIsNotRegistered"
     ],
     "existing_tests_failed": [],
     "outcome": "killed",
     "tests_run": 92
    },
    {
     "id": "M3",
     "hunk": "H4",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "line": 857,
     "operator": "negate_condition",
     "before": "                            if (specialFormatter is null && collectMemberTypes)",
     "after": "                            if (!(specialFormatter is null && collectMemberTypes))",
     "log": [
      "evidence/var-2234-v2/logs/mutation/M3.build.log",
      "evidence/var-2234-v2/logs/mutation/M3.test.1.log"
     ],
     "diff": "evidence/var-2234-v2/logs/mutation/M3.diff",
     "killed_by": [],
     "existing_tests_failed": [
      "GenerationTests.EnumFormatter(container: Namespace, usesMapMode: True)",
      "GenerationTests.EnumFormatter(container: NestingClass, usesMapMode: True)",
      "GenerationTests.EnumFormatter(container: None, usesMapMode: True)"
     ],
     "outcome": "survived",
     "tests_run": 92
    },
    {
     "id": "M4",
     "hunk": "H6",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "line": 1030,
     "operator": "negate_condition",
     "before": "                    if (isIntKey && intKey is not null)",
     "after": "                    if (!(isIntKey && intKey is not null))",
     "log": [
      "evidence/var-2234-v2/logs/mutation/M4.build.log",
      "evidence/var-2234-v2/logs/mutation/M4.test.1.log"
     ],
     "diff": "evidence/var-2234-v2/logs/mutation/M4.diff",
     "killed_by": [
      "GenerationTests.SuppressSourceGeneration_ClosedGenericIsNotRegistered",
      "GenerationTests.SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(usesMapMode: False)",
      "MsgPack00xAnalyzerTests.DuplicateKeysAreReportedWithoutCrashing",
      "MsgPack00xAnalyzerTests.MixedKeysAreReportedWithoutCrashing",
      "MsgPack00xAnalyzerTests.SuppressSourceGeneration_KeyValidation"
     ],
     "existing_tests_failed": [
      "GenerationTests.AdditionalAllowTypes",
      "GenerationTests.AdditionalFormatterTypes",
      "GenerationTests.AdditionalFormatterTypes_RedundantAttribute",
      "GenerationTests.Array2DJaggedProperty",
      "GenerationTests.ArrayTypedProperty",
      "GenerationTests.CustomFormatterViaAttributeOnProperty(usesMapMode: False)",
      "GenerationTests.DeserializingConstructorParameterMemberTypeAssignability_Incompatible",
      "GenerationTests.DeserializingConstructorParameterMemberTypeAssignability_MemberAssignsToParamType",
      "GenerationTests.EmbeddedTypes",
      "GenerationTests.EnumFormatter(container: Namespace, usesMapMode: False)",
      "GenerationTests.EnumFormatter(container: NestingClass, usesMapMode: False)",
      "GenerationTests.EnumFormatter(container: None, usesMapMode: False)",
      "GenerationTests.EnumFormatter_CollidingTypeNames",
      "GenerationTests.GenericType",
      "GenerationTests.GenericTypeArg",
      "GenerationTests.GenericType_CollidingTypeNames",
      "GenerationTests.GenericWithConstraintsThatReferenceTypeParameter",
      "GenerationTests.ImplicitFormatterTypes",
      "GenerationTests.InterfaceUnionUsedWithNullableRefAnnotation",
      "GenerationTests.MixType_CollidingTypeNames",
      "GenerationTests.NoPrivateAccessNeeded",
      "GenerationTests.NoPrivateMemberCollected",
      "GenerationTests.NonDefaultDeserializingConstructor_Private",
      "GenerationTests.NonGenericType_CollidingTypeNames",
      "GenerationTests.SystemCollectionsObjectModelCollection",
      "GenerationTests.SystemMemoryTypes",
      "GenerationTests.UnionFormatter(container: Namespace)",
      "GenerationTests.UnionFormatter(container: NestingClass)",
      "GenerationTests.UnionFormatter(container: None)",
      "MsgPack00xAnalyzerTests.AddAttributeToTypeForRecordPrimaryConstructor",
      "MsgPack00xAnalyzerTests.AddAttributesToMembersOfRecordWithPrimaryCtor",
      "MsgPack00xAnalyzerTests.NullStringKey"
     ],
     "outcome": "killed",
     "tests_run": 92
    },
    {
     "id": "M5",
     "hunk": "H9",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "line": 1046,
     "operator": "negate_condition",
     "before": "                    else if (!isIntKey && stringKey is not null)",
     "after": "                    else if (!(!isIntKey && stringKey is not null))",
     "log": [
      "evidence/var-2234-v2/logs/mutation/M5.build.log",
      "evidence/var-2234-v2/logs/mutation/M5.test.1.log"
     ],
     "diff": "evidence/var-2234-v2/logs/mutation/M5.diff",
     "killed_by": [
      "MsgPack00xAnalyzerTests.DuplicateKeysAreReportedWithoutCrashing",
      "MsgPack00xAnalyzerTests.MixedKeysAreReportedWithoutCrashing"
     ],
     "existing_tests_failed": [
      "MsgPack00xAnalyzerTests.NullStringKey"
     ],
     "outcome": "killed",
     "tests_run": 92
    },
    {
     "id": "M6",
     "hunk": "H12",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "line": 1065,
     "operator": "negate_condition",
     "before": "                    if (messagePackFormatter == null && collectMemberTypes)",
     "after": "                    if (!(messagePackFormatter == null && collectMemberTypes))",
     "log": [
      "evidence/var-2234-v2/logs/mutation/M6.build.log",
      "evidence/var-2234-v2/logs/mutation/M6.test.1.log"
     ],
     "diff": "evidence/var-2234-v2/logs/mutation/M6.diff",
     "killed_by": [
      "GenerationTests.SuppressSourceGeneration_MemberTypesAreNotCollected",
      "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MemberTypeNotSerializable"
     ],
     "existing_tests_failed": [
      "GenerationTests.Array2DJaggedProperty",
      "GenerationTests.ArrayTypedProperty",
      "GenerationTests.DeserializingConstructorParameterMemberTypeAssignability_Incompatible",
      "GenerationTests.EnumFormatter(container: Namespace, usesMapMode: False)",
      "GenerationTests.EnumFormatter(container: NestingClass, usesMapMode: False)",
      "GenerationTests.EnumFormatter(container: None, usesMapMode: False)",
      "GenerationTests.EnumFormatter_CollidingTypeNames",
      "GenerationTests.GenericType",
      "GenerationTests.GenericType_CollidingTypeNames",
      "GenerationTests.MixType_CollidingTypeNames",
      "GenerationTests.SystemCollectionsObjectModelCollection",
      "GenerationTests.SystemMemoryTypes",
      "MsgPack00xAnalyzerTests.AddAttributeToGenericType",
      "MsgPack00xAnalyzerTests.AddAttributeToTypeForRecord1",
      "MsgPack00xAnalyzerTests.AddAttributeToTypeForRecord2",
      "MsgPack00xAnalyzerTests.AddAttributeToTypeForRecordPrimaryConstructor",
      "MsgPack00xAnalyzerTests.AddAttributeToType_Properties",
      "MsgPack00xAnalyzerTests.InvalidMessageFormatterType"
     ],
     "outcome": "killed",
     "tests_run": 92
    },
    {
     "id": "M7",
     "hunk": "H15",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "line": 1183,
     "operator": "remove_call",
     "before": "                            intMembers.Add(member.IntKey, (member, item.Type));",
     "after": "                            { }",
     "log": [
      "evidence/var-2234-v2/logs/mutation/M7.build.log",
      "evidence/var-2234-v2/logs/mutation/M7.test.1.log"
     ],
     "diff": "evidence/var-2234-v2/logs/mutation/M7.diff",
     "killed_by": [
      "MsgPack00xAnalyzerTests.DuplicateKeysAreReportedWithoutCrashing",
      "MsgPack00xAnalyzerTests.SuppressSourceGeneration_KeyValidationOnFields"
     ],
     "existing_tests_failed": [
      "GenerationTests.CustomFormatterForGenericWithConstraints",
      "GenerationTests.CustomFormatterViaAttributeOnField(usesMapMode: False)",
      "GenerationTests.CustomFormatterWithSingletonPattern",
      "GenerationTests.GenericCustomFormatter",
      "GenerationTests.GenericDataTypeWithPrivateMember",
      "GenerationTests.NestedMessagePackObjects_Array",
      "GenerationTests.NoFieldWithCustomFormatterCollected",
      "GenerationTests.SimplifiedNameForKeywordsAndSyntaxSugar",
      "GenerationTests.SpecifyFormatterFromStockSet"
     ],
     "outcome": "killed",
     "tests_run": 92
    },
    {
     "id": "M8",
     "hunk": "H18",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "line": 1199,
     "operator": "remove_call",
     "before": "                            stringMembers.Add(member.StringKey, (member, item.Type));",
     "after": "                            { }",
     "log": [
      "evidence/var-2234-v2/logs/mutation/M8.build.log",
      "evidence/var-2234-v2/logs/mutation/M8.test.1.log"
     ],
     "diff": "evidence/var-2234-v2/logs/mutation/M8.diff",
     "killed_by": [
      "MsgPack00xAnalyzerTests.DuplicateKeysAreReportedWithoutCrashing"
     ],
     "existing_tests_failed": [],
     "outcome": "killed",
     "tests_run": 92
    }
   ],
   "kills_by_test": [
    {
     "name": "GenerationTests.SuppressSourceGeneration_ClosedGenericIsNotRegistered",
     "killed": [
      "M1",
      "M2",
      "M4"
     ]
    },
    {
     "name": "GenerationTests.SuppressSourceGeneration_MemberTypesAreNotCollected",
     "killed": [
      "M6"
     ]
    },
    {
     "name": "GenerationTests.SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(usesMapMode: False)",
     "killed": [
      "M4"
     ]
    },
    {
     "name": "GenerationTests.SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(usesMapMode: True)",
     "killed": []
    },
    {
     "name": "MsgPack00xAnalyzerTests.DuplicateKeysAreReportedWithoutCrashing",
     "killed": [
      "M4",
      "M5",
      "M7",
      "M8"
     ]
    },
    {
     "name": "MsgPack00xAnalyzerTests.MixedKeysAreReportedWithoutCrashing",
     "killed": [
      "M4",
      "M5"
     ]
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_AllowPrivateRequired",
     "killed": []
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_GenericTypeWithoutIssues",
     "killed": []
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_KeyValidation",
     "killed": [
      "M4"
     ]
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_KeyValidationOnFields",
     "killed": [
      "M7"
     ]
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MapMode",
     "killed": []
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MemberTypeNotSerializable",
     "killed": [
      "M6"
     ]
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MissingKeyInBaseType",
     "killed": []
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MissingKeyOnField",
     "killed": []
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_MissingKeyOnProperty",
     "killed": []
    },
    {
     "name": "MsgPack00xAnalyzerTests.SuppressSourceGeneration_ValidTypeHasNoDiagnostics",
     "killed": []
    }
   ],
   "log": "evidence/var-2234-v2/logs/mutation/"
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
  "raw_runs": "evidence/var-scripts/runs.sh -> /data/work/var/out/var-2234-v2[-fwf] (not committed; logs copied to evidence/var-2234-v2/logs/)"
 }
}
```

## Files changed (9: 3 non-generated, 6 generated)
- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs (+60 -28, source)
- tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs (+97 -0, test)
- tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs (+319 -0, test)

Generated files (6; contents and diffs NOT provided):
- tests/MessagePack.SourceGenerator.Tests/Resources/SuppressSourceGeneration_ClosedGenericIsNotRegistered/Formatters.MessagePack.GeneratedMessagePackResolver.HolderFormatter.g.cs (+58 -0)
- tests/MessagePack.SourceGenerator.Tests/Resources/SuppressSourceGeneration_ClosedGenericIsNotRegistered/MessagePack.GeneratedMessagePackResolver.g.cs (+63 -0)
- tests/MessagePack.SourceGenerator.Tests/Resources/SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(False)/Formatters.MessagePack.GeneratedMessagePackResolver.BFormatter.g.cs (+56 -0)
- tests/MessagePack.SourceGenerator.Tests/Resources/SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(False)/MessagePack.GeneratedMessagePackResolver.g.cs (+63 -0)
- tests/MessagePack.SourceGenerator.Tests/Resources/SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(True)/Formatters.MessagePack.GeneratedMessagePackResolver.BFormatter.g.cs (+62 -0)
- tests/MessagePack.SourceGenerator.Tests/Resources/SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(True)/MessagePack.GeneratedMessagePackResolver.g.cs (+63 -0)

## Diff (non-generated files)
```diff
diff --git a/src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs b/src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs
index e121773d..50ae42db 100644
--- a/src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs
+++ b/src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs
@@ -637,6 +637,13 @@ public class TypeCollector
             }
         }
 
+        // A closed generic type whose definition opted out of source generation has no source generated formatter,
+        // so we must not register one with the generated resolver (it would reference a formatter type that does not exist).
+        if (this.options.IsGeneratingSource && !type.IsDefinition && this.IsSourceGenerationSuppressed(type.OriginalDefinition))
+        {
+            return;
+        }
+
         // Generic types
         if (type.IsDefinition)
         {
@@ -682,6 +689,12 @@ public class TypeCollector
         }
     }
 
+    private bool IsSourceGenerationSuppressed(INamedTypeSymbol type)
+    {
+        AttributeData? contractAttr = type.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.MessagePackObjectAttribute));
+        return contractAttr?.NamedArguments.FirstOrDefault(kvp => kvp.Key == Constants.SuppressSourceGenerationPropertyName).Value.Value is true;
+    }
+
     private void CheckValidMessagePackFormatterAttribute(AttributeData formatterAttribute)
     {
         if (formatterAttribute.ConstructorArguments[0].Value is ITypeSymbol formatterType)
@@ -710,6 +723,11 @@ public class TypeCollector
         bool? suppressSourceGeneration = (bool?)contractAttr?.NamedArguments.FirstOrDefault(kvp => kvp.Key == Constants.SuppressSourceGenerationPropertyName).Value.Value;
         bool? allowPrivateAttribute = (bool?)contractAttr?.NamedArguments.FirstOrDefault(kvp => kvp.Key == Constants.AllowPrivatePropertyName).Value.Value;
 
+        // When the type opted out of source generation, we still validate its members so the analyzer can report diagnostics (e.g. a missing [Key]),
+        // but when generating source we must not collect the types of its members: no formatter will be generated for this type,
+        // so any formatter generated (or registered with the resolver) only because this type references it is at best unused and at worst invalid.
+        bool collectMemberTypes = suppressSourceGeneration is not true || !this.options.IsGeneratingSource;
+
         if (contractAttr is null)
         {
             ////this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.TypeMustBeMessagePackObject, ((BaseTypeDeclarationSyntax)type.DeclaringSyntaxReferences[0].GetSyntax()).Identifier.GetLocation(), type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat)));
@@ -836,7 +854,7 @@ public class TypeCollector
                                 stringMembers.Add(member.StringKey, (member, item.Type));
                             }
 
-                            if (specialFormatter is null)
+                            if (specialFormatter is null && collectMemberTypes)
                             {
                                 this.CollectCore(item.Type, item); // recursive collect
                             }
@@ -867,7 +885,7 @@ public class TypeCollector
                                 stringMembers.Add(member.StringKey, (member, item.Type));
                             }
 
-                            if (specialFormatter is null)
+                            if (specialFormatter is null && collectMemberTypes)
                             {
                                 this.CollectCore(item.Type, item); // recursive collect
                             }
@@ -1008,36 +1026,43 @@ public class TypeCollector
                         }
                     }
 
-                    if (isIntKey)
+                    // A member whose key is of the wrong kind (or null) has already been reported above and cannot be added to the member map.
+                    if (isIntKey && intKey is not null)
                     {
                         if (intMembers.ContainsKey(intKey!.Value))
                         {
+                            // Report the collision and keep the first member, rather than throwing (which would crash the analyzer with AD0001).
                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.KeysMustBeUnique, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
                         }
-
-                        var member = new MemberSerializationInfo(true, isWritable, isReadable, isInitOnly, item.IsRequired, intKey!.Value, item.Name, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
+                        else
                         {
-                            DeclaringType = GetDeclaringTypeIfColliding(item),
-                        };
-                        intMembers.Add(member.IntKey, (member, item.Type));
+                            var member = new MemberSerializationInfo(true, isWritable, isReadable, isInitOnly, item.IsRequired, intKey!.Value, item.Name, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
+                            {
+                                DeclaringType = GetDeclaringTypeIfColliding(item),
+                            };
+                            intMembers.Add(member.IntKey, (member, item.Type));
+                        }
                     }
-                    else if (stringKey is not null)
+                    else if (!isIntKey && stringKey is not null)
                     {
                         if (stringMembers.ContainsKey(stringKey!))
                         {
+                            // Report the collision and keep the first member, rather than throwing (which would crash the analyzer with AD0001).
                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.KeysMustBeUnique, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
                         }
-
-                        var member = new MemberSerializationInfo(true, isWritable, isReadable, isInitOnly, item.IsRequired, hiddenIntKey++, stringKey!, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
+                        else
                         {
-                            DeclaringType = GetDeclaringTypeIfColliding(item),
-                        };
-                        stringMembers.Add(member.StringKey, (member, item.Type));
+                            var member = new MemberSerializationInfo(true, isWritable, isReadable, isInitOnly, item.IsRequired, hiddenIntKey++, stringKey!, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
+                            {
+                                DeclaringType = GetDeclaringTypeIfColliding(item),
+                            };
+                            stringMembers.Add(member.StringKey, (member, item.Type));
+                        }
                     }
 
                     var messagePackFormatter = item.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.FormatterAttribute))?.ConstructorArguments[0];
 
-                    if (messagePackFormatter == null)
+                    if (messagePackFormatter == null && collectMemberTypes)
                     {
                         // recursive collect
                         this.CollectCore(item.Type, item);
@@ -1141,36 +1166,43 @@ public class TypeCollector
                         }
                     }
 
-                    if (isIntKey)
+                    // A member whose key is of the wrong kind (or null) has already been reported above and cannot be added to the member map.
+                    if (isIntKey && intKey is not null)
                     {
                         if (intMembers.ContainsKey(intKey!.Value))
                         {
+                            // Report the collision and keep the first member, rather than throwing (which would crash the analyzer with AD0001).
                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.KeysMustBeUnique, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
                         }
-
-                        var member = new MemberSerializationInfo(true, IsWritable: !item.IsReadOnly, IsReadable: true, IsInitOnly: false, item.IsRequired, intKey!.Value, item.Name, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
+                        else
                         {
-                            DeclaringType = GetDeclaringTypeIfColliding(item),
-                        };
-                        intMembers.Add(member.IntKey, (member, item.Type));
+                            var member = new MemberSerializationInfo(true, IsWritable: !item.IsReadOnly, IsReadable: true, IsInitOnly: false, item.IsRequired, intKey!.Value, item.Name, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
+                            {
+                                DeclaringType = GetDeclaringTypeIfColliding(item),
+                            };
+                            intMembers.Add(member.IntKey, (member, item.Type));
+                        }
                     }
-                    else
+                    else if (!isIntKey && stringKey is not null)
                     {
                         if (stringMembers.ContainsKey(stringKey!))
                         {
+                            // Report the collision and keep the first member, rather than throwing (which would crash the analyzer with AD0001).
                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.KeysMustBeUnique, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
                         }
-
-                        var member = new MemberSerializationInfo(true, IsWritable: !item.IsReadOnly, IsReadable: true, IsInitOnly: false, item.IsRequired, hiddenIntKey++, stringKey!, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
+                        else
                         {
-                            DeclaringType = GetDeclaringTypeIfColliding(item),
-                        };
-                        stringMembers.Add(member.StringKey, (member, item.Type));
+                            var member = new MemberSerializationInfo(true, IsWritable: !item.IsReadOnly, IsReadable: true, IsInitOnly: false, item.IsRequired, hiddenIntKey++, stringKey!, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
+                            {
+                                DeclaringType = GetDeclaringTypeIfColliding(item),
+                            };
+                            stringMembers.Add(member.StringKey, (member, item.Type));
+                        }
                     }
 
                     var messagePackFormatter = item.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.FormatterAttribute))?.ConstructorArguments[0];
 
-                    if (messagePackFormatter == null)
+                    if (messagePackFormatter == null && collectMemberTypes)
                     {
                         // recursive collect
                         this.CollectCore(item.Type, item);

diff --git a/tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs b/tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs
index e390a39e..67d01cd5 100644
--- a/tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs
+++ b/tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs
@@ -1144,4 +1144,101 @@ public class MyGenericType<T>
 
         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
     }
+
+    /// <summary>
+    /// A type that opts out of source generation must not cause formatters to be generated for the types of its members,
+    /// since it gets no source generated formatter that would use them.
+    /// </summary>
+    [Fact]
+    public async Task SuppressSourceGeneration_MemberTypesAreNotCollected()
+    {
+        string testSource = /* lang=c#-test */ """
+            using System.Collections.Generic;
+            using MessagePack;
+
+            [MessagePackObject(SuppressSourceGeneration = true)]
+            public class A
+            {
+                [Key(0)]
+                public Dictionary<string, IItem> Items { get; set; }
+
+                [Key(1)]
+                public MyEnum Enum { get; set; }
+
+                [Key(2)]
+                public IItem Item;
+            }
+
+            public interface IItem
+            {
+                object Value { get; }
+            }
+
+            public enum MyEnum { A, B }
+            """;
+
+        await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
+    }
+
+    /// <summary>
+    /// Types that are themselves attributed still get a formatter, even when only a suppressed type references them.
+    /// </summary>
+    [Theory, PairwiseData]
+    public async Task SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(bool usesMapMode)
+    {
+        string testSource = /* lang=c#-test */ """
+            using MessagePack;
+
+            [MessagePackObject(SuppressSourceGeneration = true)]
+            public class A
+            {
+                [Key(0)]
+                public B Value { get; set; }
+
+                [Key(1)]
+                public MyEnum Enum;
+            }
+
+            [MessagePackObject]
+            public class B
+            {
+                [Key(0)]
+                public int Value { get; set; }
+            }
+
+            public enum MyEnum { A, B }
+            """;
+
+        await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, options: new() { Generator = new() { Formatters = new() { UsesMapMode = usesMapMode } } }, testMethod: $"{nameof(SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated)}({usesMapMode})");
+    }
+
+    /// <summary>
+    /// A closed generic type whose definition opted out of source generation must not be registered with the generated resolver,
+    /// since its formatter is never generated.
+    /// </summary>
+    [Fact]
+    public async Task SuppressSourceGeneration_ClosedGenericIsNotRegistered()
+    {
+        string testSource = /* lang=c#-test */ """
+            using MessagePack;
+
+            [MessagePackObject]
+            public class Holder
+            {
+                [Key(0)]
+                public Wrapper<MyEnum> Value { get; set; }
+            }
+
+            [MessagePackObject(SuppressSourceGeneration = true)]
+            public class Wrapper<T>
+            {
+                [Key(0)]
+                public T Value { get; set; }
+            }
+
+            public enum MyEnum { A, B }
+            """;
+
+        await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
+    }
 }

diff --git a/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs b/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs
index d39d74ef..74f52448 100644
--- a/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs
+++ b/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs
@@ -1087,4 +1087,323 @@ public class Bar : Foo
 
         await VerifyCS.VerifyAnalyzerAsync(test);
     }
+
+    [Fact]
+    public async Task SuppressSourceGeneration_MissingKeyOnProperty()
+    {
+        string test = /* lang=c#-test */ """
+            using MessagePack;
+
+            [MessagePackObject(SuppressSourceGeneration = true)]
+            public class A
+            {
+                [Key(0)]
+                public int Prop1 { get; set; }
+
+                public int {|MsgPack004:Prop2|} { get; set; }
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
+    [Fact]
+    public async Task SuppressSourceGeneration_MissingKeyOnField()
+    {
+        string test = /* lang=c#-test */ """
+            using MessagePack;
+
+            [MessagePackObject(SuppressSourceGeneration = true)]
+            public class A
+            {
+                [Key(0)]
+                public int Field1;
+
+                public int {|MsgPack004:Field2|};
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
+    [Fact]
+    public async Task SuppressSourceGeneration_MissingKeyInBaseType()
+    {
+        string test = /* lang=c#-test */ """
+            using MessagePack;
+
+            public class Base
+            {
+                public int BaseProp { get; set; }
+            }
+
+            [MessagePackObject(SuppressSourceGeneration = true)]
+            public class Derived : {|MsgPack004:Base|}
+            {
+                [Key(0)]
+                public int Prop1 { get; set; }
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
+    [Fact]
+    public async Task SuppressSourceGeneration_KeyValidation()
+    {
+        string test = /* lang=c#-test */ """
+            using MessagePack;
+
+            [MessagePackObject(SuppressSourceGeneration = true)]
+            public class A
+            {
+                [Key(0)]
+                public int Prop1 { get; set; }
+
+                {|MsgPack005:[Key(0)]
+                public int Prop2 { get; set; }|}
+
+                {|MsgPack005:[Key("x")]
+                public int Prop3 { get; set; }|}
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
+    [Fact]
+    public async Task SuppressSourceGeneration_AllowPrivateRequired()
+    {
+        string test = /* lang=c#-test */ """
+            using MessagePack;
+
+            [{|MsgPack015:MessagePackObject(SuppressSourceGeneration = true)|}]
+            internal class A
+            {
+                [Key(0)]
+                public int Prop1 { get; set; }
+            }
+            """;
+
+        await VerifyCS.VerifyAnalyzerAsync(test);
+    }
+
+    [Fact]
+    public async Task SuppressSourceGeneration_MemberTypeNotSerializable()
+    {
+        string test = /* lang=c#-test */ """
+            using MessagePack;
+
+            public class NotAttributed
+            {
+            }
+
+            [MessagePackObject(SuppressSourceGeneration = true)]
+            public class A
+            {
+                [Key(0)]
+                public NotAttributed {|MsgPack003:Prop1|} { get; set; }
+            }
+            """;
+
+        await VerifyCS.VerifyAnalyzerAsync(test);
+    }
+
+    [Fact]
+    public async Task SuppressSourceGeneration_ValidTypeHasNoDiagnostics()
+    {
+        string test = /* lang=c#-test */ """
+            using MessagePack;
+
+            [MessagePackObject(SuppressSourceGeneration = true)]
+            public class A
+            {
+                [Key(0)]
+                public int Prop1 { get; set; }
+
+                [Key(1)]
+                public string Field1;
+
+                [IgnoreMember]
+                public int Ignored { get; set; }
+            }
+            """;
+
+        await VerifyCS.VerifyAnalyzerAsync(test);
+    }
+
+    [Fact]
+    public async Task SuppressSourceGeneration_KeyValidationOnFields()
+    {
+        string test = /* lang=c#-test */ """
+            using MessagePack;
+
+            [MessagePackObject(SuppressSourceGeneration = true)]
+            public class A
+            {
+                [Key(0)]
+                public int Field1;
+
+                [Key(0)]
+                public int {|MsgPack005:Field2|};
+
+                [Key("x")]
+                public int {|MsgPack005:Field3|};
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
+    [Fact]
+    public async Task SuppressSourceGeneration_GenericTypeWithoutIssues()
+    {
+        string test = /* lang=c#-test */ """
+            using MessagePack;
+
+            [MessagePackObject(SuppressSourceGeneration = true)]
+            public class Wrapper<T>
+            {
+                [Key(0)]
+                public T Value { get; set; }
+            }
+
+            [MessagePackObject]
+            public class Holder
+            {
+                [Key(0)]
+                public Wrapper<int> Value { get; set; }
+            }
+            """;
+
+        await VerifyCS.VerifyAnalyzerAsync(test);
+    }
+
+    [Fact]
+    public async Task SuppressSourceGeneration_MapMode()
+    {
+        string test = /* lang=c#-test */ """
+            using MessagePack;
+
+            [MessagePackObject(true, SuppressSourceGeneration = true)]
+            public class Base
+            {
+                public string Prop { get; set; }
+            }
+
+            [MessagePackObject(true, SuppressSourceGeneration = true)]
+            public class Derived : Base
+            {
+                public new string {|MsgPack018:Prop|} { get; set; }
+            }
+            """;
+
+        await VerifyCS.VerifyAnalyzerAsync(test);
+    }
+
+    [Fact]
+    public async Task DuplicateKeysAreReportedWithoutCrashing()
+    {
+        string test = /* lang=c#-test */ """
+            using MessagePack;
+
+            [MessagePackObject]
+            public class IntKeys
+            {
+                [Key(0)]
+                public int Prop1 { get; set; }
+
+                {|MsgPack005:[Key(0)]
+                public int Prop2 { get; set; }|}
+
+                [Key(1)]
+                public int Field1;
+
+                [Key(1)]
+                public int {|MsgPack005:Field2|};
+            }
+
+            [MessagePackObject]
+            public class StringKeys
+            {
+                [Key("a")]
+                public int Prop1 { get; set; }
+
+                {|MsgPack005:[Key("a")]
+                public int Prop2 { get; set; }|}
+
+                [Key("b")]
+                public int Field1;
+
+                [Key("b")]
+                public int {|MsgPack005:Field2|};
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
+    [Fact]
+    public async Task MixedKeysAreReportedWithoutCrashing()
+    {
+        string test = /* lang=c#-test */ """
+            using MessagePack;
+
+            [MessagePackObject]
+            public class IntFirst
+            {
+                [Key(0)]
+                public int Prop1 { get; set; }
+
+                {|MsgPack005:[Key("a")]
+                public int Prop2 { get; set; }|}
+
+                [Key("b")]
+                public int {|MsgPack005:Field1|};
+            }
+
+            [MessagePackObject]
+            public class StringFirst
+            {
+                [Key("a")]
+                public int Prop1 { get; set; }
+
+                {|MsgPack005:[Key(1)]
+                public int Prop2 { get; set; }|}
+
+                [Key(2)]
+                public int {|MsgPack005:Field1|};
+            }
+            """;
+
+        await new VerifyCS.Test
+        {
+            TestCode = test,
+            MarkupOptions = MarkupOptions.UseFirstDescriptor,
+        }.RunAsync();
+    }
 }

```

## File contents (line numbers in the gutter; quote the text after '| ')

### src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at head (6a3d2cb0), around the changed lines
```
  ... lines 1-606 not shown ...
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
  640|         // A closed generic type whose definition opted out of source generation has no source generated formatter,
  641|         // so we must not register one with the generated resolver (it would reference a formatter type that does not exist).
  642|         if (this.options.IsGeneratingSource && !type.IsDefinition && this.IsSourceGenerationSuppressed(type.OriginalDefinition))
  643|         {
  644|             return;
  645|         }
  646| 
  647|         // Generic types
  648|         if (type.IsDefinition)
  649|         {
  650|             this.CollectGenericUnion(type);
  651|             this.CollectObject(type, callerSymbol);
  652|         }
  653|         else
  654|         {
  655|             // Collect substituted types for the properties and fields.
  656|             // NOTE: It is used to register formatters from nested generic type.
  657|             //       However, closed generic types such as `Foo<string>` are not registered as a formatter.
  658|             this.GetObjectInfo(type, callerSymbol);
  659| 
  660|             // Collect generic type definition, that is not collected when it is defined outside target project.
  661|             this.CollectCore(type.OriginalDefinition, callerSymbol);
  662|         }
  663| 
  664|         // Collect substituted types for the type parameters (e.g. Bar in Foo<Bar>)
  665|         foreach (var item in type.TypeArguments)
  666|         {
  667|             this.CollectCore(item, callerSymbol);
  668|         }
  669| 
  670|         if (!isOpenGenericType)
  671|         {
  672|             GenericSerializationInfo genericSerializationInfo = GenericSerializationInfo.Create(type, this.options.Generator.Resolver);
  673|             this.collectedGenericInfo.Add(genericSerializationInfo);
  674|         }
  675| 
  676|         static ImmutableArray<GenericTypeParameterInfo> GetTypeParameters(QualifiedTypeName qtn)
  677|             => qtn is QualifiedNamedTypeName named ? named.TypeParameters : ImmutableArray<GenericTypeParameterInfo>.Empty;
  678| 
  679|         static ImmutableArray<QualifiedTypeName> GetTypeArguments(QualifiedTypeName qtn)
  680|             => qtn is QualifiedNamedTypeName named ? named.TypeArguments : ImmutableArray<QualifiedTypeName>.Empty;
  681|     }
  682| 
  683|     private void CollectObject(INamedTypeSymbol type, ISymbol? callerSymbol)
  684|     {
  685|         ObjectSerializationInfo? info = this.GetObjectInfo(type, callerSymbol);
  686|         if (info is not null)
  687|         {
  688|             this.collectedObjectInfo.Add(info);
  689|         }
  690|     }
  691| 
  692|     private bool IsSourceGenerationSuppressed(INamedTypeSymbol type)
  693|     {
  694|         AttributeData? contractAttr = type.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.MessagePackObjectAttribute));
  695|         return contractAttr?.NamedArguments.FirstOrDefault(kvp => kvp.Key == Constants.SuppressSourceGenerationPropertyName).Value.Value is true;
  696|     }
  697| 
  698|     private void CheckValidMessagePackFormatterAttribute(AttributeData formatterAttribute)
  699|     {
  700|         if (formatterAttribute.ConstructorArguments[0].Value is ITypeSymbol formatterType)
  701|         {
  702|             // Validate that the typed formatter is actually of `IMessagePackFormatter`
  703|             bool isMessagePackFormatter = formatterType.AllInterfaces.Any(x => SymbolEqualityComparer.Default.Equals(x, this.typeReferences.MessagePackFormatter));
  704|             if (!isMessagePackFormatter)
  705|             {
  706|                 Location? location = ((AttributeSyntax?)formatterAttribute.ApplicationSyntaxReference?.GetSyntax())?.ArgumentList?.Arguments[0].GetLocation();
  707|                 ImmutableDictionary<string, string?> typeInfo = ImmutableDictionary.Create<string, string?>().Add("type", formatterType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat));
  708|                 this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.MessageFormatterMustBeMessagePackFormatter, location, typeInfo));
  709|             }
  710|         }
  711|     }
  712| 
  713|     private ObjectSerializationInfo? GetObjectInfo(INamedTypeSymbol formattedType, ISymbol? callerSymbol)
  714|     {
  715|         var isClass = !formattedType.IsValueType;
  716|         bool nestedFormatterRequired = false;
  717|         List<IPropertySymbol> nestedFormatterRequiredIfPropertyIsNotSetByDeserializingCtor = new();
  718| 
  719|         AttributeData? contractAttr = formattedType.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.MessagePackObjectAttribute));
  720| 
  721|         // Examine properties set on the attribute such that we can discern whether they were explicitly set or not.
  722|         // This is useful when we have assembly-level attributes or other environmentally-controlled defaults that the attribute may override either direction.
  723|         bool? suppressSourceGeneration = (bool?)contractAttr?.NamedArguments.FirstOrDefault(kvp => kvp.Key == Constants.SuppressSourceGenerationPropertyName).Value.Value;
  724|         bool? allowPrivateAttribute = (bool?)contractAttr?.NamedArguments.FirstOrDefault(kvp => kvp.Key == Constants.AllowPrivatePropertyName).Value.Value;
  725| 
  726|         // When the type opted out of source generation, we still validate its members so the analyzer can report diagnostics (e.g. a missing [Key]),
  727|         // but when generating source we must not collect the types of its members: no formatter will be generated for this type,
  728|         // so any formatter generated (or registered with the resolver) only because this type references it is at best unused and at worst invalid.
  729|         bool collectMemberTypes = suppressSourceGeneration is not true || !this.options.IsGeneratingSource;
  730| 
  731|         if (contractAttr is null)
  732|         {
  733|             ////this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.TypeMustBeMessagePackObject, ((BaseTypeDeclarationSyntax)type.DeclaringSyntaxReferences[0].GetSyntax()).Identifier.GetLocation(), type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat)));
  734|         }
  735| 
  736|         bool isIntKey = true;
  737|         Dictionary<int, (MemberSerializationInfo Info, ITypeSymbol TypeSymbol)> intMembers = new();
  738|         Dictionary<string, (MemberSerializationInfo Info, ITypeSymbol TypeSymbol)> stringMembers = new();
  739| 
  740|         // We default to not requiring non-public members to be attributed,
  741|         // but as soon as the first non-public member *is* attributed,
  742|         // we'll require all non-public members to be attributed.
  743|         // Historically, only public members were able to be serialized by default,
  744|         // so the analyzer only highlighted missing attributes on public members.
  745|         // But once it's clear that the developer is serializing non-public members,
  746|         // we need to raise the bar for all non-public members.
  747|         bool nonPublicMembersAreSerialized = false;
  748|         List<Diagnostic> deferredDiagnosticsForNonPublicMembers = new();
  749| 
  750|         FormatterDescriptor? GetSpecialFormatter(ISymbol member)
  751|         {
  752|             INamedTypeSymbol? name = member.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.FormatterAttribute))?.ConstructorArguments[0].Value as INamedTypeSymbol;
  753|             if (name is not null)
  754|             {
  755|                 if (FormatterDescriptor.TryCreate(name, out FormatterDescriptor? descriptor))
  756|                 {
  757|                     return descriptor;
  758|                 }
  759|                 else
  760|                 {
  761|                     // Report that the named type is not a formatter.
  762|                     // this.reportDiagnostic();
  763|                 }
  ... lines 764-823 not shown ...
  824|                     case IPropertySymbol item:
  825|                         {
  826|                             ImmutableArray<AttributeData> attributes = item.GetAttributes();
  827|                             if (attributes.Any(x => (x.AttributeClass.ApproximatelyEqual(this.typeReferences.IgnoreAttribute) || x.AttributeClass?.Name == this.typeReferences.IgnoreDataMemberAttribute?.Name)) ||
  828|                                 item.DeclaredAccessibility < minimumAccessibility)
  829|                             {
  830|                                 continue;
  831|                             }
  832| 
  833|                             bool isReadable = item.GetMethod is not null;
  834|                             bool isWritable = item.SetMethod is not null;
  835|                             if (!isReadable && !isWritable)
  836|                             {
  837|                                 continue;
  838|                             }
  839| 
  840|                             bool isInitOnly = item.SetMethod?.IsInitOnly is true;
  841|                             AttributeData? keyAttribute = attributes.FirstOrDefault(attributes => attributes.AttributeClass.ApproximatelyEqual(this.typeReferences.KeyAttribute));
  842|                             string stringKey = keyAttribute?.ConstructorArguments.Length == 1 && keyAttribute.ConstructorArguments[0].Value is string name ? name : item.Name;
  843|                             ReportNonUniqueNameIfApplicable(item, stringKey);
  844| 
  845|                             nestedFormatterRequired |= item.GetMethod is not null && IsPartialTypeRequired(item.GetMethod.DeclaredAccessibility);
  846|                             nestedFormatterRequired |= item.SetMethod is not null && IsPartialTypeRequired(item.SetMethod.DeclaredAccessibility);
  847|                             FormatterDescriptor? specialFormatter = GetSpecialFormatter(item);
  848|                             MemberSerializationInfo member = new(true, isWritable, isReadable, isInitOnly, item.IsRequired, hiddenIntKey++, stringKey, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
  849|                             {
  850|                                 DeclaringType = GetDeclaringTypeIfColliding(item),
  851|                             };
  852|                             if (!stringMembers.ContainsKey(member.StringKey))
  853|                             {
  854|                                 stringMembers.Add(member.StringKey, (member, item.Type));
  855|                             }
  856| 
  857|                             if (specialFormatter is null && collectMemberTypes)
  858|                             {
  859|                                 this.CollectCore(item.Type, item); // recursive collect
  860|                             }
  861|                         }
  862| 
  863|                         break;
  864|                     case IFieldSymbol item:
  865|                         {
  866|                             ImmutableArray<AttributeData> attributes = item.GetAttributes();
  867|                             if (attributes.Any(x => (x.AttributeClass.ApproximatelyEqual(this.typeReferences.IgnoreAttribute) || x.AttributeClass?.Name == this.typeReferences.IgnoreDataMemberAttribute?.Name)) ||
  868|                                 item.DeclaredAccessibility < minimumAccessibility)
  869|                             {
  870|                                 continue;
  871|                             }
  872| 
  873|                             AttributeData? keyAttribute = attributes.FirstOrDefault(attributes => attributes.AttributeClass.ApproximatelyEqual(this.typeReferences.KeyAttribute));
  874|                             string stringKey = keyAttribute?.ConstructorArguments.Length == 1 && keyAttribute.ConstructorArguments[0].Value is string name ? name : item.Name;
  875|                             ReportNonUniqueNameIfApplicable(item, stringKey);
  876| 
  877|                             nestedFormatterRequired |= IsPartialTypeRequired(item.DeclaredAccessibility);
  878|                             FormatterDescriptor? specialFormatter = GetSpecialFormatter(item);
  879|                             MemberSerializationInfo member = new(false, IsWritable: !item.IsReadOnly, IsReadable: true, IsInitOnly: false, item.IsRequired, hiddenIntKey++, stringKey, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
  880|                             {
  881|                                 DeclaringType = GetDeclaringTypeIfColliding(item),
  882|                             };
  883|                             if (!stringMembers.ContainsKey(member.StringKey))
  884|                             {
  885|                                 stringMembers.Add(member.StringKey, (member, item.Type));
  886|                             }
  887| 
  888|                             if (specialFormatter is null && collectMemberTypes)
  889|                             {
  890|                                 this.CollectCore(item.Type, item); // recursive collect
  891|                             }
  892|                         }
  893| 
  894|                         break;
  895|                 }
  896|             }
  897|         }
  898|         else
  899|         {
  900|             // Only KeyAttribute members
  901|             var searchFirst = true;
  902|             var hiddenIntKey = 0;
  903| 
  904|             foreach (IPropertySymbol item in instanceMembers.OfType<IPropertySymbol>())
  905|             {
  906|                 if (item.IsIndexer)
  907|                 {
  908|                     continue; // .tt files don't generate good code for this yet: https://github.com/neuecc/MessagePack-CSharp/issues/390
  909|                 }
  910| 
  911|                 if (item.GetAttributes().Any(x =>
  912|                 {
  913|                     var typeReferencesIgnoreDataMemberAttribute = this.typeReferences.IgnoreDataMemberAttribute;
  914|                     return typeReferencesIgnoreDataMemberAttribute != null && (x.AttributeClass.ApproximatelyEqual(this.typeReferences.IgnoreAttribute) || x.AttributeClass.ApproximatelyEqual(typeReferencesIgnoreDataMemberAttribute));
  915|                 }))
  916|                 {
  917|                     nonPublicMembersAreSerialized |= (item.DeclaredAccessibility & Accessibility.Public) != Accessibility.Public;
  918|                     continue;
  919|                 }
  920| 
  921|                 bool isReadable = item.GetMethod is not null;
  ... lines 922-995 not shown ...
  996|                         nestedFormatterRequiredIfPropertyIsNotSetByDeserializingCtor.Add(item);
  997|                     }
  998| 
  999|                     var intKey = key is { Value: int intKeyValue } ? intKeyValue : default(int?);
 1000|                     var stringKey = key is { Value: string stringKeyValue } ? stringKeyValue : default;
 1001|                     if (intKey == null && stringKey == null)
 1002|                     {
 1003|                         this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.BothStringAndIntKeyAreNull, ((PropertyDeclarationSyntax)item.DeclaringSyntaxReferences[0].GetSyntax()).Identifier.GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name));
 1004|                     }
 1005| 
 1006|                     // A property with an init accessor and an initializer has a default that will be discarded by the deserializer.
 1007|                     if (suppressSourceGeneration is not true && isInitOnly)
 1008|                     {
 1009|                         EqualsValueClauseSyntax? initializer = item.DeclaringSyntaxReferences.Select(s => (s.GetSyntax(this.cancellationToken) as PropertyDeclarationSyntax)?.Initializer).FirstOrDefault(i => i is not null);
 1010|                         if (initializer is not null)
 1011|                         {
 1012|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AOTInitProperty, initializer.GetLocation()));
 1013|                         }
 1014|                     }
 1015| 
 1016|                     if (searchFirst)
 1017|                     {
 1018|                         searchFirst = false;
 1019|                         isIntKey = intKey != null;
 1020|                     }
 1021|                     else
 1022|                     {
 1023|                         if ((isIntKey && intKey == null) || (!isIntKey && stringKey == null))
 1024|                         {
 1025|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.DoNotMixStringAndIntKeys, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
 1026|                         }
 1027|                     }
 1028| 
 1029|                     // A member whose key is of the wrong kind (or null) has already been reported above and cannot be added to the member map.
 1030|                     if (isIntKey && intKey is not null)
 1031|                     {
 1032|                         if (intMembers.ContainsKey(intKey!.Value))
 1033|                         {
 1034|                             // Report the collision and keep the first member, rather than throwing (which would crash the analyzer with AD0001).
 1035|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.KeysMustBeUnique, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
 1036|                         }
 1037|                         else
 1038|                         {
 1039|                             var member = new MemberSerializationInfo(true, isWritable, isReadable, isInitOnly, item.IsRequired, intKey!.Value, item.Name, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
 1040|                             {
 1041|                                 DeclaringType = GetDeclaringTypeIfColliding(item),
 1042|                             };
 1043|                             intMembers.Add(member.IntKey, (member, item.Type));
 1044|                         }
 1045|                     }
 1046|                     else if (!isIntKey && stringKey is not null)
 1047|                     {
 1048|                         if (stringMembers.ContainsKey(stringKey!))
 1049|                         {
 1050|                             // Report the collision and keep the first member, rather than throwing (which would crash the analyzer with AD0001).
 1051|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.KeysMustBeUnique, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
 1052|                         }
 1053|                         else
 1054|                         {
 1055|                             var member = new MemberSerializationInfo(true, isWritable, isReadable, isInitOnly, item.IsRequired, hiddenIntKey++, stringKey!, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
 1056|                             {
 1057|                                 DeclaringType = GetDeclaringTypeIfColliding(item),
 1058|                             };
 1059|                             stringMembers.Add(member.StringKey, (member, item.Type));
 1060|                         }
 1061|                     }
 1062| 
 1063|                     var messagePackFormatter = item.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.FormatterAttribute))?.ConstructorArguments[0];
 1064| 
 1065|                     if (messagePackFormatter == null && collectMemberTypes)
 1066|                     {
 1067|                         // recursive collect
 1068|                         this.CollectCore(item.Type, item);
 1069|                     }
 1070|                 }
 1071|             }
 1072| 
 1073|             foreach (IFieldSymbol item in formattedType.GetAllMembers().OfType<IFieldSymbol>())
 1074|             {
 1075|                 if (item.IsImplicitlyDeclared || item.IsStatic)
 1076|                 {
 1077|                     continue;
 1078|                 }
 1079| 
 1080|                 if (item.GetAttributes().Any(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.IgnoreAttribute)))
 1081|                 {
 1082|                     nonPublicMembersAreSerialized |= (item.DeclaredAccessibility & Accessibility.Public) != Accessibility.Public;
 1083|                     continue;
 1084|                 }
 1085| 
 1086|                 FormatterDescriptor? specialFormatter = GetSpecialFormatter(item);
 1087|                 TypedConstant? key = item.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.KeyAttribute))?.ConstructorArguments[0];
 1088|                 if (key is null)
 1089|                 {
 1090|                     if (contractAttr is not null)
 1091|                     {
 1092|                         // If the member is attributed with a type derived from KeyAttribute, that's incompatible with source generation
 1093|                         // since we cannot know what the key is using only C# syntax and the semantic model.
 1094|                         SyntaxReference? derivedKeyAttribute = item.GetAttributes().FirstOrDefault(att => att.AttributeClass.IsApproximatelyEqualOrDerivedFrom(this.typeReferences.KeyAttribute) == RoslynAnalyzerExtensions.EqualityMatch.LeftDerivesFromRight)?.ApplicationSyntaxReference;
 1095| 
 1096|                         if (derivedKeyAttribute is null || suppressSourceGeneration is not true)
 1097|                         {
 1098|                             if (SymbolEqualityComparer.Default.Equals(item.ContainingType, formattedType))
  ... lines 1099-1135 not shown ...
 1136|                                     }
 1137|                                 }
 1138|                             }
 1139|                         }
 1140|                     }
 1141|                 }
 1142|                 else
 1143|                 {
 1144|                     // If this attributed member is non-public, then all non-public members should be attributed.
 1145|                     nonPublicMembersAreSerialized |= (item.DeclaredAccessibility & Accessibility.Public) != Accessibility.Public;
 1146| 
 1147|                     nestedFormatterRequired |= IsPartialTypeRequired(item.DeclaredAccessibility);
 1148| 
 1149|                     var intKey = key is { Value: int intKeyValue } ? intKeyValue : default(int?);
 1150|                     var stringKey = key is { Value: string stringKeyValue } ? stringKeyValue : default;
 1151|                     if (intKey == null && stringKey == null)
 1152|                     {
 1153|                         this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.BothStringAndIntKeyAreNull, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
 1154|                     }
 1155| 
 1156|                     if (searchFirst)
 1157|                     {
 1158|                         searchFirst = false;
 1159|                         isIntKey = intKey != null;
 1160|                     }
 1161|                     else
 1162|                     {
 1163|                         if ((isIntKey && intKey == null) || (!isIntKey && stringKey == null))
 1164|                         {
 1165|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.DoNotMixStringAndIntKeys, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
 1166|                         }
 1167|                     }
 1168| 
 1169|                     // A member whose key is of the wrong kind (or null) has already been reported above and cannot be added to the member map.
 1170|                     if (isIntKey && intKey is not null)
 1171|                     {
 1172|                         if (intMembers.ContainsKey(intKey!.Value))
 1173|                         {
 1174|                             // Report the collision and keep the first member, rather than throwing (which would crash the analyzer with AD0001).
 1175|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.KeysMustBeUnique, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
 1176|                         }
 1177|                         else
 1178|                         {
 1179|                             var member = new MemberSerializationInfo(true, IsWritable: !item.IsReadOnly, IsReadable: true, IsInitOnly: false, item.IsRequired, intKey!.Value, item.Name, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
 1180|                             {
 1181|                                 DeclaringType = GetDeclaringTypeIfColliding(item),
 1182|                             };
 1183|                             intMembers.Add(member.IntKey, (member, item.Type));
 1184|                         }
 1185|                     }
 1186|                     else if (!isIntKey && stringKey is not null)
 1187|                     {
 1188|                         if (stringMembers.ContainsKey(stringKey!))
 1189|                         {
 1190|                             // Report the collision and keep the first member, rather than throwing (which would crash the analyzer with AD0001).
 1191|                             this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.KeysMustBeUnique, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()));
 1192|                         }
 1193|                         else
 1194|                         {
 1195|                             var member = new MemberSerializationInfo(true, IsWritable: !item.IsReadOnly, IsReadable: true, IsInitOnly: false, item.IsRequired, hiddenIntKey++, stringKey!, item.Name, item.Type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Type.ToDisplayString(BinaryWriteFormat), specialFormatter)
 1196|                             {
 1197|                                 DeclaringType = GetDeclaringTypeIfColliding(item),
 1198|                             };
 1199|                             stringMembers.Add(member.StringKey, (member, item.Type));
 1200|                         }
 1201|                     }
 1202| 
 1203|                     var messagePackFormatter = item.GetAttributes().FirstOrDefault(x => x.AttributeClass.ApproximatelyEqual(this.typeReferences.FormatterAttribute))?.ConstructorArguments[0];
 1204| 
 1205|                     if (messagePackFormatter == null && collectMemberTypes)
 1206|                     {
 1207|                         // recursive collect
 1208|                         this.CollectCore(item.Type, item);
 1209|                     }
 1210|                 }
 1211|             }
 1212|         }
 1213| 
 1214|         // If we discovered midway through that we should be reporting diagnostics for non-public members,
 1215|         // report the ones we missed along the way.
 1216|         if ((nonPublicMembersAreSerialized || allowPrivateAttribute is true) && this.reportDiagnostic is not null)
 1217|         {
 1218|             foreach (Diagnostic deferred in deferredDiagnosticsForNonPublicMembers)
 1219|             {
 1220|                 this.reportDiagnostic(deferred);
 1221|             }
 1222|         }
 1223| 
 1224|         // GetConstructor
 1225|         var ctorEnumerator = default(IEnumerator<IMethodSymbol>);
 1226|         var ctor = formattedType.Constructors.SingleOrDefault(x => x.GetAttributes().Any(y => y.AttributeClass != null && y.AttributeClass.ApproximatelyEqual(this.typeReferences.SerializationConstructorAttribute)));
 1227|         if (ctor is null)
 1228|         {
 1229|             ctorEnumerator = formattedType.Constructors
 1230|                 .OrderByDescending(x => x.DeclaredAccessibility)
 1231|                 .ThenByDescending(x => x.Parameters.Length)
 1232|                 .GetEnumerator();
 1233| 
 1234|             if (ctorEnumerator.MoveNext())
 1235|             {
 1236|                 ctor = ctorEnumerator.Current;
 1237|             }
 1238|         }
  ... lines 1239-1523 not shown ...
```

### tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs at head (6a3d2cb0), around the changed lines
```
  ... lines 1-1113 not shown ...
 1114| 
 1115|                 [Key(39)]
 1116|                 public ArraySegment<byte>? Value40 { get; set; }
 1117|             }
 1118|             """;
 1119| 
 1120|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
 1121|     }
 1122| 
 1123|     [Fact]
 1124|     public async Task SystemMemoryTypes()
 1125|     {
 1126|         string testSource = /* lang=c#-test */ """
 1127|             using System;
 1128|             using System.Buffers;
 1129|             using MessagePack;
 1130| 
 1131|             [MessagePackObject]
 1132|             public class A
 1133|             {
 1134|                 [Key(0)]
 1135|                 public Memory<int> Value1 { get; set; }
 1136| 
 1137|                 [Key(1)]
 1138|                 public ReadOnlyMemory<int> Value2 { get; set; }
 1139| 
 1140|                 [Key(2)]
 1141|                 public ReadOnlySequence<int> Value3 { get; set; }
 1142|             }
 1143|             """;
 1144| 
 1145|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
 1146|     }
 1147| 
 1148|     /// <summary>
 1149|     /// A type that opts out of source generation must not cause formatters to be generated for the types of its members,
 1150|     /// since it gets no source generated formatter that would use them.
 1151|     /// </summary>
 1152|     [Fact]
 1153|     public async Task SuppressSourceGeneration_MemberTypesAreNotCollected()
 1154|     {
 1155|         string testSource = /* lang=c#-test */ """
 1156|             using System.Collections.Generic;
 1157|             using MessagePack;
 1158| 
 1159|             [MessagePackObject(SuppressSourceGeneration = true)]
 1160|             public class A
 1161|             {
 1162|                 [Key(0)]
 1163|                 public Dictionary<string, IItem> Items { get; set; }
 1164| 
 1165|                 [Key(1)]
 1166|                 public MyEnum Enum { get; set; }
 1167| 
 1168|                 [Key(2)]
 1169|                 public IItem Item;
 1170|             }
 1171| 
 1172|             public interface IItem
 1173|             {
 1174|                 object Value { get; }
 1175|             }
 1176| 
 1177|             public enum MyEnum { A, B }
 1178|             """;
 1179| 
 1180|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
 1181|     }
 1182| 
 1183|     /// <summary>
 1184|     /// Types that are themselves attributed still get a formatter, even when only a suppressed type references them.
 1185|     /// </summary>
 1186|     [Theory, PairwiseData]
 1187|     public async Task SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated(bool usesMapMode)
 1188|     {
 1189|         string testSource = /* lang=c#-test */ """
 1190|             using MessagePack;
 1191| 
 1192|             [MessagePackObject(SuppressSourceGeneration = true)]
 1193|             public class A
 1194|             {
 1195|                 [Key(0)]
 1196|                 public B Value { get; set; }
 1197| 
 1198|                 [Key(1)]
 1199|                 public MyEnum Enum;
 1200|             }
 1201| 
 1202|             [MessagePackObject]
 1203|             public class B
 1204|             {
 1205|                 [Key(0)]
 1206|                 public int Value { get; set; }
 1207|             }
 1208| 
 1209|             public enum MyEnum { A, B }
 1210|             """;
 1211| 
 1212|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource, options: new() { Generator = new() { Formatters = new() { UsesMapMode = usesMapMode } } }, testMethod: $"{nameof(SuppressSourceGeneration_ReferencedMessagePackObjectStillGenerated)}({usesMapMode})");
 1213|     }
 1214| 
 1215|     /// <summary>
 1216|     /// A closed generic type whose definition opted out of source generation must not be registered with the generated resolver,
 1217|     /// since its formatter is never generated.
 1218|     /// </summary>
 1219|     [Fact]
 1220|     public async Task SuppressSourceGeneration_ClosedGenericIsNotRegistered()
 1221|     {
 1222|         string testSource = /* lang=c#-test */ """
 1223|             using MessagePack;
 1224| 
 1225|             [MessagePackObject]
 1226|             public class Holder
 1227|             {
 1228|                 [Key(0)]
 1229|                 public Wrapper<MyEnum> Value { get; set; }
 1230|             }
 1231| 
 1232|             [MessagePackObject(SuppressSourceGeneration = true)]
 1233|             public class Wrapper<T>
 1234|             {
 1235|                 [Key(0)]
 1236|                 public T Value { get; set; }
 1237|             }
 1238| 
 1239|             public enum MyEnum { A, B }
 1240|             """;
 1241| 
 1242|         await VerifyCS.Test.RunDefaultAsync(this.testOutputHelper, testSource);
 1243|     }
 1244| }
```

### tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs at head (6a3d2cb0), around the changed lines
```
  ... lines 1-1056 not shown ...
 1057|                 public new string {|MsgPack018:Prop|} { get; set; }
 1058| 
 1059|                 public new string {|MsgPack018:Field|};
 1060| 
 1061|                 public new string {|MsgPack018:TwoFaced|};
 1062|             }
 1063|             """;
 1064| 
 1065|         await VerifyCS.VerifyAnalyzerAsync(test);
 1066|     }
 1067| 
 1068|     [Fact]
 1069|     public async Task AbstractFormatterDoesNotAttractAttention()
 1070|     {
 1071|         string test = /* lang=c#-test */ """
 1072|             using MessagePack;
 1073|             using MessagePack.Formatters;
 1074| 
 1075|             public abstract class AbstractFormatter1 : IMessagePackFormatter<object>
 1076|             {
 1077|                 public abstract void Serialize(ref MessagePackWriter writer, object value, MessagePackSerializerOptions options);
 1078|                 public abstract object Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options);
 1079|             }
 1080| 
 1081|             public abstract class AbstractFormatter2 : IMessagePackFormatter<object>
 1082|             {
 1083|                 public abstract void Serialize(ref MessagePackWriter writer, object value, MessagePackSerializerOptions options);
 1084|                 public abstract object Deserialize(ref MessagePackReader reader, MessagePackSerializerOptions options);
 1085|             }
 1086|             """;
 1087| 
 1088|         await VerifyCS.VerifyAnalyzerAsync(test);
 1089|     }
 1090| 
 1091|     [Fact]
 1092|     public async Task SuppressSourceGeneration_MissingKeyOnProperty()
 1093|     {
 1094|         string test = /* lang=c#-test */ """
 1095|             using MessagePack;
 1096| 
 1097|             [MessagePackObject(SuppressSourceGeneration = true)]
 1098|             public class A
 1099|             {
 1100|                 [Key(0)]
 1101|                 public int Prop1 { get; set; }
 1102| 
 1103|                 public int {|MsgPack004:Prop2|} { get; set; }
 1104|             }
 1105|             """;
 1106| 
 1107|         await new VerifyCS.Test
 1108|         {
 1109|             TestCode = test,
 1110|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
 1111|         }.RunAsync();
 1112|     }
 1113| 
 1114|     [Fact]
 1115|     public async Task SuppressSourceGeneration_MissingKeyOnField()
 1116|     {
 1117|         string test = /* lang=c#-test */ """
 1118|             using MessagePack;
 1119| 
 1120|             [MessagePackObject(SuppressSourceGeneration = true)]
 1121|             public class A
 1122|             {
 1123|                 [Key(0)]
 1124|                 public int Field1;
 1125| 
 1126|                 public int {|MsgPack004:Field2|};
 1127|             }
 1128|             """;
 1129| 
 1130|         await new VerifyCS.Test
 1131|         {
 1132|             TestCode = test,
 1133|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
 1134|         }.RunAsync();
 1135|     }
 1136| 
 1137|     [Fact]
 1138|     public async Task SuppressSourceGeneration_MissingKeyInBaseType()
 1139|     {
 1140|         string test = /* lang=c#-test */ """
 1141|             using MessagePack;
 1142| 
 1143|             public class Base
 1144|             {
 1145|                 public int BaseProp { get; set; }
 1146|             }
 1147| 
 1148|             [MessagePackObject(SuppressSourceGeneration = true)]
 1149|             public class Derived : {|MsgPack004:Base|}
 1150|             {
 1151|                 [Key(0)]
 1152|                 public int Prop1 { get; set; }
 1153|             }
 1154|             """;
 1155| 
 1156|         await new VerifyCS.Test
 1157|         {
 1158|             TestCode = test,
 1159|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
 1160|         }.RunAsync();
 1161|     }
 1162| 
 1163|     [Fact]
 1164|     public async Task SuppressSourceGeneration_KeyValidation()
 1165|     {
 1166|         string test = /* lang=c#-test */ """
 1167|             using MessagePack;
 1168| 
 1169|             [MessagePackObject(SuppressSourceGeneration = true)]
 1170|             public class A
 1171|             {
 1172|                 [Key(0)]
 1173|                 public int Prop1 { get; set; }
 1174| 
 1175|                 {|MsgPack005:[Key(0)]
 1176|                 public int Prop2 { get; set; }|}
 1177| 
 1178|                 {|MsgPack005:[Key("x")]
 1179|                 public int Prop3 { get; set; }|}
 1180|             }
 1181|             """;
 1182| 
 1183|         await new VerifyCS.Test
 1184|         {
 1185|             TestCode = test,
 1186|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
 1187|         }.RunAsync();
 1188|     }
 1189| 
 1190|     [Fact]
 1191|     public async Task SuppressSourceGeneration_AllowPrivateRequired()
 1192|     {
 1193|         string test = /* lang=c#-test */ """
 1194|             using MessagePack;
 1195| 
 1196|             [{|MsgPack015:MessagePackObject(SuppressSourceGeneration = true)|}]
 1197|             internal class A
 1198|             {
 1199|                 [Key(0)]
 1200|                 public int Prop1 { get; set; }
 1201|             }
 1202|             """;
 1203| 
 1204|         await VerifyCS.VerifyAnalyzerAsync(test);
 1205|     }
 1206| 
 1207|     [Fact]
 1208|     public async Task SuppressSourceGeneration_MemberTypeNotSerializable()
 1209|     {
 1210|         string test = /* lang=c#-test */ """
 1211|             using MessagePack;
 1212| 
 1213|             public class NotAttributed
 1214|             {
 1215|             }
 1216| 
 1217|             [MessagePackObject(SuppressSourceGeneration = true)]
 1218|             public class A
 1219|             {
 1220|                 [Key(0)]
 1221|                 public NotAttributed {|MsgPack003:Prop1|} { get; set; }
 1222|             }
 1223|             """;
 1224| 
 1225|         await VerifyCS.VerifyAnalyzerAsync(test);
 1226|     }
 1227| 
 1228|     [Fact]
 1229|     public async Task SuppressSourceGeneration_ValidTypeHasNoDiagnostics()
 1230|     {
 1231|         string test = /* lang=c#-test */ """
 1232|             using MessagePack;
 1233| 
 1234|             [MessagePackObject(SuppressSourceGeneration = true)]
 1235|             public class A
 1236|             {
 1237|                 [Key(0)]
 1238|                 public int Prop1 { get; set; }
 1239| 
 1240|                 [Key(1)]
 1241|                 public string Field1;
 1242| 
 1243|                 [IgnoreMember]
 1244|                 public int Ignored { get; set; }
 1245|             }
 1246|             """;
 1247| 
 1248|         await VerifyCS.VerifyAnalyzerAsync(test);
 1249|     }
 1250| 
 1251|     [Fact]
 1252|     public async Task SuppressSourceGeneration_KeyValidationOnFields()
 1253|     {
 1254|         string test = /* lang=c#-test */ """
 1255|             using MessagePack;
 1256| 
 1257|             [MessagePackObject(SuppressSourceGeneration = true)]
 1258|             public class A
 1259|             {
 1260|                 [Key(0)]
 1261|                 public int Field1;
 1262| 
 1263|                 [Key(0)]
 1264|                 public int {|MsgPack005:Field2|};
 1265| 
 1266|                 [Key("x")]
 1267|                 public int {|MsgPack005:Field3|};
 1268|             }
 1269|             """;
 1270| 
 1271|         await new VerifyCS.Test
 1272|         {
 1273|             TestCode = test,
 1274|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
 1275|         }.RunAsync();
 1276|     }
 1277| 
 1278|     [Fact]
 1279|     public async Task SuppressSourceGeneration_GenericTypeWithoutIssues()
 1280|     {
 1281|         string test = /* lang=c#-test */ """
 1282|             using MessagePack;
 1283| 
 1284|             [MessagePackObject(SuppressSourceGeneration = true)]
 1285|             public class Wrapper<T>
 1286|             {
 1287|                 [Key(0)]
 1288|                 public T Value { get; set; }
 1289|             }
 1290| 
 1291|             [MessagePackObject]
 1292|             public class Holder
 1293|             {
 1294|                 [Key(0)]
 1295|                 public Wrapper<int> Value { get; set; }
 1296|             }
 1297|             """;
 1298| 
 1299|         await VerifyCS.VerifyAnalyzerAsync(test);
 1300|     }
 1301| 
 1302|     [Fact]
 1303|     public async Task SuppressSourceGeneration_MapMode()
 1304|     {
 1305|         string test = /* lang=c#-test */ """
 1306|             using MessagePack;
 1307| 
 1308|             [MessagePackObject(true, SuppressSourceGeneration = true)]
 1309|             public class Base
 1310|             {
 1311|                 public string Prop { get; set; }
 1312|             }
 1313| 
 1314|             [MessagePackObject(true, SuppressSourceGeneration = true)]
 1315|             public class Derived : Base
 1316|             {
 1317|                 public new string {|MsgPack018:Prop|} { get; set; }
 1318|             }
 1319|             """;
 1320| 
 1321|         await VerifyCS.VerifyAnalyzerAsync(test);
 1322|     }
 1323| 
 1324|     [Fact]
 1325|     public async Task DuplicateKeysAreReportedWithoutCrashing()
 1326|     {
 1327|         string test = /* lang=c#-test */ """
 1328|             using MessagePack;
 1329| 
 1330|             [MessagePackObject]
 1331|             public class IntKeys
 1332|             {
 1333|                 [Key(0)]
 1334|                 public int Prop1 { get; set; }
 1335| 
 1336|                 {|MsgPack005:[Key(0)]
 1337|                 public int Prop2 { get; set; }|}
 1338| 
 1339|                 [Key(1)]
 1340|                 public int Field1;
 1341| 
 1342|                 [Key(1)]
 1343|                 public int {|MsgPack005:Field2|};
 1344|             }
 1345| 
 1346|             [MessagePackObject]
 1347|             public class StringKeys
 1348|             {
 1349|                 [Key("a")]
 1350|                 public int Prop1 { get; set; }
 1351| 
 1352|                 {|MsgPack005:[Key("a")]
 1353|                 public int Prop2 { get; set; }|}
 1354| 
 1355|                 [Key("b")]
 1356|                 public int Field1;
 1357| 
 1358|                 [Key("b")]
 1359|                 public int {|MsgPack005:Field2|};
 1360|             }
 1361|             """;
 1362| 
 1363|         await new VerifyCS.Test
 1364|         {
 1365|             TestCode = test,
 1366|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
 1367|         }.RunAsync();
 1368|     }
 1369| 
 1370|     [Fact]
 1371|     public async Task MixedKeysAreReportedWithoutCrashing()
 1372|     {
 1373|         string test = /* lang=c#-test */ """
 1374|             using MessagePack;
 1375| 
 1376|             [MessagePackObject]
 1377|             public class IntFirst
 1378|             {
 1379|                 [Key(0)]
 1380|                 public int Prop1 { get; set; }
 1381| 
 1382|                 {|MsgPack005:[Key("a")]
 1383|                 public int Prop2 { get; set; }|}
 1384| 
 1385|                 [Key("b")]
 1386|                 public int {|MsgPack005:Field1|};
 1387|             }
 1388| 
 1389|             [MessagePackObject]
 1390|             public class StringFirst
 1391|             {
 1392|                 [Key("a")]
 1393|                 public int Prop1 { get; set; }
 1394| 
 1395|                 {|MsgPack005:[Key(1)]
 1396|                 public int Prop2 { get; set; }|}
 1397| 
 1398|                 [Key(2)]
 1399|                 public int {|MsgPack005:Field1|};
 1400|             }
 1401|             """;
 1402| 
 1403|         await new VerifyCS.Test
 1404|         {
 1405|             TestCode = test,
 1406|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
 1407|         }.RunAsync();
 1408|     }
 1409| }
```

### src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base (32258fdb), around the changed lines
```
  ... lines 1-606 not shown ...
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
  ... lines 746-805 not shown ...
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
  ... lines 904-977 not shown ...
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
  ... lines 1074-1110 not shown ...
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
  ... lines 1207-1491 not shown ...
```

## What you did NOT get (refuse anything that depends on it)
- the contents and diffs of 6 generated files (listed above by name only)
- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)

Return only the JSON object described in the brief.