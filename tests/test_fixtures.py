"""End-to-end over the simulated fixtures; needs the MessagePack clone for code quotes."""

import shutil
from pathlib import Path

import pytest

from countersign import keys, mandate, measure, pack
from countersign.common import DEFAULT_REPO, Workspace

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not (Path(DEFAULT_REPO) / ".git").exists(), reason=f"{DEFAULT_REPO} not present")


@pytest.fixture
def fws(tmp_path):
    for d in ("mandate", "requirements"):
        shutil.copytree(ROOT / d, tmp_path / d, ignore=shutil.ignore_patterns("*.sig"))
    for d in ("evidence", "reviews"):  # copy, so a local fixture ledger or packs cannot leak in
        shutil.copytree(ROOT / "tests" / "fixtures" / d, tmp_path / "inputs" / d)
    # The simulated fixtures were recorded with the two-reviewer panel (Claude, Codex); drop Nemotron from this copy's
    # registry so they are replayed under the panel they were written for.
    mp = tmp_path / "mandate" / "messagepack.mandate.yaml"
    mp.write_text("\n".join(line for line in mp.read_text().splitlines() if not line.lstrip().startswith(("nemotron:", "note: \"open weights"))) + "\n")
    w = Workspace.at(tmp_path, inputs=tmp_path / "inputs")
    keys.keygen(w, "Toivo")
    mandate.sign(w, "Toivo")
    return w


def test_fixture_routing(fws):
    tiers = {c: pack.build(fws, c)["tier"] for c in fws.changes()}
    assert tiers == {"2129": "ask", "2234": "notify", "2234-mut1": "ask", "2283": "ask",
                     "2283-mut1": "block", "2283-mut2": "notify", "2297": "block"}


def test_illustrated_change_refuses_f2_and_rejects_the_invented_claim(fws):
    p = pack.build(fws, "2283")
    assert [c["id"] for c in p["refused"]["clauses"]] == ["REQ-2283-F2"]
    assert {f["id"] for f in p["rejected_claims"]} == {"X1", "X2"}
    assert [f["id"] for f in p["findings"]] == ["C1"]


def test_replay_marks_simulated_numbers(fws):
    r = measure.replay(fws)
    assert r["metrics"]["catch_rate"]["value"] == 0.67
    assert r["metrics"]["missed_defects"]["value"] == ["2283-mut2"]
    assert all(m["simulated"] for k, m in r["metrics"].items() if k.startswith("human_minutes"))
