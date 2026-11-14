# Best use of Gemini API: the adjudicator that can never clear

**Countersign** reviews agent-written changes: deterministic checks, three AI reviewers (Claude, Codex, Nemotron),
and a named human countersigns what the AI could not prove. Gemini (`gemini-4-hydrogen`, Google's
OpenAI-compatible endpoint) is the adjudicator.

**Its job.** Only when reviewers disagree, or a major finding has no second reviewer, Gemini gets each dispute:
both sides' claims and citations, the engine's verification of each, and the code around each cited line. It says
which claims the evidence supports, which not, what would settle it, and which owner should look.

**Why it can never clear.** An adjudicator that could clear would be one model outvoting a verified objection,
the failure unanimity exists to prevent. So it audits evidence instead of voting: a tested engine rule
(`decide.apply_adjudication`) lets it only add reasons and route to a human. A refused clause stays refused.

**What it ruled** (CI, `reviews/<change>/adjudication.gemini.json`):
- **2283:** Claude objected that the fix drops an analyzer warning, with a reproduction; Codex and Nemotron said met.
  Gemini backed Claude, and found that the others' "all diagnostics keep working" went beyond the passing suite.
- **2234:** the duplicate-key crash fix is supported; Codex's broad "invalid contracts no longer crash" is not, and a
  test name Nemotron cited is not in the facts. Routed to the source-generator owner.
- **<!--n:gemini_variants-->4<!--/n--> benchmark variants:** on both hidden security downgrades it confirmed the cited line (hash-collision protection
  off; object depth 500 to 5000 against the file's own stack-overflow warning) and routed to the security owner.

**In the pack.** The owner sees it beside the refusal: "Gemini on N1: Claude's objection is supported; backs 1 of 2
claims for 'not met', 2 of 4 for 'met' (advisory)", then the unsupported claims and what would settle it.

**Cost.** <!--n:gemini_calls-->6<!--/n--> calls: <!--n:gemini_tokens-->31,671<!--/n--> tokens, $<!--n:gemini_usd-->0.08<!--/n--> in total;
<!--n:gemini_call_tokens_min-->3,234<!--/n--> to <!--n:gemini_call_tokens_max-->7,012<!--/n--> tokens and $<!--n:gemini_call_usd_min-->0.007<!--/n--> to $<!--n:gemini_call_usd_max-->0.018<!--/n--> per call. The team's shared key is a CI secret; each call
appends a row to `measurement/costs.yaml` from the API's usage field, with the run URL.

**Confidential code.** Gemini is hosted, so a repo marked confidential cannot send it code. There the adjudicator
is Gemma, open weights on our own A100: see [gemma.md](gemma.md).

Code: github.com/Zawaer/countersign (`countersign/decide.py`, `prompts/adjudicate-v1.md`)

<sub>2,474 characters</sub>
