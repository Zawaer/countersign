# Change 2283: stage 1 reproduced on CRACI

- Run: https://github.com/Zawaer/countersign/actions/runs/43559078089 (job `facts`: https://github.com/Zawaer/countersign/actions/runs/43559078089/job/132338492346)
- Workflow commit: 9e708dbb849708b99fe45c3269b04f422e907d93 (main), dispatched with `job=facts change=2283`
- Runner: craci-0-ad8c6a48 (CRACI, size 8), 2026-11-14T04:56:29Z to 2026-11-14T04:58:53Z, 2 min 24 s
- Artifacts: `facts-2283` (facts.json, logs, .trx), `craci-2283` (craci.sbom / craci.network: skipped, no CRACI_API_TOKEN)

## Stage 1 reproduced on CRACI: change 2283 (head 9df83c38, SDK 8.0.402 + -)

| Check | Committed (local run) | This run | Same? | This run's summary |
|---|---|---|---|---|
| build | pass | pass | yes | 0 errors, 1 unique warnings |
| tests.targeted | pass | pass | yes | 19 passed, 0 failed, 0 skipped (3 new tests in run) |
| tests.fail_without_fix | pass | pass | yes | new tests fail on base source: 3/3 failed -> tests do cover the change |
| tests.full_suite | pass | pass | yes | tests/MessagePack.SourceGenerator.Tests: 170 tests, 170 passed, 0 failed (0 not failing on base, 0 also failing on base) |
| public_api | pass | pass | yes | no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or removed in src/ |
| analyzers | pass | pass | yes | no new warnings |
| repro.claude.C1 | pass | pass | yes | reproduced by the pipeline: failed on head (claim: failed), passed on base (claim: passed) |
| injection_scan | pass | pass | yes | no text addressed to automated reviewers in the added lines, commit message or PR text |
| deps.delta | pass | pass | yes | 238 packages on head (238 on base) across 30 projects; 0 added, 0 version changes, 0 removed; 0 new vulnerability hits (6 already on base) |
| build.egress | absent | pass | **NO** | built on CRACI under a deny-by-default policy: only 13 TLS host patterns on ports 443 (github.com, codeload.github.com, objects.githubusercontent.com, api.nuget |

9 of 10 check statuses match the committed evidence.

Every check other than `build.egress` also has the same summary text as the committed run. `build.egress` is new: it only runs on CRACI, so the committed (local) facts had none; it was appended to `evidence/2283/facts.json` with `run_url`, every other check left byte-identical.

## build.egress

- Status: **pass**. built on CRACI under a deny-by-default policy: only 13 TLS host patterns on ports 443 (github.com, codeload.github.com, objects.githubusercontent.com, api.nuget.org, *.nuget.org, pkgs.dev.azure.com, ...); presets ['github']; no blocked connection in 19 logs; every NuGet feed the head declares is inside the policy
- Policy: default deny, presets ['github'], ports [443]; sha256 `31fafb855e985c38a31b18cfa9140b83a5b9caa5539eadbdf7344e88b20d2fa1`
- TLS hosts allowed (13): `github.com`, `codeload.github.com`, `objects.githubusercontent.com`, `api.nuget.org`, `*.nuget.org`, `pkgs.dev.azure.com`, `*.vsblob.vsassets.io`, `builds.dotnet.microsoft.com`, `dotnetcli.azureedge.net`, `dotnetcli.blob.core.windows.net`, `*.dot.net`, `dot.net`, `download.visualstudio.microsoft.com`
- Blocked hosts: 0 (none), in 19 logs scanned
- NuGet feeds on head outside the policy: 0
- CRACI job CA sha256: `80978268bd616a37b11c2eb020ced01f2291a936a727976761dccf202b9c60b7`; runner craci-0-ad8c6a48
