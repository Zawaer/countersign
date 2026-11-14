# Red-team fixtures

Attacks on Countersign itself, written up in [docs/security/REDTEAM.md](../../docs/security/REDTEAM.md).

- `harness.py`: builds a throwaway world per attack: a scratch git repo with MessagePack's layout, the real mandate
  re-signed with fresh keys, stage 1's own `diff_facts` / `kind` / `injection_check` (from
  `evidence/scripts/facts.py`) run on the attack commit, recorded passing build/test checks, and reviews from the
  three registered reviewers. `World.route()` is the real `pack.build`.
- `attacks.py`: the 35 attempts (`ATTACKS`), one function each. `python tests/redteam/attacks.py` prints the table.
- `test_redteam_attacks.py`: one test per attempt asserting the attack is stopped. Known misses are
  `xfail(strict=True)`, so they document today's behaviour and fail loudly when a fix lands (then move the id out of
  `KNOWN_MISSES` and update REDTEAM.md and FAILURE_MODES.md).
- `dotnet_demos.sh`: G1 on a real .NET build (a props file compiles a `tests/` file into the shipped assembly).
  S6 (Release-only PackageReference) runs inside `attacks.py` when a `dotnet` is found, else it is skipped.

Offline: no model calls, no network (the .NET demos use an empty local feed).
