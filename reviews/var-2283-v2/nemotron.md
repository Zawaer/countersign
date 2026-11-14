# Review of var-2283-v2 by nemotron (nvidia/nemotron-3.5-super-vl-120b-a12b, review-v1)

_Run by `countersign review-llm` at 2026-11-14T12:18:51+02:00; raw response in `reviews/var-2283-v2/raw/nemotron.response.json`. Tokens in/out: 40375/20551._

**Summary:** The change fixes the root cause of issue #2283: TypeCollector now skips compiler-generated fields (metadata auto-property backing fields such as <Key>k__BackingField, whose names are not valid C# identifiers) when enumerating members in both key and map mode, and every diagnostic location that indexed DeclaringSyntaxReferences[0] now tolerates symbols without syntax via FirstOrDefault(), with a new GetIdentifierLocation that also handles record primary-constructor ParameterSyntax. On head all new generator and analyzer tests pass (full suite 203/203, no regressions versus base), while on base source 17 of the 31 new tests failed with IndexOutOfRangeException/AD0001 or InvalidCastException, so the fix covers REQ-2283-F1 through F3 and N1/N2. Two observations only: mutation coverage is thin for the new guards, and diagnostics for members of metadata-declared types may carry no location.

| Req | Verdict | Basis |
|---|---|---|
| REQ-2283-F1 | met | GeneratorProducesResolver passes for all referenced-library cases on head (including "struct generic") and GeneratorCollectsTypeArgumentOfReferencedGenericValueType passes with PayloadFormatter and global::Lib.Item<global::App.Payload> in the generated output; the same new tests failed on base source with IndexOutOfRangeException (the CS8785 path), and the fix filters metadata backing fields out of member enumeration (lines 753/1050) and stops indexing DeclaringSyntaxReferences[0] (line 1077). |
| REQ-2283-F2 | met | AnalyzerDoesNotThrow passes for all library cases on head and failed on base with AD0001/IndexOutOfRangeException; NullStringKey_RecordPrimaryConstructorParameter passes on head and failed on base with InvalidCastException from the (PropertyDeclarationSyntax) cast; BothStringAndIntKeyAreNull now uses GetIdentifierLocation (line 985) and MemberNeedsKey uses FirstOrDefault() (line 1077), both tolerating metadata symbols without syntax. |
| REQ-2283-F3 | met | AnalyzerStillReportsProblemsInReferencingProject passes on head: exactly one diagnostic, MemberNeedsKey, with Location.IsInSource true; on base it failed because the analyzer threw AD0001 instead of reporting MsgPack004. Diagnostics for metadata-symbol members now resolve to a null location via FirstOrDefault()/GetIdentifierLocation instead of crashing on empty DeclaringSyntaxReferences, so nothing is reported outside the analyzing compilation. |
| REQ-2283-N1 | met | Full suite: 203 passed, 0 failed, with no failures not on base and no failures also on base (base 167/167); build passes, no public API changes, no new analyzer warnings. |
| REQ-2283-N2 | met | fail_without_fix reports 17 of 31 new tests failing on base source (new_failed 17 / new_total 31), including every previously crashing GeneratorProducesResolver and AnalyzerDoesNotThrow case, so the fix is covered by tests that fail without it. |

## Findings

- **F1** [info, tests] Mutation coverage is thin for the new compiler-generated-field guard: Under the harness rule (only new tests count as kills), mutants at TypeCollector.cs:1050 (M2 negating the guard, M4 dropping it to if (true), M5 swapping || to &&) and at TypeCollector.cs:1455 (M3 making IsCompilerGeneratedField always return false) survived with no killing test; existing tests do fail on M2/M4, but no new test isolates the skipping of metadata auto-property backing fields.
- **F2** [info, correctness] Diagnostics for members of metadata-declared types carry no location: When a member of a type from a referenced assembly lacks a key, MemberNeedsKey is created with item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax() resolving to null, so the diagnostic has no location in the user's compilation. This does not violate REQ-2283-F3 (no location outside the compilation), but the user cannot navigate to the member, and the behavior is only implicitly covered: AnalyzerDoesNotThrowOnInvalidReferencedType asserts no AD0001, not the absence of null-location diagnostics.

## Refusals

- Security impact on runtime deserialization of untrusted input: The diff touches only compile-time generator/analyzer diagnostics (TypeCollector.cs) and tests; no runtime serialization or deserialization code is modified, so no runtime security behaviour can be judged from this evidence. (decide: area owner (security review only if a future change touches runtime deserialization))

## Not given to the model

- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- tests/MessagePack.SourceGenerator.Tests/MsgPack00xAnalyzerTests.cs at head: only ±30 lines around the changes (the full file did not fit the budget)
- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)
