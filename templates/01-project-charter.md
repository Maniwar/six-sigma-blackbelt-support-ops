# Project Charter — <Project name>

<!-- guidance -->
## How to use this

**What it is for.** The contract between you, your Champion and Finance. Nothing else in the project is allowed to contradict it.

**When.** Define, before any data collection. Re-signed at every tollgate where the scope or the benefit changes.

**Who signs it.** Black Belt drafts · Champion, Process owner and Finance partner sign

**The mistake this prevents.** A charter with a benefit number and no named harvest mechanism. If nobody has committed to removing the headcount, renegotiating the contract or absorbing the growth, the saving is occupancy reduction — real for agents, invisible to the P&L, and it will not survive Finance validation at closure.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate on the in-scope adjustments (OD-BIL-004-ADJ; 137 reopens in 966 contacts) against a target of 8%. The whole Billing queue also reopens at 14.2%, under OD-BIL-004 v2 — a different quantity that happens to agree to the decimal, which is how the two came to be multiplied together. This charter keeps them apart; a bare "14.2% reopen rate" is the defect. Delete them as you fill your own in.*

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
| Target close date | *2026-12-18 — re-baselined to the Control actual in §8; the original 2026-10-30 was overtaken* |
| Charter version / date | v2.0 / `<date this revision is signed>` — see §11 |

## 1. Problem statement
> Between `<start date>` and `<end date>`, `<metric>` in `<process / queue / segment>` was
> `<baseline value>` against a target of `<target>`, representing `<gap in units>` and an
> estimated `<$ impact>` annualized. The impact is felt by `<who>` in the form of
> `<consequence>`. **The cause is not yet known.**

*Rule: no cause and no solution in the problem statement. If you already know the
answer, this is a project plan, not a DMAIC.*

## 2. Goal statement
Reduce / increase `<metric>` from `<baseline>` to `<target>` by `<date>`, while holding
`<counter-balancing metric>` within `<tolerance>`.

## 3. Business case

| Item | Value | Source |
|---|---|---|
| Benefit denominator — in-scope adjustment volume (annual) | *11,592 in-scope billing adjustments a year — 966 a month x 12* | *966 in-scope adjustments in the baseline month (09-baseline-document.md:106), the same 966 the baseline strata total to at 09-baseline-document.md:90. Nobody has pulled a 12-month in-scope count: the reporting team who pulled the queue volume below must pull the same 12 months to 31 May on the in-scope adjustment scope, before the 90-day benefit checkpoint on 2027-02-12 (18-handover-and-benefit-validation.md:142) — §8 records every tollgate, Improve and Control included, as already closed, so there is no gate left to make this due at — and this row is a 12x extrapolation of one measured month until they do* |
| Billing queue volume (annual) — CONTEXT ONLY, never a benefit multiplier | *266,000 billing tickets a year. The 61,400 in the baseline document is the same queue over a 12-week window at ~5,100/week (09-baseline-document.md:37,51), not one quarter* | *Warehouse table `dw_ticket_fact`, queue = Billing, 12 months to 31 May — pulled by the reporting team 3 Jun. The project changes how adjustments are closed, so this figure sizes the queue the work sits in and never multiplies the benefit — see §11* |
| Baseline metric | *14.2% of in-scope billing adjustments reopened within 7 days — 137 reopens in 966 contacts* | *09-baseline-document.md:90, counted per OD-BIL-004-ADJ (7-day reopen rate, in-scope billing adjustments). Baseline month: `<start and end dates of the month the 966 were counted over>` — A. Okafor, who signed the baseline, must state it before this v2.0 revision is signed (§11), which is the same ask, on the same owner, that 09-baseline-document.md:90 carries; the pack dates this figure to "one baseline month" and never says which. The whole-queue rate under OD-BIL-004 v2 is also 14.2% (06-data-lineage.md:60, 1–31 Mar) and is a different measurement of a different population* |
| Target metric | *8.0%, on the same in-scope adjustment population* | *FY26 support quality plan, section 4 — the rate the non-billing queues already run at* |
| Units avoided / improved | *719 reopens avoided a year — 11,592 in-scope adjustments x 6.2 points* | *Arithmetic, not a system: 11,592 x (14.2% less 8.0%) = 718.7. The 16,492 this row used to carry applied the same 6.2 points to the 266,000 queue, which is the error recorded in §11* |
| Unit cost basis ($) | *$38.60 fully-loaded cost of a reopened contact* | *Finance's 2026 rate with the facilities allocation removed (09-baseline-document.md:107). It supersedes the $41.00 estimate the same row attributes to this charter. The $6.80 previously carried here is the Finance cost-to-serve model's cost of serving one contact, not the price of a reopen; using it as one is a defect* |
| **Gross annual benefit** | *$27,753* | *719 x $38.60 — chain shown below the table* |
| Realization factor | *0.85 — agreed with Finance, reflects partial harvest in year one* | *Program benefit accounting policy v4, section 3.2; rate set by J. Lindqvist at the Define tollgate* |
| **Realized annual benefit** | *$23,590, less the handle time the fix adds — under the $50,000 Finance floor* | *$27,753 x 0.85. This is the number Finance validates against at closure, and as chartered it is less than half the floor at §5* |

**Benefit chain** (show it as arithmetic, so a reader can follow every step):
> *11,592 in-scope adjustments a year x 6.2 points = 719 reopens avoided*
> *719 x $38.60 = $27,753 gross*
> *$27,753 x 0.85 = $23,590 realized*
> *less the handle time the fix adds: `<seconds added per in-scope adjustment, measured>`*
>
> *The pack has never measured that last line. The "roughly 40 s" at §7 is a Define-stage
> expectation, not a measurement, and the gage study in 08-msa-gage-rr.md, section 3,
> records that it did not measure it either. R. Okonjo, who owns the AHT scorecard in §7,
> must state the measured figure from the pilot. It cannot be due before the Improve
> tollgate: §8 records the pilot as being read AT that gate, on 2026-09-25, so the figure
> does not exist until the gate is held. It is due by the 90-day benefit checkpoint on
> 2027-02-12 (18-handover-and-benefit-validation.md:142), where
> 18-handover-and-benefit-validation.md:96 already asks Analytics to price the same
> measured change across the 11,592 adjustments; the realized benefit falls by whatever
> it comes to.*
>
> ***$23,590 does not clear the $50,000 Finance floor (§5) — it is less than half of it,
> before the handle-time deduction.*** *The project cannot be booked as chartered. It is
> not rounding error and it will not be rescued by a bigger population: applying this
> 6.2-point gap to the queue's 266,000 is precisely the mistake recorded in §11.*

**Benefit type** (select one, per the program benefit accounting policy):
- [ ] Hard — headcount reduction
- [ ] Hard — hiring avoidance against an approved plan
- [ ] Hard — outsourcer volume / rate renegotiation
- [ ] Hard — spend line reduction
- [ ] Soft — capacity freed, not harvested
- [ ] Cost avoidance — compliance / risk

**Harvest mechanism** (required — how does this reach the P&L?):
> *`<none can be named at this size>`. 719 reopens avoided a year at 412 s of handle time
> is 82 agent hours, 0.05 FTE at 1,530 handling hours a head — a twentieth of a head,
> which is not a line WFM can take out of a requisition. On the in-scope volume there is
> no hiring avoidance to claim, so the saving is occupancy: real for agents, invisible to
> the P&L, and exactly what the guidance at the top of this charter says will not survive
> Finance validation. §8 records all five tollgates closed, Control on 2026-12-18, and
> that gate is where the floor finding was reached — there is no next tollgate to defer
> this to. R. Mehta and J. Lindqvist must decide at the 90-day benefit checkpoint on
> 2027-02-12 (18-handover-and-benefit-validation.md:142) whether the project continues on
> non-financial grounds or is re-scoped. The 1.2 FTE this box
> used to claim was 16,492 reopens x 412 s, and those 16,492 were the whole queue's — §11.*

Signed by Finance: ____________________  Date: __________
Signed by WFM:     ____________________  Date: __________

## 4. Scope

*Every row below is scoped to the in-scope billing adjustment population — the population
OD-BIL-004-ADJ is defined on (06-data-lineage.md:61) — and never to the Billing queue,
which appears in §3 and §5 as context only. A scope row that says "billing" without saying
which of the two it means is the defect this table exists to prevent.*

| | |
|---|---|
| First process step | *Customer submits a billing dispute* |
| Last process step | *Adjustment has posted and the customer has confirmed* |
| In scope | *In-scope billing adjustments as OD-BIL-004-ADJ defines them: consumer accounts, voice / chat / email, sites A-D, up to the $250 Billing Ops authority limit, including the ones Tier 1 hands over because they exceed $50 (02-sipoc.md:42,43; 06-data-lineage.md:61). This is the population the metric Y in §5, the 137 / 966 baseline in §3 and the 11,592 benefit denominator are all cut on. The $250 ceiling is constitutive of it, not a detail — the same cap governs the vendor fallback at §9* |
| Out of scope | *Fraud holds, collections, anything requiring a manual refund cheque, and credits Billing Ops raises proactively with no customer contact — no dispute, so no reopen to avoid (02-sipoc.md:48,49,51). The proactive-credit exclusion is part of what OD-BIL-004-ADJ counts (06-data-lineage.md:61), not housekeeping* |
| Channels included | *Voice, chat, email — the channels of the in-scope adjustment population, not of the whole Billing queue* |
| Sites / vendors included | *Sites A-D; no outsourced volume in scope* |
| Customer segments included | *All consumer accounts that raise an in-scope adjustment; enterprise excluded (different billing stack). The consumer restriction is part of what OD-BIL-004-ADJ counts (06-data-lineage.md:61), not a queue-level filter* |

## 5. Metric hierarchy

| Type | Metric | Baseline | Target | Op. definition ref |
|---|---|---|---|---|
| Primary | *7-day reopen rate, in-scope billing adjustments* | *14.2% — 137 reopens / 966 contacts* | *8.0%* | *OD-BIL-004-ADJ — a separate definition written for this population* |
| Context, not a project metric | *7-day reopen rate, all billing tickets* | *14.2% — whole Billing queue* | *none; it is not a project target* | *OD-BIL-004 v2 (06-data-lineage.md:60)* |
| Secondary | *Median resolution time, billing* | *4.6 h* | *4.0 h* | *OD-BIL-007 v1* |
| Counter-balancing | *CSAT, billing contacts* | *4.11* | *no decline* | *OD-CX-002 v3* |

**Practical significance threshold:** `<percentage points — not settled. The threshold is
a function of the annual in-scope adjustment volume, and nobody has pulled one: the
reporting team must supply the 12-month in-scope count asked for in §3, and the Black Belt
must then recompute this field by the method below, before the 90-day benefit checkpoint on
2027-02-12 (18-handover-and-benefit-validation.md:142).>`
> Derivation (work backwards from the benefit model — anything smaller is a null
> result regardless of its p-value):
>
> *Finance will not book a project below $50,000 realized. $50,000 ÷ 0.85 is $58,824
> gross; at $38.60 a reopened contact that is 1,524 reopens avoided, which on the
> provisional 11,592 in-scope adjustments a year works out at 13.1 points. That 13.1 is
> a working figure and not the field above: §3 records that the 11,592 it is divided by
> is a 12x extrapolation of one measured month that nobody has pulled, so the threshold
> moves when the real annual count lands. On the provisional figure a drop smaller than
> 13.1 points (14.2% to 1.1%) is a null result however small its p-value — and the 6.2
> points this charter sets out to win is less than half of it. The threshold is not a
> stretch target the project might still reach: on the provisional figure it is wider
> than the entire gap between the baseline and the target, which is §11's finding read
> from the other end. The 3.3 points this row
> used to carry took the same $58,824 and divided it by $6.80 a contact (8,650 reopens)
> and then by the queue's 266,000 — the wrong price of a reopen and the wrong
> population, compounding into a threshold the project appeared to clear by 1.9x: 6.2
> points against 3.3, and, on the v1.0 chain in §11, $95,324 realized against the
> $50,000 floor. The p-value itself comes from a two-proportion
> test of baseline reopens against pilot reopens — run it in
> `13-hypothesis-test-log.xlsx`, which picks the test and prints the decision rule.*

## 6. Team and RACI

| Name | Role | R/A/C/I | Time commitment | Manager confirmed |
|---|---|---|---|---|
| *M. Berenji* | Black Belt | A | *2 days a week until Control closes* | *Yes — R. Mehta confirmed 14 Mar, QA rota backfilled* |
| *R. Mehta, Support Director* | Champion | A | *2 h a month plus a half day at each tollgate* | *Yes — standing item in the Support leadership review, 16 Mar* |
| *A. Okafor, Billing Ops* | Process owner | R | *4 h a week, one full day in each tollgate week* | *Yes — confirmed 18 Mar, Billing Ops on-call swapped to cover* |
| *R. Okonjo, Tier 1 team lead* | *Subject matter expert, Tier 1* | *C* | *8 h a week to tollgate 3, then 4 h a week* | *Yes — confirmed 20 Mar, hours backfilled from the flex pool* |

*Exactly one A per row.*

## 7. Metric-impact disclosure (required)
Which existing team or individual scorecards will this project move, in which
direction, and who has agreed to adjust targets?

| Scorecard / metric | Owner | Expected direction | Target adjusted? | Agreed by |
|---|---|---|---|---|
| *AHT, Tier 1 billing queue* | *R. Okonjo, Tier 1 team lead* | *Up. Verifying the posting before closing is expected to add roughly 40 s to a 412 s contact — an expectation set at Define, not a measurement; the added handle time is the blank in the benefit chain at §3* | *Yes — team target moved from 412 s to 450 s for the pilot quarter, still inside the 468 s upper control limit* | *R. Mehta, 22 Mar* |
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
| Control | *2026-09-28* | *2026-12-18* | *90 days of control data; benefit re-worked at this gate and found not to clear the Finance floor — §11* |

## 9. Known risks and dependencies

| Risk / dependency | Impact | Mitigation | Owner |
|---|---|---|---|
| *The 02:00 posting batch is run by the billing platform vendor; the window sits in the contract, not in our gift* | *If it cannot move, anything raised after 17:00 still waits overnight and the 960-minute wait survives the project* | *Change request raised at Define, not at Improve. Fallback agreed with the vendor: a second 14:00 run for adjustments under $250* | *A. Okafor, Billing Ops* |
| *QA analysts agree only moderately on the "resolution confirmed" rubric item — first-pass kappa 0.52* | *The primary metric is read off that item, so the 14.2% in-scope adjustment baseline (OD-BIL-004-ADJ, 137/966) could be wrong in either direction* | *Re-calibrate the rubric and re-run the attribute agreement study before the Measure tollgate closes — see 07-msa-attribute-agreement.md* | *L. Haddad, QA manager* |
| *Adjustment volume roughly doubles over the billing cycle peak, the 12th to the 18th of each month* | *A pilot that dodges the peak will not generalise; one that straddles it confounds the change with volume* | *Pilot runs a full billing cycle and the read blocks on cycle week — protocol in 16-pilot-protocol.md* | *M. Berenji* |

## 10. Data access confirmed
- [ ] Ticketing / CRM
- [ ] Telephony / ACD
- [ ] WFM
- [ ] QA platform
- [ ] Survey platform
- [ ] Data warehouse
- [ ] Sample records already pulled

## 11. Revision history

Record what changed and why, especially when a benefit figure moves. A charter that is
quietly corrected teaches nobody.

| Version | Date | Change |
|---|---|---|
| *v1.0* | *2026-04-24* | *Charter signed at the Define tollgate (§8), with the benefit chain 266,000 x 6.2 points x $6.80 x 0.85 = $95,324 realized.* |
| *v2.0* | `<date this revision is signed>` | *Benefit model rebuilt on the population the project actually touches, and the reason kept on the record rather than deleted. The v1.0 chain is arithmetically exact and causally impossible. The 6.2-point gap is measured on in-scope billing adjustments; the 266,000 is the whole Billing queue. Adjustments are 11,592 of those 266,000 contacts and 1,646 of the queue's 37,772 reopens — 4.4% of each. Fixing every adjustment reopen in the year would move the whole-queue rate from 14.2% to 13.58%: a 0.62-point move, against the 6.2 points the charter claimed. The claim was ten times the arithmetic maximum. Corrected: 11,592 x 6.2 points = 719 reopens, x $38.60 = $27,753 gross, x 0.85 = $23,590 realized, less the handle time the fix adds — under the $50,000 Finance floor, so the project is not bookable as chartered. The unit cost moved with it, from $6.80 (cost to serve one contact) to $38.60 (cost of a reopened contact, 09-baseline-document.md:107); that raises the price of every avoided reopen 5.7x and still does not rescue the case. This is the ordinary way a benefit case dies — a rate measured on one population multiplied by a volume taken from another, both figures individually true — and it is recorded here so the next reader recognises the shape of it.* |

## Signatures

| Role | Name | Signature | Date |
|---|---|---|---|
| Champion | *R. Mehta, Support Director* |  |  |
| Black Belt | *M. Berenji* |  |  |
| Finance partner | *J. Lindqvist* |  |  |
| Master Black Belt | *S. Iyer* |  |  |
