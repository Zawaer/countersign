# Review of 2234 by nemotron (nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16, review-v1)

_Run by `countersign review-llm` at 2026-11-14T12:56:00+02:00; raw response in `reviews-selfhost/2234/raw/nemotron.response.json`. Tokens in/out: 50831/24209. Endpoint host 127.0.0.1 (self-hosted, A100 80GB x1)._

**Summary:** Change 2234 modifies TypeCollector.cs to add duplicate key checks and skip members with mismatched key kinds when processing [MessagePackObject(SuppressSourceGeneration = true)] types. The 8 new analyzer tests all pass on head, with 4 failing without the fix (demonstrating the change is necessary) and the full suite passing with no regressions. However, an external reproduction test (C2) shows a crash still exists on head for positional records with Key(null), indicating the fix is incomplete for all crash scenarios.

| Req | Verdict | Basis |
|---|---|---|
| REQ-2234-F1 | met | The change ensures the analyzer reports contract diagnostics for [MessagePackObject(SuppressSourceGeneration = true)] types, as evidenced by 4 new tests passing on head but failing without the fix, and 3 supporting tests all passing on head. |
| REQ-2234-F2 | met | The change correctly skips source-generation-only diagnostics for types with SuppressSourceGeneration = true, as demonstrated by the SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed test passing on head. |
| REQ-2234-N1 | cannot_determine | While the change prevents crashes in duplicate/mixed key scenarios for SuppressSourceGeneration types (4 tests fail without fix), a crash still exists for positional records with Key(null) as demonstrated by external reproduction, so cannot deterministically establish that the analyzer will not crash on all invalid contracts. |
| REQ-2234-N2 | met | The fix is covered by 4 new tests that fail without the fix (demonstrating the change is necessary), and the full test suite passes with no regressions (175 tests, all pass). |

## Findings

- none

## Refusals

- none

## Not given to the model

- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- README.md: diff only, full file not provided (doc)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)
