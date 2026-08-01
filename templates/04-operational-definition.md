# Operational Definition — <Metric name>

<!-- guidance -->
## How to use this

**What it is for.** One page per metric, precise enough that two analysts working independently get the same number.

**When.** Measure, before the baseline. If this is not agreed, the baseline is an opinion.

**Who signs it.** Black Belt writes · Process owner and the data owner both sign

**The mistake this prevents.** Definitions that agree in principle and differ in the SQL. The test at the bottom is not optional — two people, same window, same answer, or it is not operational.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate against a target of 8%. Delete them as you fill your own in.*

---

| Field | Content |
|---|---|
| **Metric name** | *7-day reopen rate, billing adjustments* |
| **Plain-language description** | *Share of resolved billing tickets the customer reopens within 7 days* |
| **What is counted (numerator)** | *Tickets with a reopen event 0<t<=168h after first Resolved* |
| **Denominator / population** | *All billing tickets reaching Resolved in the window* |
| **Time window** | *Rolling 7 days from each ticket's first Resolved timestamp* |
| **Unit of analysis** | contact / issue / ticket / customer / agent-day |
| **Inclusions** | *All channels; all billing contact reasons; all tiers* |
| **Exclusions** | *Tickets merged into another; test/QA tickets; bot-only deflections* |
| **Stratification fields available** | *Contact reason, agent tenure band, site, channel* |
| **Source system(s)** | *Zendesk (tickets), billing platform (postings)* |
| **Source tables / fields** | *warehouse.tickets.resolved_at, warehouse.ticket_events.reopened_at* |
| **Business rules applied** | *First Resolved only; a second reopen does not double-count* |
| **Refresh cadence** | *Nightly, 02:00 UTC; restated for 3 days as late events land* |
| **Metric is final at** | T + ___ |
| **Owner** | *A. Okafor, Billing Ops Manager — owns the definition, not just the number* |
| **Known limitations** | *Excludes chat until the channel field is backfilled; understates by roughly 0.4 points* |
| **Related metrics it must reconcile with** | *Contact rate (same denominator) and the Ops weekly reopen tile (currently 1.8 pts apart — see the lineage doc)* |

## Worked example
> Show one real record and how it is classified.

| Record ID | Field values | Counted? | Why |
|---|---|---|---|
| | | | |

## Two-observer test
Two people independently applied this definition to the same 20 records.

| | Result |
|---|---|
| Agreement | ___ / 20 |
| Disagreements and resolution | *Reporting counted same-reason reopens only; operations wanted any-reason. Resolved 2026-04-24 in favour of any-reason, and the baseline was recut.* |
| Definition revised? | Yes / No |

Reviewed by: ____________  Date: __________
