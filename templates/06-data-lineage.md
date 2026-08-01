# Data Lineage — <Primary metric>

<!-- guidance -->
## How to use this

**What it is for.** Traces every number back to the system that generated it, through every transformation on the way.

**When.** Measure, alongside the operational definition.

**Who signs it.** Black Belt · signed with the data engineer who owns the pipeline

**The mistake this prevents.** Trusting a dashboard. A dashboard is the end of a lineage, not the start of one — and the transformation that quietly excludes abandoned contacts is always three joins upstream of the tile you were looking at. The second mistake it prevents: two queries that return the same number are not returning the same quantity. Record the population beside every rate, or a benefit model will eventually multiply one population's rate by another population's volume.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate on in-scope billing adjustments (OD-BIL-004-ADJ; 137 reopens / 966 contacts in the baseline month, templates/09-baseline-document.md:90) against a target of 8%. The whole Billing queue reads 14.2% as well, under a different definition on a different population — see "Competing definitions" below. Delete them as you fill your own in.*

---

**Purpose:** trace one record from the event that created it to the number on the
dashboard. Roughly a third of projects find a defect here that materially changes
the baseline.

## Hop-by-hop trace

| # | Stage | System / object | Transformation, join or filter applied | Business rule | Owner | Refresh | Known gap |
|---|---|---|---|---|---|---|---|
| 1 | Event capture | *Zendesk UI* | *Agent clicks Resolved* | *None — the UI writes the timestamp as the browser gives it* | *Support Ops* | *Real time* | *resolved_at is browser local time, converted only at hop 2* |
| 2 | Source table | *zendesk.tickets* | *Hourly copy, no transformation* | *None* | *Data Eng* | *Hourly* | *None recorded* |
| 3 | Ingest / ETL | *stg_tickets (dbt)* | *Merged tickets collapsed to the survivor* | *A merged ticket keeps the survivor's timestamps* | *Data Eng* | *02:00* | *The merged child's reopen event is dropped with it* |
| 4 | Warehouse model | *warehouse.tickets* | *Test tickets filtered on requester domain* | *Internal domains excluded* | *Data Eng* | *02:40* | *QA tickets raised from personal addresses survive the filter* |
| 5 | Semantic layer / metric definition | *warehouse.reopen_daily* | *Reopen flagged where reopened_at - resolved_at <= 168h* | *First Resolved only; the model builds OD-BIL-004 v2 — 7-day reopen rate, all billing tickets* | *Analytics* | *03:10* | *The model carries no adjustment scope, so OD-BIL-004-ADJ, the project's Y, is not built here* |
| 6 | Dashboard / report | *Looker: Ops weekly reopen* | *Filters to billing contact reasons — still the whole queue, not the in-scope adjustments* | *Chat excluded by a legacy filter* | *Ops Insights* | *06:00* | *The chat filter drops a channel entirely; the tile reads 12.4%, not the 14.2% at hop 5* |

## Single-record walkthrough

| Stage | Value at this stage | Matches previous? | If not, why |
|---|---|---|---|
| Event capture | *Agent clicks Resolved* | — | *Zendesk UI* |
| Source table | *zendesk.tickets* | *replicated hourly* | *timezone converted to UTC here* |
| ETL output | *stg_tickets* | *dbt run 02:00* | *merged tickets collapsed to the survivor* |
| Warehouse | *warehouse.tickets* | *02:40* | *test tickets filtered on requester domain* |
| Dashboard | *Ops weekly reopen tile* | *Looker* | *filters to billing reasons only — the whole queue, not the adjustment scope* |

## Competing definitions in circulation
Support organizations routinely have several figures called the same thing. Two of the
four rows below read 14.2%, and they are not the same 14.2%: one is the whole Billing
queue, the other is the in-scope adjustment population. Name the population in the row,
never just the rate.

The first three rows are cut on the same calendar month (1–31 Mar), and that is all they share:
no two of the four denominators below are the same population — billing tickets with chat
excluded, accounts with an adjustment posted, all billing tickets, in-scope adjustment contacts.
March is a comparison cut, not a baseline window: the queue baseline is 12 weeks and 61,400 tickets
(templates/09-baseline-document.md:51), and the fourth row's baseline month of 966 contacts
(templates/09-baseline-document.md:90) is a different span again. Name the population and the span.

| Where it appears | Formula actually used | Value, and the period it is cut on | Differs because |
|---|---|---|---|
| *Ops weekly reopen tile (Looker), the number quoted in the Monday stand-up* | *Reopens where the reopen reason matches the original reason ÷ billing tickets resolved, chat excluded* | *12.4% (1–31 Mar)* | *Two filters nobody remembers switching on: same-reason only, so the handset chaser after a billing credit vanishes, and a legacy channel filter that drops chat entirely. Together they take 1.8 points off the OD-BIL-004 v2 all-billing-tickets rate of 14.2%* |
| *Finance monthly pack, billing adjustments annex* | *Accounts with more than one adjustment posted in the calendar month ÷ accounts with any adjustment posted* | *17.1% (March posting month)* | *Counts accounts and calendar months, not tickets and rolling 7 days. A customer with two unrelated adjustments three weeks apart reads as a reopen, and a reopen that crosses into April is lost at the month boundary* |
| *OD-BIL-004 v2 — 7-day reopen rate, all billing tickets (warehouse.reopen_daily, built at hop 5 of the trace above. The trace does not stop there: it runs on to the Looker tile at hop 6, which is the first row of this table and reads 12.4%)* | *Tickets with any reopen event 0 < t <= 168h after first Resolved ÷ all billing tickets reaching Resolved in the window* | *14.2% (1–31 Mar)* | *The agreed queue definition: any reason, all channels, 7 days rolling from each ticket's own Resolved timestamp. It is the one the queue baseline is cut on, and for this project it is CONTEXT only — it is never a benefit denominator. It is not the project's Y; that is the row below* |
| *OD-BIL-004-ADJ — 7-day reopen rate, in-scope billing adjustments. The project's Y, and the only rate a benefit may be built on. No query for it is traced in this document* | *Reopen events 0 < t <= 168h after first Resolved ÷ in-scope adjustment contacts — consumer accounts, voice/chat/email, sites A–D, up to the $250 Billing Ops limit, excluding fraud holds, collections, manual refund cheques, enterprise accounts and proactive credits (the in-scope and out-of-scope lists in templates/02-sipoc.md)* | *14.2% — 137 reopens / 966 contacts (templates/09-baseline-document.md:90), one baseline month; `<start and end dates of the month the 966 were counted over — not recorded anywhere in the pack. A. Okafor, process owner, who signed the baseline, must state it (templates/09-baseline-document.md:90) before the 90-day checkpoint on 2027-02-12 (templates/18-handover-and-benefit-validation.md:142)>`* | *A different population, not a different formula. It lands on the same 14.2% as the queue rate by coincidence, which is exactly why the two were multiplied together. 966 contacts a month is 11,592 a year; the queue's 266,000 a year (the charter's billing-queue volume row) is context and never the denominator for this rate* |

## Findings and remediation

| Finding | Severity | Effect on baseline | Action | Owner | Status |
|---|---|---|---|---|---|
| *Two different quantities are both called "the 14.2% 7-day reopen rate": OD-BIL-004 v2 on all billing tickets (built at hop 5) and OD-BIL-004-ADJ on in-scope billing adjustments (built by a query this lineage does not trace). The benefit model took its rate gap from the adjustment population and its volume from the queue* | *High* | *Neither measured rate moves — both were correctly measured, on different populations. What moves is everything derived from them. The adjustment population is 966 a month (templates/09-baseline-document.md:90), so 11,592 a year, against the queue's 266,000 a year (the charter's billing-queue volume row, context only): 4.4% of contacts. At 14.2% each, that is 1,646 adjustment reopens against 37,772 queue reopens — 4.4% again. Closing EVERY adjustment reopen therefore moves the queue rate from 14.2% to (37,772 - 1,646) ÷ 266,000 = 13.58%, a 0.62-point move. The old chain claimed the full 6.2-point gap (templates/09-baseline-document.md:105) against the queue's 266,000 — ten times the arithmetic maximum* | *Name the population in every metric, scope, operational-definition and CTQ row; register OD-BIL-004-ADJ as its own operational definition; rebuild the benefit on the 11,592 adjustments a year and on nothing else (that figure is one measured month x 12, and the charter's benefit-denominator row records that nobody has yet pulled a 12-month in-scope count), shown as arithmetic: 11,592 x 6.2 points = 719 reopens avoided; 719 x $38.60 (Finance's 2026 fully-loaded cost of a reopened contact, templates/09-baseline-document.md:107) = $27,753 gross; x 0.85 realization (the charter's realization-factor row) = $23,590 realized, less the handle time the fix adds — `<added handle time per in-scope adjustment, and its annual cost. This document measures none and no measured figure exists in the pack; R. Okonjo, Tier 1 team lead, and Finance must measure it on the in-scope adjustment population and price it at the same 2026 rate (templates/09-baseline-document.md:123), before the 90-day checkpoint on 2027-02-12 (templates/18-handover-and-benefit-validation.md:142)>`. $23,590 does not clear Finance's $50,000 floor (the charter's benefit-floor note), and the project must say so plainly rather than reach for a bigger population to rescue it. The finding is recorded, not deleted, in the baseline document's revision table and the charter's revision history* | *Analytics · Black Belt* | *Open — `<target date>`, to be set at the next tollgate* |
| *OD-BIL-004-ADJ, the project's Y, has no lineage at all: no hop, no walkthrough, no owner, no refresh. The 137 / 966 cut at templates/09-baseline-document.md:90 came from a query nobody has traced* | *High* | *No change to any figure, but the project's own metric is unaudited end to end. Every defect below was found on the queue pipeline and none of them has been checked against the adjustment cut* | *Trace the adjustment query hop by hop into the table above, then re-run the merged-ticket, chat-filter and QA-tag remediations against it* | *Analytics · Data Eng* | *Open — `<target date>`* |
| *Merged tickets collapse to the survivor at hop 3 and the merged child's reopen event is dropped with it* | *High* | *The queue cut was restated once the fix landed, but by how much is recorded nowhere: the "21 reopens restored" and the 13.9% → 14.2% move this row used to carry are sourced nowhere else in the pack, and they do not fit each other — 21 reopens moves a March queue of roughly 22,000 tickets (266,000 a year ÷ 12, the charter's billing-queue volume row) by under 0.1 points, not 0.3. The pack's only other 0.3-point move between 14.2% and 13.9% belongs to a different cause on a different population — repeat disputers, on OD-BIL-004-ADJ (templates/14-root-cause-evidence-pack.md) — so this row should not be read as corroborating it. So `<reopens restored to the March queue cut, and the move in the all-billing-tickets rate they produce>` and `<how many of them fall inside the in-scope adjustment population>` — Data Eng to state both off the restated stg_tickets, before the 90-day checkpoint on 2027-02-12 (templates/18-handover-and-benefit-validation.md:142). Until they do, OD-BIL-004-ADJ has never been restated for this* | *Carry reopen events from the merged child onto the survivor in stg_tickets, then restate the last three months — for the adjustment cut as well as the queue cut* | *Data Eng* | *Pipeline fix closed 2026-05-06 and the queue baseline re-signed; the restatement figures above and the adjustment cut are open* |
| *A legacy channel filter on the Looker tile (hop 6) drops chat entirely* | *High* | *Understates the all-billing-tickets reopen rate by about 0.4 points of the 1.8 the tile is out by, and hides the channel with the shortest handle time* | *Delete the filter and rebuild the tile straight off warehouse.reopen_daily; backfill the channel field first* | *Ops Insights* | *Open, target 12 Jun — the tile still reads 12.4% until it lands* |
| *resolved_at is written in the agent's browser local time at hop 1 and only converted to UTC at hop 2* | *Medium* | *No material change to the monthly rate, but tickets resolved between 23:00 and 01:00 land on the wrong day, which puts false points on the daily control chart* | *Capture the agent's timezone on the event itself and stop inferring it at replication* | *Support Ops* | *Open, sized at 3 days, in the June sprint* |
| *Test tickets are filtered on requester domain only (hop 4), so QA tickets raised from personal addresses survive into the population* | *Low* | *About 15 tickets too many in the March cut. Which population they were counted on is recorded nowhere in the pack, and the 0.2 points previously recorded here is the reason to doubt the obvious answer: 0.2 points off 14.2% needs a denominator near 1,000, which is adjustment scale, not a month of the whole queue — so the count and its effect cannot both belong to the same population. `<which population the 15 were counted on>`, `<effect on the all-billing-tickets rate, recomputed against the March queue denominator>` and `<effect on OD-BIL-004-ADJ, if any of the 15 are in scope>` — Analytics to state all three before the 90-day checkpoint on 2027-02-12 (templates/18-handover-and-benefit-validation.md:142)* | *Filter on the QA ticket tag as well as the domain, and make the tag mandatory on the internal form* | *Analytics* | *Open, accepted 3 Jun — due before the 90-day checkpoint on 2027-02-12* |

Traced by: ____________  Date: __________
Confirmed by data owner: ____________  Date: __________
