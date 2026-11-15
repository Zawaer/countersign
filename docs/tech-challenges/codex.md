# Best use of Codex: it found security holes in our own pipeline

**Countersign** reviews agent-written changes: deterministic checks, three AI reviewers (Claude, Codex, Nemotron),
then a named human countersigns what the AI could not prove.

**Security holes in our pipeline** ([TRIAGE.md](../security/TRIAGE.md)). One read-only Codex run over our workflows,
signatures, ledger, and whether model output can make a clause proven. Every finding was checked against the code:
evidence could cite any path at any revision (confirmed, fixed), loose review-schema validation (confirmed, fixed),
prompt injection from diff content (confirmed, fix described), and signoff replay onto another PR (exploit fails as
stated, but the PR-binding gap behind it was real; fixed). Following its report we found four more, all fixed. The
worst: any workflow in the demo repo could forge the merge-gate status (High). Now only our "Countersign Gate"
GitHub App posts it, and branch protection accepts it from that App alone.

**What Codex did** ([CODEX_LOG.md](../CODEX_LOG.md)):

| Run | Task | Result |
|---|---|---|
| Review, read-only | 4 real changes | first pass, kept as `codex.v1` |
| Review, read-only | same 4, with the test facts | all <!--n:codex_v2_met-->11<!--/n--> of <!--n:codex_v2_clauses-->11<!--/n--> clauses met, no findings |
| Review, read-only | 3 upstream control changes | all met, every citation verifies |
| Security, read-only | our own pipeline | 4 findings, above |
| Write mode | blind seeded-review runner, `_code_excerpt` hardening | 139 tests pass |
| Write mode | demo screen | checked at 390 and 1280 px |
| Review, read-only | demo-docs1 | both clauses met |

**The rubber stamp.** Given the passing tests, its second pass said every clause was met: <!--n:codex_verified-->0<!--/n--> verified findings,
missing <!--n:codex_missed_majors-->6<!--/n--> verified majors the others found. That is why one reviewer can never clear: a clause is proven only
if every reviewer says met with verified evidence. On 2283 the pack shows "Codex said met without verified
evidence" beside Claude's reproduced objection.

**What went wrong.** Two `codex exec` runs did nothing (its sandbox cannot create a namespace in our container), yet
our script committed; CODEX_LOG corrects the two mislabelled commits.

**Tokens.** About <!--n:codex_tokens_k-->1,076<!--/n-->k over the <!--n:codex_runs-->5<!--/n--> read-only runs (`measurement/costs.yaml`).

Code: github.com/Zawaer/countersign (`reviews/*/codex.json`, `docs/security/`)

<sub>2,369 characters</sub>
