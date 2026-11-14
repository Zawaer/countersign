# Best use of CRACI: the build as a witness in a code review

**Countersign** reviews agent-written changes under a signed mandate. Deterministic checks come first, then two AI
reviewers, and a named human countersigns whatever the AI could not prove. Every job runs on CRACI with its own size
and a deny-by-default network policy. We use CRACI for three things:

**1. Supply-chain risk as review evidence.** An agent can slip in a new package, a moved version or a new NuGet
feed, and no code reviewer reads `Directory.Packages.props`. The `facts` job restores every `*.csproj` of base and
head and writes a deterministic CycloneDX 1.6 SBOM for each (purls, SHA-512, the dependency graph, NuGet Audit
advisories). Diffing the two gives `deps.delta`, a check next to build and tests in the evidence pack: what was added,
which path pulled it in, and whether the mandate allows it. On the four challenge changes it passes (2129 adds a
project, no package). CRACI produced the same SBOM serial numbers as our local run. A seeded attack on 2283
(SharpZipLib 1.2.0 plus a version bump) fails with two advisories that are not on base.

**2. The egress policy as provenance.** The change is built under a policy that allows only GitHub, the .NET
download hosts and NuGet. `build.egress` copies that policy into the facts, together with its sha256, the run URL
and the fingerprint of the CRACI job CA that enforced it. So the pack can state "the build of this change reached
only these hosts". A build step that phones home hits a proxy violation, and the check fails with the host's name.

**3. CRACI's API as an independent record.** A `craci` job pulls CRACI's own SBOM and network trace of the
`facts` job (`/v1preview1/sbom`, `/v1preview1/network-trace`) and adds them as `craci.sbom` and `craci.network`.
That means hosts, bytes, the matched rule and every violation, recorded by CRACI and not by our code. The job needs
a token and never fails without one.

**What we learned.** CRACI has no NuGet source type, so NuGet goes through a TLS connection rule. CRACI logs those
connections but does not inspect them for packages. Our SBOM therefore covers the package graph, and CRACI covers
the policy, the connections and the violations. We also found that leaving out `presets:` turns on every built-in
preset, and fixed our own policy.

Run (2129 on CRACI, 13 of 13 statuses as committed): RUN_2129
Code: github.com/Zawaer/countersign (`countersign/sbom.py`, `countersign/craci.py`, `docs/CI.md`)
