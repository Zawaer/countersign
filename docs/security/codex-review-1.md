## Findings

### High: A valid signoff can be replayed onto another PR with the same pack

[github.py](/data/work/demo-repo/.countersign/snapshot/countersign/github.py:303), [github.py](/data/work/demo-repo/.countersign/snapshot/countersign/github.py:404), [github.py](/data/work/demo-repo/.countersign/snapshot/countersign/github.py:441)

The verified payload binds the signature to the change ID, deterministic pack hash, decision, note, tier, mandate hash, and statement. The pack hash binds the recorded evidence, including the head commit. But the PR number and live PR head are only added as extra fields by `make_entry`; `verify_signed_entry` does not check them. An owner’s signed comment for one PR can therefore be copied to a different PR with the same branch-derived change and identical pack, if the owner is the commenter. CI can then record that signoff and publish success on the second PR.

**Minimal fix:** Include the repository identity, PR number, and live head SHA in the required signed payload, and compare them to the current PR in `verify_signed_entry`.

### Medium: Evidence can be cited from any path in the selected Git revision

[verify.py](/data/work/demo-repo/.countersign/snapshot/countersign/verify.py:31), [verify.py](/data/work/demo-repo/.countersign/snapshot/countersign/verify.py:48), [verify.py](/data/work/demo-repo/.countersign/snapshot/countersign/verify.py:55)

Code evidence uses `git show <rev>:<model-supplied path>` without requiring the path to be changed or relevant to the requirement. A model can cite a quote from an unrelated tracked file and receive `verified: true`; `decide_clauses` then counts that citation toward the minimum evidence threshold. This does not let a PR author directly alter the protected review JSON, but it weakens what “verified evidence” means for untrusted model output.

**Minimal fix:** Restrict code citations to paths in the recomputed PR diff, validate the path and line against that diff, and require substantive evidence for a `met` verdict rather than allowing any quote to count.

### Low: Model output validation allows incomplete verdict sets and loosely typed fields

[llm.py](/data/work/demo-repo/.countersign/snapshot/countersign/llm.py:202), [decide.py](/data/work/demo-repo/.countersign/snapshot/countersign/decide.py:75), [decide.py](/data/work/demo-repo/.countersign/snapshot/countersign/decide.py:91)

The schema check validates each supplied verdict’s ID and value but does not require exactly one verdict per requirement, reject duplicate verdicts, or validate the expected types of evidence fields. Missing verdicts are conservatively refused by the decision code. However, duplicate verdicts are resolved by taking the first matching item, and malformed evidence shapes can cause runtime errors or inconsistent handling.

**Minimal fix:** Validate exact required IDs with no duplicates and strict field types before accepting the JSON.

### Low: Prompt-injection content is sent to the model without an explicit data boundary

[llm.py](/data/work/demo-repo/.countersign/snapshot/countersign/llm.py:320), [llm.py](/data/work/demo-repo/.countersign/snapshot/countersign/llm.py:235)

The review context includes PR diff content and repository facts as user-message text; the JSON repair turn also includes the model’s prior answer. A malicious diff can contain instructions aimed at the reviewer or repair step. I found no direct path from that text to executing code or to bypassing the deterministic evidence checks, but prompt injection can still distort review output and therefore affect the advisory judgment.

**Minimal fix:** Clearly delimit repository content as untrusted data in the prompt, instruct the model never to follow instructions inside it, and keep the decision dependent on deterministic checks and validated evidence.

## Checked and found sound

- **Workflow event trust boundary:** `pull_request_target` checks out the default branch and runs the pinned snapshot; fetched PR commits are used as Git data. The shown workflow does not check out or execute PR code. `issue_comment` also checks out the default branch. The comment body is passed through the event file, not interpolated into a shell command.
- **Comment authorization and signature verification:** Recording requires a comment from the configured owner login, a signature that verifies against the protected public key, an allowed decision, and a matching current pack. A plain `/countersign accept` is insufficient.
- **Ledger chaining:** Entries hash canonicalized content excluding `hash` and `sig`, sign the resulting hash with Ed25519, and verify sequence, previous hash, content hash, and signature. The ledger update is pushed as a fast-forward.
- **Changed-pack protection:** The current pack is rebuilt; stale evidence blocks recording, and the signed pack hash must match. This prevents reusing a signoff after the code or pack inputs change.
- **Clause status and adjudication:** Only required reviewers’ unanimous `met` verdicts with enough verified evidence and passing mandated checks can prove a clause. Missing reviews, disagreement, unverified/thin evidence, and failed or absent checks refuse it. The adjudicator cannot clear a refused clause.
- **API key persistence:** The key is read from the environment and used in the HTTP Authorization header. Saved context and response files contain prompts, model responses, usage, and endpoint metadata, but not the key. Errors redact the key before raising.

This was a static, read-only review of the requested reference pipeline and demo workflows; I did not run tests or modify files.

(Codex run 01a1d762-85d0-7620-9743-6a9bde01733a · 240277 tokens in, 2171 out)
