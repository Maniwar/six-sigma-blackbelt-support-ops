#!/usr/bin/env python3
"""Canonical formula set for the Excel templates.

This file is the single source of truth for every *calculated* cell in
templates/*.xlsx. Running it is idempotent: it rewrites each listed cell to the
formula below, leaving all formatting, validation and conditional formatting
untouched.

Why this exists: each workbook is mirrored in three other places (the base64
copy inside the HTML, the preview table's formula tooltips, and docs/index.html).
Editing a formula by hand in a spreadsheet is how those four copies drifted apart.
Change a formula here, then run tools/sync_html.py.

    python3 tools/patch_workbooks.py
    python3 tools/sync_html.py
    python3 tools/verify.py

Requires: openpyxl
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chart_specs import add_charts  # noqa: E402
from worked_examples import add_examples  # noqa: E402
from xlpolish import polish_workbook  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"

# Built by tools/build_templates.py, which owns them end to end. Read from the
# previews that builder writes rather than guessed from the file name: the guess
# was `^2[0-9]-`, which silently stopped covering the pack the moment a
# thirtieth template existed, and re-saving a generated workbook here is
# destructive — openpyxl's reader keeps only the first chart type in a combo.
# The regex stays as the fallback for a checkout with no previews.json.
_BUILT_RE = re.compile(r"^(2[0-9]|[3-9][0-9])-")


def _is_built(name: str) -> bool:
    if name in _BUILT_NAMES:
        return True
    return bool(_BUILT_RE.match(name))


def _built_names() -> set:
    import json
    p = Path(__file__).resolve().parent / "previews.json"
    try:
        return set(json.loads(p.read_text(encoding="utf-8")))
    except Exception:                                            # noqa: BLE001
        return set()


_BUILT_NAMES = _built_names()

# Fill colours used across the workbooks; the preview renderer keys off these.
YELLOW_INPUT = "FFFFF9E3"

# ---------------------------------------------------------------------------
# Formula patches: (workbook, sheet, cell, formula)
# Ranges are expressed with {r} and expanded over `rows`.
# ---------------------------------------------------------------------------

SINGLE: list[tuple[str, str, str, str]] = [
    # -- 19 calculators, sheet 1: guard every division and the two NORMSINV
    #    calls. Zero defects makes NORMSINV(1) a #NUM!, and a perfect process
    #    is a plausible input.
    ("19-black-belt-calculators.xlsx", "1 Sigma level", "B9", '=IFERROR(B7/B5,"")'),
    ("19-black-belt-calculators.xlsx", "1 Sigma level", "B11", '=IFERROR(B7/(B5*B6),"")'),
    ("19-black-belt-calculators.xlsx", "1 Sigma level", "B12", '=IFERROR(B7/(B5*B6)*1000000,"")'),
    ("19-black-belt-calculators.xlsx", "1 Sigma level", "B13", '=IFERROR(EXP(-B7/B5),"")'),
    ("19-black-belt-calculators.xlsx", "1 Sigma level", "B14", '=IFERROR(NORMSINV(1-B7/(B5*B6)),"")'),
    ("19-black-belt-calculators.xlsx", "1 Sigma level", "B15", '=IFERROR(NORMSINV(1-B7/(B5*B6))+1.5,"")'),

    # -- 19 calculators, sheet 2: the verdict read B12 (chance agreement) instead
    #    of B13 (kappa). The shipped example is the one case where both land in
    #    the same band, which is why it survived review.
    ("19-black-belt-calculators.xlsx", "2 QA agreement (kappa)", "B11", '=IFERROR((B5+B8)/SUM(B5:B8),"")'),
    ("19-black-belt-calculators.xlsx", "2 QA agreement (kappa)", "B12",
     '=IFERROR(((B5+B6)/SUM(B5:B8))*((B5+B7)/SUM(B5:B8))+((B7+B8)/SUM(B5:B8))*((B6+B8)/SUM(B5:B8)),"")'),
    ("19-black-belt-calculators.xlsx", "2 QA agreement (kappa)", "B13",
     '=IFERROR((B11-B12)/(1-B12),"")'),
    ("19-black-belt-calculators.xlsx", "2 QA agreement (kappa)", "B14",
     '=IF(B13="","",IF(B13>0.9,"EXCELLENT — fit for purpose",'
     'IF(B13>0.75,"GOOD — usable, fix the weakest rubric items",'
     'IF(B13>0.4,"MARGINAL — do NOT use for individual performance management",'
     '"UNACCEPTABLE — halt all use of this data until fixed"))))'),

    # -- 19 calculators, sheet 3: the verdict read B15, which sits inside the
    #    merged note A15:D15 and is therefore always empty -> every input
    #    returned "NOT CAPABLE". Ppu lives in B13.
    ("19-black-belt-calculators.xlsx", "3 SLA capability", "B11", '=IFERROR((B5-B6)/B7,"")'),
    ("19-black-belt-calculators.xlsx", "3 SLA capability", "B12", '=IFERROR(1-NORMSDIST((B5-B6)/B7),"")'),
    ("19-black-belt-calculators.xlsx", "3 SLA capability", "B13", '=IFERROR((B5-B6)/(3*B7),"")'),
    ("19-black-belt-calculators.xlsx", "3 SLA capability", "B17",
     '=IF(B13="","",IF(B13>=1.33,"CAPABLE",IF(B13>=1,"MARGINAL — customers notice",'
     '"NOT CAPABLE — you are producing breaches")))'),

    # -- 19 calculators, sheets 4-7: divide-by-zero guards.
    ("19-black-belt-calculators.xlsx", "4 Backlog and lead time", "B9", '=IFERROR(B5/B6,"")'),
    ("19-black-belt-calculators.xlsx", "4 Backlog and lead time", "B10", '=IFERROR(B5/B6*24,"")'),
    ("19-black-belt-calculators.xlsx", "5 Process efficiency", "B9", '=IFERROR(B6*60-B5,"")'),
    ("19-black-belt-calculators.xlsx", "5 Process efficiency", "B10", '=IFERROR(B5/(B6*60),"")'),
    ("19-black-belt-calculators.xlsx", "6 Staffing", "B11", '=IFERROR(B5*B6/3600/B7,"")'),
    ("19-black-belt-calculators.xlsx", "6 Staffing", "B12",
     '=IFERROR(B5*B6/3600/B7/(1-B8)-B5*B6/3600/B7,"")'),
    ("19-black-belt-calculators.xlsx", "6 Staffing", "B13", '=IFERROR(B5*B6/3600/B7/(1-B8),"")'),
    ("19-black-belt-calculators.xlsx", "7 Benefit — AHT", "B12", '=IFERROR(B5*B6/3600/B8,"")'),
    ("19-black-belt-calculators.xlsx", "7 Benefit — AHT", "B13", '=IFERROR(B5*B6/3600/B8/1760,"")'),
    ("19-black-belt-calculators.xlsx", "7 Benefit — AHT", "B14", '=IFERROR(B5*B6/3600/B8*B7,"")'),
    ("19-black-belt-calculators.xlsx", "7 Benefit — AHT", "B15", '=IFERROR(B5*B6/3600/B8*B7*B9,"")'),

    # -- 19 calculators, sheet 9: NPV hardcoded years 1-3 while Simple ROI used
    #    B6*B7 for any B7, so the two disagreed above three years; year 1 was
    #    also unguarded, so B7=0 still banked a full year. The closed-form
    #    annuity is correct for any number of years and matches the HTML card,
    #    which loops y=1..yr.
    ("19-black-belt-calculators.xlsx", "9 ROI and payback", "B10", '=IF($B$7>=1,B6/(1+B8)^1,0)'),
    ("19-black-belt-calculators.xlsx", "9 ROI and payback", "B11", '=IF($B$7>=2,B6/(1+B8)^2,0)'),
    ("19-black-belt-calculators.xlsx", "9 ROI and payback", "B12", '=IF($B$7>=3,B6/(1+B8)^3,0)'),
    ("19-black-belt-calculators.xlsx", "9 ROI and payback", "B14", '=IFERROR((B6*B7-B5)/B5,"")'),
    ("19-black-belt-calculators.xlsx", "9 ROI and payback", "B15",
     '=IFERROR(-B5+IF(B8=0,B6*B7,B6*(1-(1+B8)^-B7)/B8),"")'),

    # -- 10 VSM: the column header says "% of lead time" but the denominator was
    #    E32 (total waiting time), overstating every share. Lead time is E33.
    #    E33/E34/E35 now reference the subtotals instead of re-summing.
    ("10-value-stream-map.xlsx", "Value stream", "E33", "=E31+E32"),
    ("10-value-stream-map.xlsx", "Value stream", "E34", "=(E31+E32)/60"),
    ("10-value-stream-map.xlsx", "Value stream", "E35", '=IFERROR(E31/E33,"")'),
    # PRODUCT() over an empty range returns 0, not an error, so IFERROR never
    # fired and a blank template reported RTY = 0%.
    ("10-value-stream-map.xlsx", "Value stream", "E36", '=IF(COUNT(G10:G28)=0,"",PRODUCT(G10:G28))'),

    # -- 12 FMEA: risk reduction divided the mean of the remediated rows by the
    #    mean of *all* scored rows. AVERAGEIF restricts both sides to the rows
    #    that actually have an after-score.
    ("12-fmea.xlsx", "FMEA", "D44",
     '=IFERROR(1-AVERAGE(R11:R35)/AVERAGEIF(R11:R35,">0",J11:J35),"")'),

    # -- 15 solution selection: the old form ran VALUE() over the whole range, so
    #    one pasted free-text value made the entire summary #VALUE!. Wrapping it
    #    in IFERROR does not help - IFERROR is not reliably element-wise inside
    #    SUMPRODUCT. Comparing the leading character as text cannot raise an
    #    error at all, and the trailing space keeps a blank cell from matching.
    ("15-solution-selection-matrix.xlsx", "Solution selection", "E37",
     '=SUMPRODUCT((M14:M32="Yes")*((LEFT(L14:L32&" ",1)="1")+(LEFT(L14:L32&" ",1)="2")'
     '+(LEFT(L14:L32&" ",1)="3")))'),
    ("15-solution-selection-matrix.xlsx", "Solution selection", "E38",
     '=SUMPRODUCT((M14:M32="Yes")*((LEFT(L14:L32&" ",1)="5")+(LEFT(L14:L32&" ",1)="6")))'),

    # -- 17 control plan: same treatment, and E32 now references E30/E29 rather
    #    than duplicating the whole SUMPRODUCT.
    ("17-control-plan.xlsx", "Control plan", "E30",
     '=SUMPRODUCT((A10:A27<>"")*((LEFT(P10:P27&" ",1)="1")+(LEFT(P10:P27&" ",1)="2")'
     '+(LEFT(P10:P27&" ",1)="3")))'),
    ("17-control-plan.xlsx", "Control plan", "E31",
     '=SUMPRODUCT((A10:A27<>"")*((LEFT(P10:P27&" ",1)="5")+(LEFT(P10:P27&" ",1)="6")))'),
    ("17-control-plan.xlsx", "Control plan", "E32", '=IFERROR(E30/E29,"")'),

    # -- 05 data collection: a target rate at or above 100% produced a negative
    #    variance term and a confidently wrong sample size. Blank it instead.
    ("05-data-collection-plan.xlsx", "Sample size calculator", "C13",
     '=IF(OR(C5<=0,C5>=1,C6<=0,C5+C6>=1,C7<=0,C7>=1,C8<=0,C8>=1),"",'
     'ROUNDUP((NORMSINV(1-C7/2)+NORMSINV(C8))^2*(C5*(1-C5)+(C5+C6)*(1-C5-C6))/C6^2,0))'),
    ("05-data-collection-plan.xlsx", "Sample size calculator", "C14", '=IF(C13="","",2*C13)'),
    ("05-data-collection-plan.xlsx", "Sample size calculator", "C11", '=IFERROR(NORMSINV(1-C7/2),"")'),
    ("05-data-collection-plan.xlsx", "Sample size calculator", "C12", '=IFERROR(NORMSINV(C8),"")'),
]

# Repeated row formulas: (workbook, sheet, cell_template, formula_template, rows)
REPEATED: list[tuple[str, str, str, str, range]] = [
    # -- 13 hypothesis log: the blank-guard checked the p-value and the effect
    #    size but not the practical threshold. A blank threshold fell through
    #    VALUE("") -> IFERROR -> 0, so |effect| >= 0 was always true and every
    #    significant result was auto-labelled "real and matters" - the exact
    #    discipline the template exists to enforce. Alpha now reads $B$8 instead
    #    of being hardcoded to 0.05.
    ("13-hypothesis-test-log.xlsx", "Test log", "N{r}",
     '=IF(OR(J{r}="",K{r}="",M{r}=""),"",IF(J{r}>$B$8,"NOT SIGNIFICANT",'
     'IF(ABS(IFERROR(VALUE(SUBSTITUTE(SUBSTITUTE(K{r},"pts",""),"%","")),0))'
     '>=ABS(IFERROR(VALUE(SUBSTITUTE(SUBSTITUTE(M{r},"pts",""),"%","")),0)),'
     '"YES — real and matters","NO — significant but too small")))',
     range(11, 34)),

    # -- 10 VSM waiting states: "% of lead time" must divide by lead time (E33),
    #    not total waiting time (E32).
    ("10-value-stream-map.xlsx", "Value stream", "C{r}", '=IFERROR(B{r}/$E$33,"")', range(44, 50)),
]

# Literal value / label corrections: (workbook, sheet, cell, value)
VALUES: list[tuple[str, str, str, object]] = [
    # The worked example used the bare number 2, which is not a member of the
    # cell's own dropdown list ("2 Design it out"). 17-control-plan already uses
    # the string form.
    ("15-solution-selection-matrix.xlsx", "Solution selection", "L14", "2 Design it out"),
    # Say out loud that the ratio is computed on remediated rows only.
    ("12-fmea.xlsx", "FMEA", "A44", "Risk reduction (on remediated rows)"),
    ("13-hypothesis-test-log.xlsx", "Test log", "A8", "Significance level (alpha)"),
    ("13-hypothesis-test-log.xlsx", "Test log", "B8", 0.05),
    ("13-hypothesis-test-log.xlsx", "Test log", "C8",
     "Used by the 'Above threshold?' column. 0.05 is standard; drop to 0.01 when acting on the result is expensive."),
    ("19-black-belt-calculators.xlsx", "9 ROI and payback", "A17",
     "Under 18 months payback is generally an easy sell. Net present value is calculated across all the years "
     "you model; the three rows above show the first three. And set year-one expectations honestly: a Black Belt "
     "completes only one project while learning, and a first cohort picks the least well-selected projects."),
    ("05-data-collection-plan.xlsx", "Sample size calculator", "A16",
     "Notice how fast this grows as the effect you want to detect gets smaller — halving the detectable effect "
     "roughly quadruples the sample. The sample size stays blank if the inputs are impossible, for example when "
     "the current rate plus the change you want to detect reaches 100%."),
]


def patch_formulas(verbose: bool = True) -> int:
    """Apply every patch. Returns the number of cells changed."""
    by_file: dict[str, list] = {}
    for wbname, sheet, cell, formula in SINGLE:
        by_file.setdefault(wbname, []).append((sheet, cell, formula))
    for wbname, sheet, celltpl, ftpl, rows in REPEATED:
        for r in rows:
            by_file.setdefault(wbname, []).append(
                (sheet, celltpl.format(r=r), ftpl.format(r=r))
            )
    for wbname, sheet, cell, value in VALUES:
        by_file.setdefault(wbname, []).append((sheet, cell, value))

    changed = 0
    for wbname in sorted(by_file):
        path = TEMPLATES / wbname
        if not path.exists():
            raise SystemExit(f"missing workbook: {path}")
        wb = load_workbook(path)
        local = 0
        for sheet, cell, value in by_file[wbname]:
            ws = wb[sheet]
            if ws[cell].value != value:
                ws[cell] = value
                local += 1
        _style_new_cells(wb)
        local += _add_validations(wb, wbname)
        local += add_examples(wb, wbname)
        local += add_charts(wb, wbname)
        local += polish_workbook(wb)
        # openpyxl's zip output is not byte-stable, so saving an unchanged
        # workbook would churn its base64 copy in the HTML on every run.
        if local:
            wb.save(path)
        changed += local
        if verbose:
            state = f"{local:3d} cell(s) rewritten" if local else "  unchanged"
            print(f"  {wbname:46s} {state}")

    # Workbooks with no calculated cells still need the finishing pass — the
    # X-Y matrix is pure scoring and would otherwise never be polished at all.
    for path in sorted(TEMPLATES.glob("*.xlsx")):
        if path.name in by_file:
            continue
        if _is_built(path.name):
            # build_templates.py already polishes these at build time. Loading
            # and re-saving here would be destructive: openpyxl's reader keeps
            # only the first chart type in a combo, so every reference line laid
            # over a bar chart would be dropped on the way back out.
            continue
        wb = load_workbook(path)
        local = add_examples(wb, path.name)
        local += add_charts(wb, path.name)
        local += polish_workbook(wb)
        if local:
            wb.save(path)
            changed += local
            if verbose:
                print(f"  {path.name:46s} {local:3d} layout fix(es)")
    return changed


def _style_new_cells(wb) -> None:
    """Style the alpha input added to the hypothesis-test log."""
    if "Test log" not in wb.sheetnames:
        return
    ws = wb["Test log"]
    if ws["A8"].value != "Significance level (alpha)":
        return
    ws["A8"].font = Font(bold=True, size=10)
    ws["B8"].fill = PatternFill("solid", fgColor=YELLOW_INPUT)
    ws["B8"].number_format = "0.00"
    ws["B8"].alignment = Alignment(horizontal="center")
    ws["C8"].font = Font(size=9, italic=True, color="FF6B7280")


def _add_validations(wb, wbname: str) -> int:
    """Bound the inputs that previously accepted impossible values.

    Returns the number of validations added, so the caller can skip the save
    when nothing changed.
    """
    specs: list[tuple[str, str, str, str, str, str]] = []
    if wbname == "19-black-belt-calculators.xlsx":
        specs = [
            ("9 ROI and payback", "B7", "whole", "1", "10",
             "Years to model must be a whole number from 1 to 10."),
            ("9 ROI and payback", "B8", "decimal", "0", "1",
             "Discount rate is a share, for example 0.10 for 10%."),
            ("3 SLA capability", "B7", "decimal", "0.0000001", "100000",
             "Standard deviation must be greater than zero."),
            ("6 Staffing", "B7", "decimal", "0.05", "1", "Target occupancy is a share between 0.05 and 1."),
            ("6 Staffing", "B8", "decimal", "0", "0.95", "Shrinkage is a share below 0.95."),
            ("7 Benefit — AHT", "B8", "decimal", "0.05", "1", "Occupancy is a share between 0.05 and 1."),
            ("1 Sigma level", "B6", "whole", "1", "50", "Opportunities per unit must be at least 1."),
        ]
    elif wbname == "05-data-collection-plan.xlsx":
        specs = [
            ("Sample size calculator", "C5", "decimal", "0.001", "0.999", "Current rate is a share between 0 and 1."),
            ("Sample size calculator", "C6", "decimal", "0.001", "0.999",
             "Change to detect is a share, for example 0.03 for 3 percentage points."),
            ("Sample size calculator", "C7", "decimal", "0.001", "0.5", "Alpha is a share, typically 0.05 or 0.01."),
            ("Sample size calculator", "C8", "decimal", "0.5", "0.999", "Power is a share, typically 0.80 or 0.90."),
        ]
    elif wbname == "13-hypothesis-test-log.xlsx":
        specs = [("Test log", "B8", "decimal", "0.001", "0.5",
                  "Alpha is a share, typically 0.05 or 0.01.")]

    added = 0
    for sheet, cell, dtype, lo, hi, msg in specs:
        ws = wb[sheet]
        # openpyxl normalises a single-cell sqref to "C5", but writing one via
        # dv.add() can leave "C5:C5" - accept either so re-running is a no-op.
        existing = {str(dv.sqref) for dv in ws.data_validations.dataValidation}
        if cell in existing or f"{cell}:{cell}" in existing:
            continue
        dv = DataValidation(type=dtype, operator="between", formula1=lo, formula2=hi,
                            allow_blank=True, showErrorMessage=True)
        dv.error = msg
        dv.errorTitle = "Check this number"
        ws.add_data_validation(dv)
        dv.add(ws[cell])
        added += 1
    return added


if __name__ == "__main__":
    print("Patching workbooks in", TEMPLATES)
    n = patch_formulas()
    print(f"Done: {n} cell(s) rewritten.")
    sys.exit(0)
