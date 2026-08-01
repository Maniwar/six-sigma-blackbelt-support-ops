# Operational Definition — <Metric name>

<!-- guidance -->
## How to use this

**What it is for.** One page per metric, precise enough that two analysts working independently get the same number.

**When.** Measure, before the baseline. If this is not agreed, the baseline is an opinion.

**Who signs it.** Black Belt writes · Process owner and the data owner both sign

**The mistake this prevents.** Definitions that agree in principle and differ in the SQL. The test at the bottom is not optional — two people, same window, same answer, or it is not operational.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate on in-scope billing adjustments (OD-BIL-004-ADJ; 137 reopens / 966 contacts in the baseline month, templates/09-baseline-document.md:90) against a target of 8%. Delete them as you fill your own in.*

*Read the metric name below before anything else. The whole Billing queue also runs a 14.2% 7-day reopen rate, under a different definition on a different population — OD-BIL-004 v2, templates/06-data-lineage.md:50. Two populations, two definitions, the same number, and that is precisely how this project's first benefit case came to multiply one population's rate by another population's volume. Every row on this page names which of the two it means. So must yours.*

---

| Field | Content |
|---|---|
| **Metric name** | *7-day reopen rate, in-scope billing adjustments — OD-BIL-004-ADJ. A new definition and a different quantity from OD-BIL-004 v2, which runs the same 168-hour rule over the whole Billing queue. A bare "14.2% reopen rate" names neither and is the defect this row exists to prevent* |
| **Plain-language description** | *Share of resolved in-scope billing adjustment cases the customer reopens within 7 days* |
| **What is counted (numerator)** | *In-scope adjustment cases with a reopen event 0<t<=168h after first Resolved — 137 in the baseline month (templates/09-baseline-document.md:90)* |
| **Denominator / population** | *All in-scope billing adjustments reaching Resolved in the window — 966 in the baseline month (templates/09-baseline-document.md:90), so 11,592 a year. 137 / 966 = 14.2%. Not the Billing queue: its 266,000 tickets a year (templates/01-project-charter.md:47) are context, never this metric's denominator and never a benefit denominator* |
| **Time window** | *Rolling 7 days from each ticket's first Resolved timestamp* |
| **Unit of analysis** | contact / issue / ticket / customer / agent-day |
| **Inclusions** | *Adjustments on consumer accounts; all channels (voice, chat, email); sites A-D; amounts up to the $250 Billing Ops authority limit, including the ones Tier 1 hands over above $50 — the SIPOC in-scope rows (templates/02-sipoc.md:42-43)* |
| **Exclusions** | *Tickets merged into another; test/QA tickets; bot-only deflections. Plus everything the SIPOC puts out of scope (templates/02-sipoc.md:48-51): fraud holds and collections, manual refund cheques, enterprise accounts, and credits Billing Ops raises proactively with no customer contact. Billing tickets that are not adjustments are not exclusions — they are a different population, counted under OD-BIL-004 v2* |
| **Stratification fields available** | *Contact reason, agent tenure band, site, channel* |
| **Source system(s)** | *Zendesk (tickets), billing platform (postings)* |
| **Source tables / fields** | *warehouse.tickets.resolved_at, warehouse.ticket_events.reopened_at* |
| **Business rules applied** | *First Resolved only; a second reopen does not double-count* |
| **Refresh cadence** | *Nightly, 02:00 UTC; restated for 3 days as late events land* |
| **Metric is final at** | T + ___ |
| **Owner** | *A. Okafor, Billing Ops Manager — owns the definition, not just the number* |
| **Known limitations** | *Excludes chat until the channel field is backfilled. The lineage doc sizes that exclusion at roughly 0.4 points on the whole-queue rate (templates/06-data-lineage.md:57); its size on this adjustment-scoped rate is `<chat-exclusion effect on OD-BIL-004-ADJ, points>` — Analytics to measure it against the 966-case population when the backfill lands, before the next baseline recut. Do not carry the queue's 0.4 across; that is the same mistake in miniature* |
| **Related metrics it must reconcile with** | *OD-BIL-004 v2 — the 7-day reopen rate on all billing tickets, same 168-hour rule, whole queue, census, also 14.2% for 1-31 Mar (templates/06-data-lineage.md:50). Same number, different quantity: context only. The two reconcile by size, not by value — 11,592 in-scope adjustments a year against the queue's 266,000 is 4.4% of it, so closing every reopen in this population moves the queue rate from 14.2% to 13.58%, a 0.62-point move. Any claim that this metric shifts the queue rate by more than that is arithmetically impossible. The Ops weekly reopen tile reads 12.4%, 1.8 points under the queue figure (templates/06-data-lineage.md:48) — that gap reconciles OD-BIL-004 v2, not this metric* |

## Worked example
> Show one real record and how it is classified.

| Record ID | Field values | Counted? | Why |
|---|---|---|---|
| *TCK-118204* | *First Resolved 4 Mar 09:12. Reopened 12 Mar 08:40 — 191 hours later, same customer, same unposted credit* | *No (numerator); yes (denominator)* | *The window is 168 hours from first Resolved and this misses it by a day. It is the same failure and it still stings, but a rolling 7-day metric that quietly stretches to 8 days is no longer the metric two people agreed on. It stays in the denominator as a resolved in-scope adjustment* |
| *TCK-118377* | *Credit posted correctly on 9 Mar. Reopened 11 Mar because the replacement handset had not arrived — nothing to do with billing* | *Yes* | *Any-reason reopen. Reporting wanted same-reason only; that disagreement was settled on 2026-04-24 in favour of any reason, because the customer experiences one contact, not a reason code. Excluded from the numerator only if the ticket is re-tagged out of the in-scope adjustment population altogether* |
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
