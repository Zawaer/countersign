# The PR flow, as installed on the demo repo

These are the exact files that run Countersign on [Zawaer/countersign-messagepack-demo](https://github.com/Zawaer/countersign-messagepack-demo), a copy of the challenge's MessagePack repo where the agent-written changes are real pull requests. Copy them into a repo to install the gate:

- `workflows/countersign.yml` → `.github/workflows/`: on every PR it runs the pipeline (facts, verified reviews, the decision under the signed mandate), posts the sticky evidence comment, and sets the required `countersign/tier` status through the Countersign Gate GitHub App.
- `workflows/countersign-command.yml` → `.github/workflows/`: records an owner's signed decision (`sign-pr`) on the `countersign-ledger` branch and updates the status.
- `vendor.sh` and `config.yaml` → `.countersign/`: `vendor.sh` copies a pinned snapshot of this repo's pipeline into `.countersign/snapshot/`.

Needed in the target repo: the App's id as variable `COUNTERSIGN_APP_ID`, its private key as secret `COUNTERSIGN_APP_KEY` (in an environment that only `main` may use), and branch protection on `main` requiring `countersign/tier` from that App. Optional: `CI_RUNNER=craci` to run on CRACI. Details: [docs/PR_FLOW.md](../../docs/PR_FLOW.md).
