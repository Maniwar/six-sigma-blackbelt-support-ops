#!/usr/bin/env python3
"""Quality audit for every workbook in templates/.

A template is only useful if someone can open it, understand what to type, and
trust what comes back. That is three separate failure modes, so this checks
three separate layers:

  CHARTS   every chart resolves to real data, is titled, and is readable
  GUIDED   every cell you are asked to fill in says where the number comes from
  NUMERIC  the whole workbook recalculates without a single error value

Run it after any change to tools/build_templates.py or tools/patch_workbooks.py:

    python3 tools/qa_templates.py            # all three layers
    python3 tools/qa_templates.py --fast     # skip NUMERIC (it is the slow one)

Exit status is non-zero if anything failed, so it drops straight into CI.
"""
from __future__ import annotations

import re
import sys
import warnings
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import range_boundaries

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"

# Colours the builders use. Yellow is "you fill this in", so a yellow cell that
# carries no explanation is the single most common way a template goes unused.
FILL_INPUT = "FFFFF9E3"
FILL_CALC = "FFF2F7FF"

# Workbooks where a chart would be noise rather than signal: a 5 Whys chain and
# a RACI grid are structures, not distributions. Everything else must chart.
NO_CHART_OK = {
    "20-five-whys-tree.xlsx": "a causal chain is a structure, not a distribution",
}

ERR_VALUES = ("#REF!", "#VALUE!", "#DIV/0!", "#NAME?", "#N/A", "#NULL!", "#NUM!")

# NA() is the only construction that reliably leaves a gap in a plotted series;
# "" plots as zero and draws a row of markers along the axis floor. The marker
# columns are therefore FULL of #N/A by design. Exempt those columns only —
# whitelisting #N/A globally would blunt the check that catches real breakage.
NA_BY_DESIGN = {
    # the ROI horizon: years beyond "Years to model" are NA() so the line stops
    # rather than dropping to zero under a title promising it crosses zero
    "19-black-belt-calculators.xlsx": {"9 ROI and payback": "B:C"},
    "27-control-charts.xlsx": {"I-MR": "AD:AF", "Laney p-prime": "AD:AE",
                               "Laney u-prime": "AD:AE", "Xbar-R": "AD:AF",
                               "EWMA": "AD:AD", "CUSUM": "AD:AD",
                               "t and g (rare events)": "AD:AG"},
}

fails: list[str] = []
warns: list[str] = []


def fail(book: str, layer: str, msg: str) -> None:
    fails.append(f"  FAIL [{layer}] {book}: {msg}")


def warn(book: str, layer: str, msg: str) -> None:
    warns.append(f"  warn [{layer}] {book}: {msg}")


# ---------------------------------------------------------------- helpers


def merged_shadow(ws) -> set[tuple[int, int]]:
    """Cells swallowed by a merge. A formula reading one of these is always empty."""
    out = set()
    for rng in ws.merged_cells.ranges:
        c1, r1, c2, r2 = range_boundaries(str(rng))
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                if (r, c) != (r1, c1):
                    out.add((r, c))
    return out


REF_RE = re.compile(r"^'?(?P<sheet>[^'!]+)'?!\$?(?P<c1>[A-Z]+)\$?(?P<r1>\d+)"
                    r"(?::\$?(?P<c2>[A-Z]+)\$?(?P<r2>\d+))?$")


def parse_ref(ref: str):
    """('Sheet1'!$B$4:$B$27) -> (sheet, min_col, min_row, max_col, max_row)."""
    m = REF_RE.match((ref or "").strip())
    if not m:
        return None
    from openpyxl.utils import column_index_from_string as ci
    c1, r1 = ci(m.group("c1")), int(m.group("r1"))
    c2 = ci(m.group("c2")) if m.group("c2") else c1
    r2 = int(m.group("r2")) if m.group("r2") else r1
    return m.group("sheet"), min(c1, c2), min(r1, r2), max(c1, c2), max(r1, r2)


def series_refs(ser):
    """(values_ref, categories_ref) for a chart series, as written in the XML."""
    val = None
    if ser.val is not None and ser.val.numRef is not None:
        val = ser.val.numRef.f
    elif getattr(ser, "yVal", None) is not None and ser.yVal.numRef is not None:
        val = ser.yVal.numRef.f
    cat = None
    if ser.cat is not None:
        if ser.cat.numRef is not None:
            cat = ser.cat.numRef.f
        elif ser.cat.strRef is not None:
            cat = ser.cat.strRef.f
    elif getattr(ser, "xVal", None) is not None:
        if ser.xVal.numRef is not None:
            cat = ser.xVal.numRef.f
        elif ser.xVal.strRef is not None:
            cat = ser.xVal.strRef.f
    return val, cat


def chart_title_text(ch) -> str:
    """openpyxl nests the title several layers down; dig it out."""
    t = getattr(ch, "title", None)
    if t is None:
        return ""
    rich = getattr(getattr(t, "tx", None), "rich", None)
    if rich is None:
        return str(t) if isinstance(t, str) else ""
    return "".join(r.t or "" for p in rich.p for r in (p.r or []))


# ---------------------------------------------------------------- layers


def audit_charts(path: Path, wb) -> int:
    """Every chart must plot real cells, be titled, and not sit on top of the data."""
    book = path.name
    total = 0
    for ws in wb.worksheets:
        shadow = merged_shadow(ws)
        for ch in getattr(ws, "_charts", []):
            total += 1
            label = f"{ws.title!r} chart {total}"
            if not chart_title_text(ch).strip():
                fail(book, "CHARTS", f"{label} has no title — a chart with no title is a decoration")
            if not ch.series:
                fail(book, "CHARTS", f"{label} has no data series at all")
                continue
            for si, ser in enumerate(ch.series, start=1):
                vref, cref = series_refs(ser)
                if not vref:
                    fail(book, "CHARTS", f"{label} series {si} has no value reference")
                    continue
                p = parse_ref(vref)
                if not p:
                    fail(book, "CHARTS", f"{label} series {si} value ref is unparseable: {vref}")
                    continue
                sheet, c1, r1, c2, r2 = p
                if sheet not in wb.sheetnames:
                    fail(book, "CHARTS", f"{label} series {si} points at missing sheet {sheet!r}")
                    continue
                src = wb[sheet]
                cells = [src.cell(row=r, column=c)
                         for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
                if len(cells) < 2:
                    fail(book, "CHARTS", f"{label} series {si} plots {len(cells)} point(s) — not a chart")
                live = [c for c in cells
                        if c.value is not None and (r1, c1) not in shadow]
                if not live:
                    fail(book, "CHARTS",
                         f"{label} series {si} range {vref} is entirely empty — this renders blank in Excel")
                hidden = [c.coordinate for c in cells if (c.row, c.column) in merged_shadow(src)]
                if hidden:
                    fail(book, "CHARTS",
                         f"{label} series {si} reads merged-shadow cells {hidden[:3]} which are always empty")
                if cref:
                    pc = parse_ref(cref)
                    if not pc:
                        fail(book, "CHARTS", f"{label} series {si} category ref unparseable: {cref}")
                    else:
                        _, cc1, cr1, cc2, cr2 = pc
                        n_cat = (cr2 - cr1 + 1) * (cc2 - cc1 + 1)
                        n_val = (r2 - r1 + 1) * (c2 - c1 + 1)
                        if n_cat != n_val:
                            fail(book, "CHARTS",
                                 f"{label} series {si} has {n_cat} categories for {n_val} values — "
                                 "Excel will silently drop the overhang")
                else:
                    warn(book, "CHARTS", f"{label} series {si} has no category axis — points get numbered 1..n")
            if ch.__class__.__name__ == "BarChart":
                for si, ser in enumerate(ch.series, start=1):
                    if ser.invertIfNegative is not False:
                        fail(book, "CHARTS",
                             f"{label} series {si} leaves invertIfNegative unset — any negative "
                             "value renders as a blank bar")
            # A series with no name shows as "Series1" the moment anything
            # turns the legend on — which laying a reference line over a bar
            # chart does.
            if getattr(ch, "legend", None) is not None:
                for si, ser in enumerate(ch.series, start=1):
                    tx = getattr(ser, "tx", None)
                    nm = ""
                    if tx is not None:
                        nm = (getattr(tx, "v", None) or
                              (tx.strRef.f if getattr(tx, "strRef", None) else "") or "")
                    if not nm:
                        fail(book, "CHARTS",
                             f"{label} series {si} has no name but the chart has a legend — "
                             "Excel will label it 'Series1'")
            if ch.height and ch.height < 5:
                warn(book, "CHARTS", f"{label} is only {ch.height}cm tall — labels will collide")
    # Per-SHEET, not just per-workbook. A workbook passed the "has charts" rule
    # on the strength of one chart while another of its tabs shipped completely
    # empty — every statistic blank and a verdict reading "paste your data".
    for ws in wb.worksheets:
        low = ws.title.lower()
        if low.startswith(("how to", "start here", "pick your", "category prompts",
                           "countermeasure", "scoring guide", "which chart",
                           "six-trap", "raci", "fishbone diagram", "5 whys")):
            continue
        # Not "few numbers" — a calculator tab legitimately has three inputs
        # and that is the whole tab. The signature is formulas with NOTHING
        # driving them: every statistic blank and a verdict reading "paste your
        # data in", which is how the distribution tab shipped.
        def _drives(c):
            if isinstance(c.value, (int, float)):
                return True
            try:                                   # a green worked-example cell
                return (c.fill and c.fill.patternType
                        and str(c.fill.fgColor.rgb) == "FFECFAEF"
                        and c.value not in (None, ""))
            except Exception:                      # noqa: BLE001
                return False
        nums = sum(1 for row in ws.iter_rows() for c in row if _drives(c))
        forms = sum(1 for row in ws.iter_rows() for c in row
                    if isinstance(c.value, str) and c.value.startswith("="))
        if forms >= 5 and nums < 2:
            fail(book, "CHARTS",
                 f"sheet {ws.title!r} has {forms} formulas and {nums} numbers to drive them — "
                 "it ships blank, so nothing on it demonstrates the point of the tab")

    if total == 0 and book not in NO_CHART_OK:
        fail(book, "CHARTS", "no charts at all — the numbers are there but nobody can see the shape")
    return total


GUIDE_TABS = ("how to use", "start here", "read me", "readme", "pick your chart")


def _column_header(ws, col: int, row: int) -> str:
    """The dark banded header above this cell, if it is in a data table.

    A table column explains itself once, in its header — demanding a note on all
    230 cells of an entry grid is not a quality bar, it is noise. A standalone
    input (a label in column A, a value in column B) has no header, and that is
    the case that genuinely needs a per-cell explanation.
    """
    for r in range(row - 1, 0, -1):
        try:
            rgb = ""
            c = ws.cell(row=r, column=col)
            if c.fill and c.fill.patternType:
                rgb = str(c.fill.fgColor.rgb)
            if rgb == "FF333C49":                # the table's header row
                return str(c.value or "") or "\x00"
            if rgb == "FFEEF1F6":                # a section band: different block
                return ""
            # a band can be merged, so it may only be filled in column A
            a = ws.cell(row=r, column=1)
            if a.fill and a.fill.patternType and str(a.fill.fgColor.rgb) == "FFEEF1F6":
                return ""
        except Exception:                                        # noqa: BLE001
            pass
    return ""


def audit_guided(path: Path, wb) -> None:
    """Every yellow cell has to say where its number comes from."""
    book = path.name
    if not any(any(s.lower().startswith(g) for g in GUIDE_TABS) for s in wb.sheetnames):
        fail(book, "GUIDED", "no instructions tab — nothing tells a first-time user what to do")
    naked, unlabelled, inputs = [], [], 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                try:
                    rgb = str(c.fill.fgColor.rgb) if c.fill and c.fill.patternType else ""
                except Exception:                                # noqa: BLE001
                    rgb = ""
                if rgb != FILL_INPUT:
                    continue
                inputs += 1
                head = _column_header(ws, c.column, c.row)
                if head:
                    # a table cell: the header carries the explanation, so the
                    # only real failure is a header that says nothing
                    # "#" is a fine header for a row-number column; only a
                    # genuinely blank one leaves the user guessing
                    if head == "\x00" or not head.strip():
                        unlabelled.append(f"{ws.title}!{c.coordinate}")
                    continue
                # standalone input: needs a comment, or prose beside it
                has_note = c.comment is not None
                # prose beside it, or the label that names it, or a note in the
                # row underneath the block
                probes = [(c.row, c.column + 1), (c.row, c.column + 2),
                          (c.row, max(1, c.column - 1)), (c.row + 1, 1), (c.row + 2, 1)]
                for pr, pc in probes:
                    if has_note:
                        break
                    v = ws.cell(row=pr, column=pc).value
                    has_note = isinstance(v, str) and len(v) > 8
                if not has_note:
                    naked.append(f"{ws.title}!{c.coordinate}")
    if inputs == 0:
        warn(book, "GUIDED", "no yellow input cells — is anything meant to be filled in?")
    if naked:
        fail(book, "GUIDED",
             f"{len(naked)} standalone input(s) with no explanation of where the number "
             f"comes from: {naked[:5]}")
    if unlabelled:
        fail(book, "GUIDED", f"{len(unlabelled)} input(s) under a blank column header: {unlabelled[:5]}")
    # A label appearing twice on one sheet is the signature of a ghost block:
    # a helper table that was moved, leaving the old copy behind, because the
    # builders only ever write cells and never clear the ground they left.
    for ws in wb.worksheets:
        # Only BOLD text counts. Ordinary content legitimately repeats — two
        # solutions can address the same root cause, two metrics can use the
        # same chart type — but a heading appearing twice means a block was
        # moved and its old copy was left behind.
        labels = {}
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if not (isinstance(v, str) and len(v) > 24 and not v.startswith("=")):
                    continue
                if not (c.font and c.font.bold):
                    continue
                labels.setdefault(v, []).append(c.coordinate)
        ghosts = {v: at for v, at in labels.items() if len(at) > 1}
        if ghosts:
            v, at = next(iter(ghosts.items()))
            fail(book, "GUIDED",
                 f"{len(ghosts)} label(s) appear more than once on {ws.title!r} — "
                 f"a moved helper block left its old copy behind: {v[:40]!r} at {at[:3]}")

    if not any(ws.sheet_view.showGridLines is False for ws in wb.worksheets):
        warn(book, "GUIDED", "gridlines left on everywhere — reads like a spreadsheet, not a tool")


def _na_ok(book: str, where: str) -> bool:
    """Is this cell one of the marker columns that is #N/A on purpose?"""
    import re as _re
    from openpyxl.utils import column_index_from_string as _ci
    sheets = NA_BY_DESIGN.get(book)
    if not sheets:
        return False
    m = _re.match(r"^(.*)!([A-Z]+)\d+$", where)
    if not m:
        return False
    # the recalculated keys come back with the sheet name upper-cased
    span = next((v for k, v in sheets.items() if k.upper() == m.group(1).upper()), None)
    if not span:
        return False
    lo, hi = (_ci(x) for x in span.split(":"))
    return lo <= _ci(m.group(2)) <= hi


def audit_numeric(path: Path) -> None:
    """Recalculate the whole workbook and refuse a single error value."""
    book = path.name
    try:
        import formulas
    except ImportError:
        warn(book, "NUMERIC", "the `formulas` package is not installed — skipped")
        return
    warnings.filterwarnings("ignore")
    try:
        xl = formulas.ExcelModel().loads(str(path)).finish()
        sol = xl.calculate()
    except Exception as exc:                                   # noqa: BLE001
        fail(book, "NUMERIC", f"workbook will not recalculate: {type(exc).__name__}: {exc}")
        return
    bad = {}
    for key, cell in sol.items():
        if "'!" not in key or "!_XLFN" in key.upper():
            continue
        try:
            v = cell.value[0, 0]
        except Exception:
            continue
        if isinstance(v, str) and v.strip() in ERR_VALUES:
            where = key.split("]")[-1].replace("'", "")
            if v.strip() == "#N/A" and _na_ok(book, where):
                continue
            bad.setdefault(v.strip(), []).append(where)
    for err, where in sorted(bad.items()):
        fail(book, "NUMERIC", f"{len(where)} cell(s) evaluate to {err}: {where[:5]}")


# ---------------------------------------------------------------- main


SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"


def render(books: list[Path], outdir: Path) -> list[Path]:
    """Render each workbook to page PNGs so the charts can actually be looked at.

    Structural checks prove a chart references live cells. They cannot tell you
    the axis runs 0-500 for data that lives between 396 and 442, so every point
    is squashed into the top fifth of the plot. Only looking at it tells you
    that, so the audit renders through LibreOffice and leaves PNGs behind.
    """
    import shutil
    import subprocess

    soffice = SOFFICE if Path(SOFFICE).exists() else shutil.which("soffice")
    if not soffice:
        print("  (no LibreOffice — skipping the visual layer)")
        return []
    if not shutil.which("pdftoppm"):
        print("  (no pdftoppm — `brew install poppler` — skipping the visual layer)")
        return []
    outdir.mkdir(parents=True, exist_ok=True)
    pngs = []
    for book in books:
        subprocess.run([soffice, "--headless", "--norestore", "--convert-to",
                        "pdf:calc_pdf_Export", "--outdir", str(outdir), str(book)],
                       check=False, capture_output=True, stdin=subprocess.DEVNULL)
        pdf = outdir / (book.stem + ".pdf")
        if not pdf.exists():
            fail(book.name, "VISUAL", "LibreOffice could not open it — the file may be corrupt")
            continue
        subprocess.run(["pdftoppm", "-r", "100", "-png", str(pdf), str(outdir / book.stem)],
                       check=False, capture_output=True)
        got = sorted(outdir.glob(book.stem + "-*.png"))
        pngs += got
        print(f"  rendered {book.name:36s} {len(got)} page(s)")
    return pngs


def audit_rubric(path: Path, wb, guidance: int) -> list[dict]:
    """Grade every chart against CHART-QA.md and fail the ones below the bar."""
    from chart_rubric import charts_in, grade, ships
    out = []
    for ch in charts_in(path):
        g = grade(path.name, ch, wb)
        g["guidance"] = guidance
        g["ships"] = ships(g, guidance)
        out.append(g)
        if not g["ships"]:
            fail(path.name, "RUBRIC",
                 f"{g['title'][:46] or '(untitled)'} — " + "; ".join(g["notes"] or ["below the bar"]))
    return out


def main() -> int:
    fast = "--fast" in sys.argv
    visual = "--visual" in sys.argv
    rubric = "--rubric" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    books = sorted(TEMPLATES.glob("*.xlsx"))
    if only:
        books = [b for b in books if any(o in b.name for o in only)]
    print(f"Auditing {len(books)} workbook(s) in templates/\n")
    charts = 0
    graded: list[dict] = []
    for path in books:
        wb = load_workbook(path)
        n = audit_charts(path, wb)
        before = len(fails)
        audit_guided(path, wb)
        guidance = 2 if len(fails) == before else 1
        charts += n
        if rubric:
            graded += audit_rubric(path, wb, guidance)
        note = f"  ({NO_CHART_OK[path.name]})" if n == 0 and path.name in NO_CHART_OK else ""
        print(f"  {path.name:36s} sheets={len(wb.worksheets):2d}  charts={n:2d}{note}")
        if not fast:
            audit_numeric(path)
    print(f"\n  {charts} charts across {len(books)} workbooks")
    if rubric and graded:
        ok = sum(1 for g in graded if g["ships"])
        print(f"\n  SCORECARD — {ok}/{len(graded)} charts clear the bar "
              "(gates pass, worth>=3, example=3, guidance=2)\n")
        print(f"  {'chart':50s} {'form':>6s} {'read':>5s} {'worth':>6s} {'exmpl':>6s} {'guide':>6s}")
        for g in sorted(graded, key=lambda x: (x["ships"], x["book"])):
            mark = "  " if g["ships"] else "->"
            print(f"{mark}{(g['title'] or '(untitled)')[:48]:50s} "
                  f"{'ok' if g['right_chart'] else 'FAIL':>6s} "
                  f"{'ok' if g['readable'] else 'FAIL':>5s} "
                  f"{g['worth']}/4{'':>3s} {g['example']}/3{'':>3s} {g['guidance']}/2")
    if visual:
        # --visual takes no value of its own: the positional arguments are
        # workbook filters, and consuming one here rendered into a directory
        # named after the filter.
        out = ROOT / ".qa-render"
        for a in sys.argv[1:]:
            if a.startswith("--out="):
                out = Path(a.split("=", 1)[1])
        print(f"\nRendering to {out} …")
        pngs = render(books, out)
        print(f"  {len(pngs)} page image(s) — open them and look at every chart")
    if warns:
        print(f"\n{len(warns)} warning(s):")
        print("\n".join(warns))
    if fails:
        print(f"\n{len(fails)} FAILURE(S):")
        print("\n".join(fails))
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
