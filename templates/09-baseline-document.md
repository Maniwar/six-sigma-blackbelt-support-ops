# Baseline — <Primary metric>

<!-- guidance -->
## How to use this

**What it is for.** The number the project is judged against, with the evidence that it is stable enough to be judged against.

**When.** End of Measure. This is the tollgate.

**Who signs it.** Black Belt · Champion and Finance both sign the baseline value

**The mistake this prevents.** Baselining an unstable process. If the control chart is signalling, the mean is not a number — it is an average of two different processes, and any improvement you claim against it is unfalsifiable.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate against a target of 8%. Delete them as you fill your own in.*

---

**This document is the zero point for the benefit clock. Finance signs it.**

## 1. Extract

| Field | Value |
|---|---|
| Metric | *7-day reopen rate, billing adjustments* |
| Operational definition ref | *OD-BIL-004 v2* |
| Period covered | (minimum 13 weeks; 12 months preferred) |
| Records (n) | *61,400 billing tickets* |
| Extract date | *2026-04-02* |
| Extract query / job ref | *warehouse job bl_reopen_baseline, commit 4f2a9c1* |
| Immutable snapshot stored at | *s3://analytics-snapshots/BIL-2026-014/baseline.parquet* |

## 2. Stability

| Field | Value |
|---|---|
| Chart type used | (I-MR / X̄-S / Laney p′ / Laney u′) |
| Chart type justification | *Proportion at ~5,100 tickets/week; sigma z = 4.25, so an ordinary p-chart would signal on almost every point* |
| Centre line | *14.2%* |
| UCL / LCL | *17.1% / 11.3%* |
| σ_z (if attribute chart) | (near 1.0 = no overdispersion; >1.2 = use Laney) |
| Special causes found | *One week (w/c 2026-02-16) above the UCL — a billing platform release* |
| Special causes excluded (and why) | *None excluded. The release is a real process condition and will recur.* |
| **Process stable?** | Yes / No |

> Capability is meaningless on an unstable process. Demonstrate stability first.

## 3. Distribution

| Statistic | Value |
|---|---|
| n | *61,400 tickets over the 12-week window (~5,100/week)* |
| Mean | *14.2%* |
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
| Index justification | *Ppu — only an upper limit exists (target is a maximum)* |
| Transformation applied | (none / Box-Cox λ = ___ / Johnson / fitted lognormal) |
| **Capability index value** | *Ppu 0.42* |
| % outside specification (observed) | *58% of weeks above the 8.0% target* |
| % outside specification (fitted) | *61%* |
| DPU / DPO / DPMO | *0.142 / 0.0284 / 28,400* |
| Opportunities per unit (program standard) | *5 — fixed at programme level, never renegotiated mid-project* |
| Z from data (long-term) | *1.90* |
| Sigma level (with 1.5σ shift) | *3.40* |
| Rolled throughput yield across tiers | *55.6% — first-pass yield compounds badly across four steps* |

## 5. Stratified baseline

| Stratum | n | Metric value | Share of total gap |
|---|---|---|---|
| *Raised before 17:00, under $50 — agent approves it, catches the same night's 02:00 batch* | *402* | *7.5% (30 reopens)* | *None — 2 reopens below the 8% target* |
| *Raised after 17:00, under $50 — misses the batch by one night* | *214* | *18.7% (40 reopens)* | *37% of the 60-reopen gap* |
| *Over $50, raised before 17:00 — needs a Billing Ops check first* | *168* | *14.3% (24 reopens)* | *17%* |
| *Over $50, raised after 17:00 — waits for the next Billing Ops run, then the next batch* | *121* | *24.8% (30 reopens)* | *33%* |
| *Multi-line accounts — the adjustment splits across lines and posts partially* | *61* | *21.3% (13 reopens)* | *13%* |
| *All strata (check: 966 contacts, 137 reopens, 14.2%; the gap to 8% is 60 reopens)* | *966* | *14.2%* | *100%* |

## 6. Context and caveats

| Event in the baseline window | Dates | Effect | Included or excluded |
|---|---|---|---|
| *Annual price letters land with the January bill — the seasonal disputes peak* | *2026-01-05 to 2026-01-30* | *Busiest weeks in the window, ~6,400 tickets/week against a ~5,100 average; reopen rate 14.6%, inside the control limits* | *Included. It happens every January, and the post-project comparison has to span the same season or it will read the calendar as an improvement* |
| *List price change on the mid-tier broadband plan* | *2026-02-01* | *Disputed-charge volume up ~18% for three weeks; reopen rate flat at 13.9% — the change moved the denominator, not the process* | *Included. Pricing changes are a standing feature of the business; the baselined metric is a rate, so volume alone does not distort it* |
| *Billing platform release 15.4 — the nightly posting job was rewritten* | *w/c 2026-02-16* | *The posting batch failed silently on two nights; reopen rate 18.9% that week, the one point above the UCL in section 2* | *Included. Releases ship every six weeks and this failure mode will recur. Excluding it would flatter the baseline and make the project look smaller than it is* |
| *Tier 1 reorganisation — the billing queue split out of general support; 11 transferred agents shadowed for two weeks* | *2026-03-02 to 2026-03-13* | *74 contacts were closed under the old general-support script rather than the billing closure steps* | *Excluded — those 74 fall outside OD-BIL-004 v2, which scopes the metric to the billing queue, and the 966 in section 5 is net of them. This is a scope exclusion, not a special-cause exclusion: neither week signalled on the chart* |

## 7. Benefit model updated with actual baseline

| Item | Charter estimate | Actual baseline | Revised benefit |
|---|---|---|---|
| *Reopen-rate gap to be closed* | *15.0% → 8.0%, so 7.0 points (2025 ops dashboard)* | *14.2% → 8.0%, so 6.2 points (12-week control chart centre line)* | *Charter's $425k/yr gross drops to $376k — the gap is 11% smaller than assumed* |
| *Billing-adjustment contacts per month* | *1,100* | *966 — the dashboard counted a contact twice whenever it was transferred between queues* | *$376k drops to $330k* |
| *Fully loaded cost of a reopened contact* | *$41.00* | *$38.60 — Finance's 2026 rate, with the facilities allocation removed* | *$330k drops to $310k/yr — the gross benefit of record* |
| *How the saving is harvested* | *"Headcount reduction", no owner named* | *No reduction is available: the billing queue is already 4 heads below its approved establishment* | *$180k/yr Finance-validated, booked as hiring avoidance and signed by WFM. The remaining $130k returns as capacity against service levels, not as cash* |

## Sign-off

| Role | Name | Signature | Date |
|---|---|---|---|
| Black Belt | *M. Berenji* |  | *2026-06-05* |
| Process owner | *A. Okafor* |  | *2026-06-05* |
| **Finance partner** | *J. Lindqvist* |  | *2026-06-08* |
| Master Black Belt | *S. Iyer* |  | *2026-06-08* |
