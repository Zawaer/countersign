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
# Change var-2283-v2: branch cs-var/2283-v2, base 32258fdbee4bcd653c79f51b4376b5103c6f4d27, head e034891270aecbc33c08138682e273b793a59eb5
Commit message: Fix generator/analyzer crash on closed generic value types from referenced assemblies

When a [MessagePackObject] member is typed as a closed generic value type
defined in a referenced assembly (e.g. Lib.Item<int> where Item<T> is a
struct or record struct), TypeCollector.CollectGeneric calls GetObjectInfo
on a metadata symbol. Roslyn imports the private fields of metadata structs
(for layout), including auto-property backing fields such as
<Key>k__BackingField, which, unlike their source counterparts, are not
flagged IsImplicitlyDeclared. Such a field has no [Key], so the
MemberNeedsKey diagnostic was built with DeclaringSyntaxReferences[0],
which is empty for metadata symbols -> IndexOutOfRangeException. The
diagnostic was constructed unconditionally, so both the generator (CS8785,
no resolver emitted) and the analyzer (AD0001) failed.

- Skip compiler-generated (unspeakable-name) fields when enumerating
  members, in both key mode and map mode.
- Never index DeclaringSyntaxReferences[0]: the MemberNeedsKey field
  location and the BothStringAndIntKeyAreNull location now tolerate
  symbols without syntax. The latter also no longer casts to
  PropertyDeclarationSyntax, which threw InvalidCastException for
  record primary constructor parameters.

Fixes #2283

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Upstream issue: https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2283

## Requirement set (requirements/var-2283-v2.yaml)
```yaml
# REUSED from requirements/2283.yaml (same clauses, same ids, unchanged text) for another fix of the same upstream issue
# #2283, so every fix of it is judged against the same clauses (docs/MEASUREMENT.md, "Same issue, several fixes").
# Still a placeholder derived from the issue, not a Tieto set.
change: "var-2283-v2"
branch: cs-var/2283-v2
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
 "change": "var-2283-v2",
 "branch": "cs-var/2283-v2",
 "base": "32258fdb",
 "head": "e0348912",
 "base_full": "32258fdbee4bcd653c79f51b4376b5103c6f4d27",
 "head_full": "e034891270aecbc33c08138682e273b793a59eb5",
 "commit_message": "Fix generator/analyzer crash on closed generic value types from referenced assemblies\n\nWhen a [MessagePackObject] member is typed as a closed generic value type\ndefined in a referenced assembly (e.g. Lib.Item<int> where Item<T> is a\nstruct or record struct), TypeCollector.CollectGeneric calls GetObjectInfo\non a metadata symbol. Roslyn imports the private fields of metadata structs\n(for layout), including auto-property backing fields such as\n<Key>k__BackingField, which, unlike their source counterparts, are not\nflagged IsImplicitlyDeclared. Such a field has no [Key], so the\nMemberNeedsKey diagnostic was built with DeclaringSyntaxReferences[0],\nwhich is empty for metadata symbols -> IndexOutOfRangeException. The\ndiagnostic was constructed unconditionally, so both the generator (CS8785,\nno resolver emitted) and the analyzer (AD0001) failed.\n\n- Skip compiler-generated (unspeakable-name) fields when enumerating\n  members, in both key mode and map mode.\n- Never index DeclaringSyntaxReferences[0]: the MemberNeedsKey field\n  location and the BothStringAndIntKeyAreNull location now tolerate\n  symbols without syntax. The latter also no longer casts to\n  PropertyDeclarationSyntax, which threw InvalidCastException for\n  record primary constructor parameters.\n\nFixes #2283\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>",
 "author": "Zawaer",
 "agent_written": true,
 "diff": {
  "files": 3,
  "insertions": 270,
  "deletions": 4,
  "by_kind": {
   "source": 1,
   "test": 2
  },
  "by_file": [
   {
    "path": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
    "ins": 32,
    "del": 4,
    "kind": "source"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs",
    "ins": 16,
    "del": 0,
    "kind": "test"
   },
   {
    "path": "tests/MessagePack.SourceGenerator.Tests/ReferencedAssemblyTypesTests.cs",
    "ins": 222,
    "del": 0,
    "kind": "test"
   }
  ]
 },
 "new_tests_in_diff": [
  "MsgPack00xAnalyzerTests.NullStringKey_RecordPrimaryConstructorParameter",
  "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow",
  "ReferencedAssemblyTypesTests.AnalyzerStillReportsProblemsInReferencingProject",
  "ReferencedAssemblyTypesTests.GeneratorCollectsTypeArgumentOfReferencedGenericValueType",
  "ReferencedAssemblyTypesTests.GeneratorProducesResolver"
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
   "log": "evidence/var-2283-v2/logs/build.log",
   "duration_s": 4.0
  },
  {
   "id": "tests.targeted",
   "tool": "dotnet test",
   "tool_version": "8.0.402",
   "status": "pass",
   "summary": "66 passed, 0 failed, 0 skipped (31 new tests in run)",
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
     "name": "MsgPack00xAnalyzerTests.NullStringKey_RecordPrimaryConstructorParameter",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "MsgPack00xAnalyzerTests.PrivateMembersInBaseClassNeedNoAttribution",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"class generic\", libraryDeclaration: \"[MessagePackObject] public partial class Item<T> {\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"readonly record struct generic\", libraryDeclaration: \"[MessagePackObject] public readonly partial record\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record class generic\", libraryDeclaration: \"[MessagePackObject] public partial record class It\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record struct generic map mode\", libraryDeclaration: \"[MessagePackObject(true)] public partial record st\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record struct generic\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record struct\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic T member\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic explicit private field\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic field\", libraryDeclaration: \"[MessagePackObject] public struct Item<T> { [Key(0\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic init\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic map mode\", libraryDeclaration: \"[MessagePackObject(true)] public partial struct It\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic string key\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct\", libraryDeclaration: \"[MessagePackObject] public partial struct Item { [\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrowOnInvalidReferencedType(libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrowOnInvalidReferencedType(libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrowOnInvalidReferencedType(libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrowOnInvalidReferencedType(libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrowOnInvalidReferencedType(libraryDeclaration: \"[MessagePackObject] public struct Item<T> { [Key(0\"···)",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerStillReportsProblemsInReferencingProject",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorCollectsTypeArgumentOfReferencedGenericValueType",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"class generic\", libraryDeclaration: \"[MessagePackObject] public partial class Item<T> {\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"readonly record struct generic\", libraryDeclaration: \"[MessagePackObject] public readonly partial record\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record class generic\", libraryDeclaration: \"[MessagePackObject] public partial record class It\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record struct generic map mode\", libraryDeclaration: \"[MessagePackObject(true)] public partial record st\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record struct generic\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record struct\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic T member\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic explicit private field\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic field\", libraryDeclaration: \"[MessagePackObject] public struct Item<T> { [Key(0\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic init\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic map mode\", libraryDeclaration: \"[MessagePackObject(true)] public partial struct It\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic string key\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct\", libraryDeclaration: \"[MessagePackObject] public partial struct Item { [\"···)",
     "outcome": "passed",
     "new": true
    }
   ],
   "log": "evidence/var-2283-v2/logs/tests_targeted.1.log",
   "duration_s": 4.0,
   "filter": [
    "FullyQualifiedName~ReferencedAssemblyTypesTests.|FullyQualifiedName~MsgPack00xAnalyzerTests."
   ],
   "project": "tests/MessagePack.SourceGenerator.Tests"
  },
  {
   "id": "tests.fail_without_fix",
   "tool": "dotnet test (source reverted, tests kept)",
   "tool_version": "8.0.402",
   "status": "pass",
   "summary": "new tests fail on base source: 17/31 failed -> tests do cover the change (14 new tests pass without the fix)",
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
     "name": "MsgPack00xAnalyzerTests.NullStringKey_RecordPrimaryConstructorParameter",
     "outcome": "failed",
     "new": true,
     "error": "System.InvalidOperationException : Context: Diagnostics of test state\nMismatch between number of diagnostics returned, expected \"2\" actual \"1\"\r\n\r\nDiagnostics:\r\n// error AD0001: Analyzer 'MessagePack.SourceGenerator.Analyzers.MsgPack00xMessagePackAnalyzer' threw an exception of type 'System.InvalidCastException' with message 'Unable to cast object of type 'Microsoft.CodeAnalysis.CSharp.Syntax.Param [...]"
    },
    {
     "name": "MsgPack00xAnalyzerTests.PrivateMembersInBaseClassNeedNoAttribution",
     "outcome": "passed",
     "new": false
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"class generic\", libraryDeclaration: \"[MessagePackObject] public partial class Item<T> {\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"readonly record struct generic\", libraryDeclaration: \"[MessagePackObject] public readonly partial record\"···)",
     "outcome": "failed",
     "new": true,
     "error": "Assert.Empty() Failure: Collection was not empty\nCollection: [warning AD0001: Analyzer 'MessagePack.SourceGenerator.Analyzers.MsgPack00xMessagePackAnalyzer' threw an exception of type 'System.IndexOutOfRangeException' with message 'Index was outside the bounds of the array.'.\r\nException occurred with following context:\r\nCompilation: App\nISymbol: Cmd (NamedType)\n\nSystem.IndexOutOfRangeException: In [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record class generic\", libraryDeclaration: \"[MessagePackObject] public partial record class It\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record struct generic map mode\", libraryDeclaration: \"[MessagePackObject(true)] public partial record st\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record struct generic\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "outcome": "failed",
     "new": true,
     "error": "Assert.Empty() Failure: Collection was not empty\nCollection: [warning AD0001: Analyzer 'MessagePack.SourceGenerator.Analyzers.MsgPack00xMessagePackAnalyzer' threw an exception of type 'System.IndexOutOfRangeException' with message 'Index was outside the bounds of the array.'.\r\nException occurred with following context:\r\nCompilation: App\nISymbol: Cmd (NamedType)\n\nSystem.IndexOutOfRangeException: In [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record struct\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic T member\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "failed",
     "new": true,
     "error": "Assert.Empty() Failure: Collection was not empty\nCollection: [warning AD0001: Analyzer 'MessagePack.SourceGenerator.Analyzers.MsgPack00xMessagePackAnalyzer' threw an exception of type 'System.IndexOutOfRangeException' with message 'Index was outside the bounds of the array.'.\r\nException occurred with following context:\r\nCompilation: App\nISymbol: Cmd (NamedType)\n\nSystem.IndexOutOfRangeException: In [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic explicit private field\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "failed",
     "new": true,
     "error": "Assert.Empty() Failure: Collection was not empty\nCollection: [warning AD0001: Analyzer 'MessagePack.SourceGenerator.Analyzers.MsgPack00xMessagePackAnalyzer' threw an exception of type 'System.IndexOutOfRangeException' with message 'Index was outside the bounds of the array.'.\r\nException occurred with following context:\r\nCompilation: App\nISymbol: Cmd (NamedType)\n\nSystem.IndexOutOfRangeException: In [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic field\", libraryDeclaration: \"[MessagePackObject] public struct Item<T> { [Key(0\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic init\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "failed",
     "new": true,
     "error": "Assert.Empty() Failure: Collection was not empty\nCollection: [warning AD0001: Analyzer 'MessagePack.SourceGenerator.Analyzers.MsgPack00xMessagePackAnalyzer' threw an exception of type 'System.IndexOutOfRangeException' with message 'Index was outside the bounds of the array.'.\r\nException occurred with following context:\r\nCompilation: App\nISymbol: Cmd (NamedType)\n\nSystem.IndexOutOfRangeException: In [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic map mode\", libraryDeclaration: \"[MessagePackObject(true)] public partial struct It\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic string key\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "failed",
     "new": true,
     "error": "Assert.Empty() Failure: Collection was not empty\nCollection: [warning AD0001: Analyzer 'MessagePack.SourceGenerator.Analyzers.MsgPack00xMessagePackAnalyzer' threw an exception of type 'System.IndexOutOfRangeException' with message 'Index was outside the bounds of the array.'.\r\nException occurred with following context:\r\nCompilation: App\nISymbol: Cmd (NamedType)\n\nSystem.IndexOutOfRangeException: In [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "failed",
     "new": true,
     "error": "Assert.Empty() Failure: Collection was not empty\nCollection: [warning AD0001: Analyzer 'MessagePack.SourceGenerator.Analyzers.MsgPack00xMessagePackAnalyzer' threw an exception of type 'System.IndexOutOfRangeException' with message 'Index was outside the bounds of the array.'.\r\nException occurred with following context:\r\nCompilation: App\nISymbol: Cmd (NamedType)\n\nSystem.IndexOutOfRangeException: In [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct\", libraryDeclaration: \"[MessagePackObject] public partial struct Item { [\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrowOnInvalidReferencedType(libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "outcome": "failed",
     "new": false,
     "error": "Assert.DoesNotContain() Failure: Filter matched in collection\n             ↓ (pos 0)\nCollection: [warning AD0001: Analyzer 'MessagePack.SourceGenerator.Analyzers.MsgPack00xMessagePackAnalyzer' threw an exception of type 'System.IndexOutOfRangeException' with message 'Index was outside the bounds of the array.'.\r\nException occurred with following context:\r\nCompilation: App\nISymbol: Cmd (NamedType)\n [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrowOnInvalidReferencedType(libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "failed",
     "new": false,
     "error": "Assert.DoesNotContain() Failure: Filter matched in collection\n                                                                                                                                                                                     ↓ (pos 1)\nCollection: [error MsgPack004: Properties and fields of MessagePackObject-attributed types require either KeyAttribute or IgnoreMemberAttribute: gl [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrowOnInvalidReferencedType(libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "failed",
     "new": false,
     "error": "Assert.DoesNotContain() Failure: Filter matched in collection\n             ↓ (pos 0)\nCollection: [warning AD0001: Analyzer 'MessagePack.SourceGenerator.Analyzers.MsgPack00xMessagePackAnalyzer' threw an exception of type 'System.IndexOutOfRangeException' with message 'Index was outside the bounds of the array.'.\r\nException occurred with following context:\r\nCompilation: App\nISymbol: Cmd (NamedType)\n [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrowOnInvalidReferencedType(libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "failed",
     "new": false,
     "error": "Assert.DoesNotContain() Failure: Filter matched in collection\n             ↓ (pos 0)\nCollection: [warning AD0001: Analyzer 'MessagePack.SourceGenerator.Analyzers.MsgPack00xMessagePackAnalyzer' threw an exception of type 'System.IndexOutOfRangeException' with message 'Index was outside the bounds of the array.'.\r\nException occurred with following context:\r\nCompilation: App\nISymbol: Cmd (NamedType)\n [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrowOnInvalidReferencedType(libraryDeclaration: \"[MessagePackObject] public struct Item<T> { [Key(0\"···)",
     "outcome": "failed",
     "new": false,
     "error": "Assert.DoesNotContain() Failure: Filter matched in collection\n             ↓ (pos 0)\nCollection: [warning AD0001: Analyzer 'MessagePack.SourceGenerator.Analyzers.MsgPack00xMessagePackAnalyzer' threw an exception of type 'System.IndexOutOfRangeException' with message 'Index was outside the bounds of the array.'.\r\nException occurred with following context:\r\nCompilation: App\nISymbol: Cmd (NamedType)\n [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerStillReportsProblemsInReferencingProject",
     "outcome": "failed",
     "new": true,
     "error": "Assert.Equal() Failure: Strings differ\n           ↓ (pos 0)\nExpected: \"MsgPack004\"\nActual:   \"AD0001\"\n           ↑ (pos 0)"
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorCollectsTypeArgumentOfReferencedGenericValueType",
     "outcome": "failed",
     "new": true,
     "error": "Assert.All() Failure: 1 out of 1 items in the collection did not pass.\n[0]: Item:  Microsoft.CodeAnalysis.GeneratorRunResult\n     Error: Assert.Null() Failure: Value is not null\n            Expected: null\n            Actual:   System.IndexOutOfRangeException: Index was outside the bounds of the array.\n               at System.Collections.Immutable.ImmutableArray`1.get_Item(Int32 index)\n            [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"class generic\", libraryDeclaration: \"[MessagePackObject] public partial class Item<T> {\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"readonly record struct generic\", libraryDeclaration: \"[MessagePackObject] public readonly partial record\"···)",
     "outcome": "failed",
     "new": true,
     "error": "Assert.All() Failure: 1 out of 1 items in the collection did not pass.\n[0]: Item:  Microsoft.CodeAnalysis.GeneratorRunResult\n     Error: Assert.Null() Failure: Value is not null\n            Expected: null\n            Actual:   System.IndexOutOfRangeException: Index was outside the bounds of the array.\n               at System.Collections.Immutable.ImmutableArray`1.get_Item(Int32 index)\n            [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record class generic\", libraryDeclaration: \"[MessagePackObject] public partial record class It\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record struct generic map mode\", libraryDeclaration: \"[MessagePackObject(true)] public partial record st\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record struct generic\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "outcome": "failed",
     "new": true,
     "error": "Assert.All() Failure: 1 out of 1 items in the collection did not pass.\n[0]: Item:  Microsoft.CodeAnalysis.GeneratorRunResult\n     Error: Assert.Null() Failure: Value is not null\n            Expected: null\n            Actual:   System.IndexOutOfRangeException: Index was outside the bounds of the array.\n               at System.Collections.Immutable.ImmutableArray`1.get_Item(Int32 index)\n            [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record struct\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic T member\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "failed",
     "new": true,
     "error": "Assert.All() Failure: 1 out of 1 items in the collection did not pass.\n[0]: Item:  Microsoft.CodeAnalysis.GeneratorRunResult\n     Error: Assert.Null() Failure: Value is not null\n            Expected: null\n            Actual:   System.IndexOutOfRangeException: Index was outside the bounds of the array.\n               at System.Collections.Immutable.ImmutableArray`1.get_Item(Int32 index)\n            [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic explicit private field\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "failed",
     "new": true,
     "error": "Assert.All() Failure: 1 out of 1 items in the collection did not pass.\n[0]: Item:  Microsoft.CodeAnalysis.GeneratorRunResult\n     Error: Assert.Null() Failure: Value is not null\n            Expected: null\n            Actual:   System.IndexOutOfRangeException: Index was outside the bounds of the array.\n               at System.Collections.Immutable.ImmutableArray`1.get_Item(Int32 index)\n            [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic field\", libraryDeclaration: \"[MessagePackObject] public struct Item<T> { [Key(0\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic init\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "failed",
     "new": true,
     "error": "Assert.All() Failure: 1 out of 1 items in the collection did not pass.\n[0]: Item:  Microsoft.CodeAnalysis.GeneratorRunResult\n     Error: Assert.Null() Failure: Value is not null\n            Expected: null\n            Actual:   System.IndexOutOfRangeException: Index was outside the bounds of the array.\n               at System.Collections.Immutable.ImmutableArray`1.get_Item(Int32 index)\n            [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic map mode\", libraryDeclaration: \"[MessagePackObject(true)] public partial struct It\"···)",
     "outcome": "passed",
     "new": true
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic string key\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "failed",
     "new": true,
     "error": "Assert.All() Failure: 1 out of 1 items in the collection did not pass.\n[0]: Item:  Microsoft.CodeAnalysis.GeneratorRunResult\n     Error: Assert.Null() Failure: Value is not null\n            Expected: null\n            Actual:   System.IndexOutOfRangeException: Index was outside the bounds of the array.\n               at System.Collections.Immutable.ImmutableArray`1.get_Item(Int32 index)\n            [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "outcome": "failed",
     "new": true,
     "error": "Assert.All() Failure: 1 out of 1 items in the collection did not pass.\n[0]: Item:  Microsoft.CodeAnalysis.GeneratorRunResult\n     Error: Assert.Null() Failure: Value is not null\n            Expected: null\n            Actual:   System.IndexOutOfRangeException: Index was outside the bounds of the array.\n               at System.Collections.Immutable.ImmutableArray`1.get_Item(Int32 index)\n            [...]"
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct\", libraryDeclaration: \"[MessagePackObject] public partial struct Item { [\"···)",
     "outcome": "passed",
     "new": true
    }
   ],
   "log": "evidence/var-2283-v2/logs/tests_fail_without_fix.1.log",
   "duration_s": 3.0,
   "reverted_files": [
    "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs"
   ],
   "full_suite_with_source_reverted": {
    "total": 203,
    "failed": 22,
    "failed_tests": [
     "MsgPack00xAnalyzerTests.NullStringKey_RecordPrimaryConstructorParameter",
     "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"readonly record struct generic\", libraryDeclaration: \"[MessagePackObject] public readonly partial record\"···)",
     "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record struct generic\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic T member\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic explicit private field\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic init\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic string key\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrowOnInvalidReferencedType(libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrowOnInvalidReferencedType(libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrowOnInvalidReferencedType(libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrowOnInvalidReferencedType(libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrowOnInvalidReferencedType(libraryDeclaration: \"[MessagePackObject] public struct Item<T> { [Key(0\"···)",
     "ReferencedAssemblyTypesTests.AnalyzerStillReportsProblemsInReferencingProject",
     "ReferencedAssemblyTypesTests.GeneratorCollectsTypeArgumentOfReferencedGenericValueType",
     "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"readonly record struct generic\", libraryDeclaration: \"[MessagePackObject] public readonly partial record\"···)",
     "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record struct generic\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic T member\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic explicit private field\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic init\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic string key\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)"
    ],
    "log": "evidence/var-2283-v2/logs/fail_without_fix.full_suite.log"
   },
   "new_failed": 17,
   "new_total": 31
  },
  {
   "id": "tests.full_suite",
   "tool": "dotnet test",
   "tool_version": "8.0.402",
   "status": "pass",
   "summary": "tests/MessagePack.SourceGenerator.Tests: 203 tests, 203 passed, 0 failed (0 not failing on base, 0 also failing on base)",
   "project": "tests/MessagePack.SourceGenerator.Tests",
   "total": 203,
   "passed": 203,
   "failed": 0,
   "failures_not_on_base": [],
   "failures_also_on_base": [],
   "log": "evidence/var-2283-v2/logs/tests_full_suite.log",
   "duration_s": 4.0,
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
    "diff_added_lines": 270,
    "files": 3,
    "paths": 3,
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
    "diff": "git diff 32258fdb e0348912 (added lines and file paths)",
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
   "summary": "5 mutants of the changed source lines: 1 killed, 4 survived; 1 of 3 mutated hunks have a killed mutant; surviving hunks: TypeCollector.cs:1050, TypeCollector.cs:1445-1455; 3 hunks not mutated",
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
    "FullyQualifiedName~ReferencedAssemblyTypesTests.|FullyQualifiedName~MsgPack00xAnalyzerTests."
   ],
   "tests_judged": [
    "MsgPack00xAnalyzerTests.NullStringKey_RecordPrimaryConstructorParameter",
    "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"class generic\", libraryDeclaration: \"[MessagePackObject] public partial class Item<T> {\"···)",
    "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"readonly record struct generic\", libraryDeclaration: \"[MessagePackObject] public readonly partial record\"···)",
    "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record class generic\", libraryDeclaration: \"[MessagePackObject] public partial record class It\"···)",
    "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record struct generic map mode\", libraryDeclaration: \"[MessagePackObject(true)] public partial record st\"···)",
    "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record struct generic\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
    "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record struct\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
    "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic T member\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
    "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic explicit private field\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
    "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic field\", libraryDeclaration: \"[MessagePackObject] public struct Item<T> { [Key(0\"···)",
    "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic init\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
    "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic map mode\", libraryDeclaration: \"[MessagePackObject(true)] public partial struct It\"···)",
    "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic string key\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
    "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
    "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct\", libraryDeclaration: \"[MessagePackObject] public partial struct Item { [\"···)",
    "ReferencedAssemblyTypesTests.AnalyzerStillReportsProblemsInReferencingProject",
    "ReferencedAssemblyTypesTests.GeneratorCollectsTypeArgumentOfReferencedGenericValueType",
    "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"class generic\", libraryDeclaration: \"[MessagePackObject] public partial class Item<T> {\"···)",
    "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"readonly record struct generic\", libraryDeclaration: \"[MessagePackObject] public readonly partial record\"···)",
    "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record class generic\", libraryDeclaration: \"[MessagePackObject] public partial record class It\"···)",
    "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record struct generic map mode\", libraryDeclaration: \"[MessagePackObject(true)] public partial record st\"···)",
    "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record struct generic\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
    "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record struct\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
    "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic T member\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
    "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic explicit private field\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
    "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic field\", libraryDeclaration: \"[MessagePackObject] public struct Item<T> { [Key(0\"···)",
    "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic init\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
    "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic map mode\", libraryDeclaration: \"[MessagePackObject(true)] public partial struct It\"···)",
    "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic string key\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
    "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
    "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct\", libraryDeclaration: \"[MessagePackObject] public partial struct Item { [\"···)"
   ],
   "not_covered": "ExecutionTests/MapModeExecutionTests (SDK 9) are not run against the mutants; files that are not C# are not mutated",
   "hunks": [
    {
     "id": "H1",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      753,
      753
     ],
     "code_lines": [
      753
     ],
     "mutants": [],
     "status": "not_mutated",
     "why": "no operator applies to its lines"
    },
    {
     "id": "H2",
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
     "status": "killed"
    },
    {
     "id": "H3",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1050,
      1050
     ],
     "code_lines": [
      1050
     ],
     "mutants": [
      "M2",
      "M4",
      "M5"
     ],
     "status": "survived"
    },
    {
     "id": "H4",
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
    },
    {
     "id": "H5",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1429,
      1443
     ],
     "code_lines": [
      1433,
      1435,
      1436,
      1438,
      1439,
      1440,
      1441
     ],
     "mutants": [],
     "status": "not_mutated",
     "why": "no operator applies to its lines"
    },
    {
     "id": "H6",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "lines": [
      1445,
      1455
     ],
     "code_lines": [
      1455
     ],
     "mutants": [
      "M3"
     ],
     "status": "survived"
    }
   ],
   "surviving_hunks": [
    "H3",
    "H6"
   ],
   "mutants": [
    {
     "id": "M1",
     "hunk": "H2",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "line": 985,
     "operator": "remove_call",
     "before": "                        this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.BothStringAndIntKeyAreNull, GetIdentifierLocation(item), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name));",
     "after": "                        { }",
     "log": [
      "evidence/var-2283-v2/logs/mutation/M1.build.log",
      "evidence/var-2283-v2/logs/mutation/M1.test.1.log"
     ],
     "diff": "evidence/var-2283-v2/logs/mutation/M1.diff",
     "killed_by": [
      "MsgPack00xAnalyzerTests.NullStringKey_RecordPrimaryConstructorParameter"
     ],
     "existing_tests_failed": [
      "MsgPack00xAnalyzerTests.NullStringKey"
     ],
     "outcome": "killed",
     "tests_run": 66
    },
    {
     "id": "M2",
     "hunk": "H3",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "line": 1050,
     "operator": "negate_condition",
     "before": "                if (item.IsImplicitlyDeclared || item.IsStatic || IsCompilerGeneratedField(item))",
     "after": "                if (!(item.IsImplicitlyDeclared || item.IsStatic || IsCompilerGeneratedField(item)))",
     "log": [
      "evidence/var-2283-v2/logs/mutation/M2.build.log",
      "evidence/var-2283-v2/logs/mutation/M2.test.1.log"
     ],
     "diff": "evidence/var-2283-v2/logs/mutation/M2.diff",
     "killed_by": [],
     "existing_tests_failed": [
      "MsgPack00xAnalyzerTests.AddAttributeToField_WithComment",
      "MsgPack00xAnalyzerTests.AddAttributeToType_Fields",
      "MsgPack00xAnalyzerTests.AddAttributeToType_Generic",
      "MsgPack00xAnalyzerTests.AddAttributeToType_Nullable",
      "MsgPack00xAnalyzerTests.AddAttributesToMembers_AllowPrivateAttribute",
      "MsgPack00xAnalyzerTests.AddAttributesToMembers_MixedVisibility",
      "MsgPack00xAnalyzerTests.AddIgnoreAttributesToMembers",
      "MsgPack00xAnalyzerTests.DerivedAttributes"
     ],
     "outcome": "survived",
     "tests_run": 66
    },
    {
     "id": "M3",
     "hunk": "H6",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "line": 1455,
     "operator": "return_default",
     "before": "    private static bool IsCompilerGeneratedField(ISymbol member) => member is IFieldSymbol { CanBeReferencedByName: false };",
     "after": "    private static bool IsCompilerGeneratedField(ISymbol member) => default;",
     "log": [
      "evidence/var-2283-v2/logs/mutation/M3.build.log",
      "evidence/var-2283-v2/logs/mutation/M3.test.1.log"
     ],
     "diff": "evidence/var-2283-v2/logs/mutation/M3.diff",
     "killed_by": [],
     "existing_tests_failed": [],
     "outcome": "survived",
     "tests_run": 66
    },
    {
     "id": "M4",
     "hunk": "H3",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "line": 1050,
     "operator": "drop_guard",
     "before": "                if (item.IsImplicitlyDeclared || item.IsStatic || IsCompilerGeneratedField(item))",
     "after": "                if (true)",
     "log": [
      "evidence/var-2283-v2/logs/mutation/M4.build.log",
      "evidence/var-2283-v2/logs/mutation/M4.test.1.log"
     ],
     "diff": "evidence/var-2283-v2/logs/mutation/M4.diff",
     "killed_by": [],
     "existing_tests_failed": [
      "MsgPack00xAnalyzerTests.AddAttributeToField_WithComment",
      "MsgPack00xAnalyzerTests.AddAttributeToType_Fields",
      "MsgPack00xAnalyzerTests.AddAttributeToType_Generic",
      "MsgPack00xAnalyzerTests.AddAttributeToType_Nullable",
      "MsgPack00xAnalyzerTests.AddAttributesToMembers_MixedVisibility",
      "MsgPack00xAnalyzerTests.AddIgnoreAttributesToMembers",
      "MsgPack00xAnalyzerTests.DerivedAttributes"
     ],
     "outcome": "survived",
     "tests_run": 66
    },
    {
     "id": "M5",
     "hunk": "H3",
     "file": "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs",
     "line": 1050,
     "operator": "swap_logical",
     "before": "                if (item.IsImplicitlyDeclared || item.IsStatic || IsCompilerGeneratedField(item))",
     "after": "                if (item.IsImplicitlyDeclared && item.IsStatic || IsCompilerGeneratedField(item))",
     "log": [
      "evidence/var-2283-v2/logs/mutation/M5.build.log",
      "evidence/var-2283-v2/logs/mutation/M5.test.1.log"
     ],
     "diff": "evidence/var-2283-v2/logs/mutation/M5.diff",
     "killed_by": [],
     "existing_tests_failed": [],
     "outcome": "survived",
     "tests_run": 66
    }
   ],
   "kills_by_test": [
    {
     "name": "MsgPack00xAnalyzerTests.NullStringKey_RecordPrimaryConstructorParameter",
     "killed": [
      "M1"
     ]
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"class generic\", libraryDeclaration: \"[MessagePackObject] public partial class Item<T> {\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"readonly record struct generic\", libraryDeclaration: \"[MessagePackObject] public readonly partial record\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record class generic\", libraryDeclaration: \"[MessagePackObject] public partial record class It\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record struct generic map mode\", libraryDeclaration: \"[MessagePackObject(true)] public partial record st\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record struct generic\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"record struct\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic T member\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic explicit private field\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic field\", libraryDeclaration: \"[MessagePackObject] public struct Item<T> { [Key(0\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic init\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic map mode\", libraryDeclaration: \"[MessagePackObject(true)] public partial struct It\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic string key\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct generic\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerDoesNotThrow(caseName: \"struct\", libraryDeclaration: \"[MessagePackObject] public partial struct Item { [\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.AnalyzerStillReportsProblemsInReferencingProject",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorCollectsTypeArgumentOfReferencedGenericValueType",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"class generic\", libraryDeclaration: \"[MessagePackObject] public partial class Item<T> {\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"readonly record struct generic\", libraryDeclaration: \"[MessagePackObject] public readonly partial record\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record class generic\", libraryDeclaration: \"[MessagePackObject] public partial record class It\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record struct generic map mode\", libraryDeclaration: \"[MessagePackObject(true)] public partial record st\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record struct generic\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"record struct\", libraryDeclaration: \"[MessagePackObject] public partial record struct I\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic T member\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic explicit private field\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic field\", libraryDeclaration: \"[MessagePackObject] public struct Item<T> { [Key(0\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic init\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic map mode\", libraryDeclaration: \"[MessagePackObject(true)] public partial struct It\"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic string key\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct generic\", libraryDeclaration: \"[MessagePackObject] public partial struct Item<T> \"···)",
     "killed": []
    },
    {
     "name": "ReferencedAssemblyTypesTests.GeneratorProducesResolver(caseName: \"struct\", libraryDeclaration: \"[MessagePackObject] public partial struct Item { [\"···)",
     "killed": []
    }
   ],
   "log": "evidence/var-2283-v2/logs/mutation/"
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
  "raw_runs": "evidence/var-scripts/runs.sh -> /data/work/var/out/var-2283-v2[-fwf] (not committed; logs copied to evidence/var-2283-v2/logs/)"
 }
}
```

## Files changed (3: 3 non-generated, 0 generated)
- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs (+32 -4, source)
- tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs (+16 -0, test)
- tests/MessagePack.SourceGenerator.Tests/ReferencedAssemblyTypesTests.cs (+222 -0, test)

## Diff (non-generated files)
```diff
diff --git a/src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs b/src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs
index e121773d..1a44cc8c 100644
--- a/src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs
+++ b/src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs
@@ -750,7 +750,7 @@ public class TypeCollector
 
         HashSet<Diagnostic> reportedDiagnostics = new();
         IEnumerable<ISymbol> instanceMembers = formattedType.GetAllMembers()
-            .Where(m => m is IFieldSymbol or IPropertySymbol && !(m.IsStatic || m.IsOverride || m.IsImplicitlyDeclared));
+            .Where(m => m is IFieldSymbol or IPropertySymbol && !(m.IsStatic || m.IsOverride || m.IsImplicitlyDeclared || IsCompilerGeneratedField(m)));
 
         // The actual member identifiers of each serializable member,
         // such that we'll recognize collisions as we enumerate members in base types
@@ -982,7 +982,7 @@ public class TypeCollector
                     var stringKey = key is { Value: string stringKeyValue } ? stringKeyValue : default;
                     if (intKey == null && stringKey == null)
                     {
-                        this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.BothStringAndIntKeyAreNull, ((PropertyDeclarationSyntax)item.DeclaringSyntaxReferences[0].GetSyntax()).Identifier.GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name));
+                        this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.BothStringAndIntKeyAreNull, GetIdentifierLocation(item), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name));
                     }
 
                     // A property with an init accessor and an initializer has a default that will be discarded by the deserializer.
@@ -1047,7 +1047,7 @@ public class TypeCollector
 
             foreach (IFieldSymbol item in formattedType.GetAllMembers().OfType<IFieldSymbol>())
             {
-                if (item.IsImplicitlyDeclared || item.IsStatic)
+                if (item.IsImplicitlyDeclared || item.IsStatic || IsCompilerGeneratedField(item))
                 {
                     continue;
                 }
@@ -1074,7 +1074,7 @@ public class TypeCollector
                             {
                                 Diagnostic diagnostic = derivedKeyAttribute is not null && suppressSourceGeneration is not true
                                     ? Diagnostic.Create(MsgPack00xMessagePackAnalyzer.AOTDerivedKeyAttribute, derivedKeyAttribute.GetSyntax(this.cancellationToken).GetLocation())
-                                    : Diagnostic.Create(MsgPack00xMessagePackAnalyzer.MemberNeedsKey, item.DeclaringSyntaxReferences[0].GetSyntax().GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name);
+                                    : Diagnostic.Create(MsgPack00xMessagePackAnalyzer.MemberNeedsKey, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax(this.cancellationToken).GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name);
                                 if (nonPublicMembersAreSerialized || (item.DeclaredAccessibility & Accessibility.Public) == Accessibility.Public)
                                 {
                                     this.reportDiagnostic?.Invoke(diagnostic);
@@ -1426,6 +1426,34 @@ public class TypeCollector
 
     private static Location? GetIdentifierLocation(INamedTypeSymbol type) => ((BaseTypeDeclarationSyntax?)type.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax())?.Identifier.GetLocation();
 
+    /// <summary>
+    /// Gets the location of the identifier of a property, which may be declared as a property or as a record primary constructor parameter.
+    /// </summary>
+    /// <returns>The location, or <see langword="null"/> if the property has no syntax (e.g. it is declared in a referenced assembly).</returns>
+    private static Location? GetIdentifierLocation(IPropertySymbol property)
+    {
+        SyntaxNode? syntax = property.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax();
+        return syntax switch
+        {
+            PropertyDeclarationSyntax { Identifier: SyntaxToken propertyId } => propertyId.GetLocation(),
+            ParameterSyntax { Identifier: SyntaxToken parameterId } => parameterId.GetLocation(),
+            not null => syntax.GetLocation(),
+            _ => null,
+        };
+    }
+
+    /// <summary>
+    /// Identifies fields that the compiler synthesized (e.g. auto-property backing fields such as <c>&lt;Key&gt;k__BackingField</c>).
+    /// </summary>
+    /// <remarks>
+    /// Such fields are flagged by <see cref="ISymbol.IsImplicitlyDeclared"/> only when they come from source.
+    /// When they come from a referenced assembly (which notably happens for the private fields of value types,
+    /// since the compiler imports them to compute struct layout), they look like ordinary private fields
+    /// except that their names are not valid C# identifiers.
+    /// They can never be serialized by generated code, nor be attributed by the user.
+    /// </remarks>
+    private static bool IsCompilerGeneratedField(ISymbol member) => member is IFieldSymbol { CanBeReferencedByName: false };
+
     private static Location? GetLocation(IParameterSymbol parameter) => parameter.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation();
 
     private static Location? GetParameterListLocation(IMethodSymbol? method) => ((BaseMethodDeclarationSyntax?)method?.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax())?.ParameterList.GetLocation();

diff --git a/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs b/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs
index d39d74ef..1d92450a 100644
--- a/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs
+++ b/tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs
@@ -92,6 +92,22 @@ public class Foo
         }.RunAsync();
     }
 
+    [Fact]
+    public async Task NullStringKey_RecordPrimaryConstructorParameter()
+    {
+        // The property is declared by a ParameterSyntax rather than a PropertyDeclarationSyntax.
+        string input = Preamble + @"
+[MessagePackObject]
+public record {|MsgPack007:Foo|}([property: Key(null)] string {|MsgPack005:Member|});
+";
+
+        await new VerifyCS.Test
+        {
+            TestCode = input,
+            MarkupOptions = MarkupOptions.UseFirstDescriptor,
+        }.RunAsync();
+    }
+
     [Fact]
     public async Task AddAttributesToMembers()
     {

diff --git a/tests/MessagePack.SourceGenerator.Tests/ReferencedAssemblyTypesTests.cs b/tests/MessagePack.SourceGenerator.Tests/ReferencedAssemblyTypesTests.cs
new file mode 100644
index 00000000..dfb8fe43
--- /dev/null
+++ b/tests/MessagePack.SourceGenerator.Tests/ReferencedAssemblyTypesTests.cs
@@ -0,0 +1,222 @@
+// Copyright (c) All contributors. All rights reserved.
+// Licensed under the MIT license. See LICENSE file in the project root for full license information.
+
+using MessagePack.SourceGenerator;
+using MessagePack.SourceGenerator.Analyzers;
+using Microsoft.CodeAnalysis;
+using Microsoft.CodeAnalysis.CSharp;
+using Microsoft.CodeAnalysis.Diagnostics;
+
+/// <summary>
+/// Tests for data types whose members are typed as types that are defined in a referenced assembly,
+/// and thus are only available as metadata symbols (no <see cref="ISymbol.DeclaringSyntaxReferences"/>).
+/// </summary>
+/// <remarks>
+/// <para>
+/// These tests deliberately reference the library by <em>emitted image</em>.
+/// The Roslyn testing framework's <c>AdditionalProjects</c> produces compilation references,
+/// whose symbols still carry syntax and therefore cannot reproduce metadata-only bugs.
+/// </para>
+/// <para>
+/// Regression tests for https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2283.
+/// </para>
+/// </remarks>
+public class ReferencedAssemblyTypesTests(ITestOutputHelper logger)
+{
+    /// <summary>
+    /// Declarations of <c>Lib.Item</c> (generic or not) as they might appear in a referenced library.
+    /// </summary>
+    public static readonly TheoryData<string, string> LibraryItemDeclarations = new()
+    {
+        // The cases from the issue that used to crash: generic value types.
+        { "record struct generic", "[MessagePackObject] public partial record struct Item<T>([property: Key(0)] string Key);" },
+        { "struct generic", "[MessagePackObject] public partial struct Item<T> { [Key(0)] public string Key { get; set; } }" },
+        { "readonly record struct generic", "[MessagePackObject] public readonly partial record struct Item<T>([property: Key(0)] string Key);" },
+        { "struct generic init", "[MessagePackObject] public partial struct Item<T> { [Key(0)] public string Key { get; init; } }" },
+        { "struct generic T member", "[MessagePackObject] public partial struct Item<T> { [Key(0)] public string Key { get; set; } [Key(1)] public T Value { get; set; } }" },
+        { "struct generic explicit private field", "[MessagePackObject] public partial struct Item<T> { private int hidden; [Key(0)] public string Key { get => hidden.ToString(); set => hidden = value.Length; } }" },
+        { "struct generic field", "[MessagePackObject] public struct Item<T> { [Key(0)] public string Key; }" },
+        { "struct generic map mode", "[MessagePackObject(true)] public partial struct Item<T> { public string Key { get; set; } }" },
+        { "record struct generic map mode", "[MessagePackObject(true)] public partial record struct Item<T>(string Key);" },
+        { "struct generic string key", "[MessagePackObject] public partial struct Item<T> { [Key(\"key\")] public string Key { get; set; } }" },
+
+        // The cases from the issue that already worked.
+        { "struct", "[MessagePackObject] public partial struct Item { [Key(0)] public string Key { get; set; } }" },
+        { "record struct", "[MessagePackObject] public partial record struct Item([property: Key(0)] string Key);" },
+        { "class generic", "[MessagePackObject] public partial class Item<T> { [Key(0)] public string Key { get; set; } }" },
+        { "record class generic", "[MessagePackObject] public partial record class Item<T>([property: Key(0)] string Key);" },
+    };
+
+    [Theory]
+    [MemberData(nameof(LibraryItemDeclarations))]
+    public async Task GeneratorProducesResolver(string caseName, string libraryDeclaration)
+    {
+        logger.WriteLine(caseName);
+        CSharpCompilation app = await CreateAppCompilationAsync(libraryDeclaration);
+
+        GeneratorDriver driver = CSharpGeneratorDriver.Create(
+            generators: [new MessagePackGenerator().AsSourceGenerator()],
+            parseOptions: ParseOptions);
+        driver = driver.RunGeneratorsAndUpdateCompilation(app, out Compilation output, out ImmutableArray<Diagnostic> generatorDiagnostics);
+        GeneratorDriverRunResult runResult = driver.GetRunResult();
+
+        foreach (SyntaxTree tree in runResult.GeneratedTrees)
+        {
+            logger.WriteLine($"--- {tree.FilePath}");
+            logger.WriteLine(tree.ToString());
+        }
+
+        // A generator exception surfaces as CS8785 and suppresses all generated output.
+        Assert.All(runResult.Results, r => Assert.Null(r.Exception));
+        Assert.Empty(generatorDiagnostics);
+
+        // The compiling assembly must end up with its generated resolver.
+        Assert.NotNull(output.GetTypeByMetadataName("MessagePack.GeneratedMessagePackResolver"));
+
+        // ...and the generated code must compile.
+        Diagnostic[] errors = output.GetDiagnostics().Where(d => d.Severity == DiagnosticSeverity.Error).ToArray();
+        Assert.True(errors.Length == 0, string.Join(Environment.NewLine, errors.Select(e => e.ToString())));
+    }
+
+    [Theory]
+    [MemberData(nameof(LibraryItemDeclarations))]
+    public async Task AnalyzerDoesNotThrow(string caseName, string libraryDeclaration)
+    {
+        logger.WriteLine(caseName);
+        CSharpCompilation app = await CreateAppCompilationAsync(libraryDeclaration);
+
+        ImmutableArray<DiagnosticAnalyzer> analyzers = typeof(MsgPack00xMessagePackAnalyzer).Assembly.GetTypes()
+            .Where(t => typeof(DiagnosticAnalyzer).IsAssignableFrom(t) && !t.IsAbstract)
+            .Select(t => (DiagnosticAnalyzer)Activator.CreateInstance(t)!)
+            .ToImmutableArray();
+
+        // Analyzer exceptions are reported as AD0001 diagnostics.
+        ImmutableArray<Diagnostic> diagnostics = await app.WithAnalyzers(analyzers).GetAnalyzerDiagnosticsAsync();
+        foreach (Diagnostic diagnostic in diagnostics)
+        {
+            logger.WriteLine(diagnostic.ToString());
+        }
+
+        Assert.Empty(diagnostics);
+    }
+
+    /// <summary>
+    /// The analyzer must still report a genuine problem in the referencing project
+    /// (rather than crashing, or reporting nothing because it crashed).
+    /// </summary>
+    [Fact]
+    public async Task AnalyzerStillReportsProblemsInReferencingProject()
+    {
+        CSharpCompilation app = await CreateAppCompilationAsync(
+            "[MessagePackObject] public partial record struct Item<T>([property: Key(0)] string Key);",
+            appMembers: "[Key(1)] public Item<int> Member { get; init; } public int Unattributed { get; set; }");
+
+        ImmutableArray<DiagnosticAnalyzer> analyzers = ImmutableArray.Create<DiagnosticAnalyzer>(new MsgPack00xMessagePackAnalyzer());
+        ImmutableArray<Diagnostic> diagnostics = await app.WithAnalyzers(analyzers).GetAnalyzerDiagnosticsAsync();
+        foreach (Diagnostic diagnostic in diagnostics)
+        {
+            logger.WriteLine(diagnostic.ToString());
+        }
+
+        Diagnostic single = Assert.Single(diagnostics);
+        Assert.Equal(MsgPack00xMessagePackAnalyzer.MemberNeedsKey.Id, single.Id);
+        Assert.True(single.Location.IsInSource);
+    }
+
+    /// <summary>
+    /// Diagnostics about members of a referenced type have no syntax to point at, and must not crash the analyzer.
+    /// </summary>
+    [Theory]
+    [InlineData("[MessagePackObject] public partial struct Item<T> { [Key((string)null)] public string Key { get; set; } }")]
+    [InlineData("[MessagePackObject] public partial record struct Item<T>([property: Key((string)null)] string Key);")]
+    [InlineData("[MessagePackObject] public partial struct Item<T> { [Key(0)] public string Key { get; set; } public int Unattributed { get; set; } }")]
+    [InlineData("[MessagePackObject] public struct Item<T> { [Key(0)] public string Key; public int Unattributed; }")]
+    [InlineData("[MessagePackObject] public partial struct Item<T> { [Key(0)] private string key; public int Unattributed; private int unattributedPrivate; }")]
+    public async Task AnalyzerDoesNotThrowOnInvalidReferencedType(string libraryDeclaration)
+    {
+        CSharpCompilation app = await CreateAppCompilationAsync(libraryDeclaration);
+
+        ImmutableArray<DiagnosticAnalyzer> analyzers = ImmutableArray.Create<DiagnosticAnalyzer>(new MsgPack00xMessagePackAnalyzer());
+        ImmutableArray<Diagnostic> diagnostics = await app.WithAnalyzers(analyzers).GetAnalyzerDiagnosticsAsync();
+        foreach (Diagnostic diagnostic in diagnostics)
+        {
+            logger.WriteLine(diagnostic.ToString());
+        }
+
+        Assert.DoesNotContain(diagnostics, d => d.Id == "AD0001");
+
+        GeneratorDriver driver = CSharpGeneratorDriver.Create(
+            generators: [new MessagePackGenerator().AsSourceGenerator()],
+            parseOptions: ParseOptions);
+        GeneratorDriverRunResult runResult = driver.RunGenerators(app).GetRunResult();
+        Assert.All(runResult.Results, r => Assert.Null(r.Exception));
+    }
+
+    /// <summary>
+    /// The type arguments of a closed generic from a referenced assembly must still be collected.
+    /// </summary>
+    [Fact]
+    public async Task GeneratorCollectsTypeArgumentOfReferencedGenericValueType()
+    {
+        CSharpCompilation app = await CreateAppCompilationAsync(
+            "[MessagePackObject] public partial record struct Item<T>([property: Key(0)] string Key, [property: Key(1)] T Value);",
+            appMembers: "[Key(1)] public Item<Payload> Member { get; init; }",
+            appTypes: "[MessagePackObject] public sealed class Payload { [Key(0)] public int X { get; set; } }");
+
+        GeneratorDriver driver = CSharpGeneratorDriver.Create(
+            generators: [new MessagePackGenerator().AsSourceGenerator()],
+            parseOptions: ParseOptions);
+        driver = driver.RunGeneratorsAndUpdateCompilation(app, out Compilation output, out ImmutableArray<Diagnostic> generatorDiagnostics);
+        GeneratorDriverRunResult runResult = driver.GetRunResult();
+        string allGenerated = string.Join(Environment.NewLine, runResult.GeneratedTrees.Select(t => t.ToString()));
+        logger.WriteLine(allGenerated);
+
+        Assert.All(runResult.Results, r => Assert.Null(r.Exception));
+        Assert.Empty(generatorDiagnostics);
+        Assert.Contains("PayloadFormatter", allGenerated);
+        Assert.Contains("global::Lib.Item<global::App.Payload>", allGenerated);
+        Assert.Empty(output.GetDiagnostics().Where(d => d.Severity == DiagnosticSeverity.Error));
+    }
+
+    private static CSharpParseOptions ParseOptions { get; } = new(LanguageVersion.CSharp12);
+
+    private static async Task<CSharpCompilation> CreateAppCompilationAsync(string libraryDeclaration, string? appMembers = null, string? appTypes = null)
+    {
+        ImmutableArray<MetadataReference> frameworkReferences = await ReferencesHelper.DefaultTargetFrameworkReferences.ResolveAsync(LanguageNames.CSharp, CancellationToken.None);
+        MetadataReference[] baseReferences = [.. frameworkReferences, .. ReferencesHelper.GetReferences(ReferencesSet.MessagePack)];
+
+        string libSource = $$"""
+            using MessagePack;
+            namespace Lib;
+            {{libraryDeclaration}}
+            """;
+        CSharpCompilation lib = CSharpCompilation.Create(
+            "Lib",
+            [CSharpSyntaxTree.ParseText(libSource, ParseOptions)],
+            baseReferences,
+            new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary, nullableContextOptions: NullableContextOptions.Disable));
+
+        using MemoryStream image = new();
+        Microsoft.CodeAnalysis.Emit.EmitResult emitResult = lib.Emit(image);
+        Assert.True(emitResult.Success, string.Join(Environment.NewLine, emitResult.Diagnostics));
+
+        string memberType = libraryDeclaration.Contains("Item<T>") ? "Item<int>" : "Item";
+        appMembers ??= $"[Key(1)] public {memberType} Member {{ get; init; }}";
+        string appSource = $$"""
+            using MessagePack;
+            using Lib;
+            namespace App;
+            [MessagePackObject]
+            public sealed partial record Cmd([property: Key(0)] string Scope)
+            {
+                {{appMembers}}
+            }
+            {{appTypes}}
+            """;
+        return CSharpCompilation.Create(
+            "App",
+            [CSharpSyntaxTree.ParseText(appSource, ParseOptions)],
+            [.. baseReferences, MetadataReference.CreateFromImage(image.ToArray())],
+            new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary, nullableContextOptions: NullableContextOptions.Disable));
+    }
+}

```

## File contents (line numbers in the gutter; quote the text after '| ')

### src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at head (e0348912), around the changed lines
```
  ... lines 1-719 not shown ...
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
  753|             .Where(m => m is IFieldSymbol or IPropertySymbol && !(m.IsStatic || m.IsOverride || m.IsImplicitlyDeclared || IsCompilerGeneratedField(m)));
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
  ... lines 787-951 not shown ...
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
  985|                         this.reportDiagnostic?.Invoke(Diagnostic.Create(MsgPack00xMessagePackAnalyzer.BothStringAndIntKeyAreNull, GetIdentifierLocation(item), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name));
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
 1050|                 if (item.IsImplicitlyDeclared || item.IsStatic || IsCompilerGeneratedField(item))
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
 1077|                                     : Diagnostic.Create(MsgPack00xMessagePackAnalyzer.MemberNeedsKey, item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax(this.cancellationToken).GetLocation(), formattedType.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat), item.Name);
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
  ... lines 1111-1395 not shown ...
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
 1429|     /// <summary>
 1430|     /// Gets the location of the identifier of a property, which may be declared as a property or as a record primary constructor parameter.
 1431|     /// </summary>
 1432|     /// <returns>The location, or <see langword="null"/> if the property has no syntax (e.g. it is declared in a referenced assembly).</returns>
 1433|     private static Location? GetIdentifierLocation(IPropertySymbol property)
 1434|     {
 1435|         SyntaxNode? syntax = property.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax();
 1436|         return syntax switch
 1437|         {
 1438|             PropertyDeclarationSyntax { Identifier: SyntaxToken propertyId } => propertyId.GetLocation(),
 1439|             ParameterSyntax { Identifier: SyntaxToken parameterId } => parameterId.GetLocation(),
 1440|             not null => syntax.GetLocation(),
 1441|             _ => null,
 1442|         };
 1443|     }
 1444| 
 1445|     /// <summary>
 1446|     /// Identifies fields that the compiler synthesized (e.g. auto-property backing fields such as <c>&lt;Key&gt;k__BackingField</c>).
 1447|     /// </summary>
 1448|     /// <remarks>
 1449|     /// Such fields are flagged by <see cref="ISymbol.IsImplicitlyDeclared"/> only when they come from source.
 1450|     /// When they come from a referenced assembly (which notably happens for the private fields of value types,
 1451|     /// since the compiler imports them to compute struct layout), they look like ordinary private fields
 1452|     /// except that their names are not valid C# identifiers.
 1453|     /// They can never be serialized by generated code, nor be attributed by the user.
 1454|     /// </remarks>
 1455|     private static bool IsCompilerGeneratedField(ISymbol member) => member is IFieldSymbol { CanBeReferencedByName: false };
 1456| 
 1457|     private static Location? GetLocation(IParameterSymbol parameter) => parameter.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation();
 1458| 
 1459|     private static Location? GetParameterListLocation(IMethodSymbol? method) => ((BaseMethodDeclarationSyntax?)method?.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax())?.ParameterList.GetLocation();
 1460| 
 1461|     private static string GetGenericFormatterClassName(INamedTypeSymbol type)
 1462|     {
 1463|         return type.Name;
 1464|     }
 1465| 
 1466|     private static string GetMinimallyQualifiedClassName(INamedTypeSymbol type)
 1467|     {
 1468|         var name = type.ContainingType is object ? GetMinimallyQualifiedClassName(type.ContainingType) + "_" : string.Empty;
 1469|         name += type.ToDisplayString(SymbolDisplayFormat.MinimallyQualifiedFormat);
 1470|         name = name.Replace('.', '_');
 1471|         name = name.Replace('<', '_');
 1472|         name = name.Replace('>', '_');
 1473|         name = Regex.Replace(name, @"\[([,])*\]", match => $"Array{match.Length - 1}");
 1474|         name = name.Replace("?", string.Empty);
 1475|         return name;
 1476|     }
 1477| 
 1478|     private static bool TryGetNextConstructor(IEnumerator<IMethodSymbol>? ctorEnumerator, ref IMethodSymbol? ctor)
 1479|     {
 1480|         if (ctorEnumerator == null || ctor != null)
 1481|         {
 1482|             return false;
 1483|         }
 1484| 
 1485|         if (ctorEnumerator.MoveNext())
 1486|         {
 1487|             ctor = ctorEnumerator.Current;
 1488|             return true;
 1489|         }
  ... lines 1490-1519 not shown ...
```

### tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs at head (e0348912), around the changed lines
```
  ... lines 1-61 not shown ...
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
   96|     public async Task NullStringKey_RecordPrimaryConstructorParameter()
   97|     {
   98|         // The property is declared by a ParameterSyntax rather than a PropertyDeclarationSyntax.
   99|         string input = Preamble + @"
  100| [MessagePackObject]
  101| public record {|MsgPack007:Foo|}([property: Key(null)] string {|MsgPack005:Member|});
  102| ";
  103| 
  104|         await new VerifyCS.Test
  105|         {
  106|             TestCode = input,
  107|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  108|         }.RunAsync();
  109|     }
  110| 
  111|     [Fact]
  112|     public async Task AddAttributesToMembers()
  113|     {
  114|         string input = Preamble + @"
  115| [MessagePackObject]
  116| public class Foo
  117| {
  118|     public string {|MsgPack004:Member1|} { get; set; }
  119|     public string {|MsgPack004:Member2|} { get; set; }
  120| }
  121| ";
  122| 
  123|         string output = Preamble + @"
  124| [MessagePackObject]
  125| public class Foo
  126| {
  127|     [Key(0)]
  128|     public string Member1 { get; set; }
  129|     [Key(1)]
  130|     public string Member2 { get; set; }
  131| }
  132| ";
  133| 
  134|         await new VerifyCS.Test
  135|         {
  136|             TestCode = input,
  137|             FixedCode = output,
  138|             MarkupOptions = MarkupOptions.UseFirstDescriptor,
  139|             CodeActionEquivalenceKey = MessagePackCodeFixProvider.AddKeyAttributeEquivanceKey,
  140|         }.RunAsync();
  141|     }
  142| 
  143|     /// <summary>
  ... lines 144-1106 not shown ...
```

### tests/MessagePack.SourceGenerator.Tests/ReferencedAssemblyTypesTests.cs at head (e0348912), full file
```
    1| // Copyright (c) All contributors. All rights reserved.
    2| // Licensed under the MIT license. See LICENSE file in the project root for full license information.
    3| 
    4| using MessagePack.SourceGenerator;
    5| using MessagePack.SourceGenerator.Analyzers;
    6| using Microsoft.CodeAnalysis;
    7| using Microsoft.CodeAnalysis.CSharp;
    8| using Microsoft.CodeAnalysis.Diagnostics;
    9| 
   10| /// <summary>
   11| /// Tests for data types whose members are typed as types that are defined in a referenced assembly,
   12| /// and thus are only available as metadata symbols (no <see cref="ISymbol.DeclaringSyntaxReferences"/>).
   13| /// </summary>
   14| /// <remarks>
   15| /// <para>
   16| /// These tests deliberately reference the library by <em>emitted image</em>.
   17| /// The Roslyn testing framework's <c>AdditionalProjects</c> produces compilation references,
   18| /// whose symbols still carry syntax and therefore cannot reproduce metadata-only bugs.
   19| /// </para>
   20| /// <para>
   21| /// Regression tests for https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2283.
   22| /// </para>
   23| /// </remarks>
   24| public class ReferencedAssemblyTypesTests(ITestOutputHelper logger)
   25| {
   26|     /// <summary>
   27|     /// Declarations of <c>Lib.Item</c> (generic or not) as they might appear in a referenced library.
   28|     /// </summary>
   29|     public static readonly TheoryData<string, string> LibraryItemDeclarations = new()
   30|     {
   31|         // The cases from the issue that used to crash: generic value types.
   32|         { "record struct generic", "[MessagePackObject] public partial record struct Item<T>([property: Key(0)] string Key);" },
   33|         { "struct generic", "[MessagePackObject] public partial struct Item<T> { [Key(0)] public string Key { get; set; } }" },
   34|         { "readonly record struct generic", "[MessagePackObject] public readonly partial record struct Item<T>([property: Key(0)] string Key);" },
   35|         { "struct generic init", "[MessagePackObject] public partial struct Item<T> { [Key(0)] public string Key { get; init; } }" },
   36|         { "struct generic T member", "[MessagePackObject] public partial struct Item<T> { [Key(0)] public string Key { get; set; } [Key(1)] public T Value { get; set; } }" },
   37|         { "struct generic explicit private field", "[MessagePackObject] public partial struct Item<T> { private int hidden; [Key(0)] public string Key { get => hidden.ToString(); set => hidden = value.Length; } }" },
   38|         { "struct generic field", "[MessagePackObject] public struct Item<T> { [Key(0)] public string Key; }" },
   39|         { "struct generic map mode", "[MessagePackObject(true)] public partial struct Item<T> { public string Key { get; set; } }" },
   40|         { "record struct generic map mode", "[MessagePackObject(true)] public partial record struct Item<T>(string Key);" },
   41|         { "struct generic string key", "[MessagePackObject] public partial struct Item<T> { [Key(\"key\")] public string Key { get; set; } }" },
   42| 
   43|         // The cases from the issue that already worked.
   44|         { "struct", "[MessagePackObject] public partial struct Item { [Key(0)] public string Key { get; set; } }" },
   45|         { "record struct", "[MessagePackObject] public partial record struct Item([property: Key(0)] string Key);" },
   46|         { "class generic", "[MessagePackObject] public partial class Item<T> { [Key(0)] public string Key { get; set; } }" },
   47|         { "record class generic", "[MessagePackObject] public partial record class Item<T>([property: Key(0)] string Key);" },
   48|     };
   49| 
   50|     [Theory]
   51|     [MemberData(nameof(LibraryItemDeclarations))]
   52|     public async Task GeneratorProducesResolver(string caseName, string libraryDeclaration)
   53|     {
   54|         logger.WriteLine(caseName);
   55|         CSharpCompilation app = await CreateAppCompilationAsync(libraryDeclaration);
   56| 
   57|         GeneratorDriver driver = CSharpGeneratorDriver.Create(
   58|             generators: [new MessagePackGenerator().AsSourceGenerator()],
   59|             parseOptions: ParseOptions);
   60|         driver = driver.RunGeneratorsAndUpdateCompilation(app, out Compilation output, out ImmutableArray<Diagnostic> generatorDiagnostics);
   61|         GeneratorDriverRunResult runResult = driver.GetRunResult();
   62| 
   63|         foreach (SyntaxTree tree in runResult.GeneratedTrees)
   64|         {
   65|             logger.WriteLine($"--- {tree.FilePath}");
   66|             logger.WriteLine(tree.ToString());
   67|         }
   68| 
   69|         // A generator exception surfaces as CS8785 and suppresses all generated output.
   70|         Assert.All(runResult.Results, r => Assert.Null(r.Exception));
   71|         Assert.Empty(generatorDiagnostics);
   72| 
   73|         // The compiling assembly must end up with its generated resolver.
   74|         Assert.NotNull(output.GetTypeByMetadataName("MessagePack.GeneratedMessagePackResolver"));
   75| 
   76|         // ...and the generated code must compile.
   77|         Diagnostic[] errors = output.GetDiagnostics().Where(d => d.Severity == DiagnosticSeverity.Error).ToArray();
   78|         Assert.True(errors.Length == 0, string.Join(Environment.NewLine, errors.Select(e => e.ToString())));
   79|     }
   80| 
   81|     [Theory]
   82|     [MemberData(nameof(LibraryItemDeclarations))]
   83|     public async Task AnalyzerDoesNotThrow(string caseName, string libraryDeclaration)
   84|     {
   85|         logger.WriteLine(caseName);
   86|         CSharpCompilation app = await CreateAppCompilationAsync(libraryDeclaration);
   87| 
   88|         ImmutableArray<DiagnosticAnalyzer> analyzers = typeof(MsgPack00xMessagePackAnalyzer).Assembly.GetTypes()
   89|             .Where(t => typeof(DiagnosticAnalyzer).IsAssignableFrom(t) && !t.IsAbstract)
   90|             .Select(t => (DiagnosticAnalyzer)Activator.CreateInstance(t)!)
   91|             .ToImmutableArray();
   92| 
   93|         // Analyzer exceptions are reported as AD0001 diagnostics.
   94|         ImmutableArray<Diagnostic> diagnostics = await app.WithAnalyzers(analyzers).GetAnalyzerDiagnosticsAsync();
   95|         foreach (Diagnostic diagnostic in diagnostics)
   96|         {
   97|             logger.WriteLine(diagnostic.ToString());
   98|         }
   99| 
  100|         Assert.Empty(diagnostics);
  101|     }
  102| 
  103|     /// <summary>
  104|     /// The analyzer must still report a genuine problem in the referencing project
  105|     /// (rather than crashing, or reporting nothing because it crashed).
  106|     /// </summary>
  107|     [Fact]
  108|     public async Task AnalyzerStillReportsProblemsInReferencingProject()
  109|     {
  110|         CSharpCompilation app = await CreateAppCompilationAsync(
  111|             "[MessagePackObject] public partial record struct Item<T>([property: Key(0)] string Key);",
  112|             appMembers: "[Key(1)] public Item<int> Member { get; init; } public int Unattributed { get; set; }");
  113| 
  114|         ImmutableArray<DiagnosticAnalyzer> analyzers = ImmutableArray.Create<DiagnosticAnalyzer>(new MsgPack00xMessagePackAnalyzer());
  115|         ImmutableArray<Diagnostic> diagnostics = await app.WithAnalyzers(analyzers).GetAnalyzerDiagnosticsAsync();
  116|         foreach (Diagnostic diagnostic in diagnostics)
  117|         {
  118|             logger.WriteLine(diagnostic.ToString());
  119|         }
  120| 
  121|         Diagnostic single = Assert.Single(diagnostics);
  122|         Assert.Equal(MsgPack00xMessagePackAnalyzer.MemberNeedsKey.Id, single.Id);
  123|         Assert.True(single.Location.IsInSource);
  124|     }
  125| 
  126|     /// <summary>
  127|     /// Diagnostics about members of a referenced type have no syntax to point at, and must not crash the analyzer.
  128|     /// </summary>
  129|     [Theory]
  130|     [InlineData("[MessagePackObject] public partial struct Item<T> { [Key((string)null)] public string Key { get; set; } }")]
  131|     [InlineData("[MessagePackObject] public partial record struct Item<T>([property: Key((string)null)] string Key);")]
  132|     [InlineData("[MessagePackObject] public partial struct Item<T> { [Key(0)] public string Key { get; set; } public int Unattributed { get; set; } }")]
  133|     [InlineData("[MessagePackObject] public struct Item<T> { [Key(0)] public string Key; public int Unattributed; }")]
  134|     [InlineData("[MessagePackObject] public partial struct Item<T> { [Key(0)] private string key; public int Unattributed; private int unattributedPrivate; }")]
  135|     public async Task AnalyzerDoesNotThrowOnInvalidReferencedType(string libraryDeclaration)
  136|     {
  137|         CSharpCompilation app = await CreateAppCompilationAsync(libraryDeclaration);
  138| 
  139|         ImmutableArray<DiagnosticAnalyzer> analyzers = ImmutableArray.Create<DiagnosticAnalyzer>(new MsgPack00xMessagePackAnalyzer());
  140|         ImmutableArray<Diagnostic> diagnostics = await app.WithAnalyzers(analyzers).GetAnalyzerDiagnosticsAsync();
  141|         foreach (Diagnostic diagnostic in diagnostics)
  142|         {
  143|             logger.WriteLine(diagnostic.ToString());
  144|         }
  145| 
  146|         Assert.DoesNotContain(diagnostics, d => d.Id == "AD0001");
  147| 
  148|         GeneratorDriver driver = CSharpGeneratorDriver.Create(
  149|             generators: [new MessagePackGenerator().AsSourceGenerator()],
  150|             parseOptions: ParseOptions);
  151|         GeneratorDriverRunResult runResult = driver.RunGenerators(app).GetRunResult();
  152|         Assert.All(runResult.Results, r => Assert.Null(r.Exception));
  153|     }
  154| 
  155|     /// <summary>
  156|     /// The type arguments of a closed generic from a referenced assembly must still be collected.
  157|     /// </summary>
  158|     [Fact]
  159|     public async Task GeneratorCollectsTypeArgumentOfReferencedGenericValueType()
  160|     {
  161|         CSharpCompilation app = await CreateAppCompilationAsync(
  162|             "[MessagePackObject] public partial record struct Item<T>([property: Key(0)] string Key, [property: Key(1)] T Value);",
  163|             appMembers: "[Key(1)] public Item<Payload> Member { get; init; }",
  164|             appTypes: "[MessagePackObject] public sealed class Payload { [Key(0)] public int X { get; set; } }");
  165| 
  166|         GeneratorDriver driver = CSharpGeneratorDriver.Create(
  167|             generators: [new MessagePackGenerator().AsSourceGenerator()],
  168|             parseOptions: ParseOptions);
  169|         driver = driver.RunGeneratorsAndUpdateCompilation(app, out Compilation output, out ImmutableArray<Diagnostic> generatorDiagnostics);
  170|         GeneratorDriverRunResult runResult = driver.GetRunResult();
  171|         string allGenerated = string.Join(Environment.NewLine, runResult.GeneratedTrees.Select(t => t.ToString()));
  172|         logger.WriteLine(allGenerated);
  173| 
  174|         Assert.All(runResult.Results, r => Assert.Null(r.Exception));
  175|         Assert.Empty(generatorDiagnostics);
  176|         Assert.Contains("PayloadFormatter", allGenerated);
  177|         Assert.Contains("global::Lib.Item<global::App.Payload>", allGenerated);
  178|         Assert.Empty(output.GetDiagnostics().Where(d => d.Severity == DiagnosticSeverity.Error));
  179|     }
  180| 
  181|     private static CSharpParseOptions ParseOptions { get; } = new(LanguageVersion.CSharp12);
  182| 
  183|     private static async Task<CSharpCompilation> CreateAppCompilationAsync(string libraryDeclaration, string? appMembers = null, string? appTypes = null)
  184|     {
  185|         ImmutableArray<MetadataReference> frameworkReferences = await ReferencesHelper.DefaultTargetFrameworkReferences.ResolveAsync(LanguageNames.CSharp, CancellationToken.None);
  186|         MetadataReference[] baseReferences = [.. frameworkReferences, .. ReferencesHelper.GetReferences(ReferencesSet.MessagePack)];
  187| 
  188|         string libSource = $$"""
  189|             using MessagePack;
  190|             namespace Lib;
  191|             {{libraryDeclaration}}
  192|             """;
  193|         CSharpCompilation lib = CSharpCompilation.Create(
  194|             "Lib",
  195|             [CSharpSyntaxTree.ParseText(libSource, ParseOptions)],
  196|             baseReferences,
  197|             new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary, nullableContextOptions: NullableContextOptions.Disable));
  198| 
  199|         using MemoryStream image = new();
  200|         Microsoft.CodeAnalysis.Emit.EmitResult emitResult = lib.Emit(image);
  201|         Assert.True(emitResult.Success, string.Join(Environment.NewLine, emitResult.Diagnostics));
  202| 
  203|         string memberType = libraryDeclaration.Contains("Item<T>") ? "Item<int>" : "Item";
  204|         appMembers ??= $"[Key(1)] public {memberType} Member {{ get; init; }}";
  205|         string appSource = $$"""
  206|             using MessagePack;
  207|             using Lib;
  208|             namespace App;
  209|             [MessagePackObject]
  210|             public sealed partial record Cmd([property: Key(0)] string Scope)
  211|             {
  212|                 {{appMembers}}
  213|             }
  214|             {{appTypes}}
  215|             """;
  216|         return CSharpCompilation.Create(
  217|             "App",
  218|             [CSharpSyntaxTree.ParseText(appSource, ParseOptions)],
  219|             [.. baseReferences, MetadataReference.CreateFromImage(image.ToArray())],
  220|             new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary, nullableContextOptions: NullableContextOptions.Disable));
  221|     }
  222| }
```

### src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base (32258fdb), around the changed lines
```
  ... lines 1-719 not shown ...
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
  ... lines 787-951 not shown ...
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
  ... lines 1111-1395 not shown ...
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
  ... lines 1462-1491 not shown ...
```

## What you did NOT get (refuse anything that depends on it)
- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)

Return only the JSON object described in the brief.