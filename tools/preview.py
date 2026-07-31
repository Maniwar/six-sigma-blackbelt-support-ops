#!/usr/bin/env python3
"""Generate a template's preview HTML from the workbook itself.

The original previews were hand-authored, which is why they could drift from the
files they describe. Anything built by tools/build_templates.py gets its preview
generated here instead, from the same workbook the user downloads.

openpyxl stores no cached formula results, so a formula cell needs a display
value supplied in `shown` — {(sheet, "B4"): "28,800"}. Everything else is read
straight off the cell and formatted from its number format.
"""
from __future__ import annotations

import html as H

from openpyxl.utils import get_column_letter, range_boundaries

# Fill colour -> preview class. These are the same colours the legend explains.
FILL_CLASS = {
    "FF151B24": "x-title",
    "FFEEF1F6": "x-band",
    "FF333C49": "x-hdr",
    "FFFFF9E3": "x-fill",
    "FFF2F7FF": "x-calc",
    "FFECFAEF": "x-ex",
    "FFFDECEC": "x-bad",
}


def _fmt(cell):
    """Render a cell value the way the sheet would show it."""
    v = cell.value
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    nf = (cell.number_format or "").lower()
    try:
        if "%" in nf:
            digits = 1 if ".0" in nf else 0
            return f"{float(v) * 100:.{digits}f}%"
        if "$" in nf or "£" in nf:
            return "$" + f"{float(v):,.0f}" if "0.00" not in nf else "$" + f"{float(v):,.2f}"
        if isinstance(v, float):
            if "0.00" in nf:
                return f"{v:,.2f}"
            if "#,##0" in nf:
                return f"{v:,.0f}"
            return f"{v:g}"
        if isinstance(v, int):
            return f"{v:,}" if "#,##0" in nf else str(v)
    except (TypeError, ValueError):
        pass
    return str(v)


def sheet_html(ws, shown: dict) -> str:
    """One sheet as the preview's table markup."""
    # merged ranges: the anchor spans, the rest are skipped
    spans, covered = {}, set()
    for rng in ws.merged_cells.ranges:
        c1, r1, c2, r2 = range_boundaries(str(rng))
        spans[(r1, c1)] = c2 - c1 + 1
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                if (r, c) != (r1, c1):
                    covered.add((r, c))

    max_r, max_c = ws.max_row, ws.max_column
    out = ['<table class="xgrid">']
    for r in range(1, max_r + 1):
        cells = []
        c = 1
        while c <= max_c:
            if (r, c) in covered:
                c += 1
                continue
            cell = ws.cell(row=r, column=c)
            span = spans.get((r, c), 1)

            cls = ""
            try:
                if cell.fill and cell.fill.patternType and cell.fill.fgColor.rgb:
                    cls = FILL_CLASS.get(str(cell.fill.fgColor.rgb), "")
            except Exception:
                pass
            if not cls and cell.font and cell.font.bold:
                cls = "x-b"

            is_formula = isinstance(cell.value, str) and cell.value.startswith("=")
            if is_formula:
                cls = (cls + " x-f").strip() if cls else "x-calc x-f"
                text = shown.get((ws.title, cell.coordinate), "")
                title = ' title="%s"' % H.escape(cell.value, quote=True)
            else:
                text = H.escape(_fmt(cell), quote=True)
                title = ""

            attrs = ""
            if span > 1:
                attrs += ' colspan="%d"' % span
            if cls:
                attrs += ' class="%s"' % cls
            attrs += title
            cells.append("<td%s>%s</td>" % (attrs, text))
            c += span
        out.append("<tr>" + "".join(cells) + "</tr>")
    out.append("</table>")
    return "".join(out)


def workbook_html(wb, shown: dict | None = None) -> str:
    """Tab strip plus one table per sheet, matching the existing previews."""
    shown = shown or {}
    tabs = "".join(
        '<button class="xtab%s" data-xs="%d">%s</button>'
        % (" on" if i == 0 else "", i, H.escape(ws.title))
        for i, ws in enumerate(wb.worksheets)
    )
    sheets = "".join(
        '<div class="xsheet%s" data-xsheet="%d">%s</div>'
        % (" on" if i == 0 else "", i, sheet_html(ws, shown))
        for i, ws in enumerate(wb.worksheets)
    )
    return '<div class="xtabs">%s</div>%s' % (tabs, sheets)
