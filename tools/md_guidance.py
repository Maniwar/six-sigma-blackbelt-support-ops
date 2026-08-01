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
        'Baseline volume (annual)': '61,400 billing tickets',
        'Baseline metric': '14.2% reopened within 7 days',
        'Target metric': '8.0%',
        'Units avoided / improved': '3,807 reopens avoided a year',
        'Unit cost basis ($)': '$6.80 fully-loaded cost per contact',
        '**Gross annual benefit**': '$25,888',
        'Realization factor': '0.85 — agreed with Finance, reflects partial harvest in year one',
        '**Realized annual benefit**': '$22,005',
        'First process step': 'Customer submits a billing dispute',
        'Last process step': 'Adjustment has posted and the customer has confirmed',
        'In scope': 'Billing adjustments, all channels, all sites',
        'Out of scope': 'Fraud holds, collections, and anything requiring a manual refund cheque',
        'Channels included': 'Voice, chat, email',
        'Sites / vendors included': 'Sites A-D; no outsourced volume in scope',
        'Customer segments included': 'All consumer accounts; enterprise excluded (different billing stack)',
        'Primary': '7-day reopen rate, billing | 14.2% | 8.0% | OD-BIL-004 v2',
        'Secondary': 'Median resolution time, billing | 4.6 h | 4.0 h | OD-BIL-007 v1',
        'Counter-balancing': 'CSAT, billing contacts | 4.11 | no decline | OD-CX-002 v3',
        'Define': '2026-04-06 | 2026-04-24 | Charter signed, SIPOC agreed',
        'Measure': '2026-04-27 | 2026-06-05 | MSA passed, baseline signed',
        'Analyze': '2026-06-08 | 2026-07-24 | Root causes evidenced on two keys',
        'Improve': '2026-07-27 | 2026-09-25 | Pilot read, solution selected',
        'Control': '2026-09-28 | 2026-12-18 | 90 days of control data, benefit validated',
        'Champion': 'R. Mehta | | 2026-04-06',
        'Black Belt': 'M. Berenji | | 2026-04-06',
        'Finance partner': 'J. Lindqvist | | 2026-04-06',
        'Master Black Belt': 'S. Iyer | | 2026-04-06',
        "Project ID": "BIL-2026-014", "Black Belt": "M. Berenji",
        "Champion": "R. Mehta, Support Director", "Process owner": "A. Okafor, Billing Ops",
        "Finance partner": "J. Lindqvist", "Master Black Belt": "S. Iyer",
        "Start date": "2026-04-06", "Target close date": "2026-10-30",
        "Charter version / date": "v1.0 / 2026-04-06",
    },
    "14-root-cause-evidence-pack": {
        '1': 'Closure permitted before the posting confirms | Statistical + mechanism | 4.9 pts | 79% | Accepted',
        '2': 'Agent cannot see posting status from the ticket | Statistical + mechanism | 1.1 pts | 18% | Accepted',
        '3': 'Reopen metric counts same-reason only | Mechanism only | — | — | Rejected — no statistical key',
        '4': 'New-hire tenure under 90 days | Statistical only | 0.4 pts | 6% | Held — no mechanism described yet',
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
        '**Owner**': 'A. Okafor, Billing Ops Manager — owns the definition, not just the number',
        '**Known limitations**': 'Excludes chat until the channel field is backfilled; understates by roughly 0.4 points',
        '**Related metrics it must reconcile with**': 'Contact rate (same denominator) and the Ops weekly reopen tile (currently 1.8 pts apart — see the lineage doc)',
        'Disagreements and resolution': 'Reporting counted same-reason reopens only; operations wanted any-reason. Resolved 2026-04-24 in favour of any-reason, and the baseline was recut.',
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
        '1': 'Event capture | Zendesk UI | Agent clicks Resolved | resolved_at is browser local time | Support Ops | Real time | Timezone is converted two stages later, not here',
        '2': 'Replication | zendesk.tickets | Hourly copy, no transformation | None | Data Eng | Hourly | Late events can arrive after the nightly build reads it',
        '3': "Staging | stg_tickets (dbt) | Merged tickets collapsed to the survivor | A merged ticket keeps the survivor's timestamps | Data Eng | 02:00 | The merged-away ticket's reopen is lost",
        '4': 'Warehouse | warehouse.tickets | Test tickets filtered on requester domain | Internal domains excluded | Data Eng | 02:40 | Contractor domains are not on the exclusion list',
        '5': 'Metric build | warehouse.reopen_daily | Reopen flagged where reopened_at - resolved_at <= 168h | First Resolved only | Analytics | 03:10 | A second reopen is not counted twice, by design',
        '6': 'Dashboard | Looker: Ops weekly reopen | Filters to billing contact reasons | Chat excluded by a legacy filter | Ops Insights | 06:00 | This is why the tile and the warehouse disagree by 1.8 points',
        'Event capture': '14.2% | — | Baseline, taken from the warehouse',
        "Event capture": "Agent clicks Resolved | Zendesk UI | resolved_at written in browser local time",
        "Source table": "zendesk.tickets | replicated hourly | timezone converted to UTC here",
        "ETL output": "stg_tickets | dbt run 02:00 | merged tickets collapsed to the survivor",
        "Warehouse": "warehouse.tickets | 02:40 | test tickets filtered on requester domain",
        "Dashboard": "Ops weekly reopen tile | Looker | filters to billing reasons only",
        "Where it appears": "The tile excludes chat; the warehouse table does not",
        "Finding": "Two published reopen rates differ by 1.8 pts because of that filter",
    },
    "07-msa-attribute-agreement": {
        'Within-appraiser agreement (repeatability)': '78% | >= 90% | Fail — QA-03 at 62%',
        'Between-appraiser agreement (reproducibility)': '64% | >= 90% | Fail',
        'Agreement with the standard (accuracy)': '71% | >= 90% | Fail',
        "Fleiss' / Cohen's kappa": '0.41 | >= 0.80 | Fail — moderate at best',
        'Rubric items rewritten': 'Items 4 and 7 | QA manager | 2026-05-22',
        'Decision rules added': 'Written rule for partial credit on empathy | QA manager | 2026-05-22',
        'Examples library built': 'Six scored calls per rubric item | QA leads | 2026-06-05',
        'Categories merged / removed': "Merged 'tone' into 'empathy' — never scored apart | QA manager | 2026-05-29",
        'Calibration cadence set': 'Fortnightly, 45 minutes, all analysts | QA manager | 2026-06-01',
        'Calibration session': '2026-06-12 | Complete',
        'Blind re-score audit': '2026-06-26 | Complete',
        'Kappa re-measurement': '2026-07-10 | kappa 0.84 — passed',
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
        'Total Gage R&R': '28.4 | 8.1 | Marginal — usable for ranking, not for judging an individual agent',
        '— Repeatability (equipment)': '11.2 | 3.2 | Acceptable',
        '— Reproducibility (appraiser)': '26.1 | 7.4 | The analysts disagree more than the tool does',
        'Part-to-part': '95.9 | 27.3 | Good spread across the sampled range',
        'Total Gage R&R': '28.4 | 8.1 | Marginal — investigate before relying on it',
        '— Repeatability (equipment)': '11.2 | 3.2 | Acceptable',
        '— Reproducibility (appraiser)': '26.1 | 7.4 | The analysts disagree more than the tool does',
        'Part-to-part': '95.9 | 27.3 | Good spread across the sampled range',
        '**Total variation**': '100.0 | 28.5 | —',
        '% Study variation': '28.4% | Marginal: under 10% good, 10-30% conditional, over 30% unusable',
        'Number of distinct categories (ndc)': '4 | 5 or more is wanted; 4 means it can just about tell four groups apart',
        'Bias': '+0.8 min | Two analysts consistently round after-call work up | Retrain on the ACW definition',
        'Linearity': 'No trend across the range | — | None needed',
        'Stability': 'Re-measured after 4 weeks, no drift | — | Re-check at 6 months',
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
        'Normality assessment (probability plot, not just the p-value)': 'Probability plot near-linear; Anderson-Darling p = 0.03, which at 12 weekly points is not a concern',
        'Bimodality present? If so, resolved by stratifying on': 'No. Checked by stratifying on site and on tenure band — one distribution in both',
        'Rolled throughput yield across tiers': '55.6% — first-pass yield compounds badly across four steps',
        'Black Belt': 'M. Berenji | | 2026-06-05',
        'Process owner': 'A. Okafor | | 2026-06-05',
        '**Finance partner**': 'J. Lindqvist | | 2026-06-08',
        'Master Black Belt': 'S. Iyer | | 2026-06-08',
        'DPU / DPO / DPMO': '0.142 / 0.0284 / 28,400',
        'Opportunities per unit (program standard)': '5 — fixed at programme level, never renegotiated mid-project',
        'Z from data (long-term)': '1.90',
        'Sigma level (with 1.5\u03c3 shift)': '3.40',
        'UCL / LCL': '17.1% / 11.3%',
        'Special causes found': 'One week (w/c 2026-02-16) above the UCL — a billing platform release',
        'Special causes excluded (and why)': 'None excluded. The release is a real process condition and will recur.',
        'n': '61,400 tickets',
        'Mean': '14.2%',
        '**Median**': '14.0%',
        'Standard deviation': '1.4 points',
        'p10 / p50 / p90 / p95': '12.3% / 14.0% / 16.2% / 16.9%',
        'Skewness': '0.31 — mild right skew, as expected for a proportion near the middle',
        'Distribution shape': 'Approximately symmetric at weekly aggregation; the underlying durations are not',
        'Normality assessment (probability plot, not just a p-value)': 'Probability plot near-linear; Anderson-Darling p = 0.03, which at n = 12 weeks is not a concern',
        'Bimodality present? If so, resolved by stratification?': 'No',
        'Index justification': 'Ppu — only an upper limit exists (target is a maximum)',
        '**Capability index value**': 'Ppu 0.42',
        '% outside specification (observed)': '58% of weeks above the 8.0% target',
        '% outside specification (fitted)': '61%',
        "Metric": "7-day reopen rate, billing adjustments",
        "Operational definition ref": "OD-BIL-004 v2",
        "Period covered": "2026-01-05 to 2026-03-29 (12 whole weeks)",
        "Records (n)": "61,400 billing tickets over the 12-week window",
        "Extract date": "2026-04-02",
        "Extract query / job ref": "warehouse job bl_reopen_baseline, commit 4f2a9c1",
        "Immutable snapshot stored at": "s3://analytics-snapshots/BIL-2026-014/baseline.parquet",
        "Chart type used": "Laney p-prime",
        "Chart type justification": "Proportion at ~5,100 tickets/week; sigma z = 4.25, so an ordinary p-chart would signal on almost every point",
        "Centre line": "14.2%",
    },
    "16-pilot-protocol": {
        '**Primary metric**': '7-day reopen rate, billing adjustments',
        '**Statistical test**': 'Two-proportion test, treatment vs concurrent control',
        'Stratification to be applied': 'Contact reason and agent tenure band',
        '**Practical significance threshold**': '1.5 percentage points — below this the benefit does not clear the cost',
        'Alpha': '0.05',
        'Power / required n per group': '80% power needs 6,900 per group; 8 weeks yields ~7,300',
        'Stopping rule': 'Stop early only for harm: CSAT down more than 0.15 or handle time up more than 8%',
        'Who runs the analysis': 'M. Berenji, with A. Okafor reviewing before it is circulated',
        'Primary:': '7-day reopen rate | 14.2% | 8.0% | 1.5 pts | 2-proportion | Weekly',
        'Counter-bal:': 'CSAT, billing | 4.11 | no decline | -0.15 | Mann-Whitney | Weekly',
        'Pilot effect': '-4.9 percentage points (CI -6.1 to -3.7)',
        'Assumed realization factor': '0.85',
        '**Forecast at full rollout**': '-4.2 points, worth $22,005 a year',
        'Basis for the realization assumption': 'Sites B and D have a different release cadence, so uptake lags by about a quarter',
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
        'Master Black Belt': 'S. Iyer | | 2026-11-20',
        '90-day': '2027-02-12 | A. Okafor | 7.9% | Held | No action',
        '**180-day re-audit**': '2027-05-14 | A. Okafor | 8.4% | Drifting | Reopen: check whether the deferred-close rule is still enforced after the platform upgrade',
        'Contact-mix chi-square, baseline vs post (p)': '0.38 — no material mix shift',
        'Mix-adjusted effect': '-4.7 points (unadjusted -4.9)',
        'Baseline metric': '14.2%',
        'Post metric': '7.6%',
        'Improvement': '6.6 percentage points',
        'Annualized units affected': '4,052 reopens avoided',
        'Unit cost basis ($)': '$6.80 fully-loaded cost per contact',
        '**Gross annual benefit**': '$27,554',
        'Realization factor applied': '0.85',
        '**Realized annual benefit**': '$23,421',
        'Harvest mechanism': 'Hiring avoidance — two billing roles removed from the Q1 plan',
        'Harvest evidence (req/plan/PO reference)': 'Headcount plan v4, lines 22-23, signed by WFM 2026-11-08',
        'Double-counting check — overlapping projects': 'Checked against BIL-2026-009 (payment retries); no shared contacts',
        'Black Belt': 'M. Berenji | | 2026-11-14',
        'Champion': 'R. Mehta | | 2026-11-15',
        '**Finance partner**': 'J. Lindqvist | | 2026-11-20',
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
    "01-charter-extra": {},
    "02-sipoc": {
        "Suppliers": "Customer; billing platform; Tier 1 support; adjustments desk",
        "**First step** (process starts when…)": "the customer submits a billing dispute",
        "**Last step** (process ends when…)": "the adjustment has posted and the customer has confirmed",
    },
    "03-voc-ctq-tree": {
        'Survey verbatims': 'All billing CSAT responses | Census, 12 weeks | 2,180 | Insights team | Apr-Jun',
        'Contact transcripts': 'All billing contacts | Topic model, then 200 read by hand | 8,400 | Black Belt | May',
        'Customer interviews': 'Customers with a disputed charge | Purposive, 6 sessions | 6 | Black Belt | May',
        'Complaint / escalation review': 'All formal billing complaints | Census, 12 weeks | 61 | Complaints team | Apr-Jun',
        'Churn exit reasons': 'Cancelling accounts | Census | 340 | Retention | Apr-Jun',
        'Survey verbatims': 'CSAT free text, billing | All billing CSAT responses | Census, 12 weeks | 2,180 | Insights | Apr-Jun | Only 14% respond — survivorship',
        'Contact transcripts': 'Chat and email, billing queue | All contacts | Topic model, then 200 read by hand | 8,400 | Black Belt | May | Voice excluded, so phone-only issues are invisible',
        'Customer interviews': 'Customers with a disputed charge | Reopened tickets | Purposive, 6 sessions | 6 | Black Belt | May | Recruited from reopens, so biased toward failure',
        'Complaint / escalation review': 'Formal complaints, billing | All | Census, 12 weeks | 61 | Complaints team | Apr-Jun | Small n, high signal',
        'Churn exit reasons': 'Cancellation survey | Cancelling accounts | Census | 340 | Retention | Apr-Jun | Self-reported and post-hoc',
        'Internal (VOB / VOE)': 'Agent forum and QA notes | Billing agents | Ongoing | n/a | QA lead | Ongoing | Agents name the posting delay unprompted',
        '1': 'Do not make me chase it | The adjustment posts before I am told it is done | Reopens within 7 days | <= 8.0% | Warehouse query OD-BIL-004 | All billing tickets | Census',
        '2': 'Tell me when it will be resolved | A committed date given at first contact | Share of contacts with a commitment logged | >= 90% | QA audit item 7 | Sampled contacts | 200/week stratified',
        '3': 'Do not make me repeat myself | Resolved without a second contact | 7-day reopen rate | <= 8.0% | OD-BIL-004 v2 | All billing tickets | Census',
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
    val = values.get(label)
    if not val or not any(c == "" for c in body):
        return line                    # nothing to say, or nothing left to fill
    if any(c.startswith("*") for c in body):
        return line                    # already carries an example — re-running
                                       # must not shift the columns along again
    # Fill the BLANKS in order and leave anything already there alone. Skipping
    # a row because one cell was pre-filled left every wide table empty — the
    # row label sits in the second column on those, so they always looked full.
    # keep empty parts: a signature row is "Name | | Date", and dropping the
    # blank shifted the date into the signature column
    parts = [x.strip() for x in val.split("|")]
    out, i = [], 0
    for c in body:
        if c == "" and i < len(parts):
            out.append("*%s*" % parts[i] if parts[i] else "")
            i += 1
        else:
            out.append(c)
    return "| %s | %s |" % (cells[1].strip(), " | ".join(out))


def main() -> int:
    changed = 0
    for name, _ in HOWTO.items():
        path = TEMPLATES / f"{name}.md"
        if not path.exists():
            print(f"  missing: {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        # Filling tables is a ONE-TIME operation. It writes into whichever cells
        # are still blank, so running it twice walks the values one column along
        # and puts the date in the signature box. The how-to block is safe to
        # rewrite; the tables are not.
        done = MARK in text
        if done:
            text = re.sub(re.escape(MARK) + r".*?\n---\n", "", text, count=1, flags=re.S)
        lines = text.split("\n")
        # the block goes after the H1 title
        for i, line in enumerate(lines):
            if line.startswith("# "):
                lines.insert(i + 1, "\n" + block(name))
                break
        # Filling is safe to repeat: fill_row skips any row that already carries
        # an italic example, so a second run is a no-op rather than a shift.
        # Gating on `done` meant a template restored from git could never be
        # re-filled, which is exactly what happened.
        values = EXAMPLE.get(name, {})
        if values:
            lines = [fill_row(ln, values) if ln.startswith("|") else ln for ln in lines]
        # The block removal leaves the newline that preceded it, so each run
        # added two blank lines and the file never settled.
        out = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
        if out != path.read_text(encoding="utf-8"):
            path.write_text(out, encoding="utf-8")
            changed += 1
        print(f"  {path.name:40s} guidance added"
              f"{', worked example filled' if values else ''}")
    print(f"\n  {changed} template(s) rewritten")
    return 0


if __name__ == "__main__":
    sys.exit(main())
