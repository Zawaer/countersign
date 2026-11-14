"""The model-agnostic reviewer runner, offline: HTTP is stubbed, nothing leaves the machine."""

import json
import shutil
from pathlib import Path

import pytest
import yaml
from conftest import SRC, make_review

from countersign import llm, mandate, pack
from countersign.common import read_json, write_json

ROOT = Path(__file__).resolve().parents[1]
ENV = {"NVIDIA_API_KEY": "nvapi-SECRET-test", "GEMINI_API_KEY": "gm-SECRET-test"}

GOOD = {
    "summary": "Adds a ContainsKey guard.",
    "reviewer": "someone-else", "model": "made-up", "reviewed_at": "1999-01-01",  # must be ignored: the runner stamps these
    "requirement_verdicts": [{"req": "REQ-9001-F1", "verdict": "met", "confidence_basis": "guard + passing test",
                              "evidence": [{"kind": "code", "file": SRC, "line": 5, "rev": "head", "quote": "if (!members.ContainsKey(key))"},
                                           {"kind": "test", "name": "CollectorTests.DuplicateKeys", "outcome": "passed"}]}],
    "findings": [{"id": "N1", "title": "no test for fields", "severity": "minor", "category": "tests", "claim": "only properties are tested",
                  "evidence": [{"kind": "check", "id": "tests.targeted"}]}],
    "refusals": [{"topic": "performance", "reason": "no benchmarks in facts", "who_should_decide": "area owner"}],
}


def completion(content, prompt=1200, completion_tokens=300):
    return json.dumps({"choices": [{"message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
                       "usage": {"prompt_tokens": prompt, "completion_tokens": completion_tokens,
                                 "total_tokens": prompt + completion_tokens}}).encode()


class Stub:
    """Plays back (status, body) pairs and records every request."""

    def __init__(self, *responses):
        self.responses, self.requests = list(responses), []

    def __call__(self, url, body, headers, timeout):
        self.requests.append({"url": url, "body": json.loads(body), "headers": headers})
        status, data = self.responses.pop(0)
        return status, {"Retry-After": "0"} if status == 429 else {}, data


@pytest.fixture
def lws(ws):
    shutil.copytree(ROOT / "prompts", ws.root / "prompts")
    return ws


def test_review_is_parsed_stamped_saved_and_costed(lws):
    fenced = "<think>let me look</think>\nHere you go:\n```json\n" + json.dumps(GOOD) + "\n```"
    stub = Stub((429, b'{"error":"rate limited"}'), (200, completion(fenced)))
    out = llm.run_review(lws, "9001", "nemotron", lws.repo, env=ENV, post=stub, sleep=lambda s: None)
    r = read_json(out)
    assert r["reviewer"] == "nemotron" and r["model"] == "nvidia/nemotron-3.5-super-vl-120b-a12b" and r["vendor"] == "NVIDIA"
    assert r["prompt_version"] == "review-v1" and r["reviewed_at"] != "1999-01-01"
    assert r["requirement_verdicts"][0]["verdict"] == "met" and r["findings"][0]["id"] == "N1"
    assert r["runner"]["usage"] == {"prompt_tokens": 1200, "completion_tokens": 300}
    # request: the right endpoint/model, the versioned prompt as system message, the code with line numbers
    req = stub.requests[-1]
    assert req["url"] == "https://integrate.api.nvidia.com/v1/chat/completions"
    assert req["body"]["model"] == "nvidia/nemotron-3.5-super-vl-120b-a12b"
    assert req["body"]["messages"][0]["content"].startswith("# Countersign reviewer brief, review-v1")
    user = req["body"]["messages"][1]["content"]
    assert "    5| " in user and "REQ-9001-F1" in user and "What you did NOT get" in user
    assert req["headers"]["Authorization"] == "Bearer nvapi-SECRET-test"
    # audit trail, without the key
    raw = lws.inputs / "reviews" / "9001" / "raw"
    assert (raw / "nemotron.response.json").exists() and (raw / "nemotron.context.md").exists()
    for p in [*raw.iterdir(), out, out.with_suffix(".md")]:
        assert "SECRET" not in p.read_text()
    # cost row from the usage field; NVIDIA's free tier is $0
    rows = yaml.safe_load((lws.inputs / "measurement" / "costs.yaml").read_text())["runs"]
    assert rows[-1]["tokens_in"] == 1200 and rows[-1]["source"] == "api usage field" and rows[-1]["change"] == "9001"
    # and the engine accepts it as a reviewer
    p = pack.build(lws, "9001")
    assert p["requirements"][0]["verdicts"]["nemotron"]["verified"] == 2


def test_one_repair_turn_then_success(lws):
    broken = '{"requirement_verdicts": [{"req": "REQ-9001-F1", "verdict": "probably"}]'
    stub = Stub((200, completion(broken)), (200, completion(json.dumps(GOOD))))
    r = read_json(llm.run_review(lws, "9001", "nemotron", lws.repo, env=ENV, post=stub, sleep=lambda s: None))
    assert r["runner"]["json_repaired"] is True and len(stub.requests) == 2
    repair = stub.requests[1]["body"]["messages"][-1]["content"]
    assert repair.startswith("That was not valid JSON") and "return only the corrected json" in repair.lower()
    assert stub.requests[1]["body"]["chat_template_kwargs"] == {"enable_thinking": False}


def test_gives_up_after_one_repair_and_writes_no_review(lws):
    stub = Stub((200, completion("not json")), (200, completion("still not json")))
    with pytest.raises(llm.LLMError):
        llm.run_review(lws, "9001", "nemotron", lws.repo, env=ENV, post=stub, sleep=lambda s: None)
    assert not (lws.inputs / "reviews" / "9001" / "nemotron.json").read_text().count("probably")  # fixture review untouched
    assert (lws.inputs / "reviews" / "9001" / "raw" / "nemotron.response.json").exists()


def test_confidential_change_sends_nothing_to_hosted_or_non_self_hostable(lws):
    text = lws.mandate_path.read_text().replace("\nconfidential: false\n", "\nconfidential: true\n", 1)
    lws.mandate_path.write_text(text)
    mandate.sign(lws, "Toivo")
    stub = Stub()
    with pytest.raises(SystemExit, match="vendor-hosted endpoint"):
        llm.run_review(lws, "9001", "nemotron", lws.repo, env=ENV, post=stub)
    with pytest.raises(SystemExit, match="not self-hostable"):
        llm.run_review(lws, "9001", "gemini", lws.repo, env=ENV, post=stub)
    assert stub.requests == []


def test_missing_key_is_a_clear_error(lws):
    with pytest.raises(SystemExit, match="NVIDIA_API_KEY"):
        llm.run_review(lws, "9001", "nemotron", lws.repo, env={}, post=Stub())


def test_adjudicate_runs_only_on_disputes_and_keeps_only_advisory_fields(lws):
    stub = Stub()
    assert llm.run_adjudication(lws, "9001", lws.repo, env=ENV, post=stub) is None and stub.requests == []
    write_json(lws.inputs / "reviews" / "9001" / "codex.json", make_review("codex", verdict="cannot_determine"))
    ruling = {"rulings": [{"dispute": "REQ-9001-F1", "verdict": "met", "status": "proven",
                           "supported": [{"reviewer": "claude", "claim": "guard exists", "why": "verified quote at head:5"}],
                           "unsupported": [{"reviewer": "codex", "claim": "cannot tell", "why": "cites the same evidence"}],
                           "evidence_that_would_settle": ["a test with duplicate keys on fields"], "route_to": "Toivo"}]}
    stub = Stub((200, completion(json.dumps(ruling))))
    out = llm.run_adjudication(lws, "9001", lws.repo, env={**ENV, "COUNTERSIGN_GEMINI_MODEL": "gemini-test"}, post=stub)
    a = read_json(out)
    assert out.name == "adjudication.gemini.json" and a["model"] == "gemini-test" and a["prompt_version"] == "adjudicate-v1"
    assert "verdict" not in a["rulings"][0] and "status" not in a["rulings"][0]
    sent = stub.requests[0]["body"]["messages"][1]["content"]
    assert '"engine_verified": true' in sent and "code_around_cited_line" in sent
    assert stub.requests[0]["url"].startswith("https://generativelanguage.googleapis.com/v1beta/openai/chat/completions")
    p = pack.build(lws, "9001")
    assert p["requirements"][0]["status"] == "refused" and p["adjudication"]["rulings"][0]["dispute"] == "REQ-9001-F1"
    assert "Adjudicator: gemini" in pack.to_markdown(p)


def test_extract_json_handles_fences_and_think_blocks():
    assert llm.extract_json('<think>{"no": 1}</think>```json\n{"a": 1}\n```') == {"a": 1}
    assert llm.extract_json('Sure! {"a": {"b": 2}} done') == {"a": {"b": 2}}
    with pytest.raises(ValueError):
        llm.extract_json("nothing here")


def test_from_raw_reparses_a_saved_answer_without_calling_the_api(lws):
    odd = json.loads(json.dumps(GOOD))
    odd["findings"][0]["category"] = "build"  # not in the brief's list; only displayed, so it is kept
    stub = Stub((200, completion(json.dumps(odd))))
    llm.run_review(lws, "9001", "nemotron", lws.repo, env=ENV, post=stub, sleep=lambda s: None)
    (lws.inputs / "reviews" / "9001" / "nemotron.json").unlink()
    out = llm.review_from_raw(lws, "9001", "nemotron", lws.repo, env=ENV)
    r = read_json(out)
    assert r["findings"][0]["category"] == "build" and "re-parsed offline" in r["runner"]["reparsed_from_raw"]
    assert len(stub.requests) == 1
