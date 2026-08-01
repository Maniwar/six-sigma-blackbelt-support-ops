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
| **Primary metric** | |
| **Statistical test** | |
| Stratification to be applied | |
| Mix-shift check | chi-square on contact-reason distribution, treatment vs control |
| **Practical significance threshold** | |
| Alpha | |
| Power / required n per group | |
| Stopping rule | |
| Who runs the analysis | |

> Changing the primary metric or the test after seeing results invalidates the pilot.
> If you must change it, say so explicitly in the tollgate and treat the result as
> exploratory.

## 4. Counter-balancing metrics (tracked from day one)

| Metric | Baseline | Tolerance | Why it might move |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

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
| Primary: | | | | | | |
| Counter-bal: | | | | | | |
| Counter-bal: | | | | | | |

**Mix-shift check:** chi-square p = ______  → confounded? Yes / No

## 7. Realization forecast

> Pilot groups know they are being watched and outperform. Expect 20–40% of a pilot's
> measured gain to evaporate at full rollout. State the assumption rather than being
> surprised by it.

| Field | Value |
|---|---|
| Pilot effect | |
| Assumed realization factor | |
| **Forecast at full rollout** | |
| Basis for the realization assumption | |

## 8. Decision

- [ ] Proceed to full rollout
- [ ] Extend the pilot
- [ ] Redesign and re-pilot
- [ ] Kill

Decided by: ____________  Date: __________
