#!/usr/bin/env python3
"""Propagate templates/ into the single-file HTML, then into docs/.

Every workbook exists in four places: templates/*.xlsx, the base64 copy inside
the HTML, the preview table's formula tooltips, and docs/index.html. Only the
first is edited by hand; this script derives the other three, so a formula fix
cannot land in one copy and miss the rest.

What it rewrites inside `const TPLS = {...}`:
  * b64      - re-read from templates/*.xlsx
  * content  - re-read from templates/*.md
  * preview  - each <td>'s title tooltip is set from the formula in the matching
               workbook cell, and text cells are re-read from the workbook.
               Cell position is recovered by accumulating colspan across each
               row, which reproduces the original generator exactly (verified
               against all 233 formulas before any change was made).

    python3 tools/patch_workbooks.py
    python3 tools/sync_html.py
    python3 tools/verify.py

Requires: openpyxl
"""
from __future__ import annotations

import base64
import html as H
import json
import re
import shutil
import sys
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "six-sigma-blackbelt-support-ops.html"
DOCS = ROOT / "docs" / "index.html"
TEMPLATES = ROOT / "templates"

RE_SHEET = re.compile(
    r'(<div class="xsheet[^"]*" data-xsheet="(\d+)"><table class="xgrid">)(.*?)(</table></div>)', re.S
)
RE_ROW = re.compile(r"(<tr>)(.*?)(</tr>)", re.S)
RE_TD = re.compile(r"<td([^>]*)>(.*?)</td>", re.S)

# Cells whose rendered text the workbook cannot supply on its own: openpyxl
# stores no cached results, so any *numeric* cell added or changed after the
# previews were generated needs its display value stated here.
TEXT_OVERRIDES: dict[tuple[str, str, str], str] = {
    ("13-hypothesis-test-log.xlsx", "Test log", "B8"): "0.05",
}

# Classes for cells that did not exist when the previews were generated.
CLASS_OVERRIDES: dict[tuple[str, str, str], str] = {
    ("13-hypothesis-test-log.xlsx", "Test log", "B8"): "x-fill",
    ("13-hypothesis-test-log.xlsx", "Test log", "A8"): "x-b",
}


def extract_tpls(src: str) -> tuple[int, int, dict]:
    """Return (start, end, parsed) for the `const TPLS = {...}` object literal."""
    i = src.index("const TPLS=")
    start = src.index("{", i)
    depth = 0
    in_str = False
    esc = False
    for j in range(start, len(src)):
        ch = src[j]
        if esc:
            esc = False
            continue
        if ch == "\\" and in_str:
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return start, j + 1, json.loads(src[start : j + 1])
    raise SystemExit("could not find the end of const TPLS")


def _set_attr(attrs: str, name: str, value: str) -> str:
    """Replace an attribute's value in place, or append it, preserving order."""
    pat = re.compile(r'(\s%s=")([^"]*)(")' % name)
    if pat.search(attrs):
        return pat.sub(lambda m: m.group(1) + value + m.group(3), attrs, count=1)
    return attrs + ' %s="%s"' % (name, value)


def rebuild_preview(preview: str, wbpath: Path, stats: dict) -> str:
    wb = load_workbook(wbpath)
    fname = wbpath.name

    def do_sheet(m: re.Match) -> str:
        idx = int(m.group(2))
        ws = wb.worksheets[idx]
        row_no = [0]
        # Columns claimed by a rowspan started in an earlier row. Without this
        # the walk shifts left on every row under a vertical merge, and the
        # fishbone's bones are vertical merges.
        held: dict[int, set[int]] = {}

        def do_row(rm: re.Match) -> str:
            row_no[0] += 1
            r = row_no[0]
            col = [1]

            def do_td(tm: re.Match) -> str:
                attrs, inner = tm.group(1), tm.group(2)
                cs = re.search(r'colspan="(\d+)"', attrs)
                rs = re.search(r'rowspan="(\d+)"', attrs)
                nc = int(cs.group(1)) if cs else 1
                nr = int(rs.group(1)) if rs else 1
                while col[0] in held.get(r, ()):
                    col[0] += 1
                c = col[0]
                col[0] += nc
                if nr > 1:
                    for rr in range(r + 1, r + nr):
                        held.setdefault(rr, set()).update(range(c, c + nc))
                cell = ws.cell(row=r, column=c)
                val = cell.value
                key = (fname, ws.title, cell.coordinate)

                if isinstance(val, str) and val.startswith("="):
                    esc_f = H.escape(val, quote=True)
                    if 'title="' not in attrs:
                        stats["title_added"] += 1
                        cls = re.search(r'class="([^"]*)"', attrs)
                        newcls = (cls.group(1) + " x-f") if cls else "x-calc x-f"
                        attrs = _set_attr(attrs, "class", newcls)
                    elif H.unescape(re.search(r'title="([^"]*)"', attrs).group(1)) != val:
                        stats["title_changed"] += 1
                    attrs = _set_attr(attrs, "title", esc_f)
                elif 'title="' in attrs:
                    # This cell used to hold a formula and no longer does. The
                    # tooltip has to go, or it survives every future sync and
                    # describes a cell somewhere else entirely.
                    stats["title_changed"] += 1
                    attrs = re.sub(r'\s*title="[^"]*"', "", attrs)
                    attrs = _set_attr(attrs, "class",
                                      (re.search(r'class="([^"]*)"', attrs).group(1)
                                       if re.search(r'class="([^"]*)"', attrs) else "").replace("x-f", "").strip())
                    if isinstance(val, str):
                        inner = H.escape(val, quote=True)

                if isinstance(val, str) and not val.startswith("="):
                    want = H.escape(val, quote=True)
                    if want != inner:
                        stats["text_changed"] += 1
                        inner = want
                elif key in TEXT_OVERRIDES:
                    want = TEXT_OVERRIDES[key]
                    if want != inner:
                        stats["text_changed"] += 1
                        inner = want

                if key in CLASS_OVERRIDES:
                    attrs = _set_attr(attrs, "class", CLASS_OVERRIDES[key])
                return "<td%s>%s</td>" % (attrs, inner)

            return rm.group(1) + RE_TD.sub(do_td, rm.group(2)) + rm.group(3)

        return m.group(1) + RE_ROW.sub(do_row, m.group(3)) + m.group(4)

    return RE_SHEET.sub(do_sheet, preview)


def main() -> int:
    src = HTML.read_text(encoding="utf-8")
    start, end, tpls = extract_tpls(src)
    stats = {"title_changed": 0, "title_added": 0, "text_changed": 0, "b64": 0, "md": 0}

    for slug, entry in tpls.items():
        path = TEMPLATES / entry["file"]
        if not path.exists():
            raise SystemExit(f"missing template: {path}")
        if entry.get("ext") == "xlsx":
            new_b64 = base64.b64encode(path.read_bytes()).decode("ascii")
            if new_b64 != entry.get("b64"):
                entry["b64"] = new_b64
                stats["b64"] += 1
            entry["preview"] = rebuild_preview(entry["preview"], path, stats)
        else:
            text = path.read_text(encoding="utf-8")
            if text != entry.get("content"):
                entry["content"] = text
                stats["md"] += 1

    payload = json.dumps(tpls, ensure_ascii=False)
    if "</script" in payload.lower():
        raise SystemExit("template content contains </script> and would break the page")

    out = src[:start] + payload + src[end:]
    HTML.write_text(out, encoding="utf-8")
    shutil.copyfile(HTML, DOCS)

    print(f"  workbooks re-embedded : {stats['b64']}")
    print(f"  markdown re-embedded  : {stats['md']}")
    print(f"  tooltips rewritten    : {stats['title_changed']} (added {stats['title_added']})")
    print(f"  preview text updated  : {stats['text_changed']}")
    print(f"  docs/index.html synced ({DOCS.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
