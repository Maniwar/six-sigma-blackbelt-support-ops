#!/usr/bin/env python3
"""The finishing pass every workbook gets, whoever built it.

Both builders (tools/build_templates.py for the newer templates,
tools/patch_workbooks.py for the originals) call polish_workbook() last. It
fixes the things that are invisible while you are writing formulas and glaring
the moment somebody opens, scrolls or prints the file:

  * charts that straddle a page break and print as two useless halves
  * axes that vanish in Excel because openpyxl leaves `delete` unset
  * 24 category labels crushed into an axis six centimetres wide
  * headers that scroll off the top the moment you reach row 30

None of it changes a single number. It is the difference between a workbook
somebody uses and one they close again.
"""
from __future__ import annotations

from openpyxl.utils import get_column_letter, range_boundaries
from openpyxl.worksheet.properties import PageSetupProperties

# openpyxl writes <c:delete val="1"/> unless told otherwise on some paths, and
# Excel then renders a chart with no axes at all.
def _fix_axes(ch) -> None:
    for ax in (getattr(ch, "x_axis", None), getattr(ch, "y_axis", None)):
        if ax is None:
            continue
        ax.delete = False
        # keep tick labels next to the axis rather than jumping to the far side
        # when a series goes negative (CUSUM's lower arm does)
        ax.tickLblPos = "low" if ax is getattr(ch, "x_axis", None) else "nextTo"


# Roughly how many characters of category label a 15cm axis carries before they
# start colliding, allowing for the rotation Excel applies on its own.
AXIS_CHARS = 90


def _thin_category_labels(ch, labels: list[str]) -> None:
    """Twenty-four labels on a 15cm axis is an unreadable smear.

    How many fit depends on how WIDE they are, not just how many there are:
    twenty-five test numbers sit comfortably where twenty-four "Day 12"s do not.
    Counting alone thinned the hypothesis log to one label in three on an axis
    with room for every one of them.
    """
    ax = getattr(ch, "x_axis", None)
    if ax is None or not labels:
        return
    # On a ranked bar chart the category label IS the content — thinning it
    # hid five of eight causes on the X-Y matrix. Only thin a long time axis.
    #
    # This used to read `ch.type == "bar"`, but on a BarChart `.type` is the bar
    # DIRECTION, so it only ever matched the horizontal ones. Every vertical
    # column chart — the ranked FMEA, the Pareto — kept being thinned, which is
    # the same defect the line above says was fixed. Excel rotates labels that
    # do not fit; it cannot invent one that was skipped.
    if ch.tagname == "barChart":
        skip = 1
    else:
        need = sum(len(t) + 1 for t in labels)
        skip = max(1, -(-need // AXIS_CHARS))
    ax.tickLblSkip = skip
    ax.tickMarkSkip = skip


def _cat_labels(ch, wb=None) -> list[str]:
    """The category labels the widest series actually plots.

    Reads the cells, rather than measuring the range the chart reserves. The
    value stream map books nineteen rows against nine filled ones; sizing the
    label thinning off nineteen made Excel show one step in three on a chart
    with room for all nine — a defect in the file the user downloads, not just
    in how we preview it. A formula cell counts as one label of average width,
    since its result is not knowable until Excel opens the file.
    """
    best: list[str] = []
    for ser in getattr(ch, "series", []) or []:
        ref = None
        for holder in (getattr(ser, "cat", None), getattr(ser, "xVal", None)):
            if holder is None:
                continue
            ref = getattr(getattr(holder, "numRef", None), "f", None) or \
                getattr(getattr(holder, "strRef", None), "f", None)
            if ref:
                break
        if not ref or "!" not in ref:
            continue
        sheet, addr = ref.split("!", 1)
        try:
            c1, r1, c2, r2 = range_boundaries(addr.replace("$", ""))
        except Exception:                                        # noqa: BLE001
            continue
        sheet = sheet.strip("'")
        if wb is None or sheet not in wb.sheetnames:
            got = ["______"] * ((r2 - r1 + 1) * (c2 - c1 + 1))
        else:
            ws = wb[sheet]
            got = []
            for r in range(r1, r2 + 1):
                for c in range(c1, c2 + 1):
                    v = ws.cell(row=r, column=c).value
                    if v in (None, ""):
                        continue
                    got.append("______" if isinstance(v, str) and v.startswith("=")
                               else str(v))
        if len(got) > len(best):
            best = got
    return best


def _header_row(ws) -> int | None:
    """The dark banded header, so panes can freeze just below it."""
    for row in ws.iter_rows(min_row=1, max_row=40):
        for c in row:
            try:
                if c.fill and c.fill.patternType and str(c.fill.fgColor.rgb) == "FF333C49":
                    return c.row
            except Exception:                                    # noqa: BLE001
                pass
    return None


# Plain English for every term of art this pack puts in a column header. The
# page makes these clickable; a downloaded workbook cannot, so the reader meets
# "MR of z" and "A2 for this n" with nothing to click and no way to guess. Every
# guidance check we had inspected whether a header EXISTS, never whether a
# person outside the discipline could read it.
GLOSSES = {
    "OBS": "OBS 1..n are your individual measurements in one subgroup — one row per period",
    "CL": "CL = centre line, the average the chart is drawn around",
    "UCL": "UCL / LCL = upper and lower control limits, ±3 sigma from the centre line",
    "LCL": "UCL / LCL = upper and lower control limits, ±3 sigma from the centre line",
    "MR": "MR = moving range, the gap between one point and the one before it",
    "R-bar": "R-bar = the average range within your subgroups",
    "X-double-bar": "X-double-bar = the average of the subgroup averages",
    "A2": "A2, D3, D4 = standard constants that depend only on your subgroup size",
    "D3": "A2, D3, D4 = standard constants that depend only on your subgroup size",
    "D4": "A2, D3, D4 = standard constants that depend only on your subgroup size",
    "u-bar": "u-bar = defects per unit across the whole baseline, not the average of daily rates",
    "p-bar": "p-bar = the overall proportion across the whole baseline",
    "sigma z": "sigma z = the Laney adjustment; 1.0 means a plain chart was fine, above that it was not",
    "z": "z = your rate restated in standard deviations, so periods of different size compare",
    "p-value": "p-value = the chance of seeing a difference this big if nothing had really changed",
    "CI": "CI = confidence interval, the range the true value plausibly sits in",
    "Effect size": "Effect size = how big the difference is, in units a manager can act on",
    "ASA": "ASA = average speed of answer, in seconds",
    "SL": "SL = service level, the share of contacts answered inside your target time",
    "Occupancy": "Occupancy = the share of logged-in time an agent is actually handling contacts",
    "Erlang A": "Erlang A = the staffing model that allows for callers hanging up; Erlang C assumes nobody does",
    "WFM": "WFM = Workforce Management, the team that owns schedules and headcount",
    "Champion": "Champion = the executive who owns the problem and clears the obstacles",
    "Black Belt": "Black Belt = the person running the project day to day",
    "AB": "AB, AC, BC = interaction columns: the product of two factor columns, +1 or -1",
    "AC": "AB, AC, BC = interaction columns: the product of two factor columns, +1 or -1",
    "BC": "AB, AC, BC = interaction columns: the product of two factor columns, +1 or -1",
    "RPN": "RPN = risk priority number, severity x occurrence x detection",
    "Coefficient": "Coefficient = how far the outcome moves for a one-unit change in that driver, with the other drivers held still",
    "Std error": "Std error = how much that number would wobble if you drew another sample the same size",
    "t-stat": "t-stat = the coefficient divided by its own standard error; roughly 2 or more is the usual signal",
    "VIF": "VIF = variance inflation factor, how much two drivers move together; under 5 is fine, over 10 means drop one",
    "Residual": "Residual = what the model missed on that row: the value that actually happened minus the fitted one",
    "Fitted y": "Fitted y = what the model predicts for that row, before you compare it with what actually happened",
    "R²": "R-squared = the share of the spread in the outcome the model explains; the rest is everything you did not measure",
    "Adjusted R²": "Adjusted R-squared = R-squared with a penalty for each extra driver, so adding columns cannot flatter the model",
    "Odds ratio": "Odds ratio = how many times the odds of the outcome multiply when that driver goes up by one",
    "AUC": "AUC = how well the model ranks a case that happened above one that did not; 0.5 is a coin toss, 0.7 upwards is useful",
    "Logit": "Logit = the log-odds the model works in, before it is turned back into a probability",
    "Predicted probability": "Predicted probability = the model's chance that this particular row ends in the outcome",
    "Sensitivity": "Sensitivity = of the cases that really happened, the share the model flagged",
    "Specificity": "Specificity = of the cases that did not happen, the share the model correctly left alone",
}
_GL_LOW = {k.lower(): v for k, v in GLOSSES.items()}


def _header_rows(ws):
    """(row, {col: label}) for every dark banded header row on the sheet."""
    rows = {}
    for row in ws.iter_rows():
        for c in row:
            try:
                dark = (c.fill and c.fill.patternType
                        and str(c.fill.fgColor.rgb) == "FF333C49")
            except Exception:                                    # noqa: BLE001
                dark = False
            if dark and isinstance(c.value, str) and c.value.strip():
                rows.setdefault(c.row, {})[c.column] = c.value.strip()
    return rows


def explain_headers(wb) -> int:
    """Write a plain-English key under any header row that uses jargon.

    Placed in the first blank row above the header, never by inserting one — an
    inserted row shifts every formula and chart range on the sheet.
    """
    from openpyxl.styles import Alignment, Font
    n = 0
    for ws in wb.worksheets:
        if ws.title.lower().startswith(("how to use", "read me", "legend")):
            continue
        for hrow, cols in _header_rows(ws).items():
            seen, wanted = set(), []
            for label in cols.values():
                for term, gloss in GLOSSES.items():
                    t = term.lower()
                    lab = label.lower()
                    hit = (lab == t or lab.startswith(t + " ") or
                           lab.endswith(" " + t) or (" " + t + " ") in lab)
                    if hit and gloss not in seen:
                        seen.add(gloss)
                        wanted.append(gloss)
            if not wanted:
                continue
            key = "Key: " + " · ".join(wanted)
            above = hrow - 1
            if above < 1:
                continue
            width = max(cols) if cols else 6
            # The band above a header is not always merged from column A — the
            # DOE's legend spans B..G, so anchoring on column 1 found an empty
            # cell, then refused to write because the row was merged.
            anchor = next(
                (ws.cell(row=above, column=c) for c in range(1, width + 1)
                 if isinstance(ws.cell(row=above, column=c).value, str)
                 and ws.cell(row=above, column=c).value.strip()),
                ws.cell(row=above, column=1))
            existing = [ws.cell(row=above, column=c).value for c in range(1, width + 1)]
            has_text = any(v not in (None, "") for v in existing)

            if has_text:
                # Almost always the section band that introduces the table —
                # exactly where a reader looks for what the columns mean. Append
                # to it rather than inserting a row, because inserting shifts
                # every formula and chart range on the sheet.
                if not isinstance(anchor.value, str) or "Key: " in anchor.value:
                    continue
                anchor.value = anchor.value.rstrip(" ·") + "  ·  " + key
            else:
                if any((above, c) in {(r, cc) for rng in ws.merged_cells.ranges
                                      for r in range(rng.min_row, rng.max_row + 1)
                                      for cc in range(rng.min_col, rng.max_col + 1)}
                       for c in range(1, width + 1)):
                    continue
                ws.merge_cells(start_row=above, start_column=1,
                               end_row=above, end_column=width)
                anchor = ws.cell(row=above, column=1, value=key)
                anchor.font = Font(italic=True, size=9, color="FF6B7280")
            anchor.alignment = Alignment(wrap_text=True, vertical="center")
            ws.row_dimensions[above].height = max(
                14, 12 * (1 + len(str(anchor.value)) // 110))
            n += 1
    return n


def stamp(wb):
    """Freeze the document timestamps so a rebuild that changes nothing is empty.

    openpyxl writes the current time into docProps/core.xml on every save. Every
    worksheet XML can be byte-identical and all 19 workbooks still come out with
    different bytes, which changes the base64 embedded in the page, which makes
    the HTML differ too. So `git diff` after a rebuild always showed 20 modified
    files and could never tell anyone whether the rebuild actually did anything
    — the same blindness as a check that cannot fail, in the one place a
    reviewer looks first.

    The date is the project's, fixed, and deliberately not derived from
    anything: a value that moves is the entire problem.
    """
    from datetime import datetime
    fixed = datetime(2026, 1, 1)
    wb.properties.created = fixed
    wb.properties.modified = fixed
    wb.properties.creator = "six-sigma-blackbelt-support-ops"
    wb.properties.lastModifiedBy = "six-sigma-blackbelt-support-ops"
    return wb


ZIP_EPOCH = (2026, 1, 1, 0, 0, 0)


def save_workbook(wb, path) -> None:
    """Save, then rewrite the archive with fixed entry timestamps.

    Freezing the document properties is only half of it, and setting them before
    the save does not survive it — openpyxl stamps dcterms:modified with the
    clock as it writes, so that one has to be corrected here, afterwards. An
    .xlsx is also a zip, and a zip records a modification time per entry, which
    Python's zipfile likewise takes from the clock. All three move independently;
    all three have to be pinned before "the build produced no diff" means what it
    says.
    """
    import re as _re
    import zipfile
    wb.save(path)
    src = zipfile.ZipFile(path)
    items = [(i, src.read(i.filename)) for i in src.infolist()]
    src.close()
    tmp = path.with_name(path.name + ".rezip")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        for info, data in items:
            if info.filename == "docProps/core.xml":
                data = _re.sub(
                    rb"(<dcterms:modified[^>]*>)[^<]*(</dcterms:modified>)",
                    rb"\g<1>2026-01-01T00:00:00Z\g<2>", data)
            zi = zipfile.ZipInfo(info.filename, date_time=ZIP_EPOCH)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zi.internal_attr = info.internal_attr
            zi.create_system = info.create_system
            out.writestr(zi, data)
    tmp.replace(path)


FILL_IN = "FFFFF9E3"        # "you fill this in"
FILL_EX = "FFECFAEF"        # "a worked example — replace it with your own"
FILL_CALC = "FFF2F7FF"      # "calculated — do not type over it"
FILL_BAND = "FFEEF1F6"      # a section band: the table above it has ended
FILL_HDR = "FF333C49"


def _boundary(ws, row: int, span) -> bool:
    """Does this row end the table above it?"""
    for c in span:
        cell = ws.cell(row=row, column=c)
        try:
            if cell.fill and cell.fill.patternType and \
                    str(cell.fill.fgColor.rgb) in (FILL_BAND, FILL_HDR):
                return True
        except Exception:                                        # noqa: BLE001
            pass
    # a note merged across the width of the block
    for rng in ws.merged_cells.ranges:
        if rng.min_row == row and (rng.max_col - rng.min_col + 1) >= max(2, len(span) - 1):
            return True
    return False


def _typed(cell) -> bool:
    """Did a person put this here? A formula did not, and neither did nothing."""
    v = cell.value
    return v not in (None, "") and not (isinstance(v, str) and v.startswith("="))


def _index_columns(ws, hrow: int, span) -> set:
    """Columns that are just a pre-printed row number: 1, 2, 3 down the block.

    Every entry grid in this pack numbers its rows in advance so the reader can
    refer to "row 14" in a meeting. Those numbers are furniture, not data, and a
    row that holds nothing else is blank however filled it looks.
    """
    out = set()
    for c in span:
        seen = []
        for r in range(hrow + 1, min(hrow + 40, ws.max_row) + 1):
            v = ws.cell(row=r, column=c).value
            if v in (None, ""):
                break
            if not isinstance(v, int) or isinstance(v, bool):
                seen = []
                break
            seen.append(v)
        if len(seen) >= 3 and seen == list(range(seen[0], seen[0] + len(seen))):
            out.add(c)
    return out


def recolour_formulas(wb) -> int:
    """A cell holding a formula is blue, wherever it sits.

    The legend gives each colour one job: yellow is yours to type, green is the
    worked example you replace, blue is calculated and must not be typed over.
    55 formula cells across six workbooks were painted green or yellow — the
    Pareto's own Share and Rank on the example row among them — which tells the
    reader to overwrite a formula and lose the calculation.

    Runs after mark_examples on purpose. Example colouring only ever repaints
    literals, so it cannot create this, but the hand-authored sheets already had
    it and nothing looked.
    """
    from openpyxl.styles import PatternFill
    blue = PatternFill("solid", fgColor=FILL_CALC)
    wrong = {FILL_IN, FILL_EX}
    n = 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if not (isinstance(c.value, str) and c.value.startswith("=")):
                    continue
                try:
                    rgb = str(c.fill.fgColor.rgb) if c.fill and c.fill.patternType else ""
                except Exception:                                # noqa: BLE001
                    continue
                if rgb in wrong:
                    c.fill = blue
                    n += 1
    return n


def mark_examples(wb) -> int:
    """Demonstration data inside a table is a worked example, so colour it one.

    The legend promises yellow means "you fill these in" and green means "a
    worked example so you can see the expected format; delete it when you
    start". 104 rows across seven sheets were demonstration data painted
    yellow, which contradicts both at once: the cell is not something you fill
    in, it is already filled.

    Scoped to banded tables on purpose. A standalone yellow input holding a
    value is a sensible DEFAULT to adjust — alpha at 0.05, a subgroup size of
    five — not an example to delete, and those must stay yellow.

    Scoped to the CONTIGUOUS pre-filled rows at the top of the block, and it
    stops at the first row that has nothing in it. Those rows are one worked
    example and the reader reads them as one: the Pareto ships five billing
    defect categories with counts and shares, and colouring the first green and
    the next four yellow says the last four are yours to invent, which is not
    what they are.

    The two wrong answers before this one are worth keeping, because they are
    opposite errors. The first painted every yellow cell in the block whatever
    lay below, which ran past the end of the logistic tab's data and turned its
    threshold and AUC settings into what looks like reference data. The second
    over-corrected to the first row alone, which split every seeded example down
    the middle. The boundary is the data, not a row count: an example ends where
    the blank rows begin.
    """
    from openpyxl.styles import PatternFill
    green = PatternFill("solid", fgColor=FILL_EX)
    n = 0
    for ws in wb.worksheets:
        if ws.title.lower().startswith(("how to use", "read me", "legend")):
            continue
        shadow = {(r, c) for rng in ws.merged_cells.ranges
                  for r in range(rng.min_row, rng.max_row + 1)
                  for c in range(rng.min_col, rng.max_col + 1)
                  if (r, c) != (rng.min_row, rng.min_col)}
        for hrow, cols in _header_rows(ws).items():
            span = sorted(cols)
            index_cols = _index_columns(ws, hrow, span)
            body = [c for c in span if c not in index_cols]
            r = hrow + 1
            while r <= ws.max_row:
                row_cells = [ws.cell(row=r, column=c) for c in span]
                # A row is part of the example only if somebody TYPED something
                # into it. Two things otherwise make an empty row look full:
                # the index column, pre-numbered down the whole block so the
                # reader can say "row 14" in a meeting, and the computed columns,
                # which carry a formula on every row whether or not it has data.
                # Counting either made the hypothesis log's rows 16-33 a worked
                # example on the strength of the numbers 6 to 23 and a column of
                # IF(...,"") that returns blank.
                if not any(_typed(ws.cell(row=r, column=c)) for c in (body or span)):
                    break
                # A table also ends at the next section band, the next header,
                # or a merged note spanning it. Walking only to the first blank
                # row ran straight past the end of the logistic tab's data and
                # recoloured the threshold and AUC cells below it — settings the
                # reader chooses, relabelled as an example to delete.
                if _boundary(ws, r, span):
                    break
                for cell in row_cells:
                    if (cell.row, cell.column) in shadow:
                        continue
                    try:
                        yellow = (cell.fill and cell.fill.patternType
                                  and str(cell.fill.fgColor.rgb) == FILL_IN)
                    except Exception:                            # noqa: BLE001
                        yellow = False
                    literal = (cell.value not in (None, "") and
                               not (isinstance(cell.value, str)
                                    and cell.value.startswith("=")))
                    if yellow and literal:
                        cell.fill = green
                        n += 1
                r += 1
    return n


def _anchor_ref(ch) -> str | None:
    """Where a chart is anchored, as "K3", whichever form openpyxl is using.

    A chart built in this session carries a plain string. One read back from a
    file carries a OneCellAnchor/TwoCellAnchor object with zero-based col/row,
    so comparing it against a string never matched and every chart looked moved
    on every run.
    """
    a = getattr(ch, "anchor", None)
    if isinstance(a, str):
        return a
    frm = getattr(a, "_from", None)
    if frm is None:
        return None
    return f"{get_column_letter(frm.col + 1)}{frm.row + 1}"


def polish_workbook(wb, landscape: bool = True) -> int:
    """Print setup, frozen headers and chart legibility, for every sheet.

    Returns how many sheets it actually changed, so a caller that only saves on
    a real change (patch_workbooks.py, to keep the embedded base64 stable) can
    tell whether this pass did anything.

    Runs at every save site in the build, which is why stamp() lives here: the
    document timestamps have to be frozen on the way out or the bytes move
    whether or not the content did.
    """
    stamp(wb)
    changed = explain_headers(wb) + mark_examples(wb) + recolour_formulas(wb)
    for ws in wb.worksheets:
        before = (ws.page_setup.fitToWidth, ws.page_setup.orientation, ws.freeze_panes)

        # --- printing: one sheet wide, so a chart is never cut in half ---
        ws.page_setup.orientation = "landscape" if landscape else "portrait"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0          # as many pages tall as it needs
        ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
        ws.print_options.horizontalCentered = True
        ws.page_margins.left = ws.page_margins.right = 0.4
        ws.page_margins.top = ws.page_margins.bottom = 0.5

        # --- reading: keep the header visible past row 30 ---
        if ws.freeze_panes is None:
            hr = _header_row(ws)
            if hr and hr < 30:
                ws.freeze_panes = f"A{hr + 1}"

        # --- charts: never on top of the data they explain ---
        # Thirteen charts were anchored over populated cells, several over the
        # very block they read from. Fixing them one at a time is how the last
        # three rounds of this went, so it is done here for the class: every
        # chart is pushed clear of the rightmost populated column on its sheet,
        # and stacked vertically in anchor order so two charts never collide.
        charts = list(getattr(ws, "_charts", []))
        if charts:
            last_col = 0
            for row in ws.iter_rows():
                for c in row:
                    if c.value not in (None, ""):
                        last_col = max(last_col, c.column)
            free = get_column_letter(last_col + 2)
            row_at = 3
            for ch in charts:
                target = f"{free}{row_at}"
                # Only a real move counts. This incremented unconditionally, so
                # every workbook with a chart reported a change on every run and
                # re-saved forever — which was invisible while the timestamps
                # churned the bytes anyway, and is the whole reason "did the
                # build change anything?" had no answer.
                if _anchor_ref(ch) != target:
                    changed += 1
                ch.anchor = target
                row_at += max(16, int((ch.height or 7.5) / 0.5) + 3)


        for ch in getattr(ws, "_charts", []):
            # Charts skip hidden cells by default. Several templates keep their
            # reference columns hidden — a quadrant divider, a noise floor —
            # and those series silently vanished from the plot.
            ch.plotVisOnly = False
            _fix_axes(ch)
            _thin_category_labels(ch, _cat_labels(ch, wb))
            # openpyxl never round-trips this one, so setting it must not count
            # as a change or every run would re-save and churn the base64 copies
            ch.roundedCorners = False

        if before != (ws.page_setup.fitToWidth, ws.page_setup.orientation, ws.freeze_panes):
            changed += 1
    return changed
