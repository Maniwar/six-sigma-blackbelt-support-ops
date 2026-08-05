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
| Metric | *7-day reopen rate, all billing tickets (OD-BIL-004 v2) — the whole Billing queue, which is what this extract holds and what sections 2–4 chart. It also reads 14.2%, and it is context only. The project's Y is the 7-day reopen rate on in-scope billing adjustments (OD-BIL-004-ADJ), stratified at section 5 and priced at section 7; this extract does not contain it* |
| Operational definition ref | *OD-BIL-004 v2 — the whole-Billing-queue definition, and the one every row of this table is cut on. The project's Y is defined separately as OD-BIL-004-ADJ; no extract for it is documented here and none is traced anywhere in the pack (06-data-lineage.md:68). The queue rate is never a benefit denominator* |
| Period covered | *2026-01-05 to 2026-03-29 — 12 whole weeks* (minimum 13 weeks; 12 months preferred — this window is one week short of the minimum this row asks for, which is flagged here rather than fixed: extending a signed baseline is a Finance/MBB call) |
| Records (n) | *61,400 billing tickets — the whole Billing queue over those 12 weeks at ~5,100/week, which is what sections 2–4 are cut on. The project's own population is the 966 in-scope adjustments in the baseline month at section 5* |
| Extract date | *2026-04-02* |
| Extract query / job ref | *warehouse job bl_reopen_baseline, commit 4f2a9c1* |
| Immutable snapshot stored at | *s3://analytics-snapshots/BIL-2026-014/baseline.parquet — the queue extract, and nothing else. There is no snapshot behind the project's Y: `<query, extract date and immutable snapshot for the 966 in-scope adjustments of section 5 — Analytics to produce before section 7 is re-signed>`* |

## 2. Stability

| Field | Value |
|---|---|
| Chart type used | *Laney p′* |
| Chart type justification | *Proportion at ~5,100 billing tickets/week — the whole queue; σ_z = 1.98, so an ordinary p-chart is too tight. Its limits would be 15.7% / 12.7%, and this document's own percentiles put p90 at 16.2% and p10 at 12.3% — at least a fifth of the twelve weeks outside, with no special cause behind them* |
| Centre line | *14.2% — the 7-day reopen rate on all billing tickets (OD-BIL-004 v2). The in-scope adjustment population is not separately charted anywhere in this document: `<weekly control chart, centre line and limits for OD-BIL-004-ADJ — Analytics to produce before the benefit in section 7 is re-signed>`* |
| UCL / LCL | *17.1% / 11.3%* |
| σ_z (if attribute chart) | *1.98 — read off the limits: half-width 2.90 points ÷ the ordinary 3σ half-width of 1.4663 points. Over 1.2, so Laney is the right chart* |
| Special causes found | *One week (w/c 2026-02-16) above the UCL — a billing platform release* |
| Special causes excluded (and why) | *None excluded. The release is a real process condition and will recur.* |
| **Process stable?** | *No — one point above the UCL. The mean of an unstable window averages two process states, so section 4 reports **Ppu**, a long-term performance index describing what this process did, rather than a Cpk-style prediction of what it will do. That is the honest index for a window with a signal in it, and it is why the release week is kept rather than excluded* |

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
| **Capability index value** | *Ppu −1.48 — (8.0% − 14.2%) ÷ (3 × 1.4 points), on the mean and standard deviation section 3 reports for this series. It is negative because the queue's mean sits above the only limit there is; the "Ppu 0.42" this row used to carry is not derivable from any series in this document* |
| % outside specification (observed) | *100% — all 12 weeks sit above the 8.0% target. The lowest weekly point is above the 11.3% LCL in section 2 and p10 is 12.3% (section 3), so no week is close to it. The "58% of weeks" this row used to carry is not derivable from that series* |
| % outside specification (fitted) | *>99.9% — at a mean of 14.2% and a standard deviation of 1.4 points, the 8.0% target is 4.4 standard deviations below the mean. The "61%" this row used to carry is not derivable from that series* |
| DPU / DPO / DPMO | *0.142 / 0.0284 / 28,400 — a different denominator from the two rows above: these count defective queue tickets against the 5 opportunities each one carries (0.142 ÷ 5 = 0.0284), not weeks against the target* |
| Opportunities per unit (program standard) | *5 — fixed at programme level, never renegotiated mid-project* |
| Z from data (long-term) | *1.90 — read from DPO 0.0284, the opportunity-level rate two rows up, not from the weekly series the index above is computed on* |
| Sigma level (with 1.5σ shift) | *3.40 — 1.90 + 1.5, so on the same opportunity-level denominator* |
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
| *Billing platform release 15.4 — the nightly posting job was rewritten* | *w/c 2026-02-16* | *The posting batch failed silently on two nights; queue reopen rate 18.9% that week, the one point above the UCL in section 2* | *Included. Releases ship every six weeks and this failure mode will recur. Excluding it would flatter the baseline and make the project look smaller than it is* |
| *Tier 1 reorganisation — the billing queue split out of general support; 11 transferred agents shadowed for two weeks* | *2026-03-02 to 2026-03-13* | *74 contacts were closed under the old general-support script rather than the billing closure steps* | *Excluded — those 74 fall outside OD-BIL-004-ADJ, which scopes the project's metric to in-scope billing adjustments. This row makes no claim about the 966 in section 5: until the baseline month those strata were counted over is named, nothing can be said to be net of a fortnight in March. It is a scope exclusion, not a special-cause exclusion: neither week signalled on the chart* |

## 7. Benefit model updated with actual baseline

| Item | Charter estimate | Actual baseline | What it does to the benefit |
|---|---|---|---|
| *Reopen-rate gap to be closed* | *No different estimate to reconcile: the charter carries the same 14.2%, and it names the population — in-scope billing adjustments under OD-BIL-004-ADJ, 137 reopens in 966 contacts (01-project-charter.md:49), split from the whole-queue rate of almost the same name in its metric hierarchy at §5, lines 124 and 125. The "15.0% from the 2025 ops dashboard" that stood in this cell is in no document in the pack* | *14.2% → 8.0%, so 6.2 points, on in-scope billing adjustments (OD-BIL-004-ADJ; 137 reopens in 966 contacts, section 5)* | *The gap does not move. What moves is the population it may be applied to: it was measured on adjustments, so it may only ever be multiplied by adjustments* |
| *In-scope billing-adjustment contacts* | *`<none — the charter states no adjustment volume at all; the "1,100 a month" that stood in this cell is in no document in the pack>`* | *966 a month (section 5), so 11,592 a year — a 12x extrapolation of one measured month, which nobody has yet replaced with a 12-month in-scope pull (01-project-charter.md:47)* | *This is the only benefit denominator. The queue's 266,000 tickets a year (01-project-charter.md:48) is context and is never a multiplier* |
| *Fully loaded cost of a reopened contact* | *$41.00 — an estimate, and stale. It stands in no charter row: the charter's unit-cost row states $38.60 and cites this document for it, and records that the $41.00 is attributed to the charter here rather than stated there (01-project-charter.md:52)* | *$38.60 — Finance's 2026 fully-loaded rate for a reopened contact, with the facilities allocation removed* | *$38.60 is the cost basis of record. The $6.80 that row previously carried, and that the superseded v1.0 chain priced reopens at (01-project-charter.md:52, and :213 in its §11 revision history), is the cost to serve one contact, not the price of a reopen; pricing a reopen at it is the defect* |
| *How the saving is harvested* | *"Headcount reduction", no owner named* | *`<whether any reduction is available, and against which plan — WFM to state the billing queue's approved establishment and its actual headcount at the claim date, before this section is re-signed>`* | *Nothing in the chain below is bookable as cash until a named harvest exists. 18-handover-and-benefit-validation.md:99 names hiring avoidance against the Q1 billing plan as the harvest of record and leaves the number of roles at `<roles removed — not settled>`; the evidence row beneath it (:100 — Headcount plan v4, lines 22-23, signed by WFM 2026-11-08) attests to that plan and to no count of roles. This document has no headcount figure of its own to set against either* |
| *Realization factor* | *0.85 — agreed with Finance at the Define tollgate (01-project-charter.md:54)* | *0.85 — unchanged* | *Applied once, at the end of the chain below* |

**The chain, as arithmetic the reader can follow:**

| Step | Arithmetic | Result |
|---|---|---|
| *In-scope adjustments a year* | *966 a month × 12* | *11,592* |
| *Reopens avoided a year* | *11,592 × 6.2 points* | *719* |
| *Gross benefit* | *719 × $38.60* | *$27,753* |
| *Realized benefit* | *$27,753 × 0.85* | *$23,590* |
| *less the handle time the fix adds* | *`<not measured in this document>`* | *`<blank>`* |

*The chain lands at $23,590, and **that does not clear the $50,000 realized floor Finance sets for a bookable project** (01-project-charter.md:137, the threshold derivation in its §5). It is 47% of the floor, before the handle-time cost below is taken off it. The 6.2 points is the whole of the gap this project is chartered to close, so $23,590 is the ceiling, not a first estimate. Do not round toward the floor and do not reach for a larger population to rescue it — reaching for the queue's 266,000 is precisely the error recorded in section 8.*

*How much handle time the fix adds: `<not measured in this document>`. Verifying the posting before the ticket closes lengthens the contact, and that cost has to come off the $23,590 before any benefit is claimed. R. Okonjo (Tier 1 team lead, and the owner of the AHT scorecard row at 01-project-charter.md:173, §7) and Finance must measure it on the in-scope adjustment population and price it at the same 2026 rate, before this section is re-signed. The charter's "roughly 40 s" (the same row, 01-project-charter.md:173) is an expectation offered at charter time, not a measurement — the charter says so itself at :63-65, and records there that the gage study did not measure it either — and it is not used here.*

## 8. Revision history

> Corrections to a signed baseline are recorded here, not quietly applied. A baseline
> whose errors are invisible cannot be audited, and the error below is the one most
> benefit cases die of.

| Version | Date | What changed, and why |
|---|---|---|
| *v1.0* | *2026-06-05* | *First issue: the 12-week queue control chart (sections 2–4), the 966-contact adjustment stratification (section 5) and the first benefit model (section 7).* |
| *v1.1* | *`<date this revision is signed>`* | *Every reopen rate in this document now names its population. Two different quantities were both being called "the 14.2% 7-day reopen rate": the whole Billing queue under OD-BIL-004 v2 (sections 2–4, context only) and in-scope billing adjustments under OD-BIL-004-ADJ (section 5, 137 reopens in 966 contacts — the project's Y). Both are genuinely measured and both land on 14.2%, which is why the collision went unseen for so long. Neither figure moved.* |
| *v1.1* | *`<same date>`* | *Section 7 rebuilt, and the reason recorded rather than deleted. The chain the pack carried ran 266,000 queue tickets a year × 6.2 points × $6.80 × 0.85 = $95,324 (the charter's v1.0 chain, recorded in its §11 revision history at 01-project-charter.md:213). The arithmetic is exact and the causality is impossible. The fix touches in-scope adjustments only: 11,592 of the 266,000 contacts, 4.4%, and at 14.2% each, 1,646 of the queue's 37,772 reopens — 4.4% again. Fix every adjustment reopen and the queue rate moves from 14.2% to (37,772 − 1,646) ÷ 266,000 = 13.58%, a 0.62-point move. The chain claimed 6.2 points: ten times the arithmetic maximum. The rate was measured on one population and the volume taken from another. Rebuilt on 11,592 adjustments a year at the $38.60 reopen cost, which supersedes the $41.00 estimate, it realizes $23,590 and does not clear the $50,000 floor. The intermediate figures this section used to carry — $425k, $376k, $330k, $310k, $180k and $130k — are not derivable from any measurement in the pack and are struck.* |
| *v1.1* | *`<same date>`* | *"Period covered" restored to 2026-01-05 to 2026-03-29 (12 whole weeks); the dates had been lost from the shipped file. The window is one week short of the 13-week minimum this document itself asks for — flagged in section 1, not fixed, because extending a signed baseline is a Finance/MBB call.* |
| *v1.1* | *`<same date>`* | *Section 1 restored to describing the extract it actually holds. Its metric and operational-definition rows name OD-BIL-004 v2, the whole-queue definition every row of that table is cut on; the job, the record count and the snapshot were always the queue's. The project's Y has no query, no extract date and no snapshot recorded here, and none traced anywhere in the pack (06-data-lineage.md:68), so the snapshot row now carries that blank instead of implying a snapshot exists.* |
| *v1.1* | *`<same date>`* | *Section 4 recomputed against the series it is cut on. Ppu was 0.42 and the out-of-spec rates 58% observed and 61% fitted; on section 3's mean of 14.2% and standard deviation of 1.4 points against the 8.0% target, Ppu is −1.48 and every one of the 12 weeks is above target. DPO, Z and sigma keep their values — 0.142 ÷ 5 = 0.0284 gives Z 1.90 and 3.40 with the shift — and now say which denominator they are on, so the section no longer reads as three rival out-of-spec rates.* |
| *v1.1* | *`<same date>`* | *Two claims struck for want of a measurement. The Tier 1 reorganisation row in section 6 no longer says the 966 is net of the 74 general-support closures: while the baseline month is unnamed, nothing can be said to be net of a fortnight in March. The harvest row in section 7 no longer says the queue is "4 heads below its approved establishment", and no longer reads two billing roles and a WFM signature of 2026-11-08 into 18-handover-and-benefit-validation.md — no establishment or headcount figure exists anywhere in the pack, that document leaves the role count at `<roles removed — not settled>` (:99), and its 2026-11-08 signature attests to Headcount plan v4, lines 22-23 (:100), not to a number of roles.* |
| *v1.1* | *`<same date>`* | *Every cross-file citation in this document re-read against the file it points at and corrected where the target had moved: 01-project-charter.md:49 with :124 and :125 for the baseline and its two populations, :48 for the queue volume, :52 for the unit cost, :54 for the realization factor, :137 for the Finance floor, :173 with :63-65 for R. Okonjo and the "roughly 40 s", :213 for the superseded v1.0 chain. Each is given with the charter section it sits in as well, because the line numbers move when that file is revised. The realization-factor row was moved below the harvest row so the harvest statement stays on the line the rest of the pack cites it by.* |

## Sign-off

**v1.0 — signed at the Measure tollgate.** These four signatures attest to the document as
first issued: the queue control chart, the stratification and the v1.0 benefit model. They do
not attest to anything v1.1 changed, and in particular not to section 7.

| Role | Name | Signature | Date |
|---|---|---|---|
| Black Belt | *M. Berenji* |  | *2026-06-05* |
| Process owner | *A. Okafor* |  | *2026-06-05* |
| **Finance partner** | *J. Lindqvist* |  | *2026-06-08* |
| Master Black Belt | *S. Iyer* |  | *2026-06-08* |

**v1.1 — not yet signed.** Section 7 has been rebuilt and still carries blanks, in it and in
the sections it draws on. Nothing in section 7 is a signed baseline figure until those blanks
are filled and the four roles below sign again.

| Role | Name | Signature | Date |
|---|---|---|---|
| Black Belt | *M. Berenji* |  | *`<date v1.1 is signed>`* |
| Process owner | *A. Okafor* |  | *`<date v1.1 is signed>`* |
| **Finance partner** | *J. Lindqvist* |  | *`<date v1.1 is signed>`* |
| Master Black Belt | *S. Iyer* |  | *`<date v1.1 is signed>`* |
