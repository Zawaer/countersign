# Review of 2283-mut1 by nemotron (nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16, review-v1)

_Run by `countersign review-llm` at 2026-11-14T13:04:07+02:00; raw response in `reviews-selfhost/2283-mut1/raw/nemotron.response.json`. Tokens in/out: 48218/6155. Endpoint host 127.0.0.1 (self-hosted, A100 80GB x1)._

**Summary:** The change fixes issue #2283 by modifying TypeCollector.cs to handle closed generic value types from referenced assemblies. Three new tests verify the fix: they pass with the head change and fail on base, confirming the root cause is addressed. The full test suite shows no regressions.

| Req | Verdict | Basis |
|---|---|---|
| REQ-2283-F1 | met | Three new tests for closed generic types from metadata references pass with head and fail on base, confirming the source generator no longer crashes (no CS8785) and produces a generated resolver. |
| REQ-2283-F2 | met | The three new tests specifically verify no AD0001 analyzer exceptions occur for closed generic types from referenced assemblies; all pass with head and fail on base. |
| REQ-2283-F3 | met | The ReportIfLocatedInCompilation method ensures diagnostics are only reported for in-source locations, preventing reporting against metadata-referenced types. The new tests confirm no AD0001 errors for such types. |
| REQ-2283-N1 | met | The full suite of 170 tests passes with 0 failures, and targeted generator tests all pass (19/19), confirming no regressions in existing diagnostics. |
| REQ-2283-N2 | met | The tests.fail_without_fix check confirms 3/3 new tests fail on base source, demonstrating the fix is covered by automated tests that fail without it. |

## Findings

- none

## Refusals

- none

## Not given to the model

- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- README.md: diff only, full file not provided (doc)
- doc/analyzers/MsgPack004.md: diff only, full file not provided (doc)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)
