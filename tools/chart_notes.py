#!/usr/bin/env python3
"""How to read each chart, and what would worry you.

Every chart in the pack is drawn from the cells above it and none of them said
how to read it. A chart title carries a hint at best — "a shapeless cloud is the
only shape you can use" — and a reader who does not already know what a residual
plot is cannot act on that. A chart nobody can interpret is decoration, which is
the same defect as a check that cannot fail.

Keyed by chart title, which is unique across the pack except for the two benefit
tabs of the calculator workbook, where the same chart is drawn twice and one note
is correct for both.

Figures quoted here are read out of the shipped worked example. Where a chart's
own numbers were not verified, the note says how to read the shape and stops —
an invented figure would be worse than no note, and this pack exists to say so.

Rendered as a <figcaption> under each chart by tools/chartsvg.py.
"""
from __future__ import annotations

NOTES: dict[str, str] = {
    # ---------------------------------------------------------------- define
    "Sample size against margin of error — and where your study sits":
        "Read down, not across: halving the margin of error roughly quadruples the sample. "
        "The marked point is your own study. If it sits on the steep left-hand part of the "
        "curve, a small change in the precision you ask for costs you a lot of tickets — "
        "decide the margin you actually need before you commit to a duration.",
    "Where the time actually goes, step by step":
        "Working time and waiting time on the same axis, one pair per step. The worked "
        "example totals 26 minutes of touch inside 2,426 minutes of lead time — 1.07%. "
        "What should worry you is a tall wait bar next to a step nobody owns: that is the "
        "queue to attack, and it is almost never the step people expect.",
    "Weighted total by candidate cause — the top three are where you start":
        "Bars are the weighted totals, so height already accounts for which CTQ matters "
        "most. Look for a clear step down after the top few. Where the top bars are level "
        "— 270 against 261 here — the ranking is inside anyone's scoring noise, and you "
        "should treat them as one set to investigate rather than an order to work through.",
    "Causes per branch — a thin bar is a blind spot":
        "This counts causes, not their importance. A branch with one cause usually means "
        "the team ran out of ideas there, not that the branch is clean — Measurement and "
        "Environment are the two that go thin in support. Fill the thin branches before "
        "you start scoring anything.",
    "Stakeholder map — influence against support":
        "Position is what matters, not the dots. High influence with low support is the "
        "quadrant that kills projects, and it is the one people leave until last. Anyone "
        "up and to the left needs a named plan and a date before Improve starts.",
    "Where your requirements fall — and which ones are worth money":
        "Delighters earn a premium today and become expected within a year or two, so "
        "read this as a snapshot with a shelf life. What should worry you is a feature "
        "you are proud of sitting in Indifferent: it costs to build and nobody values it.",

    # --------------------------------------------------------------- measure
    "Cohen's kappa against the usual thresholds":
        "Kappa is agreement after chance is removed, which is why it is so much lower "
        "than the raw agreement percentage people quote. Below 0.4 the data cannot be "
        "used for individual performance management at all. Fix the rubric and re-run — "
        "improving the training rarely moves it.",
    "Where your measurement error is — under 30% or the study stops here":
        "Bars are % study variation, a share of standard deviation. The worked example "
        "reads 28.4% — MARGINAL — and the split matters more than the total: "
        "reproducibility at 26.1% against repeatability at 11.2% says the three people "
        "disagree with each other far more than any one disagrees with himself. That is "
        "a rubric and calibration problem, and a better stopwatch will not touch it.",
    "DPMO — you against the scale":
        "A log-scaled ladder, so each sigma level is a step change rather than an "
        "increment. Your bar against the rungs is the whole message. Most support "
        "processes land between 3 and 4 sigma; treat 6 as a direction, not a target.",
    "Mean, median and p90 — quoting the mean hides the tail":
        "Three markers on one axis. The gap between mean and median is the skew, and the "
        "distance out to p90 is what your customers actually feel. If the mean sits well "
        "below the median you are quoting a number almost nobody experiences — report the "
        "median and the p90 together, or report neither.",

    # --------------------------------------------------------------- analyse
    "Handle time against transfers — the line is the model, the scatter is what it misses":
        "The line is what the model claims; the vertical distance from each point to it "
        "is what it got wrong. One driver explains 26.4% of the spread here, so three "
        "quarters of it is everything not on this chart. Read the residual plot on the "
        "next tab before you quote the slope anywhere.",
    "Residuals against fitted — a shapeless cloud is the only shape you can use":
        "Fitted values across, misses up and down, zero as the reference line. A "
        "shapeless band means the straight line is a fair description. A funnel means "
        "the error grows with the prediction, and a curve means you have fitted a line "
        "to something bent — in both cases the p-values above are not trustworthy. The "
        "24 residuals here sit between roughly -100 and +100 seconds with no funnel and "
        "no curve.",
    "Effect size — which factor actually moved the response":
        "Bars are effects, so length is what matters and the sign only tells you which "
        "way. Read the interactions beside the main effects: a large interaction means "
        "neither factor can be set on its own, and reporting its main effect alone is "
        "how a DOE result stops replicating.",
    "Where the variation lives — share of the total":
        "Shares of VARIANCE, so they add to 100% while the standard deviations behind "
        "them do not. Attack the tallest bar. A family clamped to zero has not been "
        "shown to be identical — only that this sample cannot separate it from the "
        "family nested inside it, which is a sampling result and not a finding.",
    "Mean handle time by agent — the multi-vari picture":
        "One point per agent, grouped by team and site, so the eye can see which level "
        "the spread lives at. Bars level within a team but stepped between teams point "
        "at supervision or routing; scatter inside a team points at the individuals. "
        "The axis starts at zero because seconds do.",
    "Where the hop time goes — total seconds by system pair":
        "Ranked by total seconds, so the top bar is the integration to build first. The "
        "heaviest pair here takes 198 of 737 logged seconds — 26.9% of all the swivelling "
        "on one pair. Check the re-key column beside it: a hop that re-types data is both "
        "the waste and a defect opportunity.",
    "Seconds spent hopping, contact by contact":
        "One bar per contact, so the shape tells you whether the swivel is universal or "
        "concentrated. Even bars mean every contact pays it and the fix is worth the "
        "whole volume; a few tall bars mean a subset of cases is doing something the "
        "others are not, and that subset is the thing to define.",
    "p-value by test, against alpha = 0.05":
        "The line is your alpha, not a verdict. A p-value below it says the difference "
        "is unlikely to be noise — it says nothing about whether the difference is worth "
        "acting on, which is what the practical threshold you registered beforehand is "
        "for. Watch for a wall of tests just under the line: that is the shape of "
        "hypothesis-shopping.",

    # --------------------------------------------------------------- improve
    "Weighted score by solution — the top three are the shortlist":
        "Scores land back on the 1-5 scale because the weights sum to 1. A shortlist, "
        "not a decision: check the countermeasure level of the top few before you commit, "
        "because a high-scoring solution that only guides behaviour will decay while a "
        "lower-scoring one that designs the failure out will not.",
    "Where you sit against the SLA — area past the red line is a breach":
        "The red line is your SLA limit; everything to the right of it is a contact you "
        "missed. The verdict cell reads the capability index, not this picture, but the "
        "picture is what makes the index mean something — a long right tail past the "
        "line is the promise you are actually breaking.",
    "Lead time in days — today against target":
        "Two bars, no trend. Read it beside the backlog chart on the same tab: lead time "
        "falling while open tickets rise means you are triaging rather than resolving, "
        "and the improvement will reverse the moment the queue is worked.",
    "Open tickets against the cap":
        "The cap is a decision, not a measurement — it is the level above which lead "
        "time starts to climb faster than volume. Sitting above it for more than a week "
        "means the queue is the constraint, whatever the handle-time numbers say.",
    "Minutes of work against minutes of waiting":
        "Process cycle efficiency in two bars. In support the working bar is almost "
        "always the short one, and single-digit efficiency is normal rather than "
        "alarming. The number to act on is the waiting bar's composition, not this ratio.",
    "From offered load to paid FTE — where does the headcount actually go?":
        "Each bar adds one effect: offered load, then the agents queueing theory needs "
        "on top of it, then shrinkage. Shrinkage is applied to the ANSWER, never to the "
        "load — inflating the load first and then running Erlang produces a different "
        "and wrong number.",
    "Service level against agents — the cliff, and where it flattens":
        "The curve is steep then flat, so one agent either side of the knee is worth far "
        "more than one agent further along it. At 67 agents against an offered load of "
        "60 erlangs the worked example delivers 82.3%. Past the flattening you are buying "
        "very little service level for real money, which is the argument this chart exists "
        "to make.",
    "Gross value against what Finance will actually book":
        "Two bars: what the arithmetic produces and what survives the realisation factor. "
        "The gap is not pessimism — it is the share of a saving that never becomes cash "
        "because the capacity is absorbed rather than removed. Quote the right-hand bar. "
        "A benefit case that quotes the left-hand one does not survive validation.",
    "Cumulative discounted position — it crosses zero at payback":
        "Starts negative by the whole investment and climbs by each year's discounted "
        "benefit. Where it crosses zero is payback. A line that never crosses inside the "
        "years you modelled is the answer, not a broken chart — and under 18 months is "
        "generally an easy sell.",
    "Risk priority number — ranked, and did the action reduce it?":
        "Before and after, ranked by the before. Two things to check. A row where the "
        "bars are the same height has an action that has not shipped yet — the New scores "
        "are only filled once a control is live, so an unchanged pair is honest rather "
        "than a failure. And severity 9 or 10 is acted on wherever it ranks, because "
        "severity is the one score an action cannot lower.",

    # --------------------------------------------------------------- control
    "Controls by level — lower is more durable":
        "Level 1 eliminates the demand, level 6 asks someone to be careful. A plan "
        "weighted to the right will decay: training and reminders fade within two "
        "quarters, and the process reverts with nobody accountable for noticing. Count "
        "the bars on the left before you sign it off.",
    "Where you are against what you promised (days)":
        "Actual against commitment, so the gap is the message. Read it with the WIP "
        "number on the same tab: lead time is work in progress divided by throughput, "
        "so a promise you keep missing is usually a WIP limit you never set.",
    "Individuals — is the process stable?":
        "One point per period against limits frozen from the baseline window. Limits are "
        "held still on purpose — recomputing them as data arrives lets the line follow a "
        "drift, and a chart that follows the process it is watching cannot signal that "
        "the process moved. The worked example runs flat for twenty points and then steps "
        "past the upper limit twice.",
    "Moving range — did it jump between periods?":
        "The gap between consecutive points. Read it WITH the chart above: level moving "
        "while spread holds still is a shift, and both moving together is usually a "
        "measurement or definition change rather than a process one. In the worked "
        "example the range stays in control while the individuals chart signals — the "
        "level moved and the spread did not.",
    "Laney p′ — limits that survive 8,000 contacts a day":
        "A proportion per period, with limits that widen on quiet days and tighten on "
        "busy ones. The Laney correction is what stops a plain p-chart signalling on "
        "every point once the samples get large. Two points fall through the lower limit "
        "in the worked example — a service-level collapse while volume held.",
    "Laney u′ — defects per unit":
        "Defects per unit audited, not the share of units with a defect — one contact "
        "can carry several. Same correction as the p′ chart and for the same reason: "
        "audit rates move more between weeks than sampling alone explains, and without "
        "it the chart cries wolf on the quiet weeks.",
    "Xbar — is the average stable?":
        "Subgroup averages against limits from the baseline window. Read the range chart "
        "first: limits here are computed from the within-subgroup spread, so if that is "
        "unstable these limits are meaningless. The worked example steps up across the "
        "last four subgroups while the range chart stays put.",
    "R — is the spread stable? Read this one first":
        "Within-subgroup range, and the title is the instruction. This chart supplies "
        "the sigma the Xbar chart's limits are built from, so an out-of-control range "
        "invalidates the chart above it. Settle the spread, then read the average.",
    "EWMA — the limits widen then settle as evidence accumulates":
        "Each point is a weighted memory of the ones before, so a small sustained shift "
        "shows up here long before it breaks an individuals chart. The trade is "
        "responsiveness: a single wild point barely moves the line, so run it alongside "
        "an I chart rather than instead of one.",
    "CUSUM — the sum climbs from the day the change landed":
        "It accumulates departures from target, so the SLOPE is the signal and the height "
        "is only history. The value is diagnostic: where the line starts climbing dates "
        "the change, which an individuals chart cannot tell you. In the worked example it "
        "starts climbing well before any single point looks unusual.",
    "t-chart — days between incidents. Rising is good.":
        "Time between rare events, so up is improvement and the upper limit is the one "
        "worth breaking. There is no frozen baseline here — the limits move with the "
        "data, so a gap has to be long enough to clear limits it widens itself. Gaps are "
        "exponential, not normal, which is why the chart works on a transformed scale.",
    "g-chart — contacts handled between incidents":
        "The same question counted in contacts rather than days, which is the one to use "
        "when volume swings. A rate that looks flat in days can be improving in contacts "
        "if you are simply handling more — and the reverse, which is the trap.",
    "Pareto — ranked, with cumulative share":
        "Bars ranked, line cumulative. The top category runs 42.7% and the top two reach "
        "66.8%, so two of them carry two-thirds of the volume. Where the line crosses 80% "
        "is the set worth working on. A flat Pareto with no clear break means the "
        "categories are wrong, not that the problem is evenly spread.",
}
