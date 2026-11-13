# Junction submission text

Paste everything between the two rules into the platform. Character count of that text is stated at the bottom (limit 5,000).

---

**Project name:** Countersign

**Punchline:** AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it can't, and a named human countersigns the rest.

**Challenge:** Tieto, Earned Trust in AI Code

**Tech challenges:** Codex, Gemini, CRACI, Nemotron

**Repo:** https://github.com/Zawaer/countersign

**The problem.** Agents write more code than people can read line by line, yet a named person still answers for every merge. "The AI said it was fine" is not something they can sign.

**Our recommendation.** Stop asking "did a human read every line?" and ask "did a named human sign for what was proven, what was refused, and the risk left?" Review becomes delegated authority:

1. A signed, versioned mandate per repo and area says what the AI may clear alone (silent, notify), what goes to a named owner (ask) and what is refused (block).
2. Facts first: build, tests, "do the new tests fail without the fix?", public-API and analyzer checks run before any model reads the diff.
3. Reviewers from different vendors work separately. Every claim must cite a file line, test, check or requirement clause, and the engine re-checks each citation. No evidence, no finding.
4. A requirement clause is proven only if every reviewer says met with verified evidence and its checks pass. Anything else is refused, with the reason.
5. The change explains itself: an evidence pack with the tier and why, requirement trace, findings, refusals, what wasn't checked, residual risk.
6. The named owner countersigns (Ed25519) into a hash-chained ledger.
7. Trust is earned per area from spot-checks and withdrawn after an escape.

**What it showed on Tieto's sample changes.** On ju26-issue-2234 the agent wrote sound, tested code that fixes a different bug than the issue reports: the regression comes from an upstream commit that isn't in the branch's base. Reverting the fix showed only 4 of the 8 new tests fail without it. The AI refused the "must not crash" requirement because one reviewer reproduced a remaining crash and the other said met, and it refused to decide whether the change fixes users' release line. It routed the change to its owner with every reason listed; nobody had to read 262 lines to find out. 2283 also goes to its owner (the fix silences a warning users relied on); 2129 and 2297 are blocked (new public API and failing checks; 237 files, split it).

**Trade-offs and limits.** More refusals at first, in exchange for fewer escapes. Several reviewers cost more than one, but cross-vendor disagreement is an honest uncertainty signal and self-reported confidence isn't. It can't judge intent, is only as good as the requirement text, and areas without checks fall back to humans. Trust events and review-time estimates in the demo are simulated and labelled as such.

**Codex.** Codex is our second-vendor reviewer. It reviewed all four changes twice, read-only: before the deterministic facts existed and after. Both passes are kept and every run is logged. The comparison is our clearest lesson: given passing tests, Codex marked all 11 requirement clauses met and raised no findings, while the other reviewer found the wrong-bug problem. That is why one reviewer's "all good" can never clear a change.

**Gemini.** Gemini is the adjudicator in the mandate's reviewer panel. When reviewers disagree, it reads only the disputed items with both sides' cited evidence and the engine's verification results, and says which claims hold up and what evidence would settle the rest. The engine enforces that it can only add reasons and route to a human, never clear anything: a tie-breaker that can clear would be one model approving the change.

**CRACI.** The pipeline runs as a GitHub Actions job on CRACI runners: engine tests, ledger verification, routing, and a check that every committed evidence pack rebuilds byte for byte, under a deny-by-default network policy. A second job runs the Nemotron reviews and Gemini adjudication with API keys as secrets. CRACI's per-job egress trace and SBOM show exactly what the review job could reach and install.

**Nemotron.** Nemotron is the third reviewer and the only open-weight one, marked self-hostable in the mandate. A repo or area marked confidential admits only self-hostable reviewers, and the runner refuses to send its code to a vendor-hosted endpoint, so a client's code can stay on its own infrastructure. TODO(numbers): one line on Nemotron's results on the four changes once its reviews land.

**Team:** Toivo and Rene.

---

Character count of the text between the rules: **4,526** (Python `len()` on the stripped text, including the one remaining `TODO(numbers)` placeholder in the Nemotron paragraph, about 110 characters). That leaves about 590 characters for the Nemotron result; recount before pasting:

```bash
python3 -c "print(len(open('docs/pitch/submission.md').read().split('\n---\n',2)[1].strip()))"
```
