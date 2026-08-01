#!/usr/bin/env python3
"""Enforce the chart quality bar described in CHART-QA.md.

Three gates and three scores per chart. The gates are pass/fail; the scores have
a shipping bar near the top of each, because a chart that merely plots the data
is not worth downloading a template for.

    python3 tools/qa_templates.py --rubric        # the scorecard

Grading reads the chart XML out of the .xlsx rather than openpyxl's object
model. openpyxl's reader keeps only the first chart type in a combo, so a bar
chart with a reference line laid over it reads back as a plain bar chart — the
file is correct and the in-memory view is not. The file is what ships, so the
file is what gets graded.
"""
from __future__ import annotations

import re
import zipfile
from xml.etree import ElementTree as ET

from openpyxl.utils import range_boundaries

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xlpolish import AXIS_CHARS                                  # noqa: E402

C = "{http://schemas.openxmlformats.org/drawingml/2006/chart}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

TREND, RANK, COMPARE, STEPS = "trend", "rank", "compare", "steps"
BEFORE_AFTER, RELATION, THRESHOLD, SHAPE = "before_after", "relation", "threshold", "shape"

QUESTION_FORM = {
    TREND: ("line",), RANK: ("bar",), COMPARE: ("bar",), STEPS: ("bar",),
    BEFORE_AFTER: ("bar",), RELATION: ("scatter",), THRESHOLD: ("line",),
    SHAPE: ("line", "bar", "area"),
}

INTENT = {
    ("05-data-collection-plan.xlsx", "Sample size against"): SHAPE,
    ("10-value-stream-map.xlsx", "Where the time actually goes"): STEPS,
    ("11-cause-effect-xy-matrix.xlsx", "Weighted total by candidate"): RANK,
    ("12-fmea.xlsx", "Risk priority number"): BEFORE_AFTER,
    ("13-hypothesis-test-log.xlsx", "p-value by test"): THRESHOLD,
    ("15-solution-selection-matrix.xlsx", "Weighted score by solution"): RANK,
    ("17-control-plan.xlsx", "Controls by level"): RANK,
    ("19-black-belt-calculators.xlsx", "DPMO — you against"): COMPARE,
    ("19-black-belt-calculators.xlsx", "Cohen's kappa against"): COMPARE,
    ("19-black-belt-calculators.xlsx", "Where you sit against the SLA"): SHAPE,
    ("19-black-belt-calculators.xlsx", "Lead time in days"): COMPARE,
    ("19-black-belt-calculators.xlsx", "Open tickets against"): COMPARE,
    ("19-black-belt-calculators.xlsx", "Minutes of work against"): COMPARE,
    ("19-black-belt-calculators.xlsx", "From offered load"): COMPARE,
    ("19-black-belt-calculators.xlsx", "Gross value against"): COMPARE,
    ("19-black-belt-calculators.xlsx", "Cumulative discounted position"): THRESHOLD,
    ("21-cause-effect-fishbone.xlsx", "Causes per branch"): RANK,
    ("22-stakeholder-and-raci.xlsx", "Stakeholder map"): RELATION,
    ("23-kano-analysis.xlsx", "Where your requirements fall"): RANK,
    ("24-doe-design-matrix.xlsx", "Effect size"): RANK,
    ("25-pareto-and-distribution.xlsx", "Pareto —"): RANK,
    ("25-pareto-and-distribution.xlsx", "Mean, median and p90"): COMPARE,
    ("28-erlang-staffing.xlsx", "Service level against agents"): THRESHOLD,
    ("26-kanban-and-wip.xlsx", "Where you are against"): COMPARE,
    ("27-control-charts.xlsx", "Individuals —"): TREND,
    ("27-control-charts.xlsx", "Moving range —"): TREND,
    ("27-control-charts.xlsx", "Laney p"): TREND,
    ("27-control-charts.xlsx", "Laney u"): TREND,
    ("27-control-charts.xlsx", "Xbar —"): TREND,
    ("27-control-charts.xlsx", "R — is the spread"): TREND,
    ("27-control-charts.xlsx", "EWMA —"): TREND,
    ("27-control-charts.xlsx", "CUSUM —"): TREND,
    ("27-control-charts.xlsx", "t-chart —"): TREND,
    ("27-control-charts.xlsx", "g-chart —"): TREND,
}

# A series whose name marks it as the standard brought to the data, rather than
# the data itself. This is where most of a template's value actually sits.
REFERENCE = re.compile(
    r"(ucl|lcl|centre line|center line|limit|target|alpha|breakeven|threshold|"
    r"benchmark|average|mean|cap|promised|acceptable|unusable|usual choice|"
    r"act above|80%|noise floor|quadrant|sigma)", re.I)

CONCLUSIVE = re.compile(r"[—?]|against|is the|which|where|how much|did it|actually",
                        re.IGNORECASE)

PLOT_KINDS = {"barChart": "bar", "lineChart": "line", "scatterChart": "scatter",
              "areaChart": "area", "pieChart": "pie", "bubbleChart": "bubble"}


def _text(el) -> str:
    return "".join(t.text or "" for t in el.iter(A + "t")) if el is not None else ""


def _parse(xml: bytes) -> dict:
    root = ET.fromstring(xml)
    plot = root.find(f"{C}chart/{C}plotArea")
    out = {
        "title": _text(root.find(f"{C}chart/{C}title")).strip(),
        "kinds": [], "series": [], "grouping": None,
        "legend": root.find(f"{C}chart/{C}legend") is not None,
        "axes": [], "labels": None,
    }
    for node in list(plot or []):
        tag = node.tag[len(C):]
        if tag in ("valAx", "catAx"):
            sc = node.find(f"{C}scaling")
            mn = sc.find(f"{C}min") if sc is not None else None
            mx = sc.find(f"{C}max") if sc is not None else None
            dl = node.find(f"{C}delete")
            sk = node.find(f"{C}tickLblSkip")
            out["axes"].append({
                "kind": tag,
                "deleted": dl is None or dl.get("val") not in ("0", "false"),
                "min": mn.get("val") if mn is not None else None,
                "max": mx.get("val") if mx is not None else None,
                "skip": sk.get("val") if sk is not None else None,
            })
            continue
        if tag not in PLOT_KINDS:
            continue
        out["kinds"].append(PLOT_KINDS[tag])
        grp = node.find(f"{C}grouping")
        if grp is not None and out["grouping"] is None:
            out["grouping"] = grp.get("val")
        dlb = node.find(f"{C}dLbls")
        if dlb is not None and out["labels"] is None:
            out["labels"] = {}
            for t in ("showVal", "showCatName", "showSerName", "showLegendKey"):
                e = dlb.find(C + t)
                out["labels"][t] = e is not None and e.get("val") in ("1", "true")
        for ser in node.findall(f"{C}ser"):
            tx = ser.find(f"{C}tx")
            name = ""
            if tx is not None:
                v = tx.find(f"{C}v")
                name = (v.text if v is not None and v.text else "") or _text(tx)
            val = ser.find(f"{C}val/{C}numRef/{C}f")
            if val is None:
                val = ser.find(f"{C}yVal/{C}numRef/{C}f")
            spPr = ser.find(f"{C}spPr")
            coloured = spPr is not None and spPr.find(f".//{A}solidFill") is not None
            marker = ser.find(f"{C}marker/{C}spPr")
            if marker is not None and marker.find(f".//{A}solidFill") is not None:
                coloured = True
            cat = ser.find(f"{C}cat/{C}numRef/{C}f")
            if cat is None:
                cat = ser.find(f"{C}cat/{C}strRef/{C}f")
            out["series"].append({
                "name": name, "ref": val.text if val is not None else None,
                "cat": cat.text if cat is not None else None,
                "coloured": coloured, "points": len(ser.findall(f"{C}dPt")),
                "kind": PLOT_KINDS[tag],
            })
    return out


def charts_in(path) -> list[dict]:
    """Every chart in the workbook, as it will actually be rendered."""
    out = []
    with zipfile.ZipFile(path) as z:
        for name in sorted(n for n in z.namelist()
                           if re.match(r"xl/charts/chart\d+\.xml$", n)):
            out.append(_parse(z.read(name)))
    return out


def _cells(wb, ref):
    m = re.match(r"^'?([^'!]+)'?!(.+)$", (ref or "").strip())
    if not m or m.group(1) not in wb.sheetnames:
        return []
    ws = wb[m.group(1)]
    try:
        c1, r1, c2, r2 = range_boundaries(m.group(2).replace("$", ""))
    except Exception:                                            # noqa: BLE001
        return []
    return [ws.cell(row=r, column=c) for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]


def _labels_of(wb, ref) -> list[str]:
    """The category labels a ref actually holds — blanks dropped, like Excel."""
    out = []
    for c in _cells(wb, ref):
        v = c.value
        if v in (None, ""):
            continue
        out.append("______" if isinstance(v, str) and v.startswith("=") else str(v))
    return out


def _shadow(ws):
    out = set()
    for rng in ws.merged_cells.ranges:
        c1, r1, c2, r2 = range_boundaries(str(rng))
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                if (r, c) != (r1, c1):
                    out.add((r, c))
    return out


def grade(book: str, ch: dict, wb) -> dict:
    title, kinds, sers = ch["title"], ch["kinds"], ch["series"]
    n = len(sers)
    notes: list[str] = []
    intent = next((v for (b, p), v in INTENT.items()
                   if b == book and title.startswith(p)), None)

    # ---- Gate 2: right form for the question -----------------------------
    primary = kinds[0] if kinds else "?"
    if intent is None:
        right_chart = False
        notes.append("no declared intent — add it to INTENT so the form can be checked")
    else:
        right_chart = primary in QUESTION_FORM[intent]
        if not right_chart:
            notes.append(f"{intent} questions are answered by "
                         f"{'/'.join(QUESTION_FORM[intent])}, this is {primary}")
        if intent == STEPS and ch["grouping"] != "stacked":
            right_chart = False
            notes.append("a step breakdown must be stacked or the parts do not add up")
        if intent == BEFORE_AFTER and len([s for s in sers if s["kind"] == "bar"]) != 2:
            right_chart = False
            notes.append("before/after needs exactly two bar series")

    # ---- Gate 3: readable -------------------------------------------------
    readable = True
    if not title:
        readable = False
        notes.append("no title")
    elif not CONCLUSIVE.search(title):
        readable = False
        notes.append(f"title captions rather than concludes: {title!r}")
    for ax in ch["axes"]:
        if ax["deleted"]:
            readable = False
            notes.append(f"{ax['kind']} is hidden")
    longest = max((len(_cells(wb, s["ref"])) for s in sers), default=0)
    if primary != "scatter":
        val_ax = next((a for a in ch["axes"] if a["kind"] == "valAx"), None)
        vals = [c.value for s in sers for c in _cells(wb, s["ref"])
                if isinstance(c.value, (int, float))]
        # This rule used to be the opposite: it demanded explicit bounds when
        # the data sat well above zero. That was wrong, and it is the clearest
        # example of a rubric encoding a rule that is right for the shipped
        # example and wrong for the template. OOXML axis bounds are static
        # values — they cannot follow a formula — so framing the axis on my
        # numbers guarantees the chart is wrong for anyone whose data has a
        # different magnitude. Tripling the inputs put 95 of 97 points outside
        # the frame. A static bound is now the defect, unless it is a bound
        # that is true by definition for every possible input (kappa is 0..1).
        DEFINITIONAL = {(0.0, 1.0)}
        if val_ax is not None and val_ax["min"] is not None:
            pair = (float(val_ax["min"]), float(val_ax["max"] or 0))
            if pair not in DEFINITIONAL:
                readable = False
                notes.append(f"axis pinned to {pair[0]:,.4g}..{pair[1]:,.4g}, which was "
                             "computed from the shipped example — paste data of a "
                             "different magnitude and the plot frames nothing")
        cat_ax = next((a for a in ch["axes"] if a["kind"] == "catAx"), None)
        skip = int(cat_ax["skip"]) if cat_ax and cat_ax["skip"] else 1
        # This used to read `longest > 18`, counting the rows the chart RESERVES
        # and ignoring how wide a label is. It therefore demanded thinning on a
        # value stream map with nine steps, and on a test log whose categories
        # are the numbers 1 to 25 — both of which fit with room to spare. It is
        # the same rule the polisher applies, imported rather than restated so
        # the two cannot drift apart and each vouch for the other's mistake.
        cats = max((_labels_of(wb, s["cat"]) for s in sers), key=len, default=[])
        if cats and primary != "bar":
            need = sum(len(t) + 1 for t in cats)
            want = max(1, -(-need // AXIS_CHARS))
            if skip < want:
                readable = False
                notes.append(f"{len(cats)} category labels needing 1-in-{want} "
                             f"thinning, thinned 1-in-{skip}")
    lb = ch["labels"]
    if lb and (lb["showCatName"] or lb["showSerName"] or lb["showLegendKey"]):
        readable = False
        notes.append("data labels include the category or series name")
    if n > 1 and not ch["legend"]:
        readable = False
        notes.append("more than one series and no legend")
    if n == 1 and ch["legend"] and primary != "scatter":
        readable = False
        notes.append("a legend for a single series is noise")
    bad = [i for i, s in enumerate(sers, 1) if not s["coloured"] and not s["points"]]
    if bad:
        readable = False
        notes.append(f"series {bad} have no explicit colour")

    # ---- WORTH IT (0-4) ---------------------------------------------------
    worth, why = 0, []
    refs = [s for s in sers if s["name"] and REFERENCE.search(s["name"])]
    flat = 0
    for s in sers:
        nums = [c.value for c in _cells(wb, s["ref"]) if isinstance(c.value, (int, float))]
        if nums and len(set(nums)) == 1:
            flat += 1
    if refs or flat:
        worth += 1
        why.append("brings a reference to the data")
    if sers and all(s["ref"] for s in sers):
        worth += 1
        why.append("bound to cells, so it moves")
    dp = any(s["points"] for s in sers)
    if dp or refs or flat:
        worth += 1
        why.append("encodes a decision visually")
    if title and CONCLUSIVE.search(title) and (refs or flat or dp or n > 1):
        worth += 1
        why.append("answers its own title")
    if worth < 3:
        notes.append("nothing here you could not do yourself in two minutes — "
                     "no reference brought to the data, no decision encoded")

    # ---- EXAMPLE (0-3) ----------------------------------------------------
    example = 0
    data = [s for s in sers if not (s["name"] and REFERENCE.search(s["name"]))] or sers
    plotted = []
    for s in data:
        cells = _cells(wb, s["ref"])
        sh = _shadow(cells[0].parent) if cells else set()
        plotted.append([c for c in cells if (c.row, c.column) not in sh])
    filled = [[c for c in g if c.value not in (None, "")] for g in plotted]
    biggest = max((len(g) for g in filled), default=0)
    span = max((len(g) for g in plotted), default=0)
    if biggest >= 5 or (span and biggest == span):
        example += 1
    else:
        notes.append(f"only {biggest} populated point(s) — a chart with one bar teaches nothing")
    interior = 0
    for g in plotted:
        idx = [i for i, c in enumerate(g) if c.value not in (None, "")]
        if idx:
            interior = max(interior, sum(1 for i in range(idx[0], idx[-1] + 1)
                                         if g[i].value in (None, "")))
    if not interior:
        example += 1
    else:
        notes.append(f"{interior} empty cell(s) between populated ones")

    def _key(c):
        v = c.value
        return ("f", v) if isinstance(v, str) and v.startswith("=") else ("v", v)
    distinct = max((len({_key(c) for c in g}) for g in filled), default=0)
    if distinct >= 3 or (biggest and distinct == biggest):
        example += 1
    else:
        notes.append(f"only {distinct} distinct value(s) — the example shows no shape")

    return {"book": book, "title": title, "kind": "+".join(kinds) or "?",
            "intent": intent or "?", "series": n,
            "right_chart": right_chart, "readable": readable,
            "worth": worth, "worth_why": why, "example": example, "notes": notes}


def ships(g: dict, guidance: int) -> bool:
    return (g["right_chart"] and g["readable"]
            and g["worth"] >= 3 and g["example"] == 3 and guidance == 2)
