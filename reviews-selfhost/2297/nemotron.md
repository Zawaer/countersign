# Review of 2297 by nemotron (nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16, review-v1)

_Run by `countersign review-llm` at 2026-11-14T13:01:01+02:00; raw response in `reviews-selfhost/2297/raw/nemotron.response.json`. Tokens in/out: 53154/4474. Endpoint host 127.0.0.1 (self-hosted, A100 80GB x1)._

**Summary:** The change adds [global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage] attribute to generated MessagePack formatter and resolver code templates, guarded by #if !NETSTANDARD2_0 && !NETFRAMEWORK so it only emits where the attribute is available. The new CodeCoverageExclusionTests pass with the change and fail on base, confirming the fix addresses the requirement. The full 169-test suite also passes.

| Req | Verdict | Basis |
|---|---|---|
| REQ-2297-F1 | met | The change adds the ExcludeFromCodeCoverage attribute to all relevant generated code templates with proper framework guards, and the new tests verify the attribute appears in generated output and is absent on base. |

## Findings

- none

## Refusals

- none

## Not given to the model

- the contents and diffs of 228 generated files (listed above by name only)
- src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Transforms/StringKey/StringKeyFormatterTemplate.tt at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Transforms/TransformUtilities.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Transforms/UnionTemplate.tt at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Transforms/FormatterTemplate.tt at base: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt at base: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Transforms/StringKey/StringKeyFormatterTemplate.tt at base: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Transforms/TransformUtilities.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Transforms/UnionTemplate.tt at base: only ±30 lines around the changes (the full file did not fit the budget)
- README.md: diff only, full file not provided (doc)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)
