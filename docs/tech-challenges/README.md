# Tech challenges Countersign enters

Locked in Sat 14 Nov 13:10 (Helsinki) by Toivo. Main challenge: **Tieto, Earned Trust in AI Code**. Each tech challenge below has a real job in the pipeline, not a bolt-on. The write-ups are paste-ready (≤ 2,500 characters each).

| # | Tech challenge | What it does in Countersign | Write-up | What the submission needs |
|---|---|---|---|---|
| 1 | **Best Use of Codex** (OpenAI) | Second-vendor reviewer on every change; read-only security review of our own pipeline (findings fixed); development work. Every run logged in [CODEX_LOG.md](../CODEX_LOG.md) | [codex.md](codex.md) | Show meaningful use of Codex in building the project |
| 2 | **Best Use of Gemini API** (Google DeepMind) | The adjudicator: when reviewers disagree, it audits whose citations hold. It can add reasons and route to a human; it can never clear a change | [gemini.md](gemini.md) | Meaningful, innovative use of Gemini |
| 3 | **Best use of CRACI** | The CI that produces the evidence: builds and tests run on CRACI, and its API supplies each build's network trace and SBOM as review evidence (it surfaced the silently refused revocation checks) | [craci.md](craci.md) | CI/CD on CRACI; creative use of SBOMs, traces, the API |
| 4 | **Best Use of Nemotron** (NVIDIA) | Third reviewer: Nemotron 3.5 Super VL via NVIDIA's API on every change; blind reviews of seeded bugs and generated variants; a self-hosted Nemotron for confidential code | [nemotron.md](nemotron.md) | Nemotron 3.5 Super VL in the working solution + a text: model, what it does, why it matters, how we improved its outputs |
| 5 | **Verda Compute Track** | Self-hosted reviewer on a Verda A100 in Finland: confidential code never leaves our infrastructure | [verda.md](verda.md) | Document the process; **post a summary link in Verda's Discord channel** (Toivo) |
| 6 | **Best Use of Gemma** (Google DeepMind) | Self-hosted adjudicator for confidential code (open weights, same A100): Gemini adjudicates normal repos, Gemma confidential ones | [gemma.md](gemma.md) | Innovative, impactful use of Gemma open models |

Not entered (no real job in Countersign): MariaDB, Aiven, Modal, MongoDB, Vultr, Tiger Data, Entire, Solana, ElevenLabs, Arduino, Atech, Context.dev, Oxylabs, Cloudinary.

Every number in the write-ups must come from the repo (use `<!--n:key-->` markers where a key exists; `python3 scripts/sync_numbers.py --print`). Paste the text without the markers.
