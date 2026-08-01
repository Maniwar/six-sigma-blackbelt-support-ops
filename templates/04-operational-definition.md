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
| *TCK-118204* | *First Resolved 4 Mar 09:12. Reopened 12 Mar 08:40 — 191 hours later, same customer, same unposted credit* | *No (numerator); yes (denominator)* | *The window is 168 hours from first Resolved and this misses it by a day. It is the same failure and it still stings, but a rolling 7-day metric that quietly stretches to 8 days is no longer the metric two people agreed on. It stays in the denominator as a resolved billing ticket* |
| *TCK-118377* | *Credit posted correctly on 9 Mar. Reopened 11 Mar because the replacement handset had not arrived — nothing to do with billing* | *Yes* | *Any-reason reopen. Reporting wanted same-reason only; that disagreement was settled on 2026-04-24 in favour of any reason, because the customer experiences one contact, not a reason code. Excluded from the numerator only if the ticket is re-tagged out of the billing population altogether* |
| *TCK-118391 / TCK-118392* | *Same customer emails at 14:02 and calls at 14:41 about the same disputed charge. Neither ticket had reached Resolved. 118392 merged into 118391 at 15:10* | *No — counted once, as one ticket* | *This is a duplicate contact, not a reopen: a reopen is measured from first Resolved and there was no first Resolved yet. The merge collapses 118392 into the survivor, which keeps 118391's timestamps, so the pair contributes one row to the denominator and nothing to the numerator* |
| *TCK-118412* | *Resolved 17 Mar, reopened 18 Mar, resolved again 19 Mar, reopened again 22 Mar. Both reopens inside 168 hours of the first Resolved* | *Yes — once* | *First Resolved only, and a second reopen does not double-count. The ticket is one defective outcome however many times it bounces; counting it twice would let a single badly handled account move the rate. The second reopen is kept as a severity flag, not as a second defect* |
| *TCK-118455* | *Resolved 20 Mar 16:48. Reopened 21 Mar 02:14 by the batch service account after the nightly posting failed. No customer contact before or since* | *No* | *The metric says the customer reopens it, and this customer never did — the system noticed first, which is the behaviour we want. Counting it would mix the failure with its own early warning. Tracked separately as a posting failure so the fix still sees it, and if auto-reopen ever notifies the customer this record class comes back in* |

## Two-observer test
Two people independently applied this definition to the same 20 records.

| | Result |
|---|---|
| Agreement | ___ / 20 |
| Disagreements and resolution | *Reporting counted same-reason reopens only; operations wanted any-reason. Resolved 2026-04-24 in favour of any-reason, and the baseline was recut.* |
| Definition revised? | Yes / No |

Reviewed by: ____________  Date: __________
