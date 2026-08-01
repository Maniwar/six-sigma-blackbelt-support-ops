#!/usr/bin/env python3
"""Mutation testing for the QA harness itself.

Every quality check in this repo was written after a defect got past the
previous ones, and each one has passed cleanly ever since. That is either
because the defect class is gone, or because the check cannot fire. Those two
states look identical from a green run, and only one of them is good news.

So this reintroduces each shipped defect into a real workbook and asserts the
audit catches it. A mutant that survives is a decorative check: it is reported
as a failure here, loudly, because a check nobody can trip is worse than no
check at all — it buys confidence it has not earned.

    python3 tools/qa_selftest.py

Exit status is non-zero if any mutant survived.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_templates as Q                                          # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"

HDR = "FF333C49"


# ------------------------------------------------------------------ mutants
# Each returns a description of the damage it did, or None if it could not find
# anything to damage in this workbook (in which case the mutant is skipped, not
# passed — an unapplied mutant proves nothing).


def _first_block(wb):
    for ws in wb.worksheets:
        if any(ws.title.lower().startswith(g) for g in Q.GUIDE_TABS):
            continue
        blocks = Q._blocks(ws)
        for hrow, first, last, cols in blocks:
            if last - first + 1 >= 3:
                return ws, hrow, first, last, cols
    return None


def m_empty_column(wb):
    """A column the example declares and then never fills in.

    24-doe-design-matrix shipped with a Notes header over eight blank rows.
    """
    found = _first_block(wb)
    if not found:
        return None
    ws, hrow, first, last, cols = found
    for col, head in sorted(cols.items(), reverse=True):
        cells = [ws.cell(row=r, column=col) for r in range(first, last + 1)]
        if not any(c.value not in (None, "") for c in cells):
            continue
        if any(c.fill and c.fill.patternType
               and str(c.fill.fgColor.rgb) == Q.FILL_INPUT for c in cells):
            continue                        # a yellow column may be blank
        for c in cells:
            if (c.row, c.column) in Q.merged_shadow(ws):
                continue
            try:
                c.value = None
            except AttributeError:          # merged shadow
                return None
        return f"emptied {ws.title!r} column {head!r} across {last - first + 1} rows"
    return None


def m_opaque_header(wb):
    """A header that names nothing, with the legend taken away.

    The DOE design matrix read 'A B C AB AC BC' with no key anywhere.
    """
    found = _first_block(wb)
    if not found:
        return None
    ws, hrow, first, last, cols = found
    shadow = Q.merged_shadow(ws)
    for r in (hrow - 1, hrow + 1):
        if r < 1:
            continue
        for c in range(1, max(cols) + 1):
            cell = ws.cell(row=r, column=c)
            if (r, c) in shadow:
                continue
            if isinstance(cell.value, str) and len(cell.value) > 25:
                cell.value = None
    target = max(cols)
    ws.cell(row=hrow, column=target).value = "XZ"
    return f"renamed a {ws.title!r} header to 'XZ' and removed the legend"


def m_boilerplate(wb):
    """One sentence pasted onto every row of a block.

    The DOE effects table said the same thing on all six effect rows.
    """
    found = _first_block(wb)
    if not found:
        return None
    ws, hrow, first, last, cols = found
    shadow = Q.merged_shadow(ws)
    col = max(cols)
    n = 0
    for r in range(first, min(last, first + 4) + 1):
        if (r, col) in shadow:
            continue
        ws.cell(row=r, column=col).value = (
            "Bigger absolute value = bigger effect. A large interaction "
            "means the two factors cannot be set independently.")
        n += 1
    if n < 3:
        return None
    return f"pasted one identical note onto {n} rows of {ws.title!r}"


def m_ghost_block(wb):
    """A moved helper block that left its old copy behind."""
    for ws in wb.worksheets:
        shadow = Q.merged_shadow(ws)
        for row in ws.iter_rows():
            for c in row:
                if not (isinstance(c.value, str) and len(c.value) > 24):
                    continue
                if c.value.startswith("=") or not (c.font and c.font.bold):
                    continue
                r = ws.max_row + 4
                d = ws.cell(row=r, column=c.column)
                if (r, c.column) in shadow:
                    continue
                d.value = c.value
                d.font = Font(bold=True, size=11)
                return f"left a duplicate heading on {ws.title!r} at row {r}"
    return None


def m_naked_input(wb):
    """A yellow cell with nothing anywhere near it saying what to type."""
    for ws in wb.worksheets:
        shadow = Q.merged_shadow(ws)
        r = ws.max_row + 3
        c = ws.cell(row=r, column=2)
        if (r, 2) in shadow:
            continue
        c.value = 0
        c.fill = PatternFill("solid", fgColor=Q.FILL_INPUT)
        return f"added an unexplained yellow input at {ws.title}!B{r}"
    return None


def m_empty_series(wb):
    """A chart still pointing at a block a later edit stopped feeding."""
    for ws in wb.worksheets:
        for ch in getattr(ws, "_charts", []):
            for ser in ch.series or []:
                vref, _ = Q.series_refs(ser)
                p = Q.parse_ref(vref or "")
                if not p:
                    continue
                sheet, c1, r1, c2, r2 = p
                src = wb[sheet]
                shadow = Q.merged_shadow(src)
                blanked = 0
                for r in range(r1, r2 + 1):
                    for c in range(c1, c2 + 1):
                        if (r, c) in shadow:
                            continue
                        src.cell(row=r, column=c).value = None
                        blanked += 1
                if blanked:
                    return f"blanked the {blanked} cells behind a chart on {ws.title!r}"
    return None


def m_untitled_chart(wb):
    """A chart with its title taken off — a decoration, not an answer."""
    for ws in wb.worksheets:
        for ch in getattr(ws, "_charts", []):
            if Q.chart_title_text(ch).strip():
                ch.title = None
                return f"removed the title from a chart on {ws.title!r}"
    return None


def m_paint_over_the_inputs(wb):
    """Turn a sheet all-green AND take away the sentence that explains it.

    Not hypothetical: this shipped. Repainting the worked examples green walked
    every pre-filled row of a block, took 825 cells with it, and left sheets
    with no input cell at all while the instructions still said to overwrite the
    yellow column — a colour that by then existed nowhere on them.

    Both halves are needed, because an all-green sheet is legitimate when the
    workbook says the green is what you replace. The defect is the mismatch, so
    the mutant creates the mismatch: paint the inputs over, then delete the
    instruction that would have made it coherent.
    """
    green = PatternFill("solid", fgColor="FFECFAEF")
    for ws in wb.worksheets:
        if any(ws.title.lower().startswith(g) for g in Q.GUIDE_TABS):
            continue
        shadow = Q.merged_shadow(ws)
        hit = [c for row in ws.iter_rows() for c in row
               if (c.row, c.column) not in shadow and _fill(c) == Q.FILL_INPUT]
        if not hit:
            continue
        for c in hit:
            c.fill = green
        # The instruction lives across two cells — "Green cells" in one, "Replace
        # it with your own data" in the next — so deleting whole cells that match
        # on their own removes neither half. Take the word out instead.
        for w in wb.worksheets:
            for row in w.iter_rows():
                for c in row:
                    if isinstance(c.value, str) and "green" in c.value.lower():
                        c.value = _re.sub("green", "shaded", c.value, flags=_re.I)
        return (f"repainted all {len(hit)} input cell(s) on {ws.title!r} as example "
                "data and removed the sentence that says to overwrite the green")
    return None


def _fill(c) -> str:
    try:
        return str(c.fill.fgColor.rgb) if c.fill and c.fill.patternType else ""
    except Exception:                                            # noqa: BLE001
        return ""


def m_green_formula(wb):
    """Paint a computed cell as a worked example — "replace this" on a formula."""
    green = PatternFill("solid", fgColor="FFECFAEF")
    for ws in wb.worksheets:
        shadow = Q.merged_shadow(ws)
        for row in ws.iter_rows():
            for c in row:
                if (c.row, c.column) in shadow:
                    continue
                if isinstance(c.value, str) and c.value.startswith("=") \
                        and _fill(c) == Q.FILL_CALC:
                    c.fill = green
                    return f"painted the formula at {ws.title}!{c.coordinate} as an example"
    return None


def m_bare_row(wb):
    """A name and a number, and nothing telling the reader what it is."""
    for ws in wb.worksheets:
        if any(ws.title.lower().startswith(g) for g in Q.GUIDE_TABS):
            continue
        shadow = Q.merged_shadow(ws)
        r = ws.max_row + 3
        if (r, 1) in shadow or (r, 2) in shadow:
            continue
        ws.cell(row=r, column=1, value="DPO")
        c = ws.cell(row=r, column=2, value=0.0507)
        c.number_format = "0.0000"
        c.fill = PatternFill("solid", fgColor=Q.FILL_CALC)
        return f"added an unexplained label:value row at {ws.title}!A{r}"
    return None


def m_strip_row_note(wb):
    """Take the explanation off a CALCULATED row that already has one.

    This is the one that matters. m_bare_row only proves the check notices a row
    invented for it; this proves it defends the notes actually in the workbook,
    and it targets a blue cell on purpose — GUIDED reads yellow only, so if
    ROWLABEL ever stops firing nothing else in the harness covers the row.
    """
    for ws in wb.worksheets:
        if any(ws.title.lower().startswith(g) for g in Q.GUIDE_TABS):
            continue
        shadow = Q.merged_shadow(ws)
        for r in range(1, ws.max_row + 1):
            lab, val = ws.cell(row=r, column=1).value, ws.cell(row=r, column=2)
            if not (isinstance(lab, str) and lab.strip()) or val.value in (None, ""):
                continue
            try:
                rgb = str(val.fill.fgColor.rgb) if val.fill and val.fill.patternType else ""
            except Exception:                                    # noqa: BLE001
                rgb = ""
            if rgb != Q.FILL_CALC or Q._speaks_for_itself(val):
                continue
            notes = [c for c in Q.ROWLABEL_COLS
                     if (r, c) not in shadow
                     and isinstance(ws.cell(row=r, column=c).value, str)
                     and len(ws.cell(row=r, column=c).value) >= 12]
            if not notes:
                continue
            for c in notes:
                ws.cell(row=r, column=c).value = None
            return f"blanked the note beside {ws.title}!A{r} ({lab.strip()[:30]!r})"
    return None


MUTANTS = [
    ("empty declared column", m_empty_column, "EXAMPLE"),
    ("opaque header, no legend", m_opaque_header, "EXAMPLE"),
    ("boilerplate note on every row", m_boilerplate, "EXAMPLE"),
    ("ghost block left behind", m_ghost_block, "GUIDED"),
    ("unexplained yellow input", m_naked_input, "GUIDED"),
    ("chart wired to an emptied block", m_empty_series, "CHARTS"),
    ("chart with no title", m_untitled_chart, "CHARTS"),
    ("entry grid repainted as example data", m_paint_over_the_inputs, "GUIDED"),
    ("formula cell painted as a worked example", m_green_formula, "GUIDED"),
    ("label and number, no explanation", m_bare_row, "ROWLABEL"),
    ("explanation stripped off a calculated row", m_strip_row_note, "ROWLABEL"),
]


# --------------------------------------------------------------------- run


# ------------------------------------------------------- markdown mutants
# The MARKDOWN layer is the newest, and it found 97 real defects on its first
# run — which is exactly the profile of a check that will pass forever
# afterwards and never be questioned again. These two put it back in front of
# the defects it was written for.


def md_empty_column(text: str):
    """Blank out one column of one table, on every row."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not Q.RE_MD_ROW.match(line) or i + 1 >= len(lines):
            continue
        if not Q.RE_MD_RULE.match(lines[i + 1]):
            continue
        head = [c.strip() for c in Q.RE_MD_ROW.match(line).group(1).split("|")]
        if len(head) < 2 or any(h.strip(" *").lower() in ("signature", "signed")
                                for h in head):
            continue
        j, n = i + 2, 0
        while j < len(lines) and Q.RE_MD_ROW.match(lines[j]) \
                and not Q.RE_MD_RULE.match(lines[j]):
            cells = [c for c in Q.RE_MD_ROW.match(lines[j]).group(1).split("|")]
            if len(cells) == len(head):
                cells[-1] = "  "
                lines[j] = "|" + "|".join(cells) + "|"
                n += 1
            j += 1
        if n:
            return "\n".join(lines), f"emptied column {head[-1]!r} on {n} row(s)"
    return None, None


def md_strip_method(text: str):
    """Take away every statement of how the arithmetic is done."""
    if not Q.RE_ARITH.search(text) or not Q.RE_METHOD.search(text):
        return None, None
    out = Q.RE_METHOD.sub("something", text)
    return out, "removed every formula, method and workbook pointer"


def md_break_shares(text: str):
    """Nudge one share so a column totalled at 100% no longer adds up."""
    import re as _re
    IS_TOTAL = ("total", "all ", "check")
    for head, body, line in Q.md_tables(text):
        for col in range(len(head)):
            if col >= len(head):
                continue
            pct = _re.compile(r"\*?\*?(-?\d+(?:\.\d+)?)\s*%")
            total = None
            vals = []
            for row, _ln in body:
                if col >= len(row):
                    continue
                m = pct.match(row[col].strip())
                if not m:
                    continue
                if row[0].strip(" *").lower().startswith(IS_TOTAL):
                    total = float(m.group(1))
                else:
                    vals.append((row, float(m.group(1))))
            # Only mutate a column the check actually audits — one totalled at
            # 100% — and only a row it actually sums. Mutating the total row, or
            # a column totalled at 14.2%, changes nothing the check claims to
            # cover, and a survivor there says nothing about the check.
            if total is None or abs(total - 100.0) > 0.5 or len(vals) < 3:
                continue
            vals = [(r, v) for r, v in vals]
            # Edit the raw line by number. Rebuilding it from md_tables' cells
            # cannot work — those are stripped, so the reconstructed row never
            # matches the spacing in the file and the mutant silently no-ops.
            row, lineno = vals[0][0], None                       # noqa: F841
            for cells, ln in body:
                if cells is row:
                    lineno = ln
                    break
            if lineno is None:
                continue
            lines = text.splitlines()
            raw = lines[lineno - 1]
            parts = raw.split("|")
            # a leading "|" makes parts[0] empty, so cell N is parts[N+1]
            target = col + 1
            if target >= len(parts):
                continue
            m = _re.search(r"(-?\d+(?:\.\d+)?)", parts[target])
            if not m:
                continue
            parts[target] = parts[target].replace(
                m.group(1), str(float(m.group(1)) + 9), 1)
            lines[lineno - 1] = "|".join(parts)
            return "\n".join(lines), f"added 9 points to one share in {head[col]!r}"
    return None, None


def md_bury_in_comment(text: str):
    """Hide a line of guidance inside an HTML comment, where nobody reads it.

    Four real rules shipped this way — a markdown viewer hides the comment and
    the page escaped it into visible body text, so the same sentence was both
    invisible in the file and printed raw, angle brackets and all.
    """
    for i, line in enumerate(text.split("\n")):
        s = line.strip()
        if s.startswith("*") and s.endswith("*") and 25 <= len(s) <= 120:
            lines = text.split("\n")
            lines[i] = f"<!-- {s.strip('*')} -->"
            return "\n".join(lines), f"buried {s[:34]!r} in an HTML comment"
    return None, None


MD_MUTANTS = [("markdown: empty declared column", md_empty_column),
              ("markdown: arithmetic with no method", md_strip_method),
              ("markdown: shares that do not add up", md_break_shares),
              ("markdown: guidance buried in an HTML comment", md_bury_in_comment)]


def run_markdown() -> tuple[int, int, list[str]]:
    killed = applied = 0
    survivors = []
    with tempfile.TemporaryDirectory() as td:
        for doc in sorted(TEMPLATES.glob("*.md")):
            text = doc.read_text(encoding="utf-8")
            Q.fails.clear()
            Q.audit_markdown(doc)
            baseline = set(Q.fails)
            for name, mutate in MD_MUTANTS:
                out, what = mutate(text)
                if out is None:
                    continue
                tmp = Path(td) / doc.name
                tmp.write_text(out, encoding="utf-8")
                applied += 1
                Q.fails.clear()
                Q.audit_markdown(tmp)
                if [f for f in set(Q.fails) - baseline if "[MARKDOWN]" in f]:
                    killed += 1
                else:
                    survivors.append(f"    SURVIVED [MARKDOWN] {name} on {doc.name} — {what}")
    return killed, applied, survivors


# -------------------------------------------------------- visual mutants
# The visual layer this replaces rendered PNGs and told a human to look at
# them. It made no claim, so it could not fail, so a green run from it meant
# nothing at all. The replacement asserts — and an assertion is only worth
# having if it can be shown to fire.


def run_visual() -> tuple[int, int, list[str]]:
    import re as _re
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import qa_visual as V
    from sync_html import extract_tpls
    src = (ROOT / "six-sigma-blackbelt-support-ops.html").read_text(encoding="utf-8")
    _, _, tpls = extract_tpls(src)
    svg = next((s for e in tpls.values() if e.get("ext") == "xlsx"
                for s in _re.findall(r'<svg class="xchart".*?</svg>', e["preview"], _re.S)),
               None)
    if svg is None:
        return 0, 0, []
    muts = [
        ("visual: label outside the frame",
         lambda s: _re.sub(r'<text x="[\d.]+"', '<text x="-260"', s, count=1)),
        ("visual: chart that plots nothing",
         lambda s: _re.sub(r"<(rect|circle|path)\b[^>]*/?>", "", s)),
        # Two labels at the same coordinates. The first attempt at this mutant
        # slid a right-edge axis label 90px left, which lands in empty space and
        # collides with nothing — it survived, and the check looked decorative
        # when it was the mutant that was wrong. Duplicating a label in place
        # guarantees the overlap the check exists to find.
        ("visual: two labels written over each other",
         lambda s: (lambda m: s.replace(m.group(0), m.group(0) + m.group(1)
                                        + "Average wait per step" + m.group(3), 1)
                    if m else s)(
             _re.search(r'(<text x="[\d.]+" y="[\d.]+" class="cl">)([^<]{6,})(</text>)', s))),
        # Label grey lightened until it stops being readable. 4.5:1 is the WCAG
        # AA bar for body text; #cfd4dc on white is about 1.5:1, which looks
        # fine in a thumbnail and disappears on a real screen.
        ("visual: axis labels too faint to read",
         lambda s: s.replace("fill:#5b6675", "fill:#cfd4dc")),
    ]
    contrast_mutants = {"visual: axis labels too faint to read"}
    killed = 0
    survivors = []
    for name, mutate in muts:
        V.fails.clear()
        V.passes[0] = 0
        if name in contrast_mutants:
            V.audit_contrast("mutant.xlsx", name, mutate(svg))
        else:
            V.audit_svg("mutant.xlsx", name, mutate(svg))
        if V.fails:
            killed += 1
        else:
            survivors.append(f"    SURVIVED [VISUAL] {name}")
    V.fails.clear()
    return killed, len(muts), survivors


def run_properties() -> tuple[int, int, list[str]]:
    """The property suite went from five permanent failures to none in one
    sitting. That is either five real fixes or five checks quietly declawed, and
    the two look identical from a green run — so pin an axis to the shipped
    example's magnitude and require the harness to say so.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import qa_properties as P
    book = TEMPLATES / "25-pareto-and-distribution.xlsx"
    if not book.exists():
        return 0, 0, []
    killed = applied = 0
    survivors = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / book.name
        shutil.copyfile(book, tmp)
        wb = load_workbook(tmp)
        pinned = False
        for ws in wb.worksheets:
            for ch in getattr(ws, "_charts", []):
                ch.y_axis.scaling.min, ch.y_axis.scaling.max = 0, 500
                pinned = True
        if pinned:
            wb.save(tmp)
            applied = 1
            P.fails.clear()
            P.passes[0] = 0
            try:
                P.test_axis_survives_rescale(tmp)
            except Exception:                                    # noqa: BLE001
                pass
            if P.fails:
                killed = 1
            else:
                survivors.append(
                    "    SURVIVED [PROPERTY] axis pinned to the example's magnitude")
            P.fails.clear()
    return killed, applied, survivors


def audit_to_set(path: Path) -> set[str]:
    Q.fails.clear()
    Q.warns.clear()
    wb = load_workbook(path)
    Q.audit_charts(path, wb)
    Q.audit_guided(path, wb)
    Q.audit_example(path, wb)
    Q.audit_rowlabel(path, wb)
    Q.audit_formula_colour(path, wb)
    return set(Q.fails)


def run(book: Path) -> tuple[int, int, list[str]]:
    """Apply every mutant to this workbook; return (killed, applied, survivors)."""
    killed = applied = 0
    survivors = []
    with tempfile.TemporaryDirectory() as td:
        # Round-tripping through openpyxl loses a little (combo sub-charts, for
        # one), so the baseline is the SAVED copy, not the shipped file. Only a
        # fail that is new against that baseline counts as a kill.
        base = Path(td) / ("base_" + book.name)
        shutil.copyfile(book, base)
        load_workbook(base).save(base)
        baseline = audit_to_set(base)
        for name, mutate, layer in MUTANTS:
            tmp = Path(td) / (name.replace(" ", "_") + "_" + book.name)
            shutil.copyfile(book, tmp)
            wb = load_workbook(tmp)
            try:
                what = mutate(wb)
            except Exception as exc:                             # noqa: BLE001
                what = None
                print(f"      ! {name}: could not apply ({type(exc).__name__}: {exc})")
            if not what:
                continue
            applied += 1
            wb.save(tmp)
            new = audit_to_set(tmp) - baseline
            hit = [f for f in new if f"[{layer}]" in f]
            if hit:
                killed += 1
            else:
                survivors.append(f"    SURVIVED [{layer}] {name} — {what}")
    return killed, applied, survivors


def main() -> int:
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    books = sorted(TEMPLATES.glob("*.xlsx"))
    if only:
        books = [b for b in books if any(o in b.name for o in only)]
    print(f"Mutation testing the QA harness against {len(books)} workbook(s).\n"
          "Every mutant reintroduces a defect this repo has actually shipped.\n")
    total_k = total_a = 0
    survivors: list[str] = []
    for book in books:
        k, a, s = run(book)
        total_k += k
        total_a += a
        survivors += s
        flag = "" if k == a else "   <-- a check did not fire"
        print(f"  {book.name:36s} {k}/{a} mutants killed{flag}")
    if not only:
        k, a, s = run_markdown()
        total_k += k
        total_a += a
        survivors += s
        docs = len(sorted(TEMPLATES.glob("*.md")))
        print(f"  {'(markdown templates)':36s} {k}/{a} mutants killed"
              f"{'' if k == a else '   <-- a check did not fire'}   across {docs} docs")
        k, a, s = run_visual()
        total_k += k
        total_a += a
        survivors += s
        print(f"  {'(preview visuals)':36s} {k}/{a} mutants killed"
              f"{'' if k == a else '   <-- a check did not fire'}")
        k, a, s = run_properties()
        total_k += k
        total_a += a
        survivors += s
        if a:
            print(f"  {'(input properties)':36s} {k}/{a} mutants killed"
                  f"{'' if k == a else '   <-- a check did not fire'}")
    print(f"\n  {total_k}/{total_a} mutants killed across {len(books)} workbooks")
    if survivors:
        print(f"\n{len(survivors)} SURVIVING MUTANT(S) — these checks cannot fail:")
        print("\n".join(sorted(set(survivors))))
        return 1
    print("\nEvery check still has teeth.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
