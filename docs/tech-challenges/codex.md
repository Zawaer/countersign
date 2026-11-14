# Best use of Codex: a second vendor that checks our reviewers and our pipeline

**Countersign** reviews agent-written changes: deterministic checks, three AI reviewers (Claude, Codex, Nemotron),
and a named human countersigns what the AI could not prove. Codex had three jobs; every run is in
[CODEX_LOG.md](../CODEX_LOG.md).

**1. Second-vendor reviewer.** Codex reviewed every real change read-only, same brief and schema as the others; the
engine re-checks each citation. Its second pass, given the passing tests, said all <!--n:codex_v2_met-->11<!--/n--> of <!--n:codex_v2_clauses-->11<!--/n-->
clauses were met and found nothing: <!--n:codex_verified-->0<!--/n--> verified findings, and it missed <!--n:codex_missed_majors-->6<!--/n--> verified majors the others found. That
rubber stamp taught us the core rule: one reviewer's "all good" never clears. A clause is proven only if every
reviewer says met with verified evidence, so the stamp cleared nothing; on 2283 the pack shows "Codex said
met without verified evidence" beside Claude's reproduced objection.

**2. Security review of our own pipeline.** One read-only run over the workflows, signatures, ledger, and whether
model output can make a clause proven. It reported signoff replay, evidence from any path, a loose
review schema and prompt injection. Triage (`docs/security/TRIAGE.md`): the replay exploit fails as stated, but
the PR binding gap behind it was real and is fixed; path and schema are fixed; the injection fix is described. Codex
missed four that triage found: any workflow could forge the merge status (High; now posted only by a dedicated
GitHub App), trivial evidence counting toward "met" (High), `git show` option injection from a model-supplied
revision (Medium), ledger input hardening (Low). All four fixed.

**3. Development.** In write mode Codex finished the blind review of seeded changes (the runner hides the seeding
and refuses a context that names it), hardened the adjudicator's code excerpts (5d66189) and built the demo screen,
checked with screenshots at 390 and 1280 px (5c00775).

**What went wrong.** Two earlier `codex exec` runs failed: Codex's sandbox cannot create a namespace
inside our container, so no command ran. Our script still committed, so two commits (5e366b5, 32eeaa0) were
labelled as Codex work that was not. CODEX_LOG records the correction.

**Tokens.** About <!--n:codex_tokens_k-->1,015<!--/n-->k in the <!--n:codex_runs-->4<!--/n--> read-only runs (three reviews, one security review), 19k in the
failed ones (`measurement/costs.yaml`).

Code: github.com/Zawaer/countersign (`reviews/*/codex.json`, `docs/security/`)

<sub>2,479 characters</sub>
