# Review of 2283 by nemotron (nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16, review-v1)

_Run by `countersign review-llm` at 2026-11-14T13:21:39+02:00; raw response in `reviews-selfhost/2283/raw/nemotron.response.json`. Tokens in/out: 104325/12744. Endpoint host 127.0.0.1 (self-hosted, A100 80GB x1)._

**Summary:** The change implements a ReportIfLocatedInCompilation filter in TypeCollector.cs to prevent crashes (CS8785, AD0001 IndexOutOfRangeException) when the source generator encounters closed generic value types from referenced assemblies. The 3 new tests that previously crashed on base now pass on head, the full suite (170 tests) shows no regressions, and the fix addresses all 5 requirement clauses. Documentation updates in README.md and MsgPack004.md explain the new behavior for closed generic types from referenced assemblies.

| Req | Verdict | Basis |
|---|---|---|
| REQ-2283-F1 | met | The change prevents crashes (CS8785, AD0001 IndexOutOfRangeException) for closed generic value types from referenced assemblies; 3/3 new tests fail on base and pass on head, and the full targeted test run (19 tests including 3 new) passes. |
| REQ-2283-F2 | met | The analyzer no longer throws AD0001 for closed generic types from metadata references; the 3 new tests fail on base with AD0001 exceptions and pass on head. |
| REQ-2283-F3 | met | The change implements ReportIfLocatedInCompilation which only reports diagnostics when their location is in the compilation being analyzed, preventing diagnostics about members from referenced assemblies being reported at inappropriate locations. |
| REQ-2283-N1 | met | The full suite (170 tests) passes with 0 failures, 0 failures_not_on_base, and 0 failures_also_on_base, confirming no regressions in existing analyzer diagnostics. |
| REQ-2283-N2 | met | The 3 new tests (ClosedGenericRecordStruct_FromMetadataReference, ClosedGenericStruct_FromMetadataReference, ClosedGenericStruct_FromMetadataReference_UnkeyedMember) all fail on base and pass on head, directly covering the fix. |

## Findings

- **F1** [info, correctness] Diagnostic suppression trade-off: The change suppresses some legitimate diagnostics (e.g., MsgPack003 for App.Foo lacking [MessagePackObject] when used as type argument in Lib.Item<App.Foo>) for types from referenced assemblies, as confirmed by repro.claude.C1 where head reports nothing while base reports it. This aligns with REQ-2283-F3's intent but represents a behavior change.
- **F2** [info, maintainability] Mutation testing survival: 6 of 8 mutants of the changed source lines survive mutation testing, indicating some modified code paths are not fully exercised by the new tests. Mutants M4 and M5 in H5 (lines 1446) are killed by the unkeyed member test GenericsFormatterTests.ClosedGenericStruct_FromMetadataReference_UnkeyedMember.

## Refusals

- none

## Not given to the model

- tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- README.md: diff only, full file not provided (doc)
- doc/analyzers/MsgPack004.md: diff only, full file not provided (doc)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)
