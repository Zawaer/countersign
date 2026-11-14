"""Measurement modules: the simulation is labelled and reproducible; history file kinds match facts.py's rules."""

from pathlib import Path

from countersign import history, simulate
from countersign.common import Workspace

ROOT = Path(__file__).resolve().parent.parent


def test_simulation_is_labelled_and_reproducible():
    ws = Workspace.at(ROOT)
    cfg = {"weeks": 10, "replicates": 3, "drift": {"week": 5, "panel_miss": 1.0}}
    a, b = simulate.simulate(ws, cfg), simulate.simulate(ws, cfg)
    assert a["simulated"] is True and a["summary"]["simulated"] is True
    assert a["scenarios"] == b["scenarios"]
    assert all(w["minutes"] == a["scenarios"]["full-human-review"][0]["minutes"] for w in a["scenarios"]["full-human-review"])
    assert "simulated" in simulate.chart_html(a).lower()


def test_history_file_kinds():
    tt = {"src/X/Template.tt"}
    assert history.kind("src/X/Template.cs", tt) == "generated"
    assert history.kind("src/X/Foo.g.cs", set()) == "generated"
    assert history.kind("tests/A/B.cs", set()) == "test"
    assert history.kind("src/MessagePack/PublicAPI.Unshipped.txt", set()) == "build"
    assert history.kind("doc/x.md", set()) == "doc"
    assert history.kind("src/MessagePack/Foo.cs", set()) == "source"
