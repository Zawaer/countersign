#!/usr/bin/env python3
"""Self-hosted Nemotron against the hosted one: writes measurement/selfhost.md.

    python3 scripts/selfhost/compare.py --box-hours 1.6 [--gpus 2] [--rate 2.29] [--repo /data/src/mp] <changes...>

Inputs: reviews/<c>/nemotron.json (Nemotron 3.5 Super 120B on NVIDIA's hosted API, committed) and
reviews-selfhost/<c>/nemotron.json (Nemotron 3.5 Lightning 30B on our vLLM, one A100). Two different models, same
prompt and context: this measures what a confidential repo gives up by running the smaller model on its own GPU.
Per change: per-clause verdict agreement, findings overlap (same file within LINE_WINDOW lines, or the same title),
latency, GPU-hours and estimated cost of the calls. With --repo, each change's pack is also built twice in a scratch
workspace (hosted Nemotron vs self-hosted Nemotron in the nemotron slot; everything else identical, trust events
ignored) to show whether the tier, or the planted-line catch on a seeded change, would move. The committed packs are
never touched. The bill is --box-hours x --gpus x --rate: the whole time the box existed, idle included.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINE_WINDOW = 10


def _read(p: Path) -> dict | None:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _anchors(f: dict) -> set[tuple[str, int]]:
    return {(e["file"], int(e["line"])) for e in f.get("evidence", [])
            if e.get("kind") == "code" and e.get("file") and isinstance(e.get("line"), int)}


def _same_finding(a: dict, b: dict) -> bool:
    if a.get("title", "").strip().lower() == b.get("title", "").strip().lower():
        return True
    return any(fa == fb and abs(la - lb) <= LINE_WINDOW for fa, la in _anchors(a) for fb, lb in _anchors(b))


def _hosted_latency_s(root: Path, change: str) -> float | None:
    raw = _read(root / "reviews" / change / "raw" / "nemotron.response.json")
    return round(sum(c.get("latency_ms", 0) for c in raw["calls"]) / 1000, 1) if raw else None


def _packs(root: Path, change: str, repo: str) -> tuple[dict, dict] | None:
    """(hosted pack, self-hosted pack), built the same way in a scratch workspace; None if it cannot be built."""
    sys.path.insert(0, str(ROOT))
    from countersign import measure, pack
    from countersign.common import Workspace
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        for which in ("reviews", "reviews-selfhost"):
            inputs = Path(tmp) / which
            shutil.copytree(root / "evidence" / change, inputs / "evidence" / change)
            shutil.copytree(root / "reviews" / change, inputs / "reviews" / change, ignore=shutil.ignore_patterns("raw"))
            shutil.copy(root / which / change / "nemotron.json", inputs / "reviews" / change / "nemotron.json")
            try:
                p = pack.build(Workspace.at(root, inputs, repo), change, use_trust=False)
            except (SystemExit, Exception) as e:  # noqa: BLE001 - report, don't crash the whole comparison
                print(f"{change}: pack not built ({type(e).__name__}: {e})", file=sys.stderr)
                return None
            p["_planted"] = measure.planted_line_hits(p).get("nemotron") if p.get("mutation") else None
            out.append(p)
    return out[0], out[1]


def render(root: Path, changes: list[str], box_hours: float | None, gpus: int, rate: float | None, repo: str | None = None) -> str:
    rows, details = [], []
    tot = {"clauses": 0, "agree": 0, "hf": 0, "hf_matched": 0, "sf": 0, "sf_matched": 0, "gpu_h": 0.0, "usd": 0.0, "usd_known": True,
           "wall": 0.0, "ran": 0}
    for c in changes:
        hosted, selfh = (_read(root / d / c / "nemotron.json") for d in ("reviews", "reviews-selfhost"))
        if not selfh or not hosted:
            rows.append(f"| {c} | not run | {'no self-hosted review' if not selfh else 'no hosted review'} | - | - | - | - | - | - |")
            continue
        tot["ran"] += 1
        hv = {v["req"]: v["verdict"] for v in hosted["requirement_verdicts"]}
        sv = {v["req"]: v["verdict"] for v in selfh["requirement_verdicts"]}
        reqs = sorted(set(hv) | set(sv))
        agree = [r for r in reqs if hv.get(r) == sv.get(r)]
        diff = [f"{r}: {sv.get(r, 'none')} vs {hv.get(r, 'none')}" for r in reqs if r not in agree]
        hf, sf = hosted.get("findings", []), selfh.get("findings", [])
        hm = sum(1 for f in hf if any(_same_finding(f, g) for g in sf))
        sm = sum(1 for g in sf if any(_same_finding(f, g) for f in hf))
        run = selfh.get("runner", {})
        tot.update(clauses=tot["clauses"] + len(reqs), agree=tot["agree"] + len(agree), hf=tot["hf"] + len(hf), hf_matched=tot["hf_matched"] + hm,
                   sf=tot["sf"] + len(sf), sf_matched=tot["sf_matched"] + sm, gpu_h=tot["gpu_h"] + (run.get("gpu_hours") or 0),
                   wall=tot["wall"] + (run.get("wall_clock_s") or 0))
        if run.get("usd_estimate") is None:
            tot["usd_known"] = False
        else:
            tot["usd"] += run["usd_estimate"]
        usd = "unknown" if run.get("usd_estimate") is None else f"${run['usd_estimate']:.2f}"
        rows.append(f"| {c} | {len(agree)}/{len(reqs)} | {'; '.join(diff) or 'none'} | {hm}/{len(hf)} | {sm}/{len(sf)} | "
                    f"{_hosted_latency_s(root, c)} / {run.get('wall_clock_s')} | {run.get('gpu_hours')} | {usd} | "
                    f"{run.get('endpoint_host', '?')}{' (self-hosted)' if run.get('self_hosted') else ''} |")
        if repo:
            pk = _packs(root, c, repo)
            if pk:
                h, s = pk
                proven = [sum(1 for r in x["requirements"] if r["status"] == "proven") for x in (h, s)]
                line = (f"- **{c}**: AI recommendation {h['ai_recommendation']} with the hosted review, {s['ai_recommendation']} "
                        f"with the self-hosted one; clauses proven {proven[0]} vs {proven[1]} of {len(h['requirements'])}; "
                        f"final tier {h['tier']} vs {s['tier']}")
                if h.get("mutation"):
                    line += (f"; planted line flagged: hosted {'yes' if h['_planted'] else 'no'}, "
                             f"self-hosted {'yes' if s['_planted'] else 'no'}")
                details.append(line + ".")
    models = sorted({(_read(root / "reviews-selfhost" / c / "nemotron.json") or {}).get("model") for c in changes} - {None})
    out = ["# Self-hosted Nemotron (30B, our GPU) vs hosted Nemotron (120B, NVIDIA's API)", "",
           "_Written by `scripts/selfhost/compare.py` from `reviews/<c>/nemotron.json` (Nemotron 3.5 Super 120B-A12B on "
           "NVIDIA's hosted API, committed) and `reviews-selfhost/<c>/nemotron.json` ("
           + (", ".join(models) or "Nemotron 3.5 Lightning 30B-A3B") + " on vLLM, one A100 80GB at Verda). "
           "Not the same model: the 120B does not fit one A100. Same prompt, same blind context (unless the row's "
           "context was shrunk to the server's window), both single samples at temperature 0.6, so some disagreement "
           "is sampling noise._", "",
           "| Change | Clauses agree | Disagreements (self-hosted vs hosted) | Hosted findings matched | Self-hosted findings matched "
           "| Latency hosted / self-hosted (s) | GPU-hours (calls) | Est. cost (calls) | Endpoint |",
           "|---|---|---|---|---|---|---|---|---|", *rows, ""]
    if tot["ran"]:
        out += [f"**Totals over {tot['ran']} changes:** clauses agree {tot['agree']}/{tot['clauses']}; hosted findings also found self-hosted "
                f"{tot['hf_matched']}/{tot['hf']}; self-hosted findings also found hosted {tot['sf_matched']}/{tot['sf']}; "
                f"model wall-clock {tot['wall'] / 60:.1f} min; GPU-hours in calls {tot['gpu_h']:.2f}"
                + (f" (est. ${tot['usd']:.2f})" if tot["usd_known"] else "") + ".", ""]
    if details:
        out += ["## Would the pack change?", "",
                "_Each pack built twice in a scratch workspace, only the nemotron review swapped; trust events ignored. "
                "AI recommendation = the tier under the mandate's caps, from the reviews; the final tier also applies the "
                "release gate, which holds the 30B (a model version the mandate has not released) at ask. "
                "The committed packs use the hosted reviews and are not changed._", "", *details, ""]
    out += ["## What the box cost", ""]
    if box_hours is not None:
        gh = box_hours * gpus
        out.append(f"The box existed for {box_hours} h with {gpus} GPU(s): {gh:.1f} GPU-hours"
                   + (f" x ${rate}/GPU-hour = ${gh * rate:.2f}" if rate is not None else " (no rate given)")
                   + ". That is the bill: it includes provisioning, the model download and idle time, which the per-call numbers above leave out.")
    else:
        out.append("Box time not given (--box-hours): only the per-call GPU time above is known.")
    out += ["", "Matching: a finding matches if it has the same title or cites the same file within "
            f"{LINE_WINDOW} lines. Findings are unverified here; the pack verifies them.", ""]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("changes", nargs="+")
    ap.add_argument("--box-hours", type=float, default=None, help="how long the GPU box existed (create to delete)")
    ap.add_argument("--gpus", type=int, default=2)
    ap.add_argument("--rate", type=float, default=None, help="USD per GPU-hour (default: $COUNTERSIGN_GPU_USD_PER_HOUR)")
    ap.add_argument("--repo", default=None, help="MessagePack clone: also build both packs and compare tiers")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out", default="measurement/selfhost.md")
    a = ap.parse_args(argv)
    import os
    rate = a.rate if a.rate is not None else (float(os.environ["COUNTERSIGN_GPU_USD_PER_HOUR"]) if os.environ.get("COUNTERSIGN_GPU_USD_PER_HOUR") else None)
    root = Path(a.root).resolve()
    out = root / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(root, a.changes, a.box_hours, a.gpus, rate, a.repo), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
