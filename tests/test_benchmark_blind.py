"""Benchmark variants (evidence/var-*): a blind review must not learn how the variant was made.

Needs the variant commits in the MessagePack clone (local /data/src/mp, or COUNTERSIGN_REPO after fetching
evidence/var-*/head.bundle); skipped otherwise."""
import json
import os
import subprocess
from pathlib import Path

import pytest

from countersign import llm
from countersign.common import Workspace

ROOT = Path(__file__).resolve().parents[1]
REPO = os.environ.get("COUNTERSIGN_REPO", "/data/src/mp")
SEEDED = ["var-2283-v4", "var-2234-v4"]


def _has(head: str) -> bool:
    return Path(REPO).exists() and subprocess.run(["git", "-C", REPO, "cat-file", "-e", f"{head}^{{commit}}"], capture_output=True).returncode == 0


@pytest.mark.parametrize("change", SEEDED)
def test_blind_context_hides_the_seeded_record(change):
    facts = json.loads((ROOT / "evidence" / change / "facts.json").read_text(encoding="utf-8"))
    assert facts["seeded"]["kind"] == "hidden_downgrade" and facts["generated_by"]["brief"] == "hidden_downgrade"
    if not _has(facts["head_full"]):
        pytest.skip(f"{REPO} does not have {facts['head']}")
    ws = Workspace.at(str(ROOT), None, REPO, None)
    blind = llm.build_review_context(ws, change, REPO)["text"]
    for word in (*llm.BENCHMARK_KEYS, *llm.BENCHMARK_WORDS):
        assert word not in blind
    assert facts["seeded"]["after"] in blind  # the reviewer still sees the edit itself, in the diff
    assert "hidden_downgrade" in llm.build_review_context(ws, change, REPO, blind=False)["text"]
