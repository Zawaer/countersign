# Best use of Verda: the reviewer that never leaves Europe

**Countersign** reviews agent-written changes under a signed mandate: deterministic checks first, then AI
reviewers, and a named human countersigns whatever the AI could not prove.

**Why self-hosting is the point.** Tieto's clients' code is often confidential. A mandate marked `confidential`
lets only open-weights reviewers read the code, and only on a server we run. Before Verda that rule had no server
behind it. Now the code goes over SSH to a GPU we rent from Verda, a European cloud, and nowhere else.

**What ran.**
- One A100 80GB on Verda with vLLM 0.27.1, serving **Nemotron 3.5 Lightning 30B-A3B** (BF16, open weights). The
  server listens on 127.0.0.1 only. We reach it through an SSH tunnel, so no port is open and no key is needed.
- It is the smaller sibling of the **Nemotron 3.5 Super 120B** we call on NVIDIA's hosted API. The 120B doesn't fit
  one A100 (its FP8/NVFP4 checkpoints need Hopper or Blackwell): this compares 30B on our GPU with 120B hosted.
- `countersign review-llm <change> --reviewer nemotron-selfhost --confidential` refuses every vendor endpoint before
  sending anything, including a "self-hosted" URL that points at NVIDIA. It accepts ours; each review
  records `endpoint_host: 127.0.0.1` and `self_hosted: true`.
- Ten blind reviews: the 4 real changes, 3 upstream controls and 3 seeded defects. They went to `reviews-selfhost/`,
  so the committed packs did not change.

**Results** (`measurement/selfhost.md`)
- Clause verdicts that match the hosted 120B: TODO/TODO
- Hosted findings the 30B also found: TODO/TODO
- Planted line flagged on the seeded changes: TODO of 3 (hosted: TODO of 3)
- In the nemotron slot the 30B holds at `ask` until it passes the seeded-defect set (release gate).

**Cost.** Each call is logged as GPU time, not tokens: `provider: verda`, `gpu: A100 80GB x1`, wall-clock x $2.39 per
GPU-hour, marked as an estimate.
- Model time: TODO GPU-hours (≈ $TODO) for ten reviews
- Box bill from create to delete, setup and idle included: TODO h = $TODO
- Hosted NVIDIA free tier: $0, rate-limited, and the code leaves our hands

**What we learned.** A confidentiality rule needs a real endpoint. Self-hosting picks the model
for you: what fits one A100 is the 30B. A 120B self-hosted reviewer needs 2x H100 or one H200. That is a
budget choice, not a technical limit.

Code: github.com/Zawaer/countersign (`scripts/selfhost/`, `countersign/llm.py`)
