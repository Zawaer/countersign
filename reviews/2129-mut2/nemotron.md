# Review of 2129-mut2 by nemotron (nvidia/nemotron-3.5-super-vl-120b-a12b, review-v1)

_Run by `countersign review-llm` at 2026-11-14T04:33:55+02:00; raw response in `reviews/2129-mut2/raw/nemotron.response.json`. Tokens in/out: 52060/12477._

**Summary:** The change adds [GeneratedMessagePackFormatter] so the MessagePack source generator writes a formatter for a type declared in another assembly, with contractless mode and an optional surrogate type, plus four new analyzer diagnostics (MsgPack019–MsgPack022), docs, and tests. The build passes, the targeted tests pass, and the full source-generator suite passes (173/173); the contractless external-type tests and the resolver-registration test pass. However, the execution suite has one confirmed failure: GeneratedFormatterForExternalTypesTests.SurrogateControlsKeysAndMembership fails because GeneratedFormatterCollector.cs inverts the surrogate key-kind test (`key is string` instead of `key is int`), so integer-keyed surrogates are treated as string-keyed and emitted as maps rather than sparse arrays. The feature works for contractless mode but surrogate mode is broken, so the change should not merge as-is.

| Req | Verdict | Basis |
|---|---|---|
| REQ-2129-F1 | not_met | Contractless formatters for external types round-trip and are registered (tests pass; full suite passes), but surrogate mode with integer keys is broken: GeneratedFormatterForExternalTypesTests.SurrogateControlsKeysAndMembership failed in the execution suite, and GeneratedFormatterCollector.cs line 181 inverts the key-kind test (`key is string` rather than `key is int`), so isIntKey is the opposite of the actual key kind. |

## Findings

- **N1** [blocker, correctness] Surrogate integer keys are treated as string keys, breaking surrogate mode: In GeneratedFormatterCollector.CreateSurrogateMembers, `bool memberIsIntKey = key is string;` is inverted: integer keys are classified as string keys and vice versa, so the emitted isIntKey flag is the opposite of the actual key kind. An integer-keyed surrogate is therefore serialized as a string-key map instead of a sparse array with MaxKey+1 slots. This is confirmed by the failing test GeneratedFormatterForExternalTypesTests.SurrogateControlsKeysAndMembership (execution suite: 40 passed, 1 failed). String-keyed surrogates would be broken the other way (array instead of map) but are not covered by a test.

## Refusals

- Contents of the two generated .cs files (FormatterTemplate.cs, StringKeyFormatterTemplate.cs): Their contents and diffs were not provided, so I cannot verify the emitted source for user-declared formatters; only the .tt templates were reviewed. (decide: area owner)
- Unrun checks: tests.fail_without_fix, public_api, analyzers: These checks were not run for this revision, so I cannot verify that the new tests fail without the fix or assess public-API/analyzer impact. (decide: CI or area owner)

## Not given to the model

- the contents and diffs of 2 generated files (listed above by name only)
- src/MessagePack.SourceGenerator/MessagePackGenerator.cs at base: not provided (did not fit the context budget)
- src/MessagePack.SourceGenerator/Utils/Constants.cs at base: not provided (did not fit the context budget)
- src/MessagePack.Annotations/Attributes.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Analyzers/MsgPack00xMessagePackAnalyzer.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/CodeAnalysis/ObjectSerializationInfo.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/GeneratorUtilities.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/MessagePackGenerator.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Transforms/FormatterTemplate.tt at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Transforms/StringKey/StringKeyFormatterTemplate.tt at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.Annotations/Attributes.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Analyzers/MsgPack00xMessagePackAnalyzer.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/CodeAnalysis/ObjectSerializationInfo.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Transforms/FormatterTemplate.tt at base: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/Transforms/StringKey/StringKeyFormatterTemplate.tt at base: only ±30 lines around the changes (the full file did not fit the budget)
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
