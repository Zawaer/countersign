# Best use of CRACI: the build as a witness in a code review

**Countersign** reviews agent-written changes under a mandate. Deterministic checks come first, then three AI
reviewers (Claude, Codex, Nemotron), and a named human countersigns whatever the AI could not prove. Every job runs on CRACI with its size
and a deny-by-default network policy. We use it for three things:

**1. Supply-chain risk as review evidence.** An agent can slip in a new package, version or NuGet feed, and no
reviewer reads `Directory.Packages.props`. The `facts` job restores every `*.csproj` of base and head into
deterministic CycloneDX 1.6 SBOMs (purls, SHA-512, graph, NuGet Audit advisories); their diff is `deps.delta`, a
check next to build and tests. It passes on the four changes, and CRACI produced the same SBOM serials as our local run. A seeded attack on 2283 (SharpZipLib 1.2.0) fails
with two advisories not on base.

**2. The egress policy as provenance.** Each change is built under a policy allowing only GitHub, the .NET
hosts and NuGet. `build.egress` copies it into the facts with its sha256, the run URL and the CRACI job CA
fingerprint, so the pack says "the build reached only these hosts". A build that phones home fails with the host.

| Change | CRACI run (main) | `facts` job | Statuses matched | Egress allowed | Blocked |
|---|---|---|---|---|---|
| 2283 | 43559078089 | 2m24s | 9/9 | 13 TLS patterns | 0 |
| 2234 | 43559084959 | 3m22s | 12/12 | 13 TLS patterns | 0 |
| 2129 | 43559092226 | 3m08s | 12/12 | 13 TLS patterns | 0 |
| 2297 | 43559099382 | 1m56s | 8/8 | 13 TLS patterns | 0 |

**3. CRACI's API as an independent record.** A `craci` job adds CRACI's own SBOM and network trace of `facts`
(`/v1preview1/sbom`, `/network-trace`) as `craci.sbom`, `craci.network`. No API token is set, so both are `skipped`.

**What we learned.** CRACI has no NuGet source type, so NuGet goes through a TLS rule CRACI logs but does not
inspect: our SBOM covers packages, CRACI the policy and connections. Omitting `presets:` enables every preset; we fixed ours.

Runs: github.com/Zawaer/countersign/actions/runs/<run> (table); comparisons in `evidence/<n>/ci/compare.md`
Code: github.com/Zawaer/countersign (`countersign/sbom.py`, `countersign/craci.py`)
