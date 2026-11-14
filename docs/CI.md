# CI on CRACI

One workflow, [`.github/workflows/countersign.yml`](../.github/workflows/countersign.yml). Every job runs on
[CRACI](https://docs.craci.com) (`runs-on: craci`). Each job starts with a `cracicorp/setup@v1` step that sets
its VM size and a **deny-by-default network policy**. CRACI reads that step when it schedules the job. All
actions are pinned to full commit SHAs (version in a comment). The CRACI GitHub App has access to
`Zawaer/countersign`; running jobs needs no CRACI token.

```
push / pull_request / dispatch ──► pipeline                     (always)
workflow_dispatch job=reviewers ──► reviewers                    (Nemotron reviews; Gemini adjudication if its key exists)
workflow_dispatch job=facts     ──► facts                        (stage 1 for one change, .NET 8 + 9, deps.delta, build.egress)
                                     └─► craci                    (CRACI's job SBOM + network trace of facts; needs CRACI_API_TOKEN)
```

| Job | What it does | Size | Egress allowed |
|---|---|---|---|
| `pipeline` | `uv sync --frozen` + `pytest` (fixture tests included: `COUNTERSIGN_REPO` points at a fresh clone of the challenge repo), `countersign verify-ledger`, `countersign route --all` (the table goes in the job summary), then rebuilds every committed pack and **fails if `packs/*/pack.json` differs from the rebuild**. pack.json is deterministic (no timestamps), so a diff means someone changed reviews, facts, the mandate or the engine without re-running `countersign review`. Uploads `packs` as an artifact. | 4 | PyPI preset, `github.com` |
| `reviewers` | Clones the challenge repo (read-only: the push URL is disabled, no credentials). Runs `countersign review-llm <n> --reviewer nemotron` per change, then `countersign adjudicate <n>` (Gemini, only where the reviewers disagree) **only if the `GEMINI_API_KEY` secret exists**; otherwise a `::notice` says it was skipped. Rebuilds the packs with the new reviews, renders `docs/COSTS.md`, and uploads `reviews` (reviews/, raw responses, packs, `measurement/costs.yaml`). The summary lists Nemotron's verdicts and the route table. | 2 | PyPI preset, `integrate.api.nvidia.com`, `generativelanguage.googleapis.com`, `github.com` |
| `facts` | Reproduces the stage-1 deterministic checks for one change with the same scripts as the original local run: `evidence/scripts/ci-facts.sh` creates base, head and fail-without-fix worktrees, then runs `run.sh` (SDK 8.0.402: build, targeted tests, full suite), `exec9.sh` (SDK 9.0.x: ExecutionTests) and `facts.py`. Paths come from env vars; the local defaults are unchanged. The job summary compares every check status with the committed `evidence/<n>/facts.json`. Uploads `facts-<n>`: facts.json, logs, .trx. Then `deps-delta.py` (restore every `*.csproj` of base and head, CycloneDX SBOMs, the `deps.delta` check; its table goes in the job summary) and `build-egress.py` (copies this job's network policy into facts.json as `build.egress`, fails on a blocked host). | 8 | `presets: [github]`; TLS: `github.com`, .NET download hosts, `api.nuget.org` / `*.nuget.org`, `pkgs.dev.azure.com` (the repo's dotnet-tools feed) |
| `craci` | After `facts`. Downloads `facts-<n>`, runs `python3 -m countersign.craci attach`: with the `CRACI_API_TOKEN` secret it fetches CRACI's job SBOM and network trace of the `facts` job (`GET /v1preview1/sbom`, `/v1preview1/network-trace`, by GitHub job id) and adds `craci.sbom` / `craci.network` to facts.json; without it both are `skipped` ("no CRACI_API_TOKEN") and the job passes. Uploads `craci-<n>` (facts.json + raw SBOM and trace). | 1 | `presets: [github]`; TLS: `api.craci.com`, `api.github.com` |

Secrets: `NVIDIA_API_KEY` (set by Toivo), `GEMINI_API_KEY` (to come from Rene) and, optional, `CRACI_API_TOKEN`
(CRACI app → Settings → API tokens; `gh secret set CRACI_API_TOKEN -R Zawaer/countersign`). Today only
`NVIDIA_API_KEY` is set (`gh secret list`): Gemini adjudication has not run, and the `craci` job records
`craci.sbom` / `craci.network` as skipped. The keys exist only as Actions secrets. The runner reads them from the environment and never writes them to files or logs.

## Dispatch

```bash
# Nemotron reviews (+ Gemini adjudication once its key exists) for some or all changes
gh workflow run countersign.yml -R Zawaer/countersign -f job=reviewers -f changes="2234"
gh workflow run countersign.yml -R Zawaer/countersign -f job=reviewers -f changes="2283 2234 2129 2297"

# Stage-1 deterministic checks for one change on CRACI
gh workflow run countersign.yml -R Zawaer/countersign -f job=facts -f change=2234

# from a branch instead of main
gh workflow run countersign.yml -R Zawaer/countersign --ref ci-wip -f job=reviewers -f changes="2234"

# follow it
gh run list -R Zawaer/countersign -L 5
gh run watch <run-id> -R Zawaer/countersign
gh run view <run-id> -R Zawaer/countersign --log-failed
```

## Pull the results back

```bash
gh run download <run-id> -R Zawaer/countersign -n reviews -D /tmp/cs-reviews
cp /tmp/cs-reviews/reviews/<n>/nemotron.{json,md} reviews/<n>/
cp -r /tmp/cs-reviews/reviews/<n>/raw reviews/<n>/
# append the run's new rows from /tmp/cs-reviews/measurement/costs.yaml to measurement/costs.yaml
countersign review 2283 2234 2129 2297 -q && countersign costs
git add reviews/*/nemotron.* reviews/*/raw packs measurement/costs.yaml docs/COSTS.md

gh run download <run-id> -R Zawaer/countersign -n facts-2234 -D /tmp/cs-facts
```

Review files are not committed by CI (the workflow has `contents: read`). A human pulls them in, so whatever
enters the evidence chain goes through a commit someone made.

## Supply chain: the build as a witness

The `facts` job records what building the change touched, as checks in facts.json (details in
[ARCHITECTURE.md](ARCHITECTURE.md#supply-chain-from-the-build)):

- `deps.delta`: our CycloneDX SBOMs of the restored NuGet graph of base and head, diffed. Fails on a new package or
  version the mandate does not allow, a new feed, or an advisory not on base. Runs locally too
  (`WORK=/tmp/w python3 evidence/scripts/deps-delta.py 2129`, dotnet 8.0.402 on PATH).
- `build.egress`: the network policy of this job, copied from this workflow file into facts.json with its sha256,
  the run URL and the CRACI job CA fingerprint. Fails when the logs show a blocked connection (CRACI answers a denied
  connection with HTTP 403, a reset/EOF or a failed handshake; NuGet reports NU1301) and names the host.
- `craci.sbom`, `craci.network` (job `craci`, token only): CRACI's own record of the `facts` job.

## Where CRACI's SBOM and network trace are

Open the run in the CRACI web app (or follow the CRACI link on the GitHub job). Each job has:
- **SBOM**: built from what CRACI saw the job download *through its package-aware proxy* (presets and `sources`).
  CRACI has no NuGet source type, and traffic allowed by a `connections:` rule bypasses package detection (CRACI
  docs, SBOM completeness), so for `facts` CRACI's SBOM does **not** list the NuGet packages: `deps.delta`
  does. For `pipeline`/`reviewers` (the `pypi` preset) it lists the PyPI packages from `uv.lock`.
- **Network trace** (**View trace**): it streams during the run and stays afterwards. **Proxy violations** lists
  blocked connections with a reason (`no_match`: no rule matched; `tls_no_match`: no rule for the TLS server name;
  `resolver_unknown`: a literal IP). **All network accesses** lists every connection with the rule that matched it.
  For `facts` it should show only GitHub, the .NET download hosts, `api.nuget.org` and `pkgs.dev.azure.com`; that
  is the same list `build.egress` puts in facts.json. For `reviewers`: only PyPI, GitHub and the model APIs, so the
  code under review went only to the reviewers the mandate allows. If a job fails with a 403 or a connection reset,
  look under **Proxy violations** and add the missing host to that job's `network:` block, or (for `facts`) treat it
  as what it is: the change's build tried to reach a host its mandate never allowed.

## Honest limits

- `facts` omitted `presets:` until the `craci` work: per CRACI's docs that enables **every** built-in preset (npm,
  PyPI, Docker Hub, ...), so "deny by default" was not as narrow as the comment said. It is now `presets: [github]`.
- `build.egress` sees what a blocked connection looks like from inside the job; it cannot see a connection the
  policy allowed. The full list of connections is CRACI's trace (`craci.network`, needs the token).
- `deps.delta` vulnerability results come from NuGet Audit at restore time: the advisory database changes, so a
  rerun can find more advisories for the same commit. The SBOM's dependency graph does not change.

- **CRACI is being stress-tested** (banner in the CRACI app): jobs may queue until Sun 19:00 Helsinki. A queued job
  is not a failed one.
- `reviewers` spends model calls: about 1 to 2 per change (one review, plus a JSON repair turn if needed). NVIDIA's free
  tier is about 40 requests/min, and the runner retries 429/5xx with backoff.
- The Nemotron calls go to **NVIDIA's hosted API**. That is fine for MessagePack (open source, `confidential:
  false`). For a confidential repo the runner refuses the hosted endpoint, and you set
  `COUNTERSIGN_NEMOTRON_BASE_URL` to a self-hosted server. We have not run one.
- `facts` reproduces real changes only (not the seeded mutants), and only checks that run on Linux (net8.0
  slice; the mandate's `other-targets` known gap still applies). The fail-without-fix worktree reverts every file
  the branch changed under `src/`.
- `pipeline` fails on stale packs. That is deliberate. After any change to reviews, facts, the mandate or the
  engine, run `countersign review <changes>` and commit `packs/`.
