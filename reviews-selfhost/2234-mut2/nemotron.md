# Review of 2234-mut2 by nemotron (nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16, review-v1)

_Run by `countersign review-llm` at 2026-11-14T13:03:09+02:00; raw response in `reviews-selfhost/2234-mut2/raw/nemotron.response.json`. Tokens in/out: 40337/8920. Endpoint host 127.0.0.1 (self-hosted, A100 80GB x1)._

**Summary:** The change implements support for [MessagePackObject(SuppressSourceGeneration = true)] by modifying TypeCollector.cs to properly report contract diagnostics (missing [Key], duplicate keys, mixed key kinds) for suppressed types while suppressing formatter-generation-only diagnostics (partial-class requirement, AOT-only checks). The fix adds duplicate-key checks before adding members to dictionaries, preventing AD0001 analyzer crashes that occurred on invalid contracts for suppressed types.

| Req | Verdict | Basis |
|---|---|---|
| REQ-2234-F1 | met | The 4 targeted tests that fail without the fix (DuplicateIntKeysAreReportedWithoutAnalyzerFailure, DuplicateStringKeysAreReportedWithoutAnalyzerFailure, MixedKeyKindsAreReportedWithoutAnalyzerFailure, DuplicateKeysAreReportedWithoutAnalyzerFailureForGeneratedTypes) all expect and now receive contract diagnostics for SuppressSourceGeneration=true types; without the fix they crash with AD0001 instead of reporting the expected MsgPack005 diagnostics. The other 4 new tests (MemberWithoutKeyIsReported, AllowPrivateRequiredIsReported, MemberTypeMustBeMessagePackObjectIsReported, SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed) pass both with and without the fix, confirming the analyzer correctly validates contract rules and skips formatter-only diagnostics. |
| REQ-2234-F2 | met | The test SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed passes, and the code at TypeCollector.cs line 1383-1387 explicitly returns null (skipping source generation) when suppressSourceGeneration is true, preventing MsgPack011/016/017 diagnostics from being reported for suppressed types. |
| REQ-2234-N1 | met | The full_suite check passes (175 tests, 0 failed). The fail_without_fix check shows the analyzer crashed with AD0001 on invalid contracts for suppressed types without the fix; with the fix the full suite passes and no crashes occur. |
| REQ-2234-N2 | met | The fail_without_fix check confirms 4 of 8 new tests fail without the fix, demonstrating the tests cover the change. The full_suite check shows 0 regressions (0 failing on base, 0 also failing on base). |

## Findings

- none

## Refusals

- none

## Not given to the model

- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- README.md: diff only, full file not provided (doc)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)
