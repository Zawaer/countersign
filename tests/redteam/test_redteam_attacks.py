"""Red-team regressions (docs/security/REDTEAM.md). Each attempt asserts the attack was stopped.

Attacks that currently get through are marked xfail(strict=True): the test documents today's miss and turns red
the day a fix lands, so the table in REDTEAM.md (and FAILURE_MODES.md) gets updated with it.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from attacks import ATTACKS, run  # noqa: E402

# Known misses as of 2026-11-14 (REDTEAM.md, "Misses and fixes"): none left.
KNOWN_MISSES: set[str] = set()  # TT1 (test theater) closed by tests.mutation (G4, S6 in mandate v6); see REDTEAM.md


@pytest.mark.parametrize("aid", [pytest.param(a[0], marks=pytest.mark.xfail(strict=True, reason="known miss, see REDTEAM.md"))
                                 if a[0] in KNOWN_MISSES else a[0] for a in ATTACKS])
def test_redteam_attack_is_stopped(aid, tmp_path):
    r = run(aid, tmp_path)
    if str(r["actual"]).startswith("skipped"):
        pytest.skip(r["detail"])
    assert r["caught"], f"{aid}: {r['actual']}: {r['detail']}"
