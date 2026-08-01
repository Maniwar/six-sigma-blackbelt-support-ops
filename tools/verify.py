#!/usr/bin/env python3
"""Test suite for the workbooks and the single-file HTML.

Three layers:

  STRUCTURE  every formula is checked for the defect class that produced the
             worst bug in this repo - a formula reading a cell that sits inside
             a merged range but is not its top-left anchor, and is therefore
             always empty. The SLA verdict did exactly that and returned
             "NOT CAPABLE" for every possible input.

  NUMERIC    the fixed calculators are recalculated with a real formula engine
             against inputs chosen to expose the original bugs. Needs the
             optional `formulas` package; skipped with a warning if absent.

  SYNC       the four copies of every template agree: templates/*.xlsx, the
             base64 blob in the HTML, the preview tooltips, and docs/index.html.

    python3 tools/verify.py            # everything
    python3 tools/verify.py --fast     # skip the numeric layer

Requires: openpyxl  (+ formulas, optional)
"""
from __future__ import annotations

import base64
import html as H
import json
import re
import shutil
import sys
import tempfile
import warnings
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter, range_boundaries

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from sync_html import RE_ROW, RE_SHEET, RE_TD, extract_tpls  # noqa: E402

HTML = ROOT / "six-sigma-blackbelt-support-ops.html"
DOCS = ROOT / "docs" / "index.html"
TEMPLATES = ROOT / "templates"
CALC = "19-black-belt-calculators.xlsx"

FAILURES: list[str] = []
PASSES = [0]


def check(cond: bool, label: str, detail: str = "") -> None:
    if cond:
        PASSES[0] += 1
    else:
        FAILURES.append(f"{label}" + (f"\n      {detail}" if detail else ""))


def approx(a, b, tol=1e-6) -> bool:
    try:
        return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------- STRUCTURE
CELL_REF = re.compile(r"(?<![A-Za-z0-9_!$])(\$?)([A-Z]{1,3})(\$?)([0-9]{1,7})(?![0-9(])")


def covered_non_anchor(ws) -> set[str]:
    """Cells inside a merged range that are not its top-left anchor."""
    dead = set()
    for rng in ws.merged_cells.ranges:
        min_c, min_r, max_c, max_r = range_boundaries(str(rng))
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                if (r, c) != (min_r, min_c):
                    dead.add(f"{get_column_letter(c)}{r}")
    return dead


def test_structure() -> None:
    for path in sorted(TEMPLATES.glob("*.xlsx")):
        wb = load_workbook(path)
        for ws in wb.worksheets:
            dead = covered_non_anchor(ws)
            if not dead:
                continue
            for row in ws.iter_rows():
                for cell in row:
                    v = cell.value
                    if not (isinstance(v, str) and v.startswith("=")):
                        continue
                    # ignore quoted string literals inside the formula
                    bare = re.sub(r'"[^"]*"', '""', v)
                    for m in CELL_REF.finditer(bare):
                        ref = f"{m.group(2)}{m.group(4)}"
                        if ref in dead:
                            check(
                                False,
                                f"{path.name} [{ws.title}] {cell.coordinate} reads {ref}, "
                                f"which is swallowed by a merged range and is always empty",
                                v[:120],
                            )
            PASSES[0] += 1


# ------------------------------------------------------------------ NUMERIC
def _engine(path: Path):
    warnings.filterwarnings("ignore")
    import formulas

    return formulas.ExcelModel().loads(str(path)).finish()


def _read(sol, fname: str, sheet: str, cell: str):
    key = f"'[{fname.upper()}]{sheet.upper()}'!{cell}"
    for k, v in sol.items():
        if k.upper() == key:
            try:
                return v.value[0, 0]
            except Exception:
                return v
    return "<missing>"


def recalc(scenarios: list[tuple[str, str, object]], sheets_cells):
    """Copy the calculator workbook, apply inputs, recalculate, read outputs."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / CALC
        shutil.copyfile(TEMPLATES / CALC, tmp)
        if scenarios:
            wb = load_workbook(tmp)
            for sheet, cell, val in scenarios:
                wb[sheet][cell] = val
            wb.save(tmp)
        sol = _engine(tmp).calculate()
        return {(s, c): _read(sol, CALC, s, c) for s, c in sheets_cells}


def test_numeric() -> None:
    K = "2 QA agreement (kappa)"
    S = "3 SLA capability"
    R = "9 ROI and payback"

    # --- kappa verdict must follow kappa (B13), not chance agreement (B12).
    # Perfect agreement: the old formula read Pe = 0.50 and said MARGINAL.
    out = recalc([(K, "B5", 35), (K, "B6", 0), (K, "B7", 0), (K, "B8", 35)], [(K, "B13"), (K, "B14")])
    check(approx(out[(K, "B13")], 1.0), "kappa: perfect agreement gives kappa = 1.0", repr(out[(K, "B13")]))
    check(str(out[(K, "B14")]).startswith("EXCELLENT"),
          "kappa verdict: perfect agreement reads EXCELLENT (was MARGINAL)", repr(out[(K, "B14")]))

    # Worse than chance: the old formula read Pe = 0.918 and said EXCELLENT.
    out = recalc([(K, "B5", 64), (K, "B6", 3), (K, "B7", 3), (K, "B8", 0)], [(K, "B13"), (K, "B14")])
    check(float(out[(K, "B13")]) < 0, "kappa: worse-than-chance is negative", repr(out[(K, "B13")]))
    check(str(out[(K, "B14")]).startswith("UNACCEPTABLE"),
          "kappa verdict: worse-than-chance reads UNACCEPTABLE (was EXCELLENT)", repr(out[(K, "B14")]))

    # --- SLA verdict must follow Ppu (B13). The old formula read B15, an empty
    #     merged cell, so every input returned NOT CAPABLE.
    out = recalc([(S, "B5", 8), (S, "B6", 2.6), (S, "B7", 1.1)], [(S, "B13"), (S, "B17")])
    check(approx(out[(S, "B13")], (8 - 2.6) / (3 * 1.1)), "SLA: Ppu arithmetic", repr(out[(S, "B13")]))
    check(out[(S, "B17")] == "CAPABLE",
          "SLA verdict: a capable process reads CAPABLE (was always NOT CAPABLE)", repr(out[(S, "B17")]))

    # Ppu = (6.5 - 2.6) / (3 x 1.1) = 1.18, i.e. inside the 1.00-1.33 band.
    out = recalc([(S, "B5", 6.5), (S, "B6", 2.6), (S, "B7", 1.1)], [(S, "B13"), (S, "B17")])
    check(1.0 <= float(out[(S, "B13")]) < 1.33, "SLA: test input lands in the marginal band",
          repr(out[(S, "B13")]))
    check(out[(S, "B17")].startswith("MARGINAL"), "SLA verdict: middle band reads MARGINAL", repr(out[(S, "B17")]))

    out = recalc([], [(S, "B17")])  # shipped example, Ppu 0.42
    check(out[(S, "B17")].startswith("NOT CAPABLE"),
          "SLA verdict: shipped example still reads NOT CAPABLE", repr(out[(S, "B17")]))

    # --- NPV must honour any number of years, matching the HTML card's loop.
    for years in (1, 3, 5, 10):
        out = recalc([(R, "B5", 193000), (R, "B6", 156672), (R, "B7", years), (R, "B8", 0.1)], [(R, "B15")])
        want = -193000 + sum(156672 / (1.1 ** y) for y in range(1, years + 1))
        check(approx(out[(R, "B15")], want, 1e-6),
              f"ROI: NPV correct at {years} year(s)", f"got {out[(R, 'B15')]!r} want {want:,.2f}")

    out = recalc([(R, "B5", 193000), (R, "B6", 156672), (R, "B7", 3), (R, "B8", 0)], [(R, "B15")])
    check(approx(out[(R, "B15")], -193000 + 156672 * 3), "ROI: NPV handles a zero discount rate",
          repr(out[(R, "B15")]))

    # --- zero defects used to make NORMSINV(1) a #NUM!.
    out = recalc([("1 Sigma level", "B7", 0)], [("1 Sigma level", "B15")])
    check(not isinstance(out[("1 Sigma level", "B15")], float) or out[("1 Sigma level", "B15")] == out[("1 Sigma level", "B15")],
          "sigma: zero defects does not raise #NUM!", repr(out[("1 Sigma level", "B15")]))


def test_numeric_other() -> None:
    """Hypothesis log and VSM, which live in their own workbooks."""
    # Hypothesis log: a blank practical threshold must not be read as "matters".
    src = TEMPLATES / "13-hypothesis-test-log.xlsx"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / src.name
        shutil.copyfile(src, tmp)
        wb = load_workbook(tmp)
        ws = wb["Test log"]
        ws["M11"] = None  # clear the practical threshold, keep p and effect
        wb.save(tmp)
        sol = _engine(tmp).calculate()
        got = _read(sol, src.name, "Test log", "N11")
        check(str(got).strip() in ("", "0"),
              "hypothesis log: blank practical threshold leaves the verdict blank "
              "(was 'YES - real and matters')", repr(got))

    # Durability counters must survive a free-text paste in the hierarchy column
    # instead of turning the whole summary into #VALUE!, and must still count.
    src = TEMPLATES / "15-solution-selection-matrix.xlsx"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / src.name
        shutil.copyfile(src, tmp)
        wb = load_workbook(tmp)
        ws = wb["Solution selection"]
        rows = [("a", "1 Eliminate demand", "Yes"), ("b", "3 Guide it", "Yes"),
                ("c", "2 Design it out", "Yes"), ("d", "6 Train and remind", "Yes"),
                ("e", "not a level at all", "Yes"), ("f", "1 Eliminate demand", "No")]
        for i, (name, lvl, sel) in enumerate(rows, start=14):
            ws[f"B{i}"], ws[f"L{i}"], ws[f"M{i}"] = name, lvl, sel
        wb.save(tmp)
        sol = _engine(tmp).calculate()
        e37 = _read(sol, src.name, "Solution selection", "E37")
        e38 = _read(sol, src.name, "Solution selection", "E38")
        check(approx(e37, 3), "solution matrix: durable count survives a junk paste", f"got {e37!r} want 3")
        check(approx(e38, 1), "solution matrix: decaying count survives a junk paste", f"got {e38!r} want 1")

    src = TEMPLATES / "17-control-plan.xlsx"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / src.name
        shutil.copyfile(src, tmp)
        wb = load_workbook(tmp)
        ws = wb["Control plan"]
        # the sheet now ships with worked example rows; this fixture is about
        # the formula, so clear the data region before planting it
        for r in range(10, 28):
            ws[f"A{r}"], ws[f"P{r}"] = None, None
        for i, (name, lvl) in enumerate([("m1", "2 Design it out"), ("m2", "3 Guide it"),
                                         ("m3", "5 Standardise it"), ("m4", "garbage")], start=10):
            ws[f"A{i}"], ws[f"P{i}"] = name, lvl
        wb.save(tmp)
        sol = _engine(tmp).calculate()
        e30 = _read(sol, src.name, "Control plan", "E30")
        e31 = _read(sol, src.name, "Control plan", "E31")
        e32 = _read(sol, src.name, "Control plan", "E32")
        check(approx(e30, 2), "control plan: durable count survives a junk paste", f"got {e30!r} want 2")
        check(approx(e31, 1), "control plan: decaying count survives a junk paste", f"got {e31!r} want 1")
        check(approx(e32, 0.5), "control plan: durable share", f"got {e32!r} want 0.5")

    # Kano: the published evaluation table, cell by cell. Two of these were
    # transposed — Like/Dislike returned "Delighter" and Expect-it/Dislike
    # returned "Performance", so the two most common answers in a support
    # survey each got the other's investment advice.
    src = TEMPLATES / "23-kano-analysis.xlsx"
    KANO = [
        ("Like", "Dislike", "Performance"),        # one-dimensional
        ("Like", "Live with it", "Delighter"),
        ("Like", "Neutral", "Delighter"),
        ("Like", "Expect it", "Delighter"),
        ("Like", "Like", "Questionable"),
        ("Expect it", "Dislike", "Must-have"),
        ("Neutral", "Dislike", "Must-have"),
        ("Live with it", "Dislike", "Must-have"),
        ("Neutral", "Neutral", "Indifferent"),
        ("Expect it", "Neutral", "Indifferent"),
        ("Dislike", "Neutral", "Reverse"),
        ("Neutral", "Like", "Reverse"),
        ("Dislike", "Dislike", "Questionable"),
    ]
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / src.name
        shutil.copyfile(src, tmp)
        wb = load_workbook(tmp)
        ws = wb["Kano analysis"]
        for i, (fun, dys, _) in enumerate(KANO):
            ws[f"B{7 + i}"], ws[f"C{7 + i}"] = fun, dys
        wb.save(tmp)
        sol = _engine(tmp).calculate()
        for i, (fun, dys, want) in enumerate(KANO):
            got = _read(sol, src.name, "Kano analysis", f"D{7 + i}")
            check(got == want, f"Kano: {fun} / {dys} classifies as {want}", f"got {got!r}")

    # Pareto: it is sorted by definition. The cumulative used to be a running
    # sum down the rows, which is only a Pareto if the user happens to type
    # their categories in descending order. Type them ascending — the worst
    # case — and the ranked block must still come out ranked.
    src = TEMPLATES / "25-pareto-and-distribution.xlsx"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / src.name
        shutil.copyfile(src, tmp)
        wb = load_workbook(tmp)
        ws = wb["Pareto"]
        ascending = [("Refund timing", 74), ("Proration misunderstood", 96),
                     ("Duplicate charge", 151), ("Wrong plan applied", 233),
                     ("Adjustment not posted at closure", 412)]
        for i, (nm, n) in enumerate(ascending):
            ws.cell(row=5 + i, column=1, value=nm)
            ws.cell(row=5 + i, column=2, value=n)
        wb.save(tmp)
        sol = _engine(tmp).calculate()
        counts = [_read(sol, src.name, "Pareto", f"I{5 + i}") for i in range(5)]
        try:
            nums = [float(c) for c in counts]
        except (TypeError, ValueError):
            nums = []
        check(nums == sorted(nums, reverse=True),
              "Pareto ranks itself even when the categories are typed ascending",
              f"chart plots {nums}")
        check(approx(_read(sol, src.name, "Pareto", "J7"), 0.8240165631469979, 1e-3),
              "Pareto cumulative follows the ranking, not the typing order",
              repr(_read(sol, src.name, "Pareto", "J7")))
        check(approx(_read(sol, src.name, "Pareto", "C29"), 0.8240165631469979, 1e-3),
              "'share explained by the top three' means the top three by rank",
              repr(_read(sol, src.name, "Pareto", "C29")))

    # Every chart that claims a ranking must actually rank. These plotted rows
    # in the order somebody typed them, which makes the reader do the ranking
    # the chart was supposed to do — and on an FMEA, whose whole method is
    # "work the highest RPN first", buries the worst failure mode wherever it
    # happened to be entered.
    for book, sheet, cat_col, val_col, first, n in [
            ("11-cause-effect-xy-matrix.xlsx", "X-Y matrix", "M", "N", 15, 8),
            ("15-solution-selection-matrix.xlsx", "Solution selection", "Q", "R", 14, 6),
            ("12-fmea.xlsx", "FMEA", "V", "W", 11, 6)]:
        src = TEMPLATES / book
        sol = _engine(src).calculate()
        vals = []
        for i in range(n):
            v = _read(sol, book, sheet, f"{val_col}{first + i}")
            try:
                vals.append(float(v))
            except (TypeError, ValueError):
                pass
        check(len(vals) == n and vals == sorted(vals, reverse=True),
              f"{book}: the chart plots its ranking in rank order",
              f"got {vals}")

    # A reference line that contradicts the sheet it sits on destroys trust in
    # the whole file. The FMEA drew its action line at 100 while its own summary
    # counted ">=200 (act now)"; the hypothesis log hardcoded alpha 0.05 while
    # the sheet has a validated alpha input, and keyed the line on the p-value
    # column so it stopped at the last completed test.
    src = TEMPLATES / "12-fmea.xlsx"
    sol = _engine(src).calculate()
    thr = _read(sol, src.name, "FMEA", "D45")
    line = _read(sol, src.name, "FMEA", "Y11")
    check(approx(thr, line), "FMEA: the chart's action line is the sheet's action threshold",
          f"threshold={thr!r} line={line!r}")
    check(approx(_read(sol, src.name, "FMEA", "D40"), 4),
          "FMEA: the count above the threshold follows that same cell",
          repr(_read(sol, src.name, "FMEA", "D40")))

    src = TEMPLATES / "13-hypothesis-test-log.xlsx"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / src.name
        shutil.copyfile(src, tmp)
        wb = load_workbook(tmp)
        wb["Test log"]["B8"] = 0.01          # the user tightens alpha
        wb.save(tmp)
        sol = _engine(tmp).calculate()
        drawn = []
        for r in range(11, 36):
            v = _read(sol, src.name, "Test log", f"T{r}")
            if isinstance(v, (int, float)):
                drawn.append(float(v))
        check(drawn and all(abs(v - 0.01) < 1e-9 for v in drawn),
              "the alpha line follows the alpha the sheet validates",
              f"values {sorted(set(drawn))[:3]}")
        check(len(drawn) >= 20,
              "the alpha line spans the log, not just the rows already filled in",
              f"drawn on {len(drawn)} of 25 rows")

    # A chart must reconcile to the sheet it sits on.
    src = TEMPLATES / "27-control-charts.xlsx"
    sol = _engine(src).calculate()
    lo = float(_read(sol, src.name, "t and g (rare events)", "K14"))
    hi = float(_read(sol, src.name, "t and g (rare events)", "J14"))
    cl = float(_read(sol, src.name, "t and g (rare events)", "L14"))
    check(lo < cl < hi, "t-chart: the centre line sits inside its own limits",
          f"limits {lo:.1f}..{hi:.1f}, centre {cl:.1f}")
    # the limits are built on the transformed scale, so the centre of that
    # construction is the back-transformed mean, not the mean of the raw gaps
    check(not approx(cl, _read(sol, src.name, "t and g (rare events)", "B6"), 1e-3),
          "t-chart: the centre line is the back-transformed centre, not the arithmetic mean")
    ucl = _read(sol, src.name, "t and g (rare events)", "M14")
    check(approx(ucl, _read(sol, src.name, "t and g (rare events)", "B11")),
          "g-chart: the UCL the sheet computes is the UCL the chart plots", repr(ucl))

    # Kano's chart has to account for every class its own classifier returns
    src = TEMPLATES / "23-kano-analysis.xlsx"
    sol = _engine(src).calculate()
    counts = [float(_read(sol, src.name, "Kano analysis", f"D{28 + i}")) for i in range(6)]
    check(sum(counts) == 8,
          "Kano: the summary accounts for every classified row",
          f"classes {counts} sum to {sum(counts)}, example has 8 rows")
    check(counts[4] == 1, "Kano: a Reverse classification is counted, not computed and dropped",
          f"Reverse count {counts[4]}")

    # the control plan's own durability score and its chart must count the
    # same rows, or a control appears on one and not the other
    src = TEMPLATES / "17-control-plan.xlsx"
    sol = _engine(src).calculate()
    total = _read(sol, src.name, "Control plan", "E29")
    feed = sum(float(_read(sol, src.name, "Control plan", f"B{r}")) for r in range(39, 45))
    check(approx(total, feed),
          "control plan: the durability score and the chart count the same rows",
          f"summary {total!r} vs chart feed {feed}")

    # VSM: "% of lead time" must divide by lead time, not by waiting time.
    src = TEMPLATES / "10-value-stream-map.xlsx"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / src.name
        shutil.copyfile(src, tmp)
        wb = load_workbook(tmp)
        ws = wb["Value stream"]
        # same here: wipe the shipped example so the arithmetic is the only
        # thing under test
        for r in range(10, 29):
            for col in "ABCDEFGHIJ":
                ws[f"{col}{r}"] = None
        ws["E10"], ws["F10"] = 10, 90       # touch 10, wait 90 -> lead 100
        ws["B44"], ws["B45"] = 60, 30
        wb.save(tmp)
        sol = _engine(tmp).calculate()
        lead = _read(sol, src.name, "Value stream", "E33")
        c44 = _read(sol, src.name, "Value stream", "C44")
        check(approx(lead, 100), "VSM: lead time = touch + wait", repr(lead))
        check(approx(c44, 0.60), "VSM: waiting state is a share of lead time, not of waiting time",
              f"got {c44!r}, want 0.60 (0.667 would mean it still divides by waiting time)")


# --------------------------------------------------------------------- SYNC
def test_sync() -> None:
    src = HTML.read_text(encoding="utf-8")
    _, _, tpls = extract_tpls(src)
    check(len(tpls) == 27, f"27 templates registered (found {len(tpls)})")

    exts = [e.get("ext") for e in tpls.values()]
    check(exts.count("xlsx") == 16, f"16 Excel workbooks (found {exts.count('xlsx')})")
    check(exts.count("md") == 11, f"11 Markdown templates (found {exts.count('md')})")

    for slug, entry in tpls.items():
        path = TEMPLATES / entry["file"]
        check(path.exists(), f"{entry['file']} exists on disk")
        if not path.exists():
            continue
        if entry.get("ext") == "xlsx":
            want = base64.b64encode(path.read_bytes()).decode("ascii")
            check(entry.get("b64") == want, f"{entry['file']}: embedded base64 matches the file on disk")
            _check_preview(entry, path)
        else:
            check(entry.get("content") == path.read_text(encoding="utf-8"),
                  f"{entry['file']}: embedded markdown matches the file on disk")

    check(HTML.read_bytes() == DOCS.read_bytes(), "docs/index.html is identical to the root HTML")

    # Version: the meta tag and the sidebar badge must agree, so a deploy can be
    # identified without opening the page. The release notes themselves live in
    # CHANGELOG.md — a reader who has just opened the document should not have to
    # scroll past its maintenance history — but the newest entry there has to
    # match what the page claims to be.
    meta = re.search(r'<meta name="app-version" content="([0-9.]+)"', src)
    badge = re.search(r"Customer Support Operations &middot; v([0-9.]+)", src)
    check(bool(meta), "an <meta name=\"app-version\"> tag is present")
    check(bool(badge), "the sidebar shows a version")
    check(not re.search(r'<div class="t">(New )?[Ii]n v[0-9.]+ &mdash;', src),
          "release notes are not in the product — they belong in CHANGELOG.md")
    changelog = ROOT / "CHANGELOG.md"
    check(changelog.exists(), "CHANGELOG.md exists")
    if changelog.exists():
        notes = re.findall(r"^## (?:New in )?v?([0-9.]+)", changelog.read_text(encoding="utf-8"), re.M)
        check(bool(notes), "CHANGELOG.md has at least one release entry")
        if meta and badge and notes:
            newest = max(notes, key=lambda v: [int(p) for p in v.split(".")])
            check(meta.group(1) == badge.group(1) == newest,
                  "meta tag, sidebar badge and CHANGELOG agree on the version",
                  f"meta={meta.group(1)} sidebar={badge.group(1)} changelog={newest}")
    # The glossary explainer must outrank every dialog. It renders inside the
    # template preview, the export dialog and the download menu, and at a lower
    # z-index it opens behind them where nobody can read it.
    zs = {}
    for zm in re.finditer(r"z-index\s*:\s*(\d+)", src):
        a, b = src.rfind("}", 0, zm.start()), src.rfind("{", 0, zm.start())
        zs[src[a + 1:b].strip().split()[-1]] = int(zm.group(1))
    pop = zs.get("#pop", 0)
    over = {k: v for k, v in zs.items() if k != "#pop" and v >= pop and k != ".skiplink"}
    check(pop > 0 and not over,
          "the glossary explainer sits above every dialog",
          f"#pop={pop} but these are at or above it: {over}")

    # Every template card must be a direct child of .tplgrid. Cards nested one
    # level deeper still render, but the CSS grid only lays out its own
    # children, so the whole section collapses into a single narrow column.
    g0 = src.index('<div class="tplgrid">')
    depth, j = 0, g0
    while j < len(src):
        if src.startswith("<div", j):
            depth += 1
        elif src.startswith("</div>", j):
            depth -= 1
            if depth == 0:
                break
        j += 1
    grid = src[g0:j]
    total_cards = src.count('class="tplc"')
    check(grid.count('class="tplc"') == total_cards,
          "every template card is a direct child of the grid",
          f"{grid.count('class=\"tplc\"')} of {total_cards} inside .tplgrid — the rest are nested")
    check(total_cards == len(tpls),
          f"a card for every registered template ({len(tpls)})", f"cards={total_cards}")

    # Nested explainers. An explainer that leans on three more undefined terms
    # is not an explanation, so #pop is glossed too — which needs a self-link
    # guard, a back trail, and one code path for pointer and keyboard. Enter
    # used to navigate without recording the trail, so the back button never
    # appeared for keyboard users.
    check("function openTerm(" in src, "pointer and keyboard share one openTerm() path")
    # "openTerm(g);" with the semicolon, so the definition itself is not counted
    check(src.count("openTerm(g);") == 2,
          "both the click and the keydown handler go through openTerm()",
          f"found {src.count('openTerm(g);')} call sites")
    check("autoGloss(pop, key)" in src, "the explainer's own text is glossed")
    check("if(selfKey && key === selfKey) continue;" in src,
          "an explainer never links to the term it is explaining")
    check("n.id==='pop'&&!POP_OPEN" in src,
          "#pop is glossed only when showPop asks, not on document-wide passes")
    check(src.count("POP_TRAIL.length = 0") >= 2,
          "the back trail is cleared when the explainer closes and on a fresh term")

    # Case. The matcher is deliberately case-sensitive — an "i" flag would let
    # short acronyms swallow ordinary words (IT, OR, US, AND). But ordinary-word
    # terms are routinely written lower-case mid-sentence, and those matched
    # nothing at all: "gemba" appears more often in this document than "Gemba"
    # did, and only the capitalised form was ever clickable.
    check("if(/^[A-Z0-9][A-Z0-9'\\u2032&-]{1,7}$/.test(t)) return;" in src,
          "acronym-shaped terms get no lower-case variant, so IT/OR/US stay safe")
    check("var lower = t.charAt(0).toLowerCase() + t.slice(1);" in src,
          "word-shaped glossary terms also match when written lower-case")
    for term in ("Gemba", "Kaizen", "Poka-yoke"):
        check(f'"{term}"' in src, f"{term} is still a glossary entry")

    # The eleven markdown templates shipped as well-structured blank forms with
    # nothing telling a first-time user what a good answer looks like, while
    # every workbook opened with a how-to tab and a worked example row. They
    # carry the same now.
    for md in sorted(TEMPLATES.glob("*.md")):
        body = md.read_text(encoding="utf-8")
        check("## How to use this" in body,
              f"{md.name}: has a how-to block")
        check("**The mistake this prevents.**" in body,
              f"{md.name}: names the mistake it prevents")
        check(body.count("*") > 6,
              f"{md.name}: carries a worked example", "no italic example entries found")

    for dead in ("parseCSV", "renderCSV"):
        check(dead not in src, f"dead {dead}() removed")
    check("function esc2(" in src, "esc2() retained (renderMD depends on it)")
    check(src.count("-year net<") == 0 and "'-year NPV</th>" in src,
          "wizard sensitivity column is labelled NPV, not 'net'")


def _check_preview(entry: dict, path: Path) -> None:
    wb = load_workbook(path)
    bad = []
    seen = 0
    for m in RE_SHEET.finditer(entry["preview"]):
        ws = wb.worksheets[int(m.group(2))]
        held: dict[int, set[int]] = {}      # columns claimed by an earlier rowspan
        for r, rm in enumerate(RE_ROW.finditer(m.group(3)), start=1):
            col = 1
            for tm in RE_TD.finditer(rm.group(2)):
                attrs = tm.group(1)
                cs = re.search(r'colspan="(\d+)"', attrs)
                rs = re.search(r'rowspan="(\d+)"', attrs)
                ti = re.search(r'title="([^"]*)"', attrs)
                nc = int(cs.group(1)) if cs else 1
                nr = int(rs.group(1)) if rs else 1
                while col in held.get(r, ()):
                    col += 1
                cell = ws.cell(row=r, column=col)
                if nr > 1:
                    for rr in range(r + 1, r + nr):
                        held.setdefault(rr, set()).update(range(col, col + nc))
                col += nc
                wf = cell.value if isinstance(cell.value, str) and cell.value.startswith("=") else None
                pf = H.unescape(ti.group(1)) if ti else None
                if pf or wf:
                    seen += 1
                    if pf != wf:
                        bad.append(f"[{ws.title}] {cell.coordinate}: preview={pf!r} workbook={wf!r}")
    check(not bad, f"{path.name}: all {seen} preview tooltips match the workbook", "\n      ".join(bad[:4]))


# ------------------------------------------------------------------- EXPORT
# The business case is generated in the browser: an email-safe HTML rendering
# and a real .xlsx with live formulas and native charts. These tests pull the
# shipped JavaScript straight out of the HTML, run it under node, and check the
# workbook it produces actually recalculates to the numbers the page showed.

JS_START = "/* ============================================================ xlsx writer"
# Stop before the docx writer: everything after it needs a live DOM, which node
# has no business providing. The docx package is validated in the browser
# instead, by parsing its own ZIP with DOMParser.
JS_END = "/* ============================================================ docx writer"

# Each problem archetype emits a different benefit model, so the row the gross
# value lands on shifts. Every branch gets generated and recalculated.
GROSS_ROW = {"rate": 5, "volume": 4, "aht": 5, "shrink": 6,
             "deflect": 5, "attrition": 5, "copq": 5, "churn": 5}

HARNESS = r"""
const fs=require('fs');
global.fm=function(n,d){ if(n===undefined||n===null||!isFinite(n)) return '—';
  d=(d===undefined)?0:d;
  return Number(n).toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d}); };
eval(fs.readFileSync(process.argv[2],'utf8'));
const outDir=process.argv[3];
const base={vol:480000,cpc:6.8,rate:14.0,hr:38,occ:82,aht:420,ahtsave:14,agents:120,shrink:32,
  shrinktgt:28,target:8.0,harvest:'reduce',realz:80,
  deflrate:35,cpcnew:0.35,attr:38,attrtgt:30,replcost:9500,incidentcost:85,ltv:1400,
  bbmonths:9,bbcost:120000,training:35000,eng:60000,tooling:8000,years:3,disc:10};
const kinds=[
 {kind:'rate',   n:'Reduce rework and reopens',  metric:'Reopen rate',        gross:480000*0.06*6.8},
 {kind:'volume', n:'Eliminate a contact driver', metric:'Contacts per year',
  V:{rate:40000,target:8000},                                                 gross:(40000-8000)*6.8},
 {kind:'aht',    n:'Reduce handle time',         metric:'Average handle time',gross:480000*14/3600/0.82*38},
 {kind:'shrink', n:'Recover shrinkage capacity', metric:'Shrinkage %',        gross:120*1760*0.04*38},
 {kind:'deflect',  n:'Deflect to self-service',  metric:'Share deflected',
  gross:480000*0.35*(6.8-0.35)},
 {kind:'attrition',n:'Reduce agent attrition',   metric:'Annual attrition',
  gross:120*0.08*9500},
 {kind:'copq',     n:'Cut the cost of poor quality', metric:'Incident rate',
  gross:480000*0.06*85},
 {kind:'churn',    n:'Protect revenue at risk',  metric:'Churn rate',
  gross:480000*0.06*1400}
];
const meta={};
for(const k of kinds){
  const V=Object.assign({},base,k.V||{});
  const gross=k.gross, real=gross*0.8, inv=120000*0.75+35000+60000+8000;
  let npv=-inv; for(let y=1;y<=3;y++) npv+=real/Math.pow(1.1,y);
  const m={gross,real,inv,npv,pb:inv/real,roi:(real*3-inv)/inv,fte:1,realz:0.8,
    detail:[['Improvement','a → b','6.0 pts']]};
  const a={n:k.n,d:'desc',metric:k.metric,kind:k.kind};
  const ctx={m,V,S:{arch:k.kind},a};
  fs.writeFileSync(outDir+'/'+k.kind+'.xlsx', Buffer.from(bizXlsx(ctx)));
  meta[k.kind]={gross,real,inv,npv,html:bizHTML(ctx).length};
}
fs.writeFileSync(outDir+'/meta.json', JSON.stringify(meta));
"""


def test_export() -> None:
    import subprocess

    src = HTML.read_text(encoding="utf-8")
    check("business-case.md" not in src, "markdown business case replaced by HTML/Excel")
    check("  function doc(){" not in src, "old markdown generator removed")
    for needed in ("var XLSX = (function(){", "var DOCX = (function(){",
                   "function bizXlsx(", "function bizHTML(",
                   "function openExport(", "function tplEmailHTML(", 'id="expCopy"',
                   "function showFmtMenu(", "function dlTemplateAs(",
                   # the template modal's button is created at runtime, not in the markup
                   "b.id = 'tplEmail'", "fullCalcOnLoad",
                   "wordprocessingml.document.main+xml"):
        check(needed in src, f"export code present: {needed}")

    # Download must offer a format rather than pushing a .md at everyone.
    # (Markdown is still *available* from the menu - it just isn't the default.)
    check("""if(t.ext==='xlsx'){
    dlBlob(t.file, b64ToBlob(t.b64,""" not in src,
          "old markdown-by-default download path removed")
    check("dlTemplateAs(slug, t.ext==='xlsx' ? 'xlsx' : 'docx')" in src,
          "bulk download defaults to Excel for workbooks and Word for documents")
    for fmt in ("'docx'", "'html'"):
        check(fmt in src, f"format menu offers {fmt}")
    # Markdown is a developer format; this audience gets Word and HTML only.
    check("'text/markdown'" not in src, "Markdown is no longer offered as a download")
    check("['md','Markdown'" not in src, "Markdown removed from the format menu")

    if JS_START not in src or JS_END not in src:
        check(False, "export JS block markers found in the HTML")
        return
    js = src[src.index(JS_START):src.index(JS_END)]

    if not shutil.which("node"):
        print("           node not found - skipping the generated-workbook test")
        return

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "bundle.js").write_text(js, encoding="utf-8")
        (d / "run.js").write_text(HARNESS, encoding="utf-8")
        r = subprocess.run(["node", str(d / "run.js"), str(d / "bundle.js"), str(d)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            check(False, "business case workbook generates without error", r.stderr.strip()[:400])
            return
        check(True, "business case workbook generates under node for every archetype")
        meta = json.loads((d / "meta.json").read_text())

        import zipfile
        import xml.etree.ElementTree as ET

        try:
            import formulas  # noqa: F401
            can_calc = True
        except ImportError:
            can_calc = False
            print("           formulas not installed - skipping workbook recalculation")

        for kind, e in meta.items():
            path = d / (kind + ".xlsx")
            check(e["html"] > 8000, f"{kind}: business case HTML renders ({e['html']} chars)")

            z = zipfile.ZipFile(path)
            names = set(z.namelist())
            broken = []
            for n in names:
                if n.endswith((".xml", ".rels")):
                    try:
                        ET.fromstring(z.read(n))
                    except Exception as ex:
                        broken.append(f"{n}: {ex}")
            check(not broken, f"{kind}: every xlsx part is well-formed XML", "; ".join(broken[:2]))
            charts = [n for n in names if "/charts/chart" in n]
            check(len(charts) == 4, f"{kind}: workbook carries all 4 charts (found {len(charts)})")
            ct = ET.fromstring(z.read("[Content_Types].xml"))
            ovr = {o.get("PartName") for o in ct if o.tag.endswith("Override")}
            missing = [n for n in names if not n.endswith(".rels")
                       and n != "[Content_Types].xml" and "/" + n not in ovr]
            check(not missing, f"{kind}: every xlsx part has a content type", ", ".join(missing[:3]))

            wb = load_workbook(path)
            check(wb.sheetnames == ["Business case", "Inputs", "Benefit model",
                                    "Financials", "Sensitivity"],
                  f"{kind}: workbook sheet layout", str(wb.sheetnames))

            if not can_calc:
                continue
            sol = _engine(path).calculate()
            gr = GROSS_ROW[kind]
            for label, sheet, cell, want in [
                ("gross annual value", "Benefit model", f"B{gr}", e["gross"]),
                ("realised annual benefit", "Benefit model", f"B{gr + 2}", e["real"]),
                ("total investment", "Financials", "B7", e["inv"]),
                ("net present value", "Financials", "B13", e["npv"]),
                ("cover sheet cross-reference", "Business case", "B9", e["real"]),
                ("base-case sensitivity NPV", "Sensitivity", "D5", e["npv"]),
            ]:
                got = _read(sol, path.name, sheet, cell)
                check(approx(got, want, 1e-6), f"{kind}: workbook recalculates the {label}",
                      f"got {got!r} want {want}")


# --------------------------------------------------------------------- A11Y
def test_a11y() -> None:
    """Guard the accessibility and compatibility fixes from silently regressing."""
    src = HTML.read_text(encoding="utf-8")

    # A regex lookbehind throws a SyntaxError at construction on Safari < 16.4,
    # which would abort the whole script block - taking the formula cards, the
    # wizard, the template previews and every download with it.
    check("(?<!" not in src,
          "no regex lookbehind (it aborts the entire script on Safari < 16.4)")
    check("(^|[^\\\\w-])(" in src, "glossary regex uses the portable leading-capture form")

    # The glossary terms carry tabindex, so they must be operable from a keyboard.
    check("if(e.key !== 'Enter' && e.key !== ' ' && e.key !== 'Spacebar') return;" in src,
          "glossary terms respond to Enter and Space, not just a mouse click")
    check("s.setAttribute('role','button')" in src, "glossary terms expose a button role")
    check("s.setAttribute('aria-label'" in src, "glossary terms carry an accessible name")
    check("back.focus()" in src, "closing the explainer returns focus to the term that opened it")

    # Both modals should announce themselves.
    check(src.count('aria-modal="true"') + src.count("m.setAttribute('aria-modal','true')") >= 2,
          "both dialogs are marked aria-modal")
    check('<div id="tplPrev" role="dialog"' in src, "template preview is a labelled dialog")

    check('class="skiplink"' in src, "a skip-to-content link exists for keyboard users")
    check("prefers-reduced-motion" in src, "the page honours prefers-reduced-motion")
    check("behavior:'smooth'" not in src,
          "scripted scrolls go through SCROLL_BEHAVIOR rather than hardcoding smooth")
    check(":focus-visible" in src, "a visible focus ring is defined")


JARGON = [
    # Terms that were used in the prose with no explainer behind them. If any of
    # these stops resolving, the page is talking jargon at people again.
    "Six Sigma", "Lean", "DMADV", "PDCA", "TQM", "QA", "ASQ", "IASSC", "CSSBB", "BOK",
    "SOP", "KB", "WFM", "CRM", "ACD", "IVR", "ETL", "ROI", "KPI", "SME", "DOE", "EVOP",
    "RACI", "SCAMPER", "TRIZ", "ADKAR", "QFD", "Non-parametric", "Parametric",
    "Transformation", "Normality", "Skew", "Poisson", "Binomial", "Exponential",
    "Hypothesis test", "Null hypothesis", "Type I error", "Type II error", "Sample size",
    "Statistical significance", "Welch", "Wilcoxon", "Tukey", "Levene", "Post-hoc",
    "Bonferroni", "Independence", "Clustering", "Poisson regression", "Negative binomial",
    "Offset", "Control chart", "Control limits", "Special cause", "Common cause",
    "Rational subgrouping", "I-MR", "Moving range", "p-chart", "u-chart", "g-chart",
    "t-chart", "Nelson rules", "Capability", "Cpu", "Pp", "USL", "LSL", "Z-score",
    "Attribute agreement", "Repeatability", "Reproducibility", "Bias", "Linearity",
    "Mix shift", "Operational definition", "Value stream", "Cycle time", "Lead time",
    "Touch time", "Queue time", "Kanban", "Backlog", "Deflection", "Tier 2",
    "Disposition code", "After-call work", "Concurrency", "Intraday", "Async",
    "Schedule adherence", "Forecast accuracy", "Queue discipline", "Swivel-chair",
    "Discount rate", "Soft savings", "Loaded cost", "Charter", "Control plan", "Kano",
    "Pugh", "Multiple regression", "Residual", "Multicollinearity", "Holdout",
    "Histogram", "Boxplot", "Run chart", "Pareto chart", "Percentile",
    "Standard deviation", "Variance", "Changeover", "Pull system", "Bottleneck",
]


def test_glossary() -> None:
    """No term should be used in the prose without an explainer behind it."""
    src = HTML.read_text(encoding="utf-8")
    gl = src[src.index("const GLOSS="):src.index("/* ================================================================ helpers */")]
    missing = [t for t in JARGON if f'"{t}":{{' not in gl and f"'{t}'" not in gl and f'"{t}"' not in gl]
    check(not missing, f"every audited term has a glossary entry ({len(JARGON)} checked)",
          "undefined: " + ", ".join(missing[:8]))

    # The A-Z index used to be hand-written and drifted 148 entries behind GLOSS.
    check("listEl.innerHTML = Object.keys(GLOSS)" in src,
          "the glossary index is generated from GLOSS, not hand-maintained")
    # Anything rendered after load starts with no links unless it is re-glossed.
    check(src.count("window.reGloss(") >= 5,
          f"dynamic surfaces are re-glossed (found {src.count('window.reGloss(')} call sites)")
    check("<pre id=\"tplBody\">" not in src,
          "template preview is not a <pre> (PRE is skipped, so it could never gloss)")
    check("t + 's?'" in src, "acronym plurals (SLAs, CTQs) resolve to the singular entry")
    # Test-selector results must not be dead ends.
    check("function resultLinks(" in src and "var R_TOOL={" in src,
          "statistical test results link to a tool and a template")

    # A one-character alias links every stray capital letter on the page; "Z"
    # for Z-score did exactly that. The runtime guard drops anything shorter
    # than two characters and de-duplicates aliases added by separate batches.
    check("if(a.length<2) return;" in src,
          "single-character glossary aliases are rejected at runtime")
    check("seen[a.toLowerCase()]=1" in src, "duplicate aliases are collapsed")

    # NOAUTO suppresses a term from being linked inline. It had grown to 21
    # entries and was quietly hiding t-test, ANOVA, Chi-square, Kappa, Gemba, A3
    # and Tollgate from the prose entirely. Keep it small and deliberate.
    noauto = re.search(r"var NOAUTO = \{([^}]*)\}", src)
    check(bool(noauto), "NOAUTO list is present")
    if noauto:
        n = len(re.findall(r"'[^']+':1", noauto.group(1)))
        check(n <= 10, f"NOAUTO stays short ({n} terms) so technical terms remain clickable")
        for t in ("'t-test'", "'ANOVA'", "'Chi-square'", "'Kappa'", "'Tollgate'", "'Gemba'"):
            check(t not in noauto.group(1), f"{t} is not suppressed from the prose")
    # Ordinary verbs must not be registered as synonyms for Lean vocabulary.
    for bad in ('"Pull","Push"', '"Paired data","Matched"'):
        check(bad not in src, f"no common-verb alias: {bad}")
    check('"P&L":{' in src, "P&L is defined")


def test_toollib() -> None:
    """The tool library's navigation aids, and that nothing dangles."""
    src = HTML.read_text(encoding="utf-8")

    names = re.findall(r'<span class="tn">([^<]*)</span>', src)
    check(len(names) == 52, f"52 tools present (found {len(names)})")

    # Every tool the picker recommends must exist under exactly that name, or the
    # picker renders a gap and the user hits a dead end.
    # PHKEY exists in both tool modules, so anchor the end of the block *after*
    # PICK starts or the slice runs backwards and silently matches nothing.
    p0 = src.index("var PICK=[")
    p1 = src.index("var PHKEY=", p0)
    block = src[p0:p1]
    # Scan both quote styles in one left-to-right pass. A single-quote-only regex
    # desynchronises on "Levene's test (...)" - the apostrophe inside a
    # double-quoted string reads as an opening quote and shifts every match after it.
    picked = set()
    for arr in re.findall(r"tools:\[(.*?)\]", block, re.S):
        for a, b in re.findall(r"'([^']*)'|\"([^\"]*)\"", arr):
            picked.add(a or b)
    missing = [n for n in names if n not in picked]
    check(not missing, f"every tool is reachable from the picker",
          "unreachable: " + ", ".join(missing[:5]))

    # Tool -> calculator links must point at formula cards that exist.
    calc_ids = set(re.findall(r'\{id:"([a-z]+)",group:', src))
    linked = set(re.findall(r"^\s*([a-z]+):\['([a-z',]+)'\],?$", src, re.M))
    referenced = set()
    blk = src[src.index("var TOOL_CALC={"):src.index("var CALC_NAME=")]
    for grp in re.findall(r"\[([^\]]+)\]", blk):
        referenced |= {x.strip().strip("'") for x in grp.split(",")}
    check(referenced and referenced <= calc_ids,
          "every tool->calculator link points at a real formula card",
          f"dangling: {sorted(referenced - calc_ids)}")
    check("card.id = 'fml-'+f.id" in src, "formula cards carry anchors for those links")

    for needed in ("function slugify(", "'tgroup p-'", "id=\"tExpand\"", "id=\"tReset\"",
                   "'tempty'", "mark.thit", "id=\"toolPick\"", "openFromHash",
                   "idx.className='tindex'", "className='fmlback'", "window.__gotoTool"):
        check(needed in src, f"tool library affordance present: {needed}")

    # Every formula card should name the tool that explains its method, so the
    # link runs both ways instead of stranding the reader in the arithmetic.
    card_ids = set(re.findall(r'\{id:"([a-z]+)",group:', src))
    linked_back = set()
    blk = src[src.index("var TOOL_CALC={"):src.index("var CALC_NAME=")]
    for grp in re.findall(r"\[([^\]]+)\]", blk):
        linked_back |= {x.strip().strip("'") for x in grp.split(",")}
    orphans = sorted(card_ids - linked_back)
    check(not orphans, "every formula card links back to a tool",
          f"no backlink for: {orphans}")

    # Finance is told they can check the maths in the workbook, so every chart
    # drawn in the HTML case must have a counterpart bound to cells in the Excel.
    html_charts = re.findall(r"emBar\(\{title:'([^']*)'", src)
    xl_charts = re.findall(r"type:'(?:col|bar|line)', title:'([^']*)'", src)
    check(len(html_charts) == len(xl_charts) and len(html_charts) == 4,
          f"every on-screen chart has an Excel counterpart "
          f"({len(html_charts)} in HTML, {len(xl_charts)} in Excel)",
          f"HTML={html_charts} XL={xl_charts}")


# --------------------------------------------------------------------- main
def main() -> int:
    fast = "--fast" in sys.argv
    print("STRUCTURE  merged-cell reference audit")
    test_structure()
    print("SYNC       four-way template consistency")
    test_sync()
    print("A11Y       keyboard, dialogs and browser compatibility")
    test_a11y()
    print("TOOLS      library navigation, picker and calculator links")
    test_toollib()
    print("GLOSSARY   jargon coverage and dynamic linking")
    test_glossary()
    print("EXPORT     business case HTML + live-formula workbook")
    test_export()
    if fast:
        print("NUMERIC    skipped (--fast)")
    else:
        try:
            import formulas  # noqa: F401
        except ImportError:
            print("NUMERIC    SKIPPED - pip install formulas to run the recalculation tests")
        else:
            print("NUMERIC    recalculating fixed formulas")
            test_numeric()
            test_numeric_other()

    print()
    if FAILURES:
        print(f"FAILED  {len(FAILURES)} check(s), {PASSES[0]} passed\n")
        for f in FAILURES:
            print("  x " + f)
        return 1
    print(f"PASSED  all {PASSES[0]} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
