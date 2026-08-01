# Project Charter — <Project name>

<!-- guidance -->
## How to use this

**What it is for.** The contract between you, your Champion and Finance. Nothing else in the project is allowed to contradict it.

**When.** Define, before any data collection. Re-signed at every tollgate where the scope or the benefit changes.

**Who signs it.** Black Belt drafts · Champion, Process owner and Finance partner sign

**The mistake this prevents.** A charter with a benefit number and no named harvest mechanism. If nobody has committed to removing the headcount, renegotiating the contract or absorbing the growth, the saving is occupancy reduction — real for agents, invisible to the P&L, and it will not survive Finance validation at closure.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate against a target of 8%. Delete them as you fill your own in.*

---

| Field | Value |
|---|---|
| Project ID | *BIL-2026-014* |
| Black Belt | *M. Berenji* |
| Champion | *R. Mehta, Support Director* |
| Process owner | *A. Okafor, Billing Ops* |
| Finance partner | *J. Lindqvist* |
| Master Black Belt | *S. Iyer* |
| Start date | *2026-04-06* |
| Target close date | *2026-10-30* |
| Charter version / date | v1.0 / |

## 1. Problem statement
> Between `<start date>` and `<end date>`, `<metric>` in `<process / queue / segment>` was
> `<baseline value>` against a target of `<target>`, representing `<gap in units>` and an
> estimated `<$ impact>` annualized. The impact is felt by `<who>` in the form of
> `<consequence>`. **The cause is not yet known.**

<!-- Rule: no cause and no solution in the problem statement. If you already know the
     answer, this is a project plan, not a DMAIC. -->

## 2. Goal statement
Reduce / increase `<metric>` from `<baseline>` to `<target>` by `<date>`, while holding
`<counter-balancing metric>` within `<tolerance>`.

## 3. Business case

| Item | Value | Source |
|---|---|---|
| Baseline volume (annual) | *266,000 billing tickets a year (the 61,400 in the baseline document is one quarter)* | *Warehouse table `dw_ticket_fact`, queue = Billing, 12 months to 31 May — pulled by the reporting team 3 Jun* |
| Baseline metric | *14.2% reopened within 7 days* | *Zendesk view "Billing adj — reopened <7d", 1 Mar to 31 May, counted per OD-BIL-004 v2 — pulled 1 Jun* |
| Target metric | *8.0%* | *FY26 support quality plan, section 4 — the rate the non-billing queues already run at* |
| Units avoided / improved | *16,492 reopens avoided a year — 266,000 x 6.2 points* | *Arithmetic, not a system: 266,000 x (14.2% less 8.0%). Checked in 19-black-belt-calculators.xlsx* |
| Unit cost basis ($) | *$6.80 fully-loaded cost per contact* | *Finance cost-to-serve model FY26 v3, billing contact line — agent time, telephony and overhead; issued 12 Feb* |
| **Gross annual benefit** | *$112,146* | *16,492 x $6.80 on the benefit sheet of 19-black-belt-calculators.xlsx — walked through with J. Lindqvist 12 Jun* |
| Realization factor | *0.85 — agreed with Finance, reflects partial harvest in year one* | *Program benefit accounting policy v4, section 3.2; rate set by J. Lindqvist at the Define tollgate* |
| **Realized annual benefit** | *$95,324* | *$112,146 x 0.85, same benefit sheet — the number Finance validates against at closure* |

**Benefit type** (select one, per the program benefit accounting policy):
- [ ] Hard — headcount reduction
- [ ] Hard — hiring avoidance against an approved plan
- [ ] Hard — outsourcer volume / rate renegotiation
- [ ] Hard — spend line reduction
- [ ] Soft — capacity freed, not harvested
- [ ] Cost avoidance — compliance / risk

**Harvest mechanism** (required — how does this reach the P&L?):
> *Hiring avoidance against the approved plan. 16,492 reopens avoided a year at 412 s
> of handle time is 1,887 agent hours, about 1.2 FTE at 1,530 handling hours a head.
> WFM removes 1.2 FTE from the Q4 Tier 1 requisition rather than cutting current
> heads; the amended requisition is what Finance validates against at closure.*

Signed by Finance: ____________________  Date: __________
Signed by WFM:     ____________________  Date: __________

## 4. Scope

| | |
|---|---|
| First process step | *Customer submits a billing dispute* |
| Last process step | *Adjustment has posted and the customer has confirmed* |
| In scope | *Billing adjustments, all channels, all sites* |
| Out of scope | *Fraud holds, collections, and anything requiring a manual refund cheque* |
| Channels included | *Voice, chat, email* |
| Sites / vendors included | *Sites A-D; no outsourced volume in scope* |
| Customer segments included | *All consumer accounts; enterprise excluded (different billing stack)* |

## 5. Metric hierarchy

| Type | Metric | Baseline | Target | Op. definition ref |
|---|---|---|---|---|
| Primary | *7-day reopen rate, billing* | *14.2%* | *8.0%* | *OD-BIL-004 v2* |
| Secondary | *Median resolution time, billing* | *4.6 h* | *4.0 h* | *OD-BIL-007 v1* |
| Secondary | *Median resolution time, billing* | *4.6 h* | *4.0 h* | *OD-BIL-007 v1* |
| Counter-balancing | *CSAT, billing contacts* | *4.11* | *no decline* | *OD-CX-002 v3* |
| Counter-balancing | *CSAT, billing contacts* | *4.11* | *no decline* | *OD-CX-002 v3* |

**Practical significance threshold:** `<value>`
> Derivation (work backwards from the benefit model — anything smaller is a null
> result regardless of its p-value):
>
> *Finance will not book a project below $50,000 realized. $50,000 ÷ 0.85 is $58,824
> gross; at $6.80 a contact that is 8,650 reopens avoided, which on 266,000 contacts a
> year is 3.3 points. So a drop smaller than 3.3 points (14.2% to 10.9%) is a null
> result however small its p-value. The p-value itself comes from a two-proportion
> test of baseline reopens against pilot reopens — run it in
> `13-hypothesis-test-log.xlsx`, which picks the test and prints the decision rule.*

## 6. Team and RACI

| Name | Role | R/A/C/I | Time commitment | Manager confirmed |
|---|---|---|---|---|
| *M. Berenji* | Black Belt | A | *2 days a week until Control closes* | *Yes — R. Mehta confirmed 14 Mar, QA rota backfilled* |
| *R. Mehta, Support Director* | Champion | A | *2 h a month plus a half day at each tollgate* | *Yes — standing item in the Support leadership review, 16 Mar* |
| *A. Okafor, Billing Ops* | Process owner | R | *4 h a week, one full day in each tollgate week* | *Yes — confirmed 18 Mar, Billing Ops on-call swapped to cover* |
| *R. Okonjo, Tier 1 team lead* | *Subject matter expert, Tier 1* | *C* | *8 h a week to tollgate 3, then 4 h a week* | *Yes — confirmed 20 Mar, hours backfilled from the flex pool* |

<!-- Exactly one A per row. -->

## 7. Metric-impact disclosure (required)
Which existing team or individual scorecards will this project move, in which
direction, and who has agreed to adjust targets?

| Scorecard / metric | Owner | Expected direction | Target adjusted? | Agreed by |
|---|---|---|---|---|
| *AHT, Tier 1 billing queue* | *R. Okonjo, Tier 1 team lead* | *Up. Verifying the posting before closing adds roughly 40 s to a 412 s contact* | *Yes — team target moved from 412 s to 450 s for the pilot quarter, still inside the 468 s upper control limit* | *R. Mehta, 22 Mar* |
| *Cases cleared per analyst, Billing Ops daily run* | *A. Okafor, Billing Ops* | *Down at first. Checking the account against the posting file is an extra step on every case* | *Yes — 60 cases a day cut to 52 until the posting batch moves* | *A. Okafor, 22 Mar* |
| *QA pass rate on the "resolution confirmed" rubric item* | *L. Haddad, QA manager* | *Down on paper. The rubric item is being tightened, so scores fall before they rise* | *Yes — held flat instead of the planned rise to 92% until the re-calibrated rubric has 4 weeks of data* | *L. Haddad, 4 Jun* |

Signed by affected ops leader: ____________________  Date: __________

## 8. Milestones

| Tollgate | Planned date | Actual | Outcome (Pass / Hold / Return) |
|---|---|---|---|
| Define | *2026-04-06* | *2026-04-24* | *Charter signed, SIPOC agreed* |
| Measure | *2026-04-27* | *2026-06-05* | *MSA passed, baseline signed* |
| Analyze | *2026-06-08* | *2026-07-24* | *Root causes evidenced on two keys* |
| Improve | *2026-07-27* | *2026-09-25* | *Pilot read, solution selected* |
| Control | *2026-09-28* | *2026-12-18* | *90 days of control data, benefit validated* |

## 9. Known risks and dependencies

| Risk / dependency | Impact | Mitigation | Owner |
|---|---|---|---|
| *The 02:00 posting batch is run by the billing platform vendor; the window sits in the contract, not in our gift* | *If it cannot move, anything raised after 17:00 still waits overnight and the 960-minute wait survives the project* | *Change request raised at Define, not at Improve. Fallback agreed with the vendor: a second 14:00 run for adjustments under $250* | *A. Okafor, Billing Ops* |
| *QA analysts agree only moderately on the "resolution confirmed" rubric item — first-pass kappa 0.52* | *The primary metric is read off that item, so the 14.2% baseline could be wrong in either direction* | *Re-calibrate the rubric and re-run the attribute agreement study before the Measure tollgate closes — see 07-msa-attribute-agreement.md* | *L. Haddad, QA manager* |
| *Adjustment volume roughly doubles over the billing cycle peak, the 12th to the 18th of each month* | *A pilot that dodges the peak will not generalise; one that straddles it confounds the change with volume* | *Pilot runs a full billing cycle and the read blocks on cycle week — protocol in 16-pilot-protocol.md* | *M. Berenji* |

## 10. Data access confirmed
- [ ] Ticketing / CRM
- [ ] Telephony / ACD
- [ ] WFM
- [ ] QA platform
- [ ] Survey platform
- [ ] Data warehouse
- [ ] Sample records already pulled

## Signatures

| Role | Name | Signature | Date |
|---|---|---|---|
| Champion | *R. Mehta, Support Director* |  |  |
| Black Belt | *M. Berenji* |  |  |
| Finance partner | *J. Lindqvist* |  |  |
| Master Black Belt | *S. Iyer* |  |  |
