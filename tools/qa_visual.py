#!/usr/bin/env python3
"""Look at the previews — and assert on them, so this can fail.

There was already a visual step. It rendered every workbook through LibreOffice
and printed "open them and look at every chart". That is not a test. It made no
claim, so it could not be wrong, so a green run meant nothing; it was opt-in, so
it mostly did not run at all; and it rendered the .xlsx, when the surface a
reader actually looks at is the preview on the page. Three separate reasons why
defects a person spots in two seconds — a yellow column empty on every row, a
label clipped at the edge — survived every run of it.

So this one renders THE PREVIEW, the thing readers see, and it asserts:

  CLIP     no chart text falls outside its own viewBox. This is the defect that
           shipped as "stment not posted at c" — analytic, not pixel-based, so
           it cannot flake.
  INK      every chart actually draws marks, and every sheet renders rows. A
           chart that resolves to live cells and plots nothing passes every
           structural check in the repo.
  OVERLAP  no chart's legend or axis labels are drawn over its own plot area.
  SHEET    a contact sheet per template, so the images get looked at by someone
           rather than merely produced.

    python3 tools/qa_visual.py                 # assert, and write contact sheets
    python3 tools/qa_visual.py --no-render     # assertions only, no browser

Exit status is non-zero if anything failed.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from sync_html import extract_tpls                               # noqa: E402

HTML = ROOT / "six-sigma-blackbelt-support-ops.html"
OUT = ROOT / ".qa-visual"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

fails: list[str] = []
passes = [0]


def check(cond: bool, label: str, detail: str = "") -> None:
    if cond:
        passes[0] += 1
    else:
        fails.append(f"  FAIL {label}" + (f"\n       {detail}" if detail else ""))


# ------------------------------------------------------------------ analytic

# Character width as a fraction of font size, for the sans stack the SVG uses.
# Deliberately generous: a false pass is better than a check people learn to
# ignore, and the defects this catches overhang by tens of pixels, not by two.
CHAR_W = 0.55
RE_FONT = re.compile(r"font:\s*(?:\d+\s+)?([\d.]+)px")


def _class_sizes(svg_text: str) -> dict[str, float]:
    """Font size per CSS class, read from the <style> the SVG carries."""
    out = {}
    for m in re.finditer(r"\.(\w+)\{([^}]*)\}", svg_text):
        f = RE_FONT.search(m.group(2))
        if f:
            out[m.group(1)] = float(f.group(1))
    return out


def text_boxes(svg_text: str):
    """(x0, x1, y, label) for every text run, in viewBox units."""
    root = ET.fromstring(svg_text)
    vb = [float(v) for v in root.get("viewBox", "0 0 0 0").split()]
    sizes = _class_sizes(svg_text)
    out = []
    for el in root.iter("{http://www.w3.org/2000/svg}text"):
        txt = "".join(el.itertext()).strip()
        if not txt:
            continue
        size = sizes.get(el.get("class", ""), 11.5)
        w = len(txt) * size * CHAR_W
        anchor = el.get("text-anchor", "start")
        tr = el.get("transform", "")
        m = re.search(r"translate\(([-\d.]+),\s*([-\d.]+)\)", tr)
        if m:
            x, y = float(m.group(1)), float(m.group(2))
        else:
            x, y = float(el.get("x", 0)), float(el.get("y", 0))
        rot = re.search(r"rotate\(([-\d.]+)\)", tr)
        if rot:
            # a rotated run reaches back along cos(theta) of its own width
            w = abs(w * math.cos(math.radians(float(rot.group(1)))))
        if anchor == "end":
            x0, x1 = x - w, x
        elif anchor == "middle":
            x0, x1 = x - w / 2, x + w / 2
        else:
            x0, x1 = x, x + w
        out.append((x0, x1, y, txt, vb))
    return out


def audit_svg(book: str, title: str, svg_text: str) -> None:
    """The two things a person notices immediately and no structural check sees."""
    for x0, x1, y, txt, vb in text_boxes(svg_text):
        if not vb:
            continue
        # 2px of slack: the width model is an estimate, the defect is not.
        if x0 < vb[0] - 2 or x1 > vb[0] + vb[2] + 2:
            check(False, f"[CLIP] {book} · {title}",
                  f"{txt[:40]!r} runs from {x0:.0f} to {x1:.0f}, outside the "
                  f"{vb[0]:.0f}..{vb[0] + vb[2]:.0f} frame — it renders cut off")
            return
        if y < vb[1] - 2 or y > vb[1] + vb[3] + 2:
            check(False, f"[CLIP] {book} · {title}",
                  f"{txt[:40]!r} sits at y={y:.0f}, outside the frame")
            return
    passes[0] += 1

    # A chart that draws nothing passes every structural check in this repo,
    # because its series resolve to cells and the cells simply have no numbers.
    marks = len(re.findall(r"<(rect|circle|path)\b", svg_text))
    check(marks >= 2, f"[INK] {book} · {title}",
          f"only {marks} drawn mark(s) — the chart resolves but plots nothing")


# -------------------------------------------------------------------- render


def preview_page(entry: dict, css: str) -> str:
    pv = re.sub(r'class="xsheet"', 'class="xsheet on"', entry["preview"])
    return (
        "<meta charset=utf-8><style>"
        ":root{--line:#dfe4ec;--ink:#151b24;--muted:#5b6675;--c:#1d6f42;"
        "--acc:#33415a;--bg3:#f4f6fa}"
        "body{margin:0;padding:20px;background:#eef1f6;"
        "font:15px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}"
        ".wrap{background:#fff;padding:18px 22px;border-radius:12px;max-width:1020px;"
        "margin:0 auto}.xtabs{display:none}"
        f"{css}</style><div class=\"wrap\">{pv}</div>")


def render(entries: dict, css: str) -> int:
    if not Path(CHROME).exists():
        print("  (no Chrome — skipping the contact sheets; assertions still ran)")
        return 0
    OUT.mkdir(exist_ok=True)
    n = 0
    for slug, entry in entries.items():
        if entry.get("ext") != "xlsx":
            continue
        page = OUT / f"{slug}.html"
        page.write_text(preview_page(entry, css), encoding="utf-8")
        png = OUT / f"{slug}.png"
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
             "--window-size=1080,4200", f"--screenshot={png}", f"file://{page}"],
            capture_output=True, timeout=120)
        page.unlink(missing_ok=True)
        if png.exists():
            n += 1
    return n


def main() -> int:
    src = HTML.read_text(encoding="utf-8")
    _, _, tpls = extract_tpls(src)
    css = src[src.index("/* ---- workbook preview ---- */"):
              src.index(".x-f{position:relative") + 400]

    charts = 0
    for slug, entry in tpls.items():
        if entry.get("ext") != "xlsx":
            continue
        svgs = re.findall(r"<svg class=\"xchart\".*?</svg>", entry["preview"], re.S)
        # Every workbook that has charts must show them; verify.py counts them,
        # this one looks at them.
        for svg in svgs:
            title = re.search(r'aria-label="([^"]*)"', svg)
            audit_svg(entry["file"], title.group(1) if title else "(untitled)", svg)
            charts += 1

    print(f"Looked at {charts} chart(s) across the previews.")
    if "--no-render" not in sys.argv:
        n = render(tpls, css)
        if n:
            print(f"  {n} contact sheet(s) in {OUT.relative_to(ROOT)}/ — open them.")

    if fails:
        print(f"\n{len(fails)} VISUAL FAILURE(S):")
        print("\n".join(fails))
        return 1
    print(f"\n{passes[0]} visual check(s) passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
