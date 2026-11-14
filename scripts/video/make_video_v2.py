#!/usr/bin/env python3
"""Render v2 of the Junction demo video: the real site as a screen recording on a Mac, with a voice-over.

    python3 site/build.py
    uv run --with playwright --with pillow --with numpy python scripts/video/make_video_v2.py
    ... make_video_v2.py --skip-capture          # reuse WORK/v2/capture (e.g. after a compositor change)
    ... make_video_v2.py --capture s04 s06       # re-capture only these shots

Pipeline (each step is its own module in scripts/video/, all write under WORK/v2/):
  1. v2_voice.py     ElevenLabs voice "George", one clip per line, cached in WORK/audio by a hash of the
                     text and settings (same cache as v1; a re-render spends no characters). The key is read
                     from /data/work/secrets/elevenlabs.key in-process and never printed.
  2. v2_timeline.py  the storyboard: 12 shots, how each is entered (cold / whip-pan / URL typed), timed
                     from the clips' word timestamps -> WORK/v2/timeline.json.
  3. v2_capture.py   headless Chromium (1280x720 CSS at 2x -> 2560x1440 DevTools screencast) drives the real
     v2_scenes_*.py  site/ per shot: human-like mouse moves (real hovers), real clicks, wheel scrolling with
                     inertia, the pages' own animations; logs the cursor, clicks, camera keyframes and
                     highlight boxes -> WORK/v2/capture/<shot>/. The site's system fonts are rendered with
                     Inter / JetBrains Mono (fonts.conf aliases), as SF Pro / SF Mono would be on a Mac.
  4. v2_compositor.py desktop, browser window (tabs, URL bar), macOS cursor, camera push-ins, whip-pans
                     with motion blur, typed URLs and notes, highlighter, captions -> silent H.264.
  5. here            voice track at the timeline positions, loudness -16 LUFS, mux (H.264 + AAC, yuv420p,
                     faststart), a copy for the submission form, a 9-frame contact sheet.
Nothing on screen is generated except the window frame, cursor, captions, highlights and one typed note
whose times come from the GitHub API (demo PR #11).
"""
import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import wave

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import v2_timeline  # noqa: E402
import v2_voice  # noqa: E402

WORK = pathlib.Path(os.environ.get("VIDEO_WORK", "/data/work/video"))
V2 = WORK / "v2"
FONTS = V2 / "fonts"
FONT_URLS = {"Inter.ttf": "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
             "JetBrainsMono.ttf": "https://github.com/google/fonts/raw/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf"}
FONTS_CONF = """<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>
  <dir>{d}</dir>
  <cachedir>{d}/cache</cachedir>
""" + "".join(f'  <alias binding="same"><family>{a}</family><prefer><family>{b}</family></prefer></alias>\n' for a, b in [
    ("-apple-system", "Inter"), ("BlinkMacSystemFont", "Inter"), ("Segoe UI", "Inter"),
    ("ui-monospace", "JetBrains Mono"), ("SFMono-Regular", "JetBrains Mono"), ("SF Mono", "JetBrains Mono")]) + "</fontconfig>\n"
SR = 44100


def ensure_fonts():
    FONTS.mkdir(parents=True, exist_ok=True)
    for name, url in FONT_URLS.items():
        if not (FONTS / name).exists():
            subprocess.run(["curl", "-sSfL", "-o", str(FONTS / name), url], check=True)
    (FONTS / "fonts.conf").write_text(FONTS_CONF.format(d=FONTS))


def build_audio(tl, path):
    n = int(round(tl["total"] * SR))
    buf = bytearray(n * 2)
    import array
    acc = array.array("h", bytes(buf))
    for sh in tl["shots"]:
        for ln in sh["lines"]:
            with wave.open(ln["wav"]) as w:
                assert w.getframerate() == SR and w.getnchannels() == 1
                data = array.array("h", w.readframes(w.getnframes()))
            off = int(round((sh["t0"] + ln["start"]) * SR))
            for i, v in enumerate(data[: max(0, n - off)]):
                s = acc[off + i] + v
                acc[off + i] = max(-32768, min(32767, s))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(acc.tobytes())


def contact_sheet(video, tl, out):
    """9 frames: the middle of shots 1, 2, 4, 6, 8, 9, 10, 11, 12."""
    picks = [s["t0"] + s["dur"] * 0.62 for i, s in enumerate(tl["shots"]) if i in (0, 1, 3, 5, 7, 8, 9, 10, 11)]
    inputs, chains = [], []
    for k, t in enumerate(picks):
        inputs += ["-ss", f"{t:.2f}", "-i", str(video)]
        chains.append(f"[{k}:v]scale=640:360,setsar=1[v{k}]")
    grid = "".join(f"[v{k}]" for k in range(9))
    layout = "|".join(f"{(k % 3) * 640}_{(k // 3) * 360}" for k in range(9))
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex",
                    ";".join(chains) + f";{grid}xstack=inputs=9:layout={layout}", "-frames:v", "1", str(out)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-capture", action="store_true")
    ap.add_argument("--capture", nargs="*", help="re-capture only these shots (default: all)")
    ap.add_argument("--out", default=str(WORK / "countersign-demo-v2.mp4"))
    ap.add_argument("--form-copy", default="/data/work/form/countersign-demo-v2.mp4")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    V2.mkdir(parents=True, exist_ok=True)
    ensure_fonts()

    print("voice:")
    stats = {"chars": 0}
    lines = v2_voice.build(stats)
    (V2 / "voice").mkdir(exist_ok=True)
    (V2 / "voice" / "lines.json").write_text(json.dumps(lines, indent=1))
    tl = v2_timeline.build(lines)
    (V2 / "timeline.json").write_text(json.dumps(tl, indent=1))
    print(f"  {len(lines)} lines, timeline {tl['total']:.2f}s, ElevenLabs characters this run: {stats['chars']}")
    assert tl["total"] <= 118, "over the 2:00 cap with margin"

    if not args.skip_capture:
        shots = args.capture or [s["id"] for s in tl["shots"]]
        print("capture:", " ".join(shots))
        env = dict(os.environ, FONTCONFIG_FILE=str(FONTS / "fonts.conf"))
        subprocess.run([sys.executable, str(HERE / "v2_capture.py"), *shots], check=True, env=env, cwd=str(HERE))

    print("compose:")
    import v2_compositor
    silent = V2 / "video-silent.mp4"
    v2_compositor.render(V2 / "timeline.json", V2 / "capture", str(silent), workers=args.workers)

    voice = V2 / "voice.wav"
    build_audio(tl, voice)
    total = tl["total"]
    af = f"loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.05,afade=t=out:st={total - 0.6:.3f}:d=0.6,aresample=48000"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(voice), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-af", af, "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-t", f"{total:.3f}",
                    "-movflags", "+faststart", args.out], check=True)
    if args.form_copy:
        pathlib.Path(args.form_copy).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.out, args.form_copy)
    contact_sheet(args.out, tl, WORK / "v2-contact-sheet.png")
    size = pathlib.Path(args.out).stat().st_size
    print(f"wrote {args.out}: {total:.2f}s, {size / 1e6:.1f} MB; contact sheet {WORK / 'v2-contact-sheet.png'}")


if __name__ == "__main__":
    main()
