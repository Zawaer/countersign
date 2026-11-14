# Gemma: the adjudicator for code that can't leave the building

**Countersign** reviews agent-written changes: deterministic checks, AI reviewers, and a named human countersigns
what the AI could not prove. When reviewers disagree, an adjudicator rules on each dispute. It is advisory by
construction: it can only route to a human, never clear.

**Why open weights matter here.** Our hosted adjudicator is Gemini. For confidential code, a vendor API is not an
option: the code may only go to a model on a server we run. Gemma is Google's open-weights answer to that: the same
role, on our own GPU, with the code never leaving an SSH tunnel.

**What ran.**
- `google/gemma-4-31B-it-qat-w4a16-ct` (4-bit weights, so a 31B fits easily) on vLLM 0.27.1, one A100 80GB at
  Verda, 32k context, listening on 127.0.0.1 only.
- A `gemma-selfhost` preset in `countersign/llm.py`: no API key, GPU wall-clock logged as cost, output to
  `reviews-selfhost/<change>/adjudication.gemma.json` so Gemini's hosted rulings stay as they are.
- `countersign adjudicate 2234 2283 --adjudicator gemma-selfhost`, on the same disputes the pack shows.

**Results** (`measurement/selfhost.md`)
- 3 disputes were ruled on by both Gemma and hosted Gemini. On all 3 Gemma backed the same core claims: the
  duplicate-key crash is fixed but a crash site remains (2234); passing tests prove "no test regressions", not "no
  diagnostic regressions" (2283); the location filter does drop diagnostics (2283, Claude's C1).
- It differed on side claims: it accepted one broad claim Gemini rejected, and on 2283 it backed C1 in one ruling
  while rejecting the same point in another.
- Both routed every dispute to the area owner; neither tried to clear anything.

**Cost.** 0.048 GPU-hours, about $0.12 at $2.386 per A100-hour, for both adjudications (121 s and 53 s; hosted
Gemini took 16 s and 20 s).

**Limit.** The signed mandate lists Gemini as its only adjudicator, marked not self-hostable, so a confidential change
still runs without one. Using Gemma there takes one registry line, `self_hostable: true`, signed by the owner.
Countersign does not grant that in code.

Code: github.com/Zawaer/countersign (`countersign/llm.py`, `measurement/selfhost.md`)
