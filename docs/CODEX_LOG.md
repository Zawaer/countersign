# Codex log

Every Codex (OpenAI) run made for this project, with how its output was used.

## 2026-11-14 01:13 (Europe/Helsinki): stage-2 second-vendor review of 2283, 2234, 2129, 2297

- **Purpose:** independent second-vendor review (reviewer "codex") of the four agent-written changes, branches origin/ju26-issue-{2283,2234,2129,2297} on base 32258fdb in /data/src/mp.
- **Prompt summary:** one run covering all four changes. Codex was told where the repo, the requirements files and the review JSON schema (docs/ARCHITECTURE.md) are, and given the evidence rules: code citations need file, line and exact substring at head or base; use `cannot_determine` plus a refusal when unsure; check the root cause, scope, docs vs code and test coverage. It was asked to go deep on 2283 and 2234, do a scoped review of 2129 and 2297 and refuse what it didn't cover, and to print each JSON between `=== BEGIN/END <n> ===` markers followed by prose. The tool cannot set a working directory, so the prompt gave the repo path.
- **Mode:** read-only (`readOnly: true`). Codex changed no files.
- **Model:** self-reported in the JSON as "GPT-6 Codex" (the tool used Codex's default model and does not confirm the name). Run id 01a1d72f-8096-7c81-916c-230e8cc42976, about 116k tokens in and 4k out.
- **Use of output:** saved verbatim to reviews/<n>/codex.json (all four parsed as JSON, so no syntax fixes were needed) and the prose to reviews/<n>/codex.md. Format check: every `code` and `requirement` evidence item resolves. Two citations (2283, TypeCollector.cs line 1447) match one line off, at 1446, which is inside the engine's ±3 tolerance. Two things were left as Codex wrote them: `reviewed_at` is a placeholder (`2026-11-13T00:00:00Z`), and the model name is self-reported. Not committed.
