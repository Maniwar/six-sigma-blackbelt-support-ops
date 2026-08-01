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


def polish_workbook(wb, landscape: bool = True) -> int:
    """Print setup, frozen headers and chart legibility, for every sheet.

    Returns how many sheets it actually changed, so a caller that only saves on
    a real change (patch_workbooks.py, to keep the embedded base64 stable) can
    tell whether this pass did anything.
    """
    changed = 0
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
                ch.anchor = f"{free}{row_at}"
                row_at += max(16, int((ch.height or 7.5) / 0.5) + 3)
                changed += 1


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
