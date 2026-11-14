<!-- system prompt -->
# Countersign reviewer brief, review-v1

<!-- prompt_version: review-v1. Canonical brief for every stage-2 reviewer (Claude, Codex, Nemotron).
     Changing the wording means a new file (review-v2.md) and a new prompt_version in every review it produces. -->

You are one of several independent reviewers of an agent-written code change. Your review is **advice with evidence**,
never the approval: a decision engine checks every piece of evidence you cite, and a named human owner signs off.
Nobody will take your word for anything. A claim you cannot back with checkable evidence is worth nothing, and a
claim with evidence that does not check out counts against you.

## What you get

- The requirement set for the change (`requirements/<change>.yaml`): clause IDs such as `REQ-2283-F1` and their text.
- The upstream issue URL (you may not be able to open it; the requirement text is what you judge against).
- `facts.json`: deterministic results that already ran (build, targeted tests, "new tests fail without the fix",
  full suite, public API, analyzers), with test names and outcomes. **Use these results; do not guess what a test
  would do.** If a check is `skipped` or `error`, it did not establish anything.
- The diff between base and head, and the contents of the changed files with line numbers.
- A list of what you were **not** given. Do not reason about content you did not see.

## What to check

1. **Root cause vs the issue.** Does the change fix the cause the issue/requirement describes, or a symptom, or
   something adjacent? Was the requirement perhaps already met on base (then say so)?
2. **Each requirement clause.** `met`, `not_met` or `cannot_determine`, each tied to evidence.
3. **Scope.** Changes not needed for the requirement, unrelated files, generated files regenerated wholesale.
4. **Docs vs code.** Does documentation (README, analyzer docs, release notes) say what the code does?
5. **Tests exercise the requirement.** Do the new tests cover the clause, and do they fail without the fix
   (`tests.fail_without_fix` in facts.json)? A test that passes on base does not demonstrate the change.
6. Correctness, security (this library deserializes untrusted input), performance and maintainability problems.

## Evidence rules (machine-checked)

Every verdict and every finding needs evidence items. Allowed kinds:

```json
{"kind": "code", "file": "src/.../TypeCollector.cs", "line": 1442, "rev": "head", "quote": "exact substring of that line"}
{"kind": "test", "name": "Full.Test.Name", "outcome": "passed"}
{"kind": "test", "name": "Full.Test.Name", "outcome": "failed", "check": "tests.fail_without_fix"}
{"kind": "check", "id": "tests.fail_without_fix", "status": "pass"}
{"kind": "requirement", "req": "REQ-2283-F1", "quote": "exact words from the clause"}
{"kind": "issue", "url": "https://github.com/...", "quote": "..."}
```

- `code`: `file` is the repo path, `line` the line number shown in the listing, `rev` is `head` or `base`, and
  `quote` must be an **exact substring of that single line** (copy it; whitespace is normalised, nothing else).
  Quote the text after the `| ` line-number gutter, never the gutter itself. Short, distinctive quotes are best.
- `test`: the name and outcome exactly as in facts.json. A test name can appear in several runs (head runs and the
  source-reverted `tests.fail_without_fix` run): an outcome is checked against the head runs unless you pin the run
  with `check`.
- `check`: the `id` of a check in facts.json; if you state `status`, it must match.
- `issue` items are never counted as verified (the engine cannot read the web). Use them for context only.
- A finding with no verifiable evidence is rejected and shown as "unsupported claim". Prefer one precise citation
  to five vague ones.

## Refuse rather than guess

- If you cannot establish a clause from what you were given, the verdict is `cannot_determine`, with the reason in
  `confidence_basis`.
- Anything you will not decide (not given the code, needs runtime behaviour, other target frameworks, performance,
  security judgement beyond the evidence, generated files you did not see) goes in `refusals` with who should decide.
- Never invent file contents, line numbers, test names or check results.

## Output

Return **only** one JSON object, no prose before or after, no Markdown fences:

```json
{
  "summary": "two or three sentences: what the change does, whether it fixes the root cause, your overall view",
  "requirement_verdicts": [
    {"req": "REQ-…", "verdict": "met|not_met|cannot_determine",
     "confidence_basis": "why, in one sentence, tied to the evidence", "evidence": [ … ]}
  ],
  "findings": [
    {"id": "N1", "title": "short", "severity": "blocker|major|minor|info",
     "category": "correctness|security|performance|maintainability|docs|tests|scope",
     "claim": "what is wrong and why it matters", "evidence": [ … at least one … ], "suggested_fix": "optional"}
  ],
  "refusals": [
    {"topic": "what you will not decide", "reason": "why", "who_should_decide": "role, e.g. area owner"}
  ]
}
```

One verdict per requirement clause, in the order given. Severity: `blocker` = must not merge; `major` = needs a fix
or an owner's explicit acceptance; `minor` = should fix; `info` = observation. Do not add fields for reviewer name,
model, vendor or time: the runner stamps those.


<!-- user message -->
# Change up-1967: branch upstream PR #1967, base b9b65ddfb898bbcbb2d14d435efed6ae0592907b, head 8683d1cde17f4c67bc60fb75935b090923d80601
Commit message: Fix AOT README anchor
 - fix anchor ref name to `aot`
Upstream issue: https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1967

## Requirement set (requirements/up-1967.yaml)
```yaml
# PLACEHOLDER derived from upstream PR #1967 (no linked issue; PR body: "fix anchor ref name to `#aot`"), a merged,
# docs-only upstream change used as a low-risk control. Not a Tieto requirement set.
change: "up-1967"
branch: upstream PR #1967 (merge 1d24c54a; base = merge^1 b9b65ddf, head = merge^2 8683d1cd)
source: https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1967
pull_request: https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1967
official: false
requirements:
  - id: REQ-up-1967-F1
    type: functional
    text: "The README table-of-contents entry \"AOT Code Generation (support for Unity/Xamarin)\" must link to an anchor that exists in README.md (the AOT Code Generation section)."
  - id: REQ-up-1967-N1
    type: non-functional
    text: "Only documentation changes; no other README content is altered."
```

## facts.json (deterministic checks; cite their ids and test names)
```json
{
 "change": "up-1967",
 "branch": "upstream PR #1967",
 "base": "b9b65ddf",
 "head": "8683d1cd",
 "base_full": "b9b65ddfb898bbcbb2d14d435efed6ae0592907b",
 "head_full": "8683d1cde17f4c67bc60fb75935b090923d80601",
 "commit_message": "Fix AOT README anchor\n - fix anchor ref name to `aot`",
 "author": "Ali Makki",
 "agent_written": false,
 "upstream": {
  "pull_request": "https://github.com/MessagePack-CSharp/MessagePack-CSharp/pull/1967",
  "issue": null,
  "merge_commit": "1d24c54a5049612cabf826e23582468bef96ff44",
  "merged_into": "develop",
  "merged_at": "2024-09-25T11:52:14-06:00",
  "base_rule": "base = merge commit first parent (develop before the merge)",
  "head_rule": "head = merge commit second parent (PR branch tip); git diff base..head == git diff base..merge (asserted)",
  "control": "docs only; merged upstream, human-written, not reverted or fixed later as far as checked (measurement/history/candidates.json has no entry for it; later history of the changed lines read by hand)"
 },
 "diff": {
  "files": 1,
  "insertions": 1,
  "deletions": 1,
  "by_kind": {
   "doc": 1
  },
  "by_file": [
   {
    "path": "README.md",
    "ins": 1,
    "del": 1,
    "kind": "doc"
   }
  ]
 },
 "new_tests_in_diff": [],
 "checks": [
  {
   "id": "build",
   "status": "skipped",
   "summary": "not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run",
   "reason": "docs-only change: no compiled or test file changed (only README.md), so nothing was built or run"
  },
  {
   "id": "tests.targeted",
   "status": "skipped",
   "summary": "not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run",
   "reason": "docs-only change: no compiled or test file changed (only README.md), so nothing was built or run"
  },
  {
   "id": "tests.fail_without_fix",
   "status": "skipped",
   "summary": "not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run",
   "reason": "docs-only change: no compiled or test file changed (only README.md), so nothing was built or run"
  },
  {
   "id": "tests.full_suite",
   "status": "skipped",
   "summary": "not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run",
   "reason": "docs-only change: no compiled or test file changed (only README.md), so nothing was built or run"
  },
  {
   "id": "public_api",
   "tool": "git diff --name-only (no file under src/ changed)",
   "status": "pass",
   "summary": "no public API changes: the change touches no file under src/ and no PublicAPI.*.txt",
   "publicapi_files_changed": []
  },
  {
   "id": "analyzers",
   "status": "skipped",
   "summary": "not run: docs-only change: no compiled or test file changed (only README.md), so nothing was built or run",
   "reason": "docs-only change: no compiled or test file changed (only README.md), so nothing was built or run"
  },
  {
   "id": "docs.anchors",
   "tool": "evidence/up-scripts/upfacts.py docs_anchors (GitHub heading slugs + <a name/id>)",
   "status": "pass",
   "summary": "1 intra-document link(s) on lines the change touched, 0 unresolved at head; README.md: base had 4 unresolved of 62, head has 3 unresolved on lines the change did not touch (#author-info, #migration-notes-from-v1x, #rpc)",
   "links_on_touched_lines": [
    {
     "file": "README.md",
     "line": 60,
     "anchor": "aot",
     "resolves_at_head": true
    }
   ],
   "files": [
    {
     "file": "README.md",
     "links_at_head": 62,
     "links_at_base": 62,
     "unresolved_at_base": [
      "aot-code-generation-support-for-unityxamarin",
      "author-info",
      "migration-notes-from-v1x",
      "rpc"
     ],
     "unresolved_at_head_on_untouched_lines": [
      "author-info",
      "migration-notes-from-v1x",
      "rpc"
     ]
    }
   ]
  }
 ],
 "not_run": [
  {
   "id": "docs.rendering",
   "reason": "Markdown was not rendered; anchors were resolved with GitHub slug rules re-implemented in upfacts.py"
  },
  {
   "id": "docs.external_links",
   "reason": "links to other files or URLs were not followed (offline)"
  }
 ],
 "environment": {
  "os": "linux-x64 (container)",
  "note": "no .NET build for a docs-only change"
 }
}
```

## Files changed (1: 1 non-generated, 0 generated)
- README.md (+1 -1, doc)

## Diff (non-generated files)
```diff
diff --git a/README.md b/README.md
index 3ce7e6c2..7f2a0f8c 100644
--- a/README.md
+++ b/README.md
@@ -57,7 +57,7 @@ MessagePack has a compact binary size and a full set of general purpose expressi
 - [IgnoreFormatter](#ignoreformatter)
 - [Reserved Extension Types](#reserved-extension-types)
 - [Unity support](#unity-support)
-- [AOT Code Generation (support for Unity/Xamarin)](#aot-code-generation-support-for-unityxamarin)
+- [AOT Code Generation (support for Unity/Xamarin)](#aot)
 - [RPC](#rpc)
     - [MagicOnion](#magiconion)
     - [StreamJsonRpc](#streamjsonrpc)

```

## File contents (line numbers in the gutter; quote the text after '| ')


## What you did NOT get (refuse anything that depends on it)
- README.md: diff only, full file not provided (doc)
- the upstream issue page itself (only its URL); other files of the repository; build and test logs (only the facts.json summaries)

Return only the JSON object described in the brief.