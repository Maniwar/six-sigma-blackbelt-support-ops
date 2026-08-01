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

from openpyxl.utils import range_boundaries
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


def _thin_category_labels(ch, n_cats: int) -> None:
    """Twenty-four labels on a 15cm axis is an unreadable smear."""
    ax = getattr(ch, "x_axis", None)
    if ax is None or not n_cats:
        return
    # On a ranked bar chart the category label IS the content — thinning it
    # hid five of eight causes on the X-Y matrix. Only thin a long time axis.
    if getattr(ch, "type", None) == "bar":
        skip = 1
    elif n_cats > 30:
        skip = 4
    elif n_cats > 18:
        skip = 3
    elif n_cats > 10:
        skip = 2
    else:
        skip = 1
    ax.tickLblSkip = skip
    ax.tickMarkSkip = skip


def _series_span(ch) -> int:
    """How many categories the widest series actually plots."""
    best = 0
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
        try:
            c1, r1, c2, r2 = range_boundaries(ref.split("!", 1)[1].replace("$", ""))
            best = max(best, (r2 - r1 + 1) * (c2 - c1 + 1))
        except Exception:                                        # noqa: BLE001
            continue
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

        # --- charts ---
        for ch in getattr(ws, "_charts", []):
            # Charts skip hidden cells by default. Several templates keep their
            # reference columns hidden — a quadrant divider, a noise floor —
            # and those series silently vanished from the plot.
            ch.plotVisOnly = False
            _fix_axes(ch)
            _thin_category_labels(ch, _series_span(ch))
            # openpyxl never round-trips this one, so setting it must not count
            # as a change or every run would re-save and churn the base64 copies
            ch.roundedCorners = False

        if before != (ws.page_setup.fitToWidth, ws.page_setup.orientation, ws.freeze_panes):
            changed += 1
    return changed
