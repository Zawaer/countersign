import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_numbers_compute_from_sources():
    sys.path.insert(0, str(ROOT / "scripts"))
    import sync_numbers
    v = sync_numbers.values()
    assert int(v["history_prs"]) > 0 and int(v["redteam_total"]) >= int(v["redteam_stopped"])


def test_docs_numbers_are_in_sync():
    r = subprocess.run([sys.executable, str(ROOT / "scripts/sync_numbers.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
