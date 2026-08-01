# Root Cause Evidence Pack — <Project>

<!-- guidance -->
## How to use this

**What it is for.** The evidence that a cause is real. One pack per accepted root cause.

**When.** End of Analyze, at the tollgate, before a single solution is designed.

**Who signs it.** Black Belt assembles · Process owner agrees each cause is plausible

**The mistake this prevents.** Accepting a cause on one key. A statistical result without a mechanism is a correlation, and a mechanism without a statistical result is a strongly held opinion. Both, every time, or it does not go in the pack.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate on in-scope billing adjustments (OD-BIL-004-ADJ; 137 reopens / 966 contacts in the baseline month, templates/09-baseline-document.md:90) against a target of 8%. The whole Billing queue also runs a 14.2% 7-day reopen rate, under OD-BIL-004 v2 on a far wider population (templates/06-data-lineage.md:60) — a different quantity, and context only. Every sample size and every population on this page names which of the two it means; a bare "14.2% reopen rate" is the defect. Delete them as you fill your own in.*

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
| Sample size | *`<n deferred-close cohort>` and `<n control>`, in-scope billing adjustments, 12 weeks — the 7,420 and 7,180 this row carried are billing TICKETS from the whole queue (OD-BIL-004 v2), not the OD-BIL-004-ADJ population this cause is about. Twelve weeks of in-scope adjustments is roughly 2,900 contacts in total (966 a month, templates/09-baseline-document.md:90), so no two arms of that population sum to 14,600. M. Berenji re-runs the test on the adjustment population and states both n here before the Improve tollgate* |
| Result (statistic, p-value) | *z = 5.13, p = 0.0001 — computed on the billing-ticket sample above, so it is not yet a result about in-scope adjustments; it moves with the corrected n* |
| Effect size + 95% CI | *−4.9 percentage points (CI −6.1 to −3.7)* |
| Assumptions verified | *Independence checked; one ticket per customer per window* |
| Stratification applied | *Contact reason and agent tenure* |
| Confounders considered and ruled out | *Volume mix shift (chi-sq p = 0.41); no release in window* |
| Practical threshold met? | *Against the 1.5 pts pre-registered before the pilot, yes — observed 4.9. Against the charter's own threshold of 13.1 pts, worked back from Finance's $50,000 floor over 11,592 in-scope adjustments a year (templates/01-project-charter.md:116,120-122), no. Two thresholds are in force at once and they answer this row differently; the Black Belt must retire one before Improve* |

> **How to work this out.** Neither the p-value nor the sample size above is a judgement
> call. Open `13-hypothesis-test-log.xlsx` in this pack: you say what you are comparing
> and it names the test and prints the decision rule. Comparing two reopen rates — a
> percentage against a percentage — is a **two-proportion test**. Comparing handle time
> in seconds is a **two-sample t-test**, or **Mann-Whitney** if the seconds are skewed,
> which handle time almost always is. For the sample size, use the calculator on the
> "Sample size calculator" tab of `05-data-collection-plan.xlsx`: give it the baseline
> rate, the smallest difference worth acting on, alpha and power, and it returns the n
> you need per group. Do that before you pull the data, not after.
>
> **And size it on the population your metric is defined on.** The worked example's Y is
> the reopen rate on in-scope billing adjustments — 966 contacts a month
> (`09-baseline-document.md:90`) — while the Billing queue around it runs ~5,100 tickets a
> week (`09-baseline-document.md:51`). Draw the n from the queue and you get a sample your
> own population cannot fill, and an answer about a population your project does not
> touch. Write the population next to every n in this pack, not just the number.

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
| Baseline-to-goal gap | *14.2% → 8.0% = 6.2 points on the in-scope adjustment rate (OD-BIL-004-ADJ — 137 reopens / 966 contacts, templates/09-baseline-document.md:90), not on the whole-queue rate of the same name* |
| Estimated contribution of this cause | *4.9 points of that adjustment-scoped gap* |
| Basis for the estimate | *Measured effect from the deferred-close test* |
| % of gap explained | *79%* |

> **Whose population is this gap?** A contribution in points may only ever be multiplied by
> the volume of the population it was measured on. Write the population beside the points
> here, because this is the row a benefit case will lift the number from.
>
> *In the worked example the 6.2 points are the in-scope adjustment gap. Those adjustments
> run 966 a month (`09-baseline-document.md:90`), so 11,592 a year, against the Billing
> queue's 266,000 a year (`01-project-charter.md:47`) — 4.4% of it. At 14.2% each that is
> 1,646 adjustment reopens against the queue's 37,772, so closing every one of them moves
> the queue rate from 14.2% to (37,772 − 1,646) ÷ 266,000 = 13.58%: a 0.62-point move. The
> project's first benefit case applied these 6.2 points to the queue's 266,000 — ten times
> the arithmetic maximum, and the reason every population on this page is now named.*

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

*Every "% of gap" above is a share of the 6.2-point gap on the in-scope adjustment rate
(OD-BIL-004-ADJ), not of the whole-queue rate that reads the same 14.2%.*

> **Gate criterion:** if the accepted root causes explain less than ~60% of the
> baseline-to-goal gap, the team is not ready for Improve — they will design solutions
> that cannot mathematically reach the target. This is the most commonly waived gate
> criterion and the most expensive one to waive.

## Causes tested and REJECTED
Recording these prevents re-litigation later in the project.

| Candidate cause | How tested | Result | Why rejected |
|---|---|---|---|
| *Time of day — late-shift agents rushing the close at end of shift* | *2-proportion test, adjustments closed before 17:00 vs after, 12 weeks of in-scope billing adjustments (n = `<n before 17:00>` and `<n after 17:00>`)* | *14.3% vs 14.0%, z = 0.48, p = 0.63* | *Every daytime closure sits ahead of the 02:00 posting batch, so the hour of closure cannot separate the two groups. The batch is the mechanism, not the shift. Note the n this row carried — 9,880 and 4,720 — sums to the same 14,600 as the billing-TICKET sample in root cause 1, and 12 weeks of in-scope adjustments is roughly 2,900 contacts in all, so it was counted on the queue rather than on this population. M. Berenji restates both n and re-runs the test before the Improve tollgate; the rates and the p-value stand or fall with it.* |
| *Plan type — the retired Fibre-100 tariff mis-posting adjustments* | *Chi-square of reopen rate across all six plan families, the 966 in-scope billing-adjustment contacts of the baseline month (templates/09-baseline-document.md:90)* | *Fibre-100 14.6% vs 14.1% for the rest; chi-sq p = 0.62* | *The rate is flat across every plan family. P. Nwosu confirmed in config that adjustments post through one path regardless of tariff.* |
| *Channel — chat closures being sloppier than voice* | *2-proportion test, chat vs voice, same 12-week window (n not recorded)* | *13.8% chat vs 14.5% voice, z = 0.94, p = 0.35* | *0.7 points, below the 1.5-point threshold pre-registered for the pilot and far below the 13.1 points the charter derives from Finance's $50,000 floor (templates/01-project-charter.md:116) — rejected on either threshold. The closure screen is identical in both channels.* |
| *Adjustment value — large credits queueing for approval and posting late* | *Mann-Whitney on adjustment amount, reopened vs not reopened cases (n = 137 reopened and 829 not, the 966 in-scope adjustments of the baseline month — the same 137 / 966 that gives the 14.2% baseline, templates/09-baseline-document.md:90)* | *Median $42 vs $39, p = 0.44* | *Amount does not separate reopens. Approval routing adds a step before the batch, not after it, so it cannot change whether the closure beats the posting.* |
| *Repeat disputers — a small group of customers reopening everything* | *Recounted the rate with one contact per customer per 7-day window; ranked customers by reopen count* | *The in-scope adjustment rate (OD-BIL-004-ADJ) falls from 14.2% to 13.9%; the 20 most frequent disputers are 1.8% of all reopens* | *Removing them moves the rate 0.3 points. The 6.2-point adjustment-scoped gap survives without them.* |
