# Review of 2129-mut1 by nemotron (nvidia/nemotron-3.5-super-vl-120b-a12b, review-v1)

_Run by `countersign review-llm` at 2026-11-14T04:32:21+02:00; raw response in `reviews/2129-mut1/raw/nemotron.response.json`. Tokens in/out: 51847/12723._

**Summary:** The change implements issue #2129: a new [GeneratedMessagePackFormatter] attribute lets the source generator write a formatter body into a user-declared partial class for a type in another assembly, with optional surrogate-based key/membership control, four new analyzer diagnostics (MsgPack019-MsgPack022), generator wiring, template and doc updates, and new tests. The solution builds, but the full suite fails: GeneratedMessagePackFormatterTests.FormatterMustImplementFormatterOfT fails because a formatter class with no IMessagePackFormatter<T> makes the generator crash with CS8785 instead of reporting MsgPack020. In GeneratedFormatterCollector.Collect the check `if (formatterInterfaces.Length > 1)` lets the zero-interface case fall through to `formatterInterfaces[0]`, which throws. The end-to-end execution tests for external types were not run, so the feature itself cannot be confirmed from the given evidence.

| Req | Verdict | Basis |
|---|---|---|
| REQ-2129-F1 | cannot_determine | The feature code is present and the build passes, but the MsgPack020 diagnostic path crashes the generator (test failure) and the external-type execution tests were not run, so the requirement cannot be confirmed met. |

## Findings

- **N1** [blocker, correctness] Formatter without IMessagePackFormatter<T> crashes the generator instead of reporting MsgPack020: GeneratedFormatterCollector.Collect only reports MsgPack020 when more than one IMessagePackFormatter<T> interface is implemented (`if (formatterInterfaces.Length > 1)`). With zero interfaces it falls through to `formatterInterfaces[0].TypeArguments[0]`, which throws on the empty array and fails the generator (observed as warning CS8785: Generator 'MessagePackGenerator' failed to generate source), so the documented diagnostic is never produced. This is exactly the failure in GeneratedMessagePackFormatterTests.FormatterMustImplementFormatterOfT, which failed in both the targeted run and the full suite.

## Refusals

- End-to-end behavior of generated formatters for external types (round-trip serialization, surrogate keys, resolver registration): The tests/MessagePack.SourceGenerator.ExecutionTests project and its new tests (GeneratedFormatterForExternalTypesTests) are not among the facts.json checks, so no pass/fail evidence exists for the core feature; tests.fail_without_fix was also not run. (decide: area owner / maintainer (run the execution tests before merge))
- Contents of the two generated template outputs (FormatterTemplate.cs, StringKeyFormatterTemplate.cs): Only the .tt templates were provided; the generated .cs files' contents and diffs were not given, so the exact generated code text could not be verified. (decide: area owner)
- Public API surface and analyzer rule checks: The public_api and analyzers checks were not run for this revision. (decide: area owner)

## Not given to the model

- the contents and diffs of 2 generated files (listed above by name only)
- src/MessagePack.SourceGenerator/Transforms/StringKey/StringKeyFormatterTemplate.tt at base: not provided (did not fit the context budget)
- src/MessagePack.SourceGenerator/Utils/Constants.cs at base: not provided (did not fit the context budget)
- src/MessagePack.Annotations/Attributes.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Analyzers/MsgPack00xMessagePackAnalyzer.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/CodeAnalysis/ObjectSerializationInfo.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Transforms/FormatterTemplate.tt at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Transforms/StringKey/StringKeyFormatterTemplate.tt at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.Annotations/Attributes.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Analyzers/MsgPack00xMessagePackAnalyzer.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/CodeAnalysis/ObjectSerializationInfo.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Transforms/FormatterTemplate.tt at base: only ±30 lines around the changes (the full file did not fit the budget)
- README.md: diff only, full file not provided (doc)
- doc/analyzers/MsgPack019.md: diff only, full file not provided (doc)
- doc/analyzers/MsgPack020.md: diff only, full file not provided (doc)
- doc/analyzers/MsgPack021.md: diff only, full file not provided (doc)
- doc/analyzers/MsgPack022.md: diff only, full file not provided (doc)
- doc/analyzers/index.md: diff only, full file not provided (doc)
- src/MessagePack.SourceGenerator/AnalyzerReleases.Unshipped.md: diff only, full file not provided (build)
- tests/MessagePack.SourceGenerator.ExecutionTests/MessagePack.SourceGenerator.ExecutionTests.csproj: diff only, full file not provided (build)
- tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj: diff only, full file not provided (build)
- tests/MessagePack.SourceGenerator.MapModeExecutionTests/MessagePack.SourceGenerator.MapModeExecutionTests.csproj: diff only, full file not provided (build)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)
