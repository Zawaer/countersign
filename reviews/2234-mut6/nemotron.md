# Review of 2234-mut6 by nemotron (nvidia/nemotron-3.5-super-vl-120b-a12b, review-v1)

_Run by `countersign review-llm` at 2026-11-14T04:47:22+02:00; raw response in `reviews/2234-mut6/raw/nemotron.response.json`. Tokens in/out: 42123/27397._

**Summary:** The change adds guards against duplicate-key dictionary inserts in TypeCollector.GetObjectInfo and adds tests for SuppressSourceGeneration = true validation, but it inverts the mixed-key-detection condition at TypeCollector.cs lines 1005 and 1145. On head this crashes the analyzer (AD0001/NullReferenceException) on mixed int/string keys, emits false MsgPack005 diagnostics and drops members 2+ from generated formatters for every multi-key type, producing 34 new full-suite failures. The duplicate-key crash is fixed, but the mixed-key crash from base is not resolved and a broad regression is introduced; build passes and fail-without-fix was not run. Overall: blocker, do not merge until the condition is reverted and tests re-run.

| Req | Verdict | Basis |
|---|---|---|
| REQ-2234-F1 | met | All three F1-listed tests pass on head: missing-[Key] (MsgPack004), non-MessagePackObject member type (MsgPack003), and AllowPrivate required (MsgPack015) are all reported for suppressed types. The mixed-key-kind example named in F1's text is exercised under N1 and crashes there. |
| REQ-2234-F2 | not_met | Its covering test expects zero diagnostics for a suppressed type, but head reports a false MsgPack005 mixed-key diagnostic for Prop1, so the no-extra-diagnostics requirement is not demonstrated (the failure is the same inverted condition bug, not an F2-category diagnostic). |
| REQ-2234-N1 | not_met | MixedKeyKindsAreReportedWithoutAnalyzerFailure crashes with AD0001 instead of reporting MsgPack005, and tests.full_suite fails with 34 new failures, so the analyzer/generator still crashes on invalid contracts in suppressed types. |
| REQ-2234-N2 | not_met | tests.fail_without_fix was not run, so it is unconfirmed that the new tests fail without the fix, and tests.full_suite has 34 regressions not present on base, violating the no-regression clause. |

## Findings

- **F1** [blocker, correctness] Mixed-key detection condition inverted; analyzer crashes on mixed int/string keys: TypeCollector.cs lines 1005 and 1145 use `(isIntKey && stringKey == null) || (!isIntKey && intKey == null)`, the inverse of the base condition. For a mixed type (int key then string key) no diagnostic is emitted and execution falls through to `intKey!.Value`/member.IntKey with a null key, throwing NullReferenceException (reported as analyzer crash AD0001). Base had the same crash at the unguarded `intMembers.Add`, so the change does not resolve the mixed-key crash from issue #2234.
- **F2** [blocker, correctness] Same inverted condition reports false MsgPack005 and drops members 2+ from generated output: For any type with two or more same-kind keys, the second and later members satisfy `stringKey == null` (int keys) or `intKey == null` (string keys), so the condition falsely reports DoNotMixStringAndIntKeys (MsgPack005) and the `continue` skips the `intMembers.Add`/`stringMembers.Add`. Generated formatters omit members after the first, and analyzer tests see spurious MsgPack005 diagnostics.
- **F3** [major, tests] Full-suite regressions; fail-without-fix not run: tests.full_suite fails with 34 newly failing tests (0 also failing on base), including MsgPack00xAnalyzerTests false MsgPack005 diagnostics and GenerationTests/GenericsFormatterTests source-output mismatches, violating N2's no-regression clause. tests.fail_without_fix was not run, so coverage-without-fix is unconfirmed.
- **F4** [minor, tests] Test-file hygiene issues: DuplicateKeysAreReportedWithoutAnalyzerFailureForGeneratedTypes tests a non-suppressed `[MessagePackObject]` type but lives in the suppressed-type analyzer test file, and the REQ-2234-F1 test list duplicates MemberWithoutKeyIsReported while omitting the duplicate/mixed-key tests.

## Refusals

- Root-cause confirmation on base / whether tests fail without the fix: tests.fail_without_fix was not run for this revision, so I cannot confirm the new tests fail without the fix or that the change resolves the original #2234 crash on base. (decide: area owner / decision engine)
- Performance impact of the change: No performance benchmarks or timing data were provided; the change's effect on analyzer/generator speed is unassessed. (decide: performance reviewer or area owner)

## Not given to the model

- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- README.md: diff only, full file not provided (doc)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)
