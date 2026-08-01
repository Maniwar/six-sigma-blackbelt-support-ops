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
  CONTRAST every label clears WCAG AA against whatever it is drawn on — which
           for a value label sitting on a bar is that series' own colour, not
           the white the other checks all assume.
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
        out.append((x0, x1, y, txt, vb, bool(rot)))
    return out


def _lum(hexc: str) -> float:
    h = hexc.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    parts = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        parts.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * parts[0] + 0.7152 * parts[1] + 0.0722 * parts[2]


def contrast(a: str, b: str) -> float:
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


RE_RECT = re.compile(
    r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([\d.]+)" height="([\d.]+)"[^>]*?'
    r'fill="(#[0-9a-fA-F]{3,6})"')
RE_CLS_FILL = re.compile(r"\.(\w+)\{[^}]*?fill:(#[0-9a-fA-F]{3,6})")

# WCAG AA: 4.5:1 for body text, and 3:1 only for LARGE text, which means 24px
# regular or 18.66px bold. Nothing in these charts is large — the value labels
# are 10.5px bold and even the title is 14px — so the allowance is derived from
# the declared font rather than assumed. The first version of this check listed
# the title and value classes as large by hand, which handed both of them a 3:1
# pass they are nowhere near entitled to.
AA_BODY, AA_LARGE = 4.5, 3.0
RE_FONT_FULL = re.compile(r"font:\s*(?:(\d+)\s+)?([\d.]+)px")


def _needs(cls: str, svg_text: str) -> float:
    m = re.search(r"\." + re.escape(cls) + r"\{([^}]*)\}", svg_text)
    f = RE_FONT_FULL.search(m.group(1)) if m else None
    if not f:
        return AA_BODY
    weight = int(f.group(1) or 400)
    size = float(f.group(2))
    large = size >= 24 or (weight >= 700 and size >= 18.66)
    return AA_LARGE if large else AA_BODY


def audit_contrast(book: str, title: str, svg_text: str) -> None:
    """Every label has to be readable against whatever it is drawn on.

    Text on the white plot area was never the risk — the label grey is 5.8:1 and
    the title 17:1. The risk is a value label sitting ON a bar, where the
    background is whatever colour that series happens to be, and a dark label on
    a dark fill is unreadable while every structural check still passes: the
    text exists, it is inside the frame, and it does not overlap another label.
    """
    colours = dict(RE_CLS_FILL.findall(svg_text))
    rects = [(float(x), float(y), float(w), float(h), fill)
             for x, y, w, h, fill in RE_RECT.findall(svg_text)]
    root = ET.fromstring(svg_text)
    for el in root.iter("{http://www.w3.org/2000/svg}text"):
        txt = "".join(el.itertext()).strip()
        cls = el.get("class", "")
        if not txt or cls not in colours:
            continue
        m = re.search(r"translate\(([-\d.]+),\s*([-\d.]+)\)", el.get("transform", ""))
        x = float(m.group(1)) if m else float(el.get("x", 0))
        y = float(m.group(2)) if m else float(el.get("y", 0))
        # The deepest rect containing the text's anchor is what sits behind it.
        bg = "#ffffff"
        for rx, ry, rw, rh, fill in rects:
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                bg = fill
        got = contrast(colours[cls], bg)
        need = _needs(cls, svg_text)
        if got < need:
            check(False, f"[CONTRAST] {book} · {title}",
                  f"{txt[:32]!r} is {colours[cls]} on {bg} — {got:.1f}:1, below the "
                  f"{need}:1 this text size needs to stay readable")
            return
    passes[0] += 1


def audit_svg(book: str, title: str, svg_text: str) -> None:
    """The two things a person notices immediately and no structural check sees."""
    for x0, x1, y, txt, vb, _rot in text_boxes(svg_text):
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

    # Two labels written over each other. This was reported by a reader — the
    # axis title and the legend were laid out at the same height and printed
    # through one another — and until now it was only ever checked by eye.
    # Rotated runs are exempt: a -38° category axis packs its labels close on
    # purpose and their boxes overlap without the glyphs ever touching.
    # text_boxes carries the rotation flag itself. Re-deriving it by zipping
    # against a fresh element walk silently misaligned — that walk includes the
    # empty <text> nodes text_boxes drops, so every box after the first blank
    # was paired with the wrong element and the check could not fire at all.
    flat = [(x0, x1, y, txt) for x0, x1, y, txt, _vb, rot
            in text_boxes(svg_text) if not rot]
    for i, (ax0, ax1, ay, atxt) in enumerate(flat):
        for bx0, bx1, by, btxt in flat[i + 1:]:
            if abs(ay - by) > 7:                     # different lines entirely
                continue
            overlap = min(ax1, bx1) - max(ax0, bx0)
            if overlap > 6:
                check(False, f"[OVERLAP] {book} · {title}",
                      f"{atxt[:26]!r} and {btxt[:26]!r} share the same line and "
                      f"overlap by {overlap:.0f}px — they print through each other")
                return
    passes[0] += 1


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
            name = title.group(1) if title else "(untitled)"
            audit_svg(entry["file"], name, svg)
            audit_contrast(entry["file"], name, svg)
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
