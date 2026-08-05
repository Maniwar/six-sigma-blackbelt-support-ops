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
| Survey verbatims | *CSAT free text, billing reasons* | *12 weeks* | *n=2,180* | *Black Belt* | *1 Mar – 31 May; sent 48h after every billing contact, extract pulled 2 Jun* | Non-response; bimodal responders |
| Contact transcripts | *Chat and email, billing queue* | *4 weeks* | *n=8,400* | *Black Belt; the 200 hand-read with K. Tanaka (QA Lead)* | *4 weeks to 31 May; topic model rerun each Monday, the 200 hand-reads in the week of 2 Jun* | Only contacts that happened |
| Customer interviews | *Disputed-charge customers* | *6 sessions* | *n=6* | *Black Belt* | *8–19 Apr; each session booked 7–10 days after that customer's reopen* | Selection; social desirability |
| Complaint / escalation review | *Formal complaints, billing* | *12 weeks* | *n=61* | *D. Byrne (Compliance), at the Thursday panel* | *1 Mar – 31 May, read at the Thursday complaints panel as they land* | Extreme cases only |
| Churn exit reasons | *Cancellation survey* | *12 weeks* | *n=340* | *Black Belt, from the monthly churn file* | *1 Mar – 31 May, taken with the monthly churn file on the 3rd* | Post-hoc rationalization |
| Internal — Voice of the Business / Voice of the Employee | *Agent forum and QA notes* | *ongoing* | *n/a* | *M. Alvarez (Tier 1 Team Lead)* | *Ongoing — forum threads read weekly, QA notes taken at the Friday calibration* | *Agents only meet the ones that come back; a credit that posts is never discussed* |

## 2. Affinity themes

| Theme | Frequency | Representative verbatim |
|---|---|---|
| *Told it was fixed, it was not* — the adjustment had not posted when the case closed | *412 contacts (43% of the 966 coded VOC contacts, coded from the 1 Mar – 31 May collection — the outer span of section 1's six source windows, which are shorter and differ)* | *"The lady said it was all sorted on the Tuesday. I looked on the Thursday and the charge was still sitting there."* |
| *Credited against the wrong plan* | *233 (24%)* | *"You have refunded me for the 30GB tariff. I moved to the 60GB one in January and I have the email to prove it."* |
| *Charged twice for the same month* | *151 (16%)* | *"There are two identical line items on this bill. Now I have two case numbers as well and neither of them talks to the other."* |
| *Proration not explained* | *96 (10%)* | *"I switched on the 14th, so how is this bill bigger than a normal month? Nobody could walk me through it."* |
| *No idea when the money comes back* | *74 (8%)* | *"One person said three working days, the next said up to ten. I only rang back to find out which."* |

## 3. Kano classification

| Need | Must-be | Performance | Delighter | Evidence |
|---|---|---|---|---|
| *The credit I was promised is actually on my next bill* | *x* | | | *Nobody ever thanks us for a credit that posts; 412 of the 966 coded VOC contacts (1 Mar – 31 May collection, section 1) are about one that did not* |
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
| 1 | *Do not make me chase it* | *The adjustment posts before I am told it is done* | *7-day reopen rate, in-scope billing adjustments* | *<= 8.0%* | *OD-BIL-004-ADJ — a new definition, lineage not yet traced (see the note below)* | *In-scope billing adjustments (02-sipoc scope: consumer, voice/chat/email, sites A–D, up to $250; fraud holds, collections, manual refund cheques, enterprise accounts and proactive credits excluded — 02-sipoc.md:48-51, the same five exclusions restated at 06-data-lineage.md:61)* | *Census — 966 adjustments in the baseline month* |
| 2 | *Tell me when it will be resolved* | *A committed date given at first contact* | *Share of contacts with a commitment date logged* | *>= 90%* | *`<no operational definition exists for this CTQ anywhere in the pack — L. Haddad, QA manager (01-project-charter.md §7 metric-impact disclosure, :175), must write one stating what counts as a logged commitment date and which rubric item carries it, before the 90-day checkpoint on 2027-02-12 (18-handover-and-benefit-validation.md:142)>`. "QA audit item 7" cannot stand as the method: the only item 7 the pack records is "empathy demonstrated" (07-msa-attribute-agreement.md §4, :89)* | *`<not stated — L. Haddad must name the audit frame at the same time: row 1's in-scope adjustment population, or the whole Billing queue. The attribute agreement study sampled in-scope adjustments (07-msa-attribute-agreement.md §1, :25); the routine 200/week audit is bound to neither>`* | *200/week stratified* |
| 3 | *Do not make me repeat myself* | *Resolved without a second contact* | *7-day reopen rate, all billing tickets* | *No target — context only. The 8.0% belongs to row 1's adjustment population and to nothing else (01-project-charter.md §5 metric hierarchy, primary row at :124); the same table's context row carries "none; it is not a project target" for this rate (:125). Closing every in-scope adjustment reopen moves it 0.62 points, 14.2% to 13.58%, so it is not this project's to deliver (see the note below)* | *OD-BIL-004 v2* | *All billing tickets reaching Resolved — the whole Billing queue* | *Census* |

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
> cut on — 2026-01-05 to 2026-03-29, 12 whole weeks (09-baseline-document.md:26).
> Analytics must re-run OD-BIL-004 v2 against the 02-sipoc in-scope denominator over
> that same window and issue the result as OD-BIL-004-ADJ, before the 90-day
> checkpoint on 2027-02-12 (18-handover-and-benefit-validation.md:142). It has to be
> that window and no other: a rate cut on a different span cannot be set beside the
> queue baseline in 09-baseline-document sections 2–4, which is the only reason to
> measure it. The 1 Mar – 31 May this note used to name is section 1's VOC collection
> window, and two-thirds of it falls outside the signed baseline.*

## 5. CTQ weighting (feeds the X-Y matrix)

| CTQ | Weight (1–10) | Rationale |
|---|---|---|
| *7-day reopen rate, in-scope billing adjustments (OD-BIL-004-ADJ)* | *10* | *The project Y. 14.2% — 137 reopens in 966 adjustments in the baseline month — against a target of 8.0% is why the charter was signed, and every other CTQ earns its weight by moving this one. Not the whole-queue rate of the same name under OD-BIL-004 v2, which reads 14.2% too and is a different quantity* |
| *Share of adjustments confirmed posted before the case is closed* | *9* | *The biggest bar on the Pareto — 412 coded VOC contacts. Closing the case before the nightly posting batch confirms is the mechanism the project exists to break* |
| *Share of contacts with a commitment date logged* | *7* | *Weaker link to the reopen rate, but it is the one thing a Tier 1 agent controls inside the call, and it covers the 74 coded VOC contacts about refund timing on its own* |
| *Mean handle time, billing adjustments* | *4* | *A guardrail rather than a goal: it is on the list so a fix cannot buy the reopen rate back with a longer call. 412 s today — seconds, not the 412 coded contacts two rows up — and anything outside 363–468 s is a signal* |
