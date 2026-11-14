# Junction submission text

Paste the text between the two rules into the platform, without the `<!--n:...-->` markers (they keep the numbers in sync with the result files; the command at the bottom prints the clean text). Its character count is stated at the bottom (limit 5,000).

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
3. Three reviewers, Claude, Codex and Nemotron, review separately. Every claim cites evidence the engine re-checks. A requirement clause is proven only if all three say met and its checks pass; otherwise it is refused, with the reason. A bug a reviewer claims is re-run by the pipeline as a test.
4. The evidence pack says what was checked, found, refused and not checked, and the residual risk. The owner signs its hash into a hash-chained ledger.
5. Trust is earned per area: 20 agreeing spot-checks in a row to reach notify. An escape (a merged change later reverted or fixed), a disagreeing spot-check or a missed seeded-bug canary drops a stage. A new model or prompt starts at ask.

**What it showed.** On ju26-issue-2234 the agent wrote sound code that fixes a different crash than the issue reports. Only <!--n:t2234_fail_without_fix-->4<!--/n--> of <!--n:t2234_new_tests-->8<!--/n--> new tests fail without it, so two clauses are marked "held before": met, but not achieved by this change; mutation testing agrees (their tests kill no mutant of the change). The pipeline reproduced a remaining Key(null) crash. The no-crash clause is refused (Claude: not met; Codex, Nemotron: met; Gemini found Claude's side supported). Its owner gets every reason and learns it fixes the wrong bug. On small changes like this the pack takes longer than the diff (simulated); time is saved only on large changes and ones the AI clears. 2283 goes to its owner (the fix silences a warning; reproduced by the pipeline); 2129 and 2297 are blocked. Of three small upstream controls, a one-line docs fix is cleared by the AI, which tells its owner.

**Measured.** On <!--n:history_prs-->109<!--/n--> real merged MessagePack PRs (mandate v<!--n:history_mandate-->6<!--/n-->, upstream CI credited as passed), the AI would have cleared <!--n:history_cleared-->24<!--/n-->, and <!--n:history_escapes_cleared-->0<!--/n--> of the <!--n:history_escapes-->11<!--/n--> later reverted or fixed. Checks alone catch <!--n:seeded_caught_by_checks-->14<!--/n--> of <!--n:seeded_total-->18<!--/n--> seeded changes (<!--n:seeded_bugs_caught_by_checks-->11<!--/n--> of <!--n:seeded_bugs-->14<!--/n--> one-line bugs, both prompt injections, a supply-chain attack); of the <!--n:seeded_survivors-->4<!--/n--> that got past, a reviewer flagged the planted line in <!--n:seeded_survivors_flagged_new-->3<!--/n--> with a finding the original did not already have (<!--n:seeded_survivors_flagged-->4<!--/n--> by location). A simulation showed the old trust rule let escapes rise when reviewers degrade; 20 checks plus canaries fixed it, and we changed the signed mandate (v3; now v<!--n:mandate_version-->6<!--/n-->). We attacked our own pipeline <!--n:redteam_total-->35<!--/n--> ways; after the fixes it stops <!--n:redteam_stopped-->35<!--/n-->. The last needed mutation testing: a clause is proven only if one of its tests kills a mutant of the change.

**Limits.** It can't judge intent and is only as good as the requirement text. Areas without checks fall back to humans. Reviewers share blind spots. Trust over time and review minutes are simulated and labelled.

**Codex.** One of the three reviewers, on all seven changes. Given passing tests, its second pass said every clause was met and found nothing: it acted as a rubber stamp, which is why one reviewer can never clear. Codex also reviewed our own pipeline for security; we confirmed 8 issues (4 it missed) and fixed 7, including the merge-gate hole (only our GitHub App can now post the required status); the last, low-severity, is documented.

**Gemini.** The adjudicator: it reads only disputed items with both sides' evidence and can never clear anything (enforced in code). It ruled on the disputes in 2234 and 2283, in CI.

**CRACI.** Pipeline, facts and reviewer jobs run on CRACI under deny-by-default egress. deps.delta diffs base and head SBOMs (fails on a seeded attack); build.egress records the network policy as evidence. CRACI's own SBOM and network trace (craci.sbom, craci.network) pass on all four builds, with 0 proxy violations.

**Nemotron.** The open-weight reviewer, run live in CI on all <!--n:real_changes-->7<!--/n--> real changes and the <!--n:seeded_reviewed-->17<!--/n--> seeded changes with reviews. Of the <!--n:nemotron_survivors_reviewed-->4<!--/n--> seeded changes every check missed, its blind review points at the planted line in <!--n:nemotron_survivors_flagged-->3<!--/n-->. A confidential repo may use only self-hosted reviewers, at a measured cost: a self-hosted 30B agrees on <!--n:selfhost_clauses_agree-->31<!--/n--> of <!--n:selfhost_clauses-->34<!--/n--> verdicts but finds <!--n:selfhost_findings-->2<!--/n--> issues to the hosted 120B's <!--n:selfhost_hosted_findings-->17<!--/n-->, so checks and the owner carry more there.

**Team:** Toivo and Rene.

---

Character count of the text between the rules, markers removed: **4,997** (Python `len()` on the stripped text). Print the clean text and recount before pasting:

```bash
python3 -c "import re; t=re.sub(r'<!--/?n(:[a-z0-9_]+)?-->','',open('docs/pitch/submission.md').read().split('\n---\n',2)[1].strip()); print(t); print(len(t))"
```
