# Change 2234: stage 1 reproduced on CRACI

- Run: https://github.com/Zawaer/countersign/actions/runs/43559084959 (job `facts`: https://github.com/Zawaer/countersign/actions/runs/43559084959/job/132338506177)
- Workflow commit: 9e708dbb849708b99fe45c3269b04f422e907d93 (main), dispatched with `job=facts change=2234`
- Runner: craci-1-1f0727ec (CRACI, size 8), 2026-11-14T04:56:33Z to 2026-11-14T04:59:55Z, 3 min 22 s
- Artifacts: `facts-2234` (facts.json, logs, .trx), `craci-2234` (craci.sbom / craci.network: skipped, no CRACI_API_TOKEN)

## Stage 1 reproduced on CRACI: change 2234 (head 9007cee1, SDK 8.0.402 + 9.0.321)

| Check | Committed (local run) | This run | Same? | This run's summary |
|---|---|---|---|---|
| build | pass | pass | yes | 0 errors, 1 unique warnings |
| tests.targeted | pass | pass | yes | 8 passed, 0 failed, 0 skipped (8 new tests in run) |
| tests.fail_without_fix | pass | pass | yes | new tests fail on base source: 4/8 failed -> tests do cover the change (4 new tests pass without the fix) |
| tests.full_suite | pass | pass | yes | tests/MessagePack.SourceGenerator.Tests: 175 tests, 175 passed, 0 failed (0 not failing on base, 0 also failing on base) |
| public_api | pass | pass | yes | no public API changes: no PublicAPI.Shipped/Unshipped.txt changed, no public/protected declarations added or removed in src/ |
| analyzers | pass | pass | yes | no new warnings |
| tests.targeted.execution | pass | pass | yes | SuppressedSourceGenerationTests: 4 passed, 0 failed (4 new test results; runtime: generator runs inside csc, no CS9057) |
| tests.execution_fail_without_fix | fail | fail | yes | new runtime tests pass on base source: 0/4 failed -> these runtime tests do NOT demonstrate the change (runtime behaviour they check is identical with and witho |
| tests.execution_full_suite | pass | pass | yes | tests/MessagePack.SourceGenerator.ExecutionTests: 16/16 passed (base 14/14), 0 failures not on base; tests/MessagePack.SourceGenerator.MapModeExecutionTests: 22 |
| repro.claude.C2 | pass | pass | yes | reproduced by the pipeline: failed on head (claim: failed), failed on base (claim: failed), passed on control (claim: passed) |
| injection_scan | pass | pass | yes | no text addressed to automated reviewers in the added lines, commit message or PR text |
| deps.delta | pass | pass | yes | 238 packages on head (238 on base) across 30 projects; 0 added, 0 version changes, 0 removed; 0 new vulnerability hits (6 already on base) |
| build.egress | absent | pass | **NO** | built on CRACI under a deny-by-default policy: only 13 TLS host patterns on ports 443 (github.com, codeload.github.com, objects.githubusercontent.com, api.nuget |

12 of 13 check statuses match the committed evidence.

Every check other than `build.egress` also has the same summary text as the committed run. `build.egress` is new: it only runs on CRACI, so the committed (local) facts had none; it was appended to `evidence/2234/facts.json` with `run_url`, every other check left byte-identical.

## build.egress

- Status: **pass**. built on CRACI under a deny-by-default policy: only 13 TLS host patterns on ports 443 (github.com, codeload.github.com, objects.githubusercontent.com, api.nuget.org, *.nuget.org, pkgs.dev.azure.com, ...); presets ['github']; no blocked connection in 40 logs; every NuGet feed the head declares is inside the policy
- Policy: default deny, presets ['github'], ports [443]; sha256 `31fafb855e985c38a31b18cfa9140b83a5b9caa5539eadbdf7344e88b20d2fa1`
- TLS hosts allowed (13): `github.com`, `codeload.github.com`, `objects.githubusercontent.com`, `api.nuget.org`, `*.nuget.org`, `pkgs.dev.azure.com`, `*.vsblob.vsassets.io`, `builds.dotnet.microsoft.com`, `dotnetcli.azureedge.net`, `dotnetcli.blob.core.windows.net`, `*.dot.net`, `dot.net`, `download.visualstudio.microsoft.com`
- Blocked hosts: 0 (none), in 40 logs scanned
- NuGet feeds on head outside the policy: 0
- CRACI job CA sha256: `baa0ee3ae7ed8f66cd7175b67a7351f91531c53a210f3955fbd6b456ccc79b31`; runner craci-1-1f0727ec
