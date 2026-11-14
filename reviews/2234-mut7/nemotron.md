# Review of 2234-mut7 by nemotron (nvidia/nemotron-3.5-super-vl-120b-a12b, review-v1)

_Run by `countersign review-llm` at 2026-11-14T04:50:24+02:00; raw response in `reviews/2234-mut7/raw/nemotron.response.json`. Tokens in/out: 39349/13613._

**Summary:** The change fixes the analyzer crash for [MessagePackObject(SuppressSourceGeneration = true)] types with invalid contracts: after reporting a mixed-key diagnostic it now skips the member, and duplicate-key dictionary inserts are guarded so duplicate keys no longer throw. All 8 new targeted analyzer/execution tests pass and the build passes. However, the same diff changes deserializing constructor parameter matching (`ctorParamIndex = 1`) for all types, breaking six previously-passing tests in the full suite, and the fail-without-fix check was not run, so the fix's test coverage is unverified and the change currently introduces regressions.

| Req | Verdict | Basis |
|---|---|---|
| REQ-2234-F1 | met | The contract-diagnostic tests for suppressed types pass (missing key MsgPack004, member type MsgPack003, allow-private MsgPack015), and the code still reports these diagnostics via reportDiagnostic; the fix keeps the analyzer from crashing while reporting them. |
| REQ-2234-F2 | met | SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed passes, confirming that source-generation-only checks (partial-class, AOT-only) are not raised for a suppressed type. |
| REQ-2234-N1 | met | The three WithoutAnalyzerFailure tests (duplicate int keys, duplicate string keys, mixed key kinds) pass on head, demonstrating the analyzer no longer crashes on invalid contracts for suppressed types; the full-suite failures are unrelated constructor/generation regressions covered in finding N1. |
| REQ-2234-N2 | not_met | tests.fail_without_fix was not run, so 'tests fail without the fix' is unverified, and the full suite shows six new failures (regressions), violating 'no regressions in the existing test suite'. |

## Findings

- **N1** [blocker, correctness] Change breaks six previously-passing tests (regression): The full suite reports six tests that pass on base but fail on head (GenerationTests.DeserializingConstructorParameterMemberTypeAssignability_Incompatible, GenerationTests.DeserializingConstructorParameterMemberTypeAssignability_MemberAssignsToParamType, GenerationTests.NoPrivateAccessNeeded, GenerationTests.NonDefaultDeserializingConstructor_Private, MsgPack00xAnalyzerTests.AddAttributeToTypeForRecordPrimaryConstructor, MsgPack00xAnalyzerTests.AddAttributesToMembersOfRecordWithPrimaryCtor). This violates REQ-2234-N2's 'no regressions' and blocks merging. The likely cause is the constructor-parameter index change (`ctorParamIndex = 1` at head line 1241 vs `0` at base line 1227), which alters deserializing-constructor matching for all types, not just SuppressSourceGeneration types.
- **N2** [major, tests] fail_without_fix check was not run; fix coverage unverified: REQ-2234-N2 requires automated tests that fail without the fix, but tests.fail_without_fix was not executed (listed in not_run). The new targeted tests pass on head, but their fail-without-fix behavior is unconfirmed, so the coverage requirement cannot be verified.

## Refusals

- Precise root cause of the six full-suite failures: Attributing the regressions definitively to the ctorParamIndex change would require running fail-without-fix or targeted regression tests, which were not executed; the change is the only difference between base and head, so the link is strong but not test-confirmed. (decide: Area owner / change author)

## Not given to the model

- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- README.md: diff only, full file not provided (doc)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)
