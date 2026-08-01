# Data Lineage — <Primary metric>

<!-- guidance -->
## How to use this

**What it is for.** Traces every number back to the system that generated it, through every transformation on the way.

**When.** Measure, alongside the operational definition.

**Who signs it.** Black Belt · signed with the data engineer who owns the pipeline

**The mistake this prevents.** Trusting a dashboard. A dashboard is the end of a lineage, not the start of one — and the transformation that quietly excludes abandoned contacts is always three joins upstream of the tile you were looking at.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate against a target of 8%. Delete them as you fill your own in.*

---

**Purpose:** trace one record from the event that created it to the number on the
dashboard. Roughly a third of projects find a defect here that materially changes
the baseline.

## Hop-by-hop trace

| # | Stage | System / object | Transformation, join or filter applied | Business rule | Owner | Refresh | Known gap |
|---|---|---|---|---|---|---|---|
| 1 | Event capture | *Event capture* | *Zendesk UI* | *Agent clicks Resolved* | *resolved_at is browser local time* | *Support Ops* | *Real time* |
| 2 | Source table | *Replication* | *zendesk.tickets* | *Hourly copy, no transformation* | *None* | *Data Eng* | *Hourly* |
| 3 | Ingest / ETL | *Staging* | *stg_tickets (dbt)* | *Merged tickets collapsed to the survivor* | *A merged ticket keeps the survivor's timestamps* | *Data Eng* | *02:00* |
| 4 | Warehouse model | *Warehouse* | *warehouse.tickets* | *Test tickets filtered on requester domain* | *Internal domains excluded* | *Data Eng* | *02:40* |
| 5 | Semantic layer / metric definition | *Metric build* | *warehouse.reopen_daily* | *Reopen flagged where reopened_at - resolved_at <= 168h* | *First Resolved only* | *Analytics* | *03:10* |
| 6 | Dashboard / report | *Dashboard* | *Looker: Ops weekly reopen* | *Filters to billing contact reasons* | *Chat excluded by a legacy filter* | *Ops Insights* | *06:00* |

## Single-record walkthrough

| Stage | Value at this stage | Matches previous? | If not, why |
|---|---|---|---|
| Event capture | *Agent clicks Resolved* | — | *Zendesk UI* |
| Source table | *zendesk.tickets* | *replicated hourly* | *timezone converted to UTC here* |
| ETL output | *stg_tickets* | *dbt run 02:00* | *merged tickets collapsed to the survivor* |
| Warehouse | *warehouse.tickets* | *02:40* | *test tickets filtered on requester domain* |
| Dashboard | *Ops weekly reopen tile* | *Looker* | *filters to billing reasons only* |

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
