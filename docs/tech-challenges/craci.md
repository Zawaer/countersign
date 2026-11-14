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

| Change | `facts` run | Statuses | Blocked | CRACI trace run | Hosts | Violations |
|---|---|---|---|---|---|---|
| 2283 | 43559078089 | 9/9 | 0 | 43580831017 | 6+7 | 0 |
| 2234 | 43559084959 | 12/12 | 0 | 43580841815 | 6+7 | 0 |
| 2129 | 43559092226 | 12/12 | 0 | 43580812697 | 6+7 | 0 |
| 2297 | 43559099382 | 8/8 | 0 | 43580820406 | 6+7 | 0 |

**3. CRACI's API as an independent record.** A `craci` job adds CRACI's own trace and SBOM of `facts` as checks.
On all four: craci.network: pass, 13 hosts observed (6 build hosts, all in the policy, plus 7 GitHub Actions
endpoints), 0 violations. craci.sbom: pass, 0 components.

**What we learned.** CRACI's trace saw what our log check could not: about 2,900 denied certificate revocation
lookups (NuGet signature checks), so revocation was not checked online. CRACI has no NuGet source type, so our
SBOM covers packages and CRACI the connections. A CRACI job cannot call api.craci.com, so the `craci` job runs
GitHub-hosted.

Runs: github.com/Zawaer/countersign/actions/runs/<run>; details in `evidence/<n>/ci/compare.md`
Code: github.com/Zawaer/countersign (`countersign/sbom.py`, `countersign/craci.py`)
