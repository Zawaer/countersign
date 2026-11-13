# Stage 1 evidence (facts) — how it was produced

Everything here is deterministic and can be re-run. Each `evidence/<change>/facts.json` follows the schema in `docs/ARCHITECTURE.md`; raw logs are in `evidence/<change>/logs/`. `evidence/base/` holds the base-commit reference run (`base_results.json`, logs) used for "pre-existing failure" and "new warning" comparisons. The scripts that were used are copied into `evidence/scripts/`.

- Repo: clone of MessagePack-CSharp at `/data/src/mp`. Base `32258fdbee4bcd653c79f51b4376b5103c6f4d27`.
- Branches: `origin/ju26-issue-{2283,2234,2129,2297}`, each a single commit on top of the base.
- Toolchain: .NET SDK 8.0.402 (`/data/dotnet`), Linux x64 container, Debug, at most 8 CPUs (`-m:8`, `RunConfiguration.MaxCpuCount=8`).

## 1. Environment

```bash
export DOTNET_ROOT=/data/dotnet PATH=/data/dotnet:$PATH DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1
```

(`command git` was used throughout because a shell wrapper rewrites `git` output.)

## 2. Worktrees (the checkout in /data/src/mp itself is never changed)

```bash
cd /data/src/mp
command git worktree add --detach /data/src/mp-base 32258fdb
for n in 2283 2234 2129 2297; do command git worktree add --detach /data/src/mp-$n origin/ju26-issue-$n; done

# fail-without-fix: the branch, with only the files under src/ reverted to base (tests kept)
for n in 2283 2234 2297; do
  command git worktree add --detach /data/src/mp-$n-fwf origin/ju26-issue-$n
  command git -C /data/src/mp-$n-fwf checkout 32258fdb -- $(command git diff --name-only 32258fdb origin/ju26-issue-$n -- src)
done
# 2129 adds files under src/, so the added ones are deleted and the modified ones restored:
command git worktree add --detach /data/src/mp-2129-fwf origin/ju26-issue-2129
cd /data/src/mp-2129-fwf
command git diff --name-status 32258fdb HEAD -- src | while read st f; do
  if [ "$st" = A ]; then command git rm -q "$f"; else command git checkout 32258fdb -- "$f"; fi; done

# mutants: the branch plus one single-line edit (scripts/mutate.py <file> <line> <before> <after> <record.json>)
for m in 2283-mut1 2283-mut2 2234-mut1 2234-mut2; do command git -C /data/src/mp worktree add --detach /data/src/mp-$m origin/ju26-issue-${m%-*}; done
F=src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs
(cd /data/src/mp-2283-mut1 && python3 -I mutate.py $F 1446 'diagnostic.Location.IsInSource && this.compilation.ContainsSyntaxTree(diagnostic.Location.SourceTree)' 'diagnostic.Location.IsInSource' 2283-mut1.json)
(cd /data/src/mp-2283-mut2 && python3 -I mutate.py $F 1077 'item.DeclaringSyntaxReferences.FirstOrDefault()?.GetSyntax().GetLocation()' 'item.DeclaringSyntaxReferences[0].GetSyntax().GetLocation()' 2283-mut2.json)
(cd /data/src/mp-2234-mut1 && python3 -I mutate.py $F 1023 'if (!intMembers.ContainsKey(member.IntKey))' 'if (true)' 2234-mut1.json)
(cd /data/src/mp-2234-mut2 && python3 -I mutate.py $F 1148 'continue; // The key kind does not match the other members; the diagnostic is reported, so skip this member.' '// (mutant: continue removed)' 2234-mut2.json)
```

## 3. Build and test (scripts/run.sh, driven by scripts/all.sh)

For each worktree `<wt>` (labels: base, 2283, 2234, 2129, 2297, *-fwf, *-mut*):

```bash
SG=tests/MessagePack.SourceGenerator.Tests/MessagePack.SourceGenerator.Tests.csproj
cd <wt>
# build (builds the generator, the analyzers/code fixes, Annotations, MessagePack net8.0 and the test project)
dotnet build $SG --no-incremental -m:8 -c Debug -v:m -clp:Summary "-flp:logfile=<out>/build.warnings.1.log;warningsonly;verbosity=minimal"
# targeted tests (one filter per change)
dotnet test $SG --no-build -c Debug --filter "<filter>" --logger "trx;LogFileName=<out>/targeted.1.trx" -- RunConfiguration.MaxCpuCount=8
# full suite of tests/MessagePack.SourceGenerator.Tests (all labels, including fwf and mutants)
dotnet test $SG --no-build -c Debug --logger "trx;LogFileName=<out>/full.trx" -- RunConfiguration.MaxCpuCount=8
```

Targeted filters:

| change | filter |
|---|---|
| 2283 | `FullyQualifiedName~GenericsFormatterTests.` |
| 2234 | `FullyQualifiedName~SuppressSourceGenerationAnalyzerTests.` |
| 2297 | `FullyQualifiedName~CodeCoverageExclusionTests.` |
| 2129 | `FullyQualifiedName~GeneratedMessagePackFormatterTests.` |

ExecutionTests (attempted for base, 2234 and 2129):

```bash
dotnet build tests/MessagePack.SourceGenerator.ExecutionTests/MessagePack.SourceGenerator.ExecutionTests.csproj -m:8 -v:m -clp:Summary
```

These fail to compile, **on base too**: the generator references Microsoft.CodeAnalysis 4.12.0 but SDK 8.0.402 ships Roslyn 4.11 (CS9057), so the generator never runs inside csc. They are recorded as `status: "error"` (`tests.targeted.execution`) with the reason. That affects `SuppressedSourceGenerationTests` (2234) and `GeneratedFormatterForExternalTypesTests` (2129). Swapping in a Roslyn 4.12 compiler toolset was not permitted in this run, so it was not done.

## 4. Assemble facts.json

```bash
python3 -I scripts/mkspec.py     # writes scripts/spec.json (per-change filters, public_api findings, mutation records)
python3 -I scripts/facts.py      # reads TRX/logs, git diff; writes evidence/<change>/facts.json and copies trimmed logs
```

How the checks are derived:

- **diff**: `git diff --numstat 32258fdb <head>`. kind: `*.g.cs` and T4 outputs (`.cs` next to a `.tt`) = generated, `tests/**` = test, `*.md`/`doc/**` = doc, csproj/props/sln/AnalyzerReleases*.md = build, the rest = source.
- **new tests**: `[Fact]`/`[Theory]` methods present in the head version of a changed test file but not in the base version.
- **tests.fail_without_fix**: the targeted filter run in the `-fwf` worktree. `pass` = at least one new test fails with the source reverted. Also records the full suite with the source reverted (`full_suite_with_source_reverted`).
- **tests.full_suite**: `pass` = no failures that do not also fail on base (base: 167/167 passed).
- **analyzers**: the set of build warnings, with the worktree path and line/col stripped, compared with the base set.
- **public_api**: changes to `PublicAPI.*.txt` plus added or removed `public`/`protected` declarations under `src/` (from a manual scan of `git diff`, recorded in mkspec.py).
- **mutants**: `mutation.caught` = at least one targeted test fails. `caught_by_any_deterministic_check` also counts the full suite.

## Cleanup

```bash
for w in /data/src/mp-*; do command git -C /data/src/mp worktree remove --force $w; done
```
