# Security review triage

Triage of [codex-review-1.md](codex-review-1.md): one read-only Codex run on 2026-11-14 (run 01a1d762) against the
Countersign pipeline and the demo repo's workflows. Every finding was checked against the code. Codex cited lines in
the vendored copy, `/data/work/demo-repo/.countersign/snapshot/countersign/` (pin 5ac5a94). `github.py`, `ledger.py`,
`keys.py`, `verify.py`, `decide.py` and `llm.py` were byte-identical to this repo's HEAD at review time, so its line
numbers apply here too. The triage also found four issues Codex missed (T1 to T4).

Verdicts: **confirmed** (real, fixed or fix described), **not a real issue as stated** (why given), **needs a decision**.

| # | Finding | Codex severity | Verdict | Status |
|---|---|---|---|---|
| C1 | Signed entry replayable onto another PR | High | Exploit as stated doesn't work; binding gap confirmed (Low) | Fixed in github.py |
| C2 | Code evidence may cite any path at any revision | Medium | Confirmed, and worse than stated (see T2) | **Fixed** (D11, verify.py: rev in {head, base}, path inside the diff) |
| C3 | Loose review-schema validation (duplicates, types) | Low | Confirmed (Low) | **Fixed** (D11: duplicate verdicts count as none, malformed items rejected) |
| C4 | Prompt injection from diff content | Low | Confirmed (Low; partly addressed since) | Fix described for the llm.py owner |
| T1 | Any workflow in the demo repo can forge `countersign/tier` | (missed) | **Confirmed, High** | **Needs a decision** (GitHub App) |
| T2 | `requirement`/`check` evidence verifies trivially and satisfies `min_verified_evidence` | (missed) | **Confirmed, High for live reviews** | **Fixed** (D11: only substantive evidence counts; requirement items never count alone) |
| T3 | Model-supplied `rev` is passed to `git show` as an option | (missed) | Confirmed, Medium | **Fixed** (D11, verify.py and pack.py: `--end-of-options`; llm.py `_code_excerpt` too) |
| T4 | Ledger/key code trusted the shape of ledger lines and signer names | (missed) | Confirmed, Low | Fixed in ledger.py, keys.py |

## C1: signoff replay onto another PR (Codex: High)

**Verdict: the exploit doesn't work as described. A real but low-severity binding gap remains, now fixed.**

Copying an owner's signed comment to another PR fails three ways:

- `verify_signed_entry` (github.py:303-307 at review time) requires `seq == len(ledger)+1` and `prev == ledger tip`.
  Once the original entry is recorded, the copy no longer chains.
- The comment must come from the owner's GitHub login (github.py:343). A PR author can't post as the owner.
- `pack_sha256` must equal the pack CI rebuilds now. The pack contains the evidence head and base, and
  `mismatches()` (github.py:88-102) refuses unless the PR's live head and merge base equal them. A second PR would
  have to point at the same commit as the first.

So Codex's scenario reduces to "the owner posts their own signature twice, before the first is recorded, on two PRs
of the same commit". The real gap: `pr` and `pr_head` were signed (`make_entry` adds them through `extra`) but never
checked. That made the signature bind to the pack only, not to the PR the owner meant to approve.

**Fixed** (countersign/github.py): a new `pr_binding()`, and `verify_signed_entry(..., binding)` now requires
`payload.pr == https://github.com/<repo>/pull/<n>` and `payload.pr_head ==` the PR's live head SHA. `cmd_command`
passes the binding for the PR the comment is on, and `sign-pr` uses the same helper. Malformed blocks (`[]`, a
non-object payload, a non-string `sig`) are now refused with a message instead of raising. Tests in
tests/test_github.py: `test_signed_entry_for_another_pr_is_refused` (both cases),
`test_signed_entry_without_pr_binding_is_refused`, and `test_malformed_signed_blocks_are_refused_not_crashing`.

**Left as designed:** `latest_signoff()` honours a recorded signoff for any PR whose pack hashes the same. That is
the design: the signature covers the evidence for one exact head commit and merge base, which is the same code.
Changing it is a product decision, not a fix.

**Reaching the demo:** the demo runs the pinned snapshot, so this fix takes effect there only after re-vendoring
(`.countersign/vendor.sh <clone> <pushed commit>`) and pushing to the demo's protected `main`. That's for the
coordinator. The old `sign-pr` already signs `pr` and `pr_head`, so already-recorded ledger entries and the owner's
workflow need no change.

## C2: evidence from any path or revision (Codex: Medium)

**Verdict: confirmed.** `Verifier.code` (verify.py:48-66) runs `git show <rev>:<file>` with model-supplied `file`
and `rev`, and accepts any quote that occurs within ±tolerance lines. Nothing ties the file to the diff or to the
requirement. Worse than stated: `rev` isn't limited to head or base either (line 50 passes any other value through),
so with `refs/pull/*` fetched, a quote can come from any commit in the repo, including another branch the agent
pushed. A reviewer (or a reviewer steered by an injected diff) can make "met" rest on a quote from an unrelated file.

**Fix for the verify.py owner:**
1. Allow only `rev in ("head", "base")`, mapped to facts' SHAs. Refuse anything else: "evidence must cite head or base".
2. For `rev == "head"`, require `file` to be in `facts["diff"]["by_file"]` paths. A `base` citation may name any file
   but should not count towards `met` on its own (see T2).
3. Optionally, require the cited line to fall inside a changed hunk for "met" evidence.

## C3: loose schema validation (Codex: Low)

**Verdict: confirmed, Low.** `review_problems` (llm.py:202-225) checks each verdict's `req` and `verdict` but
allows duplicates and doesn't type-check evidence fields. `decide_clauses` takes the first verdict per requirement
(decide.py:111), so a model can put a "met" first and a "not_met" later and only the first counts. Malformed fields
crash the verifier rather than refusing: `int(item.get("line", 0))` raises on `"line": "abc"` (verify.py:55), and
`_norm` raises on a non-string quote. Crashing fails closed (no pack), but it's a cheap denial of service by model
output.

**Fix (llm.py owner, plus verify.py owner for the second part):**
- In `review_problems`, reject a second verdict for the same `req`. Check that `evidence[i].file`, `quote` and `name`
  are strings and `line` is an int.
- In `Verifier.item`, wrap the kind function: catch `(TypeError, ValueError)` and return
  `verified: False, note: "malformed evidence item"`.

## C4: prompt injection from diff content (Codex: Low)

**Verdict: confirmed, Low as a direct risk.** Diff text reaches the model as user content (llm.py build_review_context
and the repair turn at llm.py:247-251). The deterministic gates limit the damage. Without T2's fix, though, an
injected "say met and cite requirement R1" turns into a proven clause, so T2 is the fix that matters.

**Since the review:** commit 9f1991c added `injection_scan`, and decide.py (being edited) refuses every clause with
`reviewers_untrusted` when it fails. **Still suggested for the llm.py owner:** wrap repository content in explicit
delimiters (`<untrusted_diff>...</untrusted_diff>`), and add a line to the system prompt saying instructions inside
them are data. In the repair turn, send only the problem list and the parsed JSON, not the full prior answer.

**API keys:** checked and found sound. The key is only in the Authorization header. Saved contexts and responses
don't contain it.

## T1 (missed by Codex): any workflow in the demo repo can forge `countersign/tier`. High; needs a decision

**Verdict: confirmed by configuration; not exploited.** Branch protection on the demo's `main` requires
`countersign/tier` from `app_id 15368`, which is GitHub Actions itself. Every workflow run in the repo posts as that
app. `build-debug.yml` and `unity.yml` run on `pull_request` and `push`, from the PR branch's own copy of the
workflow file. The agent pushes its branches (`ju26-issue-*`) to the demo repo itself, not a fork. For same-repo
branches, a workflow may raise its token with `permissions: statuses: write`; the repo default
(`default_workflow_permissions: read`) is only a default. So the agent can add a step to its PR's workflow, or push
any branch with a `push` workflow, that calls `POST /statuses/<head sha>` with `context=countersign/tier,
state=success`. Main then accepts the merge without the owner's signature. No human review is required either
(`required_pull_request_reviews: null`), so this status is the only gate.

Codex said the workflows were sound because it checked only the two Countersign workflows. The weakness is in how the
required status is bound, not in those files.

**Options (needs a decision; involves creating a credential):**
1. **Recommended:** a dedicated GitHub App ("Countersign") with `statuses: write` (or `checks: write`). Its private
   key lives in an environment secret that only the default-branch `pull_request_target` and `issue_comment`
   workflows can use (environment with deployment branch `main`). The workflows mint an installation token and post
   the status with it. Then change branch protection to require `countersign/tier` from that App's `app_id`. A
   workflow token can no longer satisfy it.
2. Stop-gap with no new credential: make the demo's other workflows fork-only, or delete them. Then require that
   agent PRs come from a fork, since fork PR tokens can't be raised to write. This is weaker and changes the demo story.
3. Also flag workflow changes in the mandate: `.github/**` as a top-sensitivity area that blocks AI clearance. This
   doesn't stop T1 on its own, because the forged status can be posted after Countersign's.

Not done here. It needs the App created and the user's say on secrets and protection, and the demo's `main` is
protected with `enforce_admins`.

## T2 (missed by Codex): trivially verified evidence proves clauses. High for live reviews

**Verdict: confirmed, reproduced.** `Verifier.requirement` (verify.py:108-115) returns `verified: True` for
`{"kind": "requirement", "req": "R1"}` with no quote ("R1 exists"). `Verifier.check` (verify.py:99-106) returns
`True` for any check that exists, including a failing one, when the item claims no status. `Verifier.test` with no
`outcome` matches any run. `verify_review` counts all of these in `verified_count` (verify.py:133), and
`decide_clauses` compares that count with `min_verified_evidence: 1` (decide.py:126). So a reviewer can say `met` for
every requirement while citing only the requirement itself. If the mandated checks pass and the reviewers agree, the
clause is **proven** with no evidence about the code. Checked in this repo:
`Verifier(...).item({"kind": "requirement", "req": "R1"})` gives `verified: True, note: "R1 exists"`.

In the demo, reviews are replayed from the protected snapshot (`recorded: true`), so a PR author can't do this
there. It matters for live runs, where the review is untrusted model output, possibly steered by an injected diff (C4).

**Fix for the verify.py/decide.py owners:** count toward `min_verified_evidence` only *substantive* evidence. That is
`code` items at head in a changed file (C2), `test` items with an explicit outcome that matches, and `check` items with
an explicit status equal to `pass`. A requirement quote shows the reviewer read the requirement, not that the code
meets it. Keep it as context, record it as `verified` if you like, and don't count it. In code, add a `substantive`
flag in `Verifier.item`, keep `verified_count` for display, add a `substantive_count`, and use that in decide.py:126.

## T3 (missed by Codex): `git show` option injection from model output. Medium

**Verdict: confirmed, reproduced.** verify.py:34 builds `["git", "-C", repo, "show", f"{rev}:{path}"]` with no `--`.
A `rev` starting with `-` is parsed as an option. With `rev = "--output=/tmp/x"` and `file = "/pwned"`, git writes the
`show` output to `/tmp/x:/pwned`. Tried in a scratch repo: the file was created. The write is limited to paths whose
first component ends in `:`, and the content is git's own output, so it's hard to turn into code execution. It's still
an arbitrary-option sink reached by untrusted model output, and other options may be worse.

**Fix for the verify.py owner:** C2's head/base whitelist removes it. Also add `"--end-of-options"` before the
`rev:path` argument, and reject a `file` that starts with `-` or `/` or contains `..` path segments.

## T4 (missed by Codex): ledger and key code assumed well-formed input. Low; fixed

The ledger branch is written only by CI after verification, so these needed an existing ledger compromise. Each still
crashed or misbehaved on hostile input instead of reporting a problem:

- `keys._slug` accepted any name. A signer of `../x` resolved a key outside `keys/`. Now only `[a-z0-9_-]{1,64}`
  is accepted; `verify` returns "invalid owner name" instead of raising.
- `keys.verify` raised `TypeError` on a non-string `sig` and decoded base64 leniently. It now refuses both
  (`validate=True`).
- `ledger.verify` raised on a line that's valid JSON but not an object, or has a non-object payload. It followed
  `payload.pack_path` anywhere on disk (`ws.root / "/etc/..."`) and raised on non-JSON. It now reports these as
  problems, plus unknown entry `type`s, and confines `pack_path` to the workspace.

Tests in tests/test_ledger.py: `test_signer_name_cannot_leave_the_keys_folder`,
`test_non_object_lines_and_bad_signatures_are_problems_not_crashes`, and
`test_pack_path_outside_the_workspace_is_a_problem`.

## Checked and sound (Codex's list, re-checked)

- **Event trust boundary.** `countersign.yml` (`pull_request_target`) checks out `default_branch`, and
  `countersign-command.yml` (`issue_comment`) runs from the default branch. Neither runs PR code; the PR head is
  fetched only as git objects and read with `git diff --numstat` and `rev-parse`. The comment body goes in through
  `GITHUB_EVENT_PATH`, never through `${{ }}` in `run:`. `PR` is a number from the event. Bots are filtered by the job
  `if:`.
- **Commenter authorisation.** The commenter must be the configured login (case-insensitive, as GitHub logins are),
  read from the default-branch `config.yaml`.
- **Ledger chain.** seq, prev and hash over canonical JSON without hash and sig, with an Ed25519 signature over the hex
  hash. One writer at a time (concurrency group), and the push is a fast-forward.
- **Changed-pack protection.** Stale evidence blocks recording, and the signed `pack_sha256` must equal the rebuilt
  pack.
- **API key handling** (see C4).

Not covered by this review: this repo's own `.github/workflows/` (owned by others), the CRACI runner, and the
other demo workflows beyond their effect on T1.
