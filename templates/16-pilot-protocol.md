# Pilot Protocol — <Project>

<!-- guidance -->
## How to use this

**What it is for.** Registers what you will do, on whom, for how long, and what result would make you stop — before you start.

**When.** Improve, before the pilot runs. Registering it afterwards is not a protocol.

**Who signs it.** Black Belt writes · Champion approves the stopping rule

**The mistake this prevents.** Deciding the success criterion after seeing the data. Write the practical threshold and the kill criteria into this document first, and the pilot can only tell you one of two things.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate against a target of 8%. Delete them as you fill your own in.*

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
| Treatment group definition | *Billing queue, sites A and C, all tenures* |
| **Concurrent control group definition** | *Billing queue, sites B and D, same period* |
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
| **Primary metric** | *7-day reopen rate, billing adjustments* |
| **Statistical test** | *Two-proportion test, treatment vs concurrent control* |
| Stratification to be applied | *Contact reason and agent tenure band* |
| Mix-shift check | chi-square on contact-reason distribution, treatment vs control |
| **Practical significance threshold** | *1.5 percentage points — below this the benefit does not clear the cost* |
| Alpha | *0.05* |
| Power / required n per group | *80% power needs 6,900 per group; 8 weeks yields ~7,300* |
| Stopping rule | *Stop early only for harm: CSAT down more than 0.15 or handle time up more than 8%* |
| Who runs the analysis | *M. Berenji, with A. Okafor reviewing before it is circulated* |

> Changing the primary metric or the test after seeing results invalidates the pilot.
> If you must change it, say so explicitly in the tollgate and treat the result as
> exploratory.

> **How to work this out.** A sample size needs four inputs and no opinions: the
> baseline rate you are starting from, the smallest difference that would be worth
> acting on, alpha (how often you will accept a false alarm) and power (how often you
> want to catch a real effect when there is one). Type them into the "Sample size
> calculator" tab of `05-data-collection-plan.xlsx` in this pack. For this pilot:
> baseline 14.2%, detect a drop to 11%, alpha 0.05, power 80% — the calculator returns
> 1,685 billing adjustments per group, 3,370 across both arms. The 6,900 in the table
> above is the same calculator asked a harder question: the threshold we pre-registered
> is much tighter than 3.2 points. Halving the difference you insist on detecting
> roughly quadruples the tickets you need, so decide the threshold first and let it set
> the duration.

## 4. Counter-balancing metrics (tracked from day one)

| Metric | Baseline | Tolerance | Why it might move |
|---|---|---|---|
| *Mean handle time, billing adjustments* | *412 s (control limits 468 / 363)* | *No more than +8% (445 s), and no point above the 468 s upper limit* | *Agents now come back to a ticket they used to finish on first touch, and the second touch lands in the same handle-time bucket* |
| *CSAT, billing adjustments* | *4.11 out of 5* | *No decline greater than 0.15* | *The customer is told the case stays open until the credit posts, which some of them read as "not fixed yet"* |
| *Billing tickets still open after 3 working days* | *3.2% (31 of the 966 baseline-month adjustment contacts)* | *No more than 6%* | *The rule deliberately holds tickets open until the posting confirms, so a Friday adjustment waits over the weekend. Past 6% it is postings failing, not postings waiting* |

## 5. Success and kill criteria

**Proceed to full rollout if:**
- [ ] Primary metric effect ≥ practical threshold, statistically significant
- [ ] No counter-balancing metric outside tolerance
- [ ] Mix shift ruled out
- [ ] Operational feasibility confirmed by supervisors

**Kill or redesign if:**
- [ ] Primary metric moves in the wrong direction at any point
- [ ] Any counter-balancing metric breaches its stated tolerance
- [ ] Supervisors report the change is operationally unworkable
- [ ] _______________________________________________

## 6. Results

| Metric | Treatment | Control | Difference | 95% CI | p | Threshold met? |
|---|---|---|---|---|---|---|
| Primary: | *7-day reopen rate* | *14.2%* | *8.0%* | *1.5 pts* | *2-proportion* | *Weekly* |
| Counter-bal: | *CSAT, billing* | *4.11* | *no decline* | *-0.15* | *Mann-Whitney* | *Weekly* |
| Counter-bal: | *CSAT, billing* | *4.11* | *no decline* | *-0.15* | *Mann-Whitney* | *Weekly* |

**Mix-shift check:** chi-square p = ______  → confounded? Yes / No

## 7. Realization forecast

> Pilot groups know they are being watched and outperform. Expect 20–40% of a pilot's
> measured gain to evaporate at full rollout. State the assumption rather than being
> surprised by it.

| Field | Value |
|---|---|
| Pilot effect | *-4.9 percentage points (CI -6.1 to -3.7)* |
| Assumed realization factor | *0.85* |
| **Forecast at full rollout** | *-4.2 points, worth $22,005 a year* |
| Basis for the realization assumption | *Sites B and D have a different release cadence, so uptake lags by about a quarter* |

## 8. Decision

- [ ] Proceed to full rollout
- [ ] Extend the pilot
- [ ] Redesign and re-pilot
- [ ] Kill

Decided by: ____________  Date: __________
