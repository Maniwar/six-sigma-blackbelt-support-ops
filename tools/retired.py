#!/usr/bin/env python3
"""Claims this pack has retired, and the facts it allows only one rendering of.

WHY THIS EXISTS

Nearly every defect found in this pack has had the same shape: one rule, stated
in several places, corrected in some of them. The kappa acceptance bands were
wrong in seven places. The benefit chain was wrong in three, and I fixed it
twice before finding the third. A sampling bias was stated backwards in four,
and I fixed two of them and reported it closed. The rolled-yield chain was in
five. Each time the fix was real and the claim of completeness was not.

The checks written in response were all per-rule and all written afterwards:
one for the kappa bands, one for the benefit calculators, one for the AHT
chain. Each catches its own defect and nothing else, and none of them existed
until the defect had already shipped.

This file is the general form. Two registries:

RETIRED — an exact string that was once in the pack and is now wrong. Nothing
    in any artefact may contain it. This makes every past correction permanent:
    a copy that was missed, or one reintroduced later by a generator, fails
    immediately and by name rather than waiting for the next audit.

CANONICAL — a fact the pack states in more than one place, with the single
    rendering it is allowed. Every occurrence of the label must carry that
    value. This catches the NEXT one: a new copy of a known fact is checked the
    moment it appears, without anyone remembering to add a check for it.

ADDING TO THIS FILE IS PART OF FIXING A DEFECT, not an optional extra. If a
correction changes a figure or a phrase that appears anywhere else, the old
form belongs in RETIRED and the new one in CANONICAL. That is the whole
mechanism: it converts "I fixed it everywhere" from a claim into a check.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Retired:
    """A string that must not appear anywhere in the pack."""

    text: str
    why: str
    replaced_by: str
    # Files allowed to keep it — the changelog and this file discuss it by
    # necessity, and docs-review.md is a historical record of the defect.
    allowed_in: tuple[str, ...] = ("CHANGELOG.md", "tools/retired.py", "docs-review.md")
    # Match as a whole word/number rather than a substring where that matters.
    word: bool = False


@dataclass(frozen=True)
class Canonical:
    """A fact stated in several places, and the one rendering it may have."""

    name: str
    # Regex identifying a statement of this fact. Group 1 is the value.
    pattern: str
    value: str
    why: str
    allowed_in: tuple[str, ...] = ("CHANGELOG.md", "tools/retired.py", "docs-review.md")
    flags: int = field(default=re.IGNORECASE)


# --------------------------------------------------------------------------
# Retired claims, oldest first. Each one shipped, in more than one place.
# --------------------------------------------------------------------------
RETIRED: list[Retired] = [
    Retired(
        "480,000",
        "the whole billing queue used as the volume for a rate measured on the "
        "11,592 in-scope adjustments — the population mismatch the charter records",
        "266,000 for the queue, 11,592 for the in-scope population",
        word=True,
    ),
    Retired(
        "0.75 – 0.90",
        "the AIAG-style kappa band, which passes a QA rubric this programme halts",
        ">0.80 good, 0.60-0.80 marginal, <0.60 unacceptable",
    ),
    Retired(
        "0.40 – 0.75",
        "the AIAG-style kappa band",
        "0.60-0.80 marginal",
    ),
    Retired(
        "0.4–0.75",
        "the AIAG-style kappa band, compact rendering",
        "0.6-0.8 marginal",
    ),
    Retired(
        "0.75–0.90",
        "the AIAG-style kappa band, compact rendering",
        "0.8-0.9 good",
    ),
    Retired(
        "k>0.75",
        "the on-page kappa calculator's retired threshold",
        "k>0.8",
    ),
    Retired(
        "B13>0.75",
        "the calculator workbook's retired kappa threshold",
        "B13>0.8",
    ),
    Retired(
        "flatters the gage",
        "narrow part sampling condemns a sound gage; it does not flatter one. "
        "This sentence was in the markdown, the workbook cell and the cell "
        "comment, and the generator that writes two of them",
        "collapses part-to-part variation, which inflates %study variation",
    ),
    Retired(
        "sigma z = 4.25",
        "a factor corroborated by nothing, which puts the baseline's control "
        "limits at 20.4%/8.0% against the 17.1%/11.3% it ships",
        "sigma z = 1.98",
    ),
    Retired(
        "0.78 × 0.94 × 0.88 × 0.96",
        "a rolled-yield chain multiplying a Tier 2 figure measured on escalated "
        "tickets only into a product covering all contacts",
        "0.78 x 0.94 x 0.97 x 0.96 = 68.3%",
    ),
    Retired(
        "an RTY of 61.9%",
        "the rolled throughput yield from the mismatched-population chain. "
        "Scoped to the claim: 61.9% also occurs as a computed cell value inside "
        "an embedded workbook preview, where it means something else entirely",
        "68.3%",
    ),
    Retired(
        "0.96 give 61.9%",
        "the same chain, stated in the glossary's compact form",
        "0.96 give 68.3%",
    ),
    Retired(
        "Paid hours  =  hours saved ÷ occupancy",
        "occupancy converts handle time into AVAILABLE hours; paid time carries "
        "shrinkage on top, and stopping here understates the benefit by 47%",
        "On-phone hours = hours saved / occupancy, then paid hours = on-phone / (1 - shrinkage)",
    ),
    Retired(
        "frees more than an hour of paid time",
        "the same stop-at-occupancy error, stated in prose in the card's own help",
        "frees more than an hour of the time agents are logged in and available",
    ),
    Retired(
        "2026-01-01 to 2026-03-31",
        "the baseline window read as a calendar quarter; the 61,400 records were "
        "taken over twelve whole weeks and annualise differently",
        "2026-01-05 to 2026-03-29",
    ),
    Retired(
        "type the 90 readings into the yellow grid",
        "the yellow cells are the five study-design fields; the readings go in "
        "the green block, and following this overwrites the design",
        "type the 90 readings over the green grid at B13:J22",
    ),
    Retired(
        "including Fleiss' kappa for more than two appraisers",
        "the pack computes Cohen's kappa from two appraisers and cannot compute "
        "Fleiss at all",
        "a statement that the pack does not compute it, and the pairwise route",
    ),
]


# --------------------------------------------------------------------------
# Facts allowed exactly one rendering, wherever they are stated.
# --------------------------------------------------------------------------
CANONICAL: list[Canonical] = [
    Canonical(
        "the billing queue's annual volume",
        r"([\d,]{6,})\s+(?:billing tickets a year|contacts a year)",
        "266,000",
        "the queue the worked project runs on",
    ),
    Canonical(
        "the in-scope population",
        r"([\d,]{5,})\s+in-scope (?:billing )?adjustments\s+a year",
        "11,592",
        "the population the 14.2% and 8.0% rates are measured on. Only the ANNUAL "
        "figure: the pack also states this population per month (966), per arm "
        "(5,300) and per arm per week (112), and those are different quantities",
    ),
    Canonical(
        "the cost of an avoided reopen",
        r"\$([\d.]+)\s+(?:a|per) reopen",
        "38.60",
        "a reopen carries the investigation and the redo; cost-to-serve is the "
        "price of a first contact and pricing rework at it is a recorded defect",
    ),
    Canonical(
        "the Finance floor",
        r"\$([\d,]+)\s+(?:realized |realised )?(?:Finance )?floor",
        "50,000",
        "the bar the worked project fails, which is the lesson",
    ),
]


def scan(text: str, path: str) -> list[str]:
    """Every retired claim and canonical disagreement in one artefact."""
    out: list[str] = []
    for r in RETIRED:
        if any(path.endswith(a) for a in r.allowed_in):
            continue
        pat = r"\b" + re.escape(r.text) + r"\b" if r.word else re.escape(r.text)
        if re.search(pat, text):
            out.append(
                f"{path}: carries the retired claim {r.text!r} — {r.why}. "
                f"It was replaced by: {r.replaced_by}")
    for c in CANONICAL:
        if any(path.endswith(a) for a in c.allowed_in):
            continue
        for m in re.finditer(c.pattern, text, c.flags):
            got = m.group(1)
            if got.replace(",", "") != c.value.replace(",", ""):
                out.append(
                    f"{path}: states {c.name} as {got!r}, and the pack's single "
                    f"rendering is {c.value!r} — {c.why}")
    return out
