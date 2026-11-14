"""The v2 storyboard: shots, how each one is entered, and its timing from the voice clips.

Shot clock: every shot runs from t=0 to its `dur`. Voice lines sit at `line.start` (shot time); word
times in `words` are shot time too. Entries:
  cold  - the video opens on this shot (page already loaded)
  whip  - a whip-pan from the previous shot, centred on the shot boundary
  type  - same window: the cursor goes to the URL bar, the URL is typed, Enter, the page loads.
          The capture's frames before TYPE_LEAD are not shown (the compositor shows the previous
          page while typing); at TYPE_LEAD the cursor is at the URL bar (CSS x=URLBAR_X, y=-40).
"""
import json, pathlib

LEAD = {"cold": 0.7, "whip": 0.55, "type": 1.25}
TYPE_LEAD = 1.0          # page of a `type` shot is shown from this shot time on
URLBAR_X = 420           # CSS x of the cursor's click in the URL bar (the bar is above the viewport, y<0)
GAP = 0.35               # pause between two lines in one shot
TAIL = 0.45
SHOTS = [
    # id,   entry,  url (relative to site/ unless it starts with '/'), display URL, extra lead, extra tail
    ("s01", "cold", "index.html",            "zawaer.github.io/countersign/",                     0.0, 0.35),
    ("s02", "whip", "pitch.html#3",          "zawaer.github.io/countersign/pitch.html#3",        0.0, 0.0),
    ("s03", "type", "tour.html#3",           "zawaer.github.io/countersign/tour.html#3",         0.0, 0.0),
    ("s04", "whip", "index.html",            "zawaer.github.io/countersign/",                     0.5, 0.2),
    ("s05", "type", "tour.html#2",           "zawaer.github.io/countersign/tour.html#2",         0.0, 0.0),
    ("s06", "type", "packs/2234/pack.html",  "zawaer.github.io/countersign/packs/2234/pack.html", 0.9, 0.3),
    ("s07", "type", "tour.html#5",           "zawaer.github.io/countersign/tour.html#5",         0.0, 0.2),
    ("s08", "whip", "prs.html",              "zawaer.github.io/countersign/prs.html",            0.2, 0.2),
    ("s09", "type", "pitch.html#5",          "zawaer.github.io/countersign/pitch.html#5",        0.0, 0.6),
    ("s10", "type", "tour.html#6",           "zawaer.github.io/countersign/tour.html#6",         0.0, 0.5),
    ("s11", "whip", "overview.html",         "zawaer.github.io/countersign/overview.html",       0.0, 0.3),
    ("s12", "whip", "pitch.html#1",          "zawaer.github.io/countersign/pitch.html#1",        0.0, 3.2),
]


def build(lines):
    shots, t = [], 0.0
    for sid, entry, url, shown, xlead, xtail in SHOTS:
        mine = [l for l in lines if l["shot"] == sid]
        cur = LEAD[entry] + xlead
        ls = []
        for i, l in enumerate(mine):
            if i:
                cur += GAP
            ls.append({"id": l["id"], "text": l["text"], "start": round(cur, 3), "clip": l["clip"], "speech": l["speech"], "wav": l["wav"],
                       "words": [[w, round(cur + a, 3), round(cur + b, 3)] for w, a, b in l["words"]]})
            if "chunks" in l:
                ls[-1]["chunks"] = l["chunks"]
            cur += l["speech"]
        dur = round(cur + TAIL + xtail, 3)
        shots.append({"id": sid, "entry": entry, "url": url, "display_url": shown, "t0": round(t, 3), "dur": dur,
                      "lines": ls})
        t += dur
    return {"fps": 30, "size": [1920, 1080], "viewport_css": [1280, 720], "dpr": 2, "type_lead": TYPE_LEAD,
            "urlbar_x": URLBAR_X, "total": round(t, 3), "shots": shots}


if __name__ == "__main__":
    W = pathlib.Path("/data/work/video/v2")
    tl = build(json.loads((W / "voice" / "lines.json").read_text()))
    (W / "timeline.json").write_text(json.dumps(tl, indent=1))
    print(f"total {tl['total']:.2f}s")
    for s in tl["shots"]:
        print(s["id"], s["entry"], f"t0={s['t0']:.2f} dur={s['dur']:.2f}", s["url"], [(l["id"], l["start"]) for l in s["lines"]])
