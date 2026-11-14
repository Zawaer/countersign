"""Red-team regressions (docs/security/REDTEAM.md). Each attempt asserts the attack was stopped.

Attacks that currently get through are marked xfail(strict=True): the test documents today's miss and turns red
the day a fix lands, so the table in REDTEAM.md (and FAILURE_MODES.md) gets updated with it.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from attacks import ATTACKS, run  # noqa: E402

# Known misses as of 2026-11-14 (REDTEAM.md, "Misses and fixes").
KNOWN_MISSES = {"I2", "I3", "I4", "I5", "I6", "I7", "I8", "R1", "R2", "R3", "R4", "R6", "R7", "G1", "G1b", "G2", "G3", "G4",
                "G6", "T1", "L1", "L2", "L3", "S2", "S3", "S4", "S6", "S7"}


@pytest.mark.parametrize("aid", [pytest.param(a[0], marks=pytest.mark.xfail(strict=True, reason="known miss, see REDTEAM.md"))
                                 if a[0] in KNOWN_MISSES else a[0] for a in ATTACKS])
def test_redteam_attack_is_stopped(aid, tmp_path):
    r = run(aid, tmp_path)
    if str(r["actual"]).startswith("skipped"):
        pytest.skip(r["detail"])
    assert r["caught"], f"{aid}: {r['actual']}: {r['detail']}"
