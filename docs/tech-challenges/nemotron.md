# Best use of Nemotron: the reviewer that caught the hidden security downgrades

**Best result.** We hid two quiet security downgrades inside otherwise reasonable fixes ([BENCHMARK.md](../BENCHMARK.md)).
Reviewing blind, Nemotron flagged both on the exact line with verified findings (<!--n:bench_downgrades_flagged-->2<!--/n--> of <!--n:bench_downgrades-->2<!--/n-->): a blocker on
`HashCollisionResistant = false`, and a major on a depth limit raised 500 to 5000 that passes every test. The tests
caught <!--n:bench_downgrades_tests_caught-->1<!--/n--> of <!--n:bench_downgrades-->2<!--/n-->. On a third seeded downgrade (`2283-sec1`) every check passed and its blind review still
pointed at the planted line.

**Model.** Nemotron 3.5 Super VL (`nvidia/nemotron-3.5-super-vl-120b-a12b`, 120B, 12B active) runs live in CI on
every change via NVIDIA's API: all <!--n:real_changes-->8<!--/n--> real changes, <!--n:seeded_reviewed-->17<!--/n--> seeded ones, <!--n:bench_variants-->8<!--/n--> fix variants. Nemotron 3.5 Lightning
30B is the self-hosted variant, on a Verda A100 ([verda.md](verda.md)).

**What it does.** One of three reviewers (with Claude and Codex) judging each clause against the diff. A clause is
proven only if all three say met with verified evidence.

**Why it matters.**
- **The only reviewer family allowed on confidential code.** A repo marked confidential may use only open-weights
  reviewers, so Lightning 30B reads it on our own server and nothing goes to a vendor.
- **A different vendor disagrees differently.** It flagged the planted line in <!--n:nemotron_seeded_flagged-->13<!--/n--> of <!--n:nemotron_seeded_of-->15<!--/n--> seeded changes, and in
  <!--n:nemotron_survivors_flagged-->3<!--/n--> of the <!--n:nemotron_survivors_reviewed-->4<!--/n--> that passed every check.

**How we improved its outputs.**
- **Strict JSON schema, one repair turn**; fences and `<think>` stripped.
- **Machine-verified citations**: <!--n:nemotron_verified-->63<!--/n--> findings verified, <!--n:nemotron_rejected-->1<!--/n--> rejected.
- **Blind context**: seeding notes and benchmark keys stripped; the runner refuses a context that names them.
- **Room to finish**: `max_tokens` 32k, since 16k cut reviews off.
- **A "what you were not given" list**, so it refuses instead of guessing (<!--n:nemotron_refusals-->48<!--/n--> refusals, shown to the owner).
- **Unanimity**: on 2283 it said met while Claude's reproduced objection stood; the clause stayed refused.

**Limits.** The owner accepted <!--n:nemotron_accepted-->8<!--/n--> of the <!--n:nemotron_rated-->10<!--/n--> findings he rated. It missed one surviving mutant and called
one variant a root-cause fix although the bug does not occur on that base.

**Cost.** <!--n:nemotron_call_min_k-->38<!--/n--> to <!--n:nemotron_call_max_k-->71<!--/n-->k tokens per review call; $0 on NVIDIA's free tier, logged in `measurement/costs.yaml`.

Code: github.com/Zawaer/countersign (`countersign/llm.py`, `reviews/*/nemotron.json`)

<sub>2,363 characters</sub>
