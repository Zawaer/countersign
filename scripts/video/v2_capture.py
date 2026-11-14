"""Capture the real site for the v2 video: one screencast per shot, plus a cursor/click/camera track.

    FONTCONFIG_FILE=/data/work/video/v2/fonts/fonts.conf \
    uv run --with playwright --with pillow --with numpy python scripts/video/v2_capture.py s01 s04 ...

Each shot is driven on its own clock (t=0..dur from timeline.json) by a scene function in
v2_scenes_*.py: `async def sNN(r, s)` gets a Rec `r` and the shot dict `s`. Output per shot:
WORK/v2/capture/<shot>/frames/*.jpg (2560x1440) and track.json (see WORK/v2/SPEC.md). The cursor is not
drawn in the page: Playwright moves the real mouse (so hover states are real) and the track logs where it
is; the compositor draws a macOS arrow there.
"""
import asyncio
import base64
import functools
import http.server
import importlib
import json
import math
import os
import pathlib
import random
import shutil
import sys
import threading
import time

from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORK = pathlib.Path(os.environ.get("VIDEO_WORK", "/data/work/video")) / "v2"
W, H, DPR = 1280, 720, 2
URLBAR = (420, -40)

INIT_JS = "try { localStorage.setItem('cs-theme', 'light'); } catch (_) {}"


def scene_modules():
    mods = []
    for p in sorted(pathlib.Path(__file__).parent.glob("v2_scenes_*.py")):
        mods.append(importlib.import_module(p.stem))
    return mods


def find_scene(sid):
    for m in scene_modules():
        if hasattr(m, sid):
            return getattr(m, sid)
    raise SystemExit(f"no scene function {sid} in v2_scenes_*.py")


def min_jerk(u):
    return u * u * u * (10 - 15 * u + 6 * u * u)


class Rec:
    def __init__(self, page, cdp, shot, out, base, base_root):
        self.page, self.cdp, self.shot, self.out = page, cdp, shot, out
        self.base, self.base_root = base, base_root
        self.frames, self.cursor, self.clicks, self.scroll, self.camera = [], [], [], [], []
        self.highlights, self.notes = [], []
        self.n = 0
        self.t0 = None
        self.pos = (W / 2, H / 2)
        self.rng = random.Random(shot["id"])
        (out / "frames").mkdir(parents=True, exist_ok=True)
        cdp.on("Page.screencastFrame", self._frame)

    # ---- clock
    def now(self):
        return time.time() - self.t0 if self.t0 is not None else -1.0

    async def at(self, t):
        """Wait until shot time t."""
        await asyncio.sleep(max(0.0, self.t0 + t - time.time()))

    def cue(self, word, line=0, end=False, nth=0):
        """Shot time when the voice says `word` (prefix match, case-insensitive, punctuation ignored)."""
        want = word.lower().strip(".,:;!?")
        hits = [w for w in self.shot["lines"][line]["words"] if w[0].lower().strip(".,:;!?").startswith(want)]
        assert len(hits) > nth, f"cue {word!r} not in line {line} of {self.shot['id']}"
        return hits[nth][2 if end else 1]

    # ---- frames
    def _frame(self, p):
        self.n += 1
        name = f"frames/{self.n:06d}.jpg"
        (self.out / name).write_bytes(base64.b64decode(p["data"]))
        ts = p["metadata"].get("timestamp") or time.time()
        self.frames.append([round(ts - self.t0, 4) if self.t0 else ts, name, ts])
        asyncio.ensure_future(self.cdp.send("Page.screencastFrameAck", {"sessionId": p["sessionId"]}))

    async def start_screencast(self):
        await self.cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 92, "maxWidth": W * DPR,
                                                      "maxHeight": H * DPR, "everyNthFrame": 1})

    # ---- page
    def url(self, rel):
        return (self.base_root + rel) if rel.startswith("/") else f"{self.base}/{rel}"

    async def goto(self, rel, settle=600):
        await self.page.goto(self.url(rel))
        await self.page.wait_for_load_state("networkidle")
        await self.page.evaluate("document.fonts.ready")
        await self.page.wait_for_timeout(settle)

    async def box(self, sel, nth=0):
        b = await self.page.locator(sel).nth(nth).bounding_box()
        assert b, f"no box for {sel}"
        return [b["x"], b["y"], b["width"], b["height"]]

    async def point(self, sel, nth=0, fx=0.5, fy=0.5):
        x, y, w, h = await self.box(sel, nth)
        return x + w * fx, y + h * fy

    # ---- cursor
    def _log(self, x, y):
        self.cursor.append([round(self.now(), 4), round(x, 2), round(y, 2)])

    async def _put(self, x, y):
        self.pos = (x, y)
        self._log(x, y)
        if y >= 0:
            await self.page.mouse.move(x, y)

    def place(self, x, y):
        """Set the cursor without moving the mouse (e.g. at the URL bar, y<0, at type_lead)."""
        self.pos = (x, y)
        self._log(x, y)

    async def move(self, x, y, dur=None, overshoot=False):
        """Human-like move: minimum-jerk speed along a slight arc. No overshoot by default (it read as a
        wobble on video); overshoot=True adds a tiny one (<= 4 CSS px) that blends into the landing.

        The real mouse is driven in real time (hovers), but the logged path is the analytic curve sampled
        at 120 Hz on the shot clock, so the compositor's cursor carries no event-loop timing jitter."""
        x0, y0 = self.pos
        dx, dy = x - x0, y - y0
        dist = math.hypot(dx, dy)
        if dist < 1:
            return
        if dur is None:
            dur = 0.32 + 0.22 * math.log2(1 + dist / 80)
        bend = self.rng.choice([-1, 1]) * min(40.0, dist * 0.07)
        nx, ny = (-dy / dist, dx / dist)
        over = min(4.0, dist * 0.015) if overshoot else 0.0

        def path(u):
            e = min_jerk(u)
            # overshoot: a bump of the along-path progress that peaks late and returns smoothly to 0 at u=1
            e += over / dist * (math.sin(math.pi * u) ** 2) * u ** 3 * 4
            arc = math.sin(math.pi * min(1.0, e)) * bend
            return x0 + dx * e + nx * arc, y0 + dy * e + ny * arc

        t_start, start = self.now(), time.time()
        while True:
            u = min(1.0, (time.time() - start) / dur)
            px, py = path(u)
            self.pos = (px, py)
            if py >= 0:
                await self.page.mouse.move(px, py)
            if u >= 1:
                break
            await asyncio.sleep(1 / 90)
        n = max(2, int(math.ceil(dur * 120)))
        for i in range(n + 1):
            px, py = path(i / n)
            self.cursor.append([round(t_start + dur * i / n, 4), round(px, 2), round(py, 2)])
        self.pos = (x, y)

    async def move_to(self, sel, nth=0, fx=0.5, fy=0.5, dur=None):
        await self.move(*(await self.point(sel, nth, fx, fy)), dur=dur)

    async def drift(self, dx, dy, dur=1.2):
        """A slow, small idle drift (a hand resting on the mouse)."""
        await self.move(self.pos[0] + dx, self.pos[1] + dy, dur=dur, overshoot=False)

    async def click(self):
        x, y = self.pos
        self.clicks.append([round(self.now(), 4), round(x, 2), round(y, 2)])
        await self.page.mouse.down()
        await asyncio.sleep(0.09)
        await self.page.mouse.up()

    # ---- scrolling with inertia (wheel deltas following an ease-out)
    async def scroll_by(self, dy, dur=0.9):
        start, done = time.time(), 0.0
        while True:
            u = min(1.0, (time.time() - start) / dur)
            e = 1 - (1 - u) ** 3
            step = dy * e - done
            if abs(step) >= 0.5 or u >= 1:
                await self.page.mouse.wheel(0, step)
                done += step
            sy = await self.page.evaluate("scrollY")
            self.scroll.append([round(self.now(), 4), sy])
            if u >= 1:
                break
            await asyncio.sleep(1 / 60)
        await asyncio.sleep(0.05)

    # ---- editorial track
    def cam(self, t, zoom, cx, cy, ease="io"):
        self.camera.append([round(t, 3), zoom, round(cx, 1), round(cy, 1), ease])

    async def highlight(self, sel_or_box, t=None, until=None, nth=0):
        box = sel_or_box if isinstance(sel_or_box, list) else await self.box(sel_or_box, nth)
        self.highlights.append({"t": round(self.now() if t is None else t, 3), "box": [round(v, 1) for v in box],
                                "until": until if until is not None else self.shot["dur"]})

    def note(self, t, until, text, anchor):
        self.notes.append({"t": t, "until": until, "text": text, "anchor": anchor})

    def save(self):
        self.frames.sort(key=lambda f: f[2])
        track = {"shot": self.shot["id"], "dur": self.shot["dur"],
                 "frames": [[f[0], f[1]] for f in self.frames], "cursor": self.cursor, "clicks": self.clicks,
                 "scroll": self.scroll, "camera": sorted(self.camera), "highlights": self.highlights,
                 "notes": self.notes}
        (self.out / "track.json").write_text(json.dumps(track))


def serve(directory):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(directory)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


async def capture(shot_ids):
    tl = json.loads((WORK / "timeline.json").read_text())
    shots = {s["id"]: s for s in tl["shots"]}
    site, base = serve(ROOT / "site")
    rootsrv, base_root = serve(ROOT)
    async with async_playwright() as p:
        # the DevTools screencast ignores the context DPR in headless mode; this flag gives 2560x1440 frames
        browser = await p.chromium.launch(args=[f"--force-device-scale-factor={DPR}"])
        for sid in shot_ids:
            shot = shots[sid]
            fn = find_scene(sid)
            out = WORK / "capture" / sid
            if out.exists():
                shutil.rmtree(out)
            out.mkdir(parents=True)
            ctx = await browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=DPR,
                                            color_scheme="light", reduced_motion="no-preference")
            await ctx.add_init_script(INIT_JS)
            page = await ctx.new_page()
            cdp = await ctx.new_cdp_session(page)
            r = Rec(page, cdp, shot, out, base, base_root + "")
            if shot["entry"] == "type":
                r.pos = URLBAR  # the cursor starts at the URL bar; the compositor animates the typing
            # prep: the scene's optional `prep` attribute runs before the clock starts
            prep = getattr(fn, "prep", None)
            if prep:
                await prep(r, shot)
            else:
                await r.goto(shot["url"])
            await r.start_screencast()
            await asyncio.sleep(0.25)
            r.t0 = time.time()
            r.frames = [[round(f[2] - r.t0, 4), f[1], f[2]] for f in r.frames]
            r._log(*r.pos)
            await fn(r, shot)
            await r.at(shot["dur"] + 0.1)
            r._log(*r.pos)
            await cdp.send("Page.stopScreencast")
            await asyncio.sleep(0.2)
            r.save()
            print(f"{sid}: {len(r.frames)} frames, {len(r.cursor)} cursor samples, {len(r.clicks)} clicks")
            await ctx.close()
        await browser.close()
    site.shutdown()
    rootsrv.shutdown()


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    asyncio.run(capture(sys.argv[1:]))
