# Junction submission text

Paste everything between the two rules into the platform. Character count of that text is stated at the bottom (limit 5,000).

---

**Project name:** Countersign

**Punchline:** AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it can't, and a named human countersigns the rest.

**Challenge:** Tieto, Earned Trust in AI Code

**Tech challenges:** Codex, Gemini, CRACI, Nemotron

**Repo:** https://github.com/Zawaer/countersign (demo: site/index.html)

**The problem.** Agents write more code than people can read line by line, yet a named person still answers for every merge. "The AI said it was fine" is not something they can sign.

**Our recommendation.** Ask "did a named human sign for what was proven, what was refused, and the risk left?", not "did a human read every line?"

0. A failing check can't be argued away: no verdict or trust record clears it.
1. A signed mandate per repo and area sets the tier the AI may give alone: silent or notify (AI clears), ask (a named owner signs), block (fix or split).
2. Facts first: build, tests, "do the new tests fail without the fix?", public API, analyzers, dependency diff, a scan for text planted for AI reviewers.
3. Claude, Codex and Nemotron review separately. Every claim cites evidence the engine re-checks. A requirement clause is proven only if all three say met and its checks pass; otherwise it is refused, with the reason. A bug a reviewer claims is re-run by the pipeline as a test.
4. The evidence pack says what was checked, found, refused and not checked, and the residual risk. The owner signs its hash into a hash-chained ledger.
5. Trust is earned per area: 20 agreeing spot-checks in a row to reach notify. An escape (a merged change later reverted or fixed), a disagreeing spot-check or a missed seeded-bug canary drops a stage. A new model or prompt starts at ask.

**What it showed.** On ju26-issue-2234 the agent wrote sound code that fixes a different crash than the issue reports. Only 4 of 8 new tests fail without it, so two clauses are marked "held before": met, but not achieved by this change. The pipeline reproduced a remaining Key(null) crash. The no-crash clause is refused (Claude: not met; Codex, Nemotron: met). It went to its owner with every reason; nobody read 262 lines. 2283 goes to its owner (the fix silences a warning; reproduced by the pipeline); 2129 and 2297 are blocked. Of three small upstream controls, a one-line docs fix is cleared by the AI, which tells its owner.

**Measured.** On 109 real merged MessagePack PRs (mandate v4, upstream CI credited as passed), the AI would have cleared 24 and none of the 11 later reverted or fixed. Checks alone catch 14 of 17 seeded changes (11 of 14 one-line bugs, both prompt injections, a supply-chain attack). A simulation showed the old trust rule let escapes rise when reviewers degrade; 20 checks plus canaries fixed it, and we changed the signed mandate (v3; now v4).

**Limits.** It can't judge intent and is only as good as the requirement text. Areas without checks fall back to humans. Reviewers share blind spots. Trust over time and review minutes are simulated and labelled. In the demo repo any Actions workflow can post the merge status (open, T1); a dedicated GitHub App would close that.

**Codex.** A reviewer on all seven changes. Given passing tests, its second pass said every clause was met and found nothing; unanimity means that can't clear a change. Codex also reviewed our own pipeline for security; we confirmed 8 issues (4 it missed) and fixed or mitigated all but the merge-gate hole.

**Gemini.** The adjudicator: it reads only disputed items with both sides' evidence and can never clear anything (enforced in code). Wired but not run (no key).

**CRACI.** Pipeline, facts and reviewer jobs run on CRACI under deny-by-default egress. deps.delta diffs CycloneDX SBOMs of base and head (passes on all four changes, fails on a seeded attack); build.egress records the build's network policy as evidence (wired, no committed run yet). CRACI's own SBOM and network trace are wired but skipped: no CRACI API token is set.

**Nemotron.** The open-weight reviewer, run live in CI on all 7 real changes and the 16 seeded changes with reviews. Of the 3 seeded bugs every test missed, its blind review points at the planted line in 2. A repo marked confidential may use only self-hostable reviewers like it.

**Team:** Toivo and Rene.

---

Character count of the text between the rules: **4,309** (Python `len()` on the stripped text). Recount before pasting:

```bash
python3 -c "print(len(open('docs/pitch/submission.md').read().split('\n---\n',2)[1].strip()))"
```
