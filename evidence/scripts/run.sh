#!/bin/bash
# usage: run.sh <label> <worktree> <build-projects (comma sep)> <targeted spec: proj=filter;proj=filter> <fullsuite:yes|no>
# WORK (default /data/work) and CS_ENV let CI reuse this script; locally nothing changes.
WORK=${WORK:-/data/work}
. "${CS_ENV:-/data/work/env.sh}"
label=$1; wt=$2; projs=$3; targeted=$4; full=$5
L=$WORK/out/$label; mkdir -p $L; cd $wt
echo "label=$label wt=$wt head=$(git rev-parse HEAD) dirty=$(git status --porcelain | wc -l)" > $L/meta.txt
s=$(date +%s); rc=0; i=0
: > $L/build.log
for p in ${projs//,/ }; do
  i=$((i+1))
  echo "### dotnet build $p --no-incremental -m:8 -c Debug" >> $L/build.log
  dotnet build $p --no-incremental -m:8 -c Debug -v:m -clp:Summary "-flp:logfile=$L/build.warnings.$i.log;warningsonly;verbosity=minimal" >> $L/build.log 2>&1 || rc=1
done
e=$(date +%s); echo "build_rc=$rc build_s=$((e-s))" >> $L/meta.txt
if [ $rc -ne 0 ]; then echo DONE >> $L/meta.txt; exit 0; fi
IFS=';' read -ra T <<< "$targeted"; j=0
for t in "${T[@]}"; do
  j=$((j+1)); p=${t%%=*}; f=${t#*=}
  s=$(date +%s)
  echo "### dotnet test $p --no-build --filter \"$f\"" > $L/targeted.$j.log
  dotnet test $p --no-build -c Debug --filter "$f" --logger "trx;LogFileName=$L/targeted.$j.trx" -- RunConfiguration.MaxCpuCount=8 >> $L/targeted.$j.log 2>&1
  r=$?; e=$(date +%s); echo "targeted_${j}_rc=$r targeted_${j}_s=$((e-s)) proj=$p filter=$f" >> $L/meta.txt
done
if [ "$full" = yes ]; then
  s=$(date +%s)
  echo "### dotnet test tests/MessagePack.SourceGenerator.Tests --no-build" > $L/full.log
  timeout 1500 dotnet test tests/MessagePack.SourceGenerator.Tests/MessagePack.SourceGenerator.Tests.csproj --no-build -c Debug --logger "trx;LogFileName=$L/full.trx" -- RunConfiguration.MaxCpuCount=8 >> $L/full.log 2>&1
  r=$?; e=$(date +%s); echo "full_rc=$r full_s=$((e-s))" >> $L/meta.txt
fi
echo DONE >> $L/meta.txt
