"""pack.html's Evidence fold: one compact row per clause, finding, check and reviewer; detail one tap deeper."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from countersign import pack_render

ROOT = Path(__file__).resolve().parent.parent


class _Visible(HTMLParser):
    """The text a reader sees in the opened Evidence fold: nested folds closed, cited excerpts hidden (shown on :target)."""
    VOID = {"br", "meta", "link", "img", "input", "hr", "path"}

    def __init__(self):
        super().__init__()
        self.stack, self.text = [], []  # (tag, attrs)

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append((tag, dict(attrs)))

    def handle_endtag(self, tag):
        if any(t == tag for t, _ in self.stack):
            while self.stack.pop()[0] != tag:
                pass

    def handle_data(self, data):
        ids = [a.get("id") for _, a in self.stack]
        if "evidence" not in ids:
            return
        inner = self.stack[ids.index("evidence") + 1:]
        if any(a.get("class") == "ev" or "more-all" in (a.get("class") or "") for _, a in inner):
            return
        if any(t == "details" and (i + 1 == len(inner) or inner[i + 1][0] != "summary") for i, (t, _) in enumerate(inner)):
            return  # inside a closed fold, outside its summary
        self.text.append(data)


def _first_level(html: str) -> str:
    v = _Visible()
    v.feed(html)
    return re.sub(r"\s+", " ", "".join(v.text)).strip()


def test_2234_evidence_is_short_and_keeps_what_decides():
    p = json.loads((ROOT / "packs/2234/pack.json").read_text(encoding="utf-8"))
    html = pack_render.to_html(p, [])
    seen = _first_level(html)
    assert 600 < len(seen) <= 1600, len(seen)
    # each disputed clause says who said what; the routing finding, the reproduced crash, failing checks and the signer
    assert "N1 Not met: Claude; met: Codex, Nemotron; Gemini sided with Claude" in seen
    assert "Claude C1 major" in seen and "reproduced" in seen
    assert "tests.mutation" in seen and "Toivo signs" in seen and "Open questions" in seen
    # detail one tap deeper: long texts cut, the source file linked
    assert f'href="{pack_render.BLOB}reviews/2234/claude.json">full text</a>' in html
    assert 'id="chain-REQ-2234-N1"' in html and 'id="f-claude-C1"' in html and 'id="supply-chain"' in html
    assert html.count('class="ev"') == len(p["evidence_index"])  # every cited excerpt is still there, shown on :target
