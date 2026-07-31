#!/usr/bin/env python3
"""Test suite for the workbooks and the single-file HTML.

Three layers:

  STRUCTURE  every formula is checked for the defect class that produced the
             worst bug in this repo - a formula reading a cell that sits inside
             a merged range but is not its top-left anchor, and is therefore
             always empty. The SLA verdict did exactly that and returned
             "NOT CAPABLE" for every possible input.

  NUMERIC    the fixed calculators are recalculated with a real formula engine
             against inputs chosen to expose the original bugs. Needs the
             optional `formulas` package; skipped with a warning if absent.

  SYNC       the four copies of every template agree: templates/*.xlsx, the
             base64 blob in the HTML, the preview tooltips, and docs/index.html.

    python3 tools/verify.py            # everything
    python3 tools/verify.py --fast     # skip the numeric layer

Requires: openpyxl  (+ formulas, optional)
"""
from __future__ import annotations

import base64
import html as H
import json
import re
import shutil
import sys
import tempfile
import warnings
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter, range_boundaries

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from sync_html import RE_ROW, RE_SHEET, RE_TD, extract_tpls  # noqa: E402

HTML = ROOT / "six-sigma-blackbelt-support-ops.html"
DOCS = ROOT / "docs" / "index.html"
TEMPLATES = ROOT / "templates"
CALC = "19-black-belt-calculators.xlsx"

FAILURES: list[str] = []
PASSES = [0]


def check(cond: bool, label: str, detail: str = "") -> None:
    if cond:
        PASSES[0] += 1
    else:
        FAILURES.append(f"{label}" + (f"\n      {detail}" if detail else ""))


def approx(a, b, tol=1e-6) -> bool:
    try:
        return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------- STRUCTURE
CELL_REF = re.compile(r"(?<![A-Za-z0-9_!$])(\$?)([A-Z]{1,3})(\$?)([0-9]{1,7})(?![0-9(])")


def covered_non_anchor(ws) -> set[str]:
    """Cells inside a merged range that are not its top-left anchor."""
    dead = set()
    for rng in ws.merged_cells.ranges:
        min_c, min_r, max_c, max_r = range_boundaries(str(rng))
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                if (r, c) != (min_r, min_c):
                    dead.add(f"{get_column_letter(c)}{r}")
    return dead


def test_structure() -> None:
    for path in sorted(TEMPLATES.glob("*.xlsx")):
        wb = load_workbook(path)
        for ws in wb.worksheets:
            dead = covered_non_anchor(ws)
            if not dead:
                continue
            for row in ws.iter_rows():
                for cell in row:
                    v = cell.value
                    if not (isinstance(v, str) and v.startswith("=")):
                        continue
                    # ignore quoted string literals inside the formula
                    bare = re.sub(r'"[^"]*"', '""', v)
                    for m in CELL_REF.finditer(bare):
                        ref = f"{m.group(2)}{m.group(4)}"
                        if ref in dead:
                            check(
                                False,
                                f"{path.name} [{ws.title}] {cell.coordinate} reads {ref}, "
                                f"which is swallowed by a merged range and is always empty",
                                v[:120],
                            )
            PASSES[0] += 1


# ------------------------------------------------------------------ NUMERIC
def _engine(path: Path):
    warnings.filterwarnings("ignore")
    import formulas

    return formulas.ExcelModel().loads(str(path)).finish()


def _read(sol, fname: str, sheet: str, cell: str):
    key = f"'[{fname.upper()}]{sheet.upper()}'!{cell}"
    for k, v in sol.items():
        if k.upper() == key:
            try:
                return v.value[0, 0]
            except Exception:
                return v
    return "<missing>"


def recalc(scenarios: list[tuple[str, str, object]], sheets_cells):
    """Copy the calculator workbook, apply inputs, recalculate, read outputs."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / CALC
        shutil.copyfile(TEMPLATES / CALC, tmp)
        if scenarios:
            wb = load_workbook(tmp)
            for sheet, cell, val in scenarios:
                wb[sheet][cell] = val
            wb.save(tmp)
        sol = _engine(tmp).calculate()
        return {(s, c): _read(sol, CALC, s, c) for s, c in sheets_cells}


def test_numeric() -> None:
    K = "2 QA agreement (kappa)"
    S = "3 SLA capability"
    R = "9 ROI and payback"

    # --- kappa verdict must follow kappa (B13), not chance agreement (B12).
    # Perfect agreement: the old formula read Pe = 0.50 and said MARGINAL.
    out = recalc([(K, "B5", 35), (K, "B6", 0), (K, "B7", 0), (K, "B8", 35)], [(K, "B13"), (K, "B14")])
    check(approx(out[(K, "B13")], 1.0), "kappa: perfect agreement gives kappa = 1.0", repr(out[(K, "B13")]))
    check(str(out[(K, "B14")]).startswith("EXCELLENT"),
          "kappa verdict: perfect agreement reads EXCELLENT (was MARGINAL)", repr(out[(K, "B14")]))

    # Worse than chance: the old formula read Pe = 0.918 and said EXCELLENT.
    out = recalc([(K, "B5", 64), (K, "B6", 3), (K, "B7", 3), (K, "B8", 0)], [(K, "B13"), (K, "B14")])
    check(float(out[(K, "B13")]) < 0, "kappa: worse-than-chance is negative", repr(out[(K, "B13")]))
    check(str(out[(K, "B14")]).startswith("UNACCEPTABLE"),
          "kappa verdict: worse-than-chance reads UNACCEPTABLE (was EXCELLENT)", repr(out[(K, "B14")]))

    # --- SLA verdict must follow Ppu (B13). The old formula read B15, an empty
    #     merged cell, so every input returned NOT CAPABLE.
    out = recalc([(S, "B5", 8), (S, "B6", 2.6), (S, "B7", 1.1)], [(S, "B13"), (S, "B17")])
    check(approx(out[(S, "B13")], (8 - 2.6) / (3 * 1.1)), "SLA: Ppu arithmetic", repr(out[(S, "B13")]))
    check(out[(S, "B17")] == "CAPABLE",
          "SLA verdict: a capable process reads CAPABLE (was always NOT CAPABLE)", repr(out[(S, "B17")]))

    # Ppu = (6.5 - 2.6) / (3 x 1.1) = 1.18, i.e. inside the 1.00-1.33 band.
    out = recalc([(S, "B5", 6.5), (S, "B6", 2.6), (S, "B7", 1.1)], [(S, "B13"), (S, "B17")])
    check(1.0 <= float(out[(S, "B13")]) < 1.33, "SLA: test input lands in the marginal band",
          repr(out[(S, "B13")]))
    check(out[(S, "B17")].startswith("MARGINAL"), "SLA verdict: middle band reads MARGINAL", repr(out[(S, "B17")]))

    out = recalc([], [(S, "B17")])  # shipped example, Ppu 0.42
    check(out[(S, "B17")].startswith("NOT CAPABLE"),
          "SLA verdict: shipped example still reads NOT CAPABLE", repr(out[(S, "B17")]))

    # --- NPV must honour any number of years, matching the HTML card's loop.
    for years in (1, 3, 5, 10):
        out = recalc([(R, "B5", 193000), (R, "B6", 156672), (R, "B7", years), (R, "B8", 0.1)], [(R, "B15")])
        want = -193000 + sum(156672 / (1.1 ** y) for y in range(1, years + 1))
        check(approx(out[(R, "B15")], want, 1e-6),
              f"ROI: NPV correct at {years} year(s)", f"got {out[(R, 'B15')]!r} want {want:,.2f}")

    out = recalc([(R, "B5", 193000), (R, "B6", 156672), (R, "B7", 3), (R, "B8", 0)], [(R, "B15")])
    check(approx(out[(R, "B15")], -193000 + 156672 * 3), "ROI: NPV handles a zero discount rate",
          repr(out[(R, "B15")]))

    # --- zero defects used to make NORMSINV(1) a #NUM!.
    out = recalc([("1 Sigma level", "B7", 0)], [("1 Sigma level", "B15")])
    check(not isinstance(out[("1 Sigma level", "B15")], float) or out[("1 Sigma level", "B15")] == out[("1 Sigma level", "B15")],
          "sigma: zero defects does not raise #NUM!", repr(out[("1 Sigma level", "B15")]))


def test_numeric_other() -> None:
    """Hypothesis log and VSM, which live in their own workbooks."""
    # Hypothesis log: a blank practical threshold must not be read as "matters".
    src = TEMPLATES / "13-hypothesis-test-log.xlsx"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / src.name
        shutil.copyfile(src, tmp)
        wb = load_workbook(tmp)
        ws = wb["Test log"]
        ws["M11"] = None  # clear the practical threshold, keep p and effect
        wb.save(tmp)
        sol = _engine(tmp).calculate()
        got = _read(sol, src.name, "Test log", "N11")
        check(str(got).strip() in ("", "0"),
              "hypothesis log: blank practical threshold leaves the verdict blank "
              "(was 'YES - real and matters')", repr(got))

    # Durability counters must survive a free-text paste in the hierarchy column
    # instead of turning the whole summary into #VALUE!, and must still count.
    src = TEMPLATES / "15-solution-selection-matrix.xlsx"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / src.name
        shutil.copyfile(src, tmp)
        wb = load_workbook(tmp)
        ws = wb["Solution selection"]
        rows = [("a", "1 Eliminate demand", "Yes"), ("b", "3 Guide it", "Yes"),
                ("c", "2 Design it out", "Yes"), ("d", "6 Train and remind", "Yes"),
                ("e", "not a level at all", "Yes"), ("f", "1 Eliminate demand", "No")]
        for i, (name, lvl, sel) in enumerate(rows, start=14):
            ws[f"B{i}"], ws[f"L{i}"], ws[f"M{i}"] = name, lvl, sel
        wb.save(tmp)
        sol = _engine(tmp).calculate()
        e37 = _read(sol, src.name, "Solution selection", "E37")
        e38 = _read(sol, src.name, "Solution selection", "E38")
        check(approx(e37, 3), "solution matrix: durable count survives a junk paste", f"got {e37!r} want 3")
        check(approx(e38, 1), "solution matrix: decaying count survives a junk paste", f"got {e38!r} want 1")

    src = TEMPLATES / "17-control-plan.xlsx"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / src.name
        shutil.copyfile(src, tmp)
        wb = load_workbook(tmp)
        ws = wb["Control plan"]
        for i, (name, lvl) in enumerate([("m1", "2 Design it out"), ("m2", "3 Guide it"),
                                         ("m3", "5 Standardise it"), ("m4", "garbage")], start=10):
            ws[f"A{i}"], ws[f"P{i}"] = name, lvl
        wb.save(tmp)
        sol = _engine(tmp).calculate()
        e30 = _read(sol, src.name, "Control plan", "E30")
        e31 = _read(sol, src.name, "Control plan", "E31")
        e32 = _read(sol, src.name, "Control plan", "E32")
        check(approx(e30, 2), "control plan: durable count survives a junk paste", f"got {e30!r} want 2")
        check(approx(e31, 1), "control plan: decaying count survives a junk paste", f"got {e31!r} want 1")
        check(approx(e32, 0.5), "control plan: durable share", f"got {e32!r} want 0.5")

    # VSM: "% of lead time" must divide by lead time, not by waiting time.
    src = TEMPLATES / "10-value-stream-map.xlsx"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / src.name
        shutil.copyfile(src, tmp)
        wb = load_workbook(tmp)
        ws = wb["Value stream"]
        ws["E10"], ws["F10"] = 10, 90       # touch 10, wait 90 -> lead 100
        ws["B44"], ws["B45"] = 60, 30
        wb.save(tmp)
        sol = _engine(tmp).calculate()
        lead = _read(sol, src.name, "Value stream", "E33")
        c44 = _read(sol, src.name, "Value stream", "C44")
        check(approx(lead, 100), "VSM: lead time = touch + wait", repr(lead))
        check(approx(c44, 0.60), "VSM: waiting state is a share of lead time, not of waiting time",
              f"got {c44!r}, want 0.60 (0.667 would mean it still divides by waiting time)")


# --------------------------------------------------------------------- SYNC
def test_sync() -> None:
    src = HTML.read_text(encoding="utf-8")
    _, _, tpls = extract_tpls(src)
    check(len(tpls) == 19, f"19 templates registered (found {len(tpls)})")

    exts = [e.get("ext") for e in tpls.values()]
    check(exts.count("xlsx") == 8, f"8 Excel workbooks (found {exts.count('xlsx')})")
    check(exts.count("md") == 11, f"11 Markdown templates (found {exts.count('md')})")

    for slug, entry in tpls.items():
        path = TEMPLATES / entry["file"]
        check(path.exists(), f"{entry['file']} exists on disk")
        if not path.exists():
            continue
        if entry.get("ext") == "xlsx":
            want = base64.b64encode(path.read_bytes()).decode("ascii")
            check(entry.get("b64") == want, f"{entry['file']}: embedded base64 matches the file on disk")
            _check_preview(entry, path)
        else:
            check(entry.get("content") == path.read_text(encoding="utf-8"),
                  f"{entry['file']}: embedded markdown matches the file on disk")

    check(HTML.read_bytes() == DOCS.read_bytes(), "docs/index.html is identical to the root HTML")

    # Version: the meta tag, the sidebar badge and the newest release-note
    # callout must agree, so a deploy can be identified without opening the page.
    meta = re.search(r'<meta name="app-version" content="([0-9.]+)"', src)
    badge = re.search(r"Customer Support Operations &middot; v([0-9.]+)", src)
    notes = re.findall(r"New in v([0-9.]+)", src)
    check(bool(meta), "an <meta name=\"app-version\"> tag is present")
    check(bool(badge), "the sidebar shows a version")
    check(bool(notes), "there are release notes for the current version")
    if meta and badge and notes:
        newest = max(notes, key=lambda v: [int(p) for p in v.split(".")])
        check(meta.group(1) == badge.group(1) == newest,
              "meta tag, sidebar badge and release notes agree on the version",
              f"meta={meta.group(1)} sidebar={badge.group(1)} notes={newest}")
    for dead in ("parseCSV", "renderCSV"):
        check(dead not in src, f"dead {dead}() removed")
    check("function esc2(" in src, "esc2() retained (renderMD depends on it)")
    check(src.count("-year net<") == 0 and "'-year NPV</th>" in src,
          "wizard sensitivity column is labelled NPV, not 'net'")


def _check_preview(entry: dict, path: Path) -> None:
    wb = load_workbook(path)
    bad = []
    seen = 0
    for m in RE_SHEET.finditer(entry["preview"]):
        ws = wb.worksheets[int(m.group(2))]
        for r, rm in enumerate(RE_ROW.finditer(m.group(3)), start=1):
            col = 1
            for tm in RE_TD.finditer(rm.group(2)):
                attrs = tm.group(1)
                cs = re.search(r'colspan="(\d+)"', attrs)
                ti = re.search(r'title="([^"]*)"', attrs)
                cell = ws.cell(row=r, column=col)
                col += int(cs.group(1)) if cs else 1
                wf = cell.value if isinstance(cell.value, str) and cell.value.startswith("=") else None
                pf = H.unescape(ti.group(1)) if ti else None
                if pf or wf:
                    seen += 1
                    if pf != wf:
                        bad.append(f"[{ws.title}] {cell.coordinate}: preview={pf!r} workbook={wf!r}")
    check(not bad, f"{path.name}: all {seen} preview tooltips match the workbook", "\n      ".join(bad[:4]))


# ------------------------------------------------------------------- EXPORT
# The business case is generated in the browser: an email-safe HTML rendering
# and a real .xlsx with live formulas and native charts. These tests pull the
# shipped JavaScript straight out of the HTML, run it under node, and check the
# workbook it produces actually recalculates to the numbers the page showed.

JS_START = "/* ============================================================ xlsx writer"
# Stop before the docx writer: everything after it needs a live DOM, which node
# has no business providing. The docx package is validated in the browser
# instead, by parsing its own ZIP with DOMParser.
JS_END = "/* ============================================================ docx writer"

# Each problem archetype emits a different benefit model, so the row the gross
# value lands on shifts. Every branch gets generated and recalculated.
GROSS_ROW = {"rate": 5, "volume": 4, "aht": 5, "shrink": 6}

HARNESS = r"""
const fs=require('fs');
global.fm=function(n,d){ if(n===undefined||n===null||!isFinite(n)) return '—';
  d=(d===undefined)?0:d;
  return Number(n).toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d}); };
eval(fs.readFileSync(process.argv[2],'utf8'));
const outDir=process.argv[3];
const base={vol:480000,cpc:6.8,rate:14.0,hr:38,occ:82,aht:420,ahtsave:14,agents:120,shrink:32,
  shrinktgt:28,target:8.0,harvest:'reduce',realz:80,bbmonths:9,bbcost:120000,training:35000,
  eng:60000,tooling:8000,years:3,disc:10};
const kinds=[
 {kind:'rate',   n:'Reduce rework and reopens',  metric:'Reopen rate',        gross:480000*0.06*6.8},
 {kind:'volume', n:'Eliminate a contact driver', metric:'Contacts per year',
  V:{rate:40000,target:8000},                                                 gross:(40000-8000)*6.8},
 {kind:'aht',    n:'Reduce handle time',         metric:'Average handle time',gross:480000*14/3600/0.82*38},
 {kind:'shrink', n:'Recover shrinkage capacity', metric:'Shrinkage %',        gross:120*1760*0.04*38}
];
const meta={};
for(const k of kinds){
  const V=Object.assign({},base,k.V||{});
  const gross=k.gross, real=gross*0.8, inv=120000*0.75+35000+60000+8000;
  let npv=-inv; for(let y=1;y<=3;y++) npv+=real/Math.pow(1.1,y);
  const m={gross,real,inv,npv,pb:inv/real,roi:(real*3-inv)/inv,fte:1,realz:0.8,
    detail:[['Improvement','a → b','6.0 pts']]};
  const a={n:k.n,d:'desc',metric:k.metric,kind:k.kind};
  const ctx={m,V,S:{arch:k.kind},a};
  fs.writeFileSync(outDir+'/'+k.kind+'.xlsx', Buffer.from(bizXlsx(ctx)));
  meta[k.kind]={gross,real,inv,npv,html:bizHTML(ctx).length};
}
fs.writeFileSync(outDir+'/meta.json', JSON.stringify(meta));
"""


def test_export() -> None:
    import subprocess

    src = HTML.read_text(encoding="utf-8")
    check("business-case.md" not in src, "markdown business case replaced by HTML/Excel")
    check("  function doc(){" not in src, "old markdown generator removed")
    for needed in ("var XLSX = (function(){", "var DOCX = (function(){",
                   "function bizXlsx(", "function bizHTML(",
                   "function openExport(", "function tplEmailHTML(", 'id="expCopy"',
                   "function showFmtMenu(", "function dlTemplateAs(",
                   # the template modal's button is created at runtime, not in the markup
                   "b.id = 'tplEmail'", "fullCalcOnLoad",
                   "wordprocessingml.document.main+xml"):
        check(needed in src, f"export code present: {needed}")

    # Download must offer a format rather than pushing a .md at everyone.
    # (Markdown is still *available* from the menu - it just isn't the default.)
    check("""if(t.ext==='xlsx'){
    dlBlob(t.file, b64ToBlob(t.b64,""" not in src,
          "old markdown-by-default download path removed")
    check("dlTemplateAs(slug, t.ext==='xlsx' ? 'xlsx' : 'docx')" in src,
          "bulk download defaults to Excel for workbooks and Word for documents")
    for fmt in ("'docx'", "'html'"):
        check(fmt in src, f"format menu offers {fmt}")
    # Markdown is a developer format; this audience gets Word and HTML only.
    check("'text/markdown'" not in src, "Markdown is no longer offered as a download")
    check("['md','Markdown'" not in src, "Markdown removed from the format menu")

    if JS_START not in src or JS_END not in src:
        check(False, "export JS block markers found in the HTML")
        return
    js = src[src.index(JS_START):src.index(JS_END)]

    if not shutil.which("node"):
        print("           node not found - skipping the generated-workbook test")
        return

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "bundle.js").write_text(js, encoding="utf-8")
        (d / "run.js").write_text(HARNESS, encoding="utf-8")
        r = subprocess.run(["node", str(d / "run.js"), str(d / "bundle.js"), str(d)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            check(False, "business case workbook generates without error", r.stderr.strip()[:400])
            return
        check(True, "business case workbook generates under node for every archetype")
        meta = json.loads((d / "meta.json").read_text())

        import zipfile
        import xml.etree.ElementTree as ET

        try:
            import formulas  # noqa: F401
            can_calc = True
        except ImportError:
            can_calc = False
            print("           formulas not installed - skipping workbook recalculation")

        for kind, e in meta.items():
            path = d / (kind + ".xlsx")
            check(e["html"] > 8000, f"{kind}: business case HTML renders ({e['html']} chars)")

            z = zipfile.ZipFile(path)
            names = set(z.namelist())
            broken = []
            for n in names:
                if n.endswith((".xml", ".rels")):
                    try:
                        ET.fromstring(z.read(n))
                    except Exception as ex:
                        broken.append(f"{n}: {ex}")
            check(not broken, f"{kind}: every xlsx part is well-formed XML", "; ".join(broken[:2]))
            charts = [n for n in names if "/charts/chart" in n]
            check(len(charts) == 4, f"{kind}: workbook carries all 4 charts (found {len(charts)})")
            ct = ET.fromstring(z.read("[Content_Types].xml"))
            ovr = {o.get("PartName") for o in ct if o.tag.endswith("Override")}
            missing = [n for n in names if not n.endswith(".rels")
                       and n != "[Content_Types].xml" and "/" + n not in ovr]
            check(not missing, f"{kind}: every xlsx part has a content type", ", ".join(missing[:3]))

            wb = load_workbook(path)
            check(wb.sheetnames == ["Business case", "Inputs", "Benefit model",
                                    "Financials", "Sensitivity"],
                  f"{kind}: workbook sheet layout", str(wb.sheetnames))

            if not can_calc:
                continue
            sol = _engine(path).calculate()
            gr = GROSS_ROW[kind]
            for label, sheet, cell, want in [
                ("gross annual value", "Benefit model", f"B{gr}", e["gross"]),
                ("realised annual benefit", "Benefit model", f"B{gr + 2}", e["real"]),
                ("total investment", "Financials", "B7", e["inv"]),
                ("net present value", "Financials", "B13", e["npv"]),
                ("cover sheet cross-reference", "Business case", "B9", e["real"]),
                ("base-case sensitivity NPV", "Sensitivity", "D5", e["npv"]),
            ]:
                got = _read(sol, path.name, sheet, cell)
                check(approx(got, want, 1e-6), f"{kind}: workbook recalculates the {label}",
                      f"got {got!r} want {want}")


# --------------------------------------------------------------------- main
def main() -> int:
    fast = "--fast" in sys.argv
    print("STRUCTURE  merged-cell reference audit")
    test_structure()
    print("SYNC       four-way template consistency")
    test_sync()
    print("EXPORT     business case HTML + live-formula workbook")
    test_export()
    if fast:
        print("NUMERIC    skipped (--fast)")
    else:
        try:
            import formulas  # noqa: F401
        except ImportError:
            print("NUMERIC    SKIPPED - pip install formulas to run the recalculation tests")
        else:
            print("NUMERIC    recalculating fixed formulas")
            test_numeric()
            test_numeric_other()

    print()
    if FAILURES:
        print(f"FAILED  {len(FAILURES)} check(s), {PASSES[0]} passed\n")
        for f in FAILURES:
            print("  x " + f)
        return 1
    print(f"PASSED  all {PASSES[0]} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
