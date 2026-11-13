# Countersign replay results

Every number says whether it is simulated. Minutes are always a model estimate (see the mandate's `measurement` block).

| Change | Tier | Score | Routed to human | Proven/refused | Why | Caught by | Full read min | With pack min | Simulated |
|---|---|---:|---|---|---|---|---:|---:|---|
| 2129 | block | 145.2 | yes | 0/1 | risk score risk | - | 114.3 | 26 | False |
| 2234 | ask | 67.6 | yes | 3/1 | verified finding claude:C1; refused clause REQ-2234-N1; reviewer refusal claude; reviewer refusal claude; reviewer refusal nemotron; reviewer refusal nemotron; reviewer refusal nemotron; reviewer refusal nemotron; risk score risk | - | 26.2 | 44 | False |
| 2283 | ask | 41.1 | yes | 0/5 | verified finding claude:C1; refused clause REQ-2283-F1; refused clause REQ-2283-F2; refused clause REQ-2283-F3; refused clause REQ-2283-N1; refused clause REQ-2283-N2; reviewer refusal claude; reviewer refusal claude; reviewer refusal codex; risk score risk | - | 23.0 | 35 | False |
| 2297 | block | 64.5 | yes | 0/1 | mandate rule split-large-change | - | 260.8 | 22 | False |

- Not replayed: 2129-mut1: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2129-mut2: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2234-mut1: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2234-mut2: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2234-mut3: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2234-mut4: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2234-mut5: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2234-mut6: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2234-mut7: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2283-mut1: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2283-mut2: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2283-mut3: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2283-mut4: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2283-mut5: no reviews yet (stage 2 not run); excluded from every metric

## Seeded defects (facts only; AI reviews pending)

| Mutant | Kind | Caught by checks | Failed checks | Tier (no reviews) | Original's tier | Attributable signal (vs original) | Reviews |
|---|---|---|---|---|---|---|---|
| 2129-mut1 | off-by-one | yes | tests.targeted, tests.full_suite | block | block | mandated-check-failed | pending |
| 2129-mut2 | wrong key kind | yes | tests.execution_full_suite | block | block | - | pending |
| 2234-mut1 | removed guard | yes | tests.targeted, tests.full_suite | block | ask | mandated-check-failed | pending |
| 2234-mut2 | removed guard | **no** | - | ask | ask | - | pending |
| 2234-mut3 | removed guard | yes | tests.targeted, tests.full_suite | block | ask | mandated-check-failed | pending |
| 2234-mut4 | swallowed diagnostic | yes | tests.targeted, tests.full_suite | block | ask | mandated-check-failed | pending |
| 2234-mut5 | inverted condition | yes | tests.full_suite | ask | ask | - | pending |
| 2234-mut6 | wrong key kind | yes | tests.targeted, tests.full_suite | block | ask | mandated-check-failed | pending |
| 2234-mut7 | off-by-one | yes | tests.full_suite | ask | ask | - | pending |
| 2283-mut1 | removed guard | **no** | - | notify | notify | - | pending |
| 2283-mut2 | removed guard | yes | tests.targeted, tests.full_suite | block | notify | mandated-check-failed | pending |
| 2283-mut3 | inverted condition | yes | tests.full_suite | ask | notify | risk 33.1 -> 58.1 (failed: tests.full_suite) | pending |
| 2283-mut4 | swallowed diagnostic | yes | tests.full_suite | ask | notify | risk 33.1 -> 58.1 (failed: tests.full_suite) | pending |
| 2283-mut5 | removed guard | **no** | - | notify | notify | - | pending |

| Metric | Value | Simulated | How |
|---|---|---|---|
| seeded_defects | 0 | False | mutants found as evidence/<change>-mutK |
| catch_rate | None | False | share of seeded defects routed to a human (ask/block) instead of AI-cleared |
| catch_rate_attributable | None | False | share routed to a human by a specific signal (failing check, verified finding, hard rule, refused clause) that the unmutated original did not raise |
| caught_by_checks_alone | 11 of 14 | False | seeded defects where a deterministic check failed (no AI involved; includes mutants without reviews) |
| missed_defects | [] | False | seeded defects the AI would have cleared |
| share_routed_to_humans | 1.0 | False | real changes (not mutants) at ask/block |
| findings_per_reviewer | claude: 13 verified, 0 rejected, 10 refusals; codex: 0 verified, 0 rejected, 3 refusals; nemotron: 5 verified, 0 rejected, 4 refusals | False | verified vs rejected (unsupported) findings over all replayed changes |
| human_minutes_full_read | 424.3 | True | reading-speed model in the mandate: lines/min + minutes per file |
| human_minutes_with_pack | 127 | True | pack reading time by tier + per refused item + per verified finding |
| review_time_saved_share | 0.7 | True | 1 - with_pack / full_read |
| escapes_recorded | 0 | False | escape events in the ledger |
| spotcheck_agreement | None | False | agreeing spot-checks / all spot-checks in the ledger |
| seeded_defects_total | 14 | False | every evidence/<change>-mutK, with or without reviews |
| seeded_routed_to_human_before_review | {'routed': 12, 'attributable': 8, 'of': 14} | False | facts only (no reviews): mutants at ask/block; attributable = a hard rule fired, or the tier rose, versus the unmutated original routed the same way |
| reviewer_cross_check | {'claude': {'major_raised_verified': 4, 'confirmed_by_another': 0, 'missed_others_verified_major': 0}, 'codex': {'major_raised_verified': 0, 'confirmed_by_another': 0, 'missed_others_verified_major': 4}, 'nemotron': {'major_raised_verified': 0, 'confirmed_by_another': 0, 'missed_others_verified_major': 1}} | False | blocker/major findings: raised and verified, confirmed by another reviewer (shared anchor), and other reviewers' verified ones this reviewer did not raise |
| time_per_change | {'2129': {'full_read_min': 114.3, 'with_pack_min': 26, 'saved_min': 88.3}, '2234': {'full_read_min': 26.2, 'with_pack_min': 44, 'saved_min': -17.8}, '2283': {'full_read_min': 23.0, 'with_pack_min': 35, 'saved_min': -12.0}, '2297': {'full_read_min': 260.8, 'with_pack_min': 22, 'saved_min': 238.8}} | True | reading model; negative = the pack costs more than reading the diff (small changes) |
| model_tokens_per_change | {'2283': 173450, '2234': 173450, '2129': 173450, '2297': 173450} | False | measurement/costs.yaml; estimates where the row says so |
