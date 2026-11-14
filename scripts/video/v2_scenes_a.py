"""v2 scenes, part A: the hook (s01). See v2_capture.py for the Rec API and WORK/v2/SPEC.md for the track."""


async def _prep_s01(r, s):
    await r.goto("index.html", settle=150)
    # Hold the page's own entrance animations at their start; each plays on the word it illustrates.
    await r.page.evaluate("""() => document.getAnimations().forEach(a => { a.pause(); a.currentTime = 0; })""")
    r.pos = (900, 560)
    await r.page.mouse.move(*r.pos)
    await r.page.wait_for_timeout(300)


async def _play(r, sel):
    """Play the CSS entrance animation of `sel` from the end of its delay (as the page does on load)."""
    await r.page.evaluate("""(sel) => document.querySelectorAll(sel).forEach(el => el.getAnimations().forEach(a => {
        const d = a.effect.getTiming().delay || 0; a.currentTime = d; a.play(); }))""", sel)


async def s01(r, s):
    r.cam(0.0, 1.0, 640, 360)
    r.cam(5.5, 1.16, 640, 230)
    await r.at(r.cue("builds") - 0.15); await _play(r, ".ticks li:nth-child(1)")
    await r.move_to(".ticks li", 0, fx=0.5, fy=0.6, dur=0.7)
    await r.at(r.cue("175") - 0.1); await _play(r, ".ticks li:nth-child(2)")
    await r.move_to(".ticks li", 1, fx=0.85, fy=0.6, dur=0.6)
    await r.at(r.cue("175") + 0.5); await r.highlight(".ticks li", nth=1, until=9.0)
    await r.at(r.cue("reviewer") - 0.2); await _play(r, ".ticks li:nth-child(3)")
    await r.move_to(".ticks li", 2, fx=0.6, fy=0.6, dur=0.6)
    await r.at(r.cue("met") + 0.3); await r.drift(-30, 70, dur=0.9)
    r.cam(r.cue("wrong", line=1) - 0.6, 1.16, 640, 230)
    r.cam(r.cue("wrong", line=1) + 0.1, 1.55, 640, 300)
    await r.at(r.cue("wrong", line=1) - 0.25); await _play(r, ".wrong, .caught")
    await r.at(r.cue("wrong", line=1) + 0.4); await r.move_to(".wrong", 0, fx=0.82, fy=0.75, dur=0.6)
    await r.at(r.cue("bug", line=1) + 0.5); await _play(r, ".decide"); await _play(r, ".acts")
    r.cam(s["dur"] - 0.2, 1.42, 640, 330, "lin")


s01.prep = _prep_s01
