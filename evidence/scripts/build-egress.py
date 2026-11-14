#!/usr/bin/env python3
"""build.egress: the network policy the build of this change ran under, recorded as provenance in facts.json.

usage: build-egress.py <facts.json> --workflow .github/workflows/countersign.yml --job facts --logs DIR [DIR ...]

The facts job runs on CRACI behind a deny-by-default policy (cracicorp/setup@v1, `network:`). This script copies
that policy out of the workflow file into the check, with its sha256, the run that used it and the CRACI job CA's
fingerprint (the proxy that enforced it), so the pack can say "the build of this change reached only these hosts".
It then looks for what a blocked connection looks like from inside a job (docs.craci.com: HTTP 403, connection
reset/EOF, handshake failure; for NuGet NU1301 "Unable to load the service index") in the run's logs, and fails
with the host when it finds one. It also checks the NuGet feeds the head's nuget.config declares (from the head
SBOM written by deps-delta.py) against the allowlist: a feed outside it would be blocked, so the build would not
be the build the change asked for.

The per-connection record (every host, bytes, the rule that matched, proxy violations) is CRACI's network trace;
countersign/craci.py attaches it as craci.network when a CRACI API token exists. This check is what the job can
know about itself without one.
"""
import fnmatch
import hashlib
import json
import os
import re
import sys
from pathlib import Path

CA = "/usr/local/share/ca-certificates/craci.crt"
BLOCK = re.compile(r"NU1301|403 \(Forbidden\)|\b403 Forbidden|Connection reset by peer|The SSL connection could not be established|"
                   r"unexpected EOF|handshake failure|Received an unexpected EOF", re.I)
URL = re.compile(r"https?://([A-Za-z0-9.-]+)")


def policy_block(workflow: str, job: str) -> str:
    """The literal `network: |` block of the cracicorp/setup step of `job`."""
    lines = Path(workflow).read_text().splitlines()
    i = next(k for k, l in enumerate(lines) if re.match(rf"^  {re.escape(job)}:\s*$", l))
    end = next((k for k in range(i + 1, len(lines)) if re.match(r"^  \S", lines[k])), len(lines))
    s = next(k for k in range(i, end) if "cracicorp/setup@" in lines[k])
    n = next(k for k in range(s, end) if re.match(r"^\s+network:\s*\|", lines[k]))
    ind = len(lines[n]) - len(lines[n].lstrip())
    out = []
    for l in lines[n + 1:end]:
        if l.strip() and len(l) - len(l.lstrip()) <= ind:
            break
        out.append(l)
    body = [l for l in out if l.strip()]
    cut = min(len(l) - len(l.lstrip()) for l in body)
    return "\n".join(l[cut:] for l in out).strip() + "\n"


def parse_policy(text: str) -> dict:
    flat = re.sub(r"\s*\n\s*", " ", text)
    lists = lambda key: [x.strip().strip("\"'") for m in re.finditer(rf"{key}:\s*\[(.*?)\]", flat) for x in m[1].split(",") if x.strip()]  # noqa: E731
    d = re.search(r"default:\s*(\w+)", text)
    pre = re.search(r"presets:\s*\[(.*?)\]", flat)
    return {"default": d[1] if d else "allow (no network input)" if not text.strip() else "deny",
            "presets": [x.strip() for x in pre[1].split(",") if x.strip()] if pre else "all (presets omitted)",
            "tls_server_name_patterns": lists("serverNamePatterns"), "tcp_host_patterns": lists("hostPatterns"),
            "cidrs": lists("cidrs"), "ports": sorted({int(p) for p in lists("ports") if p.isdigit()})}


def allowed(host: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(host.lower(), p.lower()) and (not p.startswith("*.") or host.count(".") >= p.count("."))
               for p in patterns)


def blocked_in_logs(dirs: list[str]) -> tuple[list[dict], int]:
    hits, n = [], 0
    for d in dirs:
        for f in sorted(Path(d).rglob("*.log")) if Path(d).is_dir() else []:
            n += 1
            for i, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
                if BLOCK.search(line):
                    hosts = sorted(set(URL.findall(line))) or ["(no host in the line)"]
                    hits.append({"log": str(f), "line": i, "hosts": hosts, "text": line.strip()[:300]})
    return hits, n


def feeds(sbom_path: Path) -> dict:
    if not sbom_path.exists():
        return {}
    props = {p["name"]: p["value"] for p in json.loads(sbom_path.read_text())["metadata"].get("properties", [])}
    return json.loads(props.get("countersign:package_sources", "{}"))


def main():
    a = sys.argv
    facts_path = Path(a[1])
    wf, job = a[a.index("--workflow") + 1], a[a.index("--job") + 1]
    logs = a[a.index("--logs") + 1:] if "--logs" in a else []
    facts = json.loads(facts_path.read_text())
    text = policy_block(wf, job)
    pol = parse_policy(text)
    on_craci = os.path.exists(CA)
    env = os.environ
    run_url = f"{env.get('GITHUB_SERVER_URL', 'https://github.com')}/{env.get('GITHUB_REPOSITORY', '')}/actions/runs/{env.get('GITHUB_RUN_ID', '')}"
    prov = {"workflow": wf, "job": job, "workflow_commit": env.get("GITHUB_SHA"), "run": run_url if env.get("GITHUB_RUN_ID") else None,
            "run_attempt": env.get("GITHUB_RUN_ATTEMPT"), "runner_name": env.get("RUNNER_NAME"),
            "craci_job_ca": {"path": CA, "sha256": hashlib.sha256(Path(CA).read_bytes()).hexdigest()} if on_craci else None,
            "craci_env": sorted(k for k in env if k.upper().startswith("CRACI"))}
    hits, nlogs = blocked_in_logs(logs)
    hosts = sorted({h for x in hits for h in x["hosts"]})
    fd = feeds(facts_path.parent / "sbom.cdx.json")
    feed_hosts = {k: URL.match(v)[1] for k, v in fd.items() if URL.match(v)}  # local folder feeds need no network
    outside = {k: h for k, h in feed_hosts.items() if not allowed(h, pol["tls_server_name_patterns"])}
    check = {"id": "build.egress", "tool": "CRACI network policy (cracicorp/setup@v1) + job log scan", "policy": pol,
             "policy_text": text, "policy_sha256": hashlib.sha256(text.encode()).hexdigest(), "provenance": prov,
             "logs_scanned": nlogs, "blocked": hits[:50], "blocked_hosts": hosts,
             "nuget_feeds_on_head": fd, "nuget_feeds_outside_policy": outside,
             "authoritative_record": "craci.network (CRACI network trace via the API; needs CRACI_API_TOKEN), or the job's View trace in the CRACI app"}
    patt = pol["tls_server_name_patterns"]
    if not on_craci:
        check |= {"status": "skipped", "reason": "not run under a CRACI network policy (no CRACI job CA on this machine)",
                  "summary": "not run under a CRACI network policy: the build's egress was not constrained or recorded"}
    elif pol["default"] != "deny":
        check |= {"status": "fail", "summary": f"the build ran with default: {pol['default']}: its egress is not constrained, so it proves nothing"}
    elif hosts or outside:
        why = []
        if hosts:
            why.append(f"blocked connection(s) in the build logs to {', '.join(hosts)} (CRACI proxy violation: see the job's View trace)")
        if outside:
            why.append(f"nuget.config feed(s) outside the policy: {', '.join(sorted(set(outside.values())))}")
        check |= {"status": "fail", "summary": "; ".join(why)}
    else:
        check |= {"status": "pass",
                  "summary": (f"built on CRACI under a deny-by-default policy: only {len(patt)} TLS host patterns on ports "
                              f"{', '.join(map(str, pol['ports']))} ({', '.join(patt[:6])}{', ...' if len(patt) > 6 else ''}); "
                              f"presets {pol['presets'] or 'none'}; no blocked connection in {nlogs} logs; "
                              f"every NuGet feed the head declares is inside the policy")}
    facts["checks"] = [c for c in facts["checks"] if c["id"] != "build.egress"] + [check]
    facts_path.write_text(json.dumps(facts, indent=2))
    print("build.egress", check["status"], "-", check["summary"])


if __name__ == "__main__":
    main()
