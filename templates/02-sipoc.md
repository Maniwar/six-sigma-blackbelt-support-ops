# SIPOC — <Process name>

<!-- guidance -->
## How to use this

**What it is for.** The boundary diagram. It settles what is in scope before anyone argues about it in week six.

**When.** Define, in the first workshop, on a wall, with the process owner in the room.

**Who signs it.** Black Belt facilitates · Process owner agrees the boundaries

**The mistake this prevents.** Writing the process you wish you had rather than the one that runs. Walk it before you draw it.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate against a target of 8%. Delete them as you fill your own in.*

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

## Process inputs classified

| Input (x) | Controllable | Noise | SOP-fixed | Notes |
|---|---|---|---|---|
| *How the billing queue routes — one queue for everyone, or skill-based to billing-trained agents* | *x* | | | *We set this ourselves in the routing rules. Skill-based routing took 29 s off handle time in the trial* |
| *Adjustment authority limit — $50 for Tier 1, $250 for Billing Ops* | | | *x* | *Set by the Finance delegation-of-authority policy. Raising it is a policy request, not a process change* |
| *Whether the knowledge article is shown to the agent at the point of raising the adjustment* | *x* | | | *A toggle in the agent desktop, and the cheapest of the three changes to switch on — worth 22 s* |
| *The 02:00 nightly posting batch window* | | | *x* | *Owned by the billing platform vendor and fixed in the run schedule; a second run needs a contract change, so treat it as fixed here* |
| *When the dispute arrives, and where it falls in the billing cycle (the 12th to the 18th)* | | *x* | | *Volume roughly doubles across the cycle peak. We cannot move when customers call, so block on cycle week in the analysis instead of trying to control it* |

## Reviewed with process owner
Name: ____________  Signature: ____________  Date: __________
