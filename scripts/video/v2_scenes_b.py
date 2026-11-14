"""v2 scenes, part B: s02-s06 (the mandate, the reviewers, the wrong line, the weak tests, the pack).

See v2_capture.py for the Rec API and WORK/v2/SPEC.md for the track format and the storyboard. Every
position is measured from the live DOM at run time (the site is still changing), so the scenes stay
re-runnable; text phrases are located with a DOM Range so highlights hug the words as rendered.
"""
import asyncio

URLBAR = (420, -40)

# Client rects of `phrase` inside the n-th element matching `sel`, merged per line: [[x, y, w, h], ...].
_PHRASE_JS = """([sel, phrase, nth]) => {
  const root = document.querySelectorAll(sel)[nth || 0];
  if (!root) return null;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes = []; let text = '';
  while (walker.nextNode()) { nodes.push([walker.currentNode, text.length]); text += walker.currentNode.data; }
  const norm = s => s.replace(/[\\u00a0\\u2011]/g, c => c === '\\u00a0' ? ' ' : '-');
  const i = norm(text).toLowerCase().indexOf(norm(phrase).toLowerCase());
  if (i < 0) return null;
  const j = i + phrase.length, range = document.createRange();
  for (const [n, off] of nodes) if (off <= i && i < off + n.data.length) { range.setStart(n, i - off); break; }
  for (const [n, off] of nodes) if (off < j && j <= off + n.data.length) { range.setEnd(n, j - off); break; }
  const lines = [];
  for (const r of range.getClientRects()) {
    if (r.width < 1) continue;
    const l = lines.find(L => Math.abs(L.y - r.y) < r.height / 2);
    if (l) { const x2 = Math.max(l.x + l.w, r.x + r.width); l.x = Math.min(l.x, r.x); l.w = x2 - l.x; l.h = Math.max(l.h, r.height); }
    else lines.push({x: r.x, y: r.y, w: r.width, h: r.height});
  }
  return lines.map(l => [l.x, l.y, l.w, l.h]);
}"""


async def phrase_boxes(r, sel, phrase, nth=0):
    boxes = await r.page.evaluate(_PHRASE_JS, [sel, phrase, nth])
    assert boxes, f"phrase {phrase!r} not found in {sel}"
    return boxes


def union(boxes):
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes); y1 = max(b[1] + b[3] for b in boxes)
    return [x0, y0, x1 - x0, y1 - y0]


async def _rest(r, x, y):
    r.pos = (x, y)
    await r.page.mouse.move(x, y)


async def _prep_type(r, s):
    """Type shots: the page is loaded before the clock; the cursor is at the URL bar (the compositor types)."""
    await r.goto(s["url"])
    r.pos = URLBAR


# ---------------------------------------------------------------- s02 pitch.html#3: the signed mandate

async def _prep_s02(r, s):
    await r.goto(s["url"])
    await _rest(r, 1010, 520)
    await r.page.wait_for_timeout(200)


async def s02(r, s):
    h2 = ".slide.on h2"
    chip = ".slide.on .pipe span"
    hx, hy, hw, hh = await r.box(h2)
    nchips = await r.page.locator(chip).count()
    cx0, cy0, cw0, ch0 = union([await r.box(chip, i) for i in range(nchips)])
    mid_y = (hy + cy0 + ch0) / 2
    # b03: a slow push-in on the heading and its chips
    r.cam(0.0, 1.0, 640, 360)
    r.cam(0.6, 1.0, 640, 360)
    r.cam(6.6, 1.22, hx + hw * 0.47, mid_y)
    await r.at(0.5); await r.drift(-28, 16, dur=1.5)
    # "signed mandate": the cursor comes to rest just under the words, then the marker sweeps them
    sm = await phrase_boxes(r, h2, "signed mandate")
    sx, sy, sw, sh = sm[0]
    await r.at(r.cue("signed") - 0.75)
    await r.move(sx + sw * 0.55, sy + sh + 6, dur=0.6)
    await r.at(r.cue("signed") + 0.05)
    for b in sm:
        await r.highlight(b, until=7.3)
    await r.at(r.cue("decides") + 0.2); await r.drift(22, 6, dur=1.3)
    # b04 "Facts come first": the cursor goes to the facts chip; editor zoom on the chip row
    fx, fy, fw, fh = await r.box(chip, 0)
    t_f = r.cue("Facts", line=1)
    await r.at(t_f - 0.82)
    await r.move(fx + fw * 0.62, fy + fh * 0.7, dur=0.55)
    r.cam(t_f - 0.3, 1.22, hx + hw * 0.47, mid_y)
    r.cam(t_f + 0.32, 1.75, cx0 + cw0 * 0.5, cy0 - 8)
    r.cam(r.cue("fix", line=1) - 0.2, 1.8, cx0 + cw0 * 0.5 + 10, cy0 - 6, "lin")
    # "the build, the tests": small, slow motions inside the chip (a hand on the mouse)
    await r.at(r.cue("build", line=1) - 0.1); await r.drift(-14, -3, dur=0.6)
    await r.at(r.cue("tests", line=1) - 0.1); await r.drift(12, 2, dur=0.6)
    await r.at(r.cue("fails", line=1) - 0.2); await r.drift(4, 3, dur=0.8)
    # after "fix.": on along the pipe to "reviewers" (the next shot is the reviewers)
    rx, ry, rw, rh = await r.box(chip, 1)
    await r.at(min(r.cue("fix", line=1) + 0.4, s["dur"] - 0.75))
    await r.move(rx + rw * 0.6, ry + rh * 0.7, dur=0.6)
    r.cam(s["dur"], 1.8, cx0 + cw0 * 0.5 + 40, cy0 - 6, "lin")


s02.prep = _prep_s02


# ---------------------------------------------------------------- s03 tour.html#3: three reviewers

async def s03(r, s):
    rows = "section.tstep:not([hidden]) .vlist li"
    n = await r.page.locator(rows).count()
    assert n == 3, f"s03: {n} reviewer rows"
    boxes = [await r.box(rows, i) for i in range(3)]
    lx, ly, lw, lh = union(boxes)
    claude = boxes[0]
    r.cam(0.0, 1.0, 640, 360)
    r.cam(1.4, 1.0, 640, 360)
    r.cam(3.85, 1.16, lx + lw * 0.55, ly + lh * 0.35)
    await r.at(s.get("type_lead", 1.0)); r.place(*URLBAR)
    # "Then three AI reviewers": over the three rows, one by one (the mouse really hovers each)
    who = "section.tstep:not([hidden]) .vlist li .who"
    t3 = r.cue("three")
    await r.at(1.06)
    wx, wy, ww, wh = await r.box(who, 0)
    await r.move(wx + ww * 0.42, wy + wh + 3, dur=t3 - 0.08 - 1.06)
    for i, t in ((1, r.cue("AI") + 0.05), (2, r.cue("reviewers") + 0.12)):
        await r.at(t - 0.32)
        wx, wy, ww, wh = await r.box(who, i)
        await r.move(wx + ww * (0.42 + 0.05 * i), wy + wh + 3, dur=0.32)
    # "from three vendors": out to the vendor column, then up it
    vend = "section.tstep:not([hidden]) .vlist li .muted"
    await r.at(r.cue("vendors") - 0.45)
    vx, vy, vw, vh = await r.box(vend, 2)
    await r.move(vx + vw * 0.5, vy + vh + 6, dur=0.42)
    vx, vy, vw, vh = await r.box(vend, 0)
    await r.move(vx + vw * 0.5, vy + vh + 6, dur=0.6, overshoot=False)
    # "Every citation is re-checked": editor zoom on Claude, the row that blocks unanimity
    t_e = r.cue("Every")
    r.cam(t_e - 0.15, 1.16, lx + lw * 0.55, ly + lh * 0.35)
    r.cam(t_e + 0.5, 1.72, claude[0] + claude[2] * 0.5, claude[1] + claude[3] * 0.5 + 6)
    r.cam(s["dur"], 1.78, claude[0] + claude[2] * 0.5 + 6, claude[1] + claude[3] * 0.5 + 6, "lin")
    # "what can't be proven is refused": the cursor comes to "1 of 4 not met", which gets the marker
    nm = await phrase_boxes(r, rows, "1 of 4 not met", 0)
    nx, ny, nw, nh = nm[0]
    await r.at(r.cue("re-checked") + 0.2)
    await r.drift(-40, 4, dur=0.9)
    await r.at(r.cue("proven") - 0.55)
    await r.move(nx + nw + 10, ny + nh * 0.8, dur=0.5)
    await r.at(r.cue("refused") - 0.05)
    await r.highlight(nm[0], until=s["dur"])
    await r.at(r.cue("refused") + 0.4); await r.drift(6, 10, dur=0.7)


s03.prep = _prep_type


# ---------------------------------------------------------------- s04 index.html: Show me where

async def _prep_s04(r, s):
    await r.goto(s["url"], settle=200)
    # The first screen as it is after its entrance reveal (the site's own end state, class "seen").
    await r.page.evaluate("document.body.classList.add('seen')")
    await r.page.wait_for_timeout(500)
    await _rest(r, 940, 455)
    await r.page.wait_for_timeout(200)


async def s04(r, s):
    btn = "#home a[href='#where']"
    bx, by, bw, bh = await r.box(btn)
    r.cam(0.0, 1.0, 640, 360)
    r.cam(1.9, 1.15, bx + bw * 0.5 + 80, by - 90)
    t_click = r.cue("fix", end=True)
    r.cam(t_click + 0.15, 1.15, bx + bw * 0.5 + 80, by - 90)
    await r.at(0.15); await r.drift(-18, 10, dur=0.8)
    # "Back to our fix.": to the button (a real hover), click on the end of "fix."
    await r.at(r.cue("Back") - 0.1)
    await r.move(bx + bw * 0.58, by + bh * 0.62, dur=0.7)
    await r.at(t_click - 0.05)
    await r.click()  # real hash navigation to #where
    await r.page.wait_for_function("location.hash === '#where'")
    await r.page.wait_for_timeout(60)
    # "The line behind the reported bug ...": editor zoom on line 1383 and its pin
    pinned = "#where .r.pinned"
    pin = "#where .pin"
    px, py, pw, ph = await r.box(pinned)
    qx, qy, qw, qh = await r.box(pin)
    code = await phrase_boxes(r, pinned, "if (suppressSourceGeneration is true)")
    code_end = code[0][0] + code[0][2]
    zx = (px + 40 + code_end) / 2
    zy = (py + qy + qh) / 2
    t_l = r.cue("line")
    r.cam(t_l + 0.12, 1.72, zx, zy)
    r.cam(s["dur"], 1.8, zx + 8, zy + 2, "lin")
    await r.at(t_click + 0.4)
    await r.move(code_end + 34, py + ph * 0.55, dur=0.55)
    # "the fix never touches": down to the pin, whose words get the marker
    words = await phrase_boxes(r, pin, "Untouched by the fix")
    tx, ty, tw, th = words[0]
    await r.at(r.cue("one") - 0.35)
    await r.move(tx + tw + 18, ty + th * 0.75, dur=0.45)
    await r.at(r.cue("fix", nth=1) - 0.1)
    await r.highlight(words[0], until=s["dur"])
    await r.at(r.cue("touches") + 0.3); await r.drift(8, 6, dur=0.7)


s04.prep = _prep_s04


# ---------------------------------------------------------------- s05 tour.html#2: 4 of 8 prove nothing

async def s05(r, s):
    weak = "section.tstep:not([hidden]) .tiles li.weak"
    n = await r.page.locator(weak).count()
    assert n == 4, f"s05: {n} weak tiles"
    cards = [await r.box(weak, i) for i in range(4)]
    wx, wy, ww, wh = union(cards)
    r.cam(0.0, 1.0, 640, 360)
    r.cam(1.6, 1.0, 640, 360)
    await r.at(s.get("type_lead", 1.0)); r.place(*URLBAR)
    # to the first yellow card, a beat before "4"
    t4 = r.cue("4")
    c = cards[0]
    await r.at(1.12)
    await r.move(c[0] + c[2] * 0.84, c[1] + c[3] - 9, dur=t4 - 0.3 - 1.12)
    # "4 of its 8": across the four yellow cards (each one really hovered)
    t_new = r.cue("new")
    step = (t_new + 0.1 - t4) / 3
    for i in range(1, 4):
        await r.at(t4 + step * (i - 1) + 0.02)
        c = cards[i]
        await r.move(c[0] + c[2] * 0.84, c[1] + c[3] - 9, dur=step * 0.9, overshoot=False)
    # zoom toward the yellow row
    r.cam(t4 - 0.1, 1.0, 640, 360)
    r.cam(t4 + 0.75, 1.4, wx + ww / 2, wy + wh * 0.3)
    r.cam(s["dur"], 1.48, wx + ww / 2, wy + wh * 0.3 - 4, "lin")
    # "They prove nothing": the marker on the heading's "they prove nothing"; the cursor rests by the row
    pn = await phrase_boxes(r, "section.tstep:not([hidden]) h1", "they prove nothing")
    await r.at(r.cue("still") + 0.1)
    await r.drift(-30, -8, dur=0.9)
    await r.at(r.cue("They") + 0.05)
    for b in pn:
        await r.highlight(b, until=s["dur"])
    await r.at(r.cue("prove") + 0.2); await r.drift(-12, -3, dur=0.8)


s05.prep = _prep_type


# ---------------------------------------------------------------- s06 packs/2234/pack.html: C2 reproduced

_C2_JS = """() => {
  // Claude's C2 finding: a compact Evidence row (details.row) whose summary names it.
  const rows = [...document.querySelectorAll('#evidence details.row, #evidence details')];
  let el = rows.find(d => /Claude C2/.test(d.querySelector('summary')?.textContent || ''))
        || rows.find(d => /Key\\(null\\) still crashes/.test(d.querySelector('summary')?.textContent || ''));
  if (!el) return null;
  if (!el.id) el.id = 'cs-video-c2';
  return '#' + el.id;
}"""

# The detail line that says the pipeline reproduced the finding (inside the C2 row, one tap deeper).
_REPRO_JS = """(c2) => {
  const ps = [...document.querySelectorAll(c2 + ' > :not(summary) p, ' + c2 + ' > :not(summary) li')];
  const p = ps.find(e => /reproduced by the pipeline/i.test(e.textContent) && /failed on head/i.test(e.textContent))
         || ps.find(e => /reproduced by the pipeline/i.test(e.textContent));
  if (!p) return null;
  p.dataset.csVideo = 'repro';
  return c2 + ' [data-cs-video=repro]';
}"""


async def s06(r, s):
    summ = "details#evidence > summary"
    if not await r.page.locator(summ).count():
        summ = "details > summary:has-text('Evidence')"
    r.cam(0.0, 1.0, 640, 360)
    await r.at(s.get("type_lead", 1.0)); r.place(*URLBAR)
    # open the Evidence fold: a real click on its summary
    await r.at(1.04)
    lab = await phrase_boxes(r, summ, "Evidence")
    lx, ly, lw, lh = lab[0]
    await r.move(lx + lw * 0.62, ly + lh * 0.68, dur=0.5)
    await r.at(1.6)
    await r.click()
    await r.page.wait_for_function("(s) => document.querySelector(s).parentElement.open", arg=summ)
    c2 = await r.page.evaluate(_C2_JS)
    assert c2, "s06: Claude's C2 finding row not found"
    head = f"{c2} > summary"
    # scroll with inertia so the C2 row sits high (its detail opens below it, above the caption zone)
    await r.at(1.68)
    ax, ay, aw, ah = await r.box(head)
    target = 150
    dist = ay - target
    if dist > 2600:
        await r.scroll_by(dist * 0.66, dur=0.46)
        await r.drift(0, 6, dur=0.06)
        ax, ay, aw, ah = await r.box(head)
        await r.scroll_by(ay - target, dur=0.66)
    elif dist > 4:
        await r.scroll_by(dist, dur=0.95)
    await asyncio.sleep(0.04)
    ax, ay, aw, ah = await r.box(head)
    # "A reviewer found a crash": the cursor onto the finding's row (a real hover)
    cr = await phrase_boxes(r, head, "still crashes")
    kx, ky, kw, kh = cr[0]
    t_c = r.cue("crash")
    await r.at(max(r.now(), t_c - 0.55))
    await r.move(kx + kw * 0.5, ky + kh + 4, dur=0.45)
    r.cam(t_c - 0.2, 1.0, 640, 360)
    # "the fix leaves in": one tap deeper, a real click opens the row's detail
    await r.at(r.cue("crash", end=True) + 0.08)
    await r.click()
    await r.page.wait_for_function("(s) => document.querySelector(s).open", arg=c2)
    await r.page.wait_for_timeout(40)
    rep_sel = await r.page.evaluate(_REPRO_JS, c2)
    assert rep_sel, "s06: no 'reproduced by the pipeline' line in the C2 detail"
    rep = await phrase_boxes(r, rep_sel, "reproduced by the pipeline")
    px, py, pw, ph = rep[0]
    bx, by, bw, bh = await r.box(c2)
    r.cam(t_c + 0.5, 1.0, 640, 360)
    r.cam(r.cue("pipeline") - 0.4, 1.14, bx + bw * 0.5, by + bh * 0.5)
    # "and the pipeline reproduced it": editor zoom on the repro line; marker on "reproduced by the pipeline".
    # The zoom centre sits below the line so the text lands in the upper half, clear of the captions.
    t_p = r.cue("pipeline")
    r.cam(t_p + 0.22, 1.62, px + pw * 0.75, py + 30)
    r.cam(s["dur"], 1.68, px + pw * 0.75 + 6, py + 32, "lin")
    await r.at(t_p - 0.5)
    await r.move(px + pw * 0.5, py + ph + 6, dur=0.45)
    await r.at(r.cue("reproduced") + 0.02)
    await r.highlight(rep[0], until=s["dur"])
    await r.at(r.cue("it", nth=0) + 0.1); await r.drift(10, 8, dur=0.6)


s06.prep = _prep_type
