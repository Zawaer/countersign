#!/bin/bash
# usage: exec9.sh <label> <worktree> <targeted filter>
# Builds and runs tests/MessagePack.SourceGenerator.{ExecutionTests,MapModeExecutionTests} with .NET SDK 9.0.321
# (the generator references Microsoft.CodeAnalysis 4.12, which SDK 8.0.402's Roslyn 4.11 cannot load: CS9057).
# global.json in the scratch worktree is overridden to pin 9.0.321; the repo itself pins 8.0.402.
. /data/work/env.sh
label=$1; wt=$2; filter=$3
L=/data/work/out/exec9-$label; rm -rf $L; mkdir -p $L; cd $wt
cat > global.json <<'J'
{
  "sdk": {
    "version": "9.0.321",
    "rollForward": "disable",
    "allowPrerelease": false
  }
}
J
echo "label=$label wt=$wt head=$(command git rev-parse HEAD) dirty=$(command git status --porcelain | wc -l) sdk=$(dotnet --version)" > $L/meta.txt
for P in ExecutionTests MapModeExecutionTests; do
  proj=tests/MessagePack.SourceGenerator.$P/MessagePack.SourceGenerator.$P.csproj
  [ -f $proj ] || continue
  s=$(date +%s)
  dotnet build $proj --no-incremental -m:8 -c Debug -v:m -clp:Summary > $L/$P.build.log 2>&1; rc=$?
  e=$(date +%s); echo "${P}_build_rc=$rc ${P}_build_s=$((e-s))" >> $L/meta.txt
  [ $rc -eq 0 ] || continue
  s=$(date +%s)
  echo "### dotnet test $proj --no-build --filter \"$filter\"" > $L/$P.targeted.log
  dotnet test $proj --no-build -c Debug --filter "$filter" --logger "trx;LogFileName=$L/$P.targeted.trx" -- RunConfiguration.MaxCpuCount=8 >> $L/$P.targeted.log 2>&1; rc=$?
  e=$(date +%s); echo "${P}_targeted_rc=$rc ${P}_targeted_s=$((e-s)) ${P}_targeted_filter=$filter" >> $L/meta.txt
  s=$(date +%s)
  echo "### dotnet test $proj --no-build" > $L/$P.full.log
  timeout 900 dotnet test $proj --no-build -c Debug --logger "trx;LogFileName=$L/$P.full.trx" -- RunConfiguration.MaxCpuCount=8 >> $L/$P.full.log 2>&1; rc=$?
  e=$(date +%s); echo "${P}_full_rc=$rc ${P}_full_s=$((e-s))" >> $L/meta.txt
done
# restore the repo's own global.json (8.0.402) so later SDK 8 runs in this worktree are unaffected
command git checkout -- global.json
echo DONE >> $L/meta.txt
