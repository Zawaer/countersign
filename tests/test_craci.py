"""Offline tests for the supply-chain evidence: deps.delta (countersign/sbom.py), build.egress
(evidence/scripts/build-egress.py) and the token-gated CRACI API pull (countersign/craci.py).
CRACI responses are stubs shaped like https://api.craci.com/openapi.json (NetworkTrace, CycloneDX, Problem)."""

import importlib.util
import json
from pathlib import Path

import pytest

from countersign import craci, sbom

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/countersign.yml"


def _load_script(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), ROOT / "evidence/scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- deps.delta


def _assets(tmp, rel, direct, packages, logs=()):
    """A minimal obj/project.assets.json: packages = {"Name/1.0": {"Child": "1.0"}}."""
    target = {k: {"type": "package", "dependencies": deps} for k, deps in packages.items()}
    doc = {"version": 3, "targets": {"net8.0": target},
           "libraries": {k: {"type": "package", "sha512": "AAEC"} for k in packages},
           "project": {"restore": {"projectName": Path(rel).stem, "projectPath": str(tmp / rel),
                                   "frameworks": {"net8.0": {"projectReferences": {}}}},
                       "frameworks": {"net8.0": {"dependencies": {n: {"target": "Package", "version": f"[{v}, )"} for n, v in direct.items()}}}},
           "logs": list(logs)}
    p = tmp / "obj" / Path(rel).parent / "project.assets.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc))


def _graphs(tmp_path, head_extra=None, head_logs=()):
    b, h = tmp_path / "b", tmp_path / "h"
    pk = {"FluentAssertions/7.0.0": {"System.Configuration.ConfigurationManager": "6.0.0"},
          "System.Configuration.ConfigurationManager/6.0.0": {}}
    _assets(b, "tests/T/T.csproj", {"FluentAssertions": "7.0.0"}, pk)
    hp = dict(pk, **(head_extra or {}))
    direct = {"FluentAssertions": "7.0.0", **({"SharpZipLib": "1.2.0"} if head_extra else {})}
    _assets(h, "tests/T/T.csproj", direct, hp, head_logs)
    return sbom.read_graph(b), sbom.read_graph(h)


def test_unchanged_graph_passes(tmp_path):
    bg, hg = _graphs(tmp_path)
    c = sbom.delta(bg, hg, {}, {})
    assert c["status"] == "pass" and c["packages_added"] == [] and c["new_or_changed"] == []


def test_new_package_with_advisory_fails_and_says_who_pulled_it(tmp_path):
    log = {"code": "NU1903", "message": "Package 'SharpZipLib' 1.2.0 has a known high severity vulnerability, "
                                        "https://github.com/advisories/GHSA-m22m-h4rf-pwq3", "libraryId": "SharpZipLib"}
    bg, hg = _graphs(tmp_path, {"SharpZipLib/1.2.0": {"Tiny.Dep": "2.0.0"}, "Tiny.Dep/2.0.0": {}}, [log])
    c = sbom.delta(bg, hg, {}, {})
    assert c["status"] == "fail"
    added = {x["package"]: x for x in c["packages_added"]}
    assert added["SharpZipLib"]["direct"] and not added["Tiny.Dep"]["direct"]
    assert added["Tiny.Dep"]["via"] == ["tests/T/T.csproj -> SharpZipLib 1.2.0 -> Tiny.Dep 2.0.0"]
    assert [v["advisory"].rsplit("/", 1)[-1] for v in c["vulnerabilities_new"]] == ["GHSA-m22m-h4rf-pwq3"]
    # the mandate may allow named packages; the advisory still fails the check
    c2 = sbom.delta(bg, hg, {}, {}, allowed=["SharpZipLib", "tiny.dep@2.0.0"])
    assert c2["status"] == "fail" and len(c2["fail_reasons"]) == 1 and "vulnerabilit" in c2["fail_reasons"][0]


def test_version_change_and_new_feed_fail(tmp_path):
    bg, hg = _graphs(tmp_path)
    key = ("FluentAssertions", "7.0.0")
    hg["packages"][("FluentAssertions", "7.2.0")] = hg["packages"].pop(key)
    feeds_b = {"package_sources": {"nuget.config:nuget": "https://api.nuget.org/v3/index.json"}}
    feeds_h = {"package_sources": {**feeds_b["package_sources"], "nuget.config:x": "https://pkgs.example.net/v3/index.json"}}
    c = sbom.delta(bg, hg, feeds_b, feeds_h)
    assert c["status"] == "fail"
    assert c["versions_changed"][0]["from"] == ["7.0.0"] and c["versions_changed"][0]["to"] == "7.2.0"
    assert any("pkgs.example.net" in r for r in c["fail_reasons"])
    assert "package_sources" in c["build_inputs_changed"]


def test_cyclonedx_is_deterministic_and_hex_hashed(tmp_path):
    _, hg = _graphs(tmp_path)
    d1 = sbom.cyclonedx(hg, {}, name="x", sha="abc", sdk="8.0.402")
    d2 = sbom.cyclonedx(sbom.read_graph(tmp_path / "h"), {}, name="x", sha="abc", sdk="8.0.402")
    assert d1 == d2 and d1["serialNumber"].startswith("urn:uuid:") and d1["specVersion"] == "1.6"
    fa = next(c for c in d1["components"] if c["name"] == "FluentAssertions")
    assert fa["purl"] == "pkg:nuget/FluentAssertions@7.0.0" and fa["hashes"][0]["content"] == "000102"
    sbom.write_json(tmp_path / "s.json", d1)
    assert json.loads((tmp_path / "s.json").read_text()) == d1


def test_committed_facts_carry_deps_delta():
    for n in ("2283", "2234", "2129", "2297"):
        f = json.loads((ROOT / "evidence" / n / "facts.json").read_text())
        c = next(c for c in f["checks"] if c["id"] == "deps.delta")
        assert c["status"] == "pass" and (ROOT / c["sbom"]["head"]).exists()
    c2129 = next(c for c in json.loads((ROOT / "evidence/2129/facts.json").read_text())["checks"] if c["id"] == "deps.delta")
    assert c2129["projects_added"] == ["tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj"]


# ---------------------------------------------------------------- build.egress


def test_egress_policy_is_read_from_the_workflow():
    eg = _load_script("build-egress")
    text = eg.policy_block(str(WORKFLOW), "facts")
    pol = eg.parse_policy(text)
    assert pol["default"] == "deny"
    assert "api.nuget.org" in pol["tls_server_name_patterns"] and pol["ports"] == [443]
    assert isinstance(pol["presets"], list), "presets must be explicit: omitting them enables every built-in preset"
    assert eg.allowed("www.nuget.org", pol["tls_server_name_patterns"])
    assert not eg.allowed("evil.example.com", pol["tls_server_name_patterns"])


def test_egress_finds_blocked_host_in_logs(tmp_path):
    eg = _load_script("build-egress")
    (tmp_path / "build.log").write_text("ok\n  error NU1301: Unable to load the service index for source https://pkgs.example.net/v3/index.json.\n")
    hits, n = eg.blocked_in_logs([str(tmp_path)])
    assert n == 1 and hits[0]["hosts"] == ["pkgs.example.net"]


# ---------------------------------------------------------------- CRACI API (stubbed)


TRACE = {"schemaVersion": "1", "job": {"provider": "github", "repository": "Zawaer/countersign", "runId": "1", "jobId": "77",
                                       "runAttempt": 1, "commitSha": "abc", "branch": "craci-wip", "workflow": "countersign",
                                       "jobName": "facts", "status": "success"},
         "observations": [
             {"sequence": 0, "observedAt": "2026-11-14T00:00:00Z", "protocol": "dns",
              "dns": {"nameserverIp": "10.0.0.1", "record": "api.nuget.org A", "response": "1.2.3.4"}},
             {"sequence": 1, "observedAt": "2026-11-14T00:00:01Z", "protocol": "tcp",
              "tcp": {"remoteIp": "1.2.3.4", "resolvedHosts": ["api.nuget.org"], "port": 443, "bytesToRemote": "2000",
                      "bytesFromRemote": "5000000", "allowed": True, "tlsAlpn": ["h2"], "tlsServerName": "api.nuget.org",
                      "matchedRule": "connections[0].tls"}},
             {"sequence": 2, "observedAt": "2026-11-14T00:00:02Z", "protocol": "ssh_git",
              "sshGit": {"host": "github.com", "port": 22, "user": "git", "service": "git-upload-pack", "repoPath": "x/y",
                         "originUrl": "git@github.com:x/y", "allowed": True, "bytesToUpstream": "10", "bytesFromUpstream": "900",
                         "depthForced": False}}]}
DENIED = {"sequence": 3, "observedAt": "2026-11-14T00:00:03Z", "protocol": "http",
          "http": {"method": "GET", "originUrl": "https://telemetry.example.com/collect", "ipAddress": "5.6.7.8", "statusCode": 403,
                   "bodySizeBytes": "0", "policyDenied": True, "denyReason": "no_match", "matchedRule": None}}
SBOM = {"bomFormat": "CycloneDX", "specVersion": "1.7", "serialNumber": "urn:uuid:1",
        "components": [{"type": "library", "name": "y", "purl": "pkg:github/x/y@abc"}]}


def _stub(responses, calls):
    def get(url, headers):
        calls.append((url, headers))
        for key, val in responses.items():
            if key in url:
                return val.pop(0) if isinstance(val, list) else val
        return 404, b'{"type":"about:blank","title":"Not Found","status":404,"detail":"unknown"}'
    return get


def _facts(tmp_path):
    d = tmp_path / "evidence" / "2129"
    d.mkdir(parents=True)
    f = d / "facts.json"
    f.write_text(json.dumps({"change": "2129", "checks": [
        {"id": "build", "status": "pass"},
        {"id": "build.egress", "status": "pass", "policy": {"tls_server_name_patterns": ["api.nuget.org", "*.nuget.org"]}}]}, indent=2))
    return f


def test_without_token_both_checks_skip_and_nothing_is_called(tmp_path):
    f = _facts(tmp_path)
    calls = []
    checks = craci.attach(f, "Zawaer/countersign", "1", env={}, get=_stub({}, calls))
    assert calls == []
    assert [(c["id"], c["status"], c["reason"]) for c in checks] == [("craci.sbom", "skipped", "no CRACI_API_TOKEN"),
                                                                      ("craci.network", "skipped", "no CRACI_API_TOKEN")]
    assert [c["id"] for c in json.loads(f.read_text())["checks"]] == ["build", "build.egress", "craci.sbom", "craci.network"]


def test_with_token_attaches_sbom_and_trace(tmp_path):
    f = _facts(tmp_path)
    calls = []
    jobs = {"jobs": [{"id": 76, "name": "pipeline (tests)"}, {"id": 77, "name": "facts (stage 1)"}]}
    get = _stub({"/actions/runs/1/jobs": (200, json.dumps(jobs).encode()),
                 "/v1preview1/sbom": [(409, b'{"title":"Conflict","detail":"Job is not terminal"}'), (200, json.dumps(SBOM).encode())],
                 "/v1preview1/network-trace": (200, json.dumps(TRACE).encode())}, calls)
    checks = {c["id"]: c for c in craci.attach(f, "Zawaer/countersign", "1", env={"CRACI_API_TOKEN": "s3cret"}, get=get, sleep=lambda s: None)}
    assert checks["craci.sbom"]["status"] == "pass" and checks["craci.sbom"]["source"]["job_id"] == "77"
    assert checks["craci.network"]["run_url"] == "https://github.com/Zawaer/countersign/actions/runs/1"
    assert checks["craci.sbom"]["nuget_seen_by_craci"] == 0 and "no NuGet source type" in checks["craci.sbom"]["summary"]
    net = checks["craci.network"]
    assert net["status"] == "pass" and net["dns_queries"] == 1
    assert [h["host"] for h in net["hosts"]] == ["api.nuget.org", "github.com"]
    assert net["allowed_hosts_outside_declared_tls_patterns"] == ["github.com"]
    sbom_calls = [u for u, _ in calls if "/v1preview1/sbom" in u]
    assert len(sbom_calls) == 2 and "provider=github" in sbom_calls[0] and "job_id=77" in sbom_calls[0]
    assert all(h["Authorization"] == "Bearer s3cret" for u, h in calls if "craci" in u)
    assert "s3cret" not in f.read_text() and (f.parent / "craci" / "network-trace.json").exists()


def test_proxy_violation_fails_with_the_host(tmp_path):
    t = json.loads(json.dumps(TRACE))
    t["observations"].append(DENIED)
    out = craci.summarize_trace(t, ["api.nuget.org"])
    assert out["status"] == "fail" and "telemetry.example.com (no_match)" in out["summary"]


def test_unknown_nuget_in_craci_sbom_fails(tmp_path):
    ours = [{"components": [{"purl": "pkg:nuget/FluentAssertions@7.0.0"}]}]
    doc = {"components": [{"purl": "pkg:nuget/FluentAssertions@7.0.0"}, {"purl": "pkg:nuget/Evil@1.0.0"}]}
    assert craci.summarize_sbom(doc, ours)["status"] == "fail"
    assert craci.summarize_sbom({"components": doc["components"][:1]}, ours)["status"] == "pass"


def test_rejected_token_is_an_error_not_a_crash(tmp_path):
    f = _facts(tmp_path)
    get = _stub({"/v1preview1/": (401, b'{"type":"about:blank","title":"Unauthorized","status":401,"detail":"revoked token"}')}, [])
    checks = craci.attach(f, "Zawaer/countersign", "1", env={"CRACI_API_TOKEN": "x", "CRACI_JOB_ID": "77"}, get=get)
    assert {c["status"] for c in checks} == {"error"} and "revoked token" in checks[0]["summary"]


def test_plain_403_is_reported_as_blocked_egress_not_an_api_answer(tmp_path):
    # What all four craci jobs got on 2026-11-14 (runs 43580280041..43580303397): no problem+json, so not the API.
    f = _facts(tmp_path)
    get = _stub({"/v1preview1/": (403, b"Access denied\r\n")}, [])
    checks = craci.attach(f, "Zawaer/countersign", "1", env={"CRACI_API_TOKEN": "x", "CRACI_JOB_ID": "77"}, get=get)
    assert {c["status"] for c in checks} == {"error"}
    assert "never reached the CRACI API" in checks[0]["summary"] and "api.craci.com" in checks[0]["summary"]


def _denied(seq, url, at="2026-11-14T00:00:10.5Z"):
    return {"sequence": seq, "observedAt": at, "protocol": "http",
            "http": {"method": "GET", "originUrl": url, "ipAddress": "5.6.7.8", "statusCode": 403, "bodySizeBytes": "9",
                     "policyDenied": True, "denyReason": "request does not match an allowed proxy policy rule", "matchedRule": None}}


# A real OCSP GET from the facts job (run 43580812697): base64 DER OCSPRequest with a SHA-1 CertID.
OCSP = "http://ocsp.digicert.com/MFEwTzBNMEswSTAJBgUrDgMCGgUABBT3xL4LQLXDRDM9P665TW442vrsUQQUReuir%2FSSy4IxLVGLp6chnfNtyA8CEA6bGI750C3n79tQ4ghAGFo%3D"


def test_revocation_lookups_and_setup_requests_are_listed_but_not_violations():
    t = json.loads(json.dumps(TRACE))
    setup = _denied(9, "https://aka.ms/dotnet/9.0/dotnet-sdk-linux-x64.tar.gz", "2026-11-14T00:00:00.9Z")
    setup["http"] = {**setup["http"], "method": "HEAD"}
    t["observations"] += [setup, _denied(10, "http://crl3.digicert.com/sha2-assured-cs-g1.crl"), _denied(11, OCSP), _denied(12, OCSP)]
    steps = [{"name": "Run actions/setup-dotnet", "started_at": "2026-11-14T00:00:00Z"},
             {"name": "Reproduce stage 1 (evidence/scripts/ci-facts.sh)", "started_at": "2026-11-14T00:00:01Z"}]
    out = craci.summarize_trace(t, ["api.nuget.org"], steps)
    assert out["status"] == "pass" and out["proxy_violations"] == []
    assert {(g["host"], g["count"]) for g in out["denied_certificate_status"]} == {("crl3.digicert.com", 1), ("ocsp.digicert.com", 2)}
    assert [g["host"] for g in out["denied_during_toolchain_setup"]] == ["aka.ms"]
    assert "3 certificate revocation lookups" in out["summary"] and "before the change was built (aka.ms)" in out["summary"]
    # The same aka.ms request during the build is the change's, and fails; so is any other GET to a CRL/OCSP host.
    late = craci.summarize_trace(t, ["api.nuget.org"], steps[:1])
    assert late["status"] == "fail" and [g["host"] for g in late["proxy_violations"]] == ["aka.ms"]
    t["observations"].append(_denied(13, "http://ocsp.digicert.com/upload?data=c2VjcmV0"))
    assert craci.summarize_trace(t, ["api.nuget.org"], steps)["status"] == "fail"


@pytest.mark.parametrize("url,expected", [(OCSP, True), ("http://crl4.digicert.com/DigiCertAssuredIDRootCA.crl", True),
                                          ("https://crl4.digicert.com/x.crl", False), ("http://ocsp.digicert.com/aGVsbG8gd29ybGQgdGhpcyBpcyBub3Qgb2NzcA==", False)])
def test_certificate_status_request_is_recognised_from_the_request(url, expected):
    assert craci.certificate_status_request({"method": "GET", "originUrl": url}) is expected


@pytest.mark.parametrize("argv", [[], ["nope"]])
def test_cli_usage(argv):
    assert craci.main(argv) == 2
