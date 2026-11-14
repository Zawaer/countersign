# Change 2129: stage 1 reproduced on CRACI

- Run: https://github.com/Zawaer/countersign/actions/runs/43559092226 (job `facts`: https://github.com/Zawaer/countersign/actions/runs/43559092226/job/132338528153)
- Workflow commit: 9e708dbb849708b99fe45c3269b04f422e907d93 (main), dispatched with `job=facts change=2129`
- Runner: craci-0-a22dca69 (CRACI, size 8), 2026-11-14T04:56:38Z to 2026-11-14T04:59:46Z, 3 min 8 s
- Artifacts: `facts-2129` (facts.json, logs, .trx), `craci-2129` (craci.sbom / craci.network: skipped, no CRACI_API_TOKEN)

## Stage 1 reproduced on CRACI: change 2129 (head 083afd99, SDK 8.0.402 + 9.0.321)

| Check | Committed (local run) | This run | Same? | This run's summary |
|---|---|---|---|---|
| build | pass | pass | yes | 0 errors, 2 unique warnings |
| tests.targeted | pass | pass | yes | 6 passed, 0 failed, 0 skipped (6 new tests in run) |
| tests.fail_without_fix | pass | pass | yes | new tests fail on base source: 6/6 failed -> tests do cover the change |
| tests.full_suite | pass | pass | yes | tests/MessagePack.SourceGenerator.Tests: 173 tests, 173 passed, 0 failed (0 not failing on base, 0 also failing on base) |
| public_api | fail | fail | yes | public API added: new public class MessagePack.GeneratedMessagePackFormatterAttribute (with public Type? SurrogateType) in src/MessagePack.Annotations/Attribute |
| analyzers | fail | fail | yes | 1 new warnings vs base |
| tests.targeted.execution | pass | pass | yes | GeneratedFormatterForExternalTypesTests: 7 passed, 0 failed (7 new test results; runtime: generator runs inside csc, no CS9057); tests/MessagePack.SourceGenerat |
| tests.execution_fail_without_fix | pass | pass | yes | new runtime tests do not compile with the source reverted (tests/MessagePack.SourceGenerator.ExecutionTests): 7 tests cannot exist without the fix; errors are t |
| tests.execution_full_suite | pass | pass | yes | tests/MessagePack.SourceGenerator.ExecutionTests: 21/21 passed (base 14/14), 0 failures not on base; tests/MessagePack.SourceGenerator.MapModeExecutionTests: 20 |
| solution_membership | fail | fail | yes | new project tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj is not added to MessagePack.sln (only referenced fr |
| injection_scan | pass | pass | yes | no text addressed to automated reviewers in the added lines, commit message or PR text |
| deps.delta | pass | pass | yes | 238 packages on head (238 on base) across 31 projects; 0 added, 0 version changes, 0 removed; new project(s): tests/MessagePack.SourceGenerator.ExternalTypes/Me |
| build.egress | absent | pass | **NO** | built on CRACI under a deny-by-default policy: only 13 TLS host patterns on ports 443 (github.com, codeload.github.com, objects.githubusercontent.com, api.nuget |

12 of 13 check statuses match the committed evidence.

Every check other than `build.egress` also has the same summary text as the committed run. `build.egress` is new: it only runs on CRACI, so the committed (local) facts had none; it was appended to `evidence/2129/facts.json` with `run_url`, every other check left byte-identical.

## build.egress

- Status: **pass**. built on CRACI under a deny-by-default policy: only 13 TLS host patterns on ports 443 (github.com, codeload.github.com, objects.githubusercontent.com, api.nuget.org, *.nuget.org, pkgs.dev.azure.com, ...); presets ['github']; no blocked connection in 29 logs; every NuGet feed the head declares is inside the policy
- Policy: default deny, presets ['github'], ports [443]; sha256 `31fafb855e985c38a31b18cfa9140b83a5b9caa5539eadbdf7344e88b20d2fa1`
- TLS hosts allowed (13): `github.com`, `codeload.github.com`, `objects.githubusercontent.com`, `api.nuget.org`, `*.nuget.org`, `pkgs.dev.azure.com`, `*.vsblob.vsassets.io`, `builds.dotnet.microsoft.com`, `dotnetcli.azureedge.net`, `dotnetcli.blob.core.windows.net`, `*.dot.net`, `dot.net`, `download.visualstudio.microsoft.com`
- Blocked hosts: 0 (none), in 29 logs scanned
- NuGet feeds on head outside the policy: 0
- CRACI job CA sha256: `8a248612007c26021a6c4c3d0ff0308761cf500a5551c85ea146ab803a299123`; runner craci-0-a22dca69
