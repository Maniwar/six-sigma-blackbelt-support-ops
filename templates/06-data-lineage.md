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
| *Ops weekly reopen tile (Looker), the number quoted in the Monday stand-up* | *Reopens where the reopen reason matches the original reason ÷ billing tickets resolved, chat excluded* | *12.4% (1–31 Mar)* | *Two filters nobody remembers switching on: same-reason only, so the handset chaser after a billing credit vanishes, and a legacy channel filter that drops chat entirely. Together they take 1.8 points off* |
| *Finance monthly pack, billing adjustments annex* | *Accounts with more than one adjustment posted in the calendar month ÷ accounts with any adjustment posted* | *17.1% (March posting month)* | *Counts accounts and calendar months, not tickets and rolling 7 days. A customer with two unrelated adjustments three weeks apart reads as a reopen, and a reopen that crosses into April is lost at the month boundary* |
| *This project's query, OD-BIL-004 v2 (warehouse.reopen_daily)* | *Tickets with any reopen event 0 < t <= 168h after first Resolved ÷ all billing tickets reaching Resolved in the window* | *14.2% (1–31 Mar)* | *The agreed definition: any reason, all channels, 7 days rolling from each ticket's own Resolved timestamp. This is the one the baseline is cut on; the other two are reported, not defined* |

## Findings and remediation

| Finding | Severity | Effect on baseline | Action | Owner | Status |
|---|---|---|---|---|---|
| *Merged tickets collapse to the survivor at hop 3 and the merged child's reopen event is dropped with it* | *High* | *Restored 21 reopens to March; the baseline was recut from 13.9% to the 14.2% now on the charter* | *Carry reopen events from the merged child onto the survivor in stg_tickets, then restate the last three months* | *Data Eng* | *Closed 2026-05-06, baseline recut and re-signed* |
| *A legacy channel filter on the Looker tile (hop 6) drops chat entirely* | *High* | *Understates the reopen rate by about 0.4 points and hides the channel with the shortest handle time* | *Delete the filter and rebuild the tile straight off warehouse.reopen_daily; backfill the channel field first* | *Ops Insights* | *Open, target 12 Jun — the tile still reads 12.4% until it lands* |
| *resolved_at is written in the agent's browser local time at hop 1 and only converted to UTC at hop 2* | *Medium* | *No material change to the monthly rate, but tickets resolved between 23:00 and 01:00 land on the wrong day, which puts false points on the daily control chart* | *Capture the agent's timezone on the event itself and stop inferring it at replication* | *Support Ops* | *Open, sized at 3 days, in the June sprint* |
| *Test tickets are filtered on requester domain only (hop 4), so QA tickets raised from personal addresses survive into the population* | *Low* | *About 15 tickets too many in the March denominator, worth roughly 0.2 points downward* | *Filter on the QA ticket tag as well as the domain, and make the tag mandatory on the internal form* | *Analytics* | *Open, accepted 3 Jun, no date yet* |

Traced by: ____________  Date: __________
Confirmed by data owner: ____________  Date: __________
