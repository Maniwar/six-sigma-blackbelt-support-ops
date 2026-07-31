# Data Lineage — <Primary metric>

**Purpose:** trace one record from the event that created it to the number on the
dashboard. Roughly a third of projects find a defect here that materially changes
the baseline.

## Hop-by-hop trace

| # | Stage | System / object | Transformation, join or filter applied | Business rule | Owner | Refresh | Known gap |
|---|---|---|---|---|---|---|---|
| 1 | Event capture | | | | | | |
| 2 | Source table | | | | | | |
| 3 | Ingest / ETL | | | | | | |
| 4 | Warehouse model | | | | | | |
| 5 | Semantic layer / metric definition | | | | | | |
| 6 | Dashboard / report | | | | | | |

## Single-record walkthrough

| Stage | Value at this stage | Matches previous? | If not, why |
|---|---|---|---|
| Event capture | | — | |
| Source table | | | |
| ETL output | | | |
| Warehouse | | | |
| Dashboard | | | |

## Competing definitions in circulation
Support organizations routinely have several figures called the same thing.

| Where it appears | Formula actually used | Value for the same period | Differs because |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

## Findings and remediation

| Finding | Severity | Effect on baseline | Action | Owner | Status |
|---|---|---|---|---|---|
| | | | | | |

Traced by: ____________  Date: __________
Confirmed by data owner: ____________  Date: __________
