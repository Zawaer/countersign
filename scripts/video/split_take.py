"""Split one continuous take into b01..b14 using Whisper word times matched to the script words."""
import json, re, subprocess, sys, difflib, pathlib  # noqa: E401
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import v2_voice as v
mp3, wjson, out = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
W = json.load(open(wjson))
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
# Whisper may merge or split tokens ("agent -written"); compare on characters, keyed to script words
script = [(k, w) for k, (_, _, _, t) in enumerate(v.LINES) for w in t.split()]
sw = [norm(w) for _, w in script]
ww = [norm(w[0]) for w in W]
times = [None] * len(script)
sm = difflib.SequenceMatcher(a=sw, b=ww, autojunk=False)
for a, b, n in sm.get_matching_blocks():
    for i in range(n):
        times[a + i] = (W[b + i][1], W[b + i][2])
# fill gaps by interpolation between neighbours
idx = [i for i, t in enumerate(times) if t]
for i in range(len(times)):
    if times[i] is None:
        p = max([j for j in idx if j < i], default=None); q = min([j for j in idx if j > i], default=None)
        t0 = times[p][1] if p is not None else 0.0
        t1 = times[q][0] if q is not None else t0 + 0.4
        times[i] = (t0, t1)
print("matched", len(idx), "of", len(script), "script words")
nl = len(v.LINES)
first = [min(i for i, (k, _) in enumerate(script) if k == L) for L in range(nl)]
last = [max(i for i, (k, _) in enumerate(script) if k == L) for L in range(nl)]
cuts = [0.0] + [times[last[L]][1] + min(0.12, max(0.0, (times[first[L + 1]][0] - times[last[L]][1]) / 2)) for L in range(nl - 1)] + [None]
out.mkdir(parents=True, exist_ok=True)
for L, (lid, _, _, text) in enumerate(v.LINES):
    a, b = cuts[L], cuts[L + 1]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ss", f"{a:.3f}"] + (["-to", f"{b:.3f}"] if b else []) +
                   ["-c:a", "libmp3lame", "-q:a", "2", str(out / f"{lid}.mp3")], check=True)
    chars, st, en = [], [], []
    for n, i in enumerate(range(first[L], last[L] + 1)):
        w = script[i][1]; t0, t1 = times[i][0] - a, times[i][1] - a
        if n:
            chars.append(" "); st.append(t0); en.append(t0)
        for c in w:
            chars.append(c); st.append(max(0.0, t0)); en.append(max(0.0, t1))
    json.dump({"characters": chars, "character_start_times_seconds": st, "character_end_times_seconds": en,
               "source": "whisper-small.en"}, open(out / f"{lid}.align.json", "w"))
    print(lid, f"{a:6.2f}-{(b or 0):6.2f}", text[:40])
