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


# ------------------------------------------------------- the Word export
# verify.py exercises the business case's HTML and its workbook, and stops at
# the docx marker because the Word writer needs a DOM and node has not got one.
# So nothing ever ran it, and the charts had been missing from every Word copy
# of the business case: emBar draws a bar as an empty coloured div, an empty
# element carries no text, and the writer only ever collected text. Finance got
# four charts' worth of labels and numbers with a blank column down the middle.
# The only honest way to test it is the browser the readers use.
WORD_JS = """
var base={vol:480000,cpc:6.8,rate:14.0,hr:38,occ:82,aht:420,ahtsave:14,agents:120,
  shrink:32,shrinktgt:28,target:8.0,harvest:'reduce',realz:80,years:3,disc:10,
  bbmonths:9,bbcost:120000,training:35000,eng:60000,tooling:8000};
var gross=195840, real=gross*0.8, inv=223000, npv=196620;
var m={gross:gross,real:real,inv:inv,npv:npv,pb:inv/real,roi:1,fte:1,realz:0.8,
       detail:[['Improvement','a to b','6.0 pts']]};
var ctx={m:m,V:base,S:{arch:'rate'},
  a:{n:'Reduce rework and reopens',d:'d',metric:'Reopen rate',kind:'rate'}};
var X=window.__X, html=X.bizHTML(ctx), bytes=X.DOCX.build('Business case', html);
function emit(id, text){
  var d=document.createElement('div'); d.id=id; d.textContent=text;
  document.body.appendChild(d);
}
emit('__out', btoa(Array.from(bytes,function(b){return String.fromCharCode(b);}).join('')));

/* And what the reader actually sees. A bar's length is only meaningful next to
   the other bars, so measure them where they are laid out rather than trusting
   the percentages: the ones that cross zero are nested inside a half-width
   cell, and reading a percentage off that markup is what hid the bug. */
var host=document.createElement('div');
host.style.cssText='position:absolute;left:-9999px;top:0;width:900px';
host.innerHTML=html; document.body.appendChild(host);
var geo=[];
[].slice.call(host.querySelectorAll('table[data-chart]')).forEach(function(t){
  var rows=[].slice.call(t.rows).map(function(tr){
    var cell=tr.cells[1], bar=cell.querySelector('div[style*="background"]');
    var b=bar?bar.getBoundingClientRect():null, c=cell.getBoundingClientRect();
    return {label:(tr.cells[0].textContent||'').trim(),
            value:(tr.cells[2].textContent||'').trim(),
            x: b?b.left-c.left:0, w: b?b.width:0, cw:c.width};
  });
  geo.push(rows);
});
host.remove();
emit('__geo', JSON.stringify(geo));
"""
# Handed out where they are defined: the export code lives inside the page's
# own IIFE, so there is nothing to reach from the outside.
WORD_ANCHOR = "return {build:build};\n})();"


def word_document() -> tuple[str, list] | None:
    """document.xml and the on-screen bar geometry, from the page's real code."""
    import base64
    import tempfile
    import zipfile

    if not Path(CHROME).exists():
        return None
    src = HTML.read_text(encoding="utf-8")
    if src.count(WORD_ANCHOR) != 1:
        check(False, "[WORD] the docx module is where the harness expects it",
              "the anchor moved, so the Word export is going untested")
        return None
    src = src.replace(WORD_ANCHOR, WORD_ANCHOR + "\nwindow.__X={DOCX:DOCX,bizHTML:bizHTML};")
    # The first </body> in the file is inside a JS string, not the document's.
    head, sep, tail = src.rpartition("</body>")
    src = head + "<script>window.addEventListener('load',function(){" + WORD_JS + "});</script>" + sep + tail
    with tempfile.TemporaryDirectory() as td:
        page = Path(td) / "page.html"
        page.write_text(src, encoding="utf-8")
        r = subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--virtual-time-budget=9000",
             "--dump-dom", f"file://{page}"], capture_output=True, text=True, timeout=180)
    m = re.search(r'<div id="__out">([A-Za-z0-9+/=]*)</div>', r.stdout)
    g = re.search(r'<div id="__geo">(.*?)</div>', r.stdout, re.S)
    if not m or not m.group(1) or not g:
        check(False, "[WORD] the business case exports as a Word document",
              "the page produced no bytes")
        return None
    geo = json.loads(g.group(1).replace("&quot;", '"').replace("&amp;", "&"))
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "c.docx"
        f.write_bytes(base64.b64decode(m.group(1)))
        try:
            return zipfile.ZipFile(f).read("word/document.xml").decode(), geo
        except Exception as ex:                                  # noqa: BLE001
            check(False, "[WORD] the exported document is a readable package", str(ex))
            return None


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _bars(tbl: ET.Element) -> list[tuple[int, int, str]]:
    """(offset, length, fill) for every bar drawn inside one chart table."""
    out = []
    for tr in tbl.findall(f"{W}tr"):
        for tc in tr.findall(f"{W}tc"):
            inner = tc.find(f"{W}tbl")
            if inner is None:
                continue
            off, length, fill = 0, 0, ""
            for cell in inner.find(f"{W}tr").findall(f"{W}tc"):
                pr = cell.find(f"{W}tcPr")
                w = int(pr.find(f"{W}tcW").get(f"{W}w"))
                shd = pr.find(f"{W}shd")
                if shd is None:
                    if not length:
                        off += w
                else:
                    length, fill = w, shd.get(f"{W}fill")
            out.append((off, length, fill))
    return out


def _money(s: str) -> float:
    """The number a reader sees beside a bar. '−$39,168' is negative."""
    neg = s.strip().startswith(("−", "-"))
    digits = re.sub(r"[^0-9.]", "", s)
    return (-1 if neg else 1) * float(digits or 0)


def audit_screen_bars(geo: list) -> None:
    """A bar has to be as long as the number it stands for, next to its siblings.

    Bars that cross zero are drawn inside one half of a split cell, so their CSS
    width is a percentage of that half. It used to be written out as a
    percentage of the whole axis, which made every negative bar short by the
    ratio of the halves — the realisation haircut, a fifth of the gross, drew at
    a thirtieth of it. Only measuring the laid-out boxes catches that.
    """
    for i, rows in enumerate(geo, 1):
        vals = [_money(r["value"]) for r in rows]
        span = (max(vals + [0]) - min(vals + [0])) or 1
        cw = rows[0]["cw"] or 1
        bad = []
        for r, v in zip(rows, vals):
            want = abs(v) / span * cw
            if abs(r["w"] - want) > max(3.0, want * 0.04):
                bad.append(f"{r['label']} {r['value']} drew {r['w']:.0f}px, "
                           f"should be {want:.0f}px")
        check(not bad, f"[SCREEN] chart {i}: every bar is as long as its number",
              "; ".join(bad[:3]))
        # Positive and negative bars are laid out in different cells, so a
        # common zero line is not something the markup gives you for free.
        zeros = {round(r["x"] + r["w"] if v < 0 else r["x"]) for r, v in zip(rows, vals) if v}
        check(len(zeros) == 1, f"[SCREEN] chart {i}: the bars share one zero line",
              f"zero lands at {sorted(zeros)}")


TPL_JS = """
var TPLS=window.__T.P, tplEmailHTML=window.__T.f;
var want = (window.__PICK || '');
var all = Object.keys(TPLS).filter(function(k){
  return TPLS[k].ext === 'xlsx' && /xchart/.test(TPLS[k].preview || ''); });
var slug = want ? (all.filter(function(k){ return k.indexOf(want) === 0; })[0] || all[0])
                : (all[0] || '');
var html = slug ? tplEmailHTML(slug) : '';
var d = document.createElement('div'); d.innerHTML = html;
var o = document.createElement('div'); o.id = '__tpl';
// The dialog has four outputs and only one was ever looked at. Run the two
// that transform the HTML further: the .docx builder and the plain-text
// clipboard flavour. A chart that survives as an <img> in the HTML can still
// vanish or leak in either of these.
var docx = '', plain = '';
try {
  var u8 = new Uint8Array(window.__T.D.build('t', html)), b = '';
  for (var i = 0; i < u8.length; i++) b += String.fromCharCode(u8[i]);
  docx = btoa(b);
} catch(e) { docx = 'ERR:' + e.message; }
try { plain = window.__T.P2 ? window.__T.P2(html) : ''; } catch(e) {}
o.textContent = JSON.stringify({
  slug: slug,
  plainCss: /\\.ct\\{|font:700 14px|stroke-width:/.test(plain) ? 1 : 0,
  plainLen: plain.length,
  docx: docx,
  svg:  (html.match(/<svg/g) || []).length,
  style:(html.match(/<style/g) || []).length,
  img:  (html.match(/<img src="data:image\\/svg\\+xml/g) || []).length,
  css:  /\\.ct\\{|font:700|stroke-width:/.test(d.textContent) ? 1 : 0,
  text: d.textContent.length
});
document.body.appendChild(o);
"""


def template_export(pick: str = "") -> dict | None:
    """What tplEmailHTML actually PRODUCES, from the page's own code.

    The check this replaces asserted that the string "svg.xchart" appeared in
    the function's source. That is a check on the code, not on its output, and
    it passed happily while the Pareto's Word export opened as a paragraph of
    raw CSS followed by its axis labels one per line.

    Inline SVG was the cause. A client that cannot draw it strips the element
    and KEEPS ITS TEXT CHILDREN — the <style> block and every <text> node — so
    it degrades to garbage rather than to nothing, which is what the code
    comment had assumed without testing. The browser that already drives the
    business-case export drives this one now.
    """
    import tempfile

    if not Path(CHROME).exists():
        return None
    src = HTML.read_text(encoding="utf-8")
    # tplEmailHTML lives inside the page's IIFE, so it has to be handed out the
    # same way the business-case exporter is. Anchor on the wiring comment that
    # follows it, inside the same scope.
    anchor = "/* ------------------------------------------------------------- wiring */"
    if src.count(anchor) != 1:
        check(False, "[TPLEXPORT] the harness can reach the export function",
              "the wiring anchor moved, so the template export is going untested")
        return None
    handle = ('window.__T={f:tplEmailHTML,P:TPLS,'
              'D:(typeof DOCX!=="undefined"?DOCX:null),'
              'P2:(typeof toPlain!=="undefined"?toPlain:null)};')
    src = src.replace(anchor, handle + "\n" + anchor, 1)

    head, sep, tail = src.rpartition("</body>")
    js = TPL_JS.replace("window.__PICK || ''", "'%s'" % pick)
    src = (head + "<script>window.addEventListener('load',function(){"
           + js + "});</script>" + sep + tail)
    with tempfile.TemporaryDirectory() as td:
        page = Path(td) / "p.html"
        page.write_text(src, encoding="utf-8")
        r = subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--virtual-time-budget=9000",
             "--dump-dom", f"file://{page}"], capture_output=True, text=True, timeout=180)
    m = re.search(r'<div id="__tpl">(.*?)</div>', r.stdout, re.S)
    if not m:
        check(False, "[TPLEXPORT] the template email export runs", "no output")
        return None
    import html as _h
    return json.loads(_h.unescape(m.group(1)))


def audit_template_export() -> None:
    got = template_export()
    if got is None:
        return
    check(bool(got.get("slug")), "[TPLEXPORT] a chart-bearing template was found to export")
    check(got.get("img", 0) > 0,
          "[TPLEXPORT] charts leave as a data-URI image",
          f"img={got.get('img')} — an <img> cannot leak text; inline SVG can")
    check(got.get("svg", 0) == 0,
          "[TPLEXPORT] no raw inline SVG in the export",
          f"{got.get('svg')} inline <svg> — Word strips the element and keeps "
          f"its <text> children, so the chart arrives as a column of labels")
    check(got.get("style", 0) == 0 and got.get("css", 0) == 0,
          "[TPLEXPORT] no stylesheet text reaches the document body",
          "the SVG's <style> block arrives as a paragraph of raw CSS")
    check(got.get("plainCss", 1) == 0,
          "[TPLEXPORT] the plain-text clipboard flavour carries no CSS",
          "toPlain() walks the same HTML — a leak there lands in every paste "
          "into a plain-text field")
    # The .docx is built from that HTML by a second transform, so checking the
    # HTML is not checking the document. These read the real bytes.
    import base64
    import io
    import zipfile
    raw = got.get("docx", "")
    if raw.startswith("ERR") or not raw:
        check(False, "[TPLEXPORT] the template exports as a Word document", raw[:80])
        return
    doc = zipfile.ZipFile(io.BytesIO(base64.b64decode(raw))).read(
        "word/document.xml").decode()
    check(not re.search(r"\.ct\{|font:700 14px|stroke-width:", doc),
          "[TPLEXPORT] no stylesheet text in the .docx itself",
          "this is the file the reader opens — the HTML being clean does not "
          "make the document clean, and it was the document that shipped CSS")
    # Known gap, asserted so it cannot be forgotten or silently 'fixed' by a
    # change that drops the caption too: DOCX.build renders no <w:drawing>, so
    # a template chart does not reach Word. The business-case exporter draws
    # its charts as tables of shaded cells; templates need the same. Until then
    # the caption naming the chart and pointing at the .xlsx is what stands in
    # for it, and it has to be there.
    check("the live chart is in the .xlsx" in doc,
          "[TPLEXPORT] every chart names itself and says where the live one is",
          "the caption is what a reader has if their client drops the picture")
    # Word draws neither inline SVG nor a data-URI image, so a template chart
    # only exists in the document if it was rebuilt out of shaded table cells —
    # the same thing the business-case exporter does. Count the shading: an
    # empty table would satisfy a check that only counted tables.
    bars = len(re.findall(r'w:fill="(?!auto)[0-9A-Fa-f]{6}"', doc))
    check(bars > 0,
          "[TPLEXPORT] template charts are drawn as bars in the .docx",
          "no shaded cell in the document — the chart reaches Word as a "
          "caption and nothing else")
    # The two shapes bars cannot express. A combo carries two scales, so each
    # group is drawn against its own range rather than all of them against one
    # span, which turned a Pareto's cumulative share into slivers. A scatter has
    # no categories at all and becomes the pairs it actually is.
    for pick, want, why in (
            ("25-pareto", 12, "a combo chart draws each group against its own range"),
            ("30-regression", 0, "a scatter chart reaches the document as x/y pairs")):
        g2 = template_export(pick)
        if not g2 or str(g2.get("docx", "")).startswith("ERR"):
            check(False, f"[TPLEXPORT] {pick} exports", "no document")
            continue
        d2 = zipfile.ZipFile(io.BytesIO(base64.b64decode(g2["docx"]))).read(
            "word/document.xml").decode()
        shaded = len(re.findall(r'w:fill="(?!auto)[0-9A-Fa-f]{6}"', d2))
        txt = re.sub(r"<[^>]+>", " ", d2)
        ok = shaded >= want if want else ("Residual for each contact" in txt)
        check(ok, f"[TPLEXPORT] {why}",
              f"{pick}: shaded={shaded}, wanted {want or 'x/y pairs in the text'}")


def audit_word_charts() -> None:
    got = word_document()
    if got is None:
        return
    doc, geo = got
    check(len(geo) == 4, "[SCREEN] the business case draws all four charts",
          f"found {len(geo)}")
    if len(geo) == 4:
        audit_screen_bars(geo)
    root = ET.fromstring(doc)
    body = root.find(f"{W}body")
    # A chart table is the one the writer left unbordered.
    charts = [t for t in body.findall(f"{W}tbl")
              if t.find(f"{W}tblPr/{W}tblBorders") is None]
    check(len(charts) == 4, "[WORD] all four business-case charts reach the document",
          f"found {len(charts)}")
    if len(charts) != 4:
        return

    # Split equally, a three-column chart gives the bars a third of the page and
    # the labels a third they do not need.
    for i, tbl in enumerate(charts):
        cols = [int(g.get(f"{W}w")) for g in tbl.findall(f"{W}tblGrid/{W}gridCol")]
        check(len(cols) == 3 and cols[1] > cols[0] > cols[2],
              f"[WORD] chart {i + 1} gives the page to the bars, not the labels", str(cols))

    total = 0
    for i, tbl in enumerate(charts):
        rows = tbl.findall(f"{W}tr")
        bars = _bars(tbl)
        # querySelectorAll used to reach through the nested bar tables, so each
        # bar contributed a blank row of its own to the chart around it.
        check(len(rows) == len(bars),
              f"[WORD] chart {i + 1} has one row per bar and no phantom rows",
              f"{len(rows)} rows against {len(bars)} bars")
        check(all(b[1] > 0 for b in bars),
              f"[WORD] chart {i + 1} draws a bar on every row",
              f"{sum(1 for b in bars if not b[1])} row(s) came through empty")
        total += len(bars)
    check(total == 14, "[WORD] every bar in the business case is drawn",
          f"{total} of 14")

    # The bridge is gross, the haircut, and what is left. A negative bar has to
    # finish exactly where the positive ones start, and lengths have to hold the
    # ratio of the values they stand for: the haircut is a fifth of the gross,
    # and it used to be drawn at a thirtieth of it.
    bridge = _bars(charts[0])
    if len(bridge) != 3:
        check(False, "[WORD] the bridge chart still has its three bars", str(len(bridge)))
        return
    off, ln, fill = zip(*bridge)
    check(fill == ("2F6FEB", "DC2626", "15A34A"),
          "[WORD] the bridge keeps its gross / haircut / realised colours", str(fill))
    zero = off[0]
    check(off[1] + ln[1] == zero and off[2] == zero,
          "[WORD] the bridge's bars share one zero line",
          f"negative ends at {off[1] + ln[1]}, positives start at {off[0]}/{off[2]}")
    check(abs(ln[1] / ln[0] - 0.2) < 0.02,
          "[WORD] the haircut is drawn at a fifth of the gross, as it is",
          f"ratio {ln[1] / ln[0]:.3f}")
    check(abs(ln[2] / ln[0] - 0.8) < 0.02,
          "[WORD] the realised bar is drawn at four fifths of the gross",
          f"ratio {ln[2] / ln[0]:.3f}")


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
    audit_word_charts()
    audit_template_export()
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
