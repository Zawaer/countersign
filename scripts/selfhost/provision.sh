#!/usr/bin/env bash
# ON THE GPU BOX (Verda, 1x A100 80GB, Ubuntu, as root). Installs a pinned vLLM and downloads Nemotron 3.5 Lightning
# 30B-A3B (BF16, ~66 GB) at a pinned revision. Opens no port and stores no secret.
#
#   scp -i /data/work/ssh/verda scripts/selfhost/{provision,serve}.sh root@$VERDA_HOST:
#   ssh -i /data/work/ssh/verda root@$VERDA_HOST 'bash provision.sh'
#
# Why this model: the hosted reviewer is Nemotron 3.5 Super 120B-A12B. In BF16 it needs ~240 GB, and its 4-bit and
# 8-bit checkpoints (NVFP4/FP8) need Hopper or Blackwell; an A100 has neither. Lightning 30B-A3B is the official
# smaller sibling (same family, chat template and reasoning switch), BF16, validated by NVIDIA on one A100 80GB.
set -euo pipefail

VLLM_VERSION="${VLLM_VERSION:-0.27.1}"   # the version the model card's recipes name (vllm/vllm-openai:v0.27.1)
MODEL="${MODEL:-nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16}"
REVISION="${REVISION:-a9904d24bcc1d289a1950fa9d2b978c47cf903b9}"  # main on 2026-08-24; not gated, no HF token needed
DIR="${SELFHOST_DIR:-$HOME/selfhost}"

nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
free_gb=$(df -BG --output=avail "$HOME" | tail -1 | tr -dc 0-9)
if [ "$free_gb" -lt 100 ]; then echo "need >= 100 GB free in $HOME for the model and vLLM (have ${free_gb} GB)" >&2; exit 1; fi

mkdir -p "$DIR"
command -v uv >/dev/null || { curl -LsSf https://astral.sh/uv/install.sh | sh; }
export PATH="$HOME/.local/bin:$PATH"
[ -x "$DIR/venv/bin/python" ] || uv venv --python 3.12 "$DIR/venv"
uv pip install --python "$DIR/venv/bin/python" "vllm==$VLLM_VERSION" "huggingface_hub[hf_transfer]"

# Download only the weights, tokenizer and template (skip the images in the repo).
HF_HUB_ENABLE_HF_TRANSFER=1 "$DIR/venv/bin/hf" download "$MODEL" --revision "$REVISION" --local-dir "$DIR/model" \
  --include "*.safetensors" "*.json" "*.jinja" "LICENSE"
du -sh "$DIR/model"
"$DIR/venv/bin/python" -c "import vllm, torch; print('vllm', vllm.__version__, 'torch', torch.__version__, 'cuda', torch.cuda.is_available())"
echo "provisioned: $MODEL@$REVISION in $DIR/model; next: bash serve.sh"
