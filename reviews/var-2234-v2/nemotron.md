# Review of var-2234-v2 by nemotron (nvidia/nemotron-3.5-super-vl-120b-a12b, review-v1)

_Run by `countersign review-llm` at 2026-11-14T12:28:31+02:00; raw response in `reviews/var-2234-v2/raw/nemotron.response.json`. Tokens in/out: 46684/22523._

**Summary:** The change keeps the analyzer validating [MessagePackObject(SuppressSourceGeneration = true)] types while skipping only source generation: member types are no longer recursively collected during generation, closed generics whose definition is suppressed are not registered in the resolver, and duplicate/mixed keys no longer crash the analyzer (AD0001 replaced by MsgPack005). All 183 tests pass on head, the new tests fail on base source and pass with the fix, and mutation testing killed 7 of 8 mutants. Overall the change fixes the root cause and is well covered; REQ-2234-F2 lacks a dedicated test in facts.json.

| Req | Verdict | Basis |
|---|---|---|
| REQ-2234-F1 | met | The analyzer validates members of suppressed types (collectMemberTypes only gates recursive type collection, not diagnostics) and reports MsgPack004/MsgPack005/MsgPack003; duplicate and mixed keys no longer crash (AD0001 removed). Contract-diagnostic tests pass on head and fail on base with AD0001. |
| REQ-2234-F2 | cannot_determine | The clause's named test (SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed) is not in facts.json; available tests pass but none isolates that source-generation-only diagnostics such as partial-class requirements are suppressed for SuppressSourceGeneration types, and the tail of GetObjectInfo where those requirements surface was not provided. |
| REQ-2234-N1 | met | The full suite passes on head (183/183, 0 failed) and the invalid-contract tests that crashed on base with AD0001 now pass on head, reporting MsgPack005 instead. |
| REQ-2234-N2 | met | 8 of the 16 new tests fail on base source and pass on head (fail_without_fix check passes), and the full suite on head passes with no regressions (no failures not on base, none also on base). |

## Findings

- **mutation-survivor-857** [info, tests] Mutation survivor on collectMemberTypes guard at TypeCollector.cs:857: The negated-condition mutant of `if (specialFormatter is null && collectMemberTypes)` at line 857 survived mutation testing: no new test fails on it, so this hunk's suppression of recursive member-type collection is not specifically covered by a new test. Three pre-existing EnumFormatter map-mode tests do fail on the mutant, so the guard is behaviorally significant but not newly covered.

## Refusals

- Contents of the 6 generated test fixture files: Generated file contents and diffs were not provided, so I cannot independently verify they match the generator output. (decide: area owner / CI)
- Documentation impact: No README, analyzer docs, or release notes were provided or changed, so I cannot verify documentation describes the new analyzer behavior. (decide: area owner)
- Multi-target build (net472/netstandard): Only the net8.0 slice was built; the net472/netstandard build was not run. (decide: area owner)

## Not given to the model

- the contents and diffs of 6 generated files (listed above by name only)
- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- tests/MessagePack.SourceGenerator.Tests/GenerationTests.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)
