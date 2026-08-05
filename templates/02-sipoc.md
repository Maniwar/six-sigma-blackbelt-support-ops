# SIPOC — <Process name>

<!-- guidance -->
## How to use this

**What it is for.** The boundary diagram. It settles what is in scope before anyone argues about it in week six.

**When.** Define, in the first workshop, on a wall, with the process owner in the room.

**Who signs it.** Black Belt facilitates · Process owner agrees the boundaries

**The mistake this prevents.** Writing the process you wish you had rather than the one that runs. Walk it before you draw it.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate on the in-scope adjustments (OD-BIL-004-ADJ — 137 reopens / 966 contacts in the baseline month, 09-baseline-document.md:90) against a target of 8.0%. That is not the queue-wide 14.2% (OD-BIL-004 v2, all billing tickets): two different populations that land on the same number. Delete them as you fill your own in.*

---

**Process purpose (one sentence):**
> *To take a customer's disputed charge from the moment they raise it to an adjustment
> that has actually posted and that the customer has confirmed — without a callback.*

## SIPOC

| Suppliers | Inputs | Process (5–7 steps) | Outputs | Customers |
|---|---|---|---|---|
| *Customer; billing platform (the bill that is being disputed)* | *Disputed charge, account number, the customer's account of what is wrong, bill image* | 1. *Customer raises the dispute and it lands in the unassigned billing queue* | *A ticket in the billing queue with a dispute reason and a raised timestamp* | *Tier 1 billing queue (next step); the customer, now waiting* |
| *Tier 1 agent; Knowledge team (reason codes and articles)* | *Ticket, reason-code taxonomy, knowledge article, the $50 Tier 1 authority limit* | 2. *Tier 1 triages, tags the reason and raises the adjustment request* | *A tagged adjustment request with an amount and a reason code* | *Billing Ops daily run (next step)* |
| *Billing Ops analyst; Finance (delegation of authority)* | *Account balance and charge history, the requested amount, the $250 Billing Ops limit* | 3. *Billing Ops checks the account on the daily run and approves or rejects the amount* | *An approved or rejected adjustment, with the reason for the decision recorded* | *The nightly posting batch; Finance, for the audit trail* |
| *Billing platform vendor, who runs the 02:00 posting batch* | *Approved adjustments queued to the batch; the posting file and its run log* | 4. *The nightly batch posts the adjustment and the agent verifies it landed* | *A posted credit and a posting confirmation, or a failure line in the batch log* | *The verifying Tier 1 agent; the customer, whose bill changes* |
| *Tier 1 agent; contact platform (outbound call, chat or email)* | *Posting confirmation, the customer's contact preference, the closure rubric* | 5. *Agent confirms the posting with the customer and closes the case* | *A closed case, a confirmed customer, and a QA-checkable "resolution confirmed" record* | *The customer; QA and Billing Ops for reopen reporting; Finance* |

*If you need more than 7 steps, your scope is too wide. Split the project.*

## Scope boundaries

| | |
|---|---|
| **First step** (process starts when…) | *the customer submits a billing dispute* |
| **Last step** (process ends when…) | *the adjustment has posted and the customer has confirmed* |

### Explicitly IN scope
- *Billing adjustments on consumer accounts, all channels (voice, chat, email), sites A-D*
- *Adjustments up to the $250 Billing Ops authority limit, including the ones Tier 1 hands over because they exceed $50*
- *The nightly 02:00 posting batch and the wait in front of it — anything raised after 17:00 misses that night's run*
- *Case closure itself, and the "resolution confirmed" rubric item QA scores it against*

### Explicitly OUT of scope
- *Fraud holds and collections — a different queue with a different authority chain*
- *Manual refund cheques and anything that leaves the billing platform for the payments team*
- *Enterprise accounts, which sit on a separate billing stack*
- *Credits Billing Ops raises proactively with no customer contact — no dispute, so no reopen to avoid*

### How many cases the scope contains

Scope is not agreed until you can say how many cases a year fall inside it. That count, and nothing wider, is the denominator every later benefit claim multiplies.

| | |
|---|---|
| **In scope, measured** | *966 adjustment contacts in the baseline month, 137 of them reopened inside 7 days — the 14.2% that is this project's Y, under OD-BIL-004-ADJ (09-baseline-document.md:90; the same 966 at 14-root-cause-evidence-pack.md:131, where 137 reopened and 829 not sum to it, and at 16-pilot-protocol.md:178, where the pilot's benefit starts from it). It counts the same population this page scopes, chat included, so it can stand as the size of the scope: the definition excludes no channel (04-operational-definition.md:37, Known limitations) and 06-data-lineage.md:62 states the OD-BIL-004-ADJ population as voice/chat/email. The legacy filter that drops chat sits downstream on the Looker Ops weekly tile at hop 6 (06-data-lineage.md:31, :70), which reads the whole-queue rate and not this one* |
| **In scope, annualised** | *966 x 12 = 11,592 adjustments a year — the only population a benefit for this project may be multiplied by. It is one measured month annualised: the reporting team who pulled the queue volume (01-project-charter.md §3) still owes a 12-month `dw_ticket_fact` pull filtered to the scope rows above, and until that pull lands this row stays a 12x extrapolation of one month. The gate it was once owed to has closed — the Improve tollgate was held 2026-09-25, and the benefit was re-stated not there but at the Control gate on 2026-12-18, where it was found not to clear the Finance floor (01-project-charter.md §8, Milestones) — so the pull is due before the 90-day checkpoint on 2027-02-12 (18-handover-and-benefit-validation.md:142, Part D), the deadline that document's own open blanks already run to (:96)* |
| **Context, never a multiplier** | *The whole Billing queue: 61,400 tickets counted over the 12-week baseline window, which is ~5,100 a week (09-baseline-document.md:51 — 12 weeks, not a quarter), and 266,000 a year (01-project-charter.md §3, where it is marked context only). The 61,400 is the count and the ~5,100 is the rate rounded down out of it (61,400 ÷ 12 = 5,117), so read it in that direction only — multiplying the rounded week back up gives 61,200 and loses 200 real tickets. It carries its own 7-day reopen rate, OD-BIL-004 v2, which also reads 14.2% on that far wider population* |
| **Why the two must never be mixed** | *In-scope adjustments are 11,592 of the queue's 266,000 contacts, and their reopens are 11,592 x 14.2% = 1,646 against the queue's 266,000 x 14.2% = 37,772 — 4.4% of each. Fix every adjustment reopen and the queue rate moves from 14.2% to (37,772 − 1,646) / 266,000 = 13.58%, a 0.62-point move. The benefit case first written for this project applied the adjustment-scoped 6.2-point gap (09-baseline-document.md:105) to the queue's 266,000: ten times the arithmetic maximum. A rate measured on one population and a volume taken from another is how a benefit case dies — and this one did. Rebuilt on the population it may actually be multiplied by, the chain runs 11,592 x 6.2 points = 719 reopens avoided a year, x $38.60 a reopened contact = $27,753 gross, x 0.85 realization = $23,590 realized, against the $50,000 realized floor Finance books against: **the project does not clear the floor**, and that is before the handle time the fix adds is taken off it (09-baseline-document.md:121; 01-project-charter.md §11). The 11,592 in that chain is still the 12x extrapolation of the row above* |

## Process inputs classified

| Input (x) | Controllable | Noise | SOP-fixed | Notes |
|---|---|---|---|---|
| *How the billing queue routes — one queue for everyone, or skill-based to billing-trained agents* | *x* | | | *We set this ourselves in the routing rules. Its handle-time effect is `<not measured — no trial result for it exists in the pack>`; R. Okonjo, Tier 1 team lead and owner of the AHT scorecard (01-project-charter.md §7), to measure it before the 90-day checkpoint on 2027-02-12 (18-handover-and-benefit-validation.md:142, Part D). The Improve tollgate this was once owed to was held on 2026-09-25 and Control closed on 2026-12-18 (01-project-charter.md §8), so the checkpoint is the next gate that can take it* |
| *Adjustment authority limit — $50 for Tier 1, $250 for Billing Ops* | | | *x* | *Set by the Finance delegation-of-authority policy. Raising it is a policy request, not a process change* |
| *Whether the knowledge article is shown to the agent at the point of raising the adjustment* | *x* | | | *A toggle in the agent desktop. No cost or effort is stated for either controllable change anywhere in this file, so it is not ranked against the routing row above. Its handle-time effect is `<not measured — same gap as the routing row>`; R. Okonjo to measure it alongside the routing change, before the same 2027-02-12 checkpoint* |
| *The 02:00 nightly posting batch window* | | | *x* | *Owned by the billing platform vendor and fixed in the run schedule; a second run needs a contract change, so treat it as fixed here* |
| *When the dispute arrives, and where it falls in the billing cycle (the 12th to the 18th)* | | *x* | | *Volume roughly doubles across the cycle peak. We cannot move when customers call, so block on cycle week in the analysis instead of trying to control it* |

## Reviewed with process owner
Name: ____________  Signature: ____________  Date: __________
