# Self-hosted Nemotron (30B, our GPU) vs hosted Nemotron (120B, NVIDIA's API)

_Written by `scripts/selfhost/compare.py` from `reviews/<c>/nemotron.json` (Nemotron 3.5 Super 120B-A12B on NVIDIA's hosted API, committed) and `reviews-selfhost/<c>/nemotron.json` (nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 on vLLM, one A100 80GB at Verda). Not the same model: the 120B does not fit one A100. Same prompt, same blind context (unless the row's context was shrunk to the server's window), both single samples at temperature 0.6, so some disagreement is sampling noise._

| Change | Clauses agree | Disagreements (self-hosted vs hosted) | Hosted findings matched | Self-hosted findings matched | Latency hosted / self-hosted (s) | GPU-hours (calls) | Est. cost (calls) | Endpoint |
|---|---|---|---|---|---|---|---|---|
| 2234 | 3/4 | REQ-2234-N1: cannot_determine vs met | 0/5 | 0/0 | 138.7 / 154.7 | 0.043 | $0.10 | 127.0.0.1 (self-hosted) |
| 2283 | 5/5 | none | 0/0 | 0/2 | 101.9 / 91.3 | 0.0254 | $0.06 | 127.0.0.1 (self-hosted) |
| 2129 | 1/1 | none | 0/4 | 0/0 | 149.4 / 62.8 | 0.0174 | $0.04 | 127.0.0.1 (self-hosted) |
| 2297 | 1/1 | none | 0/1 | 0/0 | 101.4 / 31.8 | 0.0088 | $0.02 | 127.0.0.1 (self-hosted) |
| up-2022 | 4/4 | none | 0/1 | 0/0 | 87.1 / 16.3 | 0.0045 | $0.01 | 127.0.0.1 (self-hosted) |
| up-1934 | 3/3 | none | 0/1 | 0/0 | 88.0 / 65.8 | 0.0183 | $0.04 | 127.0.0.1 (self-hosted) |
| up-1967 | 2/2 | none | 0/1 | 0/0 | 48.5 / 13.1 | 0.0036 | $0.01 | 127.0.0.1 (self-hosted) |
| 2234-mut2 | 3/4 | REQ-2234-N2: met vs cannot_determine | 0/1 | 0/0 | 125.0 / 58.0 | 0.0161 | $0.04 | 127.0.0.1 (self-hosted) |
| 2283-mut1 | 4/5 | REQ-2283-N2: met vs cannot_determine | 0/2 | 0/0 | 142.0 / 42.0 | 0.0117 | $0.03 | 127.0.0.1 (self-hosted) |
| 2283-sec1 | 5/5 | none | 0/1 | 0/0 | 94.1 / 80.0 | 0.0222 | $0.05 | 127.0.0.1 (self-hosted) |

**Totals over 10 changes:** clauses agree 31/34; hosted findings also found self-hosted 0/17; self-hosted findings also found hosted 0/2; model wall-clock 10.3 min; GPU-hours in calls 0.17 (est. $0.41).

## Would the pack change?

_Each pack built twice in a scratch workspace, only the nemotron review swapped; trust events ignored. AI recommendation = the tier under the mandate's caps, from the reviews; the final tier also applies the release gate, which holds the 30B (a model version the mandate has not released) at ask. The committed packs use the hosted reviews and are not changed._

- **2234**: AI recommendation ask with the hosted review, ask with the self-hosted one; clauses proven 0 vs 0 of 4; final tier ask vs ask.
- **2283**: AI recommendation ask with the hosted review, ask with the self-hosted one; clauses proven 3 vs 1 of 5; final tier ask vs ask.
- **2129**: AI recommendation block with the hosted review, block with the self-hosted one; clauses proven 1 vs 1 of 1; final tier block vs block.
- **2297**: AI recommendation block with the hosted review, block with the self-hosted one; clauses proven 0 vs 0 of 1; final tier block vs block.
- **up-2022**: AI recommendation ask with the hosted review, notify with the self-hosted one; clauses proven 4 vs 4 of 4; final tier ask vs ask.
- **up-1934**: AI recommendation ask with the hosted review, notify with the self-hosted one; clauses proven 3 vs 3 of 3; final tier ask vs ask.
- **up-1967**: AI recommendation notify with the hosted review, notify with the self-hosted one; clauses proven 2 vs 2 of 2; final tier notify vs ask.
- **2234-mut2**: AI recommendation ask with the hosted review, ask with the self-hosted one; clauses proven 0 vs 0 of 4; final tier ask vs ask; planted line flagged: hosted yes, self-hosted no.
- **2283-mut1**: AI recommendation ask with the hosted review, ask with the self-hosted one; clauses proven 0 vs 0 of 5; final tier ask vs ask; planted line flagged: hosted no, self-hosted no.
- **2283-sec1**: AI recommendation ask with the hosted review, ask with the self-hosted one; clauses proven 0 vs 0 of 5; final tier ask vs ask; planted line flagged: hosted yes, self-hosted no.

## What the box cost

The box existed for 1.13 h with 1 GPU(s): 1.1 GPU-hours x $2.386/GPU-hour = $2.70. That is the bill: it includes provisioning, the model download and idle time, which the per-call numbers above leave out.

Matching: a finding matches if it has the same title or cites the same file within 10 lines. Findings are unverified here; the pack verifies them.

## Self-hosted adjudicator: Gemma 4 31B vs hosted Gemini (written by hand, not by compare.py)

_Same box after the ten reviews: vLLM 0.27.1 serving google/gemma-4-31B-it-qat-w4a16-ct (open weights, W4A16, max-model-len 32768) on 127.0.0.1:8000, reached over the same SSH tunnel. `countersign adjudicate <c> --adjudicator gemma-selfhost` wrote `reviews-selfhost/<c>/adjudication.gemma.json`; Gemini's hosted rulings (`reviews/<c>/adjudication.gemini.json`, gemini-4-hydrogen) were not touched. One sample each, temperature 1.0. Rulings are advisory: an adjudicator can only route to a human, never clear._

The disputes are computed from today's reviews, and some reviews changed after Gemini ran, so the two did not get the same list: 2234 Gemini {REQ-2234-N1, finding:nemotron:N1-crash-remains}, Gemma {REQ-2234-N1, finding:claude:C1}; 2283 both {REQ-2283-N1, finding:claude:C1}. Three disputes are common.

| Dispute | Gemini backs | Gemma backs | Same call? |
|---|---|---|---|
| REQ-2234-N1 | duplicate-key crash fixed (claude, codex, nemotron); an unguarded cast still remains at TypeCollector.cs:985 (claude). Rejects claude's AD0001 probe and codex's "invalid contracts generally don't crash" | duplicate-key crash fixed (codex, nemotron); "a potential crash site remains" (claude). Rejects claude's "crashes on [Key(null)] record parameters" | Yes in substance: fixed for duplicate keys, a residual crash site, the specific crash claim unproven. Gemma accepts codex's broad claim, which Gemini rejects |
| REQ-2283-N1 | the suite passes (codex, nemotron, claude). Rejects "all existing diagnostics keep working" (codex, nemotron) | the suite passes (codex, nemotron). Rejects "all existing diagnostics keep working" (codex) and claude's location-filter claim | Yes: passing tests back "no test regressions", not "no diagnostic regressions" |
| finding:claude:C1 (2283) | ReportIfLocatedInCompilation drops diagnostics not located in a syntax tree (claude). Rejects the Location.None argument | the same drop (claude), plus where MsgPack003 is located. Rejects "base reports MsgPack003, head reports nothing" | Yes on the core claim. Gemma is not consistent across its two 2283 rulings: it backs C1 here and rejects claude's same point under N1 |

Both route every dispute to the area owner; neither tried to clear anything. On the three common disputes Gemma backs the same core claims as Gemini; it differs on side claims (one broad codex claim accepted, one inconsistency between rulings).

| Change | Gemini latency (s) | Gemma latency (s) | Gemma tokens in / out | Gemma GPU-hours | Est. cost |
|---|---|---|---|---|---|
| 2234 | 16.0 | 121.4 | 5,896 / 6,034 | 0.0337 | $0.08 |
| 2283 | 19.9 | 53.0 | 6,339 / 2,637 | 0.0147 | $0.04 |

Gemma total: 0.048 GPU-hours, about $0.12 at $2.386/GPU-hour; it is included in the box bill above.

## Notes from the run

- `hf download --include a b c` fetched only the json/jinja files (no shards); the weights came down with `snapshot_download` (62 GB in about 4 min).
- On the A100 vLLM needed `python3.12-dev` (Triton JIT), the venv's `bin/` on PATH (FlashInfer's ninja), and no `--enable-mamba-cache-stochastic-rounding` / `--mamba-cache-philox-rounds` (`cvt.rs` is not supported on sm_80). With those, Nemotron served at max-model-len 131072, the hosted settings unchanged.
- Gemma 4 needed transformers 5.8.0 (5.23.0 breaks vLLM 0.27.1's config reader on per-layer head_dim).
- 2283's first review was cut off by a restart of our container; it was run again (only the saved run counts).
- Box hours are 10:29Z (create) to 11:37Z (release requested on the team board). Verda bills until the infra agent deletes the instance, so the real bill may be slightly higher.
