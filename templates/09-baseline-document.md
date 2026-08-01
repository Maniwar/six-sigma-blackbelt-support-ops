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
| UCL / LCL | |
| σ_z (if attribute chart) | (near 1.0 = no overdispersion; >1.2 = use Laney) |
| Special causes found | |
| Special causes excluded (and why) | |
| **Process stable?** | Yes / No |

> Capability is meaningless on an unstable process. Demonstrate stability first.

## 3. Distribution

| Statistic | Value |
|---|---|
| n | |
| Mean | |
| **Median** | |
| Standard deviation | |
| p10 / p50 / p90 / p95 | |
| Skewness | |
| Distribution shape | |
| Normality assessment (probability plot, not just the p-value) | |
| Bimodality present? If so, resolved by stratifying on | |

> For any duration metric, report median and p90 — never the mean alone. The customers
> who suffer are in the tail, and the mean hides them.

## 4. Capability

| Field | Value |
|---|---|
| Specification | USL = ___ / LSL = ___ (support specs are usually one-sided) |
| Index used | Ppu / Ppl / Ppk / binomial capability |
| Index justification | |
| Transformation applied | (none / Box-Cox λ = ___ / Johnson / fitted lognormal) |
| **Capability index value** | |
| % outside specification (observed) | |
| % outside specification (fitted) | |
| DPU / DPO / DPMO | |
| Opportunities per unit (program standard) | |
| Z from data (long-term) | |
| Sigma level (with 1.5σ shift) | |
| Rolled throughput yield across tiers | |

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
| Black Belt | | | |
| Process owner | | | |
| **Finance partner** | | | |
| Master Black Belt | | | |
