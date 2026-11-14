# Review of 2234-mut1 by nemotron (nvidia/nemotron-3.5-super-vl-120b-a12b, review-v1)

_Run by `countersign review-llm` at 2026-11-14T04:36:56+02:00; raw response in `reviews/2234-mut1/raw/nemotron.response.json`. Tokens in/out: 38231/15689._

**Summary:** The change makes the analyzer validate [MessagePackObject(SuppressSourceGeneration = true)] types and guards duplicate-key handling in TypeCollector.cs, but the property int-key path still calls intMembers.Add unconditionally behind `if (true)`, so the analyzer crashes with AD0001 on duplicate int keys. Two new tests fail and the full suite is red, so the root cause is only partially fixed and the change should not merge as-is.

| Req | Verdict | Basis |
|---|---|---|
| REQ-2234-F1 | met | All three F1 tests pass on head: MemberWithoutKeyIsReported, MemberTypeMustBeMessagePackObjectIsReported, and AllowPrivateRequiredIsReported each report the expected contract diagnostic for a suppressed type. |
| REQ-2234-F2 | met | The F2 test SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed passes on head, confirming generation-only diagnostics (MsgPack011/016/017) are not reported for a suppressed type. |
| REQ-2234-N1 | not_met | The full suite fails on two duplicate-key tests because the analyzer still crashes (AD0001) instead of reporting only the contract diagnostic, including for a suppressed type. |
| REQ-2234-N2 | cannot_determine | The tests.fail_without_fix check required by N2 was not run and is absent from facts.json, so it cannot be established that the new tests fail without the fix; the suite shows no pre-existing regressions (0 failures also on base). |

## Findings

- **N1** [blocker, correctness] Analyzer still crashes (AD0001) on duplicate int keys: The property int-key path in GetObjectInfo still inserts into intMembers unconditionally behind `if (true)`, so a duplicate int key throws ArgumentException and surfaces as an AD0001 analyzer crash in addition to the MsgPack005 diagnostic. The field int-key path and both string-key paths are correctly guarded, showing the fix pattern was known but not applied here.

## Refusals

- Whether the new tests fail without the fix (tests.fail_without_fix): The tests.fail_without_fix check was not run and is not present in facts.json, so fail-without-fix outcomes cannot be verified from the given evidence. (decide: area owner or decision engine)

## Not given to the model

- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- README.md: diff only, full file not provided (doc)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)
