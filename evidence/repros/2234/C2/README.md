# Repro: claude / 2234 / C2 (incomplete fix: analyzer still crashes)

**Claim** (reviews/2234/claude.json, finding C2, and the basis of claude's REQ-2234-N1 `not_met`): with
`SuppressSourceGeneration = true`, a positional record with `[property: Key(null)]` still crashes the analyzer (AD0001,
`InvalidCastException`): the BothStringAndIntKeyAreNull path hard-casts the property's syntax to
`PropertyDeclarationSyntax`, but for a positional record it is a `ParameterSyntax`. The change does not touch that line, so
REQ-2234-N1 ("must not crash on invalid contracts ... in such types") is not fully met.

**Test**: `ReproClaude2234C2Tests.cs` (xunit, same helpers as the repo's analyzer tests). It runs
`MsgPack00xMessagePackAnalyzer` over `[MessagePackObject(SuppressSourceGeneration = true)] public record Cmd([property: Key(null)] string Scope);`
and asserts the analyzer did not throw (no exception reported to `CompilationWithAnalyzers`, no AD0001).
The claim predicts: **fails on head**, **fails on base** too (the crash predates the change, which leaves it in place), and,
as a control that the test can pass at all, **passes on ju26-issue-2283**, a sibling branch from the same base that replaced
this hard cast with a null-safe lookup.

**Run by the pipeline**: `python3 -I evidence/scripts/repro.py 2234/C2` (scratch worktrees
`/data/src/mp-repro-2234-C2-{head,base,control}`, SDK 8.0.402). `facts.py` records `repro.claude.C2` in
`evidence/2234/facts.json` (logs: `evidence/2234/logs/repro.claude.C2.*`).

| run | revision | claim | outcome |
|---|---|---|---|
| head | 9007cee1 (ju26-issue-2234) | failed | **failed**: "analyzer crashed: InvalidCastException: Unable to cast ... ParameterSyntax ... to ... PropertyDeclarationSyntax" |
| base | 32258fdb | failed | **failed** (same exception) |
| control | 9df83c38 (ju26-issue-2283) | passed | **passed** |

Status `pass`: reproduced by the pipeline. Not a regression: an incomplete fix.
