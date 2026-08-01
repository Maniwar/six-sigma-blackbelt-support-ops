# Handover Package and Benefit Validation — <Project>

<!-- guidance -->
## How to use this

**What it is for.** Closes the project: hands the control plan to the owner and gets the benefit signed by Finance.

**When.** Control, after 90 days of control data — not at the end of the improvement.

**Who signs it.** Process owner accepts the controls · Finance validates the benefit

**The mistake this prevents.** Handing over without a named owner for each control. A control plan with no owner is a document; the process reverts within two quarters and nobody is accountable for noticing.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate on in-scope billing adjustments (OD-BIL-004-ADJ) against a target of 8%. The whole Billing queue also runs at 14.2% under OD-BIL-004 v2; that is a different quantity, measured on a different population, and it is context only — it is never a benefit denominator. Delete them as you fill your own in.*

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
> Price replication the way Part C prices this project: on the other queue's **in-scope
> adjustment population**, at the cost of a **reopened** contact. Not on the queue's whole
> contact volume, and not at the cost to serve an average contact. Multiplying an
> adjustment-scoped rate gap by a queue-scoped volume is the error this project's own
> benefit case had to be rebuilt to remove — see the note under Part C.

| Other queue / site / product / vendor | Same root cause present? | Effort to replicate | Estimated benefit | Owner | Status |
|---|---|---|---|---|---|
| *SMB billing queue — same adjustment path, business accounts* | *Yes — same status model and same nightly posting batch; 30 SMB reopens sampled, 19 closed pre-posting* | *Low — queue-level config change, no build* | *`<annual benefit — not yet derivable>`. The SMB queue's 41,000 contacts a year is whole-queue context, not the denominator; the in-scope adjustment volume behind it has never been measured. The reporting team must pull it from dw_ticket_fact on the same scope as `02-sipoc.md:42-51`, and D. Silva must price the gap at $38.60 a reopen, before the Q1 release.* | *D. Silva, SMB Billing Ops* | *Scheduled — config change rides the Q1 release* |
| *Device provisioning queue — SIM swaps and handset upgrades* | *Yes — the provisioning confirmation also lands after the agent has closed* | *Medium — different status model, about three sprint-weeks in the orders platform* | *`<annual benefit — not yet derivable>`. The 88,000 contacts a year is whole-queue context; the in-scope provisioning-adjustment volume has never been measured, and the rate gap will be smaller here because the confirmation lands faster. The reporting team must pull the volume and P. Nwosu must price the gap at $38.60 a reopen, before the orders-backlog slot is agreed.* | *P. Nwosu, Platform Engineering* | *Scoped — awaiting a slot in the orders backlog* |
| *Manila BPO overflow site — billing adjustments at peak* | *Yes — same billing platform, but the vendor closes in its own CRM, which has no pending state* | *High — vendor change request plus a contract amendment; the CRM is not ours* | *`<annual benefit — not yet derivable>`. The 21,000 overflow contacts a year is whole-site context; the in-scope adjustment volume at peak has never been measured. The reporting team must pull it and L. Tran must price the gap at $38.60 a reopen, before the Q2 business review.* | *L. Tran, Vendor Management* | *Raised with the vendor; decision at the Q2 business review* |
| *Field engineering appointment queue* | *No — the confirmation is captured in the van app before the ticket closes; 40 reopens reviewed, none closed pre-confirmation* | *n/a* | *None* | *K. Adeyemi, Field Ops (assessed only)* | *Closed — recorded so it is not re-proposed* |

**Total replication opportunity identified:** $____________
*(Not summable until the three in-scope adjustment volumes above have been measured. Do not
carry forward a total built from whole-queue contact counts.)*

## Part C — Benefit validation

### Post-implementation performance

| Field | Value |
|---|---|
| Full implementation date | *2026-08-03* |
| Control period start | *2026-08-04* |
| Control period end | *2026-11-02* (minimum 90 days) |
| Days of control data | *91* |
| Post-period metric (centre line) | *`<post-period centre line, OD-BIL-004-ADJ>` — the pack carries two figures for this same window and they cannot both stand. A. Okafor (control-plan owner) must re-read the Laney p′ centre line for the 91 days from 2026-08-04 and publish one figure, before the 90-day checkpoint on 2027-02-12.* |
| Post-period UCL / LCL | *`<UCL>` / `<LCL>` — published with the centre line above, by the same owner and by the same date* |
| Process stable in the control period? | *Yes — no points outside the limits, no runs of 8* |

### Mix-adjusted comparison
> Required. An unadjusted before/after is not acceptable evidence.

| Field | Value |
|---|---|
| Contact-mix chi-square, baseline vs post (p) | *0.38 — no material mix shift* |
| Mix shift present? | *Checked: contact-reason mix chi-sq p = 0.38, no material shift* |
| Adjustment method applied | *None required* |
| Mix-adjusted effect | *-4.7 points (unadjusted -4.9, 95% CI -6.1 to -3.7)* |

*The -4.7-point mix-adjusted figure is the controlled effect against a concurrent control. The
benefit below is priced on the 6.2-point baseline-to-target gap. The two are different
quantities and the pack does not yet reconcile them; Analytics owns that reconciliation, and it
must be closed before the 90-day checkpoint on 2027-02-12.*

### Benefit calculation

| Item | Value |
|---|---|
| Baseline metric | *14.2% — 7-day reopen rate, **in-scope billing adjustments** (OD-BIL-004-ADJ): 137 reopens / 966 contacts in the baseline month, `09-baseline-document.md:90`* |
| Post metric | *`<post-period centre line, OD-BIL-004-ADJ>` — see Post-implementation performance above* |
| Improvement | *6.2 percentage points — the 14.2% baseline against the 8.0% target, both on OD-BIL-004-ADJ. This is the gap the chain below is priced on, not the -4.7-point mix-adjusted controlled effect* |
| Annualized units affected | *719 reopens avoided — 11,592 in-scope adjustments a year (966 a month, `09-baseline-document.md:90,106`) x 6.2 points. The Billing queue's 266,000 contacts a year is context; it is not the multiplier* |
| Unit cost basis ($) | *$38.60 — Finance's 2026 fully-loaded cost of a **reopened** contact, `09-baseline-document.md:107`. It supersedes the $41.00 estimate. It is not $6.80: that is the cost to serve one average contact, and a reopen is not an average contact* |
| **Gross annual benefit** | *$27,753 — 719 x $38.60* |
| Realization factor applied | *0.85 — the avoided-contact factor, `01-project-charter.md:53`* |
| **Realized annual benefit** | *$23,590 — $27,753 x 0.85, before the handle time the fix adds (next row)* |
| Less: handle time the fix adds | *`<annual cost of the added resolution-confirmation handle time>` — the confirmation step lengthens every in-scope adjustment, and this document holds no measured figure for it. Analytics must price the measured AHT change across 11,592 adjustments a year, before the 90-day checkpoint on 2027-02-12* |
| **Benefit against the Finance floor** | ***$23,590 realized, before the added handle time, against a $50,000 floor (`01-project-charter.md:99`). The project does not clear the floor.*** |
| Benefit type | hard / soft / cost avoidance |
| Harvest mechanism | *Hiring avoidance against the Q1 billing plan. The number of roles is `<roles removed — not settled>`: it is a function of the avoided-reopen count, which has fallen from 17,556 to 719, and `09-baseline-document.md:108` records that no reduction is available because the queue is already 4 heads below establishment. WFM must state the approved establishment and current headcount at the claim date, before the 90-day checkpoint on 2027-02-12* |
| Harvest evidence (req/plan/PO reference) | *Headcount plan v4, lines 22-23, signed by WFM 2026-11-08* |
| Benefit claim period | 12 months from ____________ |
| Double-counting check — overlapping projects | *Checked against BIL-2026-009 (payment retries); no shared contacts* |

**Show the chain. Do not assert the total.**

```
  11,592 in-scope adjustments/yr  x  6.2 points        =     719 reopens avoided
     719 reopens avoided          x  $38.60            = $27,753 gross
 $27,753 gross                    x  0.85              = $23,590 realized
 $23,590 realized                 -  <added handle time>  =  what Finance can book
```

*$23,590 is 47% of the $50,000 Finance floor, and the added handle time only moves it down.
Say that plainly at the tollgate. Do not round toward the floor and do not reach for a bigger
population to rescue it.*

> **Why the number fell from $101,474 to $23,590 — record this, do not delete it.**
> The superseded chain here was 266,000 x 6.6 points x $6.80 x 0.85 = $101,474, and the
> charter's was 266,000 x 6.2 points x $6.80 x 0.85 = $95,324. Both are arithmetically exact
> and both are causally impossible. The fix touches billing adjustments: 11,592 of the queue's
> 266,000 contacts a year, and 1,646 of its 37,772 reopens — 4.4% of each. Fixing *every*
> adjustment reopen moves the whole-queue rate from 14.2% to 13.58%, a 0.62-point move. The
> pack claimed 6.2 points against the whole queue: ten times the arithmetic maximum. The rate
> was measured on one population and the volume taken from another, and because both
> populations happened to sit at 14.2% nobody noticed they were being multiplied together.
> This is the most common way a real benefit case dies. Name the population next to every rate
> and next to every volume, and check they are the same one before you multiply.

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
| 90-day | *2027-02-12* | *7.9%* | *Held* | *No action* | *A. Okafor* |
| **180-day re-audit** | *2027-05-14* | *8.4%* | *Drifting* | *Reopen: check whether the deferred-close rule is still enforced after the platform upgrade* | *A. Okafor* |

*Read every checkpoint on the same definition and the same chart as the control period —
OD-BIL-004-ADJ — and write which definition it was on next to the figure. The pack currently
carries two centre lines for this window, so an unlabelled checkpoint reading cannot be
compared to anything.*

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
| *Running the attribute MSA before trusting the reopen data — kappa 0.52 on the "resolution confirmed" rubric item, unacceptable under the bands the study was actually run on (<0.60, `07-msa-attribute-agreement.md:83-87`), is what redirected the project from agent behaviour to the closure rule* | *Two weeks went into a coaching plan for a problem that turned out to be a system rule* | *Run the attribute MSA in Measure, before the first cause hypothesis is written down, not after — and record every re-test with its statistic, unit, appraiser count and sample size. The re-test that unblocked the reopen figure (`07-msa-attribute-agreement.md:115`) carries none of them and cannot be cited until the QA manager restates it* | *Any project whose baseline comes out of a QA rubric — audit the rubric before you audit the process* |
| *Designing the cause out (Resolved blocked until the posting confirms) rather than training agents around it — level 2 on the countermeasure hierarchy, and it held for 90 days with nobody supervising it* | *The control did not survive a platform upgrade; queue settings reset to default and nobody was watching for it* | *Put the control's configuration on the release regression checklist on day one of handover, not after the 180-day re-audit finds it* | *Any control that lives in a system setting is only as durable as the release process around it* |
| *A concurrent control (sites B and D) instead of before/after — a platform release landed mid-pilot and hit both arms equally, so it did not confound the result* | *Sites were matched on contact mix only; the day-part split differed and had to be corrected during the analysis* | *Match on day-part as well as contact mix at the design stage, and check the match against a week of live data before the pilot starts* | *Site-level pilots in any queue — the pairing is the whole design, and it is cheap to check before you start* |
| *Pre-registering the practical threshold and the kill criteria before the pilot — the method is right, and it keeps the success test out of the argument once the numbers land* | *The project ran two success tests at once and nobody noticed: 1.5 points pre-registered at `16-pilot-protocol.md:57`, against 3.3 points derived in the charter from the $50,000 Finance floor (`01-project-charter.md:99-101`), with the charter's own threshold field left blank (`01-project-charter.md:95`). The 0.85 realization factor was also settled by discussion rather than evidence, and Finance rightly pushed back on it* | *Derive the threshold from the Finance floor and the in-scope volume, write the result into the charter's threshold field, and pre-register that one number. Take the realization factor from a previous project's pilot-to-rollout decay and name the project it came from* | *Any benefit claim that goes to Finance — the assumption will be challenged, so source it before you are asked* |
| *Rebuilding the benefit case on the population the fix actually touches — it turned a $101,474 claim into $23,590 and made the number defensible, even though the project no longer clears the floor* | *The original chain multiplied a rate measured on in-scope adjustments by the whole queue's 266,000 contacts, and priced each avoided reopen at the $6.80 cost to serve rather than the $38.60 cost of a reopen. It was arithmetically exact, causally impossible, and it survived all the way to the Control tollgate* | *Write the population next to every rate and every volume in the charter, and check at the Define gate that the multiplier and the metric name the same one* | *Every benefit case in the program. A rate measured on one population against a volume from another is invisible unless both populations are named — and it is the most common way a real benefit dies* |
