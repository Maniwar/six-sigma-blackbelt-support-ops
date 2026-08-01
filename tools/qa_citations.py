#!/usr/bin/env python3
"""Resolve every `file.md:NN` the pack points at itself with.

The templates cite each other constantly, and they have to: a rate that cannot
be traced to the population it was measured on is the defect the whole pack
exists to remove. But they cite by LINE NUMBER, and a line number is not a
stable address. Editing any document shifts every pointer into it from every
sibling — one reconciliation pass added seventeen lines to the charter and
silently broke references in four other files — so the citations rot in exactly
the documents that are being maintained most carefully.

This makes the pointer a checkable claim instead of a convention.

The test is deliberately narrow, because "does line 120 support this sentence?"
is not decidable and a check that guesses is worse than none. What is decidable:

    if the citing sentence carries a FIGURE, the line it points at has to
    carry that figure too.

That is the failure mode observed every time. A citation offered as the
provenance of 14.2% pointed at a line of prose with no number on it at all.
Sentences citing a section rather than a figure are resolved for existence
only — the file has to exist and the line has to have something on it.

    python3 tools/qa_citations.py            # report
    python3 tools/qa_citations.py --quiet    # exit status only
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"

# A citation RUN, not a single reference. The pack points at several lines of
# one document at once, in two shapes, and both are load-bearing:
#
#     02-sipoc.md:48,49,51          three bullets, deliberately skipping :50
#     01-project-charter.md:52, and :213 in its revision history
#     06-data-lineage.md:31, :70
#
# Reading only the first reference of a run is what made this check's own first
# two findings. `,49,51` left behind by a half-done mask reads as the figure
# 4951, and a bare `, and :213` reads as 213 — so the check went hunting for a
# line number in the cited document and reported the citation broken. Both
# citations were correct. A checker that fails on its own parser is worse than
# no checker, so the run is matched as one unit and masked as one unit.
#
# The two continuation shapes are matched at different tightness on purpose. A
# bare number may continue a run only with no space (`,49`), because `, 966
# contacts` would otherwise be swallowed as a line number. A colon continuation
# is unambiguous, so it may carry spaces and an `and`.
RE_RUN = re.compile(
    r"\b([0-9A-Za-z][0-9A-Za-z._-]*\.(?:md|html|xlsx))"      # the document
    r"((?::\d+(?:[-–]\d+)?)"                                 # first line or range
    r"(?:,\d+(?:[-–]\d+)?|\s*,\s*(?:and\s+)?:\d+(?:[-–]\d+)?)*)"
)
RE_SPAN = re.compile(r"(\d+)(?:[-–](\d+))?")
# A figure a reader could look for: 14.2%, $38.60, 11,592, 966, 0.85
RE_FIG = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")

fails: list[str] = []
warns: list[str] = []
checked = [0]


def norm(tok: str) -> str:
    """Compare 14.2% with 14.2, and $11,592 with 11592."""
    return tok.lstrip("$").rstrip("%").replace(",", "")


def figures(text: str) -> set[str]:
    """Figures worth chasing. Bare 1-2 digit numbers are section and item
    numbers as often as they are data, and chasing them produces noise rather
    than findings."""
    out = set()
    for m in RE_FIG.finditer(text):
        n = norm(m.group(0))
        digits = n.replace(".", "")
        # Three digits, or money, or a percentage carrying a decimal. A bare
        # "2%" is a tolerance or a rounding, and chasing it finds nothing.
        if len(digits) >= 3 or "$" in m.group(0) or ("%" in m.group(0) and "." in n):
            out.add(n)
    return out


def sentence_around(line: str, at: int) -> str:
    """The clause the citation sits in — enough to see what it claims, without
    dragging in the figures of a neighbouring sentence."""
    lo = max((line.rfind(c, 0, at) for c in ".;—("), default=-1)
    hi = min((p for p in (line.find(c, at) for c in ".;—)") if p != -1), default=len(line))
    return line[lo + 1:hi]


def check_file(path: Path, cache: dict[str, list[str]]) -> None:
    lines = path.read_text(encoding="utf-8").split("\n")
    here = path.name
    for i, line in enumerate(lines, start=1):
        # Strip every citation out of the line first. A neighbouring
        # `charter.md:173` otherwise reads as the figure 173, and the check
        # then goes hunting for a line number in the cited document.
        # Blank the references BEFORE splitting into clauses, not after:
        # the dot in "01-project-charter.md:173" is a sentence boundary to
        # a naive splitter, which leaves a bare 173 behind and sends the
        # check hunting for a line number in the cited file.
        masked = RE_RUN.sub(lambda x: " " * len(x.group(0)), line)
        for m in RE_RUN.finditer(line):
            target = m.group(1)
            if not target.endswith(".md"):
                continue          # the page and the workbooks have no line map
            where = f"{here}:{i}"
            tp = TEMPLATES / target
            spans = [(int(s.group(1)), int(s.group(2) or s.group(1)))
                     for s in RE_SPAN.finditer(m.group(2))]
            checked[0] += len(spans)
            if not tp.exists():
                fails.append(f"{where} cites {target}, which does not exist")
                continue
            if target not in cache:
                cache[target] = tp.read_text(encoding="utf-8").split("\n")
            body = cache[target]
            # Every line of the run has to exist and say something. The FIGURE,
            # though, is checked against the run as a whole: "see :48, :49 and
            # :51" is one citation a reader follows collectively, and demanding
            # the number on all three would fail every list the pack writes.
            text, broke = [], False
            for lo, hi in spans:
                if hi > len(body):
                    fails.append(f"{where} cites {target}:{lo}"
                                 f"{'-' + str(hi) if hi != lo else ''} — that file ends "
                                 f"at line {len(body)}")
                    broke = True
                    continue
                if not "\n".join(body[lo - 1:hi]).strip():
                    fails.append(f"{where} cites {target}:{lo} — that line is blank")
                    broke = True
                    continue
                text.append("\n".join(body[lo - 1:hi]))
            if broke or not text:
                continue
            want = figures(sentence_around(masked, m.start()))
            if not want:
                continue                      # cites a section, not a figure
            got = {norm(x.group(0)) for x in RE_FIG.finditer("\n".join(text))}
            if want & got:
                continue
            # A cited row often carries the figure one line down when the table
            # wraps, so widen once before calling it wrong — and say that the
            # pointer is off by a line rather than that the claim is false.
            near = "\n".join("\n".join(body[max(0, lo - 3):min(len(body), hi + 2)])
                             for lo, hi in spans)
            nearby = {norm(x.group(0)) for x in RE_FIG.finditer(near)}
            hit = sorted(want & nearby)
            shown = m.group(0)
            if hit:
                warns.append(f"{where} cites {shown} for {hit[0]} — that line does "
                             f"not carry it, but a line within two of it does")
            else:
                fails.append(f"{where} cites {shown} for "
                             f"{', '.join(sorted(want)[:3])} — the line reads "
                             f"{text[0].strip()[:72]!r}")


def main() -> int:
    cache: dict[str, list[str]] = {}
    for p in sorted(TEMPLATES.glob("*.md")):
        check_file(p, cache)
    quiet = "--quiet" in sys.argv
    if not quiet:
        print(f"  {checked[0]} cross-references resolved across "
              f"{len(list(TEMPLATES.glob('*.md')))} documents")
        for w in warns:
            print(f"  warn {w}")
    if fails:
        print(f"\n{len(fails)} BROKEN CITATION(S):")
        print("\n".join(f"  FAIL {f}" for f in fails))
        return 1
    if not quiet:
        print(f"\nEvery citation resolves.{f' ({len(warns)} off by a line or two.)' if warns else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
