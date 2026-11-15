import json

from countersign import keys, ledger
from countersign.ledger import canonical, sha256_hex
from countersign.cli import main


def lines(ws):
    return ws.ledger_path.read_text().splitlines()


def write_lines(ws, ls):
    ws.ledger_path.write_text("\n".join(ls) + "\n")


def signed(ws):
    main(["review", "9001", "-q", "--root", str(ws.root), "--repo", ws.repo])
    assert main(["sign", str(ws.pack_dir("9001") / "pack.json"), "--as", "Toivo", "--decision", "accept", "--note", "ok",
                 "--root", str(ws.root), "--repo", ws.repo]) == 0
    return ws


def test_signed_ledger_verifies(ws):
    signed(ws)
    problems, warnings = ledger.verify(ws)
    assert problems == [] and warnings == []
    assert [json.loads(x)["type"] for x in lines(ws)] == ["mandate_change", "signoff"]


def test_editing_an_entry_is_detected(ws):
    signed(ws)
    ls = lines(ws)
    e = json.loads(ls[1])
    e["payload"]["decision"] = "reject"  # rewrite history
    ls[1] = json.dumps(e)
    write_lines(ws, ls)
    problems, _ = ledger.verify(ws)
    assert any("edited after it was written" in p for p in problems)


def test_recomputing_the_hash_still_fails_the_signature(ws):
    signed(ws)
    ls = lines(ws)
    e = json.loads(ls[1])
    e["payload"]["decision"] = "reject"
    e["hash"] = ledger.entry_hash(e)
    ls[1] = json.dumps(e)
    write_lines(ws, ls)
    problems, _ = ledger.verify(ws)
    assert any("signature does not verify" in p for p in problems)


def test_deleting_an_entry_breaks_the_chain(ws):
    signed(ws)
    ledger.append(ws, "spotcheck", {"change": "9001", "areas": [], "result": "agree"}, "Toivo")
    ls = lines(ws)
    write_lines(ws, [ls[0], ls[2]])
    problems, _ = ledger.verify(ws)
    assert any("chain broken" in p for p in problems) and any("seq" in p for p in problems)


def test_entry_signed_by_someone_else_is_detected(ws):
    signed(ws)
    e = json.loads(lines(ws)[1])
    e["sig"] = keys.sign(ws, "Rene", e["hash"].encode())  # Rene forges Toivo's sign-off
    write_lines(ws, [lines(ws)[0], json.dumps(e)])
    problems, _ = ledger.verify(ws)
    assert problems and "keys/toivo.pub" in problems[0]


def test_pack_changed_after_signing_is_flagged(ws):
    signed(ws)
    p = ws.pack_dir("9001") / "pack.json"
    data = json.loads(p.read_text())
    data["tier"] = "silent"
    p.write_text(json.dumps(data))
    _, warnings = ledger.verify(ws)
    assert any("changed since Toivo signed it" in w for w in warnings)


def test_re_signing_the_changed_pack_supersedes_the_stale_sign_off(ws):
    signed(ws)
    p = ws.pack_dir("9001") / "pack.json"
    data = json.loads(p.read_text())
    data["tier"] = "silent"
    p.write_text(json.dumps(data))
    assert any("changed since" in w for w in ledger.verify(ws)[1])
    # a newer sign-off of the same pack, covering its current content (written directly: `sign` refuses edited packs)
    old = json.loads(lines(ws)[-1])["payload"]
    ledger.append(ws, "signoff", {**old, "note": "re-signed", "pack_sha256": sha256_hex(canonical(data))}, "Toivo")
    problems, warnings = ledger.verify(ws)
    assert problems == [] and warnings == []   # the older sign-off is superseded, not stale


def test_only_the_named_owner_may_sign(ws, capsys):
    main(["review", "9001", "-q", "--root", str(ws.root), "--repo", ws.repo])
    try:
        main(["sign", "9001", "--as", "Rene", "--decision", "accept", "--note", "", "--root", str(ws.root), "--repo", ws.repo])
        raise AssertionError("Rene should not be able to sign")
    except SystemExit as e:
        assert "not the owner" in str(e)


def test_signer_name_cannot_leave_the_keys_folder(ws):
    ok, why = keys.verify(ws, "../keys/toivo", b"x", "AAAA")
    assert not ok and "invalid owner name" in why


def test_non_object_lines_and_bad_signatures_are_problems_not_crashes(ws):
    signed(ws)
    ls = lines(ws)
    e = json.loads(ls[1])
    e["sig"] = 12345
    write_lines(ws, [ls[0], json.dumps(e), "[1, 2]"])
    problems, _ = ledger.verify(ws)
    assert any("line 2: signature does not verify" in p for p in problems)
    assert any("line 3: not a ledger entry" in p for p in problems)


def test_pack_path_outside_the_workspace_is_a_problem(ws, tmp_path):
    (tmp_path / "outside.json").write_text("{}")
    ledger.append(ws, "signoff", {"change": "9001", "pack_path": "../" * 12 + str(tmp_path / "outside.json").lstrip("/"),
                                  "pack_sha256": "0" * 64}, "Toivo")
    problems, _ = ledger.verify(ws)
    assert any("points outside the workspace" in p for p in problems)
