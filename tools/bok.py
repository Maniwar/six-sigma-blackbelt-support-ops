#!/usr/bin/env python3
"""The two certification bodies of knowledge this curriculum maps itself to.

Here as data because the page asserts coverage against them on every module,
and an assertion nobody can check is a claim, not a mapping. Before this
existed the page cited six ASQ sections that do not exist in either the 2015 or
the 2022 body of knowledge — I.C, I.D, I.E, III.E, VII.D, VIII.E — and several
that exist but say something else entirely: "IV.B (VOC)" when IV.B is the
business case and voice of the customer is IV.A, "V.E (MSA)" when V.E is
probability and MSA is V.C, "VI.D (correlation, linear/multiple regression)"
when VI.D is gap, root cause and waste analysis and regression is VI.A.

Sources, both linked from the page's own reference list:
  ASQ    2022 Certified Six Sigma Black Belt Body of Knowledge Map, Tables 2-3
         https://www.asq.org/cert/resource/pdf/certification/2022-SSBB-BoK-Map.pdf
  IASSC  Lean Six Sigma Black Belt Body of Knowledge
         https://iassc.org/body-of-knowledge/black-belt-body-of-knowledge/

The 2022 revision kept every section letter from 2015; it added I.B.3, IV.D.6-7
and V.E.3, split VI.C into VI.C.1-2, and removed VI.B.8-9. So a code that is
absent here was never valid under either edition.
"""
from __future__ import annotations

# ASQ CSSBB 2022. Section code -> title, verbatim.
ASQ: dict[str, str] = {
    "I": "Organization-wide Planning and Deployment",
    "I.A": "Organization-wide considerations",
    "I.B": "Leadership",
    "II": "Organizational Process Management and Measures",
    "II.A": "Impact on stakeholders",
    "II.B": "Benchmarking",
    "II.C": "Business measures",
    "III": "Team Management",
    "III.A": "Team formation",
    "III.B": "Team facilitation",
    "III.C": "Team dynamics",
    "III.D": "Team training",
    "IV": "Define",
    "IV.A": "Voice of the customer",
    "IV.B": "Business case and project charter",
    "IV.C": "Project management (PM) tools",
    "IV.D": "Analytical tools",
    "V": "Measure",
    "V.A": "Process characteristics",
    "V.B": "Data collection",
    "V.C": "Measurement systems",
    "V.D": "Basic statistics",
    "V.E": "Probability",
    "V.F": "Process capability",
    "VI": "Analyze",
    "VI.A": "Measuring and modeling relationships between variables",
    "VI.B": "Hypothesis testing",
    "VI.C": "Risk analysis and management",
    "VI.D": "Additional analysis methods",
    "VII": "Improve",
    "VII.A": "Design of experiments (DOE)",
    "VII.B": "Lean methods",
    "VII.C": "Implementation",
    "VIII": "Control",
    "VIII.A": "Statistical process control (SPC)",
    "VIII.B": "Other controls",
    "VIII.C": "Maintain controls",
    "VIII.D": "Sustain improvements",
    "IX": "Design for Six Sigma (DFSS) Framework and Methodologies",
    "IX.A": "Common DFSS methodologies",
    "IX.B": "Design for X (DFX)",
    "IX.C": "Robust designs",
}

# Sub-subsections, for the modules narrow enough to cite one.
ASQ_SUB: dict[str, str] = {
    "I.A.1": "Fundamentals of six sigma and lean methodologies",
    "I.A.2": "Six sigma, lean, and continuous improvement methodologies",
    "I.A.3": "Relationships among business systems and processes",
    "I.A.4": "Strategic planning and deployment for initiatives",
    "I.B.1": "Roles and responsibilities",
    "I.B.2": "Organizational barriers",
    "I.B.3": "Change management",
    "II.C.1": "Performance measures",
    "II.C.2": "Financial measures",
    "III.A.1": "Team types and constraints",
    "III.A.2": "Team roles and responsibilities",
    "III.A.3": "Team member selection criteria",
    "III.A.4": "Team success factors",
    "III.B.1": "Motivational techniques",
    "III.B.2": "Team stages of development",
    "III.B.3": "Team communication",
    "III.B.4": "Team leadership models",
    "III.C.1": "Group behaviors",
    "III.C.2": "Meeting management",
    "III.C.3": "Team decision-making methods",
    "III.D.1": "Needs assessment",
    "III.D.2": "Delivery",
    "III.D.3": "Evaluation",
    "IV.A.1": "Customer identification",
    "IV.A.2": "Customer data collection",
    "IV.A.3": "Customer requirements",
    "IV.B.1": "Business case",
    "IV.B.2": "Problem statement",
    "IV.B.3": "Project scope",
    "IV.B.4": "Goals and objectives",
    "IV.B.5": "Project performance measurements",
    "IV.B.6": "Project charter review",
    "IV.C.1": "Gantt charts",
    "IV.C.2": "Toll-gate reviews",
    "IV.C.3": "Work breakdown structure (WBS)",
    "IV.C.4": "RACI model",
    "IV.D.1": "Affinity diagrams",
    "IV.D.2": "Tree diagrams",
    "IV.D.3": "Matrix diagrams",
    "IV.D.4": "Prioritization matrices",
    "IV.D.5": "Activity network diagrams",
    "IV.D.6": "Process decision program chart (PDPC)",
    "IV.D.7": "Interrelationship digraph (ID)",
    "V.A.1": "Process flow metrics",
    "V.A.2": "Process analysis tools",
    "V.B.1": "Types of data",
    "V.B.2": "Measurement scales",
    "V.B.3": "Sampling",
    "V.B.4": "Data collection plans and methods",
    "V.C.1": "Measurement system analysis (MSA)",
    "V.C.2": "Measurement systems across the organization",
    "V.C.3": "Metrology",
    "V.D.1": "Basic statistical terms",
    "V.D.2": "Central limit theorem",
    "V.D.3": "Descriptive statistics",
    "V.D.4": "Graphical methods",
    "V.D.5": "Valid statistical conclusions",
    "V.E.1": "Basic concepts",
    "V.E.2": "Common distributions",
    "V.E.3": "Additional distributions",
    "V.F.1": "Process capability indices",
    "V.F.2": "Process performance indices",
    "V.F.3": "General process capability studies",
    "V.F.4": "Process capability for attributes data",
    "V.F.5": "Process capability for non-normal data",
    "V.F.6": "Process performance vs. specification",
    "V.F.7": "Short-term and long-term capability",
    "VI.A.1": "Correlation coefficient",
    "VI.A.2": "Linear regression",
    "VI.A.3": "Multivariate tools",
    "VI.B.1": "Terminology",
    "VI.B.2": "Statistical vs. practical significance",
    "VI.B.3": "Sample size",
    "VI.B.4": "Point and interval estimates",
    "VI.B.5": "Tests for means, variances, and proportions",
    "VI.B.6": "Analysis of variance (ANOVA)",
    "VI.B.7": "Goodness-of-fit (chi square) tests",
    "VI.C.1": "Types of risk",
    "VI.C.2": "Failure mode and effects analysis (FMEA)",
    "VI.D.1": "Gap analysis",
    "VI.D.2": "Root cause analysis",
    "VI.D.3": "Waste analysis",
    "VII.A.1": "Terminology",
    "VII.A.2": "Design principles",
    "VII.A.3": "Planning experiments",
    "VII.A.4": "One-factor experiments",
    "VII.A.5": "Two-level fractional factorial experiments",
    "VII.A.6": "Full factorial experiments",
    "VII.B.1": "Waste elimination",
    "VII.B.2": "Cycle-time reduction",
    "VII.B.3": "Kaizen",
    "VII.B.4": "Other improvement tools and techniques",
    "VIII.A.1": "Objectives",
    "VIII.A.2": "Selection of variables",
    "VIII.A.3": "Rational subgrouping",
    "VIII.A.4": "Control chart selection",
    "VIII.A.5": "Control chart analysis",
    "VIII.B.1": "Total productive maintenance (TPM)",
    "VIII.B.2": "Visual controls",
    "VIII.C.1": "Measurement system reanalysis",
    "VIII.C.2": "Control plan",
    "VIII.D.1": "Lessons learned",
    "VIII.D.2": "Documentation",
    "VIII.D.3": "Training for process owners and staff",
    "VIII.D.4": "Ongoing evaluation",
}

# IASSC Lean Six Sigma Black Belt.
IASSC: dict[str, str] = {
    "1.1": "The Basics of Six Sigma",
    "1.2": "The Fundamentals of Six Sigma",
    "1.3": "Selecting Lean Six Sigma Projects",
    "1.4": "The Lean Enterprise",
    "2.1": "Process Definition",
    "2.2": "Six Sigma Statistics",
    "2.3": "Measurement System Analysis",
    "2.4": "Process Capability",
    "3.1": "Patterns of Variation",
    "3.2": "Inferential Statistics",
    "3.3": "Hypothesis Testing",
    "3.4": "Hypothesis Testing with Normal Data",
    "3.5": "Hypothesis Testing with Non-Normal Data",
    "4.1": "Simple Linear Regression",
    "4.2": "Multiple Regression Analysis",
    "4.3": "Designed Experiments",
    "4.4": "Full Factorial Experiments",
    "4.5": "Fractional Factorial Experiments",
    "5.1": "Lean Controls",
    "5.2": "Statistical Process Control (SPC)",
    "5.3": "Six Sigma Control Plans",
}

ALL_ASQ = {**ASQ, **ASQ_SUB}

# What each module actually covers: module id -> (ASQ codes, IASSC codes).
#
# Codes only. The titles beside them on the page are rendered from the tables
# above, so a section cannot be cited under a name it does not have — which is
# how "IV.B (VOC)" and "V.E (MSA)" survived: the code and the label beside it
# were written by hand, separately, and nothing compared them.
#
# The three tollgate clinics carried no mapping at all, which is why the drift
# went unnoticed for so long: an extraction that walks module blocks looking for
# the next mapping line silently pairs each clinic's neighbour with the wrong
# module, and reading the page top to bottom the codes still look plausible.
MODULE_MAP: dict[str, tuple[list[str], list[str]]] = {
    "M01": (["I.A"], ["1.1", "1.4"]),
    "M02": (["IV.A", "IV.D"], ["1.1", "1.2"]),
    "M03": (["II.C", "IV.B"], ["1.3"]),
    "M04": (["V.A", "VI.D"], ["1.4", "2.1"]),
    "M05": (["II.C", "V.F"], ["1.2", "2.4"]),
    "M06": (["I.B", "II.A", "III.A", "III.B", "III.C"], ["1.3"]),
    "M07": (["IV.B", "IV.C.2", "IV.C.4"], ["1.2", "1.3"]),
    "M08": (["V.B", "VI.B.3"], ["2.2", "3.2"]),
    "M09": (["V.D"], ["2.2", "3.1"]),
    "M10": (["V.C"], ["2.3"]),
    "M11": (["V.C"], ["2.3"]),
    "M12": (["V.F"], ["2.4"]),
    "M13": (["IV.C.2", "V.B", "V.C", "V.F"], ["2.1", "2.3", "2.4"]),
    "M14": (["VI.A.3", "VI.C", "VI.D"], ["2.1", "3.1"]),
    "M15": (["V.D", "V.E", "VI.B"], ["3.1", "3.2"]),
    "M16": (["VI.B"], ["3.3"]),
    "M17": (["VI.B"], ["3.4", "3.5"]),
    "M18": (["VI.A"], ["4.1", "4.2"]),
    "M19": (["IV.C.2", "VI.B", "VI.D"], ["3.2", "3.3"]),
    "M20": (["VII.B", "VII.C"], ["1.4", "5.1"]),
    "M21": (["VII.A"], ["4.3", "4.4"]),
    "M22": (["VII.A.5"], ["4.5"]),
    "M23": (["I.B.3", "VII.C"], []),
    "M24": (["VIII.A"], ["5.2"]),
    "M25": (["VIII.B", "VIII.C", "VIII.D"], ["5.1", "5.3"]),
    "M26": (["IX.A", "IX.C"], []),
}


def coverage() -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Which modules cover each section: (asq_section -> mids, iassc -> mids).

    Rolled up to the section, because a module citing V.F.2 covers part of V.F
    and a reader asking "is process capability taught here?" wants that to count.
    """
    asq_cov: dict[str, list[str]] = {k: [] for k in ASQ if "." in k}
    iassc_cov: dict[str, list[str]] = {k: [] for k in IASSC}
    for mid, (asq, iassc) in MODULE_MAP.items():
        for code in asq:
            parts = code.split(".")
            sec = f"{parts[0]}.{parts[1]}" if len(parts) > 1 else code
            if sec in asq_cov and mid not in asq_cov[sec]:
                asq_cov[sec].append(mid)
        for code in iassc:
            if mid not in iassc_cov[code]:
                iassc_cov[code].append(mid)
    return asq_cov, iassc_cov


def render(mid: str) -> str | None:
    """The BOK mapping line for a module, built from the tables above.

    IASSC publishes no Design for Six Sigma or team-management content in its
    Black Belt body of knowledge, so a module can legitimately map to ASQ alone.
    Saying so is more use to a reader than a code that does not cover it.
    """
    entry = MODULE_MAP.get(mid)
    if entry is None:
        return None
    asq, iassc = entry
    left = "ASQ " + ", ".join(f"{c} {ALL_ASQ[c]}" for c in asq)
    if not iassc:
        return left + " · not covered by the IASSC Black Belt body of knowledge"
    return left + " · IASSC " + ", ".join(f"{c} {IASSC[c]}" for c in iassc)


def asq_title(code: str) -> str | None:
    return ALL_ASQ.get(code)


def iassc_title(code: str) -> str | None:
    return IASSC.get(code)
