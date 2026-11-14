# Review of 2234-mut5 by nemotron (nvidia/nemotron-3.5-super-vl-120b-a12b, review-v1)

_Run by `countersign review-llm` at 2026-11-14T04:44:02+02:00; raw response in `reviews/2234-mut5/raw/nemotron.response.json`. Tokens in/out: 39152/27608._

**Summary:** The change stops the analyzer from crashing on [MessagePackObject(SuppressSourceGeneration = true)] types with duplicate or mixed keys: the contract diagnostics are reported and the offending member is skipped instead of throwing. All eight targeted analyzer tests pass. However, the field-handling guard is inverted (missing '!'), so int-keyed fields are silently dropped and duplicate int-keyed fields evade MsgPack005, and the full suite regresses with 14 newly failing generation tests. The change should not merge as-is.

| Req | Verdict | Basis |
|---|---|---|
| REQ-2234-F1 | met | The three F1 tests pass on head (missing key/MsgPack004, member type/MsgPack003, allow-private/MsgPack015), and the code reports these diagnostics for suppressed types before the suppress-source-generation early return, confirming no regression in contract-diagnostic reporting; they exercise non-crash paths, while the crash fix is evidenced under N1. |
| REQ-2234-F2 | met | The SourceGenerationOnlyDiagnosticsAreNotReportedWhenSuppressed test passes on head expecting zero diagnostics, and the code suppresses AOT-only checks (line 989) and returns before the partial-class check (line 1383) for suppressed types. |
| REQ-2234-N1 | met | The duplicate-int-key, duplicate-string-key, and mixed-key-kind tests for suppressed types pass on head with no analyzer crash, and the code now skips the offending member (continue) and guards the dictionary Adds, removing the crash paths; the separate field-omission defect (C1) is a silent omission, not a crash, and is reported separately. |
| REQ-2234-N2 | not_met | tests.full_suite failed with 14 failures that all pass on base (regressions), violating the “no regressions in the existing test suite” clause, and tests.fail_without_fix was not run so the “fail without fix” clause is unconfirmed. |

## Findings

- **C1** [major, correctness] Int-keyed fields silently dropped; duplicate int-keyed fields not reported: In the field-handling branch, the guard is missing '!': line 1163 adds an int-keyed field only when its key is already present, but the first occurrence is never added (line 1163 is false), so ContainsKey never becomes true. As a result every int-keyed field is silently omitted from the serialization model and duplicate int-keyed fields never reach line 1154’s KeysMustBeUnique diagnostic (no MsgPack005, no crash, silent data omission). The equivalent property branch correctly uses 'if (!intMembers.ContainsKey(...))' at line 1023; the base code added unconditionally at line 1155, so head regresses field handling versus base as well.
- **R1** [blocker, tests] Full test suite regresses: 14 generation tests newly fail on head: tests.full_suite reports 14 failed, 14 of which are “not failing on base” and 0 also failing on base. All are source-generator snapshot tests failing with “Expected source file list to match” and an unexpected extra generated file (MessagePack.GeneratedMessagePackResolver.g.cs). This violates REQ-2234-N2’s “no regressions in the existing test suite” clause; the root cause (why head changes generation output for previously passing types) is not established by the evidence given.

## Refusals

- Whether the new tests fail without the fix: tests.fail_without_fix was not run for this revision (listed in not_run), so the “fail without it” clause of REQ-2234-N2 cannot be confirmed from evidence; the code strongly suggests the duplicate/mixed-key tests would crash on base, but that is not a substitute for the check. (decide: area owner or release engineer to run the source-reverted test pass)

## Not given to the model

- src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs at base: only ±30 lines around the changes (the full file did not fit the budget)
- README.md: diff only, full file not provided (doc)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)
