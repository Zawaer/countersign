#!/usr/bin/env bash
# Stochastic rounding needs Hopper (sm_90+); the A100 (sm_80) lacks the instruction, so it is only enabled there.
CC=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -1 | tr -d .)
MAMBA_ROUNDING_FLAGS=""; [ "${CC:-0}" -ge 90 ] && MAMBA_ROUNDING_FLAGS="--enable-mamba-cache-stochastic-rounding --mamba-cache-philox-rounds 5"
# ON THE GPU BOX. Starts vLLM's OpenAI-compatible server on 127.0.0.1:8000 ONLY (reach it through tunnel.sh; nothing
# is exposed to the internet, so no API key is needed). Tries the largest context window that fits:
# 131072 (the hosted run's 180k-char context plus a 32k answer, unchanged), then 65536, then 49152; the runner reads
# the window from /v1/models and shrinks the context to match. Log: ~/selfhost/serve.log.
#
#   ssh -i /data/work/ssh/verda root@$VERDA_HOST 'bash serve.sh'
set -euo pipefail

DIR="${SELFHOST_DIR:-$HOME/selfhost}"
MODEL_ID="nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16"   # served under the HF id: the preset sends exactly this
LENS="${MAX_MODEL_LENS:-131072 65536 49152}"
LOG="$DIR/serve.log"

pkill -f "vllm serve" 2>/dev/null && sleep 5 || true
for len in $LENS; do
  echo "starting vLLM with --max-model-len $len" | tee "$LOG"
  # Flags from the model card's single-GPU recipe (vLLM 0.27.1), minus tool calling (we do not use tools) and with
  # --max-num-seqs 2 (reviews run one at a time; fewer sequences leave memory for the long window).
  # MAMBA_BACKEND=flashinfer as in the card's H100 recipe; empty uses vLLM's default kernel (safer on an A100).
  nohup "$DIR/venv/bin/vllm" serve "$DIR/model" \
    --served-model-name "$MODEL_ID" \
    --host 127.0.0.1 --port 8000 \
    --dtype bfloat16 --tensor-parallel-size 1 \
    --gpu-memory-utilization "${GPU_MEM_UTIL:-0.92}" \
    --max-model-len "$len" --max-num-seqs 2 \
    --enable-prefix-caching \
    --mamba-ssm-cache-dtype float16 ${MAMBA_ROUNDING_FLAGS} \
    ${MAMBA_BACKEND:+--mamba-backend "$MAMBA_BACKEND"} \
    --reasoning-parser nemotron_v3 \
    ${EXTRA_ARGS:-} >>"$LOG" 2>&1 &
  pid=$!
  for _ in $(seq 1 120); do   # up to 20 min: load ~66 GB and compile
    if curl -sf http://127.0.0.1:8000/v1/models >/dev/null; then
      if ss -ltn | grep ':8000 ' | grep -qv '127.0.0.1:8000'; then echo "port 8000 is bound beyond loopback; stopping" >&2; kill "$pid"; exit 1; fi
      echo "$len" > "$DIR/max_model_len"
      echo "serving $MODEL_ID on 127.0.0.1:8000 (max-model-len $len, pid $pid)"
      curl -s http://127.0.0.1:8000/v1/models; echo
      exit 0
    fi
    kill -0 "$pid" 2>/dev/null || break
    sleep 10
  done
  kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true
  # only a memory error moves to a smaller window (vLLM always logs its config, so match the error text, not the key)
  if grep -qiE "larger than the available KV cache memory|No available memory for the cache blocks|out of memory" "$LOG"; then
    echo "did not fit at $len; trying the next size" >&2; sleep 5; continue
  fi
  echo "vLLM failed for a reason other than memory; last lines of $LOG:" >&2; tail -40 "$LOG" >&2; exit 1
done
echo "no context window in '$LENS' fit; see $LOG" >&2; exit 1
