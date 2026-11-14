"""Voice-over for the v2 demo video: two cloned voices, Rene and Toivo, alternating line by line.

Keys and voice IDs are read in-process from ENV_FILE (shell format) and never printed, logged or written.
Rene's key is used only for text-to-speech of Rene's voice; Toivo's key for Toivo's voice and, if needed,
for forced alignment (word timings) of either clip. Model eleven_v3 for both (Toivo falls back to
eleven_multilingual_v2 only if v3 fails for his voice). Clips are cached in WORK/audio by a hash of
(speaker, voice, model, text, settings); a re-render spends no characters. Each clip is gain-matched to
-16 LUFS. Run directly to (re)generate: python3 scripts/video/v2_voice.py -> WORK/v2/voice/lines.json
"""
import base64, hashlib, json, os, pathlib, re, subprocess, sys, urllib.error, urllib.request, uuid, wave

WORK = pathlib.Path(os.environ.get("VIDEO_WORK", "/data/work/video"))
ENV_FILE = pathlib.Path(os.environ.get("ELEVENLABS_ENV_FILE", "/data/attachments/s_G5o6eFRtoL/secrets/elevenlabs.env"))
API = "https://api.elevenlabs.io/v1"
SETTINGS = {"stability": 1.0, "similarity_boost": 0.9}  # v3 "Robust": keeps cloned voices consistent line to line
SR = 44100
TARGET_LUFS = -16.0

# (line id, shot id, speaker, text). Every number is from scripts/sync_numbers.py or the page on screen.
# Rene sets up and measures; Toivo, the named owner in the story, speaks where the owner acts.
LINES = [
    ("b01", "s01", "rene", "An AI agent wrote this fix. It builds, all 175 tests pass, and an AI reviewer says every requirement is met."),
    ("b02", "s01", "toivo", "But it fixes the wrong bug."),
    ("b03", "s02", "rene", "Countersign reviews agent-written code under a signed mandate, which decides what AI may clear alone."),
    ("b04", "s02", "toivo", "Facts come first: the build, the tests, and whether each new test fails without the fix."),
    ("b05", "s03", "rene", "Then three AI reviewers from three vendors. Every citation is re-checked, and what can't be proven is refused."),
    ("b06", "s04", "toivo", "Back to our fix. The line behind the reported bug is one the fix never touches."),
    ("b07", "s05", "rene", "Undo the fix, and 4 of its 8 new tests still pass. They prove nothing."),
    ("b08", "s06", "toivo", "A reviewer found a crash the fix leaves in, and the pipeline reproduced it."),
    ("b09", "s07", "rene", "So the AI won't clear it. It asks the named owner, Toivo."),
    ("b10", "s08", "toivo", "That's me. On GitHub, I signed a request for changes. The required check fails, and the merge is blocked."),
    ("b11", "s09", "rene", "A low-risk docs fix is different: the AI cleared it alone, and it merged in 40 seconds."),
    ("b12", "s10", "toivo", "Every sign-off goes into a signed, hash-chained ledger. Edit one line, and the check fails."),
    ("b13", "s11", "rene", "Measured: 11 of 11 later-reverted real pull requests were sent to a human. Tests and checks caught 14 of 18 planted bugs. And 35 attacks on our own pipeline: all 35 stopped."),
    ("b14", "s12", "toivo", "Countersign. AI clears what it can prove, refuses what it can't, and a named human countersigns the rest."),
]

# Eleven v3 audio tags for Toivo's lines (Toivo, board 17:28Z: persuasive and confident). Sent to TTS only;
# captions and word timings use the untagged text.
TAGS = {
    "b02": "[leaning in] {}",
    "b04": "[confident] {}",
    "b06": "[confident] {}",
    "b08": "[leaning in] {}",
    "b10": "[chuckles] That's me. [confident] {}",
    "b12": "[confident] {}",
    "b14": "[clears throat] [confident] {}",
}


def tagged(lid, text):
    t = TAGS.get(lid)
    if not t:
        return text
    if stock_mode() and lid in STOCK_TEXT:
        return "[confident] " + text
    if t.startswith("[chuckles] That's me. "):
        assert text.startswith("That's me. "), lid
        return t.format(text[len("That's me. "):])
    return t.format(text)


def drop_tags(ws):
    """Remove [audio tag] tokens (possibly multi-word) from [(word, t0, t1)]."""
    out, inside = [], False
    for w, a, b in ws:
        if w.startswith("["):
            inside = True
        if not inside:
            out.append((w, a, b))
        if inside and w.endswith("]"):
            inside = False
    return out


# Caption chunks where the compositor's automatic split reads oddly (must join back to the line's text).
CAPTIONS = {
    "b07": ["Undo the fix,", "and 4 of its 8 new tests", "still pass.", "They prove nothing."],
    "b10": ["That's me.", "On GitHub, I signed", "a request for changes.", "The required check fails,", "and the merge is blocked."],
    "b12": ["Every sign-off goes into", "a signed, hash-chained ledger.", "Edit one line,", "and the check fails."],
    "b13": ["Measured: 11 of 11", "later-reverted real pull requests", "were sent to a human.", "Tests and checks caught",
            "14 of 18 planted bugs.", "And 35 attacks on our own pipeline:", "all 35 stopped."],
}


def _env():
    out = {}
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.replace("export", "").strip()
        out[k] = v.strip().strip('"').strip("'")
    return out


# Fallback narration with stock ElevenLabs voices (V2_VOICES=stock), all on Toivo's key (board rule: anything that
# isn't Rene's own voice goes on Toivo's key). Toivo's lines -> Eric, Rene's lines -> Sarah.
STOCK = {"toivo": "cjVigY5qzO86Huf0OWal", "rene": "EXAVITQu4vr4xnSDxMaL"}
STOCK_TEXT = {"b10": "Toivo signed a request for changes on GitHub. The required check fails, and the merge is blocked."}


def stock_mode():
    return os.environ.get("V2_VOICES") == "stock"


def _speaker(name):
    e = _env()
    if stock_mode():
        return {"key": e["TOIVO_ELEVENLABS_KEY"], "voice": STOCK[name], "models": ["eleven_v3"]}
    if name == "rene":
        return {"key": e["RENE_ELEVENLABS_KEY"], "voice": e["RENE_VOICE_ID"], "models": [e.get("RENE_MODEL_ID") or "eleven_v3"]}
    return {"key": e["TOIVO_ELEVENLABS_KEY"], "voice": e["TOIVO_VOICE_ID"], "models": ["eleven_v3", "eleven_multilingual_v2"]}


def _post(url, key, body=None, data=None, ctype="application/json", accept="application/json"):
    r = urllib.request.Request(url, data=data if data is not None else json.dumps(body).encode(), method="POST",
                               headers={"xi-api-key": key, "Content-Type": ctype, "Accept": accept,
                                        "User-Agent": "video-pipeline/1.0"})
    with urllib.request.urlopen(r, timeout=180) as resp:
        return resp.read()


def _err(e):
    """HTTP error summary without any request data (no key, no voice ID)."""
    try:
        body = e.read().decode(errors="replace")[:300]
    except Exception:
        body = ""
    return f"HTTP {getattr(e, 'code', '?')}: {body}"


def _align(mp3, text):
    """Forced alignment (Toivo's key): word timings for a clip -> (chars, starts, ends) per character."""
    key = _speaker("toivo")["key"]
    b = uuid.uuid4().hex
    parts = [f"--{b}\r\nContent-Disposition: form-data; name=\"text\"\r\n\r\n{text}\r\n".encode(),
             f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"clip.mp3\"\r\nContent-Type: audio/mpeg\r\n\r\n".encode(),
             mp3.read_bytes(), f"\r\n--{b}--\r\n".encode()]
    out = json.loads(_post(f"{API}/forced-alignment", key, data=b"".join(parts), ctype=f"multipart/form-data; boundary={b}"))
    chars = out["characters"]
    return {"characters": [c["text"] for c in chars], "character_start_times_seconds": [c["start"] for c in chars],
            "character_end_times_seconds": [c["end"] for c in chars], "source": "forced-alignment"}


def from_file(lid, text):
    """Toivo's own takes from the ElevenLabs website (V2_VOICE_DIR=<dir with b01.mp3 ... b14.mp3>): word timings by
    forced alignment on Toivo's key, cached next to the clip; loudness matched like generated clips."""
    src = pathlib.Path(os.environ["V2_VOICE_DIR"]) / f"{lid}.mp3"
    adir = WORK / "audio" / "takes"
    adir.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(src.read_bytes() + text.encode()).hexdigest()[:16]
    mp3, meta = adir / f"{lid}-{h}.mp3", adir / f"{lid}-{h}.json"
    if not meta.exists():
        mp3.write_bytes(src.read_bytes())
        meta.write_text(json.dumps({"speaker": "take", "model": "website", "text": text, "alignment": _align(mp3, text)}))
        print(f"  aligned {src.name}")
    wav = mp3.with_suffix(".wav")
    if not wav.exists():
        gain = TARGET_LUFS - lufs(mp3)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-af", f"volume={gain:.2f}dB,alimiter=limit=0.95",
                        "-ac", "1", "-ar", str(SR), str(wav)], check=True)
    with wave.open(str(wav)) as w:
        dur = w.getnframes() / w.getframerate()
    al = json.loads(meta.read_text())["alignment"]
    return wav, dur, al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"], "website"


def tts(speaker, text, stats):
    adir = WORK / "audio"
    adir.mkdir(parents=True, exist_ok=True)
    sp = _speaker(speaker)
    for model in sp["models"]:
        req = {"text": text, "model_id": model, "voice_settings": {"stability": 0.5, "similarity_boost": 0.75} if stock_mode() else SETTINGS}
        h = hashlib.sha256(json.dumps([speaker, sp["voice"], req], sort_keys=True).encode()).hexdigest()[:16]
        mp3, meta = adir / f"{speaker}-{h}.mp3", adir / f"{speaker}-{h}.json"
        if mp3.exists() and meta.exists():
            break
        try:
            out = json.loads(_post(f"{API}/text-to-speech/{sp['voice']}/with-timestamps?output_format=mp3_44100_128", sp["key"], req))
            mp3.write_bytes(base64.b64decode(out["audio_base64"]))
            al = out.get("alignment")
        except urllib.error.HTTPError as e:
            print(f"  tts {speaker} {model} with-timestamps: {_err(e)}")
            try:
                mp3.write_bytes(_post(f"{API}/text-to-speech/{sp['voice']}?output_format=mp3_44100_128", sp["key"], req,
                                      accept="audio/mpeg"))
                al = None
            except urllib.error.HTTPError as e2:
                print(f"  tts {speaker} {model}: {_err(e2)}")
                continue
        stats[speaker] = stats.get(speaker, 0) + len(text)
        if not al:
            al = _align(mp3, text)
        meta.write_text(json.dumps({"speaker": speaker, "model": model, "text": text, "alignment": al}))
        print(f"  tts {speaker} {model}: {len(text)} chars -> {mp3.name}")
        break
    else:
        raise SystemExit(f"no model worked for {speaker}")
    wav = mp3.with_suffix(".wav")
    if not wav.exists():
        gain = TARGET_LUFS - lufs(mp3)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-af", f"volume={gain:.2f}dB,alimiter=limit=0.95",
                        "-ac", "1", "-ar", str(SR), str(wav)], check=True)
    with wave.open(str(wav)) as w:
        dur = w.getnframes() / w.getframerate()
    m = json.loads(meta.read_text())
    al = m["alignment"]
    return wav, dur, al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"], m["model"]


def lufs(path):
    o = subprocess.run(["ffmpeg", "-i", str(path), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    vals = re.findall(r"I:\s+(-?[\d.]+) LUFS", o)
    return float(vals[-1]) if vals else TARGET_LUFS


def speech_end(wav, dur):
    """End of the last spoken sound: clips carry trailing silence."""
    o = subprocess.run(["ffmpeg", "-i", str(wav), "-af", "silencedetect=n=-40dB:d=0.15", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    ss = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", o)]
    se = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", o)]
    if ss and (len(ss) > len(se) or se[-1] >= dur - 0.05):
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
    stats = stats if stats is not None else {}
    res = []
    for lid, sid, speaker, text in LINES:
        if stock_mode():
            text = STOCK_TEXT.get(lid, text)
        if os.environ.get("V2_VOICE_DIR"):
            wav, dur, chars, st, en, model = from_file(lid, text)
        else:
            wav, dur, chars, st, en, model = tts(speaker, tagged(lid, text) if speaker == "toivo" else text, stats)
        ws = drop_tags(words(chars, st, en))
        assert [w for w, _, _ in ws] == text.split(), (lid, [w for w, _, _ in ws][:5])
        res.append({"id": lid, "shot": sid, "speaker": speaker, "model": model, "text": text, "wav": str(wav),
                    "clip": round(dur, 3), "speech": round(min(speech_end(wav, dur), ws[-1][2] + 0.1), 3),
                    "words": [[w, round(a, 3), round(b, 3)] for w, a, b in ws]})
        if lid in CAPTIONS and not (stock_mode() and lid in STOCK_TEXT):
            assert " ".join(CAPTIONS[lid]).split() == text.split(), lid
            res[-1]["chunks"] = [len(c.split()) for c in CAPTIONS[lid]]
    return res


if __name__ == "__main__":
    for s in ("rene", "toivo"):
        print(f"{s}: {sum(len(t) for _, _, p, t in LINES if p == s)} characters")
    if "--count" in sys.argv:
        sys.exit()
    stats = {}
    res = build(stats)
    out = WORK / "v2" / "voice" / "lines.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1))
    print(f"wrote {out}; speech {sum(r['speech'] for r in res):.1f}s; ElevenLabs characters this run: {stats}")
