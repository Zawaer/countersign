"""Voice-over for the v2 demo video: one ElevenLabs clip per line, cached like v1 (same voice, model,
settings and cache folder), with per-character timestamps. The key is read from KEY_FILE in-process and
never printed. Run directly to (re)generate: uv run python scripts/video/v2_voice.py  -> WORK/v2/voice/lines.json
"""
import base64, hashlib, json, os, pathlib, re, subprocess, sys, urllib.request, wave

WORK = pathlib.Path(os.environ.get("VIDEO_WORK", "/data/work/video"))
KEY_FILE = pathlib.Path(os.environ.get("ELEVENLABS_KEY_FILE", "/data/work/secrets/elevenlabs.key"))
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # "George" (same as v1)
MODEL = "eleven_multilingual_v2"
VOICE_SETTINGS = {"stability": 0.55, "similarity_boost": 0.75, "style": 0.0, "use_speaker_boost": True, "speed": 0.95}
SR = 44100

# (line id, shot id, text). Every number is from scripts/sync_numbers.py or the page on screen.
LINES = [
    ("b01", "s01", "An AI agent wrote this fix. It builds, all 175 tests pass, and an AI reviewer says every requirement is met."),
    ("b02", "s01", "But it fixes the wrong bug."),
    ("b03", "s02", "Countersign reviews agent-written code under a signed mandate, which decides what AI may clear alone."),
    ("b04", "s02", "Facts come first: the build, the tests, and whether each new test fails without the fix."),
    ("b05", "s03", "Then three AI reviewers from three vendors. Every citation is re-checked, and what can't be proven is refused."),
    ("b06", "s04", "Back to our fix. The line behind the reported bug is one the fix never touches."),
    ("b07", "s05", "Undo the fix, and 4 of its 8 new tests still pass. They prove nothing."),
    ("b08", "s06", "A reviewer found a crash the fix leaves in, and the pipeline reproduced it."),
    ("b09", "s07", "So the AI won't clear it. It asks the named owner, Toivo."),
    ("b10", "s08", "On GitHub, Toivo signed a request for changes. The required check fails, and the merge is blocked."),
    ("b11", "s09", "A low-risk docs fix is different: the AI cleared it alone, and it merged in 40 seconds."),
    ("b12", "s10", "Every sign-off goes into a signed, hash-chained ledger. Edit one line, and the check fails."),
    ("b13", "s11", "Measured: 11 of 11 later-reverted real pull requests were sent to a human. Tests and checks caught 14 of 18 planted bugs. And 35 attacks on our own pipeline: all 35 stopped."),
    ("b14", "s12", "Countersign. AI clears what it can prove, refuses what it can't, and a named human countersigns the rest."),
]

# Caption chunks where the compositor's automatic split reads oddly (must join back to the line's text).
CAPTIONS = {
    "b07": ["Undo the fix,", "and 4 of its 8 new tests", "still pass.", "They prove nothing."],
    "b12": ["Every sign-off goes into", "a signed, hash-chained ledger.", "Edit one line,", "and the check fails."],
    "b13": ["Measured: 11 of 11", "later-reverted real pull requests", "were sent to a human.", "Tests and checks caught",
            "14 of 18 planted bugs.", "And 35 attacks on our own pipeline:", "all 35 stopped."],
}


def tts(text, prev_text, next_text, stats):
    adir = WORK / "audio"
    adir.mkdir(parents=True, exist_ok=True)
    req = {"text": text, "model_id": MODEL, "voice_settings": VOICE_SETTINGS,
           "previous_text": prev_text or None, "next_text": next_text or None}
    h = hashlib.sha256(json.dumps([VOICE_ID, req], sort_keys=True).encode()).hexdigest()[:16]
    mp3, meta = adir / f"{h}.mp3", adir / f"{h}.json"
    if not (mp3.exists() and meta.exists()):
        key = KEY_FILE.read_text().strip()
        body = {k: v for k, v in req.items() if v is not None}
        r = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps?output_format=mp3_44100_128",
            data=json.dumps(body).encode(), method="POST",
            headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "application/json",
                     "User-Agent": "video-pipeline/1.0"})
        with urllib.request.urlopen(r, timeout=120) as resp:
            out = json.loads(resp.read())
        mp3.write_bytes(base64.b64decode(out["audio_base64"]))
        meta.write_text(json.dumps({"text": text, "alignment": out.get("alignment")}))
        stats["chars"] += len(text)
        print(f"  tts: {len(text)} chars -> {mp3.name}")
    wav = mp3.with_suffix(".wav")
    if not wav.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-ac", "1", "-ar", str(SR), str(wav)], check=True)
    with wave.open(str(wav)) as w:
        dur = w.getnframes() / w.getframerate()
    al = json.loads(meta.read_text())["alignment"]
    return wav, dur, al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]


def speech_end(wav, dur):
    """End of the last spoken sound: the clips carry 0.4-0.9 s of trailing silence."""
    o = subprocess.run(["ffmpeg", "-i", str(wav), "-af", "silencedetect=n=-40dB:d=0.15", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    ss = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", o)]
    se = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", o)]
    if ss and se and len(ss) == len(se) and se[-1] >= dur - 0.05:
        return min(dur, ss[-1] + 0.08)
    return dur


def words(chars, starts, ends):
    """[(word, t0, t1)] from character timestamps."""
    out, cur, t0, t1 = [], "", None, None
    for c, a, b in zip(chars, starts, ends):
        if c.isspace():
            if cur:
                out.append((cur, t0, t1))
            cur, t0 = "", None
            continue
        if t0 is None:
            t0 = a
        cur += c
        t1 = b
    if cur:
        out.append((cur, t0, t1))
    return out


def build(stats=None):
    stats = stats if stats is not None else {"chars": 0}
    res = []
    for k, (lid, sid, text) in enumerate(LINES):
        prev = LINES[k - 1][2] if k else ""
        nxt = LINES[k + 1][2] if k + 1 < len(LINES) else ""
        wav, dur, chars, st, en = tts(text, prev, nxt, stats)
        res.append({"id": lid, "shot": sid, "text": text, "wav": str(wav), "clip": round(dur, 3), "speech": round(speech_end(wav, dur), 3),
                    "words": [[w, round(a, 3), round(b, 3)] for w, a, b in words(chars, st, en)]})
        if lid in CAPTIONS:
            assert " ".join(CAPTIONS[lid]).split() == text.split(), lid
            res[-1]["chunks"] = [len(c.split()) for c in CAPTIONS[lid]]
    return res


if __name__ == "__main__":
    total = sum(len(t) for _, _, t in LINES)
    print(f"{len(LINES)} lines, {total} characters, {sum(len(t.split()) for _, _, t in LINES)} words")
    if "--count" in sys.argv:
        sys.exit()
    stats = {"chars": 0}
    res = build(stats)
    out = WORK / "v2" / "voice" / "lines.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1))
    print(f"wrote {out}; speech {sum(r['clip'] for r in res):.1f}s; ElevenLabs characters this run: {stats['chars']}")
