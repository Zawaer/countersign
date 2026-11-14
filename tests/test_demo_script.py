"""scripts/demo.sh runs clean from a fresh copy of the repo: exit 0, the key lines, and the repo's ledger untouched."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(shutil.which("uv") is None or shutil.which("git") is None, reason="needs uv and git")


def _fresh_copy(dest: Path) -> None:
    """What a clone contains, taken from the working tree: tracked files plus new unignored ones, so uncommitted edits are tested."""
    files = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                           check=True, capture_output=True).stdout.split(b"\0")
    for name in filter(None, (f.decode() for f in files)):
        src = ROOT / name
        if src.is_file():
            (dest / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest / name)


def test_demo_runs_clean_from_a_fresh_copy(tmp_path):
    repo = tmp_path / "countersign"
    _fresh_copy(repo)
    ledger_before = (repo / "ledger" / "ledger.jsonl").read_bytes()
    env = {k: v for k, v in os.environ.items() if not k.startswith(("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT"))}
    env["COUNTERSIGN_REPO"] = str(tmp_path / "no-messagepack-clone")  # the demo must not need it
    r = subprocess.run(["bash", "scripts/demo.sh"], cwd=repo, env=env, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    out = r.stdout
    for line in [
        "[1/9] Set up", "[9/9] The measurement in three numbers",
        "2234      ask  ",
        "Toivo  [verified finding] claude:C1",
        "up-1967   notify",
        "6 of 7 go to a human.",
        "Recommended tier: ASK    owner: Toivo",
        ">  1369 |         if (suppressSourceGeneration is true)",
        "refused: not_met, reviewers_disagree",
        "REQ-2234-F1 HELD BEFORE",
        "signed: ledger #1 request-changes by Toivo",
        "ledger OK: 1 entries, hash chain intact, every signature verifies",
        "LEDGER INVALID (1 problems):",
        "line 1: content does not match its hash",
        "claude N1 (blocker)",
        "2234-inject (planted reviewer instructions at README.md:1624) -> tier block (mandate rule R-INJECT)",
        "109 merged upstream PRs",
        "open site/index.html",
        "packs/2234/pack.md",
    ]:
        assert line in out, f"missing {line!r} in demo output:\n{out}"
    assert "Traceback" not in out + r.stderr
    assert (repo / "ledger" / "ledger.jsonl").read_bytes() == ledger_before
    assert not (repo / ".keys").exists()
