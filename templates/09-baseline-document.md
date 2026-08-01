# Baseline — <Primary metric>

<!-- guidance -->
## How to use this

**What it is for.** The number the project is judged against, with the evidence that it is stable enough to be judged against.

**When.** End of Measure. This is the tollgate.

**Who signs it.** Black Belt · Champion and Finance both sign the baseline value

**The mistake this prevents.** Baselining an unstable process. If the control chart is signalling, the mean is not a number — it is an average of two different processes, and any improvement you claim against it is unfalsifiable.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 7-day reopen rate on in-scope billing adjustments of 14.2% against a target of 8%. That rate is the project's Y, defined separately as OD-BIL-004-ADJ and measured at 137 reopens in 966 in-scope adjustments in the baseline month (section 5). The whole Billing queue's 7-day reopen rate under OD-BIL-004 v2 is also 14.2%; it is a different quantity, it is what sections 2–4 chart, and it is context only. Delete them as you fill your own in.*

---

**This document is the zero point for the benefit clock. Finance signs it.**

## 1. Extract

| Field | Value |
|---|---|
| Metric | *7-day reopen rate, in-scope billing adjustments — the project's Y. Not the whole-queue rate of almost the same name, which also reads 14.2%* |
| Operational definition ref | *OD-BIL-004-ADJ — the adjustment-scoped definition. Sections 2–4 below are cut on OD-BIL-004 v2, the whole-Billing-queue definition; that one is context and is never a benefit denominator* |
| Period covered | *2026-01-05 to 2026-03-29 — 12 whole weeks* (minimum 13 weeks; 12 months preferred — this window is one week short of the minimum this row asks for, which is flagged here rather than fixed: extending a signed baseline is a Finance/MBB call) |
| Records (n) | *61,400 billing tickets — the whole Billing queue over those 12 weeks at ~5,100/week, which is what sections 2–4 are cut on. The project's own population is the 966 in-scope adjustments in the baseline month at section 5* |
| Extract date | *2026-04-02* |
| Extract query / job ref | *warehouse job bl_reopen_baseline, commit 4f2a9c1* |
| Immutable snapshot stored at | *s3://analytics-snapshots/BIL-2026-014/baseline.parquet* |

## 2. Stability

| Field | Value |
|---|---|
| Chart type used | (I-MR / X̄-S / Laney p′ / Laney u′) |
| Chart type justification | *Proportion at ~5,100 billing tickets/week — the whole queue; sigma z = 4.25, so an ordinary p-chart would signal on almost every point* |
| Centre line | *14.2% — the 7-day reopen rate on all billing tickets (OD-BIL-004 v2). The in-scope adjustment population is not separately charted anywhere in this document: `<weekly control chart, centre line and limits for OD-BIL-004-ADJ — Analytics to produce before the benefit in section 7 is re-signed>`* |
| UCL / LCL | *17.1% / 11.3%* |
| σ_z (if attribute chart) | (near 1.0 = no overdispersion; >1.2 = use Laney) |
| Special causes found | *One week (w/c 2026-02-16) above the UCL — a billing platform release* |
| Special causes excluded (and why) | *None excluded. The release is a real process condition and will recur.* |
| **Process stable?** | Yes / No |

> Capability is meaningless on an unstable process. Demonstrate stability first.

## 3. Distribution

| Statistic | Value |
|---|---|
| n | *61,400 tickets over the 12-week window (~5,100/week) — the whole Billing queue; every statistic in this section is the queue's, not the adjustment population's* |
| Mean | *14.2% — the queue rate (OD-BIL-004 v2)* |
| **Median** | *14.0%* |
| Standard deviation | *1.4 points* |
| p10 / p50 / p90 / p95 | *12.3% / 14.0% / 16.2% / 16.9%* |
| Skewness | *0.31 — mild right skew, as expected for a proportion near the middle* |
| Distribution shape | *Approximately symmetric at weekly aggregation; the underlying durations are not* |
| Normality assessment (probability plot, not just the p-value) | *Probability plot near-linear; Anderson-Darling p = 0.03, which at 12 weekly points is not a concern* |
| Bimodality present? If so, resolved by stratifying on | *No. Checked by stratifying on site and on tenure band — one distribution in both* |

> For any duration metric, report median and p90 — never the mean alone. The customers
> who suffer are in the tail, and the mean hides them.

## 4. Capability

| Field | Value |
|---|---|
| Specification | USL = ___ / LSL = ___ (support specs are usually one-sided) |
| Index used | Ppu / Ppl / Ppk / binomial capability |
| Index justification | *Ppu — only an upper limit exists (target is a maximum). Computed on the whole-queue series charted in section 2 (OD-BIL-004 v2), so every figure in this section is the queue's capability, not the in-scope adjustment population's: `<capability of OD-BIL-004-ADJ — Analytics to compute once the adjustment-level chart above exists>`* |
| Transformation applied | (none / Box-Cox λ = ___ / Johnson / fitted lognormal) |
| **Capability index value** | *Ppu 0.42* |
| % outside specification (observed) | *58% of weeks above the 8.0% target* |
| % outside specification (fitted) | *61%* |
| DPU / DPO / DPMO | *0.142 / 0.0284 / 28,400* |
| Opportunities per unit (program standard) | *5 — fixed at programme level, never renegotiated mid-project* |
| Z from data (long-term) | *1.90* |
| Sigma level (with 1.5σ shift) | *3.40* |
| Rolled throughput yield across tiers | *55.6% — first-pass yield compounds badly across four steps* |

## 5. Stratified baseline — in-scope billing adjustments (OD-BIL-004-ADJ), the project's Y

| Stratum | n | Metric value | Share of total gap |
|---|---|---|---|
| *Raised before 17:00, under $50 — agent approves it, catches the same night's 02:00 batch* | *402* | *7.5% (30 reopens)* | *None — 2 reopens below the 8% target* |
| *Raised after 17:00, under $50 — misses the batch by one night* | *214* | *18.7% (40 reopens)* | *37% of the 60-reopen gap* |
| *Over $50, raised before 17:00 — needs a Billing Ops check first* | *168* | *14.3% (24 reopens)* | *17%* |
| *Over $50, raised after 17:00 — waits for the next Billing Ops run, then the next batch* | *121* | *24.8% (30 reopens)* | *33%* |
| *Multi-line accounts — the adjustment splits across lines and posts partially* | *61* | *21.3% (13 reopens)* | *13%* |
| *All strata, one baseline month (check: 966 in-scope adjustment contacts, 137 reopens, 14.2% under OD-BIL-004-ADJ; the gap to 8% is 60 reopens). This is a month, not the 12 weeks the extract in section 1 covers: `<which month the five strata were counted over — A. Okafor, process owner, to state before section 7 is re-signed>`* | *966* | *14.2%* | *100%* |

## 6. Context and caveats

| Event in the baseline window | Dates | Effect | Included or excluded |
|---|---|---|---|
| *Annual price letters land with the January bill — the seasonal disputes peak* | *2026-01-05 to 2026-01-30* | *Busiest weeks in the window, ~6,400 tickets/week against a ~5,100 average; queue reopen rate 14.6%, inside the control limits in section 2* | *Included. It happens every January, and the post-project comparison has to span the same season or it will read the calendar as an improvement* |
| *List price change on the mid-tier broadband plan* | *2026-02-01* | *Disputed-charge volume up ~18% for three weeks; queue reopen rate flat at 13.9% — the change moved the denominator, not the process* | *Included. Pricing changes are a standing feature of the business; the baselined metric is a rate, so volume alone does not distort it* |
| *Billing platform release 15.4 — the nightly posting job was rewritten* | *w/c 2026-02-16* | *The posting batch failed silently on two nights; reopen rate 18.9% that week, the one point above the UCL in section 2* | *Included. Releases ship every six weeks and this failure mode will recur. Excluding it would flatter the baseline and make the project look smaller than it is* |
| *Tier 1 reorganisation — the billing queue split out of general support; 11 transferred agents shadowed for two weeks* | *2026-03-02 to 2026-03-13* | *74 contacts were closed under the old general-support script rather than the billing closure steps* | *Excluded — those 74 fall outside OD-BIL-004-ADJ, which scopes the project's metric to in-scope billing adjustments, and the 966 in section 5 is net of them. This is a scope exclusion, not a special-cause exclusion: neither week signalled on the chart* |

## 7. Benefit model updated with actual baseline

| Item | Charter estimate | Actual baseline | What it does to the benefit |
|---|---|---|---|
| *Reopen-rate gap to be closed* | *No different estimate to reconcile: the charter's baseline is the same 14.2% (01-project-charter.md:48,89), though it does not say which of the two populations it means. The "15.0% from the 2025 ops dashboard" that stood in this cell is in no document in the pack* | *14.2% → 8.0%, so 6.2 points, on in-scope billing adjustments (OD-BIL-004-ADJ; 137 reopens in 966 contacts, section 5)* | *The gap does not move. What moves is the population it may be applied to: it was measured on adjustments, so it may only ever be multiplied by adjustments* |
| *In-scope billing-adjustment contacts* | *`<none — the charter states no adjustment volume at all; the "1,100 a month" that stood in this cell is in no document in the pack>`* | *966 a month (section 5), so 11,592 a year* | *This is the only benefit denominator. The queue's 266,000 tickets a year (01-project-charter.md:47) is context and is never a multiplier* |
| *Fully loaded cost of a reopened contact* | *$41.00 — an estimate, and stale. It is not traceable to the charter's own unit-cost row, which states $6.80 (01-project-charter.md:51)* | *$38.60 — Finance's 2026 fully-loaded rate for a reopened contact, with the facilities allocation removed* | *$38.60 is the cost basis of record. The $6.80 is the cost to serve one contact, not the price of a reopen; pricing a reopen at it is the defect* |
| *Realization factor* | *0.85 — agreed with Finance at the Define tollgate (01-project-charter.md:53)* | *0.85 — unchanged* | *Applied once, at the end of the chain below* |
| *How the saving is harvested* | *"Headcount reduction", no owner named* | *No reduction is available: the billing queue is already 4 heads below its approved establishment* | *Nothing in the chain below is bookable as cash until a named harvest exists. `<The queue's approved establishment and its actual headcount at the claim date — WFM to state before this section is re-signed>`: 18-handover-and-benefit-validation.md:86 records two billing roles removed from the Q1 plan, signed by WFM 2026-11-08, which this row contradicts* |

**The chain, as arithmetic the reader can follow:**

| Step | Arithmetic | Result |
|---|---|---|
| *In-scope adjustments a year* | *966 a month × 12* | *11,592* |
| *Reopens avoided a year* | *11,592 × 6.2 points* | *719* |
| *Gross benefit* | *719 × $38.60* | *$27,753* |
| *Realized benefit* | *$27,753 × 0.85* | *$23,590* |
| *less the handle time the fix adds* | *`<not measured in this document>`* | *`<blank>`* |

*The chain lands at $23,590, and **that does not clear the $50,000 realized floor Finance sets for a bookable project** (01-project-charter.md:99). It is 47% of the floor, before the handle-time cost below is taken off it. The 6.2 points is the whole of the gap this project is chartered to close, so $23,590 is the ceiling, not a first estimate. Do not round toward the floor and do not reach for a larger population to rescue it — reaching for the queue's 266,000 is precisely the error recorded in section 8.*

*How much handle time the fix adds: `<not measured in this document>`. Verifying the posting before the ticket closes lengthens the contact, and that cost has to come off the $23,590 before any benefit is claimed. R. Okonjo (Tier 1 team lead, 01-project-charter.md:123) and Finance must measure it on the in-scope adjustment population and price it at the same 2026 rate, before this section is re-signed. The charter's "roughly 40 s" (01-project-charter.md:123) is an expectation offered at charter time, not a measurement, and it is not used here.*

## 8. Revision history

> Corrections to a signed baseline are recorded here, not quietly applied. A baseline
> whose errors are invisible cannot be audited, and the error below is the one most
> benefit cases die of.

| Version | Date | What changed, and why |
|---|---|---|
| *v1.0* | *2026-06-05* | *First issue: the 12-week queue control chart (sections 2–4), the 966-contact adjustment stratification (section 5) and the first benefit model (section 7).* |
| *v1.1* | *`<date this revision is signed>`* | *Every reopen rate in this document now names its population. Two different quantities were both being called "the 14.2% 7-day reopen rate": the whole Billing queue under OD-BIL-004 v2 (sections 2–4, context only) and in-scope billing adjustments under OD-BIL-004-ADJ (section 5, 137 reopens in 966 contacts — the project's Y). Both are genuinely measured and both land on 14.2%, which is why the collision went unseen for so long. Neither figure moved.* |
| *v1.1* | *`<same date>`* | *Section 7 rebuilt, and the reason recorded rather than deleted. The chain the pack carried ran 266,000 queue tickets a year × 6.2 points × $6.80 × 0.85 = $95,324 (the charter's Define-tollgate figures, 01-project-charter.md:47,50,52,54). The arithmetic is exact and the causality is impossible. The fix touches in-scope adjustments only: 11,592 of the 266,000 contacts, 4.4%, and at 14.2% each, 1,646 of the queue's 37,772 reopens — 4.4% again. Fix every adjustment reopen and the queue rate moves from 14.2% to (37,772 − 1,646) ÷ 266,000 = 13.58%, a 0.62-point move. The chain claimed 6.2 points: ten times the arithmetic maximum. The rate was measured on one population and the volume taken from another. Rebuilt on 11,592 adjustments a year at the $38.60 reopen cost, which supersedes the $41.00 estimate, it realizes $23,590 and does not clear the $50,000 floor. The intermediate figures this section used to carry — $425k, $376k, $330k, $310k, $180k and $130k — are not derivable from any measurement in the pack and are struck.* |
| *v1.1* | *`<same date>`* | *"Period covered" restored to 2026-01-05 to 2026-03-29 (12 whole weeks); the dates had been lost from the shipped file. The window is one week short of the 13-week minimum this document itself asks for — flagged in section 1, not fixed, because extending a signed baseline is a Finance/MBB call.* |

## Sign-off

| Role | Name | Signature | Date |
|---|---|---|---|
| Black Belt | *M. Berenji* |  | *2026-06-05* |
| Process owner | *A. Okafor* |  | *2026-06-05* |
| **Finance partner** | *J. Lindqvist* |  | *2026-06-08* |
| Master Black Belt | *S. Iyer* |  | *2026-06-08* |
