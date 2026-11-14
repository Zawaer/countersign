# Repro: claude / 2283 / C1 (regression: MsgPack003 dropped)

**Claim** (reviews/2283/claude.json, finding C1, and the basis of claude's REQ-2283-N1 `not_met`): the change's new
`ReportIfLocatedInCompilation` filter drops every diagnostic whose location is not in this compilation's source. With a
generic class from a referenced assembly closed over an app type that lacks `[MessagePackObject]` (`Lib.Item<App.Foo>`),
MsgPack003 about `App.Foo` is located on the metadata member `Item.Content`, so the change drops it. Base reports it.

**Test**: `ReproClaude2283C1Tests.cs`, in the style of `tests/MessagePack.SourceGenerator.Tests` (xunit, `ReferencesHelper`,
.NET 8 reference assemblies). It compiles `Lib` to an in-memory assembly, references it from `App`, runs
`MsgPack00xMessagePackAnalyzer` and asserts (1) the analyzer did not crash and (2) MsgPack003 is reported. The test states
the behaviour REQ-2283-N1 asks for, so the claim predicts it **fails on head and passes on base** (`repro.json`).

**Run by the pipeline**: `python3 -I evidence/scripts/repro.py 2283/C1` copies the file into
`tests/MessagePack.SourceGenerator.Tests/CountersignRepro/` in scratch worktrees `/data/src/mp-repro-2283-C1-{head,base}`,
builds with SDK 8.0.402 and runs it (`run.sh`, filter `FullyQualifiedName~ReproClaude2283C1Tests`). `facts.py` records
the check `repro.claude.C1` in `evidence/2283/facts.json` (logs: `evidence/2283/logs/repro.claude.C1.*`).

| run | revision | claim | outcome |
|---|---|---|---|
| head | 9df83c38 (ju26-issue-2283) | failed | **failed**: "expected MsgPack003 ...; analyzer reported: (no diagnostics)" |
| base | 32258fdb | passed | **passed** (MsgPack003 reported) |

Status `pass`: reproduced by the pipeline. The regression is real and no test in the change covers it.
