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
        "limits at 20.4%/8.0% against the 17.2%/11.2% it ships",
        "sigma z = 2.08, computed from the twelve weekly rates rather than read "
        "backwards off the limits it was supposed to justify",
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
    # The one this registry existed for and did not catch, because I corrected
    # the threshold in the curriculum and did not retire the old value. It
    # survived in two GENERATORS — worked_examples.py and md_guidance.py — and
    # so in the shipped hypothesis log, where the project's headline test read
    # "well past the 1.5 we agreed mattered" and booked itself Accepted while
    # the charter said the benefit misses the Finance floor. Found by an audit,
    # which is exactly what this file is meant to make unnecessary.
    Retired(
        "1.5 we agreed mattered",
        "the retired practical-significance threshold, which booked the project's "
        "headline test as passing while its charter said it misses the floor",
        "13.1 points — what 11,592 adjustments must move to clear the $50,000 floor",
    ),
    Retired(
        "threshold was 1.5 pts",
        "the same retired threshold, in the guidance generator that rewrites the "
        "evidence pack",
        "the threshold is 13.1 pts",
    ),
    Retired(
        "1.5 percentage points — below this",
        "the same retired threshold, in the generator that rewrites the charter",
        "13.1 percentage points on 11,592 in-scope adjustments",
    ),
    Retired(
        "test of baseline reopens against pilot reopens",
        "a before/after comparison, which the pilot protocol forbids and this pack "
        "teaches against: it is contaminated by seasonality and mix shift. The "
        "pre-registered test is treatment against concurrent control",
        "the two-proportion test of treatment against concurrent control",
    ),
    Retired(
        "the 960-minute wait survives the project",
        "960 minutes is the customer-confirmation wait at F17 of the value stream "
        "map; the wait in front of the vendor batch, which is what this risk is "
        "about, is the 720 at F15",
        "the 720-minute wait in front of the batch survives the project",
    ),
    Retired(
        "2026-09-25",
        "an Improve tollgate actual that cannot have happened: it leaves 84 days "
        "to the Control gate on a row claiming 90, and puts full rollout 53 days "
        "before the gate that selected the solution. It sat in the charter, in "
        "the SIPOC twice, and in the guidance generator that rewrites the charter",
        "2026-07-31 — the only Friday in the window the other dates force, and "
        "every other actual in that table is a Friday",
    ),
    # The X-Y matrix ranked eight causes against five CTQs that appear in no
    # CTQ tree, using weights no customer set — breaking the rule printed on
    # the workbook's own How-to sheet. Every number the sheet teaches with
    # moved when it was re-headed on the three the tree weights.
    Retired(
        "10, 7, 8, 5 and 9",
        "X-Y matrix weights invented in the room, against the sheet's own rule "
        "that weights come from the CTQ tree. The tree weights three rows, at "
        "10, 9 and 7, and explicitly declines to weight the one the fourth "
        "column paraphrased",
        "10, 9 and 7 (C11:E11), from 03-voc-ctq-tree.md section 5",
    ),
    Retired(
        "270 against 261",
        "the matrix's headline teaching pair, computed from the orphan columns",
        "two rows at 192, and two more at 148 — exact ties, not a photo finish",
    ),
    Retired(
        "rank 1 at 270 and rank 2 at 261",
        "the same pair in the Rank definition",
        "H15 and H22 both total 192; H17 and H19 both total 148",
    ),
    # Section 3 of the baseline was written without a series behind it, so its
    # figures could not all be true at once. The standard deviation was below
    # the floor its own maximum forces, and p95 sat below that maximum. The
    # twelve weekly rates are published now and everything is computed from
    # them, so each of the old assertions is retired by name.
    Retired(
        "*1.4 points*",
        "a baseline standard deviation no series can produce: one week at 18.9% "
        "against a mean of 14.2% puts the floor at 1.48 on its own. It was the "
        "least-protected figure in the pack — too few digits for the drift check "
        "to see and below the citation checker's threshold",
        "1.8 points, computed from the twelve weekly rates now published beside it",
    ),
    Retired(
        "3 × 1.4 points",
        "the same standard deviation inside the Ppu derivation",
        "3 × 1.8 points, giving Ppu -1.15",
    ),
    Retired(
        "12.3% / 14.0% / 16.2% / 16.9%",
        "baseline percentiles that put p95 at 16.9% below an 18.9% maximum, which "
        "no 12-point series can do under any percentile convention",
        "12.4% / 14.0% / 14.9% / 16.7%",
    ),
    Retired(
        "0.31 — mild right skew",
        "a skewness describing a series with no release week in it",
        "1.56",
    ),
    Retired(
        "1.98 — read off the limits",
        "a Laney sigma_z derived from the limits it was meant to justify, so it "
        "corroborated nothing",
        "2.08, the average moving range of the z-scores / 1.128",
    ),
    Retired(
        "17.1% / 11.3%",
        "Laney limits computed from that circular sigma_z. Not anchored on the\n        markdown cell's asterisks, which was the first attempt: the page states\n        the same limits in prose, and that rendering went unseen",
        "17.2% / 11.2%",
    ),
    Retired(
        "UCL 17.1%, LCL 11.3%",
        "the same limits in the walkthrough's prose rendering",
        "UCL 17.2%, LCL 11.2%",
    ),
    Retired(
        "Ppu −1.48",
        "a capability index computed on the unreachable 1.4-point standard deviation",
        "Ppu -1.15",
    ),
    # The curriculum's own walkthrough of the worked project contradicted the
    # baseline document it ships, on four counts at once, and no check covered
    # authored page prose. It is the same defect this file exists for, one level
    # up: the narrative and the artefact were corrected independently.
    Retired(
        "Laney p′ chart over 52 weeks showed a stable process",
        "the walkthrough described a 52-week stable baseline; the document it "
        "walks through is 12 weeks and section 2 answers 'Process stable? No'",
        "the twelve signed weeks, not stable, one release week above the UCL",
    ),
    Retired(
        "two known billing-system incident weeks (excluded and documented)",
        "the baseline excludes nothing: section 2 records one special cause and "
        "keeps it, because the release ships every six weeks and will recur",
        "one release week, kept in",
    ),
    # Live in tools/md_guidance.py until this change, and re-injected into any
    # emptied row. Retiring what the template showed but not what the generator
    # held is how the same wrong number comes back a release later.
    Retired(
        "Ppu 0.42",
        "a capability index for a process whose mean sits above its only limit, "
        "so the index has to be negative. Scoped: the calculators' SLA tab has a "
        "genuinely different worked example that also reads Ppu 0.42",
        "Ppu -1.15",
        allowed_in=("CHANGELOG.md", "tools/retired.py", "docs-review.md",
                    "tools/verify.py", "19-black-belt-calculators.xlsx"),
    ),
    Retired(
        "58% of weeks above the 8.0% target",
        "every one of the twelve weeks is above the target; 58% was derivable "
        "from no series in the document",
        "100% - all 12 weeks sit above the 8.0% target",
    ),
    Retired(
        "Approximately symmetric at weekly aggregation",
        "a series with one week four points clear of the other eleven is not "
        "approximately symmetric, and its skewness is 1.56",
        "Not symmetric: eleven weeks between 12.2% and 14.9% and one at 18.9%",
    ),
    Retired(
        "Anderson-Darling p = 0.03, which at 12 weekly points is not a concern",
        "the departure from normality is the release week, which is the point of "
        "sections 2 and 4, not something to wave through on sample size",
        "A2 = 0.81 on the twelve published rates, p = 0.02, and the departure "
        "named as the release week",
    ),
    Retired(
        "9-point gap between rank 1 and rank 2",
        "the X-Y matrix's old 270-against-261 pair, quoted from the CTQ tree as "
        "the yardstick for how little separates the top of that ranking. "
        "Re-scoring on the three CTQs the tree actually weights replaced it with "
        "two exact ties, and this sentence was the copy the retirement missed - "
        "it names the gap in words rather than repeating either number, so "
        "nothing that matched on 270 or 261 could see it",
        "the first two rows tie outright at 192 and the next two at 148",
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
    # Added when the authored page prose was found to be covered by nothing.
    # Each pattern was run over the whole pack before being added here, and
    # every one of them fires on at least nine sentences that already agree --
    # a canonical matching one place enforces nothing, and one that matches a
    # look-alike is worse than none. The two the pack will not let you add:
    # "kappa 0.78", because 0.52 first-pass and 0.84 re-test are both real and
    # both correct; and any bare "14.2%", because the queue rate and the
    # in-scope adjustment rate agree to the decimal and are different
    # quantities -- which is the defect the whole pack is built around.
    Canonical(
        "the improvement target",
        r"(?:target|goal) of ([\d.]+)%",
        "8.0",
        "the number the project is judged against. Stated fifteen times across "
        "the page and the templates, and written both as 8% and 8.0%, which is "
        "why this registry compares numbers rather than strings",
    ),
    Canonical(
        "the baseline month's in-scope volume",
        r"([\d,]{3,}) (?:contacts|adjustments) in the baseline month",
        "966",
        "the denominator of the project's headline rate. Nine statements; the "
        "annualised 11,592 is a different figure with its own entry above",
    ),
    Canonical(
        "reopens in the baseline month",
        r"([\d,]{3,}) reopens in 966",
        "137",
        "the numerator of the same rate. Eleven statements, and the pair has to "
        "stay arithmetically consistent with 14.2%",
    ),
    Canonical(
        "the baseline-to-goal gap",
        r"([\d.]+)[- ]point(?:s)? gap",
        "6.2",
        "14.2% to 8.0% on the in-scope population. Ten statements. It caught a "
        "stale one on the way in: the CTQ tree still described the X-Y matrix's "
        "retired 270-against-261 pair as a 9-point gap",
    ),
]


def _same_number(got: str, want: str) -> bool:
    """Numeric equality, not string equality.

    The pack writes the same figure both ways -- "a target of 8%" and "8.0%",
    "266,000" and "266000" -- and comparing the strings made a canonical fire
    on eleven sentences that were all correct. A canonical that cannot survive
    its own pack's house style is a canonical nobody can add, which is how this
    registry ends up with four entries and the prose ends up unchecked.
    """
    a, b = got.replace(",", "").strip(), want.replace(",", "").strip()
    if a == b:
        return True
    try:
        return float(a) == float(b)
    except ValueError:
        return False


def scan(text: str, path: str) -> list[str]:
    """Every retired claim and canonical disagreement in one artefact."""
    out: list[str] = []
    for r in RETIRED:
        if any(path.endswith(a) for a in r.allowed_in):
            continue
        body = r"\s+".join(re.escape(w) for w in r.text.split())
        pat = r"\b" + body + r"\b" if r.word else body
        if re.search(pat, text):
            out.append(
                f"{path}: carries the retired claim {r.text!r} — {r.why}. "
                f"It was replaced by: {r.replaced_by}")
    for c in CANONICAL:
        if any(path.endswith(a) for a in c.allowed_in):
            continue
        for m in re.finditer(c.pattern, text, c.flags):
            got = m.group(1)
            if not _same_number(got, c.value):
                out.append(
                    f"{path}: states {c.name} as {got!r}, and the pack's single "
                    f"rendering is {c.value!r} — {c.why}")
    return out
