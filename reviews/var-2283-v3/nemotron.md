# Review of var-2283-v3 by nemotron (nvidia/nemotron-3.5-super-vl-120b-a12b, review-v1)

_Run by `countersign review-llm` at 2026-11-14T12:21:47+02:00; raw response in `reviews/var-2283-v3/raw/nemotron.response.json`. Tokens in/out: 36853/18021._

**Summary:** The change fixes the #2283 crash in TypeCollector.cs by skipping auto-property backing fields that cannot be referenced by name and by replacing direct DeclaringSyntaxReferences[0] indexing with safe FirstOrDefault-based location access (lines 985 and 1080). All functional requirements are met: the new metadata-reference tests pass on head (no CS8785, resolver generated, no analyzer exception or AD0001), two of three fail on base with the reported IndexOutOfRangeException, and the full suite shows no regressions. The sole weakness is that mutation testing found all four mutants of the changed lines survive, because the new tests assert only the absence of crashes and do not validate diagnostic behavior.

| Req | Verdict | Basis |
|---|---|---|
| REQ-2283-F1 | met | The metadata-reference tests pass on head with no CS8785, a generated resolver, and no errors, while two of three failed on base with IndexOutOfRangeException at TypeCollector.GetObjectInfo; head code at line 1050 skips non-referenceable fields and line 1080 uses safe location access. |
| REQ-2283-F2 | met | The same tests pass on head with Assert.Empty(analyzerExceptions) and no AD0001 diagnostic, so the analyzer does not throw for the metadata-referenced generic value type input. |
| REQ-2283-F3 | met | Head code skips fields that cannot be referenced by name (line 1050) and resolves diagnostic locations via FirstOrDefault with a null fallback instead of indexing DeclaringSyntaxReferences[0] (lines 985 and 1080), so members of metadata types cannot produce a crash or an external-source location; the metadata-reference tests pass without crashing. |
| REQ-2283-N1 | met | The full suite check passed: 170 tests passed, 0 failed, with no failures not on base and no failures also on base, so existing diagnostics for in-compilation types are unchanged. |
| REQ-2283-N2 | met | The fail_without_fix check passed: 2 of the 3 new tests fail on base source with IndexOutOfRangeException, so the fix is covered by automated tests that fail without it. |

## Findings

- **M1** [major, tests] Mutation tests survive; new tests do not discriminate the fix's guard logic: All four mutants of the changed source lines survived (tests.mutation failed: 0 killed, 4 survived; hunks TypeCollector.cs:985 and :1050). The new tests assert only the absence of crashes/analyzer exceptions (CS8785, AD0001) and resolver generation, not the presence, absence, or location of member diagnostics. As a result, mutants that remove the BothStringAndIntKeyAreNull diagnostic call (line 985) or weaken or drop the CanBeReferencedByName field guard (line 1050) still pass, so a regression in this logic would not be caught by the new tests.

## Refusals

- none

## Not given to the model

- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)
