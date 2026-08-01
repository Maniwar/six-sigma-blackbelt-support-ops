#!/usr/bin/env python3
"""Give the markdown templates the guidance the workbooks already have.

Every .xlsx template opens with a "How to use this" tab, a worked example row
and a note on each input saying where the number comes from. The eleven
markdown templates got none of that: they shipped as well-structured blank
forms, 460 empty fields between them, with nothing to tell a first-time user
what a good answer looks like.

This adds two things to each one, in the same style as the workbooks:

  * a HOW TO USE THIS block — what it is for, when in DMAIC, who signs it, and
    the one mistake it reliably prevents;
  * a worked example filling every field, from the same billing-dispute project
    that runs through the workbooks, so a reader following the pack sees one
    case carried end to end.

Example text is italic and prefixed, so it is obvious what to delete. Run:

    python3 tools/md_guidance.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"

MARK = "<!-- guidance -->"

# ---------------------------------------------------------------- how-to

HOWTO = {
    "01-project-charter": (
        "The contract between you, your Champion and Finance. Nothing else in the "
        "project is allowed to contradict it.",
        "Define, before any data collection. Re-signed at every tollgate where the "
        "scope or the benefit changes.",
        "Black Belt drafts · Champion, Process owner and Finance partner sign",
        "A charter with a benefit number and no named harvest mechanism. If nobody has "
        "committed to removing the headcount, renegotiating the contract or absorbing "
        "the growth, the saving is occupancy reduction — real for agents, invisible to "
        "the P&L, and it will not survive Finance validation at closure."),
    "02-sipoc": (
        "The boundary diagram. It settles what is in scope before anyone argues about it "
        "in week six.",
        "Define, in the first workshop, on a wall, with the process owner in the room.",
        "Black Belt facilitates · Process owner agrees the boundaries",
        "Writing the process you wish you had rather than the one that runs. Walk it "
        "before you draw it."),
    "03-voc-ctq-tree": (
        "Turns what customers say into something you can measure, without losing the "
        "meaning on the way.",
        "Define, after the SIPOC and before the baseline — you cannot measure a CTQ you "
        "have not defined.",
        "Black Belt · signed off with the process owner and whoever owns the survey",
        "Jumping from a verbatim straight to a metric. The middle column is the work: a "
        "need is not a driver and a driver is not a measure."),
    "04-operational-definition": (
        "One page per metric, precise enough that two analysts working independently get "
        "the same number.",
        "Measure, before the baseline. If this is not agreed, the baseline is an opinion.",
        "Black Belt writes · Process owner and the data owner both sign",
        "Definitions that agree in principle and differ in the SQL. The test at the "
        "bottom is not optional — two people, same window, same answer, or it is not "
        "operational."),
    "06-data-lineage": (
        "Traces every number back to the system that generated it, through every "
        "transformation on the way.",
        "Measure, alongside the operational definition.",
        "Black Belt · signed with the data engineer who owns the pipeline",
        "Trusting a dashboard. A dashboard is the end of a lineage, not the start of "
        "one — and the transformation that quietly excludes abandoned contacts is "
        "always three joins upstream of the tile you were looking at."),
    "07-msa-attribute-agreement": (
        "Proves your QA scoring, disposition coding or survey interpretation is a "
        "measurement system rather than a set of opinions.",
        "Measure, before you baseline anything that depends on a human judgement.",
        "Black Belt runs it · QA manager owns the remediation",
        "Reporting percent agreement instead of kappa. Two analysts who both pass 90% "
        "of calls agree 82% of the time by luck alone; kappa removes that and routinely "
        "lands at 0.35–0.60 where the organisation believed it was near 1.0."),
    "08-msa-gage-rr": (
        "The continuous-data equivalent: how much of the variation you are about to "
        "analyse is the measurement rather than the process.",
        "Measure, before capability or any hypothesis test on a continuous metric.",
        "Black Belt runs it · the system owner fixes what it finds",
        "Accepting a study whose parts do not span the real range. If every sampled "
        "contact is a routine one, %study variation flatters itself and the gage looks "
        "better than it is."),
    "09-baseline-document": (
        "The number the project is judged against, with the evidence that it is stable "
        "enough to be judged against.",
        "End of Measure. This is the tollgate.",
        "Black Belt · Champion and Finance both sign the baseline value",
        "Baselining an unstable process. If the control chart is signalling, the mean is "
        "not a number — it is an average of two different processes, and any improvement "
        "you claim against it is unfalsifiable."),
    "14-root-cause-evidence-pack": (
        "The evidence that a cause is real. One pack per accepted root cause.",
        "End of Analyze, at the tollgate, before a single solution is designed.",
        "Black Belt assembles · Process owner agrees each cause is plausible",
        "Accepting a cause on one key. A statistical result without a mechanism is a "
        "correlation, and a mechanism without a statistical result is a strongly held "
        "opinion. Both, every time, or it does not go in the pack."),
    "16-pilot-protocol": (
        "Registers what you will do, on whom, for how long, and what result would make "
        "you stop — before you start.",
        "Improve, before the pilot runs. Registering it afterwards is not a protocol.",
        "Black Belt writes · Champion approves the stopping rule",
        "Deciding the success criterion after seeing the data. Write the practical "
        "threshold and the kill criteria into this document first, and the pilot can "
        "only tell you one of two things."),
    "18-handover-and-benefit-validation": (
        "Closes the project: hands the control plan to the owner and gets the benefit "
        "signed by Finance.",
        "Control, after 90 days of control data — not at the end of the improvement.",
        "Process owner accepts the controls · Finance validates the benefit",
        "Handing over without a named owner for each control. A control plan with no "
        "owner is a document; the process reverts within two quarters and nobody is "
        "accountable for noticing."),
}

# ------------------------------------------------- worked example values
# One project runs through all of these: billing adjustments closing before the
# posting confirms, driving a 14.2% 7-day reopen rate against a target of 8%.

EXAMPLE = {
    "01-project-charter": {
        "Project ID": "BIL-2026-014", "Black Belt": "M. Berenji",
        "Champion": "R. Mehta, Support Director", "Process owner": "A. Okafor, Billing Ops",
        "Finance partner": "J. Lindqvist", "Master Black Belt": "S. Iyer",
        "Start date": "2026-04-06", "Target close date": "2026-10-30",
        "Charter version / date": "v1.0 / 2026-04-06",
    },
    "14-root-cause-evidence-pack": {
        "Test / model": "2-proportion test, deferred-close cohort vs control",
        "Sample size": "n = 7,420 and 7,180 billing tickets, 12 weeks",
        "Result (statistic, p-value)": "z = 5.13, p = 0.0001",
        "Effect size + 95% CI": "−4.9 percentage points (CI −6.1 to −3.7)",
        "Assumptions verified": "Independence checked; one ticket per customer per window",
        "Stratification applied": "Contact reason and agent tenure",
        "Confounders considered and ruled out": "Volume mix shift (chi-sq p = 0.41); no release in window",
        "Practical threshold met?": "Yes — threshold was 1.5 pts, observed 4.9",
        "Process observation": "2026-05-12 | M. Berenji | Watched 11 closures; 4 closed before the webhook returned",
        "Agent interviews (n=)": "2026-05-13 | M. Berenji | n=8; none could see posting status from the ticket",
        "Case review (n=)": "2026-05-14 | A. Okafor | n=50 reopens; 31 closed pre-posting",
        "System / config inspection": "2026-05-15 | P. Nwosu | Status model has no pending-adjustment state",
        "Baseline-to-goal gap": "14.2% → 8.0% = 6.2 points",
        "Estimated contribution of this cause": "4.9 points",
        "Basis for the estimate": "Measured effect from the deferred-close test",
        "% of gap explained": "79%",
    },
    "04-operational-definition": {
        "**Metric name**": "7-day reopen rate, billing adjustments",
        "**Plain-language description**": "Share of resolved billing tickets the customer reopens within 7 days",
        "**What is counted (numerator)**": "Tickets with a reopen event 0<t<=168h after first Resolved",
        "**Denominator / population**": "All billing tickets reaching Resolved in the window",
        "**Time window**": "Rolling 7 days from each ticket's first Resolved timestamp",
        "**Unit of analysis**": "Ticket (not contact, not customer)",
        "**Inclusions**": "All channels; all billing contact reasons; all tiers",
        "**Exclusions**": "Tickets merged into another; test/QA tickets; bot-only deflections",
        "**Stratification fields available**": "Contact reason, agent tenure band, site, channel",
        "**Source system(s)**": "Zendesk (tickets), billing platform (postings)",
        "**Source tables / fields**": "warehouse.tickets.resolved_at, warehouse.ticket_events.reopened_at",
        "**Business rules applied**": "First Resolved only; a second reopen does not double-count",
        "**Refresh cadence**": "Nightly, 02:00 UTC; restated for 3 days as late events land",
    },
    "06-data-lineage": {
        "Event capture": "Agent clicks Resolved | Zendesk UI | resolved_at written in browser local time",
        "Source table": "zendesk.tickets | replicated hourly | timezone converted to UTC here",
        "ETL output": "stg_tickets | dbt run 02:00 | merged tickets collapsed to the survivor",
        "Warehouse": "warehouse.tickets | 02:40 | test tickets filtered on requester domain",
        "Dashboard": "Ops weekly reopen tile | Looker | filters to billing reasons only",
        "Where it appears": "The tile excludes chat; the warehouse table does not",
        "Finding": "Two published reopen rates differ by 1.8 pts because of that filter",
    },
    "07-msa-attribute-agreement": {
        "Appraisers (n, names/IDs)": "4 — QA analysts QA-01 to QA-04",
        "Items sampled (n)": "50 recorded billing contacts",
        "Sample stratification": "Stratified by contact reason and by known pass/fail",
        "Replicates per appraiser": "2",
        "Separation between replicates": "At least 5 working days",
        "Order randomized?": "Yes — different random order per appraiser per replicate",
        "Appraisers blinded to prior score?": "Yes — prior scores hidden in the QA tool",
        "Standard established by": "QA manager plus process owner, by consensus, before the study",
        "Standard shown to appraisers?": "No",
    },
    "08-msa-gage-rr": {
        "Parts / items (n)": "10 contacts spanning the full handle-time range, 2 to 34 minutes",
        "Appraisers / observers (n)": "3 workforce analysts",
        "Replicates": "3",
        "Order randomized?": "Yes",
        "Appraisers blinded to prior measurement?": "Yes",
        "Total Gage R&R": "28.4% study variation — marginal, investigate before use",
        "— Repeatability (equipment)": "11.2%",
        "— Reproducibility (appraiser)": "26.1% — the analysts disagree more than the tool does",
        "Part-to-part": "95.9%",
    },
    "09-baseline-document": {
        "Metric": "7-day reopen rate, billing adjustments",
        "Operational definition ref": "OD-BIL-004 v2",
        "Period covered": "2026-01-05 to 2026-03-29 (12 whole weeks)",
        "Records (n)": "61,400 billing tickets",
        "Extract date": "2026-04-02",
        "Extract query / job ref": "warehouse job bl_reopen_baseline, commit 4f2a9c1",
        "Immutable snapshot stored at": "s3://analytics-snapshots/BIL-2026-014/baseline.parquet",
        "Chart type used": "Laney p-prime",
        "Chart type justification": "Proportion at ~5,100 tickets/week; sigma z = 4.25, so an ordinary p-chart would signal on almost every point",
        "Centre line": "14.2%",
    },
    "16-pilot-protocol": {
        "Solution(s)": "Block Resolved until the billing posting webhook confirms",
        "Root cause(s) addressed": "RC-1 closure permitted before posting confirms",
        "Countermeasure hierarchy level": "2 — Design it out",
        "Expected mechanism of effect": "The ticket cannot reach Resolved while an adjustment is in flight, so the customer has nothing to reopen for",
        "Treatment group definition": "Billing queue, sites A and C, all tenures",
        "**Concurrent control group definition**": "Billing queue, sites B and D, same period",
        "Randomization / assignment mechanism": "Site-level assignment, drawn before the baseline was read",
        "Matching factors": "Contact reason mix, tenure mix, weekly volume",
        "Start date": "2026-06-01",
        "End date": "2026-07-27 (8 whole weeks)",
    },
    "18-handover-and-benefit-validation": {
        "Full implementation date": "2026-08-03",
        "Control period start": "2026-08-04",
        "Control period end": "2026-11-02",
        "Days of control data": "91",
        "Post-period metric (centre line)": "7.6%",
        "Post-period UCL / LCL": "9.1% / 6.1%",
        "Process stable in the control period?": "Yes — no points outside the limits, no runs of 8",
        "Mix shift present?": "Checked: contact-reason mix chi-sq p = 0.38, no material shift",
        "Adjustment method applied": "None required",
    },
    "02-sipoc": {
        "Suppliers": "Customer; billing platform; Tier 1 support; adjustments desk",
        "**First step** (process starts when…)": "the customer submits a billing dispute",
        "**Last step** (process ends when…)": "the adjustment has posted and the customer has confirmed",
    },
    "03-voc-ctq-tree": {
        "Survey verbatims": "CSAT free text, billing reasons | 12 weeks | n=2,180 | Only 14% respond — survivorship",
        "Contact transcripts": "Chat and email, billing queue | 4 weeks | n=8,400 | Topic-modelled, then read 200 by hand",
        "Customer interviews": "Disputed-charge customers | 6 sessions | n=6 | Recruited from reopens, so biased to failure",
        "Complaint / escalation review": "Formal complaints, billing | 12 weeks | n=61 | Small n, high signal",
        "Churn exit reasons": "Cancellation survey | 12 weeks | n=340 | Free text, self-reported",
        "Internal (VOB / VOE)": "Agent forum and QA notes | ongoing | n/a | Agents name the same posting delay",
    },
}

FIELD_HINT = {
    "01-project-charter": {},
}


def block(name: str) -> str:
    purpose, when, who, trap = HOWTO[name]
    return (
        f"{MARK}\n"
        "## How to use this\n\n"
        f"**What it is for.** {purpose}\n\n"
        f"**When.** {when}\n\n"
        f"**Who signs it.** {who}\n\n"
        f"**The mistake this prevents.** {trap}\n\n"
        "*Italic entries below are a worked example from one project — billing "
        "adjustments closing before the posting confirms, driving a 14.2% 7-day reopen "
        "rate against a target of 8%. Delete them as you fill your own in.*\n\n"
        "---\n"
    )


def fill_row(line: str, values: dict) -> str:
    """Put the worked example into a two-column table row that is currently blank."""
    cells = line.split("|")
    if len(cells) < 3:
        return line
    label = cells[1].strip()
    if not label or label.startswith("-") or label.lower() == "field":
        return line
    body = [c.strip() for c in cells[2:-1]]
    if any(body):                      # already filled in
        return line
    val = values.get(label)
    if not val:
        return line
    parts = [p.strip() for p in val.split("|")]
    while len(parts) < len(body):
        parts.append("")
    filled = " | ".join(f"*{p}*" if p else "" for p in parts[:len(body)])
    return f"| {cells[1].strip()} | {filled} |"


def main() -> int:
    changed = 0
    for name, _ in HOWTO.items():
        path = TEMPLATES / f"{name}.md"
        if not path.exists():
            print(f"  missing: {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        if MARK in text:                              # rewrite, do not stack
            text = re.sub(re.escape(MARK) + r".*?\n---\n", "", text, count=1, flags=re.S)
        lines = text.split("\n")
        # the block goes after the H1 title
        for i, line in enumerate(lines):
            if line.startswith("# "):
                lines.insert(i + 1, "\n" + block(name))
                break
        values = EXAMPLE.get(name, {})
        if values:
            lines = [fill_row(ln, values) if ln.startswith("|") else ln for ln in lines]
        out = "\n".join(lines)
        if out != path.read_text(encoding="utf-8"):
            path.write_text(out, encoding="utf-8")
            changed += 1
        print(f"  {path.name:40s} guidance added"
              f"{', worked example filled' if values else ''}")
    print(f"\n  {changed} template(s) rewritten")
    return 0


if __name__ == "__main__":
    sys.exit(main())
