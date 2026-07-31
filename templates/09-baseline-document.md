# Baseline — <Primary metric>

**This document is the zero point for the benefit clock. Finance signs it.**

## 1. Extract

| Field | Value |
|---|---|
| Metric | |
| Operational definition ref | |
| Period covered | (minimum 13 weeks; 12 months preferred) |
| Records (n) | |
| Extract date | |
| Extract query / job ref | |
| Immutable snapshot stored at | |

## 2. Stability

| Field | Value |
|---|---|
| Chart type used | (I-MR / X̄-S / Laney p′ / Laney u′) |
| Chart type justification | |
| Centre line | |
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
