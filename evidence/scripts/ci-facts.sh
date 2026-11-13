#!/bin/bash
# usage: ci-facts.sh <change>      (CI: .github/workflows/countersign.yml, job `facts`)
# Reproduces stage 1 (deterministic checks) for one real change on a fresh machine, with the same scripts as the
# original local run (run.sh, exec9.sh, facts.py), only with paths from the environment:
#   SRC   folder holding the challenge clone at $SRC/mp (scratch worktrees go next to it as $SRC/mp-<label>)
#   WORK  scratch folder for raw outputs ($WORK/out) and the regenerated evidence ($WORK/evidence/<change>)
# dotnet must be on PATH with SDK 8.0.402 (the repo's global.json) and an SDK 9.0.x (runtime ExecutionTests).
set -euo pipefail
change=$1
here=$(cd "$(dirname "$0")" && pwd)
: "${SRC:?set SRC}" "${WORK:?set WORK}"
export WORK CS_SRC=$SRC CS_REPO=$SRC/mp CS_OUT=$WORK/out CS_EVID=$WORK/evidence CS_SPEC=$here/spec.json CS_ONLY=$change
export CS_ENV=$WORK/env.sh
mkdir -p "$WORK/out" "$WORK/evidence"
echo 'export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1' > "$CS_ENV"
SDK9_VERSION=$(dotnet --list-sdks | awk '/^9\./{v=$1} END{print v}')
export SDK9_VERSION
[ -n "$SDK9_VERSION" ] || { echo "no .NET SDK 9 installed"; exit 1; }

eval "$(python3 - "$CS_SPEC" "$change" <<'PY'
import json, shlex, sys
spec = {c['change']: c for c in json.load(open(sys.argv[1]))['changes']}
c = spec.get(sys.argv[2])
if c is None or 'mutation' in c:
    sys.exit(f"{sys.argv[2]}: not a real change in spec.json (mutants are not reproduced in CI)")
p = 'tests/MessagePack.SourceGenerator.Tests/MessagePack.SourceGenerator.Tests.csproj'
print(f"LABEL={shlex.quote(c['label'])}")
print(f"FWF={shlex.quote(c.get('fwf') or '')}")
print(f"TARGETED={shlex.quote(';'.join(f'{p}={f}' for f in c['filters']))}")
print(f"EXEC_FILTER={shlex.quote(c['execution']['filter'] if 'execution' in c else '')}")
PY
)"
PROJ=tests/MessagePack.SourceGenerator.Tests/MessagePack.SourceGenerator.Tests.csproj
BASE=32258fdbee4bcd653c79f51b4376b5103c6f4d27
n=${change%%-*}
HEAD=$(git -C "$SRC/mp" rev-parse "origin/ju26-issue-$n")
echo "change $change: base $BASE head $HEAD, SDK 9: $SDK9_VERSION"

wt() { [ -d "$SRC/mp-$1" ] || git -C "$SRC/mp" worktree add --quiet --detach "$SRC/mp-$1" "$2"; }
wt base "$BASE"
wt "$LABEL" "$HEAD"
if [ -n "$FWF" ]; then
  # fail-without-fix: the change's head with every file it changed under src/ put back to base (tests kept)
  wt "$FWF" "$HEAD"
  git -C "$SRC/mp" diff --name-only "$BASE" "$HEAD" -- src/ | while read -r f; do
    if git -C "$SRC/mp" cat-file -e "$BASE:$f" 2>/dev/null; then git -C "$SRC/mp-$FWF" checkout --quiet "$BASE" -- "$f"
    else git -C "$SRC/mp-$FWF" rm --quiet -f -- "$f"; fi
  done
  echo "fail-without-fix worktree: $(git -C "$SRC/mp-$FWF" status --porcelain | wc -l) files reverted to base"
fi

"$here/run.sh" base "$SRC/mp-base" "$PROJ" "$TARGETED" yes
"$here/run.sh" "$LABEL" "$SRC/mp-$LABEL" "$PROJ" "$TARGETED" yes
[ -z "$FWF" ] || "$here/run.sh" "$FWF" "$SRC/mp-$FWF" "$PROJ" "$TARGETED" no
if [ -n "$EXEC_FILTER" ]; then
  "$here/exec9.sh" "$LABEL" "$SRC/mp-$LABEL" "$EXEC_FILTER"
  [ -z "$FWF" ] || "$here/exec9.sh" "$FWF" "$SRC/mp-$FWF" "$EXEC_FILTER"
  "$here/exec9.sh" base "$SRC/mp-base" "$EXEC_FILTER"
fi
python3 "$here/facts.py"
echo "wrote $WORK/evidence/$change/facts.json"
