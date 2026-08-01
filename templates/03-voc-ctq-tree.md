# VOC Plan and CTQ Tree — <Project>

<!-- guidance -->
## How to use this

**What it is for.** Turns what customers say into something you can measure, without losing the meaning on the way.

**When.** Define, after the SIPOC and before the baseline — you cannot measure a CTQ you have not defined.

**Who signs it.** Black Belt · signed off with the process owner and whoever owns the survey

**The mistake this prevents.** Jumping from a verbatim straight to a metric. The middle column is the work: a need is not a driver and a driver is not a measure.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate on in-scope billing adjustments (OD-BIL-004-ADJ, measured at 137 reopens in 966 adjustments in the baseline month) against a target of 8%. That is not the same 14.2% as the whole-queue rate under OD-BIL-004 v2; see the note under the CTQ tree. Delete them as you fill your own in.*

---

## 1. VOC collection plan

| Method | Population | Sample plan | n | Who | When | Known bias |
|---|---|---|---|---|---|---|
| Survey verbatims | *CSAT free text, billing reasons* | *12 weeks* | *n=2,180* | *Only 14% respond — survivorship* | *1 Mar – 31 May; sent 48h after every billing contact, extract pulled 2 Jun* | Non-response; bimodal responders |
| Contact transcripts | *Chat and email, billing queue* | *4 weeks* | *n=8,400* | *Topic-modelled, then read 200 by hand* | *4 weeks to 31 May; topic model rerun each Monday, the 200 hand-reads in the week of 2 Jun* | Only contacts that happened |
| Customer interviews | *Disputed-charge customers* | *6 sessions* | *n=6* | *Recruited from reopens, so biased to failure* | *8–19 Apr; each session booked 7–10 days after that customer's reopen* | Selection; social desirability |
| Complaint / escalation review | *Formal complaints, billing* | *12 weeks* | *n=61* | *Small n, high signal* | *1 Mar – 31 May, read at the Thursday complaints panel as they land* | Extreme cases only |
| Churn exit reasons | *Cancellation survey* | *12 weeks* | *n=340* | *Free text, self-reported* | *1 Mar – 31 May, taken with the monthly churn file on the 3rd* | Post-hoc rationalization |
| Internal (VOB / VOE) | *Agent forum and QA notes* | *ongoing* | *n/a* | *Agents name the same posting delay* | *Ongoing — forum threads read weekly, QA notes taken at the Friday calibration* | *Agents only meet the ones that come back; a credit that posts is never discussed* |

## 2. Affinity themes

| Theme | Frequency | Representative verbatim |
|---|---|---|
| *Told it was fixed, it was not* — the adjustment had not posted when the case closed | *412 contacts (43% of the 966 coded VOC contacts, 1 Mar – 31 May collection)* | *"The lady said it was all sorted on the Tuesday. I looked on the Thursday and the charge was still sitting there."* |
| *Credited against the wrong plan* | *233 (24%)* | *"You have refunded me for the 30GB tariff. I moved to the 60GB one in January and I have the email to prove it."* |
| *Charged twice for the same month* | *151 (16%)* | *"There are two identical line items on this bill. Now I have two case numbers as well and neither of them talks to the other."* |
| *Proration not explained* | *96 (10%)* | *"I switched on the 14th, so how is this bill bigger than a normal month? Nobody could walk me through it."* |
| *No idea when the money comes back* | *74 (8%)* | *"One person said three working days, the next said up to ten. I only rang back to find out which."* |

## 3. Kano classification

| Need | Must-be | Performance | Delighter | Evidence |
|---|---|---|---|---|
| *The credit I was promised is actually on my next bill* | *x* | | | *Nobody ever thanks us for a credit that posts; 412 of the 966 coded VOC contacts (1 Mar – 31 May collection) are about one that did not* |
| *Bill me once for one month* | *x* | | | *151 coded duplicate-charge contacts, and the complaints panel escalates almost every one it sees* |
| *Tell me the date the credit will show* | | *x* | | *All 6 interviewees asked for a date unprompted; the tighter the date given, the fewer the callbacks — 74 coded contacts are refund timing alone* |
| *You tell me it has posted, so I never have to check* | | | *x* | *No verbatim asks for it. The handful of agents who ring back off their own bat get named in CSAT free text by name* |

## 4. CTQ tree

Repeat one block per need.

```
Need:      "<customer's words>"
  Driver:  <what has to be true>
    CTQ:   <the measurable characteristic>
    Spec:  <target> (measured by <method>, n=<n>/<period>, population <who>)
```

| # | Need | Driver | CTQ | Spec / target | Measurement method | Population | Sampling |
|---|---|---|---|---|---|---|---|
| 1 | *Do not make me chase it* | *The adjustment posts before I am told it is done* | *7-day reopen rate, in-scope billing adjustments* | *<= 8.0%* | *OD-BIL-004-ADJ — a new definition, lineage not yet traced (see the note below)* | *In-scope billing adjustments (02-sipoc scope: consumer, voice/chat/email, sites A–D, up to $250; fraud holds, collections, manual cheques and proactive credits excluded)* | *Census — 966 adjustments in the baseline month* |
| 2 | *Tell me when it will be resolved* | *A committed date given at first contact* | *Share of contacts with a commitment logged* | *>= 90%* | *QA audit item 7* | *Sampled contacts* | *200/week stratified* |
| 3 | *Do not make me repeat myself* | *Resolved without a second contact* | *7-day reopen rate, all billing tickets* | *<= 8.0%, but context only — closing every adjustment reopen moves this rate 0.62 points, so it is not this project's to deliver (see the note below)* | *OD-BIL-004 v2* | *All billing tickets reaching Resolved — the whole Billing queue* | *Census* |

**Completion test:** if two people could measure this CTQ differently, it is not
finished. Every row above must survive that test.

**Two rates can wear the same name.** Rows 1 and 3 are both "a 7-day reopen rate"
and they are different quantities. Bind every row to its population as well as to
its query, or the rate measured on one population ends up multiplied by the volume
of another — the most common way a real benefit case dies.
> *Both rows read 14.2% today, which is exactly why nobody noticed. Row 1 is
> OD-BIL-004-ADJ — in-scope billing adjustments only, measured at 137 reopens in
> 966 adjustments in the baseline month (09-baseline-document, section 5). Row 3 is
> OD-BIL-004 v2 — every billing ticket reaching Resolved, 14.2% over 1–31 Mar
> (06-data-lineage, competing-definitions table). The 6.2-point gap the project is
> signed up to close is row 1's gap and cannot be carried to row 3's population: 966
> adjustments a month is 11,592 a year against 266,000 billing contacts a year
> (01-project-charter), so in-scope adjustments are 4.4% of the queue and 1,646 of
> its 37,772 reopens. Fixing every one of them moves row 3 from 14.2% to 13.58% —
> 0.62 points, a tenth of the 6.2 that was claimed against the whole queue.*

**Adjustment-level rate over the full baseline window:** `<not yet measured>`
> *One month stands behind the adjustment rate, not the 12 weeks the queue rate is
> cut on (09-baseline-document, section 3). Analytics must re-run OD-BIL-004 v2
> against the 02-sipoc in-scope denominator for 1 Mar – 31 May and issue the result
> as OD-BIL-004-ADJ before this CTQ tree is signed off.*

## 5. CTQ weighting (feeds the X-Y matrix)

| CTQ | Weight (1–10) | Rationale |
|---|---|---|
| *7-day reopen rate, in-scope billing adjustments (OD-BIL-004-ADJ)* | *10* | *The project Y. 14.2% — 137 reopens in 966 adjustments in the baseline month — against a target of 8.0% is why the charter was signed, and every other CTQ earns its weight by moving this one. Not the whole-queue rate of the same name under OD-BIL-004 v2, which reads 14.2% too and is a different quantity* |
| *Share of adjustments confirmed posted before the case is closed* | *9* | *The biggest bar on the Pareto — 412 coded VOC contacts. Closing the case before the nightly posting batch confirms is the mechanism the project exists to break* |
| *Share of contacts with a commitment date logged* | *7* | *Weaker link to the reopen rate, but it is the one thing a Tier 1 agent controls inside the call, and it covers the 74 coded VOC contacts about refund timing on its own* |
| *Mean handle time, billing adjustments* | *4* | *A guardrail rather than a goal: it is on the list so a fix cannot buy the reopen rate back with a longer call. 412 s today — seconds, not the 412 coded contacts two rows up — and anything outside 363–468 s is a signal* |
