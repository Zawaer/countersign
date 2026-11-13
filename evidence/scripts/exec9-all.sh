#!/bin/bash
S=/data/work/scripts/exec9.sh
F2234='FullyQualifiedName~SuppressedSourceGenerationTests.'
F2129='FullyQualifiedName~GeneratedFormatterForExternalTypesTests.'
$S 2234 /data/src/mp-2234 "$F2234"
$S 2234-fwf /data/src/mp-2234-fwf "$F2234"
$S 2129 /data/src/mp-2129 "$F2129"
$S 2129-fwf /data/src/mp-2129-fwf "$F2129"
$S base /data/src/mp-base "$F2234|$F2129"
echo ALLDONE
