# Handover Package and Benefit Validation — <Project>

<!-- guidance -->
## How to use this

**What it is for.** Closes the project: hands the control plan to the owner and gets the benefit signed by Finance.

**When.** Control, after 90 days of control data — not at the end of the improvement.

**Who signs it.** Process owner accepts the controls · Finance validates the benefit

**The mistake this prevents.** Handing over without a named owner for each control. A control plan with no owner is a document; the process reverts within two quarters and nobody is accountable for noticing.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate against a target of 8%. Delete them as you fill your own in.*

---

## Part A — Handover checklist

- [ ] Signed control plan with named owners for every metric
- [ ] Response plan **tested at least once** (simulate a signal; confirm the reaction happened)
- [ ] Updated SOPs and work instructions — refs: ____________________
- [ ] Updated system configuration documentation — refs: ____________________
- [ ] Updated training material / new-hire curriculum — refs: ____________________
- [ ] Updated QA rubric — items changed: ____________________
- [ ] Live dashboard or report delivering the control charts to the owner — link: ____________
- [ ] Lessons learned documented and posted to the replication library
- [ ] Replication assessment complete (below)
- [ ] Process owner has formally accepted

### Process owner acceptance
> Acceptance is a gate, not a formality. A control plan handed to an unwilling owner is
> a control plan that fails.

Name: ____________  Role: ____________  Signature: ____________  Date: __________

## Part B — Replication assessment

| Other queue / site / product / vendor | Same root cause present? | Effort to replicate | Estimated benefit | Owner | Status |
|---|---|---|---|---|---|
| *SMB billing queue — same adjustment path, business accounts* | *Yes — same status model and same nightly posting batch; 30 SMB reopens sampled, 19 closed pre-posting* | *Low — queue-level config change, no build* | *$18k/yr — 41,000 contacts x 6.6 points x $6.80* | *D. Silva, SMB Billing Ops* | *Scheduled — config change rides the Q1 release* |
| *Device provisioning queue — SIM swaps and handset upgrades* | *Yes — the provisioning confirmation also lands after the agent has closed* | *Medium — different status model, about three sprint-weeks in the orders platform* | *$26k/yr — 88,000 contacts x 4.4 points x $6.80 (confirmation is faster there, so two thirds of the billing effect)* | *P. Nwosu, Platform Engineering* | *Scoped — awaiting a slot in the orders backlog* |
| *Manila BPO overflow site — billing adjustments at peak* | *Yes — same billing platform, but the vendor closes in its own CRM, which has no pending state* | *High — vendor change request plus a contract amendment; the CRM is not ours* | *$9k/yr — 21,000 overflow contacts x 6.6 points x $6.80* | *L. Tran, Vendor Management* | *Raised with the vendor; decision at the Q2 business review* |
| *Field engineering appointment queue* | *No — the confirmation is captured in the van app before the ticket closes; 40 reopens reviewed, none closed pre-confirmation* | *n/a* | *None* | *K. Adeyemi, Field Ops (assessed only)* | *Closed — recorded so it is not re-proposed* |

**Total replication opportunity identified:** $____________

## Part C — Benefit validation

### Post-implementation performance

| Field | Value |
|---|---|
| Full implementation date | *2026-08-03* |
| Control period start | *2026-08-04* |
| Control period end | (minimum 90 days) |
| Days of control data | *91* |
| Post-period metric (centre line) | *7.6%* |
| Post-period UCL / LCL | *9.1% / 6.1%* |
| Process stable in the control period? | *Yes — no points outside the limits, no runs of 8* |

### Mix-adjusted comparison
> Required. An unadjusted before/after is not acceptable evidence.

| Field | Value |
|---|---|
| Contact-mix chi-square, baseline vs post (p) | *0.38 — no material mix shift* |
| Mix shift present? | *Checked: contact-reason mix chi-sq p = 0.38, no material shift* |
| Adjustment method applied | *None required* |
| Mix-adjusted effect | *-4.7 points (unadjusted -4.9)* |

### Benefit calculation

| Item | Value |
|---|---|
| Baseline metric | *14.2%* |
| Post metric | *7.6%* |
| Improvement | *6.6 percentage points* |
| Annualized units affected | *17,556 reopens avoided — 266,000 x 6.6 points* |
| Unit cost basis ($) | *$6.80 fully-loaded cost per contact* |
| **Gross annual benefit** | *$119,381* |
| Realization factor applied | *0.85* |
| **Realized annual benefit** | *$101,474* |
| Benefit type | hard / soft / cost avoidance |
| Harvest mechanism | *Hiring avoidance — two billing roles removed from the Q1 plan* |
| Harvest evidence (req/plan/PO reference) | *Headcount plan v4, lines 22-23, signed by WFM 2026-11-08* |
| Benefit claim period | 12 months from ____________ |
| Double-counting check — overlapping projects | *Checked against BIL-2026-009 (payment retries); no shared contacts* |

### Finance validation

| Role | Name | Signature | Date |
|---|---|---|---|
| Black Belt | *M. Berenji* |  | *2026-11-14* |
| Champion | *R. Mehta* |  | *2026-11-15* |
| **Finance partner** | *J. Lindqvist* |  | *2026-11-20* |
| Master Black Belt | *S. Iyer* |  | *2026-11-20* |

## Part D — Checkpoints

| Checkpoint | Due date | Metric value | Booked benefit still valid? | Revision | Signed |
|---|---|---|---|---|---|
| 90-day | *2027-02-12* | *A. Okafor* | *7.9%* | *Held* | *No action* |
| **180-day re-audit** | *2027-05-14* | *A. Okafor* | *8.4%* | *Drifting* | *Reopen: check whether the deferred-close rule is still enforced after the platform upgrade* |

> **The 6-month re-audit is mandatory.** Programs that skip it consistently over-report
> cumulative benefits, and the number eventually gets challenged by Finance in a way the
> program does not survive. If the gain has decayed, revise the booked benefit down and
> publish the revision.

### Re-audit findings
| Finding | Cause of decay | Corrective action | New control level | Owner |
|---|---|---|---|---|
| *The deferred-close block survived the March platform upgrade on the main billing queue but not on the overflow queue — 22% of overflow closures are again happening before the posting confirms* | *The upgrade reset queue-level settings to default, and only the main queue was re-checked afterwards* | *Re-apply the setting on the overflow queue, and add every queue carrying the block to the post-release regression checklist* | *Automated weekly config check; any queue without the block raises a ticket to Billing Ops the same day* | *P. Nwosu, Platform Engineering* |
| *Agents hired since go-live are still being taught the old close-then-verify sequence* | *The training deck and the SOP were updated; the laminated desk aid on the floor was not, and it is what new hires actually use* | *Withdraw and reprint the desk aid, and put it under the same version number as the SOP so the two cannot drift apart again* | *Desk aid carries the SOP version; checked at every new-hire intake* | *H. Bauer, Support Training* |
| *The response plan is being run late — the reopen chart signalled twice in March and the reaction was logged 9 and 12 days later* | *The dashboard alert went to a shared mailbox that lost its owner when the supervisor moved queues* | *Re-point the alert to a named owner with a named deputy, and log the reaction in the control plan* | *Named owner plus deputy; reaction due within 2 working days, checked at the Monday ops review* | *A. Okafor, Billing Ops* |

## Part E — Lessons learned

| What worked | What did not | What I would do differently | Transferable to other projects |
|---|---|---|---|
| *Running the attribute MSA before trusting the reopen data — kappa 0.52 on the "resolution confirmed" rubric item is what redirected the project from agent behaviour to the closure rule* | *Two weeks went into a coaching plan for a problem that turned out to be a system rule* | *Run the attribute MSA in Measure, before the first cause hypothesis is written down, not after* | *Any project whose baseline comes out of a QA rubric — audit the rubric before you audit the process* |
| *Designing the cause out (Resolved blocked until the posting confirms) rather than training agents around it — level 2 on the countermeasure hierarchy, and it held for 90 days with nobody supervising it* | *The control did not survive a platform upgrade; queue settings reset to default and nobody was watching for it* | *Put the control's configuration on the release regression checklist on day one of handover, not after the 180-day re-audit finds it* | *Any control that lives in a system setting is only as durable as the release process around it* |
| *A concurrent control (sites B and D) instead of before/after — a platform release landed mid-pilot and hit both arms equally, so it did not confound the result* | *Sites were matched on contact mix only; the day-part split differed and had to be corrected during the analysis* | *Match on day-part as well as contact mix at the design stage, and check the match against a week of live data before the pilot starts* | *Site-level pilots in any queue — the pairing is the whole design, and it is cheap to check before you start* |
| *Pre-registering the 1.5-point practical threshold and the kill criteria — nobody argued about what counted as success once the numbers came in* | *The 0.85 realization factor was settled by discussion rather than evidence, and Finance rightly pushed back on it* | *Take the realization factor from a previous project's pilot-to-rollout decay and name the project it came from* | *Any benefit claim that goes to Finance — the assumption will be challenged, so source it before you are asked* |
