#!/bin/bash
# usage: rt.sh <label> <worktree>: build + run tests/MessagePack.Tests (net8.0) -> /data/work/out/rt-<label>/
. /data/work/env.sh
label=$1; wt=$2; L=/data/work/out/rt-$label; mkdir -p $L; cd $wt
P=tests/MessagePack.Tests/MessagePack.Tests.csproj
echo "label=$label wt=$wt head=$(git rev-parse HEAD) dirty=$(git status --porcelain | wc -l)" > $L/meta.txt
s=$(date +%s); dotnet build $P -f net8.0 -m:8 -c Debug -v:m -clp:Summary > $L/build.log 2>&1; rc=$?
echo "build_rc=$rc build_s=$(( $(date +%s)-s ))" >> $L/meta.txt
[ $rc -ne 0 ] && { echo DONE >> $L/meta.txt; exit 0; }
s=$(date +%s); timeout 1800 dotnet test $P -f net8.0 --no-build -c Debug --logger "trx;LogFileName=$L/full.trx" -- RunConfiguration.MaxCpuCount=8 > $L/full.log 2>&1
echo "full_rc=$? full_s=$(( $(date +%s)-s ))" >> $L/meta.txt; echo DONE >> $L/meta.txt
