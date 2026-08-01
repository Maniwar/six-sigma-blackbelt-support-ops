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
| | | | |

## 6. Context and caveats

| Event in the baseline window | Dates | Effect | Included or excluded |
|---|---|---|---|
| | | | |

## 7. Benefit model updated with actual baseline

| Item | Charter estimate | Actual baseline | Revised benefit |
|---|---|---|---|
| | | | |

## Sign-off

| Role | Name | Signature | Date |
|---|---|---|---|
| Black Belt | *M. Berenji* |  | *2026-06-05* |
| Process owner | *A. Okafor* |  | *2026-06-05* |
| **Finance partner** | *J. Lindqvist* |  | *2026-06-08* |
| Master Black Belt | *S. Iyer* |  | *2026-06-08* |
