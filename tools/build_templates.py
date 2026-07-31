#!/usr/bin/env python3
"""Build the templates that were missing, and their previews.

Eleven tools had no template at all, and several more pointed at one that did
not fit — the fishbone and the 5 Whys both linked to the X-Y matrix, which is a
scoring grid, not a cause diagram. These fill those gaps.

Every workbook follows the same contract as the originals: a "How to use this"
tab, yellow cells you fill in, blue cells that calculate, one worked example
row, and a note on every input saying where the number comes from.

    python3 tools/build_templates.py     # writes templates/*.xlsx + previews.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.chart import BarChart, LineChart, Reference, ScatterChart, Series
from openpyxl.chart.legend import Legend
from openpyxl.chart.marker import Marker
from openpyxl.chart.series import SeriesLabel
from openpyxl.comments import Comment

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preview import workbook_html  # noqa: E402
from xlpolish import polish_workbook  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"

TITLE = PatternFill("solid", fgColor="FF151B24")
BAND = PatternFill("solid", fgColor="FFEEF1F6")
HDR = PatternFill("solid", fgColor="FF333C49")
IN = PatternFill("solid", fgColor="FFFFF9E3")
CALC = PatternFill("solid", fgColor="FFF2F7FF")
EX = PatternFill("solid", fgColor="FFECFAEF")
THIN = Border(bottom=Side("thin", color="FFD8DEE7"))

F_TITLE = Font(bold=True, size=15, color="FFFFFFFF")
F_HDR = Font(bold=True, size=10, color="FFFFFFFF")
F_BAND = Font(bold=True, size=11)
F_B = Font(bold=True, size=11)
F_NOTE = Font(italic=True, size=9, color="FF6B7280")
F_CALC = Font(size=11, color="FF1D4ED8")

SHOWN: dict = {}          # (sheet, cell) -> what the preview should display


def note(ws, row, col, text):
    """Attach 'where this number comes from' to an input cell.

    Inputs inside a table are explained once by their column header. A
    standalone input has no header, so it carries its own note — which is what
    the page means when it says every yellow cell tells you where to look.
    """
    c = ws.cell(row=row, column=col)
    c.comment = Comment(text, "Template")
    c.comment.width = 320
    c.comment.height = 110
    return c


def title(ws, text, sub, width):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=width)
    ws.cell(row=1, column=1, value=text).font = F_TITLE
    for c in range(1, width + 1):
        ws.cell(row=1, column=c).fill = TITLE
    ws.row_dimensions[1].height = 26
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=width)
    ws.cell(row=2, column=1, value=sub).font = F_NOTE
    ws.sheet_view.showGridLines = False


def band(ws, row, text, width):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=width)
    ws.cell(row=row, column=1, value=text).font = F_BAND
    for c in range(1, width + 1):
        ws.cell(row=row, column=c).fill = BAND


def header(ws, row, labels):
    for i, l in enumerate(labels, start=1):
        c = ws.cell(row=row, column=i, value=l)
        c.fill, c.font = HDR, F_HDR
        c.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[row].height = 30


def widths(ws, ws_widths):
    for i, w in enumerate(ws_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def howto(wb, lines):
    ws = wb.create_sheet("How to use this", 0)
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 2
    ws.column_dimensions["B"].width = 108
    for i, (bold, text) in enumerate(lines, start=2):
        c = ws.cell(row=i, column=2, value=text)
        c.font = F_B if bold else Font(size=11)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        if not bold:
            ws.row_dimensions[i].height = max(15, 15 * (len(text) // 100 + 1))
    return ws



def overlay(ch, ws, ref, name, colour="C0392B"):
    """Lay a dashed reference line over a bar chart — the standard, on the data."""
    from openpyxl.chart.legend import Legend
    ln = LineChart()
    sr = Series(ref, title=name)
    sr.graphicalProperties.line.solidFill = colour
    sr.graphicalProperties.line.width = 18000
    sr.graphicalProperties.line.dashStyle = "dash"
    sr.marker = Marker(symbol="none")
    sr.smooth = False
    ln.series.append(sr)
    ch += ln
    ch.legend = Legend()
    ch.legend.position = "b"
    return ch


def bar(ws, title_, cat_ref, val_ref, anchor, horizontal=False, pct=False, series=None,
        colours=None):
    """A chart bound to the cells, so it moves when the numbers do.

    Series titles are set here rather than read from a header cell, because the
    header row is usually inside a merged band and merged cells are read-only.
    """
    ch = BarChart()
    ch.type = "bar" if horizontal else "col"
    ch.style = 10
    ch.title = title_
    ch.legend = None
    ch.height, ch.width = 7.5, 15
    ch.gapWidth = 60
    ch.add_data(val_ref, titles_from_data=False)
    ch.set_categories(cat_ref)
    if ch.series and colours:
        from openpyxl.chart.marker import DataPoint
        from openpyxl.chart.shapes import GraphicalProperties
        ch.series[0].data_points = [
            DataPoint(idx=i, spPr=GraphicalProperties(solidFill=c))
            for i, c in enumerate(colours)]
    elif ch.series:
        ch.series[0].graphicalProperties.solidFill = "1F4E79"
        ch.series[0].graphicalProperties.line.solidFill = "1F4E79"
    # OOXML's invertIfNegative defaults on, and with no negative fill defined
    # the renderer draws negative bars as nothing at all. This has to apply on
    # both paths above — the per-point-colour branch used to skip it.
    for ser in ch.series:
        ser.invertIfNegative = False
    if series:
        ch.series[0].tx = None
    ch.y_axis.majorGridlines = None if horizontal else ch.y_axis.majorGridlines
    if pct:
        ch.y_axis.numFmt = "0%"
    ws.add_chart(ch, anchor)
    return ch


def mark(ws, row, col, kind, note=None):
    c = ws.cell(row=row, column=col)
    if kind == "in":
        c.fill, c.border = IN, THIN
    elif kind == "calc":
        c.fill, c.font, c.border = CALC, F_CALC, THIN
    elif kind == "ex":
        c.fill, c.border = EX, THIN
    return c


LEGEND = [
    (True, "Yellow cells"), (False, "You fill these in."),
    (True, "Blue cells"), (False, "Calculated for you. Do not type over them — they contain formulas."),
    (True, "Green row"), (False, "A worked example so you can see the expected format. Delete it when you start."),
]


# ---------------------------------------------------------------- 20 five whys
def five_whys():
    wb = Workbook(); wb.remove(wb.active)
    ws = wb.create_sheet("5 Whys tree")
    title(ws, "5 Whys — run it as a tree, not a chain",
          "A single chain gives you one cause and false confidence. Branching gives you a hypothesis set you can test.", 9)
    widths(ws, [10, 30, 30, 30, 30, 30, 12, 14, 32])   # 6 clipped "Instance" to "Instan"
    band(ws, 4, "THE PROBLEM — one specific instance, not a general statement", 9)
    ws.cell(row=5, column=1, value="Instance").font = F_B
    ws.merge_cells("B5:E5"); mark(ws, 5, 2, "in")
    ws.cell(row=5, column=2, value="Billing ticket #48217, closed 12 Mar, reopened 14 Mar")
    note(ws, 5, 2, "One concrete record, with it open in front of you: ticket number, what happened, "
                   "and when. 'Reopens are high' is not an instance and cannot be walked back to a cause.")
    ws.cell(row=5, column=7, value="Date").font = F_B
    mark(ws, 5, 8, "in").value = "2026-03-14"
    note(ws, 5, 8, "The date of the instance, not the date you ran the session. You will want to go "
                   "back to the system state as it was.")
    ws.cell(row=6, column=1, value="Effect").font = F_B
    ws.merge_cells("B6:E6"); mark(ws, 6, 2, "in")
    ws.cell(row=6, column=2, value="Customer had to contact us a second time about the same adjustment")
    note(ws, 6, 2, "What the customer experienced, in their terms. Not the internal symptom and not "
                   "the fix you already have in mind.")
    ws.cell(row=7, column=2, value="Start from a concrete instance with the record in front of you. "
            "At each level ask 'what else could cause this?' before you go deeper.").font = F_NOTE

    # It is called the 5 Whys. Collapsing four and five into one column asks
    # four, and four is usually one short of anything you can act on.
    header(ws, 9, ["#", "Why 1", "Why 2", "Why 3", "Why 4", "Why 5", "Branch?",
                   "Testable with data?", "How you would test it"])
    # The tool is called "a tree, not a chain", so a single-branch example
    # argues against the template. Three branches from the same instance.
    ex = [
        ["1", "The adjustment had not posted when the ticket was closed",
         "Closure is allowed before the posting webhook confirms",
         "The ticket status model has no 'pending adjustment' state",
         "The billing integration was specified as fire-and-forget, with no callback",
         "No one owned the ticket lifecycle across billing and support when it was designed",
         "A", "Yes", "Count reopens where closure preceded the webhook timestamp"],
        ["2", "The agent could not see whether the adjustment had posted",
         "Billing status lives in another system with no view inside the ticket",
         "The integration was scoped to write, never to read",
         "Scope was cut on integration cost, with no one costing the agent's workflow",
         "Design reviews do not require sign-off from anyone who works the queue",
         "B", "Yes", "Sample 50 reopens and check whether the agent had visibility at closure"],
        ["3", "We only count reopens raised for the same reason",
         "The metric was defined by reporting without asking operations",
         "No operational definition was agreed when the project started",
         "The charter template does not require one before the baseline is taken",
         "Metric definitions have no owner anywhere in the organisation",
         "C", "Yes", "Recount reopens on an any-reason definition and compare the two series"],
    ]
    for k, row in enumerate(ex):
        for i, v in enumerate(row, start=1):
            c = ws.cell(row=10 + k, column=i, value=v); c.fill = EX; c.border = THIN
            c.alignment = Alignment(wrap_text=True, vertical="top")
        # size the row to its longest cell: a fixed 30pt clipped the last line
        # of every branch, which is exactly the line that names the root cause
        widest = max(len(str(v)) for v in row[1:6])
        ws.row_dimensions[10 + k].height = max(32, 15 * -(-widest // 25))
    for r in range(13, 26):
        ws.cell(row=r, column=1, value=r - 9).font = F_NOTE
        for c in range(2, 10):
            mark(ws, r, c, "in").alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = 30
    dv = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
    ws.add_data_validation(dv); dv.add("H10:H25")

    band(ws, 27, "CHECK BEFORE YOU LEAVE THIS TOOL", 9)
    rows = [("Branches explored", '=COUNTA(B10:B25)', "3"),
            ("Branches you can test with data", '=COUNTIF(H10:H25,"Yes")', "3"),
            ("Chains that reached five levels", '=COUNTA(F10:F25)', "3"),
            ("Chains that stopped at a person",
             '=COUNTIF(F10:F25,"*training*")+COUNTIF(F10:F25,"*follow the process*")', "0")]
    for i, (label, f, shown) in enumerate(rows, start=28):
        ws.cell(row=i, column=1, value=label).font = F_B
        ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=5)
        c = mark(ws, i, 6, "calc"); c.value = f
        SHOWN[("5 Whys tree", f"F{i}")] = shown
    ws.merge_cells("A33:I33")
    ws.cell(row=33, column=1, value="If your last why is 'not enough training' or 'the agent did not follow the "
            "process', you stopped one level too early. Ask why the process was skippable — that is the cause you "
            "can actually fix.").font = F_NOTE
    howto(wb, LEGEND + [
        (True, "What this is for"),
        (False, "Moving from a symptom to a cause you can act on, without the false confidence a single chain gives you."),
        (True, "The two rules"),
        (False, "1. Start from one concrete instance with the record open. Not 'reopens are high' — ticket #48217."),
        (False, "2. At every level ask 'what else could cause this?' before descending. Two or three branches, not one line."),
        (True, "When to stop"),
        (False, "When you reach something the organisation can change, or when the next why leaves your sphere entirely."),
        (True, "What comes out"),
        (False, "A hypothesis list, not a root cause. It becomes a root cause only when you test it — that is what the "
                "last two columns are for. Carry the testable branches into the X-Y matrix and the hypothesis test log."),
    ])
    return wb, "20-five-whys-tree.xlsx"


# --------------------------------------------------------- 21 cause and effect
def fishbone():
    wb = Workbook(); wb.remove(wb.active)
    ws = wb.create_sheet("Fishbone")
    title(ws, "Cause & effect (Ishikawa) — support categories, not 6M",
          "Machine / Method / Material / Measurement / Man / Mother Nature was written for a factory. These are the categories a support process actually fails in.", 6)
    widths(ws, [30, 46, 14, 14, 16, 34])
    band(ws, 4, "THE EFFECT — use the problem statement's metric and magnitude", 6)
    ws.merge_cells("B5:F5"); mark(ws, 5, 2, "in")
    ws.cell(row=5, column=1, value="Effect").font = F_B
    ws.cell(row=5, column=2, value="7-day reopen rate on billing tickets is 14.2% against a target of 8%")
    note(ws, 5, 2, "Copy the problem statement's metric and magnitude verbatim — the measured value, "
                   "the target, and the population. A vague effect gives you a fishbone of vague causes.")

    header(ws, 7, ["Category", "Candidate cause", "Likelihood 1-5", "Impact 1-5",
                   "Priority", "Evidence you would need"])
    cats = ["People", "Process", "Systems", "Knowledge", "Routing & demand",
            "Product / upstream", "Measurement"]
    # One example cause left six of the seven branches reading "EMPTY — look
    # again", so the template's own quality gate was firing on its own example.
    ex = [
        ["Process", "Ticket can be closed before the billing adjustment posts", 5, 5,
         "Reopens where closure timestamp precedes the posting webhook"],
        ["Process", "Billing Ops pull the queue once a day, so nothing moves overnight", 4, 4,
         "Queue age distribution by hour of arrival"],
        ["Systems", "The status model has no pending-adjustment state", 5, 5,
         "Count of closures with an adjustment still in flight"],
        ["Systems", "The nightly adjustment batch fails silently", 3, 5,
         "Batch exit codes against the days reopens spiked"],
        ["People", "New hires close on the request, not on the posting", 3, 4,
         "Reopen rate split by agent tenure band"],
        ["Knowledge", "No written definition of 'resolved' for a billing adjustment", 4, 3,
         "Ask ten agents to define it and compare the answers"],
        ["Routing & demand", "Adjustment requests route to general billing, not the adjustments desk", 3, 3,
         "Share of reopens that were transferred at least once"],
        ["Product / upstream", "The billing platform posts asynchronously with no callback", 4, 5,
         "Distribution of the gap between request and posting"],
        ["Measurement", "Reopen rate counts same-reason reopens only, hiding the rest", 3, 4,
         "Recount on an any-reason definition"],
    ]
    for k, row in enumerate(ex):
        rr = 8 + k
        for i, v in enumerate(row, start=1):
            col = i if i < 5 else 6            # column 5 is the calculated priority
            c = ws.cell(row=rr, column=col, value=v); c.fill = EX; c.border = THIN
            c.alignment = Alignment(wrap_text=True, vertical="top")
        c = mark(ws, rr, 5, "calc"); c.value = f'=IF(COUNT(C{rr}:D{rr})<2,"",C{rr}*D{rr})'
        c.fill = EX
        SHOWN[("Fishbone", f"E{rr}")] = str(row[2] * row[3])
    for rr in range(8 + len(ex), 36):
        for cc in range(1, 7):
            mark(ws, rr, cc, "in").alignment = Alignment(wrap_text=True, vertical="top")
        c = mark(ws, rr, 5, "calc")
        c.value = f'=IF(COUNT(C{rr}:D{rr})<2,"",C{rr}*D{rr})'
        SHOWN[("Fishbone", f"E{rr}")] = ""
    # Key the table so the diagram can pull "the nth cause in this category".
    # INDEX/MATCH on a composite key works in every Excel version; FILTER and
    # TEXTJOIN do not.
    ws.cell(row=7, column=20, value="key (used by the diagram)").font = F_NOTE
    for rr in range(8, 36):
        k = ws.cell(row=rr, column=20)
        k.value = f'=IF(A{rr}="","",A{rr}&"|"&COUNTIF($A$8:A{rr},A{rr}))'
        k.font = F_NOTE
        SHOWN[("Fishbone", f"T{rr}")] = ""
    ws.column_dimensions[get_column_letter(20)].width = 22
    ws.column_dimensions[get_column_letter(20)].hidden = True   # plumbing, not content

    dvc = DataValidation(type="list", formula1='"%s"' % ",".join(cats), allow_blank=True)
    ws.add_data_validation(dvc); dvc.add("A8:A35")
    dvs = DataValidation(type="whole", operator="between", formula1=1, formula2=5, allow_blank=True)
    ws.add_data_validation(dvs); dvs.add("C8:D35")

    band(ws, 37, "BRANCH BALANCE — a thin branch is a blind spot, not an absence of causes", 6)
    for i, cat in enumerate(cats):
        r = 38 + i
        ws.cell(row=r, column=1, value=cat).font = F_B
        c = mark(ws, r, 2, "calc"); c.value = f'=COUNTIF($A$8:$A$35,A{r})'
        n = sum(1 for e in ex if e[0] == cat)
        SHOWN[("Fishbone", f"B{r}")] = str(n)
        c2 = mark(ws, r, 3, "calc")
        c2.value = f'=IF(COUNTIF($A$8:$A$35,A{r})=0,"EMPTY — look again","")'
        SHOWN[("Fishbone", f"C{r}")] = "" if n else "EMPTY — look again"
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=6)
    for i in range(7):
        r = 38 + i
        c = mark(ws, r, 8, "calc")
        c.value = "=AVERAGE($B$38:$B$44)"
        c.number_format = "#,##0.0"
        SHOWN[("Fishbone", f"H{r}")] = "%.1f" % (len(ex) / 7.0)
    ws.cell(row=37, column=8, value="Mean causes per branch").font = F_NOTE
    fb = bar(ws, "Causes per branch — a thin bar is a blind spot",
             Reference(ws, min_col=1, min_row=38, max_row=44),
             Reference(ws, min_col=2, min_row=38, max_row=44), "J8")
    overlay(fb, ws, Reference(ws, min_col=8, min_row=38, max_row=44),
            "Mean — below this is a branch you are not looking at")
    ws.merge_cells("A46:F46")
    ws.cell(row=46, column=1, value="Support teams over-populate People and under-populate Systems and Knowledge, "
            "because blaming agents is culturally available. An empty Measurement branch is almost always wrong — "
            "if you have not questioned the measurement, you have not finished.").font = F_NOTE

    # ---- the diagram itself -------------------------------------------
    # An Ishikawa is a fishbone-SHAPED diagram: a spine pointing at the effect
    # with angled bones for each category. A table and a bar chart of counts is
    # not one. This draws the real thing, and every cause cell is a formula
    # reading the table, so the picture updates as you type.
    wsd = wb.create_sheet("Fishbone diagram", 1)
    wsd.sheet_view.showGridLines = False
    BONE = Side("medium", color="FF333C49")
    SPINE = Side("thick", color="FF151B24")

    wsd.column_dimensions["A"].width = 2
    for c in range(2, 27):
        wsd.column_dimensions[get_column_letter(c)].width = 7.5
    for c in range(27, 31):
        wsd.column_dimensions[get_column_letter(c)].width = 13

    wsd.merge_cells(start_row=1, start_column=1, end_row=1, end_column=30)
    t = wsd.cell(row=1, column=1, value="Cause & effect — the diagram")
    t.font = F_TITLE
    for c in range(1, 31):
        wsd.cell(row=1, column=c).fill = TITLE
    wsd.row_dimensions[1].height = 26
    wsd.merge_cells(start_row=2, start_column=1, end_row=2, end_column=30)
    wsd.cell(row=2, column=1, value="Every box below is a formula reading the Fishbone tab. Type there; "
             "this redraws itself. Four causes per branch are shown — the tab holds as many as you like.").font = F_NOTE

    TOP = ["People", "Process", "Systems", "Knowledge"]
    BOT = ["Routing & demand", "Product / upstream", "Measurement"]
    CAUSE_ROWS_TOP = [6, 8, 10, 12]
    CAUSE_ROWS_BOT = [18, 20, 22, 24]
    SPINE_ROW = 15

    def cause(row, c1, c2, category, n):
        wsd.merge_cells(start_row=row, start_column=c1, end_row=row, end_column=c2)
        cell = wsd.cell(row=row, column=c1)
        cell.value = ('=IFERROR(INDEX(Fishbone!$B$8:$B$35,'
                      'MATCH("%s|%d",Fishbone!$T$8:$T$35,0)),"")' % (category, n))
        cell.font = Font(size=9)
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.fill = CALC
        wsd.row_dimensions[row].height = 26
        SHOWN[("Fishbone diagram", cell.coordinate)] = ""

    def catbox(row, c1, c2, name):
        wsd.merge_cells(start_row=row, start_column=c1, end_row=row, end_column=c2)
        cell = wsd.cell(row=row, column=c1, value=name)
        cell.font = F_HDR
        cell.alignment = Alignment(horizontal="center", vertical="center")
        for c in range(c1, c2 + 1):
            wsd.cell(row=row, column=c).fill = HDR
        wsd.row_dimensions[row].height = 20

    for j, name in enumerate(TOP):
        c = 2 + 6 * j
        catbox(4, c, c + 3, name)
        for i, r in enumerate(CAUSE_ROWS_TOP, start=1):
            cause(r, c, c + 3, name, i)
        # one merged block with a single diagonal is a clean straight bone;
        # a stack of per-cell diagonals renders as a dashed staircase
        wsd.merge_cells(start_row=5, start_column=c + 4, end_row=SPINE_ROW - 1, end_column=c + 5)
        wsd.cell(row=5, column=c + 4).border = Border(diagonal=BONE, diagonalDown=True)

    for j, name in enumerate(BOT):
        c = 5 + 6 * j
        for i, r in enumerate(CAUSE_ROWS_BOT, start=1):
            cause(r, c, c + 3, name, i)
        catbox(26, c, c + 3, name)
        wsd.merge_cells(start_row=SPINE_ROW + 1, start_column=c + 4, end_row=25, end_column=c + 5)
        wsd.cell(row=SPINE_ROW + 1, column=c + 4).border = Border(diagonal=BONE, diagonalUp=True)

    for c in range(2, 27):
        wsd.cell(row=SPINE_ROW, column=c).border = Border(bottom=SPINE)
    wsd.row_dimensions[SPINE_ROW].height = 10

    wsd.merge_cells(start_row=SPINE_ROW - 3, start_column=27, end_row=SPINE_ROW + 3, end_column=30)
    eff = wsd.cell(row=SPINE_ROW - 3, column=27, value="=Fishbone!B5")
    eff.font = Font(bold=True, size=12, color="FFFFFFFF")
    eff.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    for r in range(SPINE_ROW - 3, SPINE_ROW + 4):
        for c in range(27, 31):
            wsd.cell(row=r, column=c).fill = PatternFill("solid", fgColor="FFC0392B")
    SHOWN[("Fishbone diagram", eff.coordinate)] = \
        "7-day reopen rate on billing tickets is 14.2% against a target of 8%"

    wsd.merge_cells(start_row=28, start_column=1, end_row=28, end_column=30)
    wsd.cell(row=28, column=1, value="A branch with no boxes is where you are not looking, not where there is "
             "nothing to find. An empty Measurement branch is almost always wrong.").font = F_NOTE

    ws2 = wb.create_sheet("Category prompts")
    ws2.sheet_view.showGridLines = False
    widths(ws2, [26, 96])
    title(ws2, "What lives in each branch", "Prompts to force entries into the thin branches.", 2)
    prompts = [
        ("People", "Skill, tenure, authority limits, coaching, workload, incentive conflicts."),
        ("Process", "Steps that can be skipped, missing pending states, approvals, handoffs, queue discipline."),
        ("Systems", "Tooling gaps, swivel-chair work, latency, permissions, integrations that fail silently."),
        ("Knowledge", "Missing or wrong articles, search that does not find them, content nobody owns."),
        ("Routing & demand", "Mis-routing, IVR options, skill-based routing rules, arrival patterns, mix shift."),
        ("Product / upstream", "Defects reaching customers, confusing UX, billing logic, release cadence."),
        ("Measurement", "Disposition codes, QA rubric, operational definitions, instrumentation gaps."),
    ]
    for i, (k, v) in enumerate(prompts, start=4):
        ws2.cell(row=i, column=1, value=k).font = F_B
        c = ws2.cell(row=i, column=2, value=v)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws2.row_dimensions[i].height = 28
    howto(wb, LEGEND + [
        (True, "What this is for"),
        (False, "Getting every candidate cause out of the team's heads and onto one page, grouped so the gaps are visible."),
        (True, "How to run it"),
        (False, "Write the effect precisely first. Brainwrite silently for five minutes before anyone speaks — "
                "verbal-first brainstorming is dominated by the most senior voice in the room."),
        (False, "Push each branch down two levels with 'why does that happen?'. Then score likelihood and impact."),
        (True, "The check that matters"),
        (False, "Look at the branch balance table. A thin or empty branch is where you are not looking, not where "
                "there is nothing to find."),
        (True, "What comes out"),
        (False, "Causes on a fishbone are hypotheses, not findings. Nothing leaves this tool without being tested — "
                "carry the highest-priority ones into the X-Y matrix."),
    ])
    return wb, "21-cause-effect-fishbone.xlsx"


# ------------------------------------------------------ 22 stakeholder / RACI
STAKEHOLDERS = [('A. Okafor', 'Billing Ops Manager', 5, -1, 'Proof this will not add work to her team', 'Black Belt'), ('R. Mehta', 'Support Director', 5, 2, 'A monthly number she can take to the exec review', 'Champion'), ('J. Lindqvist', 'Finance Business Partner', 4, 0, 'The benefit accounting policy agreed before baseline', 'Black Belt'), ('S. Duarte', 'WFM Lead', 4, -2, 'Assurance the harvest is scheduled, not assumed', 'Champion'), ('P. Nwosu', 'Platform Engineering Manager', 3, 1, 'A scoped ticket, not a standing request', 'Black Belt'), ('K. Tanaka', 'QA Lead', 3, 2, 'Involvement in the operational definition', 'Black Belt'), ('M. Alvarez', 'Tier 1 Team Lead', 2, 1, 'Her agents consulted before the process changes', 'Process owner'), ('D. Byrne', 'Compliance', 2, 0, 'Sight of anything touching retention or consent', 'Champion')]

RACI_ROWS = [('Sign the benefit and harvest mechanism', 'C', 'A', 'C', 'C', 'R'), ('Agree the operational definition of a defect', 'R', 'I', 'A', 'I', 'C'), ('Approve the pilot design and stopping rule', 'R', 'A', 'C', 'C', 'I'), ('Change the routing rules in production', 'C', 'I', 'A', 'C', 'I'), ('Own the control chart and its reaction plan', 'C', 'I', 'A', 'R', 'I'), ('Release the headcount the project frees', 'I', 'C', 'C', 'R', 'A')]


def stakeholder():
    wb = Workbook(); wb.remove(wb.active)
    ws = wb.create_sheet("Stakeholders")
    title(ws, "Stakeholder analysis — who can stop this, and who will",
          "Projects rarely fail on the statistics. They fail because someone with influence was never asked.", 7)
    widths(ws, [26, 26, 14, 14, 16, 30, 30])
    header(ws, 4, ["Name", "Role", "Influence 1-5", "Support -2..+2", "Action needed",
                   "What they need from you", "Owner"])
    # One stakeholder is not a stakeholder map, and it left every quadrant of
    # the grid empty but one.
    for k, (nm, role, inf, sup, need, owner) in enumerate(STAKEHOLDERS):
        r = 5 + k
        for i, v in enumerate((nm, role, inf, sup), start=1):
            c = ws.cell(row=r, column=i, value=v); c.fill = EX; c.border = THIN
            c.alignment = Alignment(wrap_text=True, vertical="top")
        for i, v in ((6, need), (7, owner)):
            c = ws.cell(row=r, column=i, value=v); c.fill = EX; c.border = THIN
            c.alignment = Alignment(wrap_text=True, vertical="top")
        c = mark(ws, r, 5, "calc"); c.fill = EX
        c.value = (f'=IF(COUNT(C{r}:D{r})<2,"",IF(AND(C{r}>=4,D{r}<0),"ENGAGE NOW",'
                   f'IF(C{r}>=4,"KEEP CLOSE",IF(D{r}<0,"MONITOR","INFORM"))))')
        SHOWN[("Stakeholders", f"E{r}")] = (
            "ENGAGE NOW" if inf >= 4 and sup < 0 else
            "KEEP CLOSE" if inf >= 4 else "MONITOR" if sup < 0 else "INFORM")
        ws.row_dimensions[r].height = 26
    for r in range(5 + len(STAKEHOLDERS), 24):
        for cc in [1, 2, 3, 4, 6, 7]:
            mark(ws, r, cc, "in").alignment = Alignment(wrap_text=True, vertical="top")
        c = mark(ws, r, 5, "calc")
        c.value = (f'=IF(COUNT(C{r}:D{r})<2,"",IF(AND(C{r}>=4,D{r}<0),"ENGAGE NOW",'
                   f'IF(C{r}>=4,"KEEP CLOSE",IF(D{r}<0,"MONITOR","INFORM"))))')
        SHOWN[("Stakeholders", f"E{r}")] = ""
    # The stakeholder map itself: influence against support, so the quadrant a
    # name lands in is visible rather than inferred from two columns of digits.
    sc = ScatterChart()
    sc.title = "Stakeholder map — influence against support"
    sc.style = 13
    sc.height, sc.width = 10, 15
    sc.x_axis.title = "Support:  -2 opposed  \u2192  +2 advocate"
    sc.y_axis.title = "Influence over the outcome"
    sc.x_axis.delete = False
    sc.y_axis.delete = False
    sc.x_axis.scaling.min, sc.x_axis.scaling.max = -2.5, 2.5
    sc.y_axis.scaling.min, sc.y_axis.scaling.max = 0, 6
    # Without an explicit scatterStyle no series gets a line, so the quadrant
    # dividers were written to the file and then not drawn by anything.
    sc.scatterStyle = "lineMarker"
    sc.legend = None
    pts = Series(Reference(ws, min_col=3, min_row=5, max_row=4 + len(STAKEHOLDERS)),
                 xvalues=Reference(ws, min_col=4, min_row=5, max_row=4 + len(STAKEHOLDERS)),
                 title="Stakeholders")
    pts.marker = Marker(symbol="circle", size=9)
    pts.marker.graphicalProperties.solidFill = "1F4E79"
    pts.graphicalProperties.line.noFill = True      # points only, no joining line
    sc.series.append(pts)

    # Without the dividers this is a scatter of two columns you already have.
    # With them it is the map: the top-left quadrant is who can stop you.
    n = len(STAKEHOLDERS)
    for i in range(n):
        r = 5 + i
        ws.cell(row=r, column=9, value=3.5).font = F_NOTE          # influence split
        ws.cell(row=r, column=10, value="=D%d" % r).font = F_NOTE  # support, for the x
        ws.cell(row=r, column=11, value=0).font = F_NOTE           # support split
        ws.cell(row=r, column=12, value="=C%d" % r).font = F_NOTE  # influence, for the y
        SHOWN[("Stakeholders", f"J{r}")] = str(STAKEHOLDERS[i][3])
        SHOWN[("Stakeholders", f"L{r}")] = str(STAKEHOLDERS[i][2])
    ws.cell(row=4, column=9, value="quadrant dividers — the chart reads these").font = F_NOTE
    for col in "IJKL":
        ws.column_dimensions[col].width = 6      # narrow, not hidden: a chart
                                                 # will not plot a hidden cell

    hline = Series(Reference(ws, min_col=9, min_row=5, max_row=4 + n),
                   xvalues=Reference(ws, min_col=10, min_row=5, max_row=4 + n),
                   title="High influence threshold")
    hline.marker = Marker(symbol="none")
    hline.graphicalProperties.line.solidFill = "C0392B"
    hline.graphicalProperties.line.dashStyle = "dash"
    sc.series.append(hline)

    vline = Series(Reference(ws, min_col=12, min_row=5, max_row=4 + n),
                   xvalues=Reference(ws, min_col=11, min_row=5, max_row=4 + n),
                   title="Opposed / supportive threshold")
    vline.marker = Marker(symbol="none")
    vline.graphicalProperties.line.solidFill = "C0392B"
    vline.graphicalProperties.line.dashStyle = "dash"
    sc.series.append(vline)
    sc.legend = Legend()
    sc.legend.position = "b"
    ws.add_chart(sc, "N4")

    dvi = DataValidation(type="whole", operator="between", formula1=1, formula2=5, allow_blank=True)
    ws.add_data_validation(dvi); dvi.add("C5:C23")
    dvs = DataValidation(type="whole", operator="between", formula1=-2, formula2=2, allow_blank=True)
    ws.add_data_validation(dvs); dvs.add("D5:D23")
    band(ws, 25, "SUMMARY", 7)
    for i, (label, f, shown) in enumerate([
            ("Stakeholders mapped", '=COUNTA(A5:A23)', str(len(STAKEHOLDERS))),
            ("High influence and opposed — deal with these first", '=COUNTIF(E5:E23,"ENGAGE NOW")',
             str(sum(1 for x in STAKEHOLDERS if x[2] >= 4 and x[3] < 0))),
            ("High influence and supportive — your sponsors", '=COUNTIF(E5:E23,"KEEP CLOSE")',
             str(sum(1 for x in STAKEHOLDERS if x[2] >= 4 and x[3] >= 0)))], start=26):
        ws.cell(row=i, column=1, value=label).font = F_B
        ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=4)
        mark(ws, i, 5, "calc").value = f
        SHOWN[("Stakeholders", f"E{i}")] = shown

    ws2 = wb.create_sheet("RACI")
    ws2.sheet_view.showGridLines = False
    title(ws2, "RACI — exactly one Accountable per row",
          "Two names in the Accountable column is the most common reason a control plan quietly stops being executed.", 7)
    widths(ws2, [40, 16, 16, 16, 16, 16, 26])
    header(ws2, 4, ["Activity / decision", "Black Belt", "Champion", "Process owner",
                    "WFM", "Finance", "Accountable count"])
    for k, row in enumerate(RACI_ROWS):
        r = 5 + k
        for i, v in enumerate(row, start=1):
            c = ws2.cell(row=r, column=i, value=v); c.fill = EX; c.border = THIN
            c.alignment = Alignment(wrap_text=True, vertical="center")
        c = mark(ws2, r, 7, "calc"); c.fill = EX
        c.value = (f'=IF(COUNTIF(B{r}:F{r},"A")=1,"OK",IF(COUNTIF(B{r}:F{r},"A")=0,'
                   f'"NO OWNER","MORE THAN ONE"))')
        SHOWN[("RACI", f"G{r}")] = "OK"
    for r in range(5 + len(RACI_ROWS), 22):
        for cc in range(1, 7):
            mark(ws2, r, cc, "in")
        c = mark(ws2, r, 7, "calc")
        c.value = (f'=IF(COUNTA(A{r})=0,"",IF(COUNTIF(B{r}:F{r},"A")=1,"OK",'
                   f'IF(COUNTIF(B{r}:F{r},"A")=0,"NO OWNER","MORE THAN ONE")))')
        SHOWN[("RACI", f"G{r}")] = ""
    dvr = DataValidation(type="list", formula1='"R,A,C,I"', allow_blank=True)
    ws2.add_data_validation(dvr); dvr.add("B5:F21")
    ws2.merge_cells("A23:G23")
    ws2.cell(row=23, column=1, value="R = does the work · A = owns the outcome (exactly one) · "
             "C = asked before the decision · I = told after it.").font = F_NOTE
    howto(wb, LEGEND + [
        (True, "What this is for"),
        (False, "Finding the person who can stop your project before they do, and settling who owns what while it is cheap."),
        (True, "Stakeholders tab"),
        (False, "Score influence 1-5 and support -2 to +2 honestly. The Action column works out who to deal with first: "
                "high influence and opposed is where projects die."),
        (True, "RACI tab"),
        (False, "The count column flags any row that does not have exactly one Accountable. Fix every flag before you "
                "leave the tollgate — 'we are both accountable' means nobody is."),
    ])
    return wb, "22-stakeholder-and-raci.xlsx"


# ------------------------------------------------------------------- 23 Kano
def kano():
    wb = Workbook(); wb.remove(wb.active)
    ws = wb.create_sheet("Kano analysis")
    title(ws, "Kano analysis — which requirements actually win anything",
          "Ask each customer two questions per feature: how do you feel if it is present, and how if it is absent.", 6)
    widths(ws, [40, 24, 24, 20, 18, 40])
    ws.merge_cells("A4:F4")
    ws.cell(row=4, column=1, value="Answer scale for both questions: Like · Expect it · Neutral · Live with it · Dislike").font = F_NOTE
    header(ws, 6, ["Feature or requirement", "If present (functional)", "If absent (dysfunctional)",
                   "Category", "Invest?", "What it means for you"])
    scale = "Like,Expect it,Neutral,Live with it,Dislike"
    # Kano's published evaluation table. The previous version had two cells of
    # it transposed: Like/Dislike is One-dimensional (Performance) and
    # Expect-it/Dislike is Must-be — they were returning each other's answer,
    # which inverts the investment advice on the two most common responses.
    CATF = ('=IF(OR(B{r}="",C{r}=""),"",'
            'IF(B{r}="Like",'
            'IF(C{r}="Like","Questionable",IF(C{r}="Dislike","Performance","Delighter")),'
            'IF(B{r}="Dislike",'
            'IF(C{r}="Dislike","Questionable","Reverse"),'
            'IF(C{r}="Dislike","Must-have",'
            'IF(C{r}="Like","Reverse","Indifferent")))))')
    INVF = ('=IF(D{r}="","",IF(D{r}="Must-have","Fix it — no credit for doing it, all the blame for not",'
            'IF(D{r}="Performance","Invest — more is better, and measurable",'
            'IF(D{r}="Delighter","Consider — wins goodwill, costs you nothing if absent",'
            'IF(D{r}="Reverse","Stop doing it — they want the opposite",'
            'IF(D{r}="Questionable","Re-ask — the two answers contradict each other",'
            '"Do not spend here"))))))')
    # One row demonstrated one category and left the other three reading zero,
    # so the chart was a single bar and the summary said nothing.
    EXROWS = [
        ("Resolved without me repeating myself", "Expect it", "Dislike", "Must-have"),
        ("Answered within the time you promised", "Expect it", "Dislike", "Must-have"),
        ("Agent already knows my account history", "Like", "Dislike", "Performance"),
        ("Fewer transfers between teams", "Like", "Dislike", "Performance"),
        ("Proactive notice before I notice the problem", "Like", "Live with it", "Delighter"),
        ("A follow-up note a week later", "Like", "Neutral", "Delighter"),
        ("Choice of chat colour scheme", "Neutral", "Neutral", "Indifferent"),
        ("A survey after every single contact", "Dislike", "Neutral", "Reverse"),
    ]
    for k, (feat, fun, dys, _cat) in enumerate(EXROWS):
        rr = 7 + k
        for i, v in enumerate((feat, fun, dys), start=1):
            c = ws.cell(row=rr, column=i, value=v); c.fill = EX; c.border = THIN
        for col, f in [(4, CATF.format(r=rr)), (5, INVF.format(r=rr))]:
            c = mark(ws, rr, col, "calc"); c.fill = EX; c.value = f
        SHOWN[("Kano analysis", f"D{rr}")] = _cat
        SHOWN[("Kano analysis", f"E{rr}")] = ""
    for col, f, shown in [(4, CATF.format(r=7), "Must-have"),
                          (5, INVF.format(r=7), "Fix it — no credit for doing it, all the blame for not")]:
        c = mark(ws, 7, col, "calc"); c.fill = EX; c.value = f
        SHOWN[("Kano analysis", f"{get_column_letter(col)}7")] = shown
    mark(ws, 7, 6, "in").fill = EX
    for r in range(8, 26):
        for cc in [1, 2, 3, 6]:
            mark(ws, r, cc, "in").alignment = Alignment(wrap_text=True, vertical="top")
        for col, f in [(4, CATF.format(r=r)), (5, INVF.format(r=r))]:
            mark(ws, r, col, "calc").value = f
            SHOWN[("Kano analysis", f"{get_column_letter(col)}{r}")] = ""
    dv = DataValidation(type="list", formula1=f'"{scale}"', allow_blank=True)
    ws.add_data_validation(dv); dv.add("B7:C25")
    band(ws, 27, "WHERE YOUR EFFORT SHOULD GO", 6)
    for i, (label, cat, shown) in enumerate([
            ("Must-haves — table stakes", "Must-have", "0"),
            ("Performance — scale with investment", "Performance", "1"),
            ("Delighters — differentiators", "Delighter", "0"),
            ("Indifferent — stop spending here", "Indifferent", "0")], start=28):
        ws.cell(row=i, column=1, value=label).font = F_B
        ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=3)
        mark(ws, i, 4, "calc").value = f'=COUNTIF($D$7:$D$25,"{cat}")'
        SHOWN[("Kano analysis", f"D{i}")] = shown
    # red = you get no credit for it and all the blame without it;
    # blue = worth scaling; green = worth a little; grey = worth nothing
    bar(ws, "Where your requirements fall — and which ones are worth money",
        Reference(ws, min_col=1, min_row=28, max_row=31),
        Reference(ws, min_col=4, min_row=28, max_row=31), "G7",
        colours=["C0392B", "1F4E79", "3F8F5A", "9AA4B2"])
    ws.merge_cells("A33:F33")
    ws.cell(row=33, column=1, value="Speed in support is usually a must-have: being twice as fast wins you nothing "
            "once you are fast enough, while being slow loses you everything. Spending your improvement budget on a "
            "must-have that is already met is the most common way to move a metric and change nothing.").font = F_NOTE
    howto(wb, LEGEND + [
        (True, "What this is for"),
        (False, "Deciding which customer requirements are worth investment, instead of assuming more of everything is better."),
        (True, "How to run it"),
        (False, "For each requirement ask two questions of real customers: how do you feel if it IS present, and how "
                "do you feel if it is NOT. The pair of answers gives you the category automatically."),
        (True, "Reading the categories"),
        (False, "Must-have: absence is punished, presence earns nothing. Performance: satisfaction scales with it. "
                "Delighter: absence is forgiven, presence wins goodwill. Indifferent: stop spending."),
    ])
    return wb, "23-kano-analysis.xlsx"


# --------------------------------------------------------------------- 24 DOE
def doe():
    wb = Workbook(); wb.remove(wb.active)
    ws = wb.create_sheet("2^3 design")
    title(ws, "Design of Experiments — 2³ full factorial",
          "Change several things at once in a planned pattern, so you can see interactions one-at-a-time testing can never find.", 9)
    widths(ws, [8, 14, 14, 14, 18, 18, 18, 16, 30])
    band(ws, 4, "YOUR FACTORS — name them and set the two levels you will actually run", 9)
    for i, (f, lo, hi) in enumerate([("Routing rule", "Current", "Skill-based"),
                                     ("Authority limit", "$50", "$250"),
                                     ("Article shown", "No", "Yes")], start=5):
        # chr(63 + i - 4) started at '@': the matrix columns are A, B, C, so a
        # factor labelled '@' pointed at nothing
        ws.cell(row=i, column=1, value=f"Factor {chr(64 + i - 4)}").font = F_B
        mark(ws, i, 2, "in").value = f
        note(ws, i, 2, "Name the factor as the team says it out loud. It must be something you can "
                       "actually set to either level for the whole run — if you cannot control it, "
                       "it is noise to block or stratify, not a factor.")
        note(ws, i, 6, "The level you run today. Keep one arm at current practice so the experiment "
                       "still tells you whether changing anything was worth it.")
        note(ws, i, 8, "The level you are testing. Push it far enough to move the response — a timid "
                       "high level is the most common reason a DOE returns nothing.")
        ws.merge_cells(start_row=i, start_column=2, end_row=i, end_column=4)
        ws.cell(row=i, column=5, value="Low (−1)").font = F_NOTE
        mark(ws, i, 6, "in").value = lo
        ws.cell(row=i, column=7, value="High (+1)").font = F_NOTE
        mark(ws, i, 8, "in").value = hi
    header(ws, 9, ["Run", "A", "B", "C", "AB", "AC", "BC", "Response", "Notes"])
    design = [(-1, -1, -1), (1, -1, -1), (-1, 1, -1), (1, 1, -1),
              (-1, -1, 1), (1, -1, 1), (-1, 1, 1), (1, 1, 1)]
    resp = [412, 388, 401, 372, 395, 366, 380, 344]
    for i, (a, bq, c) in enumerate(design):
        r = 10 + i
        ws.cell(row=r, column=1, value=i + 1).font = F_B
        for col, v in zip((2, 3, 4), (a, bq, c)):
            cc = ws.cell(row=r, column=col, value=v); cc.fill = CALC; cc.font = F_CALC; cc.border = THIN
            cc.alignment = Alignment(horizontal="center")
        for col, f in [(5, f"=B{r}*C{r}"), (6, f"=B{r}*D{r}"), (7, f"=C{r}*D{r}")]:
            mark(ws, r, col, "calc").value = f
            SHOWN[("2^3 design", f"{get_column_letter(col)}{r}")] = str(
                {5: a * bq, 6: a * c, 7: bq * c}[col])
        e = mark(ws, r, 8, "in"); e.value = resp[i]
        e.alignment = Alignment(horizontal="center")
        mark(ws, r, 9, "in")
    band(ws, 19, "EFFECTS — how much each factor moves the response", 9)
    eff = [("Effect of A", "B", 2), ("Effect of B", "C", 3), ("Effect of C", "D", 4),
           ("Interaction AB", "E", 5), ("Interaction AC", "F", 6), ("Interaction BC", "G", 7)]
    vals = {}
    for a_, b_, c_ in [(0, 0, 0)]:
        pass
    import statistics
    cols = {2: [d[0] for d in design], 3: [d[1] for d in design], 4: [d[2] for d in design]}
    cols[5] = [d[0] * d[1] for d in design]
    cols[6] = [d[0] * d[2] for d in design]
    cols[7] = [d[1] * d[2] for d in design]
    for label, letter, idx in eff:
        r = 20 + [e[0] for e in eff].index(label)
        ws.cell(row=r, column=1, value=label).font = F_B
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
        f = f"=SUMPRODUCT({letter}10:{letter}17,$I$10:$I$17)/4"
        cc = mark(ws, r, 4, "calc"); cc.value = f.replace("$I$", "$H$")
        v = sum(s * y for s, y in zip(cols[idx], resp)) / 4
        SHOWN[("2^3 design", f"D{r}")] = f"{v:.1f}"
        ws.merge_cells(start_row=r, start_column=5, end_row=r, end_column=9)
        ws.cell(row=r, column=5, value="Bigger absolute value = bigger effect. A large interaction means the two "
                "factors cannot be set independently.").font = F_NOTE
    # A..I are merged across the effects block, so the reference column goes
    # to the right of everything the sheet already uses
    for r in range(20, 26):
        c = ws.cell(row=r, column=11)
        c.value = "=-AVERAGE(ABS($D$23),ABS($D$24),ABS($D$25))"
        c.number_format = "#,##0.0"
        c.font = F_NOTE
        SHOWN[("2^3 design", f"K{r}")] = "-2.8"
    ws.cell(row=19, column=11, value="Noise floor").font = F_NOTE
    ws.column_dimensions["K"].width = 11         # visible: charts skip hidden cells
    de = bar(ws, "Effect size — which factor actually moved the response",
             Reference(ws, min_col=1, min_row=20, max_row=25),
             Reference(ws, min_col=4, min_row=20, max_row=25), "M5", horizontal=True)
    overlay(de, ws, Reference(ws, min_col=11, min_row=20, max_row=25),
            "Noise floor — the mean interaction, anything smaller is nothing")
    ws.merge_cells("A27:I27")
    ws.cell(row=27, column=1, value="Randomise the run order before you execute, and repeat the whole design if you "
            "can afford it. Eight runs with no replication tells you about size, not about noise.").font = F_NOTE
    howto(wb, LEGEND + [
        (True, "What this is for"),
        (False, "Finding the best combination of settings, and detecting interactions — where two changes together do "
                "something neither does alone. One-factor-at-a-time testing cannot see those at all."),
        (True, "How to use it"),
        (False, "Name three factors and their two levels. Run all eight combinations in randomised order and enter the "
                "response you measured. The effects table then tells you which factor moved it and by how much."),
        (True, "In support"),
        (False, "Factors are things like routing rule, authority limit, whether an article is shown, script version. "
                "The response is handle time, resolution rate or satisfaction."),
        (True, "The trap"),
        (False, "Run the design as designed. Dropping the combinations that look silly destroys the balance the whole "
                "method depends on and the effects become uninterpretable."),
    ])
    return wb, "24-doe-design-matrix.xlsx"


# ------------------------------------------------- 25 pareto and distribution
def pareto():
    wb = Workbook(); wb.remove(wb.active)
    ws = wb.create_sheet("Pareto")
    title(ws, "Pareto — where the bulk of the problem actually sits",
          "Ranked categories with a running cumulative share, so you can see how much of the problem the top few explain.", 5)
    widths(ws, [40, 12, 11, 9, 34, 3, 7, 40, 12, 13, 11])
    header(ws, 4, ["Category", "Count", "Share", "Rank", "Validated by reading tickets?"])
    data = [("Adjustment not posted at closure", 412), ("Wrong plan applied", 233),
            ("Duplicate charge", 151), ("Proration misunderstood", 96), ("Refund timing", 74)]
    total = sum(d[1] for d in data)

    # A Pareto is sorted by definition. The cumulative used to be a running sum
    # down the rows, which is only a Pareto if the user happens to type their
    # categories in descending order — and if they do not, the 80% line names
    # the wrong vital few, confidently. Type them in any order now: the ranked
    # block to the right sorts itself, and the chart reads that.
    RANKF = ('=IF(B{r}="","",RANK(B{r},$B$5:$B$24,0)+COUNTIF($B$5:B{r},B{r})-1)')
    for i, (name, n) in enumerate(data):
        r = 5 + i
        c = mark(ws, r, 1, "ex" if i == 0 else "in"); c.value = name
        c2 = mark(ws, r, 2, "ex" if i == 0 else "in"); c2.value = n
        sh = mark(ws, r, 3, "calc")
        sh.value = f'=IF(OR(B{r}="",SUM($B$5:$B$24)=0),"",B{r}/SUM($B$5:$B$24))'
        sh.number_format = "0.0%"
        rk = mark(ws, r, 4, "calc"); rk.value = RANKF.format(r=r); rk.number_format = "0"
        if i == 0:
            sh.fill = EX; rk.fill = EX
        SHOWN[("Pareto", f"C{r}")] = f"{n/total*100:.1f}%"
        SHOWN[("Pareto", f"D{r}")] = str(i + 1)
        mark(ws, r, 5, "ex" if i == 0 else "in")
    for r in range(10, 25):
        for cc in [1, 2, 5]:
            mark(ws, r, cc, "in")
        sh = mark(ws, r, 3, "calc")
        sh.value = f'=IF(OR(B{r}="",SUM($B$5:$B$24)=0),"",B{r}/SUM($B$5:$B$24))'
        sh.number_format = "0.0%"
        rk = mark(ws, r, 4, "calc"); rk.value = RANKF.format(r=r); rk.number_format = "0"
        SHOWN[("Pareto", f"C{r}")] = ""
        SHOWN[("Pareto", f"D{r}")] = ""
    dv = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
    ws.add_data_validation(dv); dv.add("E5:E24")

    # ---- the ranked block the chart actually plots ----------------------
    ws.cell(row=3, column=7, value="RANKED — this is what the chart plots. "
            "Type above in any order; this sorts itself.").font = F_BAND
    for c in range(7, 12):
        ws.cell(row=3, column=c).fill = BAND
    # not header(), which writes every column in the row and would blank the
    # input block's own headers in A4:E4
    for col, lab in ((7, "#"), (8, "Category"), (9, "Count"),
                     (10, "Cumulative"), (11, "80% line")):
        c = ws.cell(row=4, column=col, value=lab)
        c.fill, c.font = HDR, F_HDR
        c.alignment = Alignment(wrap_text=True, vertical="center")
    run = 0
    for i in range(20):
        r = 5 + i
        ws.cell(row=r, column=7, value=i + 1).font = F_NOTE
        for col, f, fmt in [
            (8, f'=IFERROR(INDEX($A$5:$A$24,MATCH(G{r},$D$5:$D$24,0)),"")', "General"),
            (9, f'=IFERROR(INDEX($B$5:$B$24,MATCH(G{r},$D$5:$D$24,0)),"")', "#,##0"),
            (10, f'=IF(I{r}="","",SUM($I$5:I{r})/SUM($I$5:$I$24))', "0.0%"),
            (11, f'=IF(I{r}="","",0.8)', "0%"),
        ]:
            c = mark(ws, r, col, "calc"); c.value = f; c.number_format = fmt
        if i < len(data):
            run += data[i][1]
            SHOWN[("Pareto", f"H{r}")] = data[i][0]
            SHOWN[("Pareto", f"I{r}")] = f"{data[i][1]:,}"
            SHOWN[("Pareto", f"J{r}")] = f"{run/total*100:.1f}%"
            SHOWN[("Pareto", f"K{r}")] = "80%"
        else:
            for col in "HIJK":
                SHOWN[("Pareto", f"{col}{r}")] = ""
    band(ws, 26, "SUMMARY", 5)
    for i, (label, f, shown) in enumerate([
            ("Total", '=SUM(B5:B24)', f"{total:,}"),
            ("Categories", '=COUNTA(A5:A24)', str(len(data))),
            # the top three by RANK, not the top three rows somebody happened
            # to type first
            ("Share explained by the top three", '=IFERROR(SUM(I5:I7)/SUM(I5:I24),"")',
             f"{sum(d[1] for d in data[:3])/total*100:.1f}%")], start=27):
        ws.cell(row=i, column=1, value=label).font = F_B
        ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=2)
        c = mark(ws, i, 3, "calc"); c.value = f
        if "%" in shown: c.number_format = "0.0%"
        SHOWN[("Pareto", f"C{i}")] = shown
    pc = BarChart(); pc.type = "col"; pc.style = 10
    pc.title = "Pareto — ranked, with cumulative share"
    pc.height, pc.width = 9, 19
    pc.gapWidth = 40
    pc.legend = None
    pc.legend = Legend()
    pc.legend.position = "b"
    pc.add_data(Reference(ws, min_col=9, min_row=5, max_row=14), titles_from_data=False)
    pc.set_categories(Reference(ws, min_col=8, min_row=5, max_row=14))
    for ser in pc.series:
        ser.invertIfNegative = False
        ser.graphicalProperties.solidFill = "1F4E79"
        ser.tx = SeriesLabel(v="Count")
    pc.y_axis.title = "Count"
    line = LineChart()
    line.add_data(Reference(ws, min_col=10, min_row=5, max_row=14), titles_from_data=False)
    line.series[0].tx = SeriesLabel(v="Cumulative share")
    line.add_data(Reference(ws, min_col=11, min_row=5, max_row=14), titles_from_data=False)
    line.series[1].tx = SeriesLabel(v="80% — the vital few are left of here")
    line.series[1].graphicalProperties.line.dashStyle = "dash"
    line.series[1].graphicalProperties.line.solidFill = "C0392B"
    line.series[0].graphicalProperties.line.solidFill = "B45309"
    line.series[0].graphicalProperties.line.width = 24000
    line.y_axis.delete = False
    line.y_axis.axId = 200
    line.y_axis.numFmt = "0%"
    line.y_axis.title = "Cumulative share"
    line.y_axis.crosses = "max"
    pc += line
    ws.add_chart(pc, "G4")
    ws.merge_cells("A31:E31")
    ws.cell(row=31, column=1, value="A Pareto inherits the quality of your categories. Disposition codes are chosen "
            "by agents under time pressure, so a Pareto of them ranks your data-entry habits as much as your problems. "
            "Read 50 tickets in the top bar before you size a business case on it — that is what the last column is for.").font = F_NOTE

    ws2 = wb.create_sheet("Shape and spread")
    ws2.sheet_view.showGridLines = False
    title(ws2, "Is this data the shape you assumed?",
          "Support durations are right-skewed. The mean flatters you; the median and p90 do not.", 4)
    widths(ws2, [34, 18, 18, 60])
    ws2.cell(row=4, column=1, value="Paste your values into column B").font = F_NOTE
    header(ws2, 5, ["Statistic", "Value", "", "What it tells you"])
    stats = [("Count", '=COUNT($B$20:$B$1000)', "0"),
             ("Mean", '=IFERROR(AVERAGE($B$20:$B$1000),"")', ""),
             ("Median (p50)", '=IFERROR(MEDIAN($B$20:$B$1000),"")', ""),
             ("p90", '=IFERROR(PERCENTILE($B$20:$B$1000,0.9),"")', ""),
             ("Standard deviation", '=IFERROR(STDEV($B$20:$B$1000),"")', ""),
             ("Interquartile range", '=IFERROR(QUARTILE($B$20:$B$1000,3)-QUARTILE($B$20:$B$1000,1),"")', ""),
             ("Mean ÷ median", '=IFERROR(AVERAGE($B$20:$B$1000)/MEDIAN($B$20:$B$1000),"")', "")]
    notes = ["How many values you pasted.",
             "Dragged upward by the long tail. Rarely the number to quote.",
             "The typical experience. Quote this.",
             "What your worst-served customers get. This is what generates complaints.",
             "Assumes symmetry, so it describes skewed data poorly.",
             "The middle half. A better spread measure for this data.",
             "Above about 1.2 means meaningful right skew — use non-parametric tests and quote percentiles."]
    for i, ((label, f, shown), note) in enumerate(zip(stats, notes), start=6):
        ws2.cell(row=i, column=1, value=label).font = F_B
        c = mark(ws2, i, 2, "calc"); c.value = f; c.number_format = "#,##0.00"
        SHOWN[("Shape and spread", f"B{i}")] = shown
        n = ws2.cell(row=i, column=4, value=note); n.font = F_NOTE
        n.alignment = Alignment(wrap_text=True, vertical="top")
    band(ws2, 14, "VERDICT", 4)
    c = mark(ws2, 14, 1, "calc")
    ws2.merge_cells("A15:D15")
    v = ws2.cell(row=15, column=1)
    v.value = ('=IF(COUNT($B$20:$B$1000)=0,"Paste your data into column B below.",'
               'IF(AVERAGE($B$20:$B$1000)/MEDIAN($B$20:$B$1000)>1.2,'
               '"RIGHT-SKEWED — quote the median and p90, and prefer non-parametric tests.",'
               '"ROUGHLY SYMMETRIC — the mean and a parametric test are defensible."))')
    v.fill, v.font = CALC, F_CALC
    SHOWN[("Shape and spread", "A15")] = "Paste your data into column B below."
    ws2.cell(row=18, column=1, value="Your data").font = F_B
    ws2.cell(row=19, column=2, value="Values ↓").font = F_NOTE
    for r in range(20, 60):
        mark(ws2, r, 2, "in")
    howto(wb, LEGEND + [
        (True, "What this is for"),
        (False, "Two things you should do before any analysis: find out where the bulk of the problem is, and find out "
                "what shape your data actually has."),
        (True, "Pareto tab"),
        (False, "Enter categories and counts. Share and cumulative calculate themselves. The last column is the one "
                "people skip — validate the top category by reading tickets before you build a case on it."),
        (True, "Shape and spread tab"),
        (False, "Paste raw values into column B. The verdict tells you whether your data is skewed enough that the "
                "mean and a t-test would mislead you. Support durations almost always are."),
    ])
    return wb, "25-pareto-and-distribution.xlsx"


# ------------------------------------------------------------ 26 flow and WIP
def flow():
    wb = Workbook(); wb.remove(wb.active)
    ws = wb.create_sheet("WIP and lead time")
    title(ws, "Kanban sizing — pick a wait, get the WIP limit",
          "Little's Law is arithmetic, not a theory. If the closing rate is fixed and you want shorter waits, you must cap the work in progress.", 4)
    widths(ws, [40, 18, 18, 64])
    band(ws, 4, "YOUR NUMBERS", 4)
    inputs = [("Open items right now", 4200, "Live count from your ticketing system, same time of day each time."),
              ("Items closed per day", 1100, "Average daily closing rate over a stable period."),
              ("Lead time you want to promise (days)", 2, "What you want customers to wait."),
              ("Agents working this queue", 40, "Used to turn the queue-level cap into a per-agent limit.")]
    for i, (label, v, note) in enumerate(inputs, start=5):
        ws.cell(row=i, column=1, value=label).font = F_B
        mark(ws, i, 2, "in").value = v
        n = ws.cell(row=i, column=4, value=note); n.font = F_NOTE
        n.alignment = Alignment(wrap_text=True, vertical="top")
    band(ws, 10, "WHAT THAT MEANS", 4)
    outs = [("Lead time today (days)", '=IFERROR(B5/B6,"")', "3.82",
             "Backlog ÷ closing rate. Nothing else affects it."),
            ("Lead time today (hours)", '=IFERROR(B5/B6*24,"")', "91.6", ""),
            ("Backlog cap to hit your target", '=IFERROR(B6*B7,"")', "2,200",
             "This is your queue-level WIP limit."),
            ("Backlog you must remove first", '=IFERROR(MAX(0,B5-B6*B7),"")', "2,000",
             "Until this is cleared the cap cannot hold."),
            ("WIP limit per agent", '=IFERROR(ROUND(B6*B7/B8,0),"")', "55",
             "Enforce this in the tool, not in a briefing. A limit nobody can exceed is a control; a limit in a "
             "document is a suggestion."),
            ("Days to clear the excess at current rate", '=IFERROR(MAX(0,B5-B6*B7)/B6,"")', "1.82",
             "Assumes arrivals stop, which they will not — plan a temporary lift in closing rate instead.")]
    for i, (label, f, shown, note) in enumerate(outs, start=11):
        ws.cell(row=i, column=1, value=label).font = F_B
        c = mark(ws, i, 2, "calc"); c.value = f; c.number_format = "#,##0.00"
        SHOWN[("WIP and lead time", f"B{i}")] = shown
        if note:
            n = ws.cell(row=i, column=4, value=note); n.font = F_NOTE
            n.alignment = Alignment(wrap_text=True, vertical="top")
            ws.row_dimensions[i].height = 28
    ws.cell(row=21, column=1, value="Lead time today").font = F_B
    c = mark(ws, 21, 2, "calc"); c.value = "=B11"; c.number_format = "#,##0.00"
    ws.cell(row=22, column=1, value="Lead time promised").font = F_B
    c = mark(ws, 22, 2, "calc"); c.value = "=B7"; c.number_format = "#,##0.00"
    SHOWN[("WIP and lead time", "B21")] = "3.82"
    SHOWN[("WIP and lead time", "B22")] = "2.00"
    bar(ws, "Where you are against what you promised (days)",
        Reference(ws, min_col=1, min_row=21, max_row=22),
        Reference(ws, min_col=2, min_row=21, max_row=22), "F5",
        colours=["C0392B", "3F8F5A"])
    ws.merge_cells("A19:D19")
    ws.cell(row=19, column=1, value="There is no third option. If you cannot cap the work and cannot raise the "
            "closing rate, the wait will not fall — and saying so early is more useful than promising otherwise.").font = F_NOTE
    howto(wb, LEGEND + [
        (True, "What this is for"),
        (False, "Turning a lead-time promise into a work-in-progress limit you can actually enforce."),
        (True, "How to use it"),
        (False, "Enter your open count, your closing rate and the wait you want to promise. The cap that follows is "
                "arithmetic — Little's Law — not an opinion."),
        (True, "The part people skip"),
        (False, "You usually have to clear the excess backlog before the cap can hold. Plan that as a separate push "
                "with a start and an end, or the limit gets abandoned in week one."),
    ])
    return wb, "26-kanban-and-wip.xlsx"



# --------------------------------------------------------------------------
# Control charts. The program's chart-selection table names seven chart types
# and, until now, nothing in the repo produced one. This builds all seven off
# your own numbers, with the limits as live formulas so you can see the maths.
# --------------------------------------------------------------------------

def bounds(*seqs, pad=0.10):
    """Axis min/max that frame the data instead of crushing it against the top.

    Left to auto-scale, a control chart of values around 415 with limits at 363
    and 470 renders on a 0-500 axis in most viewers: every point sits in the top
    fifth and the variation you are supposed to be reading is invisible.
    """
    vals = [float(v) for seq in seqs for v in seq
            if isinstance(v, (int, float)) and v == v]
    if not vals:
        return None, None
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or (abs(hi) or 1.0)
    lo -= span * pad
    hi += span * pad
    if min(vals) >= 0 and lo < 0:
        lo = 0.0                       # counts and durations never go negative
    return lo, hi


def spc_chart(ws, title_, cats, series_defs, anchor, y_title="", pct=False,
              height=8, width=19, ylim=None):
    """A control chart: the data as marked points, the limits as flat lines."""
    ch = LineChart()
    ch.title = title_
    ch.style = 2
    ch.height, ch.width = height, width
    if y_title:
        ch.y_axis.title = y_title      # setting this to "" writes the text "None"
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    if ylim and ylim[0] is not None:
        ch.y_axis.scaling.min, ch.y_axis.scaling.max = ylim
    if pct:
        ch.y_axis.numFmt = "0.0%"
    for ref, name, colour, dashed, marker in series_defs:
        sr = Series(ref, title=name)
        lp = sr.graphicalProperties.line
        lp.solidFill = colour
        lp.width = 28000 if not dashed else 16000
        if dashed:
            lp.dashStyle = "dash"
        if marker:
            sr.marker = Marker(symbol="circle", size=6)
            sr.marker.graphicalProperties.solidFill = colour
        else:
            sr.marker = Marker(symbol="none")
        sr.smooth = False
        ch.series.append(sr)
    ch.set_categories(cats)
    ws.add_chart(ch, anchor)
    return ch


N_PTS = 24                       # 24 periods is enough to set honest limits
BASE_N = 12                      # baseline window for EWMA/CUSUM: the "before" period


def _mrbar(seq):
    """Average moving range — the short-term sigma estimator every chart here uses."""
    return sum(abs(seq[i] - seq[i - 1]) for i in range(1, len(seq))) / (len(seq) - 1)


def _laney(ns, ks, poisson=False):
    """p-bar (or u-bar), sigma-z and the per-point sigma, exactly as the sheet computes them."""
    pbar = sum(ks) / float(sum(ns))
    sig = [((pbar / n) ** 0.5) if poisson else ((pbar * (1 - pbar) / n) ** 0.5) for n in ns]
    z = [((ks[i] / float(ns[i])) - pbar) / sig[i] for i in range(len(ns))]
    return pbar, sig, z, max(1.0, _mrbar(z) / 1.128)


def _spc_stats(ws, rows, width):
    """The stats band every control-chart tab opens with."""
    band(ws, 4, "The maths, calculated from your data — nothing here is hard-coded", width)
    ws.column_dimensions["A"].width = max(ws.column_dimensions["A"].width or 0, 32)
    r = 5
    for label, formula, fmt, note in rows:
        ws.cell(row=r, column=1, value=label).font = F_B
        c = mark(ws, r, 2, "calc")
        c.value = formula
        c.number_format = fmt
        if note:
            # one narrow column cannot hold a sentence; span the rest of the row
            ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=width)
            n = ws.cell(row=r, column=3, value=note)
            n.font = F_NOTE
            n.alignment = Alignment(wrap_text=True, vertical="center")
            ws.row_dimensions[r].height = 15 * (1 + len(note) // 95)
        r += 1
    return r


def control_charts():
    """27 — every chart type the selection table sends you to."""
    wb = Workbook()
    wb.remove(wb.active)

    # ---- I-MR -----------------------------------------------------------
    ws = wb.create_sheet("I-MR")
    title(ws, "Individuals and Moving Range (I-MR)",
          "One number per day or week — daily AHT, daily backlog, weekly SLA%. "
          "Not for raw per-contact durations: those are heavily skewed and the limits will lie to you.", 9)
    widths(ws, [16, 13, 14, 11, 11, 11, 11, 11, 20])
    _spc_stats(ws, [
        ("Points with data", "=COUNT(B14:B37)", "0", "Fewer than 20 and the limits are provisional."),
        ("Centre line (mean)", "=AVERAGE(B14:B37)", "#,##0.00", "The process average over the baseline window."),
        ("Average moving range", "=AVERAGE(C15:C37)", "#,##0.00", "Mean gap between consecutive points — this is your short-term variation."),
        ("Sigma estimate", "=B7/1.128", "#,##0.00", "MR-bar / 1.128. Uses only point-to-point movement, so a slow drift does not widen the limits."),
        ("Upper control limit", "=B6+2.66*B7", "#,##0.00", "2.66 = 3 / 1.128. Same thing as mean + 3 sigma."),
        ("Lower control limit", "=B6-2.66*B7", "#,##0.00", "If this goes below zero on a count, treat the lower limit as zero."),
        ("Moving-range UCL", "=3.267*B7", "#,##0.00", "A point above this means the process jumped between two periods."),
    ], 9)
    band(ws, 12, "Your data — one row per period, oldest first", 9)
    header(ws, 13, ["Period", "Value", "Moving range", "CL", "UCL", "LCL", "MR CL", "MR UCL", "Signal"])
    vals = [408, 415, 402, 431, 419, 396, 424, 410, 438, 405, 417, 429,
            401, 422, 413, 407, 435, 398, 420, 411, 442, 404, 416, 428]
    for i in range(N_PTS):
        r = 14 + i
        ws.cell(row=r, column=1, value="Day %d" % (i + 1))
        c = mark(ws, r, 2, "in" if i else "ex")
        c.value = vals[i]
        c.number_format = "#,##0.00"
        if i:
            f = mark(ws, r, 3, "calc")
            f.value = "=IF(COUNT(B%d:B%d)=2,ABS(B%d-B%d),\"\")" % (r - 1, r, r, r - 1)
            f.number_format = "#,##0.00"
            SHOWN[("I-MR", "C%d" % r)] = "%.2f" % abs(vals[i] - vals[i - 1])
        for col, ref in ((4, "$B$6"), (5, "$B$9"), (6, "$B$10"), (7, "$B$7"), (8, "$B$11")):
            g = mark(ws, r, col, "calc")
            g.value = "=IF(B%d=\"\",\"\",%s)" % (r, ref)
            g.number_format = "#,##0.00"
        sg = mark(ws, r, 9, "calc")
        if i >= 7:
            # the run rule needs eight rows of history; before row 21 the window
            # would reach up into the banded header, which is merged and empty
            sg.value = ("=IF(B{r}=\"\",\"\",IF(OR(B{r}>$B$9,B{r}<$B$10),\"OUT OF CONTROL\","
                        "IF(AND(COUNT(B{p8}:B{r})=8,OR(MIN(B{p8}:B{r})>$B$6,MAX(B{p8}:B{r})<$B$6)),"
                        "\"8 in a row one side — shift\",\"\")))").format(r=r, p8=r - 7)
        else:
            sg.value = ("=IF(B{r}=\"\",\"\",IF(OR(B{r}>$B$9,B{r}<$B$10),"
                        "\"OUT OF CONTROL\",\"\"))").format(r=r)
    mu = sum(vals) / float(len(vals))
    mrb = _mrbar(vals)
    SHOWN.update({("I-MR", "B5"): "%d" % N_PTS, ("I-MR", "B6"): "%.2f" % mu,
                  ("I-MR", "B7"): "%.2f" % mrb, ("I-MR", "B8"): "%.2f" % (mrb / 1.128),
                  ("I-MR", "B9"): "%.2f" % (mu + 2.66 * mrb), ("I-MR", "B10"): "%.2f" % (mu - 2.66 * mrb),
                  ("I-MR", "B11"): "%.2f" % (3.267 * mrb)})
    for k, v in (("D", mu), ("E", mu + 2.66 * mrb), ("F", mu - 2.66 * mrb), ("G", mrb), ("H", 3.267 * mrb)):
        for i in range(N_PTS):
            SHOWN[("I-MR", "%s%d" % (k, 14 + i))] = "%.2f" % v
    cats = Reference(ws, min_col=1, min_row=14, max_row=37)
    spc_chart(ws, "Individuals — is the process stable?", cats, [
        (Reference(ws, min_col=2, min_row=14, max_row=37), "Value", "1F4E79", False, True),
        (Reference(ws, min_col=4, min_row=14, max_row=37), "Centre line", "3F8F5A", False, False),
        (Reference(ws, min_col=5, min_row=14, max_row=37), "UCL", "C0392B", True, False),
        (Reference(ws, min_col=6, min_row=14, max_row=37), "LCL", "C0392B", True, False),
    ], "K4", ylim=bounds(vals, [mu - 2.66 * mrb, mu + 2.66 * mrb]))
    spc_chart(ws, "Moving range — did it jump between periods?", cats, [
        (Reference(ws, min_col=3, min_row=14, max_row=37), "Moving range", "6B4FA0", False, True),
        (Reference(ws, min_col=7, min_row=14, max_row=37), "MR centre line", "3F8F5A", False, False),
        (Reference(ws, min_col=8, min_row=14, max_row=37), "MR UCL", "C0392B", True, False),
    ], "K22", height=7,
        ylim=bounds([abs(vals[i] - vals[i - 1]) for i in range(1, len(vals))], [0, 3.267 * mrb]))

    # ---- Laney p' -------------------------------------------------------
    ws = wb.create_sheet("Laney p-prime")
    title(ws, "Laney p\u2032 chart — the default for support percentages",
          "FCR%, SLA met%, QA pass%, reopen%. At thousands of contacts a day an ordinary p-chart's limits are "
          "far too tight and almost every point looks out of control — until the team stops looking at the chart.", 9)
    widths(ws, [14, 14, 13, 11, 12, 10, 11, 11, 22])
    _spc_stats(ws, [
        ("Overall proportion (p-bar)", "=SUM(C14:C37)/SUM(B14:B37)", "0.00%",
         "Total defectives / total opportunities — NOT the average of the daily percentages."),
        ("Average moving range of z", "=AVERAGE(G15:G37)", "#,##0.000",
         "How much the standardised points move period to period."),
        ("Sigma z (Laney adjustment)", "=MAX(1,B6/1.128)", "#,##0.000",
         "This is the whole trick. Sigma z = 1 means no overdispersion and this collapses to an ordinary p-chart. "
         "Above about 1.2 you had a real problem."),
        ("Ordinary p-chart limits would be", "=\"\u00b1\"&TEXT(3*SQRT(B5*(1-B5)/AVERAGE(B14:B37)),\"0.00%\")",
         "@", "Compare with the Laney limits in the chart. This is why the old chart cried wolf."),
    ], 9)
    band(ws, 12, "Your data — one row per day", 9)
    header(ws, 13, ["Day", "Contacts (n)", "Met / passed", "Proportion", "Sigma p", "z", "MR of z", "", "Signal"])
    ws.cell(row=13, column=8, value="").fill = HDR
    ns = [7820, 8140, 7960, 8310, 7690, 8020, 8450, 7880, 8210, 7740, 8090, 8380,
          7930, 8260, 7810, 8150, 8470, 7860, 8030, 8340, 7900, 8180, 7770, 8240]
    ks = [5610, 5990, 5570, 6120, 5410, 5880, 6210, 5490, 6050, 5380, 5940, 6180,
          5520, 6010, 5480, 5860, 6240, 5600, 5760, 6090, 5710, 5900, 5450, 6020]
    pbar, sigs, zs, sz = _laney(ns, ks)
    SHOWN.update({("Laney p-prime", "B5"): "%.2f%%" % (100 * pbar),
                  ("Laney p-prime", "B6"): "%.3f" % _mrbar(zs),
                  ("Laney p-prime", "B7"): "%.3f" % sz,
                  ("Laney p-prime", "B8"): "\u00b1%.2f%%" % (
                      100 * 3 * (pbar * (1 - pbar) / (sum(ns) / float(len(ns)))) ** 0.5)})
    for i in range(N_PTS):
        r = 14 + i
        ws.cell(row=r, column=1, value="Day %d" % (i + 1))
        for col, v in ((2, ns[i]), (3, ks[i])):
            c = mark(ws, r, col, "in" if i else "ex")
            c.value = v
            c.number_format = "#,##0"
        p = mark(ws, r, 4, "calc"); p.value = "=IF(B%d=\"\",\"\",C%d/B%d)" % (r, r, r); p.number_format = "0.00%"
        sp = mark(ws, r, 5, "calc"); sp.value = "=IF(B%d=\"\",\"\",SQRT($B$5*(1-$B$5)/B%d))" % (r, r); sp.number_format = "0.0000"
        z = mark(ws, r, 6, "calc"); z.value = "=IF(B%d=\"\",\"\",(D%d-$B$5)/E%d)" % (r, r, r); z.number_format = "#,##0.00"
        if i:
            m = mark(ws, r, 7, "calc"); m.value = "=IF(COUNT(F%d:F%d)=2,ABS(F%d-F%d),\"\")" % (r - 1, r, r, r - 1); m.number_format = "#,##0.00"
        sg = mark(ws, r, 9, "calc")
        sg.value = "=IF(D{r}=\"\",\"\",IF(OR(D{r}>K{r},D{r}<L{r}),\"OUT OF CONTROL\",\"\"))".format(r=r)
        SHOWN[("Laney p-prime", "D%d" % r)] = "%.2f%%" % (100.0 * ks[i] / ns[i])
        SHOWN[("Laney p-prime", "E%d" % r)] = "%.4f" % sigs[i]
        SHOWN[("Laney p-prime", "F%d" % r)] = "%.2f" % zs[i]
    # limit columns live off to the right so the chart has something flat to plot
    ws.cell(row=13, column=11, value="UCL").fill = HDR; ws.cell(row=13, column=11).font = F_HDR
    ws.cell(row=13, column=12, value="LCL").fill = HDR; ws.cell(row=13, column=12).font = F_HDR
    ws.cell(row=13, column=13, value="CL").fill = HDR; ws.cell(row=13, column=13).font = F_HDR
    for i in range(N_PTS):
        r = 14 + i
        u = ws.cell(row=r, column=11, value="=IF(B%d=\"\",\"\",MIN(1,$B$5+3*E%d*$B$7))" % (r, r)); u.number_format = "0.00%"
        l = ws.cell(row=r, column=12, value="=IF(B%d=\"\",\"\",MAX(0,$B$5-3*E%d*$B$7))" % (r, r)); l.number_format = "0.00%"
        c = ws.cell(row=r, column=13, value="=IF(B%d=\"\",\"\",$B$5)" % r); c.number_format = "0.00%"
    cats = Reference(ws, min_col=1, min_row=14, max_row=37)
    spc_chart(ws, "Laney p\u2032 — limits that survive 8,000 contacts a day", cats, [
        (Reference(ws, min_col=4, min_row=14, max_row=37), "Proportion", "1F4E79", False, True),
        (Reference(ws, min_col=13, min_row=14, max_row=37), "Centre line", "3F8F5A", False, False),
        (Reference(ws, min_col=11, min_row=14, max_row=37), "UCL", "C0392B", True, False),
        (Reference(ws, min_col=12, min_row=14, max_row=37), "LCL", "C0392B", True, False),
    ], "O4", pct=True,
        ylim=bounds([ks[i] / float(ns[i]) for i in range(N_PTS)],
                    [max(0.0, pbar - 3 * sigs[i] * sz) for i in range(N_PTS)],
                    [pbar + 3 * sigs[i] * sz for i in range(N_PTS)]))

    # ---- Laney u' -------------------------------------------------------
    ws = wb.create_sheet("Laney u-prime")
    title(ws, "Laney u\u2032 chart — defects per unit with varying volume",
          "Defects per 100 contacts, escalations per 1,000 tickets, errors per audit. Same overdispersion problem "
          "as percentages, same fix.", 9)
    widths(ws, [14, 15, 13, 12, 12, 10, 11, 11, 22])
    _spc_stats(ws, [
        ("Overall rate (u-bar)", "=SUM(C14:C37)/SUM(B14:B37)", "#,##0.0000",
         "Total defects / total units. Not the average of the daily rates."),
        ("Average moving range of z", "=AVERAGE(G15:G37)", "#,##0.000", "Movement of the standardised points."),
        ("Sigma z (Laney adjustment)", "=MAX(1,B6/1.128)", "#,##0.000",
         "1.0 means an ordinary u-chart was fine. Above that, it was not. It never drops below 1 — the adjustment "
         "widens limits, it never tightens them."),
        ("Rate per 100 units", "=B5*100", "#,##0.00", "The same number in the units people actually quote."),
    ], 9)
    band(ws, 12, "Your data — one row per week", 9)
    header(ws, 13, ["Week", "Contacts audited", "Defects found", "Rate (u)", "Sigma u", "z", "MR of z", "", "Signal"])
    ws.cell(row=13, column=8, value="").fill = HDR
    us = [1240, 1310, 1180, 1420, 1275, 1195, 1360, 1230, 1405, 1150, 1290, 1375,
          1215, 1330, 1185, 1265, 1440, 1205, 1300, 1355, 1170, 1285, 1225, 1390]
    # the underlying defect rate really does move week to week in an audit
    # programme — that is the overdispersion the Laney adjustment exists for,
    # so the example data has to show it rather than being tidy Poisson noise
    rates = [.031, .052, .036, .058, .033, .049, .041, .056, .030, .047, .038, .054,
             .032, .050, .035, .057, .040, .045, .031, .053, .037, .048, .034, .055]
    ds = [int(round(us[i] * rates[i])) for i in range(N_PTS)]
    ubar, usig, uz, usz = _laney(us, ds, poisson=True)
    SHOWN.update({("Laney u-prime", "B5"): "%.4f" % ubar, ("Laney u-prime", "B6"): "%.3f" % _mrbar(uz),
                  ("Laney u-prime", "B7"): "%.3f" % usz, ("Laney u-prime", "B8"): "%.2f" % (ubar * 100)})
    for i in range(N_PTS):
        r = 14 + i
        ws.cell(row=r, column=1, value="Week %d" % (i + 1))
        for col, v in ((2, us[i]), (3, ds[i])):
            c = mark(ws, r, col, "in" if i else "ex"); c.value = v; c.number_format = "#,##0"
        u = mark(ws, r, 4, "calc"); u.value = "=IF(B%d=\"\",\"\",C%d/B%d)" % (r, r, r); u.number_format = "0.0000"
        su = mark(ws, r, 5, "calc"); su.value = "=IF(B%d=\"\",\"\",SQRT($B$5/B%d))" % (r, r); su.number_format = "0.0000"
        z = mark(ws, r, 6, "calc"); z.value = "=IF(B%d=\"\",\"\",(D%d-$B$5)/E%d)" % (r, r, r); z.number_format = "#,##0.00"
        if i:
            m = mark(ws, r, 7, "calc"); m.value = "=IF(COUNT(F%d:F%d)=2,ABS(F%d-F%d),\"\")" % (r - 1, r, r, r - 1); m.number_format = "#,##0.00"
        sg = mark(ws, r, 9, "calc")
        sg.value = "=IF(D{r}=\"\",\"\",IF(OR(D{r}>K{r},D{r}<L{r}),\"OUT OF CONTROL\",\"\"))".format(r=r)
        SHOWN[("Laney u-prime", "D%d" % r)] = "%.4f" % (ds[i] / float(us[i]))
        SHOWN[("Laney u-prime", "E%d" % r)] = "%.4f" % usig[i]
        SHOWN[("Laney u-prime", "F%d" % r)] = "%.2f" % uz[i]
    for col, lab in ((11, "UCL"), (12, "LCL"), (13, "CL")):
        h = ws.cell(row=13, column=col, value=lab); h.fill, h.font = HDR, F_HDR
    for i in range(N_PTS):
        r = 14 + i
        ws.cell(row=r, column=11, value="=IF(B%d=\"\",\"\",$B$5+3*E%d*$B$7)" % (r, r)).number_format = "0.0000"
        ws.cell(row=r, column=12, value="=IF(B%d=\"\",\"\",MAX(0,$B$5-3*E%d*$B$7))" % (r, r)).number_format = "0.0000"
        ws.cell(row=r, column=13, value="=IF(B%d=\"\",\"\",$B$5)" % r).number_format = "0.0000"
    cats = Reference(ws, min_col=1, min_row=14, max_row=37)
    spc_chart(ws, "Laney u\u2032 — defects per unit", cats, [
        (Reference(ws, min_col=4, min_row=14, max_row=37), "Rate", "1F4E79", False, True),
        (Reference(ws, min_col=13, min_row=14, max_row=37), "Centre line", "3F8F5A", False, False),
        (Reference(ws, min_col=11, min_row=14, max_row=37), "UCL", "C0392B", True, False),
        (Reference(ws, min_col=12, min_row=14, max_row=37), "LCL", "C0392B", True, False),
    ], "O4",
        ylim=bounds([ds[i] / float(us[i]) for i in range(N_PTS)],
                    [max(0.0, ubar - 3 * usig[i] * usz) for i in range(N_PTS)],
                    [ubar + 3 * usig[i] * usz for i in range(N_PTS)]))

    # ---- Xbar-R ---------------------------------------------------------
    ws = wb.create_sheet("Xbar-R")
    title(ws, "Xbar-R chart — subgroups of a continuous metric",
          "Five sampled handle times per day, five audited tickets per analyst. Getting the subgrouping right is "
          "the hard part: everything inside a subgroup must share the same conditions.", 12)
    widths(ws, [12, 9, 9, 9, 9, 9, 11, 10, 11, 11, 11, 22])
    _spc_stats(ws, [
        ("Subgroup size (n)", "=COUNT(B14:F14)", "0", "Change how many observation columns you fill and this follows."),
        ("Grand average (X-double-bar)", "=AVERAGE(G14:G37)", "#,##0.00", "Average of the subgroup averages."),
        ("Average range (R-bar)", "=AVERAGE(H14:H37)", "#,##0.00", "Average within-subgroup spread."),
        ("A2 for this n", "=IFERROR(LOOKUP(B5,{2;3;4;5;6;7;8;9;10},{1.880;1.023;0.729;0.577;0.483;0.419;0.373;0.337;0.308}),\"n out of range\")",
         "#,##0.000", "Standard constant. Above n=8 most people switch to Xbar-S."),
        ("D4 for this n", "=IFERROR(LOOKUP(B5,{2;3;4;5;6;7;8;9;10},{3.267;2.574;2.282;2.114;2.004;1.924;1.864;1.816;1.777}),\"n out of range\")", "#,##0.000", ""),
        ("D3 for this n", "=IFERROR(LOOKUP(B5,{2;3;4;5;6;7;8;9;10},{0;0;0;0;0;0.076;0.136;0.184;0.223}),\"n out of range\")", "#,##0.000", "Zero below n=7 — a range cannot be meaningfully small."),
        ("Xbar UCL / LCL", "=TEXT(B6+B8*B7,\"#,##0.00\")&\"  /  \"&TEXT(B6-B8*B7,\"#,##0.00\")", "@", "Grand average plus or minus A2 x R-bar."),
    ], 12)
    band(ws, 12, "Your data — five observations per subgroup", 12)
    header(ws, 13, ["Subgroup", "Obs 1", "Obs 2", "Obs 3", "Obs 4", "Obs 5",
                    "Average", "Range", "Xbar CL", "Xbar UCL", "Xbar LCL", "Signal"])
    import math as _m
    _avgs, _rngs = [], []
    for i in range(N_PTS):
        r = 14 + i
        ws.cell(row=r, column=1, value="Day %d" % (i + 1))
        base = 400 + 14 * _m.sin(i / 2.4) + (i % 5) * 3
        obs = [round(base + 22 * _m.sin(i * 1.7 + j * 2.1), 0) for j in range(5)]
        for j, v in enumerate(obs):
            c = mark(ws, r, 2 + j, "in" if i else "ex"); c.value = v; c.number_format = "#,##0"
        a = mark(ws, r, 7, "calc"); a.value = "=IF(COUNT(B%d:F%d)=0,\"\",AVERAGE(B%d:F%d))" % (r, r, r, r); a.number_format = "#,##0.00"
        g = mark(ws, r, 8, "calc"); g.value = "=IF(COUNT(B%d:F%d)=0,\"\",MAX(B%d:F%d)-MIN(B%d:F%d))" % (r, r, r, r, r, r); g.number_format = "#,##0.00"
        for col, f in ((9, "$B$6"), (10, "$B$6+$B$8*$B$7"), (11, "$B$6-$B$8*$B$7")):
            c = mark(ws, r, col, "calc"); c.value = "=IF(G%d=\"\",\"\",%s)" % (r, f); c.number_format = "#,##0.00"
        sg = mark(ws, r, 12, "calc")
        sg.value = "=IF(G{r}=\"\",\"\",IF(OR(G{r}>J{r},G{r}<K{r}),\"OUT OF CONTROL\",\"\"))".format(r=r)
        _avgs.append(sum(obs) / 5.0)
        _rngs.append(max(obs) - min(obs))
        SHOWN[("Xbar-R", "G%d" % r)] = "%.2f" % _avgs[-1]
        SHOWN[("Xbar-R", "H%d" % r)] = "%.2f" % _rngs[-1]
    grand = sum(_avgs) / float(len(_avgs))
    rbar = sum(_rngs) / float(len(_rngs))
    SHOWN.update({("Xbar-R", "B5"): "5", ("Xbar-R", "B6"): "%.2f" % grand, ("Xbar-R", "B7"): "%.2f" % rbar,
                  ("Xbar-R", "B8"): "0.577", ("Xbar-R", "B9"): "2.114", ("Xbar-R", "B10"): "0.000",
                  ("Xbar-R", "B11"): "%.2f  /  %.2f" % (grand + 0.577 * rbar, grand - 0.577 * rbar)})
    for i in range(N_PTS):
        for col, v in (("I", grand), ("J", grand + 0.577 * rbar), ("K", grand - 0.577 * rbar)):
            SHOWN[("Xbar-R", "%s%d" % (col, 14 + i))] = "%.2f" % v
    cats = Reference(ws, min_col=1, min_row=14, max_row=37)
    spc_chart(ws, "Xbar — is the average stable?", cats, [
        (Reference(ws, min_col=7, min_row=14, max_row=37), "Subgroup average", "1F4E79", False, True),
        (Reference(ws, min_col=9, min_row=14, max_row=37), "Centre line", "3F8F5A", False, False),
        (Reference(ws, min_col=10, min_row=14, max_row=37), "UCL", "C0392B", True, False),
        (Reference(ws, min_col=11, min_row=14, max_row=37), "LCL", "C0392B", True, False),
    ], "N4", ylim=bounds(_avgs, [grand - 0.577 * rbar, grand + 0.577 * rbar]))
    for i in range(N_PTS):
        r = 14 + i
        ws.cell(row=r, column=14, value="=IF(H%d=\"\",\"\",$B$7)" % r).number_format = "#,##0.00"
        ws.cell(row=r, column=15, value="=IF(H%d=\"\",\"\",$B$9*$B$7)" % r).number_format = "#,##0.00"
        ws.cell(row=r, column=16, value="=IF(H%d=\"\",\"\",$B$10*$B$7)" % r).number_format = "#,##0.00"
    spc_chart(ws, "R — is the spread stable? Read this one first", cats, [
        (Reference(ws, min_col=8, min_row=14, max_row=37), "Subgroup range", "6B4FA0", False, True),
        (Reference(ws, min_col=14, min_row=14, max_row=37), "R centre line", "3F8F5A", False, False),
        (Reference(ws, min_col=15, min_row=14, max_row=37), "R UCL", "C0392B", True, False),
        (Reference(ws, min_col=16, min_row=14, max_row=37), "R LCL", "C0392B", True, False),
    ], "N22", height=7, ylim=bounds(_rngs, [0, 2.114 * rbar]))

    # ---- EWMA -----------------------------------------------------------
    ws = wb.create_sheet("EWMA")
    title(ws, "EWMA — catch a slow slide before it becomes obvious",
          "An ordinary chart is poor at small sustained shifts, which is exactly what a decaying improvement looks "
          "like. Lambda around 0.2 detects a 1-sigma drift in a handful of periods.", 9)
    widths(ws, [14, 13, 13, 12, 12, 12, 11, 11, 22])
    _spc_stats(ws, [
        ("Lambda (weight on the newest point)", 0.2, "0.00",
         "0.05 is very smooth and slow; 0.4 behaves nearly like an ordinary chart. 0.2 is the usual choice."),
        ("L (limit width in sigmas)", 2.7, "0.0", "2.7 with lambda 0.2 gives roughly the same false-alarm rate as a 3-sigma chart."),
        ("Target / process mean", "=AVERAGE(B16:B27)", "#,##0.00",
         "Baseline window only — the first 12 periods. Averaging the whole series folds the very drift you are hunting "
         "into the centre line. Type your own target over this if you have one."),
        ("Average moving range", "=AVERAGE(C17:C27)", "#,##0.00", "Baseline window, same reason."),
        ("Sigma estimate", "=B8/1.128", "#,##0.00", "Short-term variation only — the same estimate the I chart uses."),
    ], 9)
    ws.cell(row=5, column=2).fill = IN
    ws.cell(row=6, column=2).fill = IN
    band(ws, 14, "Your data — one row per period, oldest first", 9)
    header(ws, 15, ["Period", "Value", "Moving range", "EWMA", "CL", "UCL", "LCL", "", "Signal"])
    ws.cell(row=15, column=8, value="").fill = HDR
    drift = [408, 415, 402, 431, 419, 396, 424, 410, 438, 405, 417, 429,
             418, 426, 431, 428, 437, 433, 441, 439, 448, 444, 452, 449]
    for i in range(N_PTS):
        r = 16 + i
        ws.cell(row=r, column=1, value="Day %d" % (i + 1))
        c = mark(ws, r, 2, "in" if i else "ex"); c.value = drift[i]; c.number_format = "#,##0.00"
        if i:
            m = mark(ws, r, 3, "calc"); m.value = "=IF(COUNT(B%d:B%d)=2,ABS(B%d-B%d),\"\")" % (r - 1, r, r, r - 1); m.number_format = "#,##0.00"
        e = mark(ws, r, 4, "calc")
        prev = "$B$7" if i == 0 else "D%d" % (r - 1)
        e.value = "=IF(B%d=\"\",\"\",$B$5*B%d+(1-$B$5)*%s)" % (r, r, prev)
        e.number_format = "#,##0.00"
        cl = mark(ws, r, 5, "calc"); cl.value = "=IF(B%d=\"\",\"\",$B$7)" % r; cl.number_format = "#,##0.00"
        for col, sign in ((6, "+"), (7, "-")):
            l = mark(ws, r, col, "calc")
            l.value = ("=IF(B%d=\"\",\"\",$B$7%s$B$6*$B$9*SQRT($B$5/(2-$B$5)*(1-(1-$B$5)^(2*%d))))" % (r, sign, i + 1))
            l.number_format = "#,##0.00"
        sg = mark(ws, r, 9, "calc")
        sg.value = "=IF(D{r}=\"\",\"\",IF(OR(D{r}>F{r},D{r}<G{r}),\"SIGNAL — the process has drifted\",\"\"))".format(r=r)
    _ewb = drift[:BASE_N]
    _emu, _emr = sum(_ewb) / float(BASE_N), _mrbar(_ewb)
    SHOWN.update({("EWMA", "B7"): "%.2f" % _emu, ("EWMA", "B8"): "%.2f" % _emr,
                  ("EWMA", "B9"): "%.2f" % (_emr / 1.128)})
    prev, _esig = _emu, _emr / 1.128
    for i in range(N_PTS):
        prev = 0.2 * drift[i] + 0.8 * prev
        hw = 2.7 * _esig * (0.2 / 1.8 * (1 - 0.8 ** (2 * (i + 1)))) ** 0.5
        SHOWN[("EWMA", "D%d" % (16 + i))] = "%.2f" % prev
        SHOWN[("EWMA", "E%d" % (16 + i))] = "%.2f" % _emu
        SHOWN[("EWMA", "F%d" % (16 + i))] = "%.2f" % (_emu + hw)
        SHOWN[("EWMA", "G%d" % (16 + i))] = "%.2f" % (_emu - hw)
    cats = Reference(ws, min_col=1, min_row=16, max_row=39)
    spc_chart(ws, "EWMA — the limits widen then settle as evidence accumulates", cats, [
        (Reference(ws, min_col=4, min_row=16, max_row=39), "EWMA", "1F4E79", False, True),
        (Reference(ws, min_col=5, min_row=16, max_row=39), "Target", "3F8F5A", False, False),
        (Reference(ws, min_col=6, min_row=16, max_row=39), "UCL", "C0392B", True, False),
        (Reference(ws, min_col=7, min_row=16, max_row=39), "LCL", "C0392B", True, False),
    ], "K4", ylim=bounds(drift, [_emu - 2.7 * _esig * (0.2 / 1.8) ** 0.5,
                                 _emu + 2.7 * _esig * (0.2 / 1.8) ** 0.5]))

    # ---- CUSUM ----------------------------------------------------------
    ws = wb.create_sheet("CUSUM")
    title(ws, "CUSUM — confirm a change landed on the day you deployed it",
          "Fastest detection of a step change. Two running sums: one accumulates evidence the process went up, "
          "the other that it went down. Whichever crosses h first tells you the direction.", 9)
    widths(ws, [14, 13, 13, 12, 12, 11, 11, 11, 24])
    _spc_stats(ws, [
        ("k (slack, in sigmas)", 0.5, "0.00", "Half the shift you care about. 0.5 is tuned to catch a 1-sigma shift."),
        ("h (decision interval)", 4, "0.0", "4 or 5. Lower means faster detection and more false alarms."),
        ("Target / pre-change mean", "=AVERAGE(B16:B27)", "#,##0.00",
         "Set this from the BEFORE window only. Including the after period hides the very shift you are testing for."),
        ("Average moving range", "=AVERAGE(C17:C27)", "#,##0.00", "Baseline window only, for the same reason."),
        ("Sigma estimate", "=B8/1.128", "#,##0.00", ""),
    ], 9)
    ws.cell(row=5, column=2).fill = IN
    ws.cell(row=6, column=2).fill = IN
    band(ws, 14, "Your data — one row per period, oldest first", 9)
    header(ws, 15, ["Period", "Value", "Moving range", "Standardised", "SH (up)", "SL (down)", "h", "-h", "Signal"])
    step = [408, 415, 402, 431, 419, 396, 424, 410, 438, 405, 417, 429,
            452, 461, 448, 470, 457, 466, 449, 463, 471, 455, 468, 460]
    for i in range(N_PTS):
        r = 16 + i
        ws.cell(row=r, column=1, value="Day %d" % (i + 1))
        c = mark(ws, r, 2, "in" if i else "ex"); c.value = step[i]; c.number_format = "#,##0.00"
        if i:
            m = mark(ws, r, 3, "calc"); m.value = "=IF(COUNT(B%d:B%d)=2,ABS(B%d-B%d),\"\")" % (r - 1, r, r, r - 1); m.number_format = "#,##0.00"
        y = mark(ws, r, 4, "calc"); y.value = "=IF(B%d=\"\",\"\",(B%d-$B$7)/$B$9)" % (r, r); y.number_format = "#,##0.00"
        ph = "0" if i == 0 else "E%d" % (r - 1)
        pl = "0" if i == 0 else "F%d" % (r - 1)
        sh = mark(ws, r, 5, "calc"); sh.value = "=IF(B%d=\"\",\"\",MAX(0,D%d-$B$5+%s))" % (r, r, ph); sh.number_format = "#,##0.00"
        sl = mark(ws, r, 6, "calc"); sl.value = "=IF(B%d=\"\",\"\",MAX(0,-D%d-$B$5+%s))" % (r, r, pl); sl.number_format = "#,##0.00"
        hh = mark(ws, r, 7, "calc"); hh.value = "=IF(B%d=\"\",\"\",$B$6)" % r; hh.number_format = "#,##0.00"
        hl = mark(ws, r, 8, "calc"); hl.value = "=IF(B%d=\"\",\"\",-$B$6)" % r; hl.number_format = "#,##0.00"
        sg = mark(ws, r, 9, "calc")
        sg.value = ("=IF(E{r}=\"\",\"\",IF(E{r}>$B$6,\"SHIFT UP confirmed\","
                    "IF(F{r}>$B$6,\"SHIFT DOWN confirmed\",\"\")))").format(r=r)
    _cub = step[:BASE_N]
    _cmu, _cmr = sum(_cub) / float(BASE_N), _mrbar(_cub)
    _csig = _cmr / 1.128
    SHOWN.update({("CUSUM", "B7"): "%.2f" % _cmu, ("CUSUM", "B8"): "%.2f" % _cmr,
                  ("CUSUM", "B9"): "%.2f" % _csig})
    sh_v = sl_v = 0.0
    _cusum_shown = []
    for i in range(N_PTS):
        yv = (step[i] - _cmu) / _csig
        SHOWN[("CUSUM", "D%d" % (16 + i))] = "%.2f" % yv
        SHOWN[("CUSUM", "G%d" % (16 + i))] = "4.00"
        SHOWN[("CUSUM", "H%d" % (16 + i))] = "-4.00"
        sh_v = max(0.0, yv - 0.5 + sh_v)
        sl_v = max(0.0, -yv - 0.5 + sl_v)
        SHOWN[("CUSUM", "E%d" % (16 + i))] = "%.2f" % sh_v
        SHOWN[("CUSUM", "F%d" % (16 + i))] = "%.2f" % sl_v
        _cusum_shown.extend((sh_v, sl_v))
    cats = Reference(ws, min_col=1, min_row=16, max_row=39)
    spc_chart(ws, "CUSUM — the sum climbs from the day the change landed", cats, [
        (Reference(ws, min_col=5, min_row=16, max_row=39), "SH (evidence it went up)", "1F4E79", False, True),
        (Reference(ws, min_col=6, min_row=16, max_row=39), "SL (evidence it went down)", "6B4FA0", False, True),
        (Reference(ws, min_col=7, min_row=16, max_row=39),
         "Decision limit h — crossing it is the signal", "C0392B", True, False),
    ], "K4", ylim=bounds([0, 4], _cusum_shown))

    # ---- t and g --------------------------------------------------------
    ws = wb.create_sheet("t and g (rare events)")
    title(ws, "t-chart and g-chart — for things that almost never happen",
          "Sev-1 outages, compliance misses, security incidents. Charting COUNTS of a rare event gives you a chart "
          "of zeros that tells you nothing. Chart the gap BETWEEN events instead — longer gaps mean improvement.", 8)
    widths(ws, [16, 15, 15, 13, 13, 13, 13, 26])
    _spc_stats(ws, [
        ("Events recorded", "=COUNT(B14:B37)", "0", "Ten events is a workable minimum."),
        ("Average days between (t-chart)", "=AVERAGE(B14:B37)", "#,##0.00", "Rising over time is the improvement you want."),
        ("Transformed mean", "=AVERAGE(C14:C37)", "#,##0.0000",
         "Gaps between rare events are exponential, not normal. The 1/3.6 power (Nelson) makes them near-normal so ordinary limits apply."),
        ("Transformed MR-bar", "=AVERAGE(D15:D37)", "#,##0.0000", ""),
        ("t-chart UCL / LCL (days)", "=TEXT((B7+2.66*B8)^3.6,\"#,##0.0\")&\"  /  \"&TEXT(MAX(0,(B7-2.66*B8))^3.6,\"#,##0.0\")",
         "@", "Limits are computed on the transformed scale and then converted back to days."),
        ("Average opportunities between (g-chart)", "=AVERAGE(F14:F37)", "#,##0.00", "Use this instead of days when volume swings — 'contacts between misses' beats 'days between misses'."),
        ("g-chart UCL", "=B10+3*SQRT(B10*(B10+1))", "#,##0.00", "Geometric, so the limits are wide and the lower limit is almost always zero."),
    ], 8)
    band(ws, 12, "One row per event, oldest first", 8)
    header(ws, 13, ["Event", "Days since previous", "Transformed", "Moving range",
                    "Transformed CL", "Contacts since previous", "g CL", "Signal"])
    gaps = [14, 9, 22, 31, 18, 27, 41, 12, 35, 24, 48, 19, 33, 26, 52, 21, 38, 29, 44, 36, 58, 31, 47, 40]
    vol = [12800, 8400, 21600, 29800, 17400, 26100, 39900, 11200, 33500, 23100, 46800, 18300,
           31700, 25400, 50600, 20200, 36900, 27800, 43100, 34600, 56900, 29900, 45200, 38400]
    for i in range(N_PTS):
        r = 14 + i
        ws.cell(row=r, column=1, value="Incident %d" % (i + 1))
        c = mark(ws, r, 2, "in" if i else "ex"); c.value = gaps[i]; c.number_format = "#,##0"
        t = mark(ws, r, 3, "calc"); t.value = "=IF(B%d=\"\",\"\",B%d^(1/3.6))" % (r, r); t.number_format = "0.0000"
        if i:
            m = mark(ws, r, 4, "calc"); m.value = "=IF(COUNT(C%d:C%d)=2,ABS(C%d-C%d),\"\")" % (r - 1, r, r, r - 1); m.number_format = "0.0000"
        cl = mark(ws, r, 5, "calc"); cl.value = "=IF(B%d=\"\",\"\",$B$7)" % r; cl.number_format = "0.0000"
        v = mark(ws, r, 6, "in" if i else "ex"); v.value = vol[i]; v.number_format = "#,##0"
        gcl = mark(ws, r, 7, "calc"); gcl.value = "=IF(F%d=\"\",\"\",$B$10)" % r; gcl.number_format = "#,##0"
        sg = mark(ws, r, 8, "calc")
        sg.value = ("=IF(B{r}=\"\",\"\",IF(C{r}>$B$7+2.66*$B$8,\"Longer gap than expected — improvement\","
                    "IF(C{r}<$B$7-2.66*$B$8,\"Shorter gap than expected — investigate\",\"\")))").format(r=r)
        SHOWN[("t and g (rare events)", "C%d" % r)] = "%.4f" % (gaps[i] ** (1 / 3.6))
    for i in range(N_PTS):
        r = 14 + i
        ws.cell(row=r, column=10, value="=IF(B%d=\"\",\"\",($B$7+2.66*$B$8)^3.6)" % r).number_format = "#,##0.0"
        ws.cell(row=r, column=11, value="=IF(B%d=\"\",\"\",MAX(0,$B$7-2.66*$B$8)^3.6)" % r).number_format = "#,##0.0"
        ws.cell(row=r, column=12, value="=IF(B%d=\"\",\"\",$B$6)" % r).number_format = "#,##0.0"
    _tt = [g ** (1 / 3.6) for g in gaps]
    _tm, _tmr = sum(_tt) / float(len(_tt)), _mrbar(_tt)
    _gm = sum(vol) / float(len(vol))
    SHOWN.update({("t and g (rare events)", "B5"): "%d" % N_PTS,
                  ("t and g (rare events)", "B6"): "%.2f" % (sum(gaps) / float(len(gaps))),
                  ("t and g (rare events)", "B7"): "%.4f" % _tm,
                  ("t and g (rare events)", "B8"): "%.4f" % _tmr,
                  ("t and g (rare events)", "B9"): "%.1f  /  %.1f" % (
                      (_tm + 2.66 * _tmr) ** 3.6, max(0.0, _tm - 2.66 * _tmr) ** 3.6),
                  ("t and g (rare events)", "B10"): "{:,.2f}".format(_gm),
                  ("t and g (rare events)", "B11"): "{:,.2f}".format(_gm + 3 * (_gm * (_gm + 1)) ** 0.5)})
    for i in range(N_PTS):
        SHOWN[("t and g (rare events)", "E%d" % (14 + i))] = "%.4f" % _tm
        SHOWN[("t and g (rare events)", "G%d" % (14 + i))] = "{:,.0f}".format(_gm)
    cats = Reference(ws, min_col=1, min_row=14, max_row=37)
    spc_chart(ws, "t-chart — days between incidents. Rising is good.", cats, [
        (Reference(ws, min_col=2, min_row=14, max_row=37), "Days between", "1F4E79", False, True),
        (Reference(ws, min_col=12, min_row=14, max_row=37), "Average", "3F8F5A", False, False),
        (Reference(ws, min_col=10, min_row=14, max_row=37), "UCL", "C0392B", True, False),
        (Reference(ws, min_col=11, min_row=14, max_row=37), "LCL", "C0392B", True, False),
    ], "N4", ylim=bounds(gaps, [0, (_tm + 2.66 * _tmr) ** 3.6]))
    spc_chart(ws, "g-chart — contacts handled between incidents", cats, [
        (Reference(ws, min_col=6, min_row=14, max_row=37), "Contacts between", "6B4FA0", False, True),
        (Reference(ws, min_col=7, min_row=14, max_row=37), "Average", "3F8F5A", False, False),
    ], "N22", height=7, ylim=bounds(vol, [0]))

    # ---- picker ---------------------------------------------------------
    ws = wb.create_sheet("Pick your chart", 0)
    title(ws, "Which control chart does your data need?",
          "Pick the row that matches what you have. Getting this wrong is the most common SPC mistake in support.", 4)
    widths(ws, [46, 20, 74, 2])
    header(ws, 4, ["Your data", "Use this chart", "Why, and what to watch out for", ""])
    rows = [
        ("One number per day or week (daily AHT, daily backlog, weekly SLA%)", "I-MR",
         "Fine on daily aggregates. Wrong on raw per-contact durations, which are heavily skewed. Watch for day-of-week patterns."),
        ("A percentage, with thousands of contacts a day (FCR%, SLA met%, QA pass%, reopen%)", "Laney p-prime",
         "THE DEFAULT FOR SUPPORT. An ordinary p-chart's limits are far too tight at these volumes and almost every point will look out of control, until the team stops looking at the chart entirely."),
        ("Defects per 100 contacts, with varying volume", "Laney u-prime",
         "Same overdispersion problem as percentages. Use the Laney version."),
        ("A continuous metric where you can form sensible subgroups", "Xbar-R",
         "Switch to Xbar-S when subgroups are larger than about 8. Getting the subgrouping right is the hard part."),
        ("You need to catch a slow slide before it becomes obvious", "EWMA",
         "Ordinary charts are poor at small sustained shifts — which is exactly what a decaying improvement looks like. Use lambda around 0.2."),
        ("You need to confirm a change landed on the day you deployed it", "CUSUM",
         "Fastest detection of a step change."),
        ("A rare event — sev-1 outages, compliance misses, security incidents", "t and g (rare events)",
         "Chart the time BETWEEN events. Charting counts gives you a chart of zeros and tells you nothing."),
    ]
    for i, (data, chart, why) in enumerate(rows):
        r = 5 + i
        a = ws.cell(row=r, column=1, value=data); a.alignment = Alignment(wrap_text=True, vertical="top"); a.border = THIN
        b = ws.cell(row=r, column=2, value=chart); b.font = Font(bold=True, color="FFB45309"); b.border = THIN
        b.alignment = Alignment(vertical="top")
        c = ws.cell(row=r, column=3, value=why); c.alignment = Alignment(wrap_text=True, vertical="top"); c.border = THIN
        ws.row_dimensions[r].height = 46
    band(ws, 13, "Before you plot anything", 4)
    for i, t in enumerate([
        "Set the limits from a stable BASELINE window, then freeze them. Recomputing limits every time you add data is how a "
        "deteriorating process gets a clean chart.",
        "Twenty to twenty-five points is the working minimum. Fewer than that and the limits move every time you add a day.",
        "Limits are not targets and targets are not limits. Limits describe what the process does; a target describes what you "
        "want. Never draw a target on a control chart and call a point beyond it a special cause.",
        "A point outside the limits is a signal to investigate, not proof of a cause. Go and find out what was different that day.",
    ], start=14):
        c = ws.cell(row=i, column=1, value="\u2022  " + t)
        ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=3)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[i].height = 30

    howto(wb, [
        (True, "Control charts — seven chart types, one workbook"),
        (False, "Every chart the program's selection table sends you to is built here, on your own numbers, with the "
                "control limits written as live formulas so you can see exactly where each line comes from."),
        (True, "How to use it"),
        (False, "1. Open the 'Pick your chart' tab and find the row that matches the data you have."),
        (False, "2. Go to that tab. Overwrite the yellow column with your own numbers, oldest first. The green row is a "
                "worked example — replace it too once you have the hang of it."),
        (False, "3. The chart, the limits and the signal column update themselves. Nothing else needs touching."),
        (False, "4. Blue cells are calculated. Read the formula bar on any of them to see the arithmetic — the constants "
                "(1.128, 2.66, 3.267, A2, D3, D4) are all visible, not buried."),
        (True, "The two mistakes that kill SPC in a support organisation"),
        (False, "Using an ordinary p-chart on high-volume percentages. At 8,000 contacts a day the binomial limits around a "
                "72% FCR are about plus or minus 1.5 points, while real daily FCR swings 4 points from contact mix and "
                "staffing alone. Almost every point reads as out of control, the team stops trusting the chart, and SPC is "
                "discredited within a month. The Laney p-prime tab fixes this — check its 'sigma z' cell: if it is well "
                "above 1.0, an ordinary p-chart was never going to work on your data."),
        (False, "Recomputing the limits every week. Limits come from a baseline window and then stay put. If you recompute "
                "them continuously, a process that is slowly getting worse drags its own limits down with it and never "
                "signals."),
        (True, "Where the numbers come from"),
        (False, "Daily volumes and outcome counts: your contact platform's daily summary (Genesys, NICE, Five9, Zendesk "
                "Explore, Salesforce reports). Defect counts: your QA tool's audit export. Incident dates: the incident "
                "management system, not a spreadsheet somebody keeps by hand."),
        (True, "Reading a chart honestly"),
        (False, "A point outside a limit, eight points in a row on one side, or a run of six steadily rising or falling all "
                "mean something changed. Anything else is noise and reacting to it makes the process worse — that is "
                "tampering, and it is the single most expensive habit in operations management."),
    ])
    return wb, "27-control-charts.xlsx"


BUILDERS = [five_whys, fishbone, stakeholder, kano, doe, pareto, flow, control_charts]


def main() -> int:
    previews = {}
    for fn in BUILDERS:
        wb, name = fn()
        polish_workbook(wb)
        path = TEMPLATES / name
        wb.save(path)
        # regenerate from the saved file so the preview describes what ships
        previews[name] = workbook_html(load_workbook(path), SHOWN)
        print(f"  built {name:34s} {path.stat().st_size:>7,} bytes  "
              f"{len(previews[name]):>7,} chars of preview")
    (ROOT / "tools" / "previews.json").write_text(json.dumps(previews), encoding="utf-8")
    print(f"\n  {len(previews)} templates written, previews cached for sync_html.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
