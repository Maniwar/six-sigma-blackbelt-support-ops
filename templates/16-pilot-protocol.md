# Pilot Protocol — <Project>

<!-- guidance -->
## How to use this

**What it is for.** Registers what you will do, on whom, for how long, and what result would make you stop — before you start.

**When.** Improve, before the pilot runs. Registering it afterwards is not a protocol.

**Who signs it.** Black Belt writes · Champion approves the stopping rule

**The mistake this prevents.** Deciding the success criterion after seeing the data. Write the practical threshold and the kill criteria into this document first, and the pilot can only tell you one of two things.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate on in-scope billing adjustments (OD-BIL-004-ADJ — 137 reopens in 966 contacts, 09-baseline-document.md:90) against a target of 8.0%. The whole Billing queue's 7-day reopen rate under OD-BIL-004 v2 is also 14.2% (06-data-lineage.md:61); it is a different measurement of a different population and it is never this pilot's metric. Delete them as you fill your own in.*

---

**Complete and circulate this BEFORE the pilot starts. Pre-registration is what stops
post-hoc metric-shopping, which is the single largest source of inflated benefits in
support improvement programs.**

## 1. What is being piloted

| Field | Content |
|---|---|
| Solution(s) | *Block Resolved until the billing posting webhook confirms* |
| Root cause(s) addressed | *RC-1 closure permitted before posting confirms* |
| Countermeasure hierarchy level | *2 — Design it out* |
| Expected mechanism of effect | *The ticket cannot reach Resolved while an adjustment is in flight, so the customer has nothing to reopen for* |

## 2. Design

| Field | Value |
|---|---|
| Treatment group definition | *Sites A and C, all tenures — in-scope billing adjustments only. The change is made inside the Billing queue, but the population piloted and measured is the adjustment population under OD-BIL-004-ADJ, not the queue* |
| **Concurrent control group definition** | *Sites B and D, same period, same in-scope adjustment definition* |
| Randomization / assignment mechanism | (agent-level / site-level / time-block / switchback) |
| Matching factors | contact mix · tenure distribution · channel split · site · day-part |
| Start date | *2026-06-01* |
| End date | *2026-07-27 (8 whole weeks)* |
| **Duration** | (minimum 4 full weeks) |
| **Weeks excluded from analysis** | (week 1 — learning curve is a confounder, not the steady state) |
| Blinding | (ambient / announced) |

> **Always run a concurrent control**, not a before/after comparison, unless the change
> is physically impossible to partition. Before/after in support is contaminated by
> demand shifts, product releases, staffing changes and seasonality.

## 3. Pre-registered analysis

| Field | Value |
|---|---|
| **Primary metric** | *7-day reopen rate, in-scope billing adjustments — OD-BIL-004-ADJ. Not the 7-day reopen rate for all billing tickets (OD-BIL-004 v2), which reads 14.2% as well and is a different quantity* |
| **Statistical test** | *Two-proportion test, treatment vs concurrent control* |
| Stratification to be applied | *Contact reason and agent tenure band* |
| Mix-shift check | chi-square on contact-reason distribution, treatment vs control |
| **Practical significance threshold** | *13.1 percentage points — below this the benefit does not clear the $50,000 realized floor Finance books against. Derivation at 01-project-charter.md:137-139: $50,000 ÷ 0.85 = $58,824 gross; at $38.60 a reopened contact that is 1,524 reopens avoided; on 11,592 in-scope adjustments a year that is 13.1 points* |
| Alpha | *0.05* |
| Power / required n per group | *80% power at alpha 0.05, sized on the 13.1-point threshold pre-registered in the row above: **61 per group**. The "Sample size calculator" tab of `05-data-collection-plan.xlsx` adds the change to the current rate, so the entry that asks this question is Current rate 1.1%, Change you want to detect +13.1 points — 1.1% against 14.2%. The pilot supplies far more than 61: 966 in-scope adjustments a month (§4) is about 223 a week (966 × 12 ÷ 52), and the seven weeks left once §2 excludes week 1 supply roughly 1,560 across both arms, about 780 a group. The pilot is therefore comfortably powered against its own threshold; what it cannot do is clear that threshold, which is a different problem and is the note below. M. Berenji, who runs the analysis, confirms the entry and the figure before the pilot starts. The "6,900 per group, 8 weeks yields ~7,300" this row used to carry is queue-scale arithmetic on an adjustment-scale population; no adjustment volume in the pack produces it* |
| Stopping rule | *Stop early only for harm: CSAT down more than 0.15 or handle time up more than 8% (445 s against the 412 s baseline in §4)* |
| Who runs the analysis | *M. Berenji, with A. Okafor reviewing before it is circulated* |

> Changing the primary metric or the test after seeing results invalidates the pilot.
> If you must change it, say so explicitly in the tollgate and treat the result as
> exploratory.

> **Register what the threshold means before you start.** In the worked example the
> threshold is wider than the gap the project is chartered to close: 13.1 points against
> a 6.2-point gap from the 14.2% OD-BIL-004-ADJ baseline on in-scope billing adjustments
> to the 8.0% target on the same population. So no result this pilot can
> produce will clear the Finance floor, and that is a finding to take to the Champion
> before the pilot runs — not a reason to lower the threshold once the data is in. The
> pilot can still answer whether the mechanism works. It cannot answer whether the
> project is bookable, and §7 must not be read as if it could.

> **How to work this out.** A sample size needs four inputs and no opinions: the
> baseline rate you are starting from, the smallest difference that would be worth
> acting on, alpha (how often you will accept a false alarm) and power (how often you
> want to catch a real effect when there is one). Type them into the "Sample size
> calculator" tab of `05-data-collection-plan.xlsx` in this pack. Read the tab before you
> type into it: "Change you want to detect" is ADDED to "Current rate" (`C10 = C5 + C6`),
> and the answer cell is blank for any change that is not positive. So a drop is entered
> as the lower rate with a positive gap. Take a 3.2-point question on this population —
> 11.0% against the 14.2% in-scope adjustment baseline. Entering 11.0% with +3.2 points,
> alpha 0.05, power 80% returns 1,685 in-scope adjustments per group, 3,370 across both
> arms. Entering 14.2% with +3.2 does not ask that question — it sizes a rise to 17.4% and
> returns 2,036 — and entering 14.2% with −3.2 returns an empty cell. Halving the
> difference you insist on detecting roughly quadruples the tickets you need, so decide
> the threshold first and let it set the duration. Then check the answer against the
> population you actually have, which is the step this pilot skipped: 3,370 adjustments is
> more than twice the ~1,560 that the seven analysed weeks of in-scope adjustments supply,
> so a 3.2-point question cannot be asked at this duration. Note which question that is.
> It is not the one §3 pre-registers: the registered 13.1-point threshold needs 61 a group
> and this pilot answers it many times over. The population is too small for the smaller,
> unregistered question and ample for the registered one, and the §6 read-out settles
> neither — see the note under that table.

## 4. Counter-balancing metrics (tracked from day one)

| Metric | Baseline | Tolerance | Why it might move |
|---|---|---|---|
| *Mean handle time, in-scope billing adjustments* | *412 s (control limits 468 / 363)* | *No more than +8% (445 s), and no point above the 468 s upper limit* | *Agents now come back to a ticket they used to finish on first touch, and the second touch lands in the same handle-time bucket* |
| *CSAT, in-scope billing adjustments* | *4.11 out of 5* | *No decline greater than 0.15* | *The customer is told the case stays open until the credit posts, which some of them read as "not fixed yet"* |
| *In-scope billing adjustments still open after 3 working days* | *`<not measured — no document in the pack counts in-scope adjustments by age. A. Okafor, who signed the baseline, must measure it on the same baseline month as the 966 and state it before the Improve tollgate>`. The 3.2% (31 contacts) this cell used to carry is in no document in the pack, and the 09-baseline-document.md:90 it cited carries 966, 137 and 14.2% — nothing about ticket age* | *No more than 6%* | *The rule deliberately holds tickets open until the posting confirms, so a Friday adjustment waits over the weekend. Past 6% it is postings failing, not postings waiting* |

## 5. Success and kill criteria

**Proceed to full rollout if:**
- [ ] Primary metric effect ≥ practical threshold, statistically significant
- [ ] No counter-balancing metric outside tolerance
- [ ] Mix shift ruled out
- [ ] Operational feasibility confirmed by supervisors

**Kill or redesign if:**
- [ ] Primary metric moves in the wrong direction on the analysed window as a whole (weeks 2–8 pooled), not on any single week — §3's stopping rule is "stop early only for harm" and it governs. At about 112 in-scope adjustments an arm a week, a weekly arm difference carries roughly 4.7 points of standard error (√(0.142 × 0.858 × 2 ÷ 112)), so an adverse week is near-certain across a seven-week read and killing on one would be killing on noise
- [ ] Any counter-balancing metric breaches its stated tolerance
- [ ] Supervisors report the change is operationally unworkable
- [ ] _______________________________________________

## 6. Results

| Metric | Treatment | Control | Difference | 95% CI | p | Threshold met? |
|---|---|---|---|---|---|---|
| *Primary: 7-day reopen rate, in-scope billing adjustments (OD-BIL-004-ADJ)* | *8.9%* | *13.8%* | *-4.9 pts* | *-6.1 to -3.7* | *< 0.001* | *No — 4.9 points is a long way short of the 13.1-point threshold in §3. Significant is not the same as bookable* |
| *Counter-bal: mean handle time, in-scope billing adjustments* | *7:04 (424 s)* | *6:41 (401 s)* | *+23 s (+5.7%)* | *`<not published>`* | *`<not published>`* | *Within tolerance — 424 s is inside the 445 s (+8%) tolerance and the 468 s upper limit in §4* |
| *Counter-bal: CSAT, in-scope billing adjustments* | *4.42* | *4.31* | *+0.11* | *`<not published>`* | *ns, favourable* | *Yes — no decline* |
| *Counter-bal: in-scope billing adjustments still open after 3 working days* | *`<not reported>`* | *`<not reported>`* | *—* | *—* | *—* | *Cannot be judged. §5 kills the pilot on any counter-balancing metric outside tolerance, and this one was declared in §4 and never read out* |

*Source of the read-out: six-sigma-blackbelt-support-ops.html:2436 (8.9% vs 13.8%, -4.9 pts, CI -6.1 to -3.7), :2437 (p < 0.001), :2438 (7:04 vs 6:41, +23 s), :2439 (CSAT 4.42 vs 4.31). These numbers did not come from the design §2 registers, and the published CI is what shows it. A 95% half-width of 1.2 points is a standard error of 1.2 ÷ 1.96 = 0.61 points, or 0.0061; (0.089 × 0.911 + 0.138 × 0.862) ÷ 0.0061² is about 5,300 in-scope adjustments an arm, more than 10,000 across both — nearly seven times the ~1,560 that the seven analysed weeks of this population supply (§3). That multiplication was never done, which is the failure this pack exists to record: an imported result and a stated population sitting two sections apart. Two things must therefore be reconciled before this table is circulated and neither can be settled from the pack: the read-out describes a 6-week pilot in 2 of 6 billing pods (n = 41 agents, html:2432), while §2 registers 8 weeks across sites A and C against B and D — M. Berenji must state which design and which population produced these numbers; and the read-out publishes no CI or p for the counter-balancing arms and no reading at all for the third one declared in §4, all of which the same analysis owner must supply. Everything in this paragraph before the Improve tollgate.*

*The handle-time row is judged against §4's tolerance, which is the guardrail of record — 445 s at +8%, inside the 468 s upper limit that 01-project-charter.md:173 and 03-voc-ctq-tree.md:101 state independently. Two collisions come with that choice and neither may be settled quietly. First, +23 s is +5.7%, so the same result fails the +5% ceiling declared at six-sigma-blackbelt-support-ops.html:2334. Second, the charter row cited above is not only support for the 468 s limit: the same line records the Tier 1 team target formally moved "from 412 s to 450 s for the pilot quarter", signed by R. Mehta on 22 Mar, and an expected rise of "roughly 40 s to a 412 s contact" — 452 s. Both sit above the 445 s tolerance in §4, and §5 makes a tolerance breach a kill criterion, so as written this pilot is pre-registered to be killed for producing exactly the handle-time rise the charter has already agreed and signed. Which guardrail survives — the +5% ceiling, §4's +8% / 445 s, or the signed 450 s — is a decision for R. Mehta, not an editorial tidy-up, and §4 and §5 must be re-signed to whichever it is before the pilot runs.*

*What this table used to hold: `7-day reopen rate | 14.2% | 8.0% | 1.5 pts | 2-proportion | Weekly`, with the CSAT row repeated verbatim and no handle-time row at all. Those are the §3 pre-registration values written one column right of their headers, so the baseline appeared as a treatment result and the one metric that could have failed the pilot had nowhere to appear.*

**Mix-shift check:** chi-square p = ______  → confounded? Yes / No

> Treatment against concurrent control, over the pilot window. The p = 0.38 in
> 18-handover-and-benefit-validation.md:74 is a different check — baseline against the
> post-implementation period — and must not be copied into this line.

## 7. Realization forecast

> Pilot groups know they are being watched and outperform, so state a realization
> assumption rather than being surprised by one. **How much evaporates depends on the
> archetype, and the pack sets the two bands rather than leaving it to taste.**
> Handle-time projects keep 0.6–0.8, so expect 20–40% of the pilot's measured gain to go
> — `templates/19-black-belt-calculators.xlsx` '7 Benefit — AHT'!B9 sets 0.7 and D9 says
> "Typically 60–80%", and the program's benefit-accounting policy says the same from the
> other end, that benefits are booked at the 90-day measured rate and typical realization
> is 60–80% of pilot (six-sigma-blackbelt-support-ops.html:2677-2678). Avoided-contact
> projects keep more, 0.8–0.9: '8 Benefit — avoided contacts'!B9 sets 0.85 and D9 gives
> the reason — "Higher than for handle-time projects, because an avoided contact is
> unambiguously avoided" — there is no harvesting argument to make, because the work never
> arrives, whereas a handle-time saving only becomes money if schedules change
> (the band itself is stated at six-sigma-blackbelt-support-ops.html:3647, "0.8–0.9 is
> reasonable ... because an avoided contact is unambiguously avoided"). **The worked
> example is an avoided-contact project**, so the 20–40% figure above is not its band and
> the 0.85 in the table below is not a departure from it.

> **One factor, one job.** The worked example uses 0.85 here, which is the factor Finance
> agreed for this project's avoided-contact benefit (01-project-charter.md:54), and it is
> applied once — to the effect size, in the table below. Do not apply it again to the
> money. That 0.85 is now doing two jobs the pack treats as one: the pilot-to-rollout
> haircut in this document and the benefit-accounting factor in the charter. J. Lindqvist,
> who set the rate, should confirm one number covers both before the Improve tollgate.

| Field | Value |
|---|---|
| Pilot effect | *-4.9 percentage points (CI -6.1 to -3.7), treatment against concurrent control* |
| Assumed realization factor | *0.85 — the value 19-black-belt-calculators.xlsx '8 Benefit — avoided contacts'!B9 carries, inside the 0.8–0.9 band six-sigma-blackbelt-support-ops.html:3647 gives for this archetype, and not the 0.6–0.8 handle-time band in the note above. Applied here, to the effect size, and not again to the money* |
| **Forecast at full rollout** | *-4.2 points (-4.9 × 0.85) on the in-scope adjustment population, worth $18,798 a year less the handle time the fix adds — see the chain below. **It does not clear the $50,000 Finance floor.*** |
| Basis for the realization assumption | *Sites B and D have a different release cadence, so uptake lags by about a quarter* |

**The chain, as arithmetic the reader can follow:**

| Step | Arithmetic | Result |
|---|---|---|
| *In-scope adjustments a year* | *966 a month × 12 (09-baseline-document.md:106)* | *11,592* |
| *Reopens avoided a year at the forecast effect* | *11,592 × 4.2 points* | *487* |
| *Benefit at the 2026 cost of a reopened contact* | *487 × $38.60 (09-baseline-document.md:107)* | *$18,798* |
| *less the handle time the fix adds* | *`<the +23 s per contact measured at §6, priced — nothing in the pack costs it>`* | *`<blank>`* |

*R. Okonjo, who owns the AHT scorecard (01-project-charter.md:173), and Finance must price
that last line on the in-scope adjustment population at the same 2026 rate, before the
Improve tollgate. The charter's "roughly 40 s" is a Define-stage expectation, not a
measurement, and is not used here.*

*$18,798 is 38% of the $50,000 realized floor, and the deduction above only takes it
lower. The project does not clear the floor at its chartered ceiling either: 11,592 ×
6.2 points = 719 reopens avoided, × $38.60 = $27,753 gross, × 0.85 = $23,590 realized
(01-project-charter.md:57-60). Say that plainly at the tollgate rather than rounding
toward the floor. The $22,005 this row used to carry was the old charter's realized
benefit — 61,400 queue tickets × 6.2 points × $6.80 × 0.85 — copied into a cell labelled
"forecast at full rollout": not this pilot's effect, not this project's population, and
$6.80 is the cost of serving one contact rather than the price of a reopen. The one move
that is never available is to rescue the number by multiplying an adjustment-measured
effect by the queue's 266,000 a year; that is the error recorded in the baseline
document's revision history.*

## 8. Decision

- [ ] Proceed to full rollout
- [ ] Extend the pilot
- [ ] Redesign and re-pilot
- [ ] Kill

Decided by: ____________  Date: __________
