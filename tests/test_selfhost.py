"""Self-hosted Nemotron (nemotron-selfhost), offline: a stub OpenAI-compatible server on 127.0.0.1 stands in for vLLM."""

import json
import shutil
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
import yaml
from test_llm import ENV, GOOD, Stub, completion

from countersign import cli, costs, llm, pack
from countersign.common import read_json

ROOT = Path(__file__).resolve().parents[1]
MODEL = "nvidia/nemotron-3.5-super-vl-120b-a12b"  # hosted (the mandate's nemotron)
LIGHTNING = "nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16"  # self-hosted on one A100


@pytest.fixture
def lws(ws):
    shutil.copytree(ROOT / "prompts", ws.root / "prompts")
    return ws


@pytest.fixture
def server():
    """A local OpenAI-compatible server (what vLLM looks like through the SSH tunnel). Records each request."""
    seen = []

    class H(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            seen.append({"path": self.path, "body": body, "auth": self.headers.get("Authorization")})
            data = completion(json.dumps(GOOD), prompt=41000, completion_tokens=9000)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *a):
            pass

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), H)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{httpd.server_port}/v1", seen
    httpd.shutdown()


def selfhost_env(url, rate="2.39"):
    return {"COUNTERSIGN_SELFHOST_URL": url, "COUNTERSIGN_GPU_USD_PER_HOUR": rate}


def test_preset_needs_the_url_and_no_key():
    with pytest.raises(SystemExit, match="COUNTERSIGN_SELFHOST_URL"):
        llm.config("nemotron-selfhost", {})
    c = llm.config("nemotron-selfhost", {"COUNTERSIGN_SELFHOST_URL": "http://127.0.0.1:8000/v1/"})
    assert c.base_url == "http://127.0.0.1:8000/v1" and c.endpoint_host == "127.0.0.1"
    assert c.model == LIGHTNING and c.registry == "nemotron" and c.self_hosted and not c.hosted_default
    assert c.api_key == "" and c.provider == "verda" and c.gpu == "A100 80GB x1" and c.gpu_usd_per_hour is None


def test_context_is_fitted_to_the_servers_window():
    assert llm.selfhost_fit(131072) == (llm.DEFAULT_CONTEXT_CHARS, 32768)  # the hosted settings, unchanged
    chars, out = llm.selfhost_fit(65536)
    assert out == 16384 and chars / 3.1 + out + 1024 <= 65536
    chars, out = llm.selfhost_fit(49152)
    assert out == 16384 and chars / 3.1 + out + 1024 <= 49152


def test_selfhost_review_over_real_http_fills_the_nemotron_slot_and_logs_gpu_time(lws, server):
    url, seen = server
    committed = (lws.inputs / "reviews" / "9001" / "nemotron.json").read_text()
    out = llm.run_review(lws, "9001", "nemotron-selfhost", lws.repo, env=selfhost_env(url), confidential=True)
    # the request: same model id, same thinking switch, no key sent anywhere
    assert seen[0]["path"] == "/v1/chat/completions" and seen[0]["auth"] is None
    assert seen[0]["body"]["model"] == LIGHTNING and seen[0]["body"]["chat_template_kwargs"] == {"enable_thinking": True}
    # written to reviews-selfhost/ as the nemotron slot; the committed hosted review is untouched
    assert out == lws.inputs / "reviews-selfhost" / "9001" / "nemotron.json"
    assert (lws.inputs / "reviews" / "9001" / "nemotron.json").read_text() == committed
    r = read_json(out)
    assert r["reviewer"] == "nemotron" and r["model"] == LIGHTNING
    run = r["runner"]
    assert run["preset"] == "nemotron-selfhost" and run["endpoint_host"] == "127.0.0.1" and run["self_hosted"] is True
    assert run["confidential"] is True and run["confidential_forced"] is True
    assert run["gpu"] == "A100 80GB x1" and run["raw"] == "reviews-selfhost/9001/raw/nemotron.response.json"
    assert run["gpu_hours"] >= 0 and run["usd_estimate"] == pytest.approx(run["gpu_hours"] * 2.39, abs=1e-3)
    raw = read_json(lws.inputs / "reviews-selfhost" / "9001" / "raw" / "nemotron.response.json")
    assert raw["self_hosted"] is True and raw["endpoint"].startswith("http://127.0.0.1:")
    # cost: GPU time x rate, labelled estimate; never the $0 per-token NVIDIA price for the same model id
    row = yaml.safe_load((lws.inputs / "measurement" / "costs.yaml").read_text())["runs"][-1]
    assert row["provider"] == "verda" and row["gpu"] == "A100 80GB x1" and row["source"] == "estimate"
    assert row["tokens_in"] == 41000 and "wall-clock" in row["basis"]
    assert row["usd"] == pytest.approx(row["gpu_seconds"] / 3600 * 2.39, abs=1e-3)
    # the engine reads it as nemotron when it sits in the slot; a model the mandate has not released holds at ask
    shutil.copy(out, lws.inputs / "reviews" / "9001" / "nemotron.json")
    p = pack.build(lws, "9001")
    assert p["requirements"][0]["verdicts"]["nemotron"]["verified"] == 2
    assert p["tier"] in ("ask", "block")


def test_small_window_shrinks_answer_and_context(lws):
    stub = Stub((200, completion(json.dumps(GOOD))))
    env = {"COUNTERSIGN_SELFHOST_URL": "http://127.0.0.1:8000/v1", "COUNTERSIGN_SELFHOST_MAX_MODEL_LEN": "49152"}
    r = read_json(llm.run_review(lws, "9001", "nemotron-selfhost", lws.repo, env=env, post=stub))
    assert stub.requests[0]["body"]["max_tokens"] == 16384 and r["runner"]["max_model_len"] == 49152
    assert f"budget {llm.selfhost_fit(49152)[0]})" in " ".join(r["inputs"])


def test_gpu_cost_without_a_rate_is_unknown_not_free(lws):
    lws_costs = lws.inputs / "measurement" / "costs.yaml"
    lws_costs.parent.mkdir(parents=True, exist_ok=True)
    lws_costs.write_text(costs.HEADER.replace("prices_usd_per_1m: {}", f"prices_usd_per_1m:\n  {LIGHTNING}: {{in: 0, out: 0}}"))
    stub = Stub((200, completion(json.dumps(GOOD))))
    env = {"COUNTERSIGN_SELFHOST_URL": "http://127.0.0.1:8000/v1"}
    llm.run_review(lws, "9001", "nemotron-selfhost", lws.repo, env=env, post=stub)
    row = yaml.safe_load(lws_costs.read_text())["runs"][-1]
    assert row["usd"] is None and row["source"] == "unknown" and row["gpu"] == "A100 80GB x1"
    assert costs.row_usd({LIGHTNING: {"in": 0, "out": 0}}, row) is None


def test_confidential_refuses_every_vendor_endpoint_and_accepts_the_self_hosted_one(lws):
    stub = Stub((200, completion(json.dumps(GOOD))))
    # vendor-hosted Nemotron: refused before anything is sent
    with pytest.raises(SystemExit, match="vendor-hosted endpoint"):
        llm.run_review(lws, "9001", "nemotron", lws.repo, env=ENV, post=stub, confidential=True)
    # not self-hostable at all (gemini is the adjudicator, but the registry check comes first)
    with pytest.raises(SystemExit, match="not self-hostable"):
        llm.run_review(lws, "9001", "gemini", lws.repo, env=ENV, post=stub, confidential=True)
    # "self-hosted" pointed at NVIDIA's host is still NVIDIA's host
    for env in ({"COUNTERSIGN_SELFHOST_URL": "https://integrate.api.nvidia.com/v1"},
                {**ENV, "COUNTERSIGN_NEMOTRON_BASE_URL": "https://integrate.api.nvidia.com/v1/"}):
        name = "nemotron" if "NVIDIA_API_KEY" in env else "nemotron-selfhost"
        with pytest.raises(SystemExit, match="vendor-hosted endpoint"):
            llm.run_review(lws, "9001", name, lws.repo, env=env, post=stub, confidential=True)
    assert stub.requests == []
    # the self-hosted endpoint is allowed
    r = read_json(llm.run_review(lws, "9001", "nemotron-selfhost", lws.repo, env={"COUNTERSIGN_SELFHOST_URL": "http://127.0.0.1:8000/v1"},
                                 post=stub, confidential=True))
    assert r["runner"]["self_hosted"] is True and r["runner"]["endpoint_host"] == "127.0.0.1"
    assert stub.requests[0]["url"] == "http://127.0.0.1:8000/v1/chat/completions"
    # without --confidential the open-source change still goes to the hosted API as before
    llm.run_review(lws, "9001", "nemotron", lws.repo, env=ENV, post=Stub((200, completion(json.dumps(GOOD)))))


def test_out_must_stay_inside_the_workspace(lws):
    with pytest.raises(SystemExit, match="--out"):
        llm.run_review(lws, "9001", "nemotron-selfhost", lws.repo, env={"COUNTERSIGN_SELFHOST_URL": "http://127.0.0.1:8000/v1"},
                       post=Stub(), out_dir="../elsewhere")


def test_cli_confidential_demo(lws, server, monkeypatch, capsys):
    url, seen = server
    for k, v in {**ENV, **selfhost_env(url)}.items():
        monkeypatch.setenv(k, v)
    base = ["--root", str(lws.root), "--repo", lws.repo]
    with pytest.raises(SystemExit, match="refused"):
        cli.main(["review-llm", "9001", "--reviewer", "nemotron", "--confidential", *base])
    assert seen == []
    assert cli.main(["review-llm", "9001", "--reviewer", "nemotron-selfhost", "--confidential", *base]) == 0
    assert "endpoint 127.0.0.1 (self-hosted: true)" in capsys.readouterr().out


def test_compare_writes_selfhost_measurement(tmp_path):
    """scripts/selfhost/compare.py: per-clause agreement, findings overlap, latency, GPU-hours, cost."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("compare", ROOT / "scripts" / "selfhost" / "compare.py")
    cmp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cmp)

    def review(verdicts, findings, runner):
        return {"reviewer": "nemotron", "model": MODEL, "requirement_verdicts": [{"req": k, "verdict": v} for k, v in verdicts.items()],
                "findings": [{"id": f"N{i}", "title": t, "severity": s, "evidence": [{"kind": "code", "file": f, "line": ln}]}
                             for i, (t, s, f, ln) in enumerate(findings, 1)], "refusals": [], "runner": runner}

    hosted = tmp_path / "reviews" / "9001"
    selfh = tmp_path / "reviews-selfhost" / "9001"
    hosted.mkdir(parents=True)
    selfh.mkdir(parents=True)
    (hosted / "nemotron.json").write_text(json.dumps(review({"R1": "met", "R2": "not_met"}, [("a", "major", "x.cs", 10), ("b", "minor", "y.cs", 3)],
                                                            {"endpoint_host": "integrate.api.nvidia.com"})))
    (hosted / "raw").mkdir()
    (hosted / "raw" / "nemotron.response.json").write_text(json.dumps({"calls": [{"latency_ms": 100000}]}))
    (selfh / "nemotron.json").write_text(json.dumps(review({"R1": "met", "R2": "met"}, [("a2", "major", "x.cs", 12)],
                                                           {"preset": "nemotron-selfhost", "endpoint_host": "127.0.0.1", "self_hosted": True,
                                                            "wall_clock_s": 80.0, "gpu_hours": 0.0444, "usd_estimate": 0.11})))
    md = cmp.render(tmp_path, ["9001", "9002"], box_hours=1.5, gpus=2, rate=2.5)
    assert "| 9001 | 1/2 |" in md and "R2: met vs not_met" in md
    assert "1 of 2 hosted findings" in md.replace("\n", " ") or "| 1/2 |" in md
    assert "9002" in md and "not run" in md
    assert "3.0 GPU-hours" in md and "$7.50" in md


def test_gemma_selfhost_adjudicates_into_reviews_selfhost_without_a_key(lws):
    """The self-hosted adjudicator (Gemma on our vLLM) sits in the mandate's adjudicator slot, needs no API key, logs
    GPU time, and writes reviews-selfhost/<c>/adjudication.gemma.json: the hosted reviews/<c>/adjudication.gemini.json
    is never touched."""
    from conftest import make_review
    from test_llm import Stub
    from countersign.common import write_json
    write_json(lws.inputs / "reviews" / "9001" / "codex.json", make_review("codex", verdict="cannot_determine"))
    ruling = {"rulings": [{"dispute": "REQ-9001-F1", "supported": [], "unsupported": [], "route_to": "Toivo"}]}
    stub = Stub((200, completion(json.dumps(ruling))))
    env = {**selfhost_env("http://127.0.0.1:8000/v1"), "COUNTERSIGN_SELFHOST_MAX_MODEL_LEN": "32768"}
    out = llm.run_adjudication(lws, "9001", lws.repo, adjudicator="gemma-selfhost", env=env, post=stub)
    assert out == lws.inputs / "reviews-selfhost" / "9001" / "adjudication.gemma.json"
    assert not (lws.inputs / "reviews" / "9001" / "adjudication.gemma.json").exists()
    a = read_json(out)
    assert a["reviewer"] == "gemma-selfhost" and a["model"] == "google/gemma-4-31B-it-qat-w4a16-ct" and a["vendor"] == "Google"
    assert a["runner"]["endpoint_host"] == "127.0.0.1" and a["runner"]["self_hosted"] is True and a["runner"]["gpu_hours"] >= 0
    assert a["runner"]["raw"] == "reviews-selfhost/9001/raw/adjudication.gemma.response.json"
    req = stub.requests[0]
    assert req["url"] == "http://127.0.0.1:8000/v1/chat/completions" and "Authorization" not in req["headers"]
    assert req["body"]["max_tokens"] <= 16384
    row = yaml.safe_load((lws.inputs / "measurement" / "costs.yaml").read_text())["runs"][-1]
    assert row["provider"] == "verda" and row["purpose"].startswith("adjudicate 9001 (gemma-selfhost") and row["usd"] is not None
