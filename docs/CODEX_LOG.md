# Codex log

Every Codex (OpenAI) run made for this project, with how its output was used.

## 2026-11-14 01:13 (Europe/Helsinki): stage-2 second-vendor review of 2283, 2234, 2129, 2297

- **Purpose:** independent second-vendor review (reviewer "codex") of the four agent-written changes, branches origin/ju26-issue-{2283,2234,2129,2297} on base 32258fdb in /data/src/mp.
- **Prompt summary:** one run covering all four changes. Codex was told where the repo, the requirements files and the review JSON schema (docs/ARCHITECTURE.md) are, and given the evidence rules: code citations need file, line and exact substring at head or base; use `cannot_determine` plus a refusal when unsure; check the root cause, scope, docs vs code and test coverage. It was asked to go deep on 2283 and 2234, do a scoped review of 2129 and 2297 and refuse what it didn't cover, and to print each JSON between `=== BEGIN/END <n> ===` markers followed by prose. The tool cannot set a working directory, so the prompt gave the repo path.
- **Mode:** read-only (`readOnly: true`). Codex changed no files.
- **Model:** self-reported in the JSON as "GPT-6 Codex" (the tool used Codex's default model and does not confirm the name). Run id 01a1d72f-8096-7c81-916c-230e8cc42976, about 116k tokens in and 4k out.
- **Use of output:** saved verbatim to reviews/<n>/codex.json (all four parsed as JSON, so no syntax fixes were needed) and the prose to reviews/<n>/codex.md. Format check: every `code` and `requirement` evidence item resolves. Two citations (2283, TypeCollector.cs line 1447) match one line off, at 1446, which is inside the engine's ±3 tolerance. Two things were left as Codex wrote them: `reviewed_at` is a placeholder (`2026-11-13T00:00:00Z`), and the model name is self-reported. Not committed.

## 2026-11-14 01:37 (Europe/Helsinki): second-pass review of 2283, 2234, 2129, 2297 with deterministic facts

- **Purpose:** second pass of the independent second-vendor review (reviewer "codex"), this time pointing Codex at evidence/<n>/facts.json (build, targeted tests, fail-without-fix, full suites, SDK 9 execution tests, public API and analyzer checks) and requirements/<n>.yaml. The first-pass outputs were kept as reviews/<n>/codex.v1.json / codex.v1.md.
- **Prompt summary:** one run covering all four changes; same evidence rules as before (code/test/check citations must be machine-verifiable, `cannot_determine` plus refusal when unsure, judge root cause, note requirements that already held on base). Deep review of 2283 and 2234, scoped review of 2129 and 2297 with explicit refusals. Told not to read existing files under reviews/. Output printed between `=== BEGIN/END <n> ===` markers, then prose.
- **Mode:** read-only (`readOnly: true`). The tool reported docs/CONCEPT_CARD.md as changed, but that file was added in commit f4e47be by another agent at 01:38:53, during the run; the working tree had no diff to it afterwards, so Codex changed no files.
- **Model:** self-reported in the JSON as "GPT-6" (tool default model; name not confirmed by the tool). Run id 01a1d745-bd4e-7ef0-a26c-3a633f6d472a, about 378k tokens in and 4.8k out.
- **Use of output:** saved verbatim to reviews/<n>/codex.json (all four parsed as JSON; no syntax fixes) and prose to reviews/<n>/codex.md. `reviewed_at` was stamped by the runner with the run start time (2026-11-14T01:37:14+02:00), replacing Codex's placeholder. Ran `countersign review <n>` for each change: all `code` and `check` items verify; 8 `test` items (outcome "passed") are marked unverified with "facts.json says failed" (2283: 3, 2234: 3, 2297: 2). Each of those tests appears both as passed in the targeted run and as failed in the source-reverted run, so this looks like the verifier matching the fail-without-fix entry; left as Codex wrote them.

## 2026-11-14 02:06 (Europe/Helsinki): review of three upstream control changes (up-2022, up-1934, up-1967)

- **Purpose:** independent second-vendor review (reviewer "codex") of three small merged upstream MessagePack-CSharp PRs (#2022, #1934, #1967), used as low-risk controls for the clearance demo.
- **Prompt summary:** one short run. Codex was pointed at the per-change briefs /tmp/up-briefs/<pr>.md (rules and full context, followed as written), the repo /data/src/mp, told to use reviewer "codex", vendor "OpenAI", its exact model name and prompt_version "review-v1", not to read anything under reviews/, and to print each JSON between `=== BEGIN/END up-<pr> ===` markers followed by prose.
- **Mode:** read-only (`readOnly: true`). The tool reported 17 files as changed (evidence/repros/*, evidence/scripts/repro.py, site/*, countersign/history.py, countersign/measure.py, measurement/history/*, docs/MEASUREMENT.md); these are other agents' concurrent work in the shared worktree (already dirty before the run, or committed in 353239a / created by the repro work), not Codex edits.
- **Model:** self-reported in the JSON as "GPT-6" (tool default model; name not confirmed by the tool). Run id 01a1d760-c533-7c02-8536-d8f8364e5c98, 265,396 tokens in and 4,358 out.
- **Use of output:** saved to reviews/up-<pr>/codex.json (all three parsed as JSON; no syntax fixes) and prose to reviews/up-<pr>/codex.md. `reviewed_at` was stamped by the runner with the run start time (2026-11-14T02:06:41+02:00), replacing Codex's `2026-11-14T00:07:27Z`. All three: every requirement "met", no findings, no refusals. `countersign review up-<pr>`: every cited evidence item verifies (no unverified refs). Requirements still show REFUSED in the packs only because Claude and Nemotron have not reviewed these changes yet (1 of 3 reviewers).

## 2026-11-14 02:08 (Europe/Helsinki): security review of Countersign's own pipeline

- **Purpose:** a security review of our own pipeline during development, not a review of a change. Covered the GitHub workflows (`pull_request_target`, `issue_comment`), signature verification, ledger chaining, what is signed, commenter authorisation (github.py, ledger.py, keys.py), whether untrusted reviewer JSON can make a clause proven (verify.py, decide.py), and prompt-injection and key-leak exposure in llm.py. Targets: this repo and the demo repo's `.github/workflows/` and `.countersign/`.
- **Prompt summary:** one run. Asked for severity, file:line, an exploit scenario and a minimal fix per issue, plus an explicit list of what it checked and found sound, in Markdown.
- **Mode:** read-only (`readOnly: true`). The tool reported 19 files as changed (evidence/repros/*, packs/up-*, reviews/up-*/claude.json, site/*). These are other agents' concurrent work in the shared worktree (untracked, and part of it already present before the run), not Codex edits.
- **Model:** the tool's default Codex model (the name isn't reported). Run id 01a1d762-85d0-7620-9743-6a9bde01733a, 240,277 tokens in and 2,171 out (reported by the tool).
- **Use of output:** saved verbatim to docs/security/codex-review-1.md and triaged in docs/security/TRIAGE.md. Codex reported four findings: signoff replay (High), evidence from any path (Medium), loose schema (Low) and prompt injection (Low). On triage, the replay exploit doesn't work as stated, but a binding gap was real and is fixed in github.py. The other three were confirmed and handed to their files' owners. The triage also found four issues Codex missed: workflow-token status forgery on the demo (High, needs a decision), trivially verified `requirement`/`check` evidence counting toward `met` (High for live reviews), `git show` option injection from model-supplied `rev` (Medium), and ledger/key input hardening (Low, fixed). No follow-up run.

## 2026-11-14 03:10 (Europe/Helsinki): correction, two failed CLI runs
Two `codex exec` runs (write mode, started from a script during Claude downtime) did nothing: Codex's sandbox (bubblewrap) can't create a namespace inside this container, so every shell command failed and Codex made no changes (15k and 4k tokens). The script still committed the working tree afterwards, so commits **5e366b5** ("Blind model review of seeded changes ... written with Codex") and **32eeaa0** ("Site: 'the code is the scene' demo screen (finished with Codex)") are mislabelled: their content is unfinished work by Claude agents that had stopped on a usage limit, not Codex's. Codex's real contributions are the logged review and security-review runs above and the runs below.

## 2026-11-14 03:17 (Europe/Helsinki): blind review of seeded changes + `_code_excerpt` hardening, write mode

- **Purpose:** complete blind model review for seeded changes and harden adjudicator code excerpts against model-supplied revisions and paths.
- **Changes:** build the review context from the branch diff with its recorded edit applied; show the base change id and requirements; omit the recorded edit metadata and reject contexts containing forbidden terms. The planted edit is replayed correctly when `before` is empty. `_code_excerpt` accepts only `head`/`base`, confines paths to the change diff (or allowed base context), and uses `git show --end-of-options`.
- **Files changed:** `countersign/llm.py`, `tests/test_llm.py`, `docs/CODEX_LOG.md`.
- **Verification:** `.venv/bin/python -m pytest -q` — 139 passed.

## 2026-11-14 03:21 (Europe/Helsinki): "the code is the scene" demo screen, write mode

- **Purpose:** finish the Countersign judge-facing landing page as a focused code scene for the Junction 2026 demo.
- **Changes:** build the landing scene from pack/facts/review evidence, attach compact status pins to cited diff/test lines, provide evidence cards and scene switching (including seeded bugs), and simplify the top navigation and mobile layout. Light is the default; the theme control supports dark mode.
- **Files changed:** `site/scene.py`, generated site pages under `site/`, and this log entry.
- **Visual review:** Playwright screenshots at 390px and 1280px; two removal passes removed mobile title truncation and a duplicate verdict phrase. Final screenshot paths: `/data/work/screenshots/countersign/scene-390-final.png` and `/data/work/screenshots/countersign/scene-1280-final.png`.
