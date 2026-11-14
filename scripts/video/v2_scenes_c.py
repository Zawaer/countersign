"""v2 scenes, part C: s07..s12 (owner card, GitHub PR, docs fix, ledger, numbers, close).

See v2_capture.py for the Rec API and WORK/v2/SPEC.md for the storyboard. Selectors lean on structure and
visible text (not on icon glyphs), so the icon swap to Material Symbols does not break them.
"""
import asyncio

URLBAR = (420, -40)

# Bounding box of the first on-screen line of visible text `text` inside `sel` (CSS px).
_TEXT_BOX_JS = """([sel, text]) => {
  const roots = document.querySelectorAll(sel);
  for (const root of roots) {
    const full = root.textContent;
    const at = full.indexOf(text);
    if (at < 0) continue;
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let pos = 0, n, sN = null, sO = 0, eN = null, eO = 0;
    while ((n = w.nextNode())) {
      const L = n.data.length;
      if (!sN && at < pos + L) { sN = n; sO = at - pos; }
      if (sN && at + text.length <= pos + L) { eN = n; eO = at + text.length - pos; break; }
      pos += L;
    }
    if (!sN || !eN) continue;
    const rg = document.createRange(); rg.setStart(sN, sO); rg.setEnd(eN, eO);
    const rs = [...rg.getClientRects()].filter(r => r.width > 0.5);
    if (!rs.length) continue;
    // union of the rects on the first line
    const top = rs[0].top, line = rs.filter(r => Math.abs(r.top - top) < 4);
    const x0 = Math.min(...line.map(r => r.left)), x1 = Math.max(...line.map(r => r.right));
    const y0 = Math.min(...line.map(r => r.top)), y1 = Math.max(...line.map(r => r.bottom));
    return [x0, y0, x1 - x0, y1 - y0];
  }
  return null;
}"""


async def tbox(r, sel, text):
    b = await r.page.evaluate(_TEXT_BOX_JS, [sel, text])
    assert b, f"text {text!r} not found in {sel}"
    return b


async def cbox(r, sel):
    """Box of the rendered text of `sel` (all lines), not of its block."""
    b = await r.page.evaluate("""(sel) => {
        const w = document.createTreeWalker(document.querySelector(sel), NodeFilter.SHOW_TEXT);
        const rs = []; let n;
        while ((n = w.nextNode())) { if (!n.data.trim()) continue;
            const rg = document.createRange(); rg.selectNodeContents(n);
            rs.push(...[...rg.getClientRects()].filter(r => r.width > 0.5)); }
        const x0 = Math.min(...rs.map(r => r.left)), y0 = Math.min(...rs.map(r => r.top));
        return [x0, y0, Math.max(...rs.map(r => r.right)) - x0, Math.max(...rs.map(r => r.bottom)) - y0]; }""", sel)
    return b


def mid(b, fx=0.5, fy=0.5):
    return b[0] + b[2] * fx, b[1] + b[3] * fy


async def enter_from_urlbar(r, x, y, dur=0.75):
    """Type shots: the compositor animates the URL bar until type_lead; the cursor then comes into the page."""
    await r.at(1.0)
    r.place(*URLBAR)
    await r.at(1.03)
    await r.move(x, y, dur=dur)


async def _prep_type(r, s):
    """Type shots: the page is loaded before t=0 and the logged cursor sits at the URL bar until type_lead."""
    await r.goto(s["url"])
    r.pos = URLBAR


async def _settle_mouse(r, x, y):
    r.pos = (x, y)
    await r.page.mouse.move(x, y)


# ---------------------------------------------------------------- s07 tour.html#5: ASK -> Toivo
async def s07(r, s):
    card = await r.box(".mini-card")
    pill = await r.box(".mini-card .pill")
    ccx, ccy = mid(card)
    r.cam(0.0, 1.0, 640, 360)
    r.cam(1.0, 1.0, 640, 360)
    r.cam(3.0, 1.14, ccx + 60, ccy - 20)
    # editor zoom onto the card as the voice reaches "asks"
    r.cam(r.cue("asks") - 0.35, 1.14, ccx + 60, ccy - 20)
    r.cam(r.cue("asks") + 0.3, 1.6, ccx, ccy - 10)
    r.cam(s["dur"], 1.66, ccx, ccy - 18, "lin")

    # into the page: rest on the empty right side of the card (hover lights its border)
    await enter_from_urlbar(r, card[0] + card[2] * 0.86, card[1] + card[3] * 0.62, dur=0.8)
    await r.at(2.0)
    await r.drift(-14, 10, dur=0.9)
    # "It asks the named owner": cursor onto the pill a beat before "asks"
    await r.at(r.cue("asks") - 0.75)
    await r.move(*mid(pill, 0.74, 0.78), dur=0.5)
    # "Toivo": a small nudge along the pill toward the name
    await r.at(r.cue("toivo") - 0.35)
    await r.move(*mid(pill, 0.9, 0.95), dur=0.35, overshoot=False)
    await r.at(r.cue("toivo") + 0.6)
    await r.move(pill[0] + pill[2] + 34, pill[1] + pill[3] * 0.7, dur=1.0, overshoot=False)


s07.prep = _prep_type


# ---------------------------------------------------------------- s08 prs.html: PR #2 on GitHub
async def _prep_s08(r, s):
    await r.goto(s["url"])
    # keep the folds closed (Toivo's note lives in "How this was checked")
    await r.page.evaluate("document.querySelectorAll('.pr-main details[open]').forEach(d => d.open = false)")
    await _settle_mouse(r, 905, 610)
    await r.page.wait_for_timeout(200)


async def s08(r, s):
    toivo = await tbox(r, ".pr-main .ghc-b h3", "by Toivo")
    h3 = await cbox(r, ".pr-main .ghc-b h3")  # "Countersign · changes requested by Toivo (ledger #3)"
    hx, hy = mid(h3)
    r.cam(0.0, 1.0, 640, 360)
    r.cam(0.6, 1.0, 640, 360)
    r.cam(1.3, 1.55, hx + 40, hy + 30)

    # "On GitHub, Toivo signed a request for changes": to the sticky comment heading
    await r.at(0.75)
    await r.move(toivo[0] + toivo[2] * 0.85, toivo[1] + toivo[3] * 1.12, dur=0.7)
    await r.at(r.cue("signed") - 0.1)
    await r.highlight(h3, until=round(r.cue("changes") + 0.35, 3))
    await r.at(r.cue("toivo") + 0.6)
    await r.drift(-12, 6, dur=0.5)

    # "The required check fails": scroll a little (inertia), then the status row
    sc0 = r.cue("changes") + 0.35
    await r.at(sc0)
    rows0 = await r.box(".pr-main .ghs-row")
    want = rows0[1] - 300  # bring the checks to ~300..400 CSS px
    await r.scroll_by(want, dur=0.85)
    row = await r.box(".pr-main .ghs-row")
    fail = await tbox(r, ".pr-main .ghs-row", "countersign/tier")
    merge = await tbox(r, ".pr-main .ghs-row.merge", "Merging is blocked")
    r.cam(sc0 + 0.05, 1.6, hx + 40, hy + 26, "lin")
    r.cam(sc0 + 0.75, 1.62, fail[0] + 230, (row[1] + merge[1]) / 2 + 12)
    r.cam(s["dur"], 1.68, fail[0] + 230, (row[1] + merge[1]) / 2 + 18, "lin")
    # cursor to "countersign/tier FAILING" (rests just past the word FAILING)
    await r.move(fail[0] + fail[2] + 70, fail[1] + fail[3] * 0.95, dur=0.5)
    # "the merge is blocked"
    await r.at(r.cue("merge") - 0.55)
    await r.move(merge[0] + merge[2] + 16, merge[1] + merge[3] * 0.8, dur=0.45)
    await r.at(r.cue("blocked"))
    await r.highlight(merge, until=s["dur"])
    await r.at(r.cue("blocked") + 0.4)
    await r.drift(26, -5, dur=0.7)


s08.prep = _prep_s08


# ---------------------------------------------------------------- s09 pitch.html#5: docs fix cleared
NOTE_S09 = "PR #11 · docs fix · opened 14:04:15 · merged 14:04:55 (40 s)"


async def s09(r, s):
    chip = await r.box('.slide.on .chg:has-text("demo-docs1")')
    badge = await r.box('.slide.on .chg:has-text("demo-docs1") .badge')
    cx, cy = mid(chip)
    r.cam(0.0, 1.0, 640, 360)
    r.cam(1.0, 1.0, 640, 360)
    r.cam(r.cue("docs") - 0.3, 1.1, 600, 360)
    # keep the slide's heading ("Every change says why. Low risk can clear.") in frame with the chip
    hx = 625
    r.cam(r.cue("docs") + 0.35, 1.45, hx, cy - 10)
    r.cam(r.cue("merged") - 0.35, 1.47, hx + 4, cy - 8, "lin")
    # make room for the typed note under the chip
    r.cam(r.cue("merged") + 0.25, 1.45, hx + 12, cy + 14)
    r.cam(s["dur"], 1.48, hx + 12, cy + 16, "lin")

    await enter_from_urlbar(r, 760, 520, dur=0.65)
    # "A low-risk docs fix": onto the chip a beat before "docs"
    await r.at(r.cue("docs") - 0.55)
    await r.move(*mid(chip, 0.36, 0.86), dur=0.45)
    # "the AI cleared it alone": onto the NOTIFY badge
    await r.at(r.cue("cleared") - 0.45)
    await r.move(*mid(badge, 0.62, 0.9), dur=0.4, overshoot=False)
    # "merged in 40 seconds": the note types in under the chip; the cursor eases off to the right
    await r.at(r.cue("merged") - 0.2)
    # the note sits under the second row of chips (anchor = its left edge, vertical centre)
    row2 = await r.box('.slide.on .chg:has-text("up-2022")')
    r.note(round(r.cue("merged"), 3), s["dur"], NOTE_S09, [round(chip[0] - 60, 1), round(row2[1] + row2[3] + 30, 1)])
    await r.move(chip[0] + chip[2] + 40, chip[1] - 10, dur=0.6, overshoot=False)
    await r.at(r.cue("seconds") + 0.3)
    await r.drift(8, -6, dur=1.0)


s09.prep = _prep_type


# ---------------------------------------------------------------- s10 tour.html#6: tamper the ledger
async def _prep_s10(r, s):
    await _prep_type(r, s)
    await r.page.wait_for_function(
        "() => { const b = document.getElementById('lstatus'); return b && /Ledger OK/.test(b.textContent)"
        " && document.querySelectorAll('.lline .st').length > 0 }", timeout=20000)
    await r.page.wait_for_timeout(300)


async def s10(r, s):
    l1 = await r.box(".lline", 0)
    l4 = await r.box(".lline", 3)
    tam = await r.box('#tamper, button:has-text("Tamper")')
    banner = await r.box("#lstatus")
    r.cam(0.0, 1.0, 640, 360)
    r.cam(1.0, 1.0, 640, 360)
    r.cam(4.6, 1.16, 560, 380)
    r.cam(r.cue("check") - 0.4, 1.16, 560, 380, "lin")

    # "Every sign-off goes into a signed, hash-chained ledger": down the ledger lines
    ly = lambda b: b[1] + b[3] * 0.62
    await enter_from_urlbar(r, 730, ly(l1) + 6, dur=0.7)
    await r.at(r.cue("signed") - 0.5)
    await r.move(712, ly(await r.box(".lline", 2)) + 4, dur=0.9, overshoot=False)
    await r.at(r.cue("ledger") - 0.4)
    await r.move(724, ly(l4) + 8, dur=0.8, overshoot=False)
    # "Edit one line": onto "1. Tamper", click on the end of "line"
    await r.at(r.cue("edit") - 0.35)
    await r.move(*mid(tam, 0.62, 0.62), dur=0.6)
    await r.at(r.cue("line", end=True) - 0.04)
    await r.click()
    await r.page.wait_for_function("() => /LEDGER INVALID/.test(document.getElementById('lstatus').textContent)",
                                   timeout=5000)
    # "and the check fails": editor zoom onto the red banner, sized to its text
    banner = await r.box("#lstatus")
    txt = await tbox(r, "#lstatus", "LEDGER INVALID")
    rects = await r.page.evaluate("""() => { const b = document.getElementById('lstatus');
        const rg = document.createRange(); rg.selectNodeContents(b);
        const rs = [...rg.getClientRects()].filter(r => r.width > 0.5);
        return [Math.min(...rs.map(r => r.left)), Math.max(...rs.map(r => r.right))]; }""")
    tw = rects[1] - rects[0]
    zoom = round(max(1.4, min(1.65, 1600 / (tw + 80))), 3)  # 1600/zoom CSS px are in frame
    bx = (rects[0] + rects[1]) / 2
    by = banner[1] + banner[3] / 2
    t1 = r.cue("check") - 0.4
    r.cam(t1 + 0.6, zoom, bx, by + 20)
    r.cam(s["dur"], zoom + 0.05, bx, by + 18, "lin")
    await r.highlight(txt, t=round(r.cue("fails") + 0.05, 3), until=s["dur"])
    # cursor eases off the button, below the banner, out of the text
    await r.at(r.cue("fails") - 0.3)
    await r.move(tam[0] + tam[2] + 330, tam[1] + tam[3] * 0.55, dur=0.7, overshoot=False)


s10.prep = _prep_s10


# ---------------------------------------------------------------- s11 overview.html: three numbers
async def _prep_s11(r, s):
    await r.goto(s["url"])
    await _settle_mouse(r, 820, 560)


async def s11(r, s):
    bigs = []
    for i in range(3):
        bigs.append(await r.box(".bignums .big", i))
    nums = [await r.box(".bignums .big b", i) for i in range(3)]
    txt = [await r.page.locator(".bignums .big b").nth(i).inner_text() for i in range(3)]
    shown = [t.replace("\n", "").replace(" ", "") for t in txt]
    if shown != ["11/11", "14/18", "35/35"]:
        print(f"s11 WARNING: numbers on screen are {shown}, voice says 11/11, 14/18, 35/35")
    Z = 1.8

    def focus(i):
        b = nums[i]
        return b[0] + b[2] / 2, b[1] + b[3] / 2 + 34

    f = [focus(i) for i in range(3)]
    r.cam(0.0, 1.0, 640, 360)
    r.cam(0.5, 1.0, 640, 360)
    r.cam(1.15, Z, *f[0])
    r.cam(5.75, Z + 0.07, f[0][0] + 6, f[0][1] - 4, "lin")
    r.cam(6.4, Z, *f[1])
    r.cam(9.95, Z + 0.06, f[1][0] + 6, f[1][1] - 4, "lin")
    r.cam(10.55, Z, *f[2])
    r.cam(13.7, Z + 0.06, f[2][0] - 4, f[2][1] - 4, "lin")
    r.cam(15.0, 1.1, 640, 350)
    r.cam(s["dur"], 1.1, 640, 350)

    def near(i):
        # inside the tile (so its hover shows), right of the number, below its baseline: not on the text
        b, n = bigs[i], nums[i]
        return min(b[0] + b[2] - 22, n[0] + n[2] + 26), n[1] + n[3] * 0.98

    await r.at(0.45)
    await r.move(*near(0), dur=0.6)
    await r.at(3.0)
    await r.drift(-10, 12, dur=1.4)
    await r.at(r.cue("tests") - 0.4)
    await r.move(*near(1), dur=0.65)
    await r.at(8.9)
    await r.drift(-8, 10, dur=1.2)
    await r.at(r.cue("and", nth=1) - 0.25)
    await r.move(*near(2), dur=0.6)
    await r.at(12.2)
    await r.drift(-10, 8, dur=1.2)
    # ease out with the camera: the hand leaves the tile
    await r.at(14.2)
    await r.move(1170, 560, dur=0.9, overshoot=False)


s11.prep = _prep_s11


# ---------------------------------------------------------------- s12 pitch.html#1: the close
async def _prep_s12(r, s):
    await r.goto(s["url"])
    await _settle_mouse(r, 950, 505)


async def s12(r, s):
    c = await cbox(r, ".slide.on .sl")
    content = [c[0], c[1], c[0] + c[2], c[1] + c[3]]
    repo = await tbox(r, ".slide.on", "github.com/Zawaer/countersign")
    cx = (content[0] + content[2]) / 2 + 30
    cy = (content[1] + content[3]) / 2 + 8
    r.cam(0.0, 1.0, 640, 360)
    r.cam(7.4, 1.25, cx, cy, "io")
    r.cam(s["dur"], 1.3, cx, cy + 4, "lin")

    await r.at(1.6)
    await r.drift(-18, 10, dur=1.6)
    await r.at(5.2)
    await r.drift(12, 16, dur=1.5)
    rest = r.cue("rest", end=True)
    await r.at(rest + 0.1)
    await r.highlight(repo, until=s["dur"])
    await r.at(rest + 1.0)
    await r.drift(-10, 6, dur=1.6)


s12.prep = _prep_s12
