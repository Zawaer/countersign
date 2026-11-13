# Historical replay on real escapes

**Real data.** Merged pull requests of the upstream MessagePack-CSharp repo, routed by Countersign's deterministic stage, compared with what actually happened to them afterwards. Results: [results.md](results.md) (and `results.json`).

## Files

| File | What |
|---|---|
| `raw/prs.json`, `raw/bodies.json` | `gh pr list -R MessagePack-CSharp/MessagePack-CSharp --state merged --limit 600 --json ...` (fetched 2026-11-13) |
| `make_dataset.py` -> `dataset.yaml` | the PR set, chosen by a fixed rule (below) |
| `find_escapes.py` -> `candidates.json` | machine-proposed escape candidates (revert, explicit reference, SZZ blame) |
| `labels.yaml` | **our labels**: every escape with its links, every examined fix we did not count and why, regressions we could not attribute |
| `countersign/history.py` | facts from the diff + routing; `countersign history` writes `results.json` / `results.md` |

## The PR set

Merged into `develop` or `master` between 2023-06-01 and 2026-06-30 (v3 era; at least 4.5 months for an escape to show up), human author, not a branch-sync PR, and changing at least one `.cs` file under `src/MessagePack.SourceGenerator`, `src/MessagePack.Analyzers*` or `src/MessagePack`. 110 PRs; #2274 is excluded as a mirror of #2275, leaving **109**.

## Labelling rule (escape / no escape found)

A PR is an **escape** if, within 12 months, either

1. **revert**: a later PR reverts it, fully or in effect (#2045 "effectively reverts #2013"); or
2. **follow-up fix**: a later PR fixes a *user-visible* defect (crash, wrong generated code, wrong or missing diagnostic, wire-format change, exception at runtime) **and** the lines that fix changes were written by this PR (SZZ: `git blame` of the deleted/modified lines on the fix's first parent) **and** the fix's description is consistent with this PR having introduced the defect.

Confidence `high` = revert, or the fix explicitly ties the defect to this change; `medium` = SZZ + consistent description, but other PRs also touched the code. Performance-only issues, feature gaps ("this case was never supported") and defects whose code predates the set are **not** counted; each such fix we examined is listed under `examined_not_counted` with the reason.

Everything not labelled escape is **"no escape found"**: absence of evidence, not proof of correctness. Some defects are never reported, and some reported regressions could not be attributed to one PR (`unattributed` in labels.yaml).

Result: **11 escapes of 109** (6 high, 5 medium confidence).

## What is routed, and how

`countersign.history.facts_from_diff` builds facts from the diff alone (file kinds, generated files, test delta, public API surface from `PublicAPI.*.txt` / `AnalyzerReleases.*.md` / public declarations in shipped libraries). `route()` calls `countersign.decide.decide()` with the signed mandate **as written** (we did not tune it to this history), no reviews and no requirement clauses. Two modes:

- `ci-credited` (headline): build and tests credited as passed (the PR merged with green CI), fail-without-fix credited when tests changed alongside source. This is lenient on purpose: it is the most a facts stage could clear.
- `diff-only`: nothing run, so every mandated check is missing and the mandate routes everything to a human.

AI reviewers can only add reasons to route to a human, never remove one, so the tier here is the most lenient Countersign could give: **escapes in the cleared bucket are an upper bound** on what the AI would have let through.

## Limits

- Labels are our judgement; SZZ is noisy (see `candidates.json`: 87 PRs carry at least one weak signal). Read `labels.yaml` and disagree where you like.
- n is small: 24 cleared PRs with 0 escapes still allows an escape rate in the cleared bucket of up to about 12% (rule of three, 95%).
- The checks are credited, not re-run, and fail-without-fix is a proxy.
- The PRs were written by people, not agents.
