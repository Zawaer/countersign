# Review of 2234-mut2 by nemotron (nvidia/nemotron-3.5-super-vl-120b-a12b, review-v1)

_Run by `countersign review-llm` at 2026-11-14T04:38:41+02:00; raw response in `reviews/2234-mut2/raw/nemotron.response.json`. Tokens in/out: 39175/18335._

**Summary:** The change keeps the analyzer validating [MessagePackObject(SuppressSourceGeneration = true)] types instead of skipping them: contract diagnostics (missing key, duplicate keys, mixed key kinds, non-public member allowance, member type) are still reported, while generation-only diagnostics (partial class, AOT checks) are suppressed, and duplicate-key dictionary crashes are guarded. The root cause is addressed for the tested scenarios; the targeted tests and full suite pass with no regressions. One gap remains: the field branch lacks the continue after the mixed-key diagnostic, so mixed key kinds on fields can still throw inside the analyzer.

| Req | Verdict | Basis |
|---|---|---|
| REQ-2234-F1 | met | All F1 tests pass on head: missing [Key] (MsgPack004), member type (MsgPack003), AllowPrivate (MsgPack015), duplicate int/string keys and mixed key kinds (MsgPack005) on suppressed types; the head code reports each diagnostic before the suppress-source-generation early return. |
| REQ-2234-F2 | met | SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed passes on head, and the code skips the AOT init-property check when suppressed (line 989) and returns before the partial-type check (lines 1383-1387), so generation-only diagnostics are not reported for suppressed types. |
| REQ-2234-N1 | met | The full suite passed 175/175 with no failures not present on base, and the WithoutAnalyzerFailure tests (duplicate keys, mixed keys) pass on head; see finding M1 for an unguarded field edge case. |
| REQ-2234-N2 | cannot_determine | No regressions are evidenced (full suite: failures_not_on_base empty), but the tests.fail_without_fix check required by N2 was not run and does not appear in facts.json, so it cannot be established from the given evidence that the new tests fail without the fix. |

## Findings

- **M1** [major, correctness] Analyzer can still crash on mixed key kinds for fields in suppressed types: In the field branch, the DoNotMixStringAndIntKeys diagnostic is reported but execution continues into intKey!.Value (line 1154) and stringMembers.ContainsKey(stringKey!) (line 1170), which throw when the key is null; a suppressed type whose first field uses an int key and a later field uses a string key (or vice versa) still crashes the analyzer. The property branch has the matching continue (line 1008); the field branch does not, and no test covers mixed key kinds on fields.

## Refusals

- Public API compatibility / breaking-change judgment: The public_api check was not run for this revision (facts.not_run) and no public API surface evidence was provided. (decide: area owner or release maintainer)
- Static-analyzer and style compliance of the new code: The analyzers check was not run for this revision (facts.not_run). (decide: area owner)
- Performance and runtime behavior on other platforms, target frameworks, or .NET SDKs (including AOT): Execution tests ran only on linux-x64 containers with SDKs 8.0.402 and 9.0.321; no cross-platform or performance evidence was provided. (decide: area owner)

## Not given to the model

- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- README.md: diff only, full file not provided (doc)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)
