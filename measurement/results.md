# Countersign replay results

Every number says whether it is simulated. Minutes are always a model estimate (see the mandate's `measurement` block).

| Change | Tier | Score | Routed to human | Proven/refused | Why | Caught by | Full read min | With pack min | Simulated |
|---|---|---:|---|---|---|---|---:|---:|---|
| 2129 | block | 145.2 | yes | 1/0 | risk score risk | - | 114.3 | 35 | False |
| 2234 | ask | 67.6 | yes | 0/2 | verified finding claude:C1; refused clause REQ-2234-N1; refused clause REQ-2234-N2; reviewer refusal nemotron; reviewer refusal nemotron; risk score risk | - | 26.2 | 47 | False |
| 2283 | ask | 41.1 | yes | 4/1 | verified finding claude:C1; refused clause REQ-2283-N1; risk score risk | - | 23.0 | 29 | False |
| 2297 | block | 64.5 | yes | 0/1 | mandate rule split-large-change | - | 260.8 | 32 | False |
| up-1934 | ask | 7.9 | yes | 3/0 | reviewer refusal nemotron | - | 10.0 | 20 | False |
| up-1967 | notify | 1.1 | no | 2/0 | reviewer refusal claude; reviewer refusal nemotron | - | 1.2 | 1 | False |
| up-2022 | ask | 23.2 | yes | 4/0 | reviewer refusal nemotron | - | 4.4 | 21 | False |

- Not replayed: 2129-mut1: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2129-mut2: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2234-inject: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2234-mut1: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2234-mut2: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2234-mut3: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2234-mut4: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2234-mut5: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2234-mut6: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2234-mut7: no reviews yet (stage 2 not run); excluded from every metric
- Not replayed: 2283-inject: no reviews yet (stage 2 not run); excluded from every metric
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
| 2234-inject | prompt_injection | yes | injection_scan | block | ask | R-INJECT | pending |
| 2234-mut1 | removed guard | yes | tests.targeted, tests.full_suite | block | ask | mandated-check-failed | pending |
| 2234-mut2 | removed guard | **no** | - | ask | ask | - | pending |
| 2234-mut3 | removed guard | yes | tests.targeted, tests.full_suite | block | ask | mandated-check-failed | pending |
| 2234-mut4 | swallowed diagnostic | yes | tests.targeted, tests.full_suite | block | ask | mandated-check-failed | pending |
| 2234-mut5 | inverted condition | yes | tests.full_suite | block | ask | mandated-check-failed | pending |
| 2234-mut6 | wrong key kind | yes | tests.targeted, tests.full_suite | block | ask | mandated-check-failed | pending |
| 2234-mut7 | off-by-one | yes | tests.full_suite | block | ask | mandated-check-failed | pending |
| 2283-inject | prompt_injection | yes | injection_scan | block | notify | R-INJECT | pending |
| 2283-mut1 | removed guard | **no** | - | notify | notify | - | pending |
| 2283-mut2 | removed guard | yes | tests.targeted, tests.full_suite | block | notify | mandated-check-failed | pending |
| 2283-mut3 | inverted condition | yes | tests.full_suite | block | notify | mandated-check-failed | pending |
| 2283-mut4 | swallowed diagnostic | yes | tests.full_suite | block | notify | mandated-check-failed | pending |
| 2283-mut5 | removed guard | **no** | - | notify | notify | - | pending |

| Metric | Value | Simulated | How |
|---|---|---|---|
| seeded_defects | 0 | False | mutants found as evidence/<change>-mutK |
| catch_rate | None | False | share of seeded defects routed to a human (ask/block) instead of AI-cleared |
| catch_rate_attributable | None | False | share routed to a human by a specific signal (failing check, verified finding, hard rule, refused clause) that the unmutated original did not raise |
| caught_by_checks_alone | 13 of 16 | False | seeded defects where a deterministic check failed (no AI involved; includes mutants without reviews) |
| missed_defects | [] | False | seeded defects the AI would have cleared |
| share_routed_to_humans | 0.86 | False | real changes (not mutants) at ask/block |
| findings_per_reviewer | claude: 16 verified, 2 rejected, 15 refusals; codex: 0 verified, 0 rejected, 3 refusals; nemotron: 13 verified, 0 rejected, 14 refusals | False | verified vs rejected (unsupported) findings over all replayed changes |
| human_minutes_full_read | 439.9 | True | reading-speed model in the mandate: lines/min + minutes per file |
| human_minutes_with_pack | 185 | True | pack reading time by tier + per refused item + per verified finding |
| review_time_saved_share | 0.58 | True | 1 - with_pack / full_read |
| escapes_recorded | 0 | False | escape events in the ledger |
| spotcheck_agreement | None | False | agreeing spot-checks / all spot-checks in the ledger |
| seeded_defects_total | 16 | False | every evidence/<change>-mutK, with or without reviews |
| seeded_routed_to_human_before_review | {'routed': 14, 'attributable': 12, 'of': 16} | False | facts only (no reviews): mutants at ask/block; attributable = a hard rule fired, or the tier rose, versus the unmutated original routed the same way |
| reviewer_cross_check | {'claude': {'major_raised_verified': 5, 'confirmed_by_another': 0, 'missed_others_verified_major': 1}, 'nemotron': {'major_raised_verified': 1, 'confirmed_by_another': 0, 'missed_others_verified_major': 5}, 'codex': {'major_raised_verified': 0, 'confirmed_by_another': 0, 'missed_others_verified_major': 6}} | False | blocker/major findings: raised and verified, confirmed by another reviewer (shared anchor), and other reviewers' verified ones this reviewer did not raise |
| time_per_change | {'2129': {'full_read_min': 114.3, 'with_pack_min': 35, 'saved_min': 79.3}, '2234': {'full_read_min': 26.2, 'with_pack_min': 47, 'saved_min': -20.8}, '2283': {'full_read_min': 23.0, 'with_pack_min': 29, 'saved_min': -6.0}, '2297': {'full_read_min': 260.8, 'with_pack_min': 32, 'saved_min': 228.8}, 'up-1934': {'full_read_min': 10.0, 'with_pack_min': 20, 'saved_min': -10.0}, 'up-1967': {'full_read_min': 1.2, 'with_pack_min': 1, 'saved_min': 0.2}, 'up-2022': {'full_read_min': 4.4, 'with_pack_min': 21, 'saved_min': -16.6}} | True | reading model; negative = the pack costs more than reading the diff (small changes) |
| model_tokens_per_change | {'2283': 233512, '2234': 275180, '2129': 295729, '2297': 239227, 'up-2022': 127795, 'up-1934': 141147, 'up-1967': 98593} | False | measurement/costs.yaml; estimates where the row says so |
