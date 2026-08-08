#!/usr/bin/env python3
"""Measure how the Word export actually renders tables.

Every check here reads the produced OOXML, never the source that writes it.
The distinction is the whole point: this file exists because a check that
asserted `w:fill` appeared in the XML reported success for twenty templates
whose charts Word drew as nothing at all.

Run:  python tools/qa_wordtables.py [--only 22-stakeholder-and-raci]
"""
from __future__ import annotations

import argparse
import base64
import io
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import qa_visual as V  # noqa: E402
from sync_html import extract_tpls  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "six-sigma-blackbelt-support-ops.html"

# A table cell's text, in document order, with the runs of one paragraph joined
# and paragraphs kept apart. Word breaks lines at paragraphs and <w:br/>; the
# text of two runs inside one paragraph is one visual line.
RE_TBL = re.compile(r"<w:tbl>(?:(?!<w:tbl>).)*?</w:tbl>", re.S)
RE_ROW = re.compile(r"<w:tr\b.*?</w:tr>", re.S)
RE_CELL = re.compile(r"<w:tc>.*?</w:tc>", re.S)
RE_PARA = re.compile(r"<w:p\b.*?</w:p>", re.S)
RE_TEXT = re.compile(r"<w:t[^>]*>(.*?)</w:t>", re.S)
RE_BR = re.compile(r"<w:br\s*/>")
RE_GRIDCOL = re.compile(r'<w:gridCol w:w="(\d+)"/>')
RE_SPAN = re.compile(r'<w:gridSpan w:val="(\d+)"/>')

# A value followed with no separator by the formula that produced it:
# "ENGAGE NOW=IF(COUNT(C5:D5)<2,..." — one visual line in Word.
#
# The character before the "=" must not be a comparison operator: a formula
# that contains ">=ABS(" is one expression, not a value run into a formula,
# and matching it flagged five clean cells in the hypothesis-test log.
RE_JAMMED = re.compile(r"[^\s<>=!]=[A-Z]{2,}\(")


def _unesc(s: str) -> str:
    return (s.replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"').replace("&amp;", "&"))


def cell_lines(cell_xml: str) -> list[str]:
    """The visual lines of one cell: one per paragraph, split again on <w:br/>."""
    lines: list[str] = []
    for p in RE_PARA.findall(cell_xml):
        # A <w:br/> inside a paragraph starts a new visual line.
        for chunk in RE_BR.split(p):
            txt = "".join(_unesc(t) for t in RE_TEXT.findall(chunk))
            lines.append(txt)
    return lines


def cell_text(cell_xml: str) -> str:
    return "".join(cell_lines(cell_xml)).strip()


def doc_text(doc: str) -> str:
    """Everything the document prints, in order."""
    return "".join(_unesc(t) for t in RE_TEXT.findall(doc))


def tables(doc: str) -> list[str]:
    """Innermost tables only — a bar drawn as a nested table is not a data table."""
    return RE_TBL.findall(doc)


def is_chart_bar(tbl: str) -> bool:
    """A bar table: shaded cells, no text anywhere."""
    if not re.search(r'w:fill="(?!auto|333C49)[0-9A-Fa-f]{6}"', tbl):
        return False
    return not any(cell_text(c) for c in RE_CELL.findall(tbl))


def grid_of(tbl: str) -> list[int]:
    return [int(w) for w in RE_GRIDCOL.findall(tbl)]


def columns(tbl: str) -> list[list[str]]:
    """Text per column, honouring gridSpan. Returns [] if the table is ragged."""
    cols = len(grid_of(tbl))
    if not cols:
        return []
    out: list[list[str]] = [[] for _ in range(cols)]
    for row in RE_ROW.findall(tbl):
        i = 0
        for cell in RE_CELL.findall(row):
            if i >= cols:
                break
            m = RE_SPAN.search(cell)
            span = int(m.group(1)) if m else 1
            out[i].append(cell_text(cell))
            for k in range(i + 1, min(i + span, cols)):
                out[k].append("")  # covered by the span, not a column of its own
            i += span
    return out


def spanned_columns(tbl: str) -> set[int]:
    """Columns that some gridSpan reaches across — never safe to drop."""
    cols = len(grid_of(tbl))
    hit: set[int] = set()
    for row in RE_ROW.findall(tbl):
        i = 0
        for cell in RE_CELL.findall(row):
            m = RE_SPAN.search(cell)
            span = int(m.group(1)) if m else 1
            if span > 1:
                hit.update(range(i, min(i + span, cols)))
            i += span
    return hit


def audit_doc(key: str, doc: str, preview: str = "") -> list[str]:
    """Every table-rendering defect visible in one document's OOXML."""
    bad: list[str] = []
    for ti, tbl in enumerate(tables(doc)):
        if is_chart_bar(tbl):
            continue
        grid = grid_of(tbl)
        cols = columns(tbl)
        if not cols:
            continue

        # 1. A column with no text in any row still takes a share of the page.
        spanned = spanned_columns(tbl)
        for ci, col in enumerate(cols):
            if ci in spanned or not col:
                continue
            if not any(c.strip() for c in col) and grid[ci] > 400:
                bad.append(
                    f"{key} table#{ti} col#{ci}: empty in all {len(col)} rows "
                    f"yet {grid[ci]}dxa wide")

        # 2. A value and the formula that produced it on one visual line.
        for row in RE_ROW.findall(tbl):
            for cell in RE_CELL.findall(row):
                for line in cell_lines(cell):
                    if RE_JAMMED.search(line):
                        bad.append(
                            f"{key} table#{ti}: value and formula share a line: "
                            f"{line.strip()[:60]!r}")
                        break

        # 3. A formula with no value above it is noise: the row is unfilled.
        for row in RE_ROW.findall(tbl):
            for cell in RE_CELL.findall(row):
                lines = [l.strip() for l in cell_lines(cell)]
                real = [l for l in lines if l]
                if len(real) == 1 and real[0].startswith("="):
                    bad.append(
                        f"{key} table#{ti}: formula printed with no value: "
                        f"{real[0][:50]!r}")
                    break

        # 4. A heading narrower than its own longest word. Word cannot wrap
        #    inside a word, so it sets the heading one letter per line and the
        #    column becomes a vertical ribbon. This is what a reader sees first
        #    and it is what the earlier width work missed: the checks proved
        #    columns were not EMPTY and not below Word's cell padding, and never
        #    that the text could fit in them. A control plan came out eighteen
        #    columns at a third of an inch.
        CH, PAD = 96, 96                       # twips per character, plus margins
        rows = RE_ROW.findall(tbl)
        head = next((r for r in rows if "<w:tblHeader/>" in r), None)
        # Rotation is NOT an exemption. w:textDirection is a Word feature and
        # Pages ignores it, so a heading sized as though it were vertical comes
        # out horizontal in a column too narrow for it — which is the defect a
        # reader on a Mac actually sees. Check the width the heading needs if
        # nothing rotates it.
        if head:
            at = 0
            for cell in RE_CELL.findall(head):
                m = RE_SPAN.search(cell)
                span = int(m.group(1)) if m else 1
                ci, at = at, at + span
                if ci >= len(grid):
                    break
                # The width the heading actually has is the sum of the columns
                # it spans. Comparing a spanning heading against one column's
                # width reported the fishbone's category labels as too narrow
                # when each of them has three columns to sit in — this check
                # misreading the table, not the table being wrong.
                # The FIRST visual line only. A heading cell can carry its
                # formula on a second line, and joining the two reads the
                # heading and the formula as one 24-character token — which is
                # this check misreading its own fix rather than a defect. A
                # formula is allowed to be too long for its column; it wraps.
                lines = [l.strip() for l in cell_lines(cell) if l.strip()]
                first = lines[0] if lines else ""
                longest = max((len(w) for w in first.split()), default=0)
                avail = sum(grid[ci:ci + span])
                if longest and avail < longest * CH + PAD:
                    bad.append(
                        f"{key} table#{ti} col#{ci}: heading "
                        f"{first[:28]!r} has a {longest}-character word "
                        f"in {avail}dxa ({avail/1440:.2f}in) — Word will set "
                        f"it one letter per line")

        # 6. A body column too narrow for an ordinary word. Rotating the
        #    headings stops them breaking but says nothing about the cells
        #    below, and a 0.36in column breaks those instead. Only ordinary
        #    words count: a 68-character identifier fits nowhere and Word
        #    breaks it wherever it must, which is not a layout defect.
        # Body rows only. cols[] includes the header row, and a rotated heading
        # reads down its column — counting it here re-flagged every heading the
        # rotation had just fixed, which is this check undoing its own premise.
        body_rows = [r for r in RE_ROW.findall(tbl) if "<w:tblHeader/>" not in r]
        body_cols: list[list[str]] = [[] for _ in grid]
        for row in body_rows:
            at = 0
            for cell in RE_CELL.findall(row):
                m = RE_SPAN.search(cell)
                span = int(m.group(1)) if m else 1
                if at < len(grid) and span == 1:
                    body_cols[at].append(cell_text(cell))
                at += span
        for ci, col in enumerate(body_cols):
            if ci >= len(grid):
                break
            ordinary = [w for cell in col for w in cell.split()
                        if 3 <= len(w) <= 14 and not w.startswith("=")]
            if not ordinary:
                continue
            longest_body = max(len(w) for w in ordinary)
            if grid[ci] < longest_body * CH + PAD:
                worst = max(ordinary, key=len)
                bad.append(
                    f"{key} table#{ti} col#{ci}: {grid[ci]}dxa "
                    f"({grid[ci]/1440:.2f}in) cannot hold {worst!r} — an "
                    f"ordinary word Word will have to break")

        # 5. A grid wider than the page. Every column can be wide enough for
        #    its own text and the table still run off the paper — the control
        #    plan's eighteen columns added to 21,392 twips against 12,960
        #    usable. The heading check above looked at columns one at a time and
        #    could not see it; this adds them up.
        page = 12960 if 'w:orient="landscape"' in doc else 9360
        total = sum(grid)
        if total > page + 40:
            bad.append(
                f"{key} table#{ti}: its {len(grid)} columns add to {total}dxa "
                f"({total/1440:.2f}in) against {page/1440:.2f}in of usable page — "
                f"the right-hand columns fall off the paper")

    # Document-level properties. These are stated once per file rather than
    # per table, because each is about the document being coherent with itself.
    data = [t for t in tables(doc) if not is_chart_bar(t)]

    # Nothing the reader can see may go missing on the way into Word.
    #
    # This is the check that was absent when the column trimmer shipped: it
    # dropped columns nothing wrote to, which is right, and then discarded the
    # cells that spanned only those columns, which deleted the "HOW TO READ IT"
    # note under every chart in the pack. Every defect this file exists for is
    # a variant of the same thing, so compare the two documents directly.
    # Separate cells with a newline, not a space: joining them let the tail of
    # one cell and the head of the next form a phrase that exists in neither,
    # and the check then went looking for it in the document. The heading
    # pattern below cannot span a newline, so the boundary does the work.
    body = re.sub(r"<[^>]+>", "\n", preview)
    body = (body.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                .replace("&quot;", '"').replace("&#x27;", "'").replace("&nbsp;", " "))
    seen = " ".join(doc_text(doc).split())
    for phrase in re.findall(r"[A-Z][A-Z ]{6,}\.", body):   # the sheets' own headings
        want = " ".join(phrase.split())
        if want not in seen:
            bad.append(f"{key}: the preview shows {want[:40]!r} and the document does not")

    # A sheet whose preview marks header cells must arrive with header rows:
    # bold, shaded, and repeating when the table breaks across a page. Sheets
    # that genuinely have no header row (a calculator is label-then-value) are
    # not required to invent one — hence the comparison against the preview
    # rather than a flat assertion.
    if data and 'x-hdr' in preview and "<w:tblHeader/>" not in doc:
        bad.append(f"{key}: the preview marks header cells but no table has a header row")

    # The closing note explains a colour key. Every colour it names has to be
    # somewhere in the document, and every coded colour the sheet uses has to
    # be named — otherwise the note sends the reader looking for cells that
    # are not there, or leaves coloured cells unexplained.
    for name, fill, cls in (("yellow", "FFF9E3", "x-fill"),
                            ("blue", "F2F7FF", "x-calc"),
                            ("green", "ECFAEF", "x-ex")):
        named = f"{name.capitalize()} cells" in doc
        drawn = f'w:fill="{fill}"' in doc
        if named and not drawn:
            bad.append(f"{key}: the note explains the {name} cells but none carry {fill}")
        if drawn and not named:
            bad.append(f"{key}: {name} cells are used but the note never explains them")
    return bad


def run(only: str | None = None) -> int:
    _, _, T = extract_tpls(PAGE.read_text(encoding="utf-8"))
    keys = [only] if only else sorted(T)
    failures: list[str] = []
    checked = 0
    for key in keys:
        if "preview" not in T.get(key, {}):
            continue
        try:
            g = V.template_export(key)
        except Exception as exc:  # a template that will not export is its own defect
            failures.append(f"{key}: export failed: {exc}")
            continue
        doc = zipfile.ZipFile(
            io.BytesIO(base64.b64decode(g["docx"]))).read("word/document.xml").decode()
        checked += 1
        found = audit_doc(key, doc, T[key].get("preview", ""))
        failures.extend(found)
        print(f"  {key:32s} {'OK' if not found else str(len(found)) + ' defect(s)'}")

    print()
    if failures:
        print(f"{len(failures)} table defect(s) across {checked} document(s):")
        for f in failures[:40]:
            print("   -", f)
        if len(failures) > 40:
            print(f"   ... and {len(failures)-40} more")
        return 1
    print(f"{checked} document(s): every table renders cleanly.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    a = ap.parse_args()
    raise SystemExit(run(a.only))
