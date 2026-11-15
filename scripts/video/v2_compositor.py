"""Compositor for the v2 demo video: real browser captures -> a "screen recording on a Mac".

    uv run --with pillow --with numpy python scripts/video/v2_compositor.py --start 0 --end 14 --out /tmp/x.mp4
    uv run --with pillow --with numpy python scripts/video/v2_compositor.py --frames 3.5,11.63 --png-dir /tmp/f

Reads WORK/v2/timeline.json and WORK/v2/capture/<shot>/{track.json,frames/} (see WORK/v2/SPEC.md) and
writes a silent H.264 video. Everything lives in one "desktop" coordinate system (1920x1080 at zoom 1):
wallpaper, browser window (chrome + page viewport), cursor, highlights, notes. The camera maps a
rectangle of the desktop onto the output frame; static layers are kept at 2x and the page is sampled from
the capture frame directly (one resize with a float box per layer), so text stays sharp up to zoom 2.
Captions are drawn afterwards in output space (not affected by the camera).
"""
import argparse
import bisect
import json
import math
import os
import pathlib
import subprocess
import sys
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

WORK = pathlib.Path(os.environ.get("VIDEO_WORK", "/data/work/video")) / "v2"
FONTS = WORK / "fonts"
W, H = 1920, 1080
S = 2                                   # static layers: layer px per desktop px
WIN = (192, 44, 1728, 988)              # browser window on the desktop
CHROME_H = 80
VP = (192, 124, 1728, 988)              # page viewport
VPS = 1.2                               # CSS px -> desktop px
RADIUS = 12
MARGIN = 40                             # camera clamp: window + this much desktop
URL_CSS = (420, -40)                    # where captures put the cursor for the URL bar
PILL = (108, 45, 1444, 75)              # URL pill, window-local desktop px
URL_TEXT_X = 144
URL_CY = WIN[1] + 60                    # desktop y of the URL pill centre (104)

WHITE = (255, 255, 255)
FG = (31, 35, 40)
MUTED = (89, 99, 110)
BORDER = (209, 217, 224)
ACCENT = (9, 105, 218)
STRIP = (223, 228, 234)
PILL_BG = (237, 241, 245)
SEL = (180, 213, 254)
HL = (84, 174, 255)

WHIP = 0.36
TITLES = {
    "index.html": "Countersign: an AI agent wrote this fix",
    "pitch.html": "Countersign: pitch",
    "tour.html": "How it works: change 2234 in six steps",
    "prs.html": "PR flow: what the reviewer sees on GitHub",
    "overview.html": "Countersign: the numbers",
    "packs/2234/pack.html": "Countersign 2234: ask, owner Toivo",
}
# One tab per page the video visits (a real tab switch replaces typing URLs): window-local desktop px.
TABS = ["index.html", "pitch.html", "tour.html", "packs/2234/pack.html", "prs.html", "overview.html"]
TAB_X0, TAB_W = 84, 210
TAB_CY = 24                             # window-local y of the tab titles
TAB_GLIDE0, TAB_GLIDE1, TAB_CLICK = 0.30, 0.80, 0.84   # type entry: glide to the tab, click (page switches)


def tab_index(url):
    try:
        return TABS.index(url.split("#")[0])
    except ValueError:
        return 0


def tab_css(i):
    """CSS-space point the cursor clicks on tab i (the chrome is above the viewport: y < 0)."""
    x = TAB_X0 + TAB_W * i + 92
    y = URL_CSS[1] + (WIN[1] + TAB_CY - URL_CY) / VPS
    return x / VPS, y


# ----------------------------------------------------------------------------------------- helpers
def ease_io(u):
    u = min(1.0, max(0.0, u))
    return 4 * u * u * u if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def clamp(v, a, b):
    return a if v < a else b if v > b else v


_fonts = {}


def font(size, weight=400, mono=False):
    key = (round(size * 4) / 4, weight, mono)
    f = _fonts.get(key)
    if f is None:
        f = ImageFont.truetype(str(FONTS / ("JetBrainsMono.ttf" if mono else "Inter.ttf")), key[0])
        try:
            axes = f.get_variation_axes()
            vals = []
            for a in axes:
                n = a["name"].lower() if isinstance(a["name"], str) else a["name"].decode().lower()
                vals.append(clamp(size, a["minimum"], a["maximum"]) if "optical" in n else
                            clamp(weight, a["minimum"], a["maximum"]) if "weight" in n else a["default"])
            f.set_variation_by_axes(vals)
        except Exception:
            pass
        _fonts[key] = f
    return f


def rrect_alpha(w, h, rect, r, ox=0.0, oy=0.0):
    """Anti-aliased rounded-rect coverage (float32 HxW) via a signed distance; rect in pixel units."""
    x0, y0, x1, y1 = rect
    ys = np.arange(h, dtype=np.float32)[:, None] + 0.5 + oy
    xs = np.arange(w, dtype=np.float32)[None, :] + 0.5 + ox
    cx, cy, hw, hh = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    qx = np.abs(xs - cx) - (hw - r)
    qy = np.abs(ys - cy) - (hh - r)
    d = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r
    return d


def cov(d):
    return np.clip(0.5 - d, 0, 1).astype(np.float32)


def L(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), "L")


def css_to_desk(x, y):
    if y >= 0:
        return WIN[0] + VPS * x, VP[1] + VPS * y
    # In the chrome: CSS y=-40 is the URL bar (captures log it there); keep it continuous.
    if y >= URL_CSS[1]:
        return WIN[0] + VPS * x, URL_CY + (y - URL_CSS[1]) / -URL_CSS[1] * (VP[1] - URL_CY)
    return WIN[0] + VPS * x, URL_CY + (y - URL_CSS[1]) * VPS


# ----------------------------------------------------------------------------------- static layers
def make_background():
    """Wallpaper + shadow + window body at S x (no menu bar: it is not trying to be a full screen grab); plus the window coverage mask at S x."""
    w1, h1 = W, H
    ys, xs = np.mgrid[0:h1, 0:w1].astype(np.float32)
    u = (xs / w1 * 0.6 + ys / h1 * 0.4)[..., None]
    c0, c1 = np.array([219, 231, 245], np.float32), np.array([197, 214, 236], np.float32)
    img = c0 * (1 - u) + c1 * u
    g = np.exp(-(((xs - 1620) / 620) ** 2 + ((ys - 980) / 420) ** 2))[..., None]
    img = img * (1 - 0.16 * g) + np.array(ACCENT, np.float32) * 0.16 * g
    g2 = np.exp(-(((xs - 260) / 700) ** 2 + ((ys - 120) / 420) ** 2))[..., None]
    img = img * (1 - 0.35 * g2) + 255 * 0.35 * g2
    # soft shadow: 0 20px 50px rgba(31,35,40,.28)
    sh = L(cov(rrect_alpha(w1, h1, (WIN[0], WIN[1] + 20, WIN[2], WIN[3] + 20), RADIUS)))
    sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(25)), np.float32)[..., None] / 255 * 0.28
    sh2 = L(cov(rrect_alpha(w1, h1, (WIN[0], WIN[1] + 3, WIN[2], WIN[3] + 3), RADIUS)))
    sh2 = np.asarray(sh2.filter(ImageFilter.GaussianBlur(4)), np.float32)[..., None] / 255 * 0.10
    for a in (sh, sh2):
        img = img * (1 - a) + np.array(FG, np.float32) * a
    img += np.random.default_rng(1).normal(0, 0.6, img.shape).astype(np.float32)   # anti-banding
    bg = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").resize((W * S, H * S), Image.BICUBIC)

    # window body + 1 px ring rgba(0,0,0,.08)
    d = rrect_alpha(W * S, H * S, tuple(v * S for v in WIN), RADIUS * S)
    body = cov(d)
    ring = np.clip(1 - np.abs(d - 1.0), 0, 1) * 0.10
    arr = np.asarray(bg, np.float32)
    arr = arr * (1 - ring[..., None])
    arr = arr * (1 - body[..., None]) + 255 * body[..., None]
    bg = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")

    return bg, L(body)


def favicon(dr, D, x, y, spin=None):
    # site/favicon.svg: Material Symbols Rounded "check_box" (filled), #1f2328
    if spin is None:
        dr.rounded_rectangle([(x + 1.8) * D, (y + 1.8) * D, (x + 14.2) * D, (y + 14.2) * D], radius=1.8 * D, fill=FG)
        dr.line([(x + 4.9) * D, (y + 8.2) * D, (x + 7.0) * D, (y + 10.3) * D, (x + 11.2) * D, (y + 6.1) * D],
                fill=WHITE, width=int(1.75 * D), joint="curve")
    else:
        a0 = (spin * 360) % 360
        dr.arc([(x + 1) * D, (y + 1) * D, (x + 15) * D, (y + 15) * D], a0, a0 + 270, fill=ACCENT, width=int(2 * D))


def draw_chrome(title, url, mode="show", nsel=(0, 0), typed=None, caret=False, load=0.0, load_a=0.0, spin=None,
                active=0):
    """The browser's top 80 px (tab strip + toolbar), window-local, at S x."""
    D = 4
    w, h = WIN[2] - WIN[0], CHROME_H
    im = Image.new("RGB", (w * D, h * D), STRIP)
    dr = ImageDraw.Draw(im)

    def R(x0, y0, x1, y1):
        return [x0 * D, y0 * D, x1 * D, y1 * D]

    dr.rectangle(R(0, 40, w, h), fill=WHITE)
    # traffic lights
    for i, (c, b) in enumerate([((255, 95, 87), (224, 68, 62)), ((254, 188, 46), (222, 161, 35)),
                                ((40, 200, 64), (26, 171, 41))]):
        x = 21 + 20 * i
        dr.ellipse(R(x - 6, 15, x + 6, 27), fill=b)
        dr.ellipse(R(x - 5.4, 15.6, x + 5.4, 26.4), fill=c)
    # tab strip: one tab per page; the active one is white with flared bottom corners
    for i in range(len(TABS)):
        x0 = TAB_X0 + TAB_W * i
        if i != active and i + 1 != active and i + 1 < len(TABS):
            dr.line(R(x0 + TAB_W, 15, x0 + TAB_W, 33), fill=(196, 203, 211), width=int(1 * D))
    tx0, tx1 = TAB_X0 + TAB_W * active, TAB_X0 + TAB_W * (active + 1)
    dr.rounded_rectangle(R(tx0, 7, tx1, 50), radius=9 * D, fill=WHITE)
    for cx, sx in ((tx0, -1), (tx1, 1)):
        dr.rectangle(R(min(cx, cx + sx * 9), 31, max(cx, cx + sx * 9), 40), fill=WHITE)
        dr.ellipse(R(cx + sx * 9 - 9, 22, cx + sx * 9 + 9, 40), fill=STRIP)
    f = font(13 * D, 450)
    xs = np.arange(im.size[0], dtype=np.float32)
    for i, page in enumerate(TABS):
        x0, x1 = TAB_X0 + TAB_W * i, TAB_X0 + TAB_W * (i + 1)
        favicon(dr, D, x0 + 13, 15.5, spin if i == active else None)
        # title, faded out at the right edge (as Chrome truncates)
        tl = Image.new("L", im.size, 0)
        ImageDraw.Draw(tl).text(((x0 + 37) * D, TAB_CY * D), TITLES[page], font=f, fill=255, anchor="lm")
        fade_x1, fade_x0 = (x1 - 34) * D, (x1 - 54) * D
        ramp = np.clip((fade_x1 - xs) / (fade_x1 - fade_x0), 0, 1) * (xs >= x0 * D)
        tla = np.asarray(tl, np.float32) * ramp[None, :]
        im.paste(FG if i == active else (60, 66, 74), (0, 0), Image.fromarray(tla.astype(np.uint8), "L"))
        cx, cy = x1 - 20, TAB_CY
        for a, b in (((-4, -4), (4, 4)), ((-4, 4), (4, -4))):
            dr.line(R(cx + a[0], cy + a[1], cx + b[0], cy + b[1]), fill=MUTED, width=int(1.5 * D))
    px = TAB_X0 + TAB_W * len(TABS) + 22
    dr.line(R(px - 6, 24, px + 6, 24), fill=MUTED, width=int(1.6 * D))
    dr.line(R(px, 18, px, 30), fill=MUTED, width=int(1.6 * D))
    # toolbar icons: back, forward (disabled), reload
    lw = int(1.8 * D)
    y = 60
    dr.line(R(16, y, 30, y), fill=MUTED, width=lw)
    dr.line([16 * D + lw / 3, y * D, 22 * D, (y - 6) * D], fill=MUTED, width=lw)
    dr.line([16 * D + lw / 3, y * D, 22 * D, (y + 6) * D], fill=MUTED, width=lw)
    dis = (184, 191, 199)
    dr.line(R(46, y, 60, y), fill=dis, width=lw)
    dr.line([60 * D - lw / 3, y * D, 54 * D, (y - 6) * D], fill=dis, width=lw)
    dr.line([60 * D - lw / 3, y * D, 54 * D, (y + 6) * D], fill=dis, width=lw)
    rx = 86
    dr.arc(R(rx - 7, y - 7, rx + 7, y + 7), -40, 260, fill=MUTED, width=lw)
    ax, ay = rx + 7 * math.cos(math.radians(-40)), y + 7 * math.sin(math.radians(-40))
    dr.polygon([(ax * D + 4.5 * D, ay * D - 5.5 * D), (ax * D + 4 * D, ay * D + 2 * D), (ax * D - 3 * D, ay * D - 1 * D)],
               fill=MUTED)
    # URL pill
    x0, y0, x1, y1 = PILL
    focused = mode in ("select", "type")
    if focused:
        dr.rounded_rectangle(R(x0 - 1, y0 - 1, x1 + 1, y1 + 1), radius=16 * D, fill=ACCENT)
        dr.rounded_rectangle(R(x0 + 1, y0 + 1, x1 - 1, y1 - 1), radius=14 * D, fill=WHITE)
    else:
        dr.rounded_rectangle(R(x0, y0, x1, y1), radius=15 * D, fill=PILL_BG)
    ix = x0 + 19
    dr.ellipse(R(ix - 7.5, y - 7.5, ix + 7.5, y + 7.5), outline=MUTED, width=int(1.5 * D))
    dr.ellipse(R(ix - 1, y - 4.6, ix + 1, y - 2.6), fill=MUTED)
    dr.line(R(ix, y - 1, ix, y + 4.4), fill=MUTED, width=int(1.8 * D))
    # star
    sx, sy, ro, ri = x1 - 22, y, 7.5, 3.3
    pts = []
    for k in range(10):
        r = ro if k % 2 == 0 else ri
        a = math.radians(-90 + k * 36)
        pts.append((sx + r * math.cos(a)) * D)
        pts.append((sy + r * math.sin(a)) * D)
    dr.polygon(pts, outline=MUTED, width=int(1.5 * D))
    # URL text
    f = font(15 * D, 430)
    tx = URL_TEXT_X * D
    if mode == "show":
        cut = url.find("/")
        host, path = (url, "") if cut < 0 else (url[:cut], url[cut:])
        dr.text((tx, y * D), host, font=f, fill=MUTED, anchor="lm")
        if path:
            dr.text((tx + f.getlength(host), y * D), path, font=f, fill=FG, anchor="lm")
    else:
        a, b = nsel
        if b > a:
            sxa = tx + f.getlength(url[:a])
            sxb = tx + f.getlength(url[:b])
            dr.rectangle([sxa, (y - 10) * D, sxb, (y + 10) * D], fill=SEL)
        dr.text((tx, y * D), url, font=f, fill=FG, anchor="lm")
        if caret:
            cxp = tx + f.getlength(url[:a if b > a else len(url)] if typed is None else url[:typed])
            dr.rectangle([cxp, (y - 9.5) * D, cxp + 1.4 * D, (y + 9.5) * D], fill=FG)
    # profile + kebab
    px = w - 60
    dr.ellipse(R(px - 11, y - 11, px + 11, y + 11), fill=(221, 244, 255))
    dr.text((px * D, y * D + D), "T", font=font(12 * D, 600), fill=ACCENT, anchor="mm")
    kx = w - 26
    for dy in (-6, 0, 6):
        dr.ellipse(R(kx - 1.7, y + dy - 1.7, kx + 1.7, y + dy + 1.7), fill=MUTED)
    dr.rectangle(R(0, h - 1, w, h), fill=BORDER)
    out = im.resize((w * S, h * S), Image.LANCZOS)
    if load_a > 0 and load > 0:
        bar = Image.new("RGB", (max(1, int(w * S * load)), 3 * S // 2 + 1), ACCENT)
        m = Image.new("L", bar.size, int(255 * load_a))
        out.paste(bar, (0, h * S - bar.size[1]), m)
    return out


def make_cursor_master():
    """macOS-style arrow: white fill, black outline, soft shadow. Returns (RGBA, hotspot, height)."""
    u = 12.0                            # px per unit at master scale
    pts = [(0, 0), (0, 16.6), (3.95, 12.85), (6.55, 18.95), (9.35, 17.75), (6.85, 11.85), (12.25, 11.85)]
    pad = 4.5
    sz = (int((12.25 + 2 * pad) * u), int((18.95 + 2 * pad) * u))
    D = 4
    big = Image.new("RGBA", (sz[0] * D, sz[1] * D), (0, 0, 0, 0))
    dr = ImageDraw.Draw(big)
    P = [((x + pad) * u * D, (y + pad - 0.4) * u * D) for x, y in pts]
    dr.polygon(P, fill=(255, 255, 255, 255))
    dr.line(P + [P[0]], fill=(0, 0, 0, 255), width=int(1.0 * u * D), joint="curve")
    arrow = big.resize(sz, Image.LANCZOS)
    a = arrow.getchannel("A")
    shadow = Image.new("RGBA", sz, (0, 0, 0, 0))
    sm = a.filter(ImageFilter.GaussianBlur(1.1 * u)).point(lambda v: int(v * 0.42))
    shadow.paste((0, 0, 0, 255), (0, int(0.9 * u)), sm)
    out = Image.alpha_composite(shadow, arrow)
    return out, ((pad) * u, (pad - 0.4) * u), 19.95 * u


# ------------------------------------------------------------------------------------- timeline
def chunk_line(words):
    """Split a voice line into caption chunks (<= 7 words): a small DP that prefers breaks at
    punctuation, chunks of ~5 words, and never ends a chunk on a weak word (article, preposition)."""
    WEAK = {"the", "a", "an", "of", "to", "and", "in", "on", "its", "our", "is", "are", "were", "what", "can",
            "each", "new", "every", "into", "for", "from", "whether", "but", "so", "it", "may"}
    CONJ = {"and", "but", "which", "so", "that", "were", "was", "then", "or"}
    n = len(words)
    txt = [w[0] for w in words]

    def cost(j, i):
        size = i - j
        end = txt[i - 1]
        c = 1.0 + 0.12 * (size - 5) ** 2
        if i == n or end[-1] in ".!?":
            pass
        elif end[-1] in ",;:":
            c += 0.3
        else:
            c += 1.8 + (2.5 if end.lower() in WEAK else 0) + (2.5 if i < n and txt[i].lower() == "of" else 0)
        if j > 0 and txt[j].lower() in CONJ:
            c -= 0.5
        return c

    best = [0.0] + [math.inf] * n
    back = [0] * (n + 1)
    for i in range(1, n + 1):
        for j in range(max(0, i - 7), i):
            if any(txt[k][-1] in ".!?" for k in range(j, i - 1)):
                continue                          # never run across a sentence end
            c = best[j] + cost(j, i)
            if c < best[i]:
                best[i], back[i] = c, j
    out, i = [], n
    while i > 0:
        out.append(words[back[i]:i])
        i = back[i]
    return out[::-1]


class Shot:
    pass


def load(timeline_path, capture_dir):
    tl = json.loads(pathlib.Path(timeline_path).read_text())
    capture_dir = pathlib.Path(capture_dir)
    lead = tl.get("type_lead", 1.0)
    shots = []
    for i, s in enumerate(tl["shots"]):
        sh = Shot()
        sh.i, sh.id, sh.entry, sh.t0, sh.dur = i, s["id"], s["entry"], s["t0"], s["dur"]
        sh.url, sh.display = s["url"], s["display_url"]
        sh.title = TITLES.get(s["url"].split("#")[0], "Countersign")
        sh.tab = tab_index(s["url"])
        sh.lines = s["lines"]
        sh.lead = lead if sh.entry == "type" else 0.0
        d = capture_dir / sh.id
        tp = d / "track.json"
        if tp.exists():
            tr = json.loads(tp.read_text())
            sh.missing = False
            sh.frames = [(f[0], str(d / f[1])) for f in tr["frames"]]
        else:
            tr = {"cursor": [[0, 900, 560]], "clicks": [], "camera": [[0, 1.0, 640, 360, "io"]],
                  "highlights": [], "notes": []}
            sh.missing = True
            sh.frames = [(0.0, None)]
        sh.ftimes = [f[0] for f in sh.frames]
        sh.cursor = tr.get("cursor") or []
        sh.ctimes = [c[0] for c in sh.cursor]
        sh.clicks = list(tr.get("clicks") or [])
        sh.highlights = tr.get("highlights") or []
        plan_drags(sh)
        sh.notes = tr.get("notes") or []
        cam = [list(k) + (["io"] if len(k) < 5 else []) for k in (tr.get("camera") or [[0, 1.0, 640, 360, "io"]])]
        sh.camera = sorted(cam, key=lambda k: k[0])
        shots.append(sh)

    # type entries: a tab switch. From the previous shot's end state the cursor glides to the new page's
    # tab and clicks it; the tab becomes active and the page switches on the click (no load).
    for sh in shots:
        if sh.entry != "type" or sh.i == 0:
            continue
        prev = shots[sh.i - 1]
        sh.type_from = cursor_at(prev, prev.dur)
        sh.t_click = min(TAB_CLICK, sh.lead - 0.05)
        sh.tab_pt = tab_css(sh.tab)
        sh.clicks = [[sh.t_click, *sh.tab_pt]] + sh.clicks

    plan_camera(shots)

    # caption chunks on the global clock
    chunks = []
    for sh in shots:
        first = True
        for ln in sh.lines:
            if ln.get("chunks"):
                ks = [sum(ln["chunks"][:k]) for k in range(len(ln["chunks"]) + 1)]
                parts = [ln["words"][a:b] for a, b in zip(ks, ks[1:])]
            else:
                parts = chunk_line(ln["words"])
            for c in parts:
                st, fade = sh.t0 + c[0][1], 0.1
                if first:
                    if sh.i == 0:
                        st = 0.0
                    elif sh.entry == "whip":
                        st, fade = sh.t0 - WHIP / 2, WHIP
                    first = False
                chunks.append((st, fade, " ".join(w[0] for w in c)))
    return tl, shots, chunks


# ----------------------------------------------------------------------------------------- camera
# The captures log camera keyframes; the compositor turns them into a short list of calm moves:
#  - "lin" keyframes (slow drifts after a zoom) are dropped: the camera holds still while the voice talks.
#    Drifts started at zero speed right after an ease-out, and some reversed the zoom (a visible bounce).
#  - every move is one ease-in-out between two framed rectangles, 0.6-1.0 s long, never overlapping
#    another move. Long segments (slow push-ins) become a 0.9 s move placed where it overlaps the voice
#    least, i.e. between phrases.
#  - targets are clamped to the window first, and the move interpolates the clamped rectangles as a
#    similarity (scale exponentially about the fixed point), so no coordinate changes direction mid-move
#    and no clamp engages mid-move (that was an abrupt stop of the pan).
#  - a `type` entry zooms out to the whole window across the cut (from the end of the previous shot).
MOVE_MIN, MOVE_MAX, MOVE_LONG, MOVE_GAP = 0.6, 1.0, 0.9, 0.15
MERGE_GAP = 0.6                         # moves closer than this are merged into one
STILL_PX = 6.0                          # target changes below this (output px) are not worth a move
EXIT_DUR, EXIT_INTO = 0.8, 0.3          # type entry: zoom-out length, and how far it runs into the new shot


def rect_of(z, cx, cy):
    x, y, w, _ = view_rect(clamp(z, 1.0, 2.0), cx, cy)
    return (x, y, w)


FULL = None


def rect_lerp(A, B, e):
    xa, ya, wa = A
    xb, yb, wb = B
    if abs(wb - wa) < 1e-6 * wa:
        return xa + (xb - xa) * e, ya + (yb - ya) * e, wa
    s = (wb / wa) ** e
    px = (xa * wb - xb * wa) / (wb - wa)
    py = (ya * wb - yb * wa) / (wb - wa)
    return px - (px - xa) * s, py - (py - ya) * s, wa * s


def rect_diff(A, B):
    """Largest on-screen displacement (output px) between two framings."""
    k = W / min(A[2], B[2])
    return max(abs(A[0] - B[0]), abs(A[1] - B[1]), abs(A[2] - B[2]), abs(A[0] + A[2] - B[0] - B[2]),
               abs(A[1] + A[2] * H / W - B[1] - B[2] * H / W)) * k


def speech_spans(sh):
    sp = sorted((w[1], w[2]) for ln in sh.lines for w in ln["words"])
    out = []
    for a, b in sp:
        if out and a - out[-1][1] < 0.15:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def overlap(spans, a, b):
    return sum(max(0.0, min(b, y) - max(a, x)) for x, y in spans)


def plan_camera(shots):
    global FULL
    FULL = rect_of(1.0, 640.0, (540 - VP[1]) / VPS)
    for sh in shots:
        nxt = shots[sh.i + 1] if sh.i + 1 < len(shots) else None
        kfs = [k for k in sh.camera if k[4] != "lin"]
        if sh.entry == "type" and sh.i > 0:
            cur, t_prev, free = FULL, sh.lead, sh.lead + 0.15
            kfs = [k for k in kfs if k[0] > sh.lead + 1e-3]
        else:
            cur, t_prev = rect_of(*kfs[0][1:4]), kfs[0][0]
            free = 0.4 if sh.entry == "cold" else WHIP / 2 + 0.1
            kfs = kfs[1:]
        latest = sh.dur - (WHIP / 2 + 0.05 if nxt is not None and nxt.entry == "whip" else 0.1)
        sh.cam0, sh.moves, flex = cur, [], []
        spans = speech_spans(sh)
        for k in kfs:
            tgt = rect_of(*k[1:4])
            if rect_diff(cur, tgt) < STILL_PX:
                t_prev = max(t_prev, k[0])
                continue
            a, b = max(t_prev, free), k[0]
            if b - a <= MOVE_MAX:
                d = max(MOVE_MIN, b - a)
                start = max(free, b - d)
            else:
                d = MOVE_LONG
                n = int((b - a - d) * 30)
                ends = [a + d + i / 30 for i in range(n + 1)]
                end = min(ends, key=lambda e: (round(overlap(spans, e - d, e), 2), -e))
                start = end - d
            end = min(start + d, latest)
            if end - start < 0.45:
                continue
            flexible = b - a > MOVE_MAX
            if sh.moves and start - sh.moves[-1][1] < MERGE_GAP:
                # two moves nearly back to back read as stop-and-go: make them one move, timed like the
                # word-timed one of the two (the second, unless only the first was word-timed)
                p, p_flex = sh.moves.pop(), flex.pop()
                if p_flex:
                    start = max(p[0], end - MOVE_MAX)
                else:
                    start, end = p[0], min(end, p[0] + MOVE_MAX)
                if rect_diff(p[2], tgt) >= STILL_PX:
                    sh.moves.append((start, end, p[2], tgt))
                    flex.append(False)
            else:
                sh.moves.append((start, end, cur, tgt))
                flex.append(flexible)
            cur, t_prev, free = tgt, max(k[0], end), end + MOVE_GAP
    # type entries: zoom out to the whole window across the cut, as one move shared by both shots
    for sh in shots:
        if sh.entry != "type" or sh.i == 0:
            continue
        prev = shots[sh.i - 1]
        end_state = prev.moves[-1][3] if prev.moves else prev.cam0
        if rect_diff(end_state, FULL) < STILL_PX:
            sh.cam0 = FULL
            continue
        start = prev.dur + EXIT_INTO - EXIT_DUR
        if prev.moves and prev.moves[-1][1] + MOVE_GAP > start:
            start = prev.moves[-1][1] + MOVE_GAP
        prev.moves.append((start, start + EXIT_DUR, end_state, FULL))
        sh.cam0 = end_state
        sh.moves.insert(0, (start - prev.dur, start + EXIT_DUR - prev.dur, end_state, FULL))


def view_at(sh, t):
    """Desktop rectangle (x, y, w, h) the camera shows at shot time t."""
    cur = sh.cam0
    for t0, t1, A, B in sh.moves:
        if t < t0:
            break
        if t < t1:
            cur = rect_lerp(A, B, ease_io((t - t0) / (t1 - t0)))
            break
        cur = B
    return cur[0], cur[1], cur[2], cur[2] * H / W


def view_rect(z, cx, cy):
    """Desktop rectangle shown in the output frame (x, y, w, h)."""
    z = clamp(z, 1.0, 2.0)
    w, h = W / z, H / z
    px, py = css_to_desk(cx, cy)
    ax0, ay0, ax1, ay1 = WIN[0] - MARGIN, WIN[1] - MARGIN, WIN[2] + MARGIN, WIN[3] + MARGIN
    res = []
    for p, size, a0, a1, full in ((px, w, ax0, ax1, W), (py, h, ay0, ay1, H)):
        if size <= a1 - a0:
            lo, hi = a0, a1 - size
        else:
            lo, hi = max(0, a1 - size), min(a0, full - size)
        res.append(clamp(p - size / 2, lo, max(lo, hi)))
    return res[0], res[1], w, h


# ------------------------------------------------------------------------------ highlighter drags
# A highlight is a text selection, so the cursor makes it: it glides to the start of the phrase, presses,
# drags across the words with the selection edge (same easing and duration as the sweep), and releases at
# the end. Lines of a multi-line phrase (several boxes logged at the same time) are swept one after
# another, the cursor hopping to the start of the next line. Before and after, the drawn cursor blends
# from/to the captured track, so it never jumps.
HL_PAD = 4                               # CSS px around the words (as drawn by Renderer.highlight)
DRAG_IN, DRAG_PRESS, DRAG_HOP, DRAG_OUT, DRAG_BACK = 0.5, 0.06, 0.2, 0.25, 0.5


def sweep_dur(w):
    return clamp(0.3 + (w + 2 * HL_PAD) / 600, 0.45, 0.8)


def plan_drags(sh):
    sh.drags = []
    groups = []
    for hl in sorted(sh.highlights, key=lambda h: (h["t"], h["box"][1])):
        if groups and abs(hl["t"] - groups[-1][0]["t"]) < 0.02:
            groups[-1].append(hl)
        else:
            groups.append([hl])
    for g in groups:
        t0 = g[0]["t"]
        t, segs = t0, []
        for i, hl in enumerate(g):
            x, y, w, h = hl["box"]
            yy = y + h * 0.6
            if i:
                segs.append(("hop", t, t + DRAG_HOP, segs[-1][4], segs[-1][5], x - HL_PAD, yy))
                t += DRAG_HOP
            sd = sweep_dur(w)
            hl["t"], hl["sd"] = round(t, 3), sd
            segs.append(("sweep", t, t + sd, x - HL_PAD, yy, x + w + HL_PAD, yy))
            t += sd
        start = (segs[0][3], segs[0][4])
        sh.drags.append({"in": t0 - DRAG_IN, "press": t0 - DRAG_PRESS, "segs": segs, "release": t,
                         "start": start, "end": (segs[-1][5], segs[-1][6])})


def _drag_pos(sh, t, base):
    for d in getattr(sh, "drags", ()):
        if t < d["in"] or t > d["release"] + DRAG_OUT + DRAG_BACK:
            continue
        if t < d["press"]:
            e = min_jerk((t - d["in"]) / (d["press"] - d["in"]))
            return base[0] + (d["start"][0] - base[0]) * e, base[1] + (d["start"][1] - base[1]) * e
        if t <= d["segs"][0][1]:
            return d["start"]
        for kind, a, b, x0, y0, x1, y1 in d["segs"]:
            if a <= t <= b:
                e = ease_io((t - a) / (b - a)) if kind == "sweep" else min_jerk((t - a) / (b - a))
                return x0 + (x1 - x0) * e, y0 + (y1 - y0) * e
        if t <= d["release"] + DRAG_OUT:
            return d["end"]
        e = min_jerk((t - d["release"] - DRAG_OUT) / DRAG_BACK)
        return d["end"][0] + (base[0] - d["end"][0]) * e, d["end"][1] + (base[1] - d["end"][1]) * e
    return base


def min_jerk(u):
    u = clamp(u, 0.0, 1.0)
    return u * u * u * (10 - 15 * u + 6 * u * u)


def pressed(sh, t):
    """0..1: how far the button is held down (a drag), for the cursor's press feedback."""
    for d in getattr(sh, "drags", ()):
        if d["press"] - 0.08 <= t <= d["release"] + 0.1:
            return min(clamp((t - d["press"] + 0.08) / 0.08, 0, 1), clamp((d["release"] + 0.1 - t) / 0.1, 0, 1))
    return 0.0


def cursor_at(sh, t):
    """Cursor CSS position at shot time t (track, or the synthesised URL-bar move of a type entry), with
    the highlighter drags laid over it."""
    p = _cursor_track(sh, t)
    return p if p is None else _drag_pos(sh, t, p)


def _cursor_track(sh, t):
    if sh.entry == "type" and hasattr(sh, "type_from") and t < sh.lead:
        x0, y0 = sh.type_from
        x1, y1 = sh.tab_pt
        e = min_jerk((t - TAB_GLIDE0) / (TAB_GLIDE1 - TAB_GLIDE0))
        dx, dy = x1 - x0, y1 - y0
        dist = math.hypot(dx, dy) or 1
        arc = math.sin(math.pi * e) * min(40, dist * 0.07)
        return x0 + dx * e - dy / dist * arc, y0 + dy * e + dx / dist * arc
    p = _cursor_log(sh, t)
    if p is not None and sh.entry == "type" and hasattr(sh, "tab_pt") and t < sh.lead + TAB_BACK:
        # the capture logs the cursor at the URL bar at type_lead: blend from the tab into the logged track
        k = 1 - min_jerk((t - sh.lead) / TAB_BACK)
        p = (p[0] + (sh.tab_pt[0] - URL_CSS[0]) * k, p[1] + (sh.tab_pt[1] - URL_CSS[1]) * k)
    return p


TAB_BACK = 0.5


def _cursor_log(sh, t):
    c = sh.cursor
    if not c:
        return None
    i = bisect.bisect_right(sh.ctimes, t)
    if i == 0:
        return c[0][1], c[0][2]
    if i >= len(c):
        return c[-1][1], c[-1][2]
    a, b = c[i - 1], c[i]
    u = (t - a[0]) / max(1e-6, b[0] - a[0])
    return a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u


# ------------------------------------------------------------------------------- per-frame render
class Renderer:
    def __init__(self, timeline_path, capture_dir):
        self.tl, self.shots, self.chunks = load(timeline_path, capture_dir)
        self.fps = self.tl["fps"]
        self.total = self.tl["total"]
        self.bg, self.winmask = make_background()
        self.cur_master, self.cur_hot, self.cur_h = make_cursor_master()
        self._chrome, self._frames, self._caps = {}, {}, {}
        self.chunk_starts = [c[0] for c in self.chunks]

    # ---- sources
    def page_image(self, sh, t):
        if sh.missing:
            key = ("missing", sh.id)
            if key not in self._frames:
                im = Image.new("RGB", (1280, 720), WHITE)
                ImageDraw.Draw(im).text((640, 360), f"{sh.id} missing", font=font(16), fill=(150, 156, 163),
                                        anchor="mm")
                self._frames[key] = pad(im)
            return self._frames[key]
        i = max(0, bisect.bisect_right(sh.ftimes, t) - 1)
        path = sh.frames[i][1]
        im = self._frames.get(path)
        if im is None:
            if len(self._frames) > 6:
                self._frames.clear()
            im = self._frames[path] = pad(Image.open(path).convert("RGB"))
        return im

    def chrome(self, sh, t):
        prev = self.shots[sh.i - 1] if sh.i else None
        st = dict(title=sh.title, url=sh.display)
        st["active"] = sh.tab
        if sh.entry == "type" and prev is not None and t < sh.t_click:
            st = dict(title=prev.title, url=prev.display, active=prev.tab)
        key = tuple(sorted((k, v if not isinstance(v, list) else tuple(v)) for k, v in st.items()))
        im = self._chrome.get(key)
        if im is None:
            if len(self._chrome) > 40:
                self._chrome.clear()
            im = self._chrome[key] = pad(draw_chrome(**st), 2)
        return im

    # ---- one shot at shot time t (no captions)
    def compose(self, sh, t):
        vx, vy, vw, vh = view_at(sh, t)
        k = W / vw                                    # output px per desktop px

        def to_out(x, y):
            return (x - vx) * k, (y - vy) * k

        box = (vx * S, vy * S, (vx + vw) * S, (vy + vh) * S)
        base = self.bg.resize((W, H), Image.LANCZOS, box=box)
        content = base.copy()
        # page
        prev = self.shots[sh.i - 1] if sh.i else None
        if sh.entry == "type" and prev is not None and t < sh.t_click:
            page = self.page_image(prev, prev.dur + 1)
        elif sh.entry == "type" and prev is not None:
            page = self.page_image(sh, max(t, sh.lead))    # the tab switch: the new page at once
        else:
            page = self.page_image(sh, t)
        place(content, page, (*to_out(VP[0], VP[1]), *to_out(VP[2], VP[3])))
        # highlights (multiply, under the cursor)
        if not (sh.entry == "type" and t < sh.lead):
            for hl in sh.highlights:
                self.highlight(content, hl, t, to_out, k)
        place(content, self.chrome(sh, t), (*to_out(WIN[0], WIN[1]), *to_out(WIN[2], WIN[1] + CHROME_H)), padpx=2)
        mask = self.winmask.resize((W, H), Image.LANCZOS, box=box)
        frame = Image.composite(content, base, mask)
        if not (sh.entry == "type" and t < sh.lead):
            for nt in sh.notes:
                self.note(frame, sh, nt, t, to_out, k)
        self.cursor(frame, sh, t, to_out, k)
        return frame

    def highlight(self, img, hl, t, to_out, k):
        t0, t1 = hl["t"], hl.get("until", hl["t"] + 3)
        if t < t0 or t > t1 + 0.3:
            return
        sd = hl.get("sd", 0.35)
        prog = ease_io((t - t0) / sd) if t < t0 + sd else 1.0
        alpha = 0.34 * (1 - clamp((t - t1) / 0.3, 0, 1))
        x, y, w, h = hl["box"]
        p = 4
        dx0, dy0 = css_to_desk(x - p, y - p)
        dx1, dy1 = css_to_desk(x + w + p, y + h + p)
        ox0, oy0 = to_out(dx0, dy0)
        ox1, oy1 = to_out(dx1, dy1)
        vx0, vy0 = to_out(VP[0], VP[1])
        vx1, vy1 = to_out(VP[2], VP[3])
        X0, Y0 = int(max(0, vx0, math.floor(ox0))), int(max(0, vy0, math.floor(oy0)))
        X1, Y1 = int(min(W, vx1, math.ceil(ox1))), int(min(H, vy1, math.ceil(oy1)))
        if X1 <= X0 or Y1 <= Y0:
            return
        d = rrect_alpha(X1 - X0, Y1 - Y0, (ox0 - X0, oy0 - Y0, ox1 - X0, oy1 - Y0), 4 * k / VPS)
        m = cov(d)
        sweep_x = ox0 - X0 + (ox1 - ox0) * prog
        xs = np.arange(X1 - X0, dtype=np.float32) + 0.5
        m *= np.clip((sweep_x - xs) / max(1.0, 6 * k / VPS) + 0.5, 0, 1)[None, :]
        reg = np.asarray(img.crop((X0, Y0, X1, Y1)), np.float32)
        f = 1 - alpha * m[..., None] * (1 - np.array(HL, np.float32) / 255)
        img.paste(Image.fromarray(np.clip(reg * f + 0.5, 0, 255).astype(np.uint8), "RGB"), (X0, Y0))

    def note(self, img, sh, nt, t, to_out, k):
        t0, t1 = nt["t"], nt.get("until", nt["t"] + 4)
        if t < t0 or t > t1 + 0.25:
            return
        zref = W / view_at(sh, min(t1, t0 + 0.5))[2]
        s_out = k / zref                              # output px per "note px" (26 px text at zref)
        s = 2.0                                       # drawn at 2x, then placed with float precision
        a_in = clamp((t - t0) / 0.15, 0, 1)
        a = a_in * (1 - clamp((t - t1) / 0.25, 0, 1))
        text = nt["text"]
        n = clamp(int((t - t0 - 0.12) * 35) + 1, 0, len(text)) if t > t0 + 0.12 else 0
        f = font(26 * s, 430)
        padx, pady, r = 16 * s, 11 * s, 8 * s
        th = 26 * s * 1.25
        full_cw = f.getlength(text) + 2 * padx + 3 * s
        cw = f.getlength(text[:n]) + 2 * padx + 3 * s     # the card grows as the text is typed
        ch = th + 2 * pady
        ax, ay = to_out(*css_to_desk(*nt["anchor"]))
        ax, ay = ax * s / s_out, ay * s / s_out        # layout in the 2x card space
        gap = 14 * s
        q = s / s_out                                 # card px per output px
        Wq = W * q
        if ax + gap + full_cw <= min(Wq - 16 * q, to_out(VP[2], 0)[0] * q - 8 * s):
            x0 = clamp(ax + gap, 16 * q, Wq - 16 * q - full_cw)
        else:
            x0 = clamp(ax - gap - full_cw, 16 * q, Wq - 16 * q - full_cw) + full_cw - cw
        y0 = clamp(ay - ch / 2, 16 * q, 1000 * q - ch)
        sc = 0.96 + 0.04 * ease_io(a_in)
        sh_pad = int(24 * s)
        cwi, chi = int(math.ceil(cw)) + 2 * sh_pad, int(math.ceil(ch)) + 2 * sh_pad
        card = np.zeros((chi, cwi, 4), np.float32)
        d = rrect_alpha(cwi, chi, (sh_pad, sh_pad, sh_pad + cw, sh_pad + ch), r)
        shadow = L(cov(rrect_alpha(cwi, chi, (sh_pad, sh_pad + 6 * s, sh_pad + cw, sh_pad + ch + 6 * s), r)))
        shadow = np.asarray(shadow.filter(ImageFilter.GaussianBlur(9 * s)), np.float32) / 255 * 0.18
        body = cov(d)
        ring = np.clip(1 - np.abs(d + 0.5), 0, 1)
        col = np.zeros((chi, cwi, 3), np.float32)
        col[:] = np.array(FG, np.float32)
        col = col * (1 - body[..., None]) + 255 * body[..., None]
        col = col * (1 - ring[..., None]) + np.array(BORDER, np.float32) * ring[..., None]
        al = np.maximum(shadow, np.maximum(body, ring))
        card = Image.fromarray(np.dstack([np.clip(col, 0, 255), al * 255]).astype(np.uint8), "RGBA")
        dr = ImageDraw.Draw(card)
        tx, ty = sh_pad + padx, sh_pad + ch / 2
        dr.text((tx, ty), text[:n], font=f, fill=FG + (255,), anchor="lm")
        if n < len(text) or (t * 2) % 1 < 0.5:
            cx = tx + f.getlength(text[:n]) + 1 * s
            dr.rectangle([cx, ty - 13 * s, cx + max(1.5, 2 * s), ty + 13 * s], fill=ACCENT + (255,))
        if a < 0.999:
            card.putalpha(card.getchannel("A").point(lambda v: int(v * a)))
        f_ = sc / q                                   # card px -> output px, with the pop-in scale
        cxo = (x0 - sh_pad + cwi / 2) / q - cwi * f_ / 2
        cyo = (y0 - sh_pad + chi / 2) / q - chi * f_ / 2
        paste_scaled(img, card, cxo, cyo, f_)

    def cursor(self, img, sh, t, to_out, k):
        p = cursor_at(sh, t)
        if p is None:
            return
        ox, oy = to_out(*css_to_desk(*p))
        size = clamp(30 * k, 26, 44)
        # clicks: shrink + ripple
        scale = 1.0
        for c in sh.clicks:
            dt = t - c[0]
            if 0 <= dt < 0.45:
                if dt < 0.16:
                    scale = min(scale, 0.85 if dt < 0.1 else 0.85 + 0.15 * (dt - 0.1) / 0.06)
                if dt < 0.35:
                    rx, ry = to_out(*css_to_desk(c[1], c[2]))
                    ripple(img, rx, ry, dt / 0.35, size / 30)
        scale = min(scale, 1 - 0.12 * pressed(sh, t))   # button held during a highlighter drag
        kk = size * scale / self.cur_h      # sub-pixel position and continuous size: no stepping
        paste_scaled(img, self.cur_master, ox - self.cur_hot[0] * kk, oy - self.cur_hot[1] * kk, kk)

    def caption_text(self, text):
        sp = self._caps.get(text)
        if sp is None:
            f = font(30, 500)
            tw = f.getlength(text)
            im = Image.new("L", (int(math.ceil(tw)) + 4, 56), 0)
            ImageDraw.Draw(im).text((im.size[0] / 2, 29), text, font=f, fill=255, anchor="mm")
            sp = self._caps[text] = (im, tw + 36)
        return sp

    def caption_pill(self, pw):
        key = ("pill", int(round(pw)))
        sp = self._caps.get(key)
        if sp is None:
            pw = key[1]
            ph = 56
            d = rrect_alpha(pw + 2, ph + 2, (1, 1, 1 + pw, 1 + ph), 10)
            a = cov(d) * 0.86
            sp = Image.new("RGBA", (pw + 2, ph + 2), FG + (0,))
            sp.putalpha(L(a))
            self._caps[key] = sp
        return sp

    def captions(self, img, t):
        """Always-on caption: pill width morphs between chunks, text fades out then in."""
        i = max(0, bisect.bisect_right(self.chunk_starts, t) - 1)
        st, fade, text = self.chunks[i]
        cur_txt, cur_w = self.caption_text(text)
        u = (t - st) / fade
        if i > 0 and 0 <= u < 1:
            old_txt, old_w = self.caption_text(self.chunks[i - 1][2])
            e = ease_io(u)
            pw = old_w + (cur_w - old_w) * e
            if fade > 0.15:   # across a whip-pan: the whole caption (pill and text) fades out, then in
                k = 1 - 2 * u if u < 0.5 else 2 * u - 1
                m, w_ = (old_txt, old_w) if u < 0.5 else (cur_txt, cur_w)
                pill = self.caption_pill(w_)
                if k > 0.01:
                    pa = pill.getchannel("A").point(lambda v, k=k: int(v * k))
                    pill = pill.copy(); pill.putalpha(pa)
                    img.paste(pill, (round(W / 2 - pill.size[0] / 2), round(1036 - pill.size[1] / 2)), pill)
                    mm = m.point(lambda v, k=k: int(v * k))
                    img.paste(WHITE, (round(W / 2 - m.size[0] / 2), round(1036 - m.size[1] / 2)), mm)
                return
            else:
                texts = [(old_txt, clamp(1 - 2 * u, 0, 1)), (cur_txt, clamp(2 * u - 1, 0, 1))]
        else:
            pw, texts = cur_w, [(cur_txt, 1.0)]
        pill = self.caption_pill(pw)
        cy = 1036
        img.paste(pill, (round(W / 2 - pill.size[0] / 2), round(cy - pill.size[1] / 2)), pill)
        for m, a in texts:
            if a <= 0.01:
                continue
            if a < 0.999:
                m = m.point(lambda v, a=a: int(v * a))
            img.paste(WHITE, (round(W / 2 - m.size[0] / 2), round(cy - m.size[1] / 2)), m)

    # ---- one output frame at global time t
    def frame(self, t):
        shots = self.shots
        j = max(0, bisect.bisect_right([s.t0 for s in shots], t) - 1)
        sh = shots[j]
        img = None
        # whip window around a boundary (either side)
        for b_sh in (sh, shots[j + 1] if j + 1 < len(shots) else None):
            if b_sh is None or b_sh.entry != "whip" or b_sh.i == 0:
                continue
            b = b_sh.t0
            if b - WHIP / 2 <= t < b + WHIP / 2:
                u = (t - (b - WHIP / 2)) / WHIP
                off = ease_io(u) * W
                du = 1 / (self.fps * WHIP)
                speed = (ease_io(u + du / 2) - ease_io(u - du / 2)) * W     # px per frame
                a_sh, n_sh = shots[b_sh.i - 1], b_sh
                img = Image.new("RGB", (W, H))
                xo = round(off)
                if xo < W:
                    img.paste(self.compose(a_sh, t - a_sh.t0), (-xo, 0))
                if xo > 0:
                    img.paste(self.compose(n_sh, t - n_sh.t0), (W - xo, 0))
                r = min(80.0, speed * 0.32)
                if r >= 1:
                    img = img.filter(ImageFilter.BoxBlur((r / 2, 0))).filter(ImageFilter.BoxBlur((r / 2, 0)))
                break
        if img is None:
            img = self.compose(sh, t - sh.t0)
        self.captions(img, t)
        fade = min(1.0, t / 0.3, (self.total - t) / 0.6)
        if fade < 1:
            img = Image.eval(img, lambda v, f=max(0.0, fade): int(v * f))
        return img


def pad(im, p=4):
    """Pad a source with its edge pixels so float boxes can reach slightly outside it."""
    a = np.asarray(im)
    a = np.pad(a, ((p, p), (p, p), (0, 0)), mode="edge")
    out = Image.fromarray(a, im.mode)
    out.pad_px = p
    return out


def place(dst, src, rect, padpx=None):
    """Paste `src` (padded by src.pad_px) so it exactly covers the float output `rect`, sampled once."""
    p = getattr(src, "pad_px", 0) if padpx is None else padpx
    sw, shh = src.size[0] - 2 * p, src.size[1] - 2 * p
    x0, y0, x1, y1 = rect
    if x1 - x0 <= 0 or y1 - y0 <= 0:
        return
    sx, sy = sw / (x1 - x0), shh / (y1 - y0)
    X0, Y0 = max(0, math.floor(x0)), max(0, math.floor(y0))
    X1, Y1 = min(W, math.ceil(x1)), min(H, math.ceil(y1))
    if X1 <= X0 or Y1 <= Y0:
        return
    bx0 = clamp((X0 - x0) * sx + p, 0, src.size[0])
    bx1 = clamp((X1 - x0) * sx + p, 0, src.size[0])
    by0 = clamp((Y0 - y0) * sy + p, 0, src.size[1])
    by1 = clamp((Y1 - y0) * sy + p, 0, src.size[1])
    dst.paste(src.resize((X1 - X0, Y1 - Y0), Image.LANCZOS, box=(bx0, by0, bx1, by1)), (X0, Y0))


def paste_scaled(dst, src, x, y, scale):
    """Alpha-composite RGBA `src` so its pixel (u, v) lands on output (x + u*scale, y + v*scale), sampled
    once with float precision. `src` must have a transparent border (its outermost fraction is cropped)."""
    x1, y1 = x + src.size[0] * scale, y + src.size[1] * scale
    X0, Y0, X1, Y1 = math.ceil(x), math.ceil(y), math.floor(x1), math.floor(y1)
    if X1 <= X0 or Y1 <= Y0:
        return
    box = ((X0 - x) / scale, (Y0 - y) / scale, (X1 - x) / scale, (Y1 - y) / scale)
    sp = src.resize((X1 - X0, Y1 - Y0), Image.LANCZOS, box=box)
    dst.paste(sp, (X0, Y0), sp)


def ripple(img, x, y, u, s):
    e = 1 - (1 - u) ** 2
    r = (10 + 18 * e) * s                 # diameter 20 -> 56 px
    lw = 2.6 * s
    a = 0.35 * (1 - u)
    R = int(math.ceil(r + lw + 2))
    ys, xs = np.mgrid[-R:R, -R:R].astype(np.float32) + 0.5
    fx, fy = x - math.floor(x), y - math.floor(y)
    d = np.sqrt((xs - fx + 0.5) ** 2 + (ys - fy + 0.5) ** 2)
    m = np.clip(lw / 2 + 0.5 - np.abs(d - r), 0, 1) * a
    m = m + np.clip(r - d, 0, 1) * a * 0.18
    sp = Image.fromarray(np.dstack([np.full(m.shape + (3,), ACCENT, np.float32), np.clip(m, 0, 1) * 255]).astype(np.uint8),
                         "RGBA")
    img.paste(sp, (math.floor(x) - R, math.floor(y) - R), sp)


# ----------------------------------------------------------------------------------- driver
_R = None


def _init(timeline_path, capture_dir):
    global _R
    _R = Renderer(timeline_path, capture_dir)


def _render_one(t):
    return _R.frame(t).tobytes()


def render(timeline_path=WORK / "timeline.json", capture_dir=WORK / "capture", out_mp4_video_only="/tmp/v2.mp4",
           workers=8, start=None, end=None, every=1):
    """Render [start, end) seconds (default: whole timeline) to a silent H.264 mp4. Returns frames/s."""
    import multiprocessing as mp
    tl = json.loads(pathlib.Path(timeline_path).read_text())
    fps, total = tl["fps"], tl["total"]
    n_total = int(round(total * fps))
    f0 = int(round((start or 0) * fps))
    f1 = min(n_total, int(round(end * fps)) if end is not None else n_total)
    idx = list(range(f0, f1, max(1, every)))
    times = [i / fps for i in idx]
    out_fps = fps / max(1, every)
    workers = max(1, min(8, workers))
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", f"{out_fps}", "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out_mp4_video_only)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t_start = time.time()
    ctx = mp.get_context("fork")
    with ctx.Pool(workers, initializer=_init, initargs=(str(timeline_path), str(capture_dir))) as pool:
        for k, buf in enumerate(pool.imap(_render_one, times, chunksize=6)):
            ff.stdin.write(buf)
            if k % 150 == 0:
                el = time.time() - t_start
                print(f"  frame {k}/{len(times)}  t={times[k]:.2f}s  {k / max(el, 1e-6):.1f} f/s", file=sys.stderr)
    ff.stdin.close()
    ff.wait()
    el = time.time() - t_start
    rate = len(times) / el
    print(f"rendered {len(times)} frames in {el:.1f}s ({rate:.1f} f/s) -> {out_mp4_video_only}", file=sys.stderr)
    return rate


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--timeline", default=str(WORK / "timeline.json"))
    ap.add_argument("--capture", default=str(WORK / "capture"))
    ap.add_argument("--start", type=float)
    ap.add_argument("--end", type=float)
    ap.add_argument("--every", type=int, default=1)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default="/tmp/v2_video.mp4")
    ap.add_argument("--frames", help="comma-separated times (s): dump PNGs instead of a video")
    ap.add_argument("--png-dir", default="/tmp/v2_frames")
    a = ap.parse_args()
    if a.frames:
        r = Renderer(a.timeline, a.capture)
        d = pathlib.Path(a.png_dir)
        d.mkdir(parents=True, exist_ok=True)
        for s in a.frames.split(","):
            t = float(s)
            t0 = time.time()
            im = r.frame(t)
            p = d / f"f_{t:07.3f}.png"
            im.save(p)
            print(f"{p}  ({(time.time() - t0) * 1000:.0f} ms)")
        return
    render(a.timeline, a.capture, a.out, a.workers, a.start, a.end, a.every)


if __name__ == "__main__":
    main()
