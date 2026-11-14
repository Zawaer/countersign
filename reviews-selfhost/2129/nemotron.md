# Review of 2129 by nemotron (nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16, review-v1)

_Run by `countersign review-llm` at 2026-11-14T12:59:58+02:00; raw response in `reviews-selfhost/2129/raw/nemotron.response.json`. Tokens in/out: 52802/9454. Endpoint host 127.0.0.1 (self-hosted, A100 80GB x1)._

**Summary:** The change implements REQ-2129-F1 by adding the [GeneratedMessagePackFormatter] attribute and source generator support for creating formatters for types in referenced assemblies. New execution tests verify contractless and surrogate-based serialization of ExternalPerson, ExternalPoint, and ExternalWidget types, and all 6 new tests fail without the fix (tests.fail_without_fix), confirming the change is the root cause of the feature.

| Req | Verdict | Basis |
|---|---|---|
| REQ-2129-F1 | met | New [GeneratedMessagePackFormatter] attribute, generator code, and analyzers enable formatter generation for types in referenced assemblies; 6/6 new tests fail on base (tests.fail_without_fix) and all 173 tests pass (tests.full_suite), confirming the feature is fully implemented and functional. |

## Findings

- none

## Refusals

- none

## Not given to the model

- the contents and diffs of 2 generated files (listed above by name only)
- src/MessagePack.SourceGenerator/MessagePackGenerator.cs at head: not provided (did not fit the context budget)
- src/MessagePack.SourceGenerator/Transforms/FormatterTemplate.tt at head: not provided (did not fit the context budget)
- src/MessagePack.SourceGenerator/Transforms/StringKey/StringKeyFormatterTemplate.tt at head: not provided (did not fit the context budget)
- src/MessagePack.SourceGenerator/Utils/Constants.cs at head: not provided (did not fit the context budget)
- tests/MessagePack.SourceGenerator.ExecutionTests/GeneratedFormatterForExternalTypes.cs at head: not provided (did not fit the context budget)
- tests/MessagePack.SourceGenerator.ExecutionTests/GeneratedFormatterForExternalTypesTests.cs at head: not provided (did not fit the context budget)
- tests/MessagePack.SourceGenerator.ExternalTypes/ExternalPoint.cs at head: not provided (did not fit the context budget)
- tests/MessagePack.SourceGenerator.ExternalTypes/ExternalWidget.cs at head: not provided (did not fit the context budget)
- tests/MessagePack.SourceGenerator.Tests/GeneratedMessagePackFormatterTests.cs at head: not provided (did not fit the context budget)
- src/MessagePack.Annotations/Attributes.cs at base: not provided (did not fit the context budget)
- src/MessagePack.SourceGenerator/Analyzers/MsgPack00xMessagePackAnalyzer.cs at base: not provided (did not fit the context budget)
- src/MessagePack.SourceGenerator/CodeAnalysis/ObjectSerializationInfo.cs at base: not provided (did not fit the context budget)
- src/MessagePack.SourceGenerator/GeneratorUtilities.cs at base: not provided (did not fit the context budget)
- src/MessagePack.SourceGenerator/MessagePackGenerator.cs at base: not provided (did not fit the context budget)
- src/MessagePack.SourceGenerator/Transforms/FormatterTemplate.tt at base: not provided (did not fit the context budget)
- src/MessagePack.SourceGenerator/Transforms/StringKey/StringKeyFormatterTemplate.tt at base: not provided (did not fit the context budget)
- src/MessagePack.SourceGenerator/Utils/Constants.cs at base: not provided (did not fit the context budget)
- src/MessagePack.Annotations/Attributes.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Analyzers/MsgPack00xMessagePackAnalyzer.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/CodeAnalysis/ObjectSerializationInfo.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
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
