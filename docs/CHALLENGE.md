# Challenge brief: Earned Trust in AI Code (Tieto), Junction 2026

Copied from the Junction platform challenge page for reference.

**The challenge:** How does AI code review keep pace with AI-written code, while humans stay accountable for every change?

**Introduction:** It is Friday afternoon. A pull request lands from an agent. Two hundred lines, and your name is on the approval. Usually you would open the diff and start digging. But what if the change opened with its own explanation? What it does, why it was made, what else it touches, and how sure the AI is about each part. Suddenly you are not hunting for problems. You are checking a story, and questioning the parts that do not add up.

**Background:** Agent tokens passed human tokens in February 2026 and reached 7.3 trillion by August (OpenRouter data, a16z chart). Reviewing every change by hand does not scale, yet engineers need a sound basis to trust AI-reviewed code.

**Task:** Design an AI code review concept, then show it works. Define the concept, principles, reference implementation and technology considerations, across frontend, backend and security. Challenge the traditional model: is line-by-line review still the right way to ensure quality? Balance risk, hallucination, transparency, confidence and quality in AI review. The result is a reference implementation that illustrates the concept; it is not a product.

## What we expect from each team
1. Define the concept: what your team recommends the "PR review" factory should follow.
2. State its key principles, including how it balances risk, hallucination, transparency, confidence and quality.
3. Illustrate it as a reference, on one sample agent-written change with its requirement ID.
4. Show what the AI found, what it refused to decide, and why.
5. Show how the evidence lets a named human accept the change without a full read.
6. Name the failure modes you saw, and keep a short log of decisions.

Use synthetic or cleared sample data only.

## Code input
https://github.com/te-industry-tech-office/junction26-messagepack-csharp (make your own copy). Branches with AI-made changes:
- `ju26-issue-2283`: bug #2283, 4 files
- `ju26-issue-2234`: bug #2234, 4 files
- `ju26-issue-2129`: issue #2129, 28 files
- `ju26-issue-2297`: issue #2297, 237 files

"We put more weight on the concept than only the technical implementation." "How can AI review the code made by AI so that humans can trust it?"

## Deliverables
- Concept card: recommendation, principles, trade-offs, limits
- Live walkthrough showing where the trust comes from
- Lessons log and a demo video/presentation

Out of scope: a finished product, model training and vendor selection.
Expected outcome: a concept with explicit trade-offs that humans can trust and be accountable for.

## Insight: AI reviews. Humans stay accountable.
Trust is built on evidence a person can check and own, not on the AI being confident.

How humans build trust they can stand behind:
- A named engineer owns each change and signs off on it.
- The AI review is advice with evidence, never the approval itself.
- Evidence is traceable to a requirement, so the owner can check it quickly.
- Depth of human review follows risk: low-risk changes get light checks, high-risk ones get a full read.
- Humans spot-check the AI reviewer, and track what it misses.
- Trust is earned per area, from track record, and withdrawn after escapes.

What the owner signs: what was checked, and by whom or what; what was not checked, and why; the residual risk they accept.

Not accepted: "The AI said it was fine." An unowned merge. Confidence without evidence, or a risk score nobody can explain.

What major vendors recommend: route human attention by risk; keep reviews fast and low-noise. Review with full repo context, and verify findings before posting. Measure outcomes (reverts, incidents), not review activity.

Directions (options, not requirements): a **generalist reviewer** covering frontend, backend, security and performance (how to train or prompt for that breadth is part of the work), or a **classifier** that flags code that genuinely needs human review and separates it from code that meets the standard.

Questions judges will ask: What would make you not trust your own output? Who owns the decision? How would this scale?

Resources Tieto brings: background on what good code means at Tieto (standards, security and quality); a requirements set (intent, functional and non-functional); sample agent-written changes, each with its requirement ID. Partner models are available through Junction partner credits.

## Judging
- **Clarity (30%):** a clear recommendation with stated principles, explicit trade-offs and limits.
- **Practicality (25%):** the concept could work in a real pull-request flow and scale, with a named human owning each decision.
- **Measurement (25%):** shows how trust is measured: reverts and incidents don't rise as review time falls, AI findings are real and accepted, time to merge, share routed to humans.
- **Evidence (20%):** evidence traceable to a requirement lets a named human accept a change without a full read, incl. what the AI found, what it refused to decide, and why.

Prizes: €2,000 / €1,000 / €500.
