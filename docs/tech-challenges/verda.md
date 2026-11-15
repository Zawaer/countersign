# Best use of Verda: the reviewer that never leaves Europe

**The fit.** Clients' code is often confidential. In **Countersign** (deterministic checks, then AI reviewers, then a
named human countersigns what the AI could not prove), a `confidential` mandate lets only open-weights reviewers read
the code, and only on a server we run. On Verda that is a real endpoint: it listens on 127.0.0.1 only, we reach it
through an SSH tunnel, `--confidential` refuses every vendor endpoint before sending anything, and every review
records `endpoint_host: 127.0.0.1`, `self_hosted: true`.

**The trade-off, measured** (`measurement/selfhost.md`). The self-hosted 30B agrees with the hosted 120B on
**31/34 clause verdicts** but finds **0/17 of its findings** (it wrote 2 of its own in ten reviews). So confidential
mode keeps the verdict, and the release gate holds the 30B at `ask`. Spending more GPU (a 120B needs 2x H100 or one
H200) is a budget choice, not a technical one.

**What ran.**
- One A100 80GB, vLLM 0.27.1, **Nemotron 3.5 Lightning 30B-A3B** (BF16, open weights), 131k context: the smaller
  sibling of the **Super 120B** we call on NVIDIA's API, which doesn't fit one A100.
- Ten blind reviews (4 real changes, 3 upstream controls, 3 seeded defects) into `reviews-selfhost/`.
- Then **Gemma 4 31B** (W4A16) on the same box as the self-hosted adjudicator.

**More results**
- Planted line flagged on the seeded changes: 0 of 3 (hosted: 2 of 3)
- Gemma backed the same core claims as hosted Gemini on the 3 disputes both ruled on
- Median latency 60 s per review vs 102 s hosted

**Cost.** Logged as GPU time, not tokens: wall-clock x $2.386 per GPU-hour, marked as an estimate.
- Model time: 0.17 GPU-hours (≈ $0.41, about $0.04 per review); Gemma 0.05 h (≈ $0.12)
- Box bill, setup and idle included: 1.13 h = $2.70; the A100 was released right after the run

Code: github.com/Zawaer/countersign (`scripts/selfhost/`, `countersign/llm.py`)
