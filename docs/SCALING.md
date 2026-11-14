# How would this scale?

Short answer: on small changes Countersign costs the owner more reading time than the diff, and on this repo it still routes most changes to a human. What scales is the rest: the machine cost per change is bounded and linear, a change the AI can prove costs no human time, large changes get cheaper to review, and every decision has a name on it. Every number below links to its source. **Simulated** numbers are labelled.

## What one change costs today (measured)

**Model tokens per change** ([measurement/costs.yaml](../measurement/costs.yaml), rendered in [COSTS.md](COSTS.md)):

| Reviewer | Tokens per change | Metered? | Price |
|---|---|---|---|
| Nemotron (CI job) | One review call: 8.7k on a 1-line docs fix (up-1967), 38k to 68k on everything from 2 to 237 files. A JSON repair turn added 45k to 54k on 2 of 4 agent changes | yes, the API's `usage` field, per change | $0 (NVIDIA free tier, about 40 requests/min) |
| Codex | about 126k (two passes) on the agent changes, 90k on the controls | no: run summaries, split evenly over the changes in a run | unknown (OpenAI credits) |
| Claude | about 48k (v1 pass); later passes not recorded | no: one usage report for four changes; three runs unknown | unknown (subscription) |

All reviewers together: 234k to 296k tokens per agent-written change, 99k to 141k per upstream control. Tokens do not grow with the diff: the reviewer context is capped at 180k characters, about 50k tokens (`DEFAULT_CONTEXT_CHARS` in `countersign/llm.py`), and what does not fit is listed in the pack as not given. 2297 (237 files) used fewer Nemotron tokens than 2129 (28 files).

**CI minutes on CRACI** (job start and end times from `gh run view <id> -R Zawaer/countersign --json jobs`, runs listed in `costs.yaml`):

| Job | Measured | Run |
|---|---|---|
| `pipeline` (tests, ledger, routing, rebuild every pack; 4 vCPU) | 23 to 31 s per run, for all changes | 43530101073, 43530175195, 43531874491, 43546838730 |
| `reviewers`, Nemotron (2 vCPU) | 2.7 min for 2234 alone; 4.1 min for three small controls; 32.2 min for 16 seeded changes (2.0 min each) | 43530175195, 43531874491, 43546838730 |
| `facts`, .NET 8 + 9 build and tests, fail-without-fix (8 vCPU) | 2.9 min for 2234 (the only change run on CRACI) | 43530403169 |

**Push to pack.** With recorded inputs, a pull request in the demo repo gets its pack comment and `countersign/tier` status 21 s after the event (run 43554119253 on Zawaer/countersign-messagepack-demo, GitHub-hosted runner). Live on CRACI, the measured jobs for 2234 add up to about 6 minutes (facts 2.9 + Nemotron 2.7 + pipeline 0.4). We have not run that chain end to end in one run, and the Claude and Codex review times were not recorded.

**Small versus large.** The machine cost barely changes with size. The human cost does. Reading-model minutes, **simulated** ([MEASUREMENT.md](MEASUREMENT.md)): the pack is slower than the diff on 2234 (47 vs 26 min), 2283 (29 vs 23), up-1934 (20 vs 10) and up-2022 (21 vs 4). It is faster on 2129 (35 vs 114) and 2297 (32 vs 261).

## Where human attention goes

- **History (real):** 85 of 109 merged upstream PRs go to a human under mandate v6 (same as v2 and v4), with upstream CI credited ([history results](../measurement/history/results.json)). The 24 the AI would clear include none of the 11 escapes (0 of 24 still allows up to about 12%). The cleared PRs are the small ones: about 552 of 8256 full-read minutes (7%, simulated reading model).
- **What drives that 78%:** of the 85 routed PRs, 66 hit a hard rule and 17 a risk score of 40 or more. Only 2 are held by an area's clearance cap alone. The rules are source changed without a test change (34), public API changed (31), a mandated check missing (15) and more than 50 files (7). On this repo the share is set by test and API discipline, not by how much the AI is trusted.
- **Real changes:** 6 of 7 go to a human. Only the one-line docs fix up-1967 is cleared (`notify`).
- **Over time (simulated, 200 runs x 52 weeks, [simulation/results.json](../measurement/simulation/results.json)):** every area starts on probation. The share routed starts at 73% and falls to about 62% as areas earn clearance around weeks 10 to 12. Human minutes per week drop from 652 to 549, against 710 for a full human review (23% less). Escapes do not rise (0.13 vs 0.16 a week). This assumes the pack saves nothing on a read. **Drift (simulated):** when reviewers start agreeing with everything at week 26, escapes rise to 0.23 a week under the written restore rule. With weekly canaries they return to 0.18 (baseline 0.17), because trust is withdrawn: the routed share climbs to 95% and minutes to 687 a week. Humans pay for bad reviewers, by design.

## The honest claim

1. **Only what can't be proven goes to a human.** The share that goes to a human falls only where an area earns `notify` or `silent` and changes come with tests. Trust takes about 11 points off it in the simulation (73% to 62%). Test discipline is the bigger lever on the history.
2. **Every decision is accountable and auditable at no extra human cost.** The pack, its hash, the tier with its reason, and the ledger entry are all machine work. The owner's part is one signed command at the end of a read they would do anyway. For AI-cleared changes, the accountable person is the owner who delegated that clearance in the signed mandate.
3. **Large changes are where the pack saves reading time** (2297: 32 vs 261 min, simulated), and changes over 50 files are blocked and split before anyone reads them.
4. **Cost per change is tokens plus CI minutes, bounded and linear:** at most about 50k context tokens per reviewer call, 1 or 2 calls per reviewer, about 2 to 3 reviewer minutes and 3 facts minutes on CRACI. A busy repo outgrows the free Nemotron tier (40 requests/min) and needs a paid or self-hosted endpoint.

**What it doesn't solve:** reading time on small changes; intent and bad requirements; areas without checks (UI, performance, other targets) fall back to humans; reviewers share blind spots. It is also not yet shown with a real stopwatch or a real countersignature. The ledger holds four mandate versions and no sign-off.

## How a team adopts it

- **One signed mandate per repo.** Areas are CODEOWNERS-style globs (first match wins), each with an owner, a sensitivity, its checks and the most the AI may clear alone (`max_ai_tier`). [mandate/messagepack.mandate.yaml](../mandate/messagepack.mandate.yaml) has 7 areas and 2 owners. Adding a team means adding an area and re-signing.
- **Start strict.** Put every area on probation, as the simulation does, and let it climb: `notify` after 20 agreeing spot-checks in a row, `silent` after 40. Raise caps only by a signed mandate change.
- **Reviewers are CI jobs.** The same `reviewers` job runs per change. For a confidential repo (`confidential: true`), only reviewers marked `self_hostable` may read the code. Today that is Nemotron (open weights). Point `COUNTERSIGN_NEMOTRON_BASE_URL` at your own server; we have not run one ([CI.md](CI.md)).
- **The seeded set is the release gate.** A new model or prompt version holds every area at `ask` until it catches the seeded set (`trust.release_gate`, min catch rate 1.0). The same set runs as weekly canaries: 2 per area.
- **What has to exist first:** requirement IDs in tickets (ours are placeholders, `official: false`); tests that fail without the fix (fail-without-fix is a mandated check, and missing tests drove 34 of 85 routed history PRs); and a merge gate that only a Countersign App can turn green (open item T1).

## Three numbers for a slide

1. **24 of 109 real PRs cleared by the AI, 0 of 11 escapes among them** (real; [measurement/history/results.json](../measurement/history/results.json)).
2. **38k to 68k tokens and about 2 CI minutes per review, from 2 to 237 files** (measured; Nemotron rows in [measurement/costs.yaml](../measurement/costs.yaml), CRACI runs 43546838730 and 43530175195).
3. **23% fewer human minutes a week with escapes not rising: 549 vs 710 min, 0.13 vs 0.16 escapes** (simulated; [measurement/simulation/results.json](../measurement/simulation/results.json)).
