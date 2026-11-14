# Countersign in a pull-request flow

The four agent-written changes are open as pull requests in our copy of the challenge repo,
[Zawaer/countersign-messagepack-demo](https://github.com/Zawaer/countersign-messagepack-demo) (private; base `32258fdb`),
each with Countersign's evidence pack as a comment, a `countersign/tier` status that `main` requires, and the owner
named in the signed mandate assigned:

| PR | Change | Tier | `countersign/tier` | Owner |
|---|---|---|---|---|
| [#1](https://github.com/Zawaer/countersign-messagepack-demo/pull/1) | 2283, 4 files | ask | pending: awaiting countersignature by Toivo | Toivo (Zawaer) |
| [#2](https://github.com/Zawaer/countersign-messagepack-demo/pull/2) | 2234, 4 files | ask | pending: awaiting countersignature by Toivo | Toivo (Zawaer) |
| [#3](https://github.com/Zawaer/countersign-messagepack-demo/pull/3) | 2129, 28 files | block | failure: risk score (failing checks, critical area, size) | Toivo (Zawaer) |
| [#4](https://github.com/Zawaer/countersign-messagepack-demo/pull/4) | 2297, 237 files | block | failure: split-large-change | Toivo (Zawaer) |

## The flow

```
1. agent opens PR            branch ju26-issue-<n>, label agent-written; the branch names the change and its requirement set
2. facts                     CI recomputes the diff (merge base, head, files, +/-) and checks it matches the evidence
3. reviewers                 Claude, Codex, Nemotron (same prompt, no shared context); Gemini adjudicates disputes only (wired, not run: no key)
4. verify + decide           every citation re-checked against the PR's git objects; tier = strictest driver
5. pack comment              one sticky comment: tier, owner, mandate, "evidence matches this PR", pack sha256, the pack
   status + routing          countersign/tier: success (silent/notify) | pending (ask) | failure (block); owner assigned
6. owner countersigns        on their machine: `countersign.github sign-pr` -> signed `/countersign accept|reject|request-changes <note>`
7. ledger                    CI verifies login, signature, pack hash, chain -> appends to branch countersign-ledger, flips the status
8. merge                     branch protection on main requires countersign/tier = success, set by GitHub Actions only
```

Every new push to the PR re-runs steps 2 to 5. A countersignature covers one pack hash, and the pack is only valid
while the PR head matches its evidence, so a push after signing turns the status back to pending.

### Who may countersign, and why CI cannot

The decision is an Ed25519 signature by the owner's own key over the ledger entry, which names the pack's sha256,
the decision, the note, the tier, the mandate's sha256 and the sign-off statement. CI never holds a private key, so it
cannot sign for anyone; it can only check. The owner runs, from a clone of the demo repo:

```bash
PYTHONPATH=.countersign/snapshot python -m countersign.github sign-pr 1 --gh-repo Zawaer/countersign-messagepack-demo \
  --as Toivo --decision accept --note "..." --key <path to toivo.key> --post
```

It fetches the PR and the ledger tip, rebuilds the pack (packs are deterministic: same inputs, same sha256 as CI's),
shows the sign-off card, signs the entry and posts it as a comment. The `Countersign command` workflow records it only if
all of these hold, and otherwise replies with the reasons and changes nothing:

- the commenter is the GitHub login that `.countersign/config.yaml` maps to the pack's owner (Toivo = Zawaer);
- the signature verifies against `keys/<owner>.pub` from `main` (a PR cannot swap the key: the workflows run as
  `pull_request_target` / `issue_comment`, so the workflow, mandate, keys and login map always come from `main`, and
  PR code is never executed, only read as git objects);
- the entry covers exactly the pack CI rebuilds now, with an allowed decision (a `block` pack accepts only reject or
  request-changes), and the PR head still matches the evidence;
- it chains onto the ledger tip (`seq`, `prev`); a concurrent signature makes it stale ("sign again").

A plain `/countersign accept` without the signed block is answered with the command to run. `/countersign status`
re-evaluates the PR. Tests: `tests/test_github.py` (accept recorded and pushed, unsigned, wrong login, wrong key,
tampered pack hash / chain / decision, new commits after the review).

**Production key:** the demo keys come from `countersign keygen` (`.keys/`, gitignored). In production the owner's
key should be hardware-backed and the same identity GitHub already verifies: an SSH signing key on a security key
(`ed25519-sk`), registered on the owner's GitHub account as a signing key, with `keys/<owner>.pub` derived from it.
The check then also confirms that the key on file is one GitHub lists for that login.

### Merge gate

`main` is protected: the required status is `countersign/tier`, pinned to the GitHub Actions app, so a person with
a personal token cannot post a fake green status. **Known hole (security triage T1, open):** GitHub Actions as a whole
is trusted, so a workflow file added on an agent's own branch could post `countersign/tier=success` itself. The fix
is a dedicated Countersign GitHub App whose key lives in an environment secret limited to `main`, with branch
protection requiring the status from that App only; it needs the repo owner to create the App. The lesson for the
concept: the gate must come from an identity the agent cannot use. The ledger branch `countersign-ledger` refuses force pushes and deletion, so it can
only grow; `countersign verify-ledger` re-checks the whole chain and every signature from any clone. Protection is
enforced for admins too, so not even the repo owner can merge an `ask` PR without the countersignature (pushing a
new snapshot to `main` means switching that off for the push and back on).

## What is real in the demo, and what is recorded

Real, on every run: the PRs and their commits; the diff recomputed from git and compared with the recorded evidence;
verifying every cited code line against the PR's git objects; the decision and tier under the signed mandate (the version vendored at
the pinned commit, signature checked); the pack and its sha256; the sticky comment, the status, the label and the owner assignment; the
ledger check; and the merge gate. Owner signatures are verified with the real Ed25519 keys in `keys/`.

Recorded: the reviewers' output (`reviews/<n>/`), the adjudication and the build/test results in `evidence/<n>/facts.json`
come from Zawaer/countersign at the pinned commit (`.countersign/snapshot/PINNED`). Every comment says so:
*"Recorded reviews; a live run calls the reviewers with the same prompt"* (`prompts/review-v1.md`). A live run adds
`countersign review-llm` per reviewer (API keys as CI secrets, as in Zawaer/countersign's own CI) and the dotnet
facts job before the pack step. The demo has no `silent`/`notify` change, so the green AI-cleared path is exercised only
by tests.

Why vendored: Zawaer/countersign is private, and we did not want to add a cross-repo secret for a demo. The pipeline
code and recorded inputs are copied into `.countersign/snapshot/` with the source commit in `PINNED`
(`.countersign/vendor.sh` refreshes it). To check out the pinned commit instead, add one repo secret: a fine-grained
token with *Contents: read-only* on Zawaer/countersign only, used by `actions/checkout` with `repository:` and `ref:`.
Making Zawaer/countersign public removes the need for both.

Runner: the workflows follow the team's CRACI pattern (`runs-on: ${{ vars.CI_RUNNER || 'ubuntu-24.04' }}` plus a
`cracicorp/setup` step). The demo repo runs on GitHub-hosted runners until the CRACI GitHub App covers it; then set the
repo variable `CI_RUNNER=craci`.

## How it scales

- **One mandate per repo, owners per area.** The mandate's `areas` are CODEOWNERS-style globs (first match wins) with an
  owner, a sensitivity and the AI's clearance right. The change's owner is the owner of the most sensitive area it
  touches; other area owners get an FYI. Adding a team is adding an area, signed by the mandate owner. The login map
  belongs in the signed mandate too (here it is `.countersign/config.yaml` in the demo repo), so changing who may sign
  needs a signature.
- **Humans see only what was not proven.** `silent`/`notify` changes go green without a person; `ask` assigns one named
  owner with a pack that says what was checked, what was refused and why; `block` names the rule to fix. As areas earn
  clearance from agreeing spot-checks (and lose it after escapes), the share routed to humans falls without changing
  the flow.
- **Plain files and one CI job.** The PR step is about 20 seconds on a 2-vCPU runner with recorded inputs. Per change,
  the measured cost of the live inputs (`measurement/costs.yaml`, rendered in [COSTS.md](COSTS.md)): Nemotron
  40k to 53k input tokens per review call on the four agent-written changes (3k to 39k on the small upstream controls), $0 on NVIDIA's free tier (about 40 requests/min, so a busy repo needs a paid or
  self-hosted endpoint); Codex about 95k input tokens per change for its second pass and Claude about 48k per change for v1 (both
  estimates; Codex billed to OpenAI credits, Claude to a subscription; cost unknown); CRACI pipeline runs 0.4 job-minutes, reviewer jobs 3 to 7
  job-minutes for one to three changes. A full dotnet facts run is the largest fixed cost (minutes per change, 8 vCPU).
- **Concurrency.** PR checks run per PR in parallel; ledger writes are serialised by one concurrency group and the
  hash chain, so two owners signing at once cannot overwrite each other: the second is told to sign again.
- **Confidential repos** admit only self-hostable reviewers (the mandate's `confidential` flag), so the same flow works
  on code that may not leave the company.
