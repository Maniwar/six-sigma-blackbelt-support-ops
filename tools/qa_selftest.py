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
import qa_citations as C                                          # noqa: E402
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
    import re as _re

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


# ------------------------------------------------- control-chart mutants
# The two ways a control chart's worked example goes wrong, both of which this
# repo shipped: data so quiet the rule never fires, and a baseline that is
# itself out of control so every limit is computed from an unstable process.


def cc_flatten(wb):
    """Put the monitoring window back inside the limits — the state four of
    the seven charts shipped in, where the Signal column is blank on all 24
    rows and the rule has never once been evaluated."""
    ws = wb["I-MR"]
    for row, v in zip(range(34, 38), (442, 404, 416, 428)):
        ws[f"B{row}"] = v
    return "I-MR monitoring window back inside the limits"


def cc_unstable_baseline(wb):
    """Push a BASELINE point outside the limits, so the sheet computes its own
    limits from a process it shows is not in control."""
    ws = wb["Xbar-R"]
    for col in "BCDEF":
        ws[f"{col}20"] = 505
    return "Xbar-R baseline point 7 forced out of control"


CC_MUTANTS = [("control chart: worked data never signals", cc_flatten),
              ("control chart: baseline is out of control", cc_unstable_baseline)]


def run_control() -> tuple[int, int, list[str]]:
    import importlib

    V = importlib.import_module("verify")
    book = TEMPLATES / "27-control-charts.xlsx"
    killed = applied = 0
    survivors = []
    with tempfile.TemporaryDirectory() as td:
        def audit(path: Path) -> set[str]:
            V.FAILURES.clear()
            V.PASSES[0] = 0
            V.audit_control_signals(V._engine(path).calculate(), book.name)
            return set(V.FAILURES)

        # Same FILENAME, different directory. `formulas` keys every cell by the
        # workbook's file name, so a copy called base_27-... resolves nothing at
        # all — every lookup returns None, the audit fails identically before and
        # after, and both mutants survive against a check that was working. That
        # cost a round trip and is exactly the false negative a mutation suite
        # is supposed to catch, so it is written down rather than just fixed.
        def stage(sub: str) -> Path:
            d = Path(td) / sub
            d.mkdir()
            dst = d / book.name
            shutil.copyfile(book, dst)
            return dst

        baseline = audit(stage("base"))
        for i, (name, mutate) in enumerate(CC_MUTANTS):
            tmp = stage(f"m{i}")
            wb = load_workbook(tmp)
            what = mutate(wb)
            if not what:
                continue
            wb.save(tmp)
            applied += 1
            if audit(tmp) - baseline:
                killed += 1
            else:
                survivors.append(f"    SURVIVED [CONTROL] {name} — {what}")
    V.FAILURES.clear()
    V.PASSES[0] = 0
    return killed, applied, survivors


# ------------------------------------------------------ guidance mutants
# md_guidance.py holds a second copy of the pack's worked example, and a second
# copy of a number is a number that will drift. It had: it still carried the
# benefit chain that was withdrawn for being causally impossible, and it
# rewrote every document's preamble with a bare "14.2% reopen rate" — the one
# sentence those documents now exist to warn against. Nothing in the build ran
# it, so nothing noticed for a release.
#
# These mutate the module rather than a file, so each one saves and restores.


def gm_drift_figure(MG):
    """A worked-example number the pack does not state anywhere."""
    for name, vals in MG.EXAMPLE.items():
        for label, v in vals.items():
            if any(c.isdigit() for c in v):
                vals[label] = "999,777 units at $888.55"
                return f"{name} {label!r} offers a figure nothing states"
    return None


def gm_dead_row(MG):
    """A key that addresses a row no template has — dead weight carrying a
    number, which is how the stale ones hid."""
    for name, vals in MG.EXAMPLE.items():
        if vals:
            k = next(iter(vals))
            vals["Row that no template has"] = vals.pop(k)
            return f"{name} {k!r} renamed to a row that does not exist"
    return None


def gm_unpopulated_preamble(MG):
    """The preamble that says 14.2% without saying 14.2% of WHAT."""
    orig = MG.block
    MG.block = lambda n: orig(n).replace("OD-BIL-004-ADJ", "the billing queue")
    return "preamble no longer names the population it measures"


GUIDE_MUTANTS = [("guidance: a figure the pack does not state", gm_drift_figure),
                 ("guidance: a row no template has", gm_dead_row),
                 ("guidance: preamble drops the population", gm_unpopulated_preamble)]


def run_guidance() -> tuple[int, int, list[str]]:
    import copy
    import importlib

    V = importlib.import_module("verify")
    MG = importlib.import_module("md_guidance")

    def fails() -> list[str]:
        V.FAILURES.clear()
        V.PASSES[0] = 0
        V.test_guidance()
        return list(V.FAILURES)

    killed = applied = 0
    survivors = []
    baseline = fails()
    for name, mutate in GUIDE_MUTANTS:
        saved, saved_block = copy.deepcopy(MG.EXAMPLE), MG.block
        try:
            what = mutate(MG)
            if not what:
                continue
            applied += 1
            if set(fails()) - set(baseline):
                killed += 1
            else:
                survivors.append(f"    SURVIVED [GUIDANCE] {name} — {what}")
        finally:
            MG.EXAMPLE.clear()
            MG.EXAMPLE.update(saved)
            MG.block = saved_block
    V.FAILURES.clear()
    V.PASSES[0] = 0
    return killed, applied, survivors


# ------------------------------------------------------- numeric mutants
# The #N/A exemption used to be a hand-written list of column spans, and two
# workbooks that use the same NA() idiom were never added to it — so the gate
# ran red on 37 deliberate cells for months and everyone learned to read past
# it. It is now a property of the formula: a deliberate gap CALLS NA(), an
# accidental one falls out of a lookup that missed.
#
# That rule is only worth having if it can tell the two apart, so the first
# mutant leaves the cell reporting the very same #N/A and changes nothing but
# the REASON. If the check survives that, it is reading the value and calling
# it a design decision, which is where the old list ended up.
#
# audit_numeric recalculates a whole workbook, far too slow for the per-mutant
# loop above, so this runs only on the four workbooks that use NA() at all.
NA_BOOKS = ["05-data-collection-plan", "19-black-belt-calculators",
            "25-pareto-and-distribution", "27-control-charts"]
MISS = '=MATCH("no such row",$A$1:$A$2,0)'


def nm_reason_swap(wb):
    """A gap that is #N/A because a lookup missed, not because it was written.

    Every NA() in the book, not the first one found: `=IF(I5="",NA(),...)` on a
    row that HAS data never takes its NA() branch, so swapping that one changes
    no value and proves nothing.
    """
    n = 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and "NA()" in c.value.replace(" ", ""):
                    c.value = c.value.replace("NA()", MISS.lstrip("="))
                    n += 1
    return f"{n} deliberate gap(s) now come from a missed lookup" if n else None


def nm_hidden_break(wb):
    """A broken lookup somewhere ordinary — the base check, not the exemption."""
    for ws in wb.worksheets:
        if ws.max_row < 2:
            continue
        ws.cell(row=ws.max_row + 3, column=60).value = MISS
        return f"broken lookup dropped into {ws.title}!BH{ws.max_row}"
    return None


NUM_MUTANTS = [("numeric: #N/A for the wrong reason", nm_reason_swap),
               ("numeric: a lookup that misses", nm_hidden_break)]


def run_numeric() -> tuple[int, int, list[str]]:
    killed = applied = 0
    survivors = []
    with tempfile.TemporaryDirectory() as td:
        for stem in NA_BOOKS:
            book = TEMPLATES / f"{stem}.xlsx"
            base = Path(td) / ("base_" + book.name)
            shutil.copyfile(book, base)
            load_workbook(base).save(base)
            Q.fails.clear()
            Q.audit_numeric(base)
            baseline = set(Q.fails)
            for name, mutate in NUM_MUTANTS:
                safe = "".join(ch if ch.isalnum() else "_" for ch in name)
                tmp = Path(td) / (safe + "_" + book.name)
                shutil.copyfile(book, tmp)
                wb = load_workbook(tmp)
                what = mutate(wb)
                if not what:
                    continue
                wb.save(tmp)
                applied += 1
                Q.fails.clear()
                Q.audit_numeric(tmp)
                if [f for f in set(Q.fails) - baseline if "[NUMERIC]" in f]:
                    killed += 1
                else:
                    survivors.append(
                        f"    SURVIVED [NUMERIC] {name} on {book.name} — {what}")
    return killed, applied, survivors


# ------------------------------------------------------ citation mutants
# This layer shipped DEAD. tools/qa_citations.py was written, wired into
# verify.py, and never called by main() — so for one whole release the pack's
# 163 cross-references were resolved by nothing at all, and the harness said
# "PASSED" with the same confidence it says everything else. That is the exact
# failure a mutation suite exists to catch, and it caught it only because these
# mutants were written afterwards. Anything not mutated here can die the same
# way without anybody noticing.
#
# Citations are cross-document, so unlike the markdown mutants these cannot run
# against one file in isolation: the whole templates directory is copied, one
# document is edited, and the resolver is pointed at the copy.


def _cite_runs(text: str, want_figures: bool):
    """Citation runs in this document, optionally only the ones whose clause
    demands a figure (the ones the resolution check can actually judge)."""
    out = []
    for i, line in enumerate(text.split("\n"), start=1):
        masked = C.RE_RUN.sub(lambda x: " " * len(x.group(0)), line)
        for m in C.RE_RUN.finditer(line):
            if not m.group(1).endswith(".md"):
                continue
            want = C.figures(C.sentence_around(masked, m.start()))
            if want or not want_figures:
                out.append((i, m, want))
    return out


def _retarget(text: str, i: int, m, line_no) -> str:
    lines = text.split("\n")
    lines[i - 1] = (lines[i - 1][:m.start()] + f"{m.group(1)}:{line_no}"
                    + lines[i - 1][m.end():])
    return "\n".join(lines)


def cite_drift(text: str):
    """A citation that no longer lands on its row.

    The pack cites by line number and every edit shifts them — one pass added
    seventeen lines to the charter and silently broke references in four other
    files. The mutant moves a reference onto a line that carries none of the
    figures its sentence claims, and stays clear of the +/-2 window the check
    forgives as an off-by-a-line.
    """
    for i, m, want in _cite_runs(text, want_figures=True):
        tgt = TEMPLATES / m.group(1)
        if not tgt.exists():
            continue
        body = tgt.read_text(encoding="utf-8").split("\n")
        for j, ln in enumerate(body, start=1):
            if not ln.strip():
                continue
            near = "\n".join(body[max(0, j - 3):j + 2])
            if want & {C.norm(x.group(0)) for x in C.RE_FIG.finditer(near)}:
                continue
            return _retarget(text, i, m, j), f"moved {m.group(0)} to :{j}"
    return None, None


def cite_past_eof(text: str):
    """A citation into a document that has since been shortened."""
    for i, m, _ in _cite_runs(text, want_figures=False):
        if (TEMPLATES / m.group(1)).exists():
            return _retarget(text, i, m, 99999), f"sent {m.group(0)} past the end"
    return None, None


def cite_blank(text: str):
    """A citation onto a line with nothing on it — what a deleted row leaves."""
    for i, m, _ in _cite_runs(text, want_figures=False):
        tgt = TEMPLATES / m.group(1)
        if not tgt.exists():
            continue
        body = tgt.read_text(encoding="utf-8").split("\n")
        for j, ln in enumerate(body, start=1):
            if not ln.strip():
                return _retarget(text, i, m, j), f"pointed {m.group(0)} at a blank line"
    return None, None


CITE_MUTANTS = [("citation: drifted off its row", cite_drift),
                ("citation: past the end of the file", cite_past_eof),
                ("citation: onto a blank line", cite_blank)]


def _cite_fails(work: Path) -> set[str]:
    C.fails.clear()
    C.warns.clear()
    C.checked[0] = 0
    cache: dict = {}
    for doc in sorted(work.glob("*.md")):
        C.check_file(doc, cache)
    return set(C.fails)


def run_citations() -> tuple[int, int, list[str]]:
    killed = applied = 0
    survivors = []
    with tempfile.TemporaryDirectory() as td:
        work = Path(td) / "templates"
        shutil.copytree(TEMPLATES, work)
        real = C.TEMPLATES
        C.TEMPLATES = work
        try:
            baseline = _cite_fails(work)
            for doc in sorted(TEMPLATES.glob("*.md")):
                text = doc.read_text(encoding="utf-8")
                for name, mutate in CITE_MUTANTS:
                    out, what = mutate(text)
                    if out is None:
                        continue
                    (work / doc.name).write_text(out, encoding="utf-8")
                    applied += 1
                    if _cite_fails(work) - baseline:
                        killed += 1
                    else:
                        survivors.append(
                            f"    SURVIVED [CITATION] {name} on {doc.name} — {what}")
                    (work / doc.name).write_text(text, encoding="utf-8")
        finally:
            C.TEMPLATES = real
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
                # A mutant that raises is evidence of nothing, and it used to
                # print a note and move on. `m_paint_over_the_inputs` died on a
                # NameError against sixteen of the twenty-one workbooks and the
                # suite still reported every mutant killed, because a mutant
                # that never applied is not counted as applied. Same shape as
                # the citation check that was never called: silent absence
                # reading as success. It fails the run now.
                what = None
                survivors.append(f"    ERRORED  [{layer}] {name} on {book.name} "
                                 f"— {type(exc).__name__}: {exc}")
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
        k, a, s = run_control()
        total_k += k
        total_a += a
        survivors += s
        print(f"  {'(control charts)':36s} {k}/{a} mutants killed"
              f"{'' if k == a else '   <-- a check did not fire'}")
        k, a, s = run_guidance()
        total_k += k
        total_a += a
        survivors += s
        print(f"  {'(template filler)':36s} {k}/{a} mutants killed"
              f"{'' if k == a else '   <-- a check did not fire'}")
        k, a, s = run_numeric()
        total_k += k
        total_a += a
        survivors += s
        print(f"  {'(recalculated values)':36s} {k}/{a} mutants killed"
              f"{'' if k == a else '   <-- a check did not fire'}")
        k, a, s = run_citations()
        total_k += k
        total_a += a
        survivors += s
        print(f"  {'(cross-references)':36s} {k}/{a} mutants killed"
              f"{'' if k == a else '   <-- a check did not fire'}")
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
