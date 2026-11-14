#!/usr/bin/env bash
# IN THIS CONTAINER, with tunnel.sh up. Blind reviews by the self-hosted Nemotron (Lightning 30B on our A100) of the
# changes the hosted Nemotron (Super 120B) already reviewed, all in confidential mode (--confidential: vendor
# endpoints refused, the self-hosted one accepted). Output goes to reviews-selfhost/<change>/, so the committed
# reviews/ and packs/ stay as they are. Then writes measurement/selfhost.md (scripts/selfhost/compare.py).
#
#   scripts/selfhost/run_reviews.sh                      # all ten changes
#   BOX_HOURS=1.7 scripts/selfhost/run_reviews.sh        # also the box bill (create -> delete), after teardown
#   ONLY="2283" scripts/selfhost/run_reviews.sh          # a subset
set -uo pipefail
cd "$(dirname "$0")/../.."

CHANGES="${ONLY:-2234 2283 2129 2297 up-2022 up-1934 up-1967 2234-mut2 2283-mut1 2283-sec1}"
export COUNTERSIGN_SELFHOST_URL="${COUNTERSIGN_SELFHOST_URL:-http://127.0.0.1:8000/v1}"
export COUNTERSIGN_GPU_USD_PER_HOUR="${COUNTERSIGN_GPU_USD_PER_HOUR:-2.39}"   # Verda 1x A100 80GB
export COUNTERSIGN_GPU_TYPE="${COUNTERSIGN_GPU_TYPE:-A100 80GB}" COUNTERSIGN_GPU_COUNT="${COUNTERSIGN_GPU_COUNT:-1}"
REPO="${COUNTERSIGN_REPO:-/data/src/mp}"
PY=.venv/bin/python

models=$(curl -sf "$COUNTERSIGN_SELFHOST_URL/models") || { echo "no server at $COUNTERSIGN_SELFHOST_URL: is tunnel.sh running?" >&2; exit 1; }
want=$($PY -c "from countersign import llm; print(llm.PRESETS['nemotron-selfhost']['model'])")
read -r served len < <(echo "$models" | $PY -c "import json,sys; d=json.load(sys.stdin)['data'][0]; print(d['id'], d.get('max_model_len') or '')")
[ "$served" = "$want" ] || { echo "server serves $served, the preset sends $want" >&2; exit 1; }
[ -n "$len" ] && export COUNTERSIGN_SELFHOST_MAX_MODEL_LEN="$len"
echo "server: $served, max-model-len ${len:-unknown}; rate \$$COUNTERSIGN_GPU_USD_PER_HOUR per GPU-hour"

before=$(git diff --stat -- reviews packs)
failed=""
for c in $CHANGES; do
  echo "== $c"
  $PY -m countersign review-llm "$c" --reviewer nemotron-selfhost --confidential --repo "$REPO" || failed="$failed $c"
done
[ "$(git diff --stat -- reviews packs)" = "$before" ] || { echo "reviews/ or packs/ changed: this run must not touch them" >&2; exit 1; }

$PY scripts/selfhost/compare.py --repo "$REPO" ${BOX_HOURS:+--box-hours "$BOX_HOURS"} --gpus "$COUNTERSIGN_GPU_COUNT" $CHANGES
[ -z "$failed" ] || { echo "failed:$failed (rerun with ONLY=\"...\")" >&2; exit 1; }
