#!/usr/bin/env python3
"""Render the Junction demo video: a scripted screen recording of the real site plus a voice-over.

    python3 site/build.py
    uv run --with playwright python scripts/video/make_video.py            # ElevenLabs voice if the key exists
    uv run --with playwright python scripts/video/make_video.py --silent   # silent placeholder voice, same timing

Nothing is generated except the voice: every frame is site/ in headless Chromium (1280x720 CSS at device
scale 1.5, so 1920x1080 pixels), captured with the DevTools screencast while this script moves a visible
cursor and clicks. The voice-over and captions are read from docs/pitch/video-script.md (numbers markers
stripped); SHOT_OVERRIDES below lists the shots that differ from that table because the site changed.

Voice: ElevenLabs text-to-speech with timestamps, one clip per shot, cached under WORK/audio keyed by a
hash of (text, voice, model, settings), so a re-render spends no characters. The key is read from
KEY_FILE inside this process and never printed. Each shot lasts lead + clip + tail; clicks are timed to
the word they illustrate using the character timestamps.

Output: WORK/countersign-demo.mp4 (H.264 + AAC, yuv420p, faststart) and WORK/contact-sheet.png.
"""
import argparse
import asyncio
import base64
import bisect
import functools
import hashlib
import http.server
import json
import os
import pathlib
import re
import shutil
import subprocess
import threading
import time
import urllib.request
import wave

from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "pitch" / "video-script.md"
WORK = pathlib.Path(os.environ.get("VIDEO_WORK", "/data/work/video"))
KEY_FILE = pathlib.Path(os.environ.get("ELEVENLABS_KEY_FILE", "/data/work/secrets/elevenlabs.key"))
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # "George", premade, calm British male narrator
MODEL = "eleven_multilingual_v2"
VOICE_SETTINGS = {"stability": 0.55, "similarity_boost": 0.75, "style": 0.0, "use_speaker_boost": True, "speed": 0.95}
FPS = 30
W, H = 1280, 720          # CSS viewport
SCALE = 1.5               # -> 1920x1080 frames
SR = 44100
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# The site moved on after the shot list was written (Demo v3): index.html no longer has pins or a bottom
# bar. Shots map to the same facts on the current pages; only shot 2's words and caption change.
SHOT_OVERRIDES = {
    1: {"vo": "Countersign checks the evidence itself, and says no: it fixes the wrong bug.",
        "caption": "Countersign checks the evidence"},
}


# ---------------------------------------------------------------- script

def strip_markers(s):
    return re.sub(r"<!--n:[^>]*-->(.*?)<!--/n-->", r"\1", s)


def read_script():
    text = strip_markers(DOC.read_text(encoding="utf-8"))
    table = text.split("## Shot list", 1)[1].split("## Voice-over", 1)[0]
    rows = [r for r in table.splitlines() if re.match(r"\|\s*\d:\d\d", r)]
    caps = []
    for r in rows:
        cell = [c.strip() for c in r.strip().strip("|").split("|")][2]
        caps.append([] if cell.startswith("(none") else [c.strip() for c in cell.split("· then:")])
    vo_block = text.split("## Voice-over", 1)[1].split("\n## ", 1)[0]
    paras, cur = [], []
    for line in vo_block.splitlines():
        if line.startswith(">"):
            body = line[1:].strip()
            if body:
                cur.append(body)
            elif cur:
                paras.append(" ".join(cur)); cur = []
    if cur:
        paras.append(" ".join(cur))
    assert len(paras) == len(caps) == 10, (len(paras), len(caps))
    shots = [{"vo": v, "captions": c} for v, c in zip(paras, caps)]
    for i, o in SHOT_OVERRIDES.items():
        shots[i]["vo"] = o["vo"]
        shots[i]["captions"] = [o["caption"]]
    for s in shots:
        for c in s["captions"]:
            assert len(c.split()) <= 6, c
    return shots


# ---------------------------------------------------------------- voice

def tts(text, prev_text, next_text, silent, stats):
    """Return (wav_path, duration, chars, char_start_times). Cached by content hash."""
    adir = WORK / "audio"
    adir.mkdir(parents=True, exist_ok=True)
    if silent or not KEY_FILE.exists():
        dur = max(1.0, len(text.split()) / 2.5)
        wav = adir / f"silent-{hashlib.sha1(text.encode()).hexdigest()[:12]}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono",
                        "-t", f"{dur:.3f}", str(wav)], check=True)
        return wav, dur, list(text), [dur * i / len(text) for i in range(len(text))]
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
    else:
        print(f"  tts: cached {mp3.name}")
    wav = mp3.with_suffix(".wav")
    if not wav.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-ac", "1", "-ar", str(SR), str(wav)], check=True)
    with wave.open(str(wav)) as w:
        dur = w.getnframes() / w.getframerate()
    al = json.loads(meta.read_text())["alignment"]
    return wav, dur, al["characters"], al["character_start_times_seconds"]


# ---------------------------------------------------------------- browser helpers

CURSOR_JS = r"""
(() => {
  const mk = () => {
    if (document.getElementById('__cur') || !document.body) return;
    const d = document.createElement('div'); d.id = '__cur';
    d.style.cssText = 'position:fixed;width:26px;height:26px;margin:-13px 0 0 -13px;border-radius:50%;' +
      'background:rgba(9,105,218,.28);border:2.5px solid rgba(9,105,218,.95);box-shadow:0 0 0 2px rgba(255,255,255,.9),0 2px 6px rgba(0,0,0,.25);' +
      'pointer-events:none;z-index:2147483647;transition:transform .12s ease-out;left:-100px;top:-100px';
    try { const p = JSON.parse(sessionStorage.getItem('__cur') || 'null'); if (p) { d.style.left = p[0] + 'px'; d.style.top = p[1] + 'px'; } } catch (_) {}
    document.body.appendChild(d);
  };
  addEventListener('mousemove', e => { const d = document.getElementById('__cur'); if (!d) { mk(); }
    const c = document.getElementById('__cur'); if (!c) return;
    c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px';
    try { sessionStorage.setItem('__cur', JSON.stringify([e.clientX, e.clientY])); } catch (_) {} }, true);
  addEventListener('mousedown', () => { const c = document.getElementById('__cur'); if (c) c.style.transform = 'scale(.6)'; }, true);
  addEventListener('mouseup', () => { const c = document.getElementById('__cur'); if (c) c.style.transform = 'scale(1)'; }, true);
  if (document.readyState === 'loading') addEventListener('DOMContentLoaded', mk); else mk();
  try { localStorage.setItem('cs-theme', 'light'); } catch (_) {}
})();
"""


class Recorder:
    def __init__(self, page, cdp, fdir):
        self.page, self.cdp, self.fdir = page, cdp, fdir
        self.frames = []  # (timestamp, path)
        self.n = 0
        self.mouse = (W / 2, H / 2)
        cdp.on("Page.screencastFrame", self._frame)

    def _frame(self, p):
        self.n += 1
        path = self.fdir / f"{self.n:06d}.jpg"
        path.write_bytes(base64.b64decode(p["data"]))
        ts = p["metadata"].get("timestamp") or time.time()
        self.frames.append((ts, path))
        asyncio.ensure_future(self.cdp.send("Page.screencastFrameAck", {"sessionId": p["sessionId"]}))

    async def start(self):
        await self.cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 92, "maxWidth": int(W * SCALE),
                                                      "maxHeight": int(H * SCALE), "everyNthFrame": 1})

    async def goto(self, url, settle=700):
        await self.page.goto(url)
        await self.page.wait_for_load_state("networkidle")
        await self.page.evaluate("document.fonts.ready")
        await self.page.mouse.move(*self.mouse)
        await self.page.wait_for_timeout(settle)

    async def move(self, x, y, dur=0.7):
        x0, y0 = self.mouse
        steps = max(2, int(dur * 60))
        t0 = time.time()
        for i in range(1, steps + 1):
            u = i / steps
            e = u * u * (3 - 2 * u)  # smoothstep
            await self.page.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e)
            await asyncio.sleep(max(0, t0 + dur * i / steps - time.time()))
        self.mouse = (x, y)

    async def box(self, sel, nth=0, fx=0.5, fy=0.5):
        b = await self.page.locator(sel).nth(nth).bounding_box()
        assert b, f"no box for {sel}"
        return b["x"] + b["width"] * fx, b["y"] + b["height"] * fy

    async def move_to(self, sel, nth=0, dur=0.7, fx=0.5, fy=0.5):
        await self.move(*(await self.box(sel, nth, fx, fy)), dur=dur)

    async def click(self):
        await self.page.mouse.down()
        await asyncio.sleep(0.12)
        await self.page.mouse.up()


class Shot:
    def __init__(self, rec, t0, lead, text, chars, starts):
        self.rec, self.t0, self.lead = rec, t0, lead
        self.text, self.chars, self.starts = text, chars, starts
        self.joined = "".join(chars)

    def cue(self, phrase):
        i = self.joined.find(phrase)
        assert i >= 0, f"cue {phrase!r} not in {self.joined!r}"
        return self.lead + self.starts[i]

    async def at(self, t):
        await asyncio.sleep(max(0, self.t0 + t - time.time()))


# ---------------------------------------------------------------- the ten shots
# prep(rec, base): get the page ready before the shot's clock starts (not recorded).
# act(rec, s): runs on the shot's clock; s.cue("words") is when the voice says them.

async def p1(r, base):
    await r.goto(f"{base}/pitch.html#4")
    await r.move(640, 590, 0.05)

async def a1(r, s):
    await s.at(s.cue("The build passes") - 0.6); await r.move_to('.slide[data-i="3"] .tile', 0, 0.9)
    await s.at(s.cue("an AI reviewer") - 0.5); await r.move_to('.slide[data-i="3"] .tile', 1, 0.8)

async def p2(r, base):
    await r.goto(f"{base}/index.html", settle=100)
    # rewind the reveal (ticks, then "It fixes the wrong bug.") so it plays on the shot's clock
    await r.page.evaluate("document.getAnimations().forEach(a => { a.pause(); a.currentTime = 0; })")
    await r.move(640, 600, 0.05)
    await r.page.wait_for_timeout(400)

async def a2(r, s):
    await r.page.evaluate("document.getAnimations().forEach(a => a.play())")
    await s.at(0.6); await r.move_to(".ticks li", 1, 1.0, fy=1.45)  # just under "175/175 tests pass"
    await s.at(max(4.0, s.dur - 1.5)); await r.move_to('.home a[href="#where"]', 0, 0.8)
    await s.at(s.dur - 0.35); await r.click()

async def a3(r, s):
    await s.at(s.cue("This one") - 0.3); await r.move_to("#where .pin", 0, 0.8, fx=0.3)
    await s.at(s.cue("The agent fixed") - 0.3); await r.move_to("#where .r.ctx", 6, 1.0, fx=0.25)

async def p4(r, base):
    await r.goto(f"{base}/packs/2234/pack.html")
    await r.page.evaluate("""() => { document.getElementById('evidence').open = true;
        const a = document.getElementById('f-claude-C2'); scrollTo(0, a.getBoundingClientRect().top + scrollY - 110); }""")
    await r.move(1150, 200, 0.05)
    await r.page.wait_for_timeout(500)

async def a4(r, s):
    await s.at(s.cue("still crashes") - 0.5); await r.move_to("#f-claude-C2 h4", 0, 0.8, fx=0.75)
    await s.at(s.cue("A reviewer claimed") - 0.4); await r.move_to("#f-claude-C2 p.sm.mut", 0, 0.7, fx=0.5)
    await s.at(s.cue("the pipeline reproduced") - 0.5); await r.move_to("#f-claude-C2 p.sm", 2, 0.8, fx=0.55)

async def p5(r, base):
    await r.goto(f"{base}/tour.html#2")
    await r.move(700, 250, 0.05)

async def a5(r, s):
    await s.at(s.cue("four of the eight") - 0.4)
    for i in range(4):
        await r.move_to("#s2 li.weak", i, 0.45, fx=0.5, fy=0.7)
        await asyncio.sleep(0.15)
    await s.at(s.cue("They prove nothing") - 0.2); await r.move_to("#s2 li.ok", 0, 0.7, fx=0.5, fy=0.7)

async def p6(r, base):
    await r.goto(f"{base}/tour.html#5")
    await r.move(800, 230, 0.05)

async def a6(r, s):
    await s.at(s.cue("It asks") - 0.6); await r.move_to("#s5 .pill.ask", 0, 0.8)

async def p7(r, base):
    await r.goto(f"{base}/tour.html#6", settle=1500)  # signatures verify asynchronously
    await r.page.evaluate("scrollTo(0, 150)")
    await r.move(760, 120, 0.05)
    await r.page.wait_for_timeout(400)

async def a7(r, s):
    await s.at(s.cue("signs into") - 0.4); await r.move_to(".lres", 6, 0.9, fx=0.25)
    await s.at(s.cue("Edit one line") - 0.7); await r.move_to("#tamper", 0, 0.7)
    await s.at(s.cue("Edit one line") + 0.25); await r.click()
    await s.at(s.cue("Recompute") - 0.6); await r.move_to("#rehash", 0, 0.6)
    await s.at(s.cue("Recompute") + 0.4); await r.click()
    await s.at(s.cue("Only his key") - 0.3); await r.move_to("#lstatus", 0, 0.8, fx=0.6)

async def p8(r, base):
    await r.goto(f"{base}/index.html", settle=4500)  # let the reveal finish before the shot
    await r.move(640, 470, 0.05)

async def a8(r, s):
    await s.at(s.cue("Now sneak") - 0.2); await r.move_to('.home a[href="#sneak"]', 0, 0.7)
    await s.at(s.cue("sneak a bug in") + 0.3); await r.click()
    await s.at(s.cue("delete one line") - 0.6); await r.move_to('a[href="#bug-guard"]', 0, 0.6)
    await s.at(s.cue("delete one line") + 0.2); await r.click()
    await s.at(s.cue("Every test passes") - 0.1); await r.move_to("#h-bug-guard", 0, 0.7, fx=1.06)
    await s.at(s.cue("A reviewer still") - 0.2); await r.move_to("#bug-guard .code .r", 0, 0.7, fx=0.25)

async def p9(r, base):
    await r.goto(f"{base}/overview.html")
    await r.move(640, 520, 0.05)

async def a9(r, s):
    await s.at(0.4); await r.move(270 + 20, 300, 0.9)
    await s.at(s.cue("We attacked") - 0.3); await r.move(1010 + 20, 300, 1.0)

async def p10(r, base):
    await r.goto(f"{base}/pitch.html#1")
    await r.move(1150, 560, 0.05)

async def a10(r, s):
    pass

PLAN = [(p1, a1), (p2, a2), (None, a3), (p4, a4), (p5, a5), (p6, a6), (p7, a7), (p8, a8), (p9, a9), (p10, a10)]
LEAD = [0.9, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6]
TAIL = [1.0, 0.6, 1.0, 1.0, 1.0, 1.0, 1.4, 1.0, 1.0, 2.5]
MIN_DUR = [0, 5.0, 0, 0, 0, 0, 0, 0, 0, 0]


# ---------------------------------------------------------------- main

def serve_site():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=str(ROOT / "site"))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


async def record(shots, base, fdir):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=SCALE,
                                        color_scheme="light", reduced_motion="no-preference")
        await ctx.add_init_script(CURSOR_JS)
        page = await ctx.new_page()
        cdp = await ctx.new_cdp_session(page)
        rec = Recorder(page, cdp, fdir)
        await rec.start()
        for k, ((prep, act), sh) in enumerate(zip(PLAN, shots)):
            if prep:
                await prep(rec, base)
            await asyncio.sleep(0.3)
            s = Shot(rec, time.time(), sh["lead"], sh["vo"], sh["chars"], sh["starts"])
            s.base, s.dur = base, sh["dur"]
            await act(rec, s)
            await s.at(s.dur)
            sh["t0"] = s.t0
            print(f"  shot {k + 1}: {s.dur:.2f}s, {len(rec.frames)} frames so far")
        await cdp.send("Page.stopScreencast")
        await asyncio.sleep(0.3)
        await browser.close()
    return rec.frames


def compose_video_frames(frames, shots, seqdir):
    frames.sort()
    ts = [f[0] for f in frames]
    if seqdir.exists():
        shutil.rmtree(seqdir)
    seqdir.mkdir(parents=True)
    n = 0
    for sh in shots:
        for i in range(round(sh["dur"] * FPS)):
            t = sh["t0"] + i / FPS
            j = max(0, bisect.bisect_right(ts, t) - 1)
            n += 1
            os.symlink(frames[j][1], seqdir / f"{n:06d}.jpg")
    return n


def build_audio(shots, total, path):
    buf = bytearray(int(total * SR) * 2)
    t = 0.0
    for sh in shots:
        with wave.open(str(sh["wav"])) as w:
            data = w.readframes(w.getnframes())
        off = int((t + sh["lead"]) * SR) * 2
        data = data[: max(0, len(buf) - off)]
        buf[off:off + len(data)] = data
        t += sh["dur"]
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(bytes(buf))


def esc(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")


def caption_filters(shots, capdir):
    capdir.mkdir(parents=True, exist_ok=True)
    out, t = [], 0.0
    for k, sh in enumerate(shots):
        caps = sh["captions"]
        spans = []
        if len(caps) == 1:
            spans = [(t, t + sh["dur"], caps[0])]
        elif len(caps) == 2:
            mid = t + sh["split"]
            spans = [(t, mid, caps[0]), (mid, t + sh["dur"], caps[1])]
        for j, (a, b, c) in enumerate(spans):
            f = capdir / f"cap{k}_{j}.txt"
            f.write_text(c, encoding="utf-8")
            alpha = f"max(0,min(1,min((t-{a:.3f})/0.2,({b:.3f}-t)/0.2)))"
            out.append(f"drawtext=fontfile={FONT}:textfile={f}:fontsize=46:fontcolor=white:"
                       f"box=1:boxcolor=0x111418@0.8:boxborderw=22:x=72:y=h-th-84:"
                       f"alpha='{alpha}':enable='between(t,{a:.3f},{b - 0.001:.3f})'")
        t += sh["dur"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--silent", action="store_true", help="silent placeholder voice (no ElevenLabs call)")
    ap.add_argument("--url", help="base URL of a running site server (default: serve site/ here)")
    ap.add_argument("--out", default=str(WORK / "countersign-demo.mp4"))
    args = ap.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    shots = read_script()
    stats = {"chars": 0}
    print("voice:")
    for k, sh in enumerate(shots):
        prev = shots[k - 1]["vo"] if k else ""
        nxt = shots[k + 1]["vo"] if k + 1 < len(shots) else ""
        sh["wav"], sh["clip"], sh["chars"], sh["starts"] = tts(sh["vo"], prev, nxt, args.silent, stats)
        sh["lead"] = LEAD[k]
        sh["dur"] = max(MIN_DUR[k], LEAD[k] + sh["clip"] + TAIL[k])
        if len(sh["captions"]) == 2:
            i = "".join(sh["chars"]).find("We attacked")
            sh["split"] = sh["lead"] + sh["starts"][i] - 0.2
    total = sum(sh["dur"] for sh in shots)
    print(f"total {total:.2f}s; shots " + " ".join(f"{sh['dur']:.1f}" for sh in shots))
    assert total <= 120, "over two minutes"

    httpd, base = (None, args.url) if args.url else serve_site()
    fdir = WORK / "build" / "frames"
    if fdir.exists():
        shutil.rmtree(fdir)
    fdir.mkdir(parents=True)
    print("recording:")
    frames = asyncio.run(record(shots, base, fdir))
    if httpd:
        httpd.shutdown()
    seq = WORK / "build" / "seq"
    n = compose_video_frames(frames, shots, seq)
    wav = WORK / "build" / "voice.wav"
    build_audio(shots, n / FPS, wav)
    total = n / FPS
    vf = ",".join(["scale=1920:1080:flags=lanczos", "format=yuv420p"] + caption_filters(shots, WORK / "build" / "captions")
                  + [f"fade=t=in:st=0:d=0.4", f"fade=t=out:st={total - 0.7:.3f}:d=0.7"])
    af = f"loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=out:st={total - 0.7:.3f}:d=0.7,aresample=48000"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(seq / "%06d.jpg"),
                    "-i", str(wav), "-vf", vf, "-af", af, "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ac", "2", "-shortest",
                    "-movflags", "+faststart", args.out], check=True)
    # contact sheet: the middle of shots 1, 7 and 10
    mids, t = [], 0.0
    for sh in shots:
        mids.append(t + sh["dur"] / 2); t += sh["dur"]
    sheet = WORK / "contact-sheet.png"
    picks = [mids[0], mids[6], mids[9]]
    inputs = []
    for m in picks:
        inputs += ["-ss", f"{m:.2f}", "-i", args.out]
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex",
                    "[0:v]scale=640:-1[a];[1:v]scale=640:-1[b];[2:v]scale=640:-1[c];[a][b][c]hstack=3",
                    "-frames:v", "1", str(sheet)], check=True)
    (WORK / "build" / "timeline.json").write_text(json.dumps(
        [{"vo": sh["vo"], "captions": sh["captions"], "dur": sh["dur"], "mid": m} for sh, m in zip(shots, mids)], indent=1))
    size = pathlib.Path(args.out).stat().st_size
    print(f"wrote {args.out}: {total:.2f}s, {size / 1e6:.1f} MB; contact sheet {sheet}")
    print(f"ElevenLabs characters this run: {stats['chars']}")


if __name__ == "__main__":
    main()
