# Best use of Verda: the reviewer that never leaves Europe

**Countersign** reviews agent-written changes under a signed mandate: deterministic checks first, then AI
reviewers, and a named human countersigns whatever the AI could not prove.

**Why self-hosting is the point.** Clients' code is often confidential. A `confidential` mandate lets only
open-weights reviewers read it, and only on a server we run. Now the code goes over SSH to a GPU we rent from
Verda, a European cloud, and nowhere else.

**What ran.**
- One A100 80GB, vLLM 0.27.1, **Nemotron 3.5 Lightning 30B-A3B** (BF16, open weights), 131k context. It listens on
  127.0.0.1 only; we reach it through an SSH tunnel, so no port is open and no key is needed.
- It is the smaller sibling of the **Super 120B** we call on NVIDIA's API, which doesn't fit one A100: this compares
  30B on our GPU with 120B hosted.
- `review-llm --reviewer nemotron-selfhost --confidential` refuses every vendor endpoint before sending anything.
  Each review records `endpoint_host: 127.0.0.1`, `self_hosted: true`.
- Ten blind reviews (4 real changes, 3 upstream controls, 3 seeded defects) into `reviews-selfhost/`.
- Then **Gemma 4 31B** (W4A16) on the same box as the self-hosted adjudicator.

**Results** (`measurement/selfhost.md`)
- Clause verdicts that match the hosted 120B: 31/34
- Hosted findings the 30B also found: 0/17 (it wrote 2 in ten reviews)
- Planted line flagged on the seeded changes: 0 of 3 (hosted: 2 of 3)
- Gemma backed the same core claims as hosted Gemini on the 3 disputes both ruled on
- The 30B holds at `ask` until it passes the seeded-defect set (release gate)

**Cost.** Logged as GPU time, not tokens: wall-clock x $2.386 per GPU-hour, marked as an estimate.
- Model time: 0.17 GPU-hours (≈ $0.41) for ten reviews, median 60 s vs 102 s hosted; Gemma 0.05 h (≈ $0.12)
- Box bill, setup and idle included: 1.13 h = $2.70

**What we learned.** A confidentiality rule needs a real endpoint, and self-hosting picks the model for you. The
30B agrees on verdicts but finds almost nothing: a confidential-mode floor, not a replacement. A 120B needs 2x H100
or one H200. That is a budget choice, not a technical limit.

Code: github.com/Zawaer/countersign (`scripts/selfhost/`, `countersign/llm.py`)
