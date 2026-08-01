# Root Cause Evidence Pack — <Project>

<!-- guidance -->
## How to use this

**What it is for.** The evidence that a cause is real. One pack per accepted root cause.

**When.** End of Analyze, at the tollgate, before a single solution is designed.

**Who signs it.** Black Belt assembles · Process owner agrees each cause is plausible

**The mistake this prevents.** Accepting a cause on one key. A statistical result without a mechanism is a correlation, and a mechanism without a statistical result is a strongly held opinion. Both, every time, or it does not go in the pack.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate against a target of 8%. Delete them as you fill your own in.*

---

**The two-key rule:** a root cause is accepted only with a statistical result **and** a
described physical mechanism verified at the gemba. Statistics without mechanism is
correlation. Mechanism without statistics is opinion.

---

## Root cause 1: <name>

### Key 1 — Statistical evidence
| Field | Content |
|---|---|
| Test / model | *2-proportion test, deferred-close cohort vs control* |
| Sample size | *n = 7,420 and 7,180 billing tickets, 12 weeks* |
| Result (statistic, p-value) | *z = 5.13, p = 0.0001* |
| Effect size + 95% CI | *−4.9 percentage points (CI −6.1 to −3.7)* |
| Assumptions verified | *Independence checked; one ticket per customer per window* |
| Stratification applied | *Contact reason and agent tenure* |
| Confounders considered and ruled out | *Volume mix shift (chi-sq p = 0.41); no release in window* |
| Practical threshold met? | *Yes — threshold was 1.5 pts, observed 4.9* |

> **How to work this out.** Neither the p-value nor the sample size above is a judgement
> call. Open `13-hypothesis-test-log.xlsx` in this pack: you say what you are comparing
> and it names the test and prints the decision rule. Comparing two reopen rates — a
> percentage against a percentage — is a **two-proportion test**. Comparing handle time
> in seconds is a **two-sample t-test**, or **Mann-Whitney** if the seconds are skewed,
> which handle time almost always is. For the sample size, use the calculator on the
> "Sample size calculator" tab of `05-data-collection-plan.xlsx`: give it the baseline
> rate, the smallest difference worth acting on, alpha and power, and it returns the n
> you need per group. Do that before you pull the data, not after.

### Key 2 — Mechanism
> Describe *how* this cause produces the effect. Written so an operations director who
> has never seen the data would say "yes, that is how it works."

**Verified at the gemba by:**
| Method | Date | Observer | What was observed |
|---|---|---|---|
| Process observation | *2026-05-12* | *M. Berenji* | *Watched 11 closures; 4 closed before the webhook returned* |
| Agent interviews (n=) | *2026-05-13* | *M. Berenji* | *n=8; none could see posting status from the ticket* |
| Case review (n=) | *2026-05-14* | *A. Okafor* | *n=50 reopens; 31 closed pre-posting* |
| System / config inspection | *2026-05-15* | *P. Nwosu* | *Status model has no pending-adjustment state* |

### Contribution to the gap
| Field | Value |
|---|---|
| Baseline-to-goal gap | *14.2% → 8.0% = 6.2 points* |
| Estimated contribution of this cause | *4.9 points* |
| Basis for the estimate | *Measured effect from the deferred-close test* |
| % of gap explained | *79%* |

### Process owner agreement
Name: ____________  Agrees this cause is real and plausible: Yes / No  Date: ______

---

*Duplicate the block above for each accepted root cause.*

## Summary

| # | Root cause | Statistical evidence | Mechanism verified | % of gap | Accepted |
|---|---|---|---|---|---|
| 1 | *Closure permitted before the posting confirms* | *Statistical + mechanism* | *4.9 pts* | *79%* | *Accepted* |
| 2 | *Agent cannot see posting status from the ticket* | *Statistical + mechanism* | *1.1 pts* | *18%* | *Accepted* |
| 3 | *Reopen metric counts same-reason only* | *Mechanism only* | *—* | *—* | *Rejected — no statistical key* |
| 4 | *New-hire tenure under 90 days* | *Statistical only* | *0.4 pts* | *6%* | *Held — no mechanism described yet* |
| | | | **Total % of gap explained** | | |

> **Gate criterion:** if the accepted root causes explain less than ~60% of the
> baseline-to-goal gap, the team is not ready for Improve — they will design solutions
> that cannot mathematically reach the target. This is the most commonly waived gate
> criterion and the most expensive one to waive.

## Causes tested and REJECTED
Recording these prevents re-litigation later in the project.

| Candidate cause | How tested | Result | Why rejected |
|---|---|---|---|
| *Time of day — late-shift agents rushing the close at end of shift* | *2-proportion test, tickets closed before 17:00 vs after, 12 weeks of billing adjustments (n = 9,880 vs 4,720)* | *14.3% vs 14.0%, z = 0.48, p = 0.63* | *Every daytime closure sits ahead of the 02:00 posting batch, so the hour of closure cannot separate the two groups. The batch is the mechanism, not the shift.* |
| *Plan type — the retired Fibre-100 tariff mis-posting adjustments* | *Chi-square of reopen rate across all six plan families, 966 baseline-month billing-adjustment contacts* | *Fibre-100 14.6% vs 14.1% for the rest; chi-sq p = 0.62* | *The rate is flat across every plan family. P. Nwosu confirmed in config that adjustments post through one path regardless of tariff.* |
| *Channel — chat closures being sloppier than voice* | *2-proportion test, chat vs voice, same 12-week window* | *13.8% chat vs 14.5% voice, z = 0.94, p = 0.35* | *0.7 points, below the 1.5-point practical threshold, and the closure screen is identical in both channels.* |
| *Adjustment value — large credits queueing for approval and posting late* | *Mann-Whitney on adjustment amount, reopened vs not reopened cases (n = 137 vs 829)* | *Median $42 vs $39, p = 0.44* | *Amount does not separate reopens. Approval routing adds a step before the batch, not after it, so it cannot change whether the closure beats the posting.* |
| *Repeat disputers — a small group of customers reopening everything* | *Recounted the rate with one contact per customer per 7-day window; ranked customers by reopen count* | *14.2% falls to 13.9%; the 20 most frequent disputers are 1.8% of all reopens* | *Removing them moves the rate 0.3 points. The 6.2-point gap survives without them.* |
