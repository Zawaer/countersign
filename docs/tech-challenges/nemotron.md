# Best use of Nemotron: the open-weights reviewer that checks the others

**Model.** Nemotron 3.5 Super VL (`nvidia/nemotron-3.5-super-vl-120b-a12b`, 120B total, 12B active), via NVIDIA's
OpenAI-compatible API from CI.

**What it does.** In Countersign it is the third reviewer beside Claude and Codex, live on all <!--n:real_changes-->7<!--/n--> real changes. A clause
is proven only if all three say met with verified evidence. It also reviews blind: <!--n:seeded_reviewed-->17<!--/n--> seeded changes and <!--n:bench_variants-->8<!--/n--> fix
variants of the same issues.

**Why it matters.**
- A different vendor disagrees differently. It flagged the planted line in <!--n:nemotron_seeded_flagged-->13<!--/n--> of the <!--n:nemotron_seeded_of-->15<!--/n--> seeded changes it reviewed,
  and in <!--n:nemotron_survivors_flagged-->3<!--/n--> of the <!--n:nemotron_survivors_reviewed-->4<!--/n--> that passed every check.
- It flagged both hidden security downgrades on the exact line (<!--n:bench_downgrades_flagged-->2<!--/n--> of <!--n:bench_downgrades-->2<!--/n-->), including a depth limit raised 500 to
  5000 that passes every test. The tests caught <!--n:bench_downgrades_tests_caught-->1<!--/n--> of <!--n:bench_downgrades-->2<!--/n-->.
- Open weights: a repo marked confidential may use only self-hostable reviewers, so Nemotron is the one that can
  read confidential code on our own server (Lightning 30B on a Verda A100, see [verda.md](verda.md)).

**How we improved its outputs.**
- **Strict JSON schema, one repair turn.** Fences and `<think>` are stripped; malformed output gets one retry.
- **Machine-verified citations.** Every quote, test and check is re-checked; unsupported claims
  are rejected: <!--n:nemotron_verified-->63<!--/n--> findings verified, <!--n:nemotron_rejected-->1<!--/n--> rejected.
- **Blind context.** Seeding notes and benchmark keys are stripped, and the runner refuses to send a context that
  still names them.
- **Room to finish.** 16k output tokens cut a review off (reasoning counts), so `max_tokens` is 32k.
- **Context budget and a "what you were not given" list.** Files shrink to windows around the hunks; the model is
  told what it did not get, so it refuses instead of guessing (<!--n:nemotron_refusals-->47<!--/n--> refusals, each shown to the owner).
- **Unanimity.** On 2283 it said met beside Codex while Claude's reproduced objection stood; the clause stayed
  refused. Its "all good" never clears alone.

**Limits.** The owner accepted <!--n:nemotron_accepted-->8<!--/n--> of the <!--n:nemotron_rated-->10<!--/n--> findings he rated. It missed one surviving mutant and
called one variant a root-cause fix although the bug does not occur on that base.

**Cost.** <!--n:nemotron_call_min_k-->38<!--/n--> to <!--n:nemotron_call_max_k-->71<!--/n-->k tokens per review call (<!--n:nemotron_seeded_min_k-->51<!--/n--> to <!--n:nemotron_seeded_max_k-->70<!--/n-->k on seeded changes); $0 on NVIDIA's
free tier, each call logged in `measurement/costs.yaml`.

Code: github.com/Zawaer/countersign (`countersign/llm.py`, `reviews/*/nemotron.json`)

<sub>2,386 characters</sub>
