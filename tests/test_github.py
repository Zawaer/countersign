"""The pull-request glue: only the owner's own signature over exactly this pack, chained onto the ledger, flips the status."""

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from countersign import github as gh_mod, ledger, pack as pack_mod
from countersign.common import canonical, sha256_hex, write_json

from conftest import SRC, TEST, git, make_facts


class FakeGitHub:
    def __init__(self, repo, pr):
        self.repo, self.pr, self.comments, self.statuses, self.sticky = repo, pr, [], [], None

    def call(self, method, path, body=None, ok404=False):
        assert (method, path) == ("GET", f"/pulls/{self.pr['number']}")
        return {"head": {"ref": self.pr["head_ref"], "sha": self.pr["head_sha"]}, "base": {"sha": self.pr["base_sha"]},
                "user": {"login": "agent-bot"}}

    def comment(self, number, body):
        self.comments.append(body)

    def status(self, sha, state, description, context, target_url):
        self.statuses.append((sha, state, description, context))

    def upsert_sticky(self, number, body):
        self.sticky = body
        return "url"

    def set_tier_label(self, number, tier):
        pass

    def route_to_owner(self, number, login, author):
        return "review requested"


@pytest.fixture
def pr_world(ws, tmp_path, monkeypatch):
    """The conftest workspace as the pinned snapshot, a ledger branch with a bare remote, and a fake GitHub."""
    repo = ws.repo
    # make the recorded facts match the commit exactly, so the evidence is about this PR's head
    numstat = git(repo, "diff", "--numstat", ws.base, ws.head).split("\t")
    write_json(ws.facts_path("9001"), make_facts(base=ws.base, head=ws.head, diff={
        "files": 1, "insertions": int(numstat[0]), "deletions": int(numstat[1]),
        "by_file": [{"path": SRC, "ins": int(numstat[0]), "del": int(numstat[1]), "kind": "source"}]}))
    git(repo, "branch", "ju26-issue-9001", ws.head)
    remote, ldir = tmp_path / "ledger.git", tmp_path / "ledger"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    git(repo, "remote", "add", "origin", str(remote))
    git(repo, "worktree", "add", "-q", "--detach", str(ldir))  # like CI: a worktree of the checkout
    git(ldir, "checkout", "-q", "--orphan", "seed")
    git(ldir, "rm", "-rq", "--cached", ".")
    (ldir / "ledger.jsonl").write_text(ws.ledger_path.read_text())
    git(ldir, "add", "ledger.jsonl")
    git(ldir, "commit", "-qm", "seed")
    git(ldir, "push", "-q", "origin", "HEAD:countersign-ledger")
    git(ldir, "checkout", "-q", "--detach")
    cfg = tmp_path / "config.yaml"
    cfg.write_text("owners: {Toivo: toivo-gh, Rene: rene-gh}\nledger_branch: countersign-ledger\n")
    pr = {"number": 7, "head_ref": "ju26-issue-9001", "head_sha": ws.head, "base_sha": ws.base}
    fake = FakeGitHub("o/demo", pr)
    monkeypatch.setattr(gh_mod, "GitHub", lambda repo, token=None: fake)
    args = dict(snapshot=str(ws.root), config=str(cfg), repo_dir=repo, gh_repo="o/demo", ledger_dir=str(ldir), artifacts=None)
    snap = gh_mod.workspace(str(ws.root), repo, (ldir / "ledger.jsonl").read_text())
    p = pack_mod.build(snap, "9001")
    return SimpleNamespace(ws=ws, snap=snap, p=p, fake=fake, args=args, ldir=ldir, remote=remote, tmp=tmp_path, pr=pr)


def _comment(w, body, login):
    event = w.tmp / "event.json"
    event.write_text(json.dumps({"comment": {"body": body, "user": {"login": login}},
                                 "issue": {"number": 7, "pull_request": {}}}))
    return gh_mod.cmd_command(SimpleNamespace(**w.args, event=str(event)))


def _signed_comment(w, signer="Toivo", decision="accept", note="ok", key_of="toivo"):
    entry = gh_mod.make_entry(w.snap, w.p, signer, decision, note, (w.ws.private_keys / f"{key_of}.key").read_text())
    return f"/countersign {decision} {note}\n\n```{gh_mod.FENCE}\n{json.dumps(entry)}\n```\n", entry


def test_check_routes_ask_to_owner_and_sets_pending(pr_world):
    w = pr_world
    gh_mod.cmd_check(SimpleNamespace(**w.args, pr=7))
    state = w.fake.statuses[-1][1]
    assert state == {"ask": "pending", "block": "failure", "silent": "success", "notify": "success"}[w.p["tier"]]
    assert gh_mod.MARKER in w.fake.sticky and "Recorded reviews; a live run calls the reviewers" in w.fake.sticky
    assert "Evidence matches this PR | yes" in w.fake.sticky


def test_signed_accept_by_owner_is_recorded_and_pushed(pr_world):
    w = pr_world
    body, entry = _signed_comment(w)
    _comment(w, body, "toivo-gh")
    assert w.fake.comments[-1].startswith("Recorded: **accept** by Toivo"), w.fake.comments[-1]
    assert w.fake.statuses[-1][1] == "success"
    pushed = subprocess.run(["git", "--git-dir", str(w.remote), "show", "countersign-ledger:ledger.jsonl"],
                            capture_output=True, text=True, check=True).stdout
    assert json.loads(pushed.splitlines()[-1])["hash"] == entry["hash"]
    # a status re-run (new CI run, fresh workspace) still sees the countersignature
    gh_mod.cmd_check(SimpleNamespace(**w.args, pr=7))
    assert w.fake.statuses[-1][1] == "success" and "countersigned by Toivo" in w.fake.statuses[-1][2]


def test_unsigned_command_changes_nothing(pr_world):
    w = pr_world
    _comment(w, "/countersign accept looks fine", "toivo-gh")
    assert w.fake.comments[-1].startswith("Not recorded yet") and "sign-pr 7" in w.fake.comments[-1]
    assert not w.fake.statuses


def test_someone_else_cannot_countersign(pr_world):
    w = pr_world
    body, _ = _signed_comment(w)
    _comment(w, body, "rene-gh")
    assert "cannot countersign" in w.fake.comments[-1]
    assert not w.fake.statuses


@pytest.mark.parametrize("tamper,expect", [
    (lambda e: e["payload"].update(pack_sha256="0" * 64), "payload.pack_sha256"),
    (lambda e: e.update(prev="1" * 64), "the ledger moved on"),
    (lambda e: e["payload"].update(decision="reject"), "payload.decision"),
])
def test_tampered_entries_are_refused(pr_world, tamper, expect):
    w = pr_world
    entry = gh_mod.make_entry(w.snap, w.p, "Toivo", "accept", "ok", (w.ws.private_keys / "toivo.key").read_text())
    tamper(entry)
    errs = gh_mod.verify_signed_entry(entry, w.snap, w.p, sha256_hex(canonical(w.p)), "accept", "ok")
    assert any(expect in e for e in errs), errs
    assert any("hash does not match" in e for e in errs)


def test_wrong_key_is_refused(pr_world):
    w = pr_world
    body, _ = _signed_comment(w, key_of="rene")
    _comment(w, body, "toivo-gh")
    assert "does not verify" in w.fake.comments[-1] and "keys/toivo.pub" in w.fake.comments[-1]
    assert not w.fake.statuses
    assert len(ledger.read(w.ws)) == len((w.ldir / "ledger.jsonl").read_text().splitlines())


def test_new_commits_make_the_evidence_stale(pr_world):
    w = pr_world
    repo = w.ws.repo
    git(repo, "checkout", "-q", "ju26-issue-9001")
    extra = Path(repo) / TEST
    extra.parent.mkdir(parents=True, exist_ok=True)
    extra.write_text("// a test the agent added after the review\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "agent pushes more")
    w.pr["head_sha"] = git(repo, "rev-parse", "HEAD")
    gh_mod.cmd_check(SimpleNamespace(**w.args, pr=7))
    assert w.fake.statuses[-1][1] == "pending" and "evidence out of date" in w.fake.statuses[-1][2]
    body, _ = _signed_comment(w)
    _comment(w, body, "toivo-gh")
    assert w.fake.comments[-1].startswith("Not recorded: evidence is for head")
