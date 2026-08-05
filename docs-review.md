# Markdown template review — findings

> **Status: a point-in-time audit, not a live worklist.**
>
> Recorded 2026-08-01 at commit `bbbcd23` and never updated. Two things follow
> from that, and both matter before you act on anything below.
>
> **The `L` numbers are stale.** They address lines as they stood at `bbbcd23`.
> Several of these documents have gained and lost lines since, so an `L50` here
> is not `L50` today. Search for the quoted text instead of trusting the number.
>
> **Nothing below records whether it was fixed.** Every finding is marked
> CONFIRMED and carries a prescriptive **Fix.**, in the present tense, because
> that is how it was written — not because it is still open. A good many have
> since been closed, and this file cannot tell you which. What is known:
>
> | Cluster | Where it stands |
> |---|---|
> | The population / volume / unit-cost disagreement — the theme of the note below, and of most of the high findings | Closed in v3.9. The worked example runs the charter's chain: 11,592 in-scope adjustments, $38.60 a reopen, $23,590 realised, under the $50,000 floor. `verify` now reads the volume, population, unit cost and floor from `01-project-charter.md` rather than from the page, so the two cannot drift apart again |
> | The baseline window stated as a calendar quarter | Closed in v3.9, and checked against `09-baseline-document.md` |
> | Gage R&R teaching the sampling bias backwards | Closed in v3.9, in both the `.md` and the workbook cell that duplicated it |
> | Fleiss' kappa cited but never implemented | Closed in v3.9 — the template now says the pack does not compute it, and gives the pairwise route that it does |
> | The VOC plan's unowned methods, and VOB / VOE undefined | Closed in v3.9 |
> | The operational definition's blank two-observer test | Closed in v3.9 |
> | Everything else | **Not re-audited.** Some is closed, some is not, and telling them apart means re-reading the document rather than trusting this file |
>
> Release notes are the record of what actually changed: see `CHANGELOG.md`.
> If you want this file to be a worklist again, the honest move is to re-run the
> audit against the current documents rather than to tick boxes here.

Eleven documents read line by line and adversarially verified. 86 findings confirmed
(31 high, 49 medium, 6 low); 12 rejected as taste or
already covered by the machine audits.

These are NOT independent edits. The pack runs one worked example — the billing
adjustment project — through all eleven documents, and the numbers do not reconcile
across them. Most of the high findings are one disagreement seen from a different
document. Fixing them one at a time would produce a differently inconsistent pack.

## 01-project-charter.md

### L50 · WRONG · high

> *16,492 reopens avoided a year — 266,000 x 6.2 points*

CONFIRMED (with one citation corrected). The two rows above this one name two different populations. Line 48 sources the 14.2% to the Zendesk view "Billing adj — reopened <7d" counted per OD-BIL-004 v2 — and 09-baseline-document.md line 24 names that metric '7-day reopen rate, billing ADJUSTMENTS'. Line 47 sources the 266,000 to `dw_ticket_fact`, queue = Billing — every billing ticket. The benefit then multiplies the adjustment rate by the whole-queue volume. 09-baseline-document.md line 90 puts the in-scope adjustment population at 966 contacts (line 106: '966' a month), i.e. 11,592 a year — 23x smaller. The pack states three different volumes for the same worked example: 266,000 (charter), 11,592 (09 §5/§7), and 480,000 (curriculum case study, six-sigma-blackbelt-support-ops.html line 2328: 'billing support queue was 14.2% against a target of 8.0%, across 480,000 contacts'). Everything downstream scales with the choice: the $112,146, the 1.2 FTE, and the 3.3-point practical threshold. CORRECTION to the report: the warning text 'Annual volume for the queue your project covers. Not the whole contact centre…' is cell D5 of sheet '7 Benefit — AHT', not sheet '8 Benefit — avoided contacts' (whose D5 reads 'Contacts per year in the queue you are working on.'). Right workbook, wrong sheet — the substance stands.

**Fix.** Decide which population the 14.2% is measured on and use its volume everywhere. If the metric is adjustments only, the volume is 966/month = 11,592/yr (and the project as scoped falls under the $50,000 floor in section 5, which the template should say out loud). If the project is the whole billing queue, re-baseline the rate on that denominator and make 09 §5 and the curriculum case study agree. Do not leave the rate and the volume measured on different populations.

### L51 · CONTRADICTION · high

> *$6.80 fully-loaded cost per contact*

CONFIRMED. 01 and 09 carry the same worked example (identical italic note at line 14 of both, same Black Belt, same Finance partner, same 14.2% -> 8.0%) and cost it differently by a factor of six. This charter: $6.80 a contact, $112,146 gross (line 52), $95,324 realised (line 54). 09-baseline-document.md line 107 records the CHARTER's figure as '$41.00', revised to '$38.60'; line 105 records 'Charter's $425k/yr gross' revised to $376k; line 108 ends at $180k Finance-validated. 09 also attributes a 15.0% -> 8.0% gap 'from the 2025 ops dashboard' to the charter, where this charter records 14.2% from a Zendesk view. These are two different quantities never distinguished anywhere in the pack — average cost to serve ($6.80) versus marginal cost of a reopened contact ($41.00) — and 09's column is headed 'Charter estimate', so it is quoting numbers that do not appear in the charter. A reader who downloads both cannot tell which basis Finance accepts, and cannot use 09 section 7, which exists precisely to show a charter number being revised.

**Fix.** Pick one basis and propagate it. If $6.80 is intended, change 09 line 107 to '$6.80 / $6.40' and restate 09's benefit column in those units; if $41.00 is intended, restate charter lines 51, 52, 54 and the derivation at 99-101. Either way 09's 'Charter estimate' column must quote numbers that actually appear in 01, and the pack should say once, somewhere, which of the two cost concepts a benefit case uses.

### L64 · CONTRADICTION · high

> **Harvest mechanism** (required — how does this reach the P&L?):

CONFIRMED. The charter makes the harvest mechanism mandatory and calls its absence 'The mistake this prevents' (line 12). The workbook it sends the reader to for exactly this benefit type says the opposite. 19-black-belt-calculators.xlsx, sheet '8 Benefit — avoided contacts' — the sheet whose inputs the example uses verbatim (B6 0.142, B7 0.08, B8 6.8, B9 0.85) — has D12: 'Contacts that simply never happen. Unlike a handle-time saving this needs no harvesting argument, because the work is not there to be redeployed.' The companion sheet '7 Benefit — AHT' carries the opposite instruction at A17 ('none of this is real money unless the capacity is actually harvested… name the harvest mechanism'). The workbook is the one that is wrong: 09-baseline-document.md line 108 shows this very project failing to harvest ('No reduction is available: the billing queue is already 4 heads below its approved establishment… The remaining $130k returns as capacity against service levels, not as cash'). A reader who follows the charter's pointer, opens sheet 8 and reads D12 concludes the required section does not apply to them.

**Fix.** Change D12 in sheet '8 Benefit — avoided contacts' to: 'The harvesting argument is easier here than for a handle-time saving — the work is not there to be redeployed — but it is still required: name what changes in the establishment, the hiring plan or the outsourcer commitment.' Leave charter line 64 as it stands.

### L66 · WRONG · high

> of handle time is 1,887 agent hours, about 1.2 FTE at 1,530 handling hours a head.

CONFIRMED, and stronger than reported — the sign is wrong at any volume. The harvest block counts only the handle time removed. Line 123 of the same document discloses the handle time added: verifying the posting before closing 'adds roughly 40 s to a 412 s contact', with the team target moved 412 s -> 450 s. Break-even is volume-independent: you spend 40 s on every in-scope contact to avoid 6.2% of contacts costing 412 s each, i.e. 0.062 x 412 = 25.5 s of saving per contact against 40 s of cost. Per 100 contacts: +4,000 s spent, -2,554 s saved. On the charter's own 266,000 that is 2,956 hours added against 1,887 saved (net +1,069 hrs, ~0.7 FTE MORE); on the 11,592 adjustments denominator it is 129 hrs added against 82 saved. Priced at the charter's own $6.80/412 s, the added handle time is $175,560 a year against a $112,146 gross benefit. The charter asks WFM to sign a 1.2 FTE cut off a calculation that, completed, requires more staff.

**Fix.** Net the disclosed cost before quoting FTE: (reopens avoided x 412 s) less (in-scope contacts x 40 s), divided by 1,530. State the result even when negative, and add a line requiring every metric-impact disclosure in section 7 to be priced and subtracted from the benefit. Ask WFM to sign the net number.

### L101 · CONTRADICTION · high

> year is 3.3 points. So a drop smaller than 3.3 points (14.2% to 10.9%) is a null

CONFIRMED. Three documents give this project two different practical-significance thresholds. The charter derives 3.3 points here (internally sound: $50,000/0.85 = $58,824; /$6.80 = 8,650; /266,000 = 3.3 pts) and then sends the reader to 13-hypothesis-test-log.xlsx three lines later. Row 11 of that workbook is this same project's same test — B11 'Did the deferred-close rule cut reopens?', C11 '2-proportion test' — carrying M11 = '1.5 pts', and O11 reads 'Reopens fell 4.9 points, well past the 1.5 we agreed mattered'. The curriculum case study agrees with the workbook, not the charter: six-sigma-blackbelt-support-ops.html line 2342, 'Practical significance | 1.5 percentage points (derived: $49k benefit ≈ minimum worth pursuing)'. The gap is entirely the volume ($49k/$6.80/480,000 = 1.5 pts vs the charter's 266,000). A 2-point drop is a null result in one document and a win in the other, and the reader cannot tell which their tollgate will apply.

**Fix.** Settle the volume first (see the line 50 finding), then make all three agree. Whichever number survives must appear identically in the charter derivation, in M11 of 13-hypothesis-test-log.xlsx, and in the case-study charter table on the curriculum page.

### L115 · CONTRADICTION · high

> *Exactly one A per row.*

CONFIRMED. Section 6 is a person-per-row table with a single R/A/C/I cell per person, so 'exactly one A per row' is satisfied by construction on every row anyone will ever write — the rule cannot fail. Meanwhile the worked example puts A against both M. Berenji (line 110, Black Belt) and R. Mehta (line 111, Champion): two Accountables for one project, with the process owner given R. That is precisely the failure mode 22-stakeholder-and-raci.xlsx exists to catch — its 'How to use this' B13 reads 'The count column flags any row that does not have exactly one Accountable. Fix every flag before you leave the tollgate — "we are both accountable" means nobody is', its RACI sheet A23 reads 'A = owns the outcome (exactly one)', and the curriculum page (line 2558) advertises the workbook as flagging 'the two failure modes: no A on a row, or an A on every row.' A reader checks their charter against the stated rule, passes, and walks into the tollgate with two Accountables.

**Fix.** Match the rule to the layout: 'Exactly one A in the whole table — the Champion or process owner is A for the outcome, the Black Belt is R for delivery. Two names carrying A means nobody does.' Then fix one of the two A rows in the example, or replace section 6 with the activity-by-role grid used in 22-stakeholder-and-raci.xlsx, where 'one A per row' is meaningful.

### L27 · CONTRADICTION · medium

> | Target close date | *2026-10-30* |

CONFIRMED — the plan cannot deliver its own Control gate on either reading. Line 137 puts Control at 2026-09-28 with the outcome '90 days of control data, benefit validated'. 90 days is a programme rule, not a preference: 18-handover-and-benefit-validation.md line 8, 'Control, after 90 days of control data — not at the end of the improvement', line 56 'Control period end | (minimum 90 days)', and the curriculum page line 936, 'Minimum 90 days of post-implementation control data before benefits are certified.' If the 90 days run from the Control gate, certification lands 2026-12-27, eight weeks past target close. If they end at the gate, they would have to start 2026-06-30 — before the Improve gate at 2026-07-27 (planned Improve->Control is only 63 days). The same worked example in 18 settles it: implementation 2026-08-03, control start 2026-08-04, 91 days of data, Finance signature 2026-11-20 — three weeks after this target close. The charter's own Actual column concedes 2026-12-18 while the target close is left unrevised at v1.0.

**Fix.** Set the target close at least 90 days after the planned Control tollgate, or add a note to the Milestones table: 'The target close date must be at least 90 days after the Control tollgate; benefit cannot be certified before then.' If 'target close' means improvement-complete rather than benefit-certified, rename the field and say which.

### L91 · HOLLOW · medium

> | Secondary | *Median resolution time, billing* | *4.6 h* | *4.0 h* | *OD-BIL-007 v1* |

CONFIRMED. Line 91 is character-for-character identical to line 90, and lines 92/93 repeat each other the same way. The table looks like it demonstrates two secondary and two counter-balancing metrics; it demonstrates one of each, twice. The same duplication appears in 16-pilot-protocol.md lines 106/107, so it is a production defect, not a deliberate 'add a second row' prompt. A reader cannot tell whether the repeat is an error or a signal that two are expected, and if they read it as the model answer they take one secondary metric to the tollgate where the curriculum's model charter (six-sigma-blackbelt-support-ops.html line 2342) names three secondary metrics (billing AHT; contacts per resolved issue; Tier-2 touch rate) and four counter-balancing (billing CSAT; first-response time; agent QA score; credit spend per contact).

**Fix.** Replace line 91 with a genuinely different secondary metric (e.g. 'Contacts per resolved issue, billing | 1.34 | 1.10 | OD-BIL-009 v1') and line 93 with a second counter-balance such as first-response time or credit spend per contact — or delete both duplicates and leave one blank row of each type. Fix 16-pilot-protocol.md lines 106/107 in the same pass.

### L92 · UNFOLLOWABLE · medium

> | Counter-balancing | *CSAT, billing contacts* | *4.11* | *no decline* | *OD-CX-002 v3* |

CONFIRMED, and corroborated by a sibling template. Line 41 of this document requires a tolerance ('while holding `<counter-balancing metric>` within `<tolerance>`'); 'no decline' is a zero tolerance on a five-point-scale mean from a responding sample, so it trips on noise or is adjudicated by eye. The pack itself knows better: 16-pilot-protocol.md line 84 gives the same metric a real tolerance — 'CSAT, billing adjustments | 4.11 out of 5 | No decline greater than 0.15'. Worse, the metric this project knowingly degrades is absent from section 5 entirely: line 123 discloses handle time rising 40 s on 412 s (+9.7%) with the target moved to 450 s, while 16-pilot-protocol.md line 83 sets the AHT counter-balance at 'No more than +8% (445 s)' and line 60 makes 'handle time up more than 8%' a stopping rule — so the charter authorises a target change that would trip the pilot's own stopping rule, with no guardrail in the charter to catch it. The curriculum's model charter (six-sigma-blackbelt-support-ops.html line 2334) does both properly: 'holding billing AHT within +5% and billing CSAT at or above baseline.'

**Fix.** Give CSAT the tolerance the pilot protocol already uses ('no decline greater than 0.15 on a rolling 4-week mean'), and add an AHT counter-balancing row consistent with 16-pilot-protocol.md: 'AHT, Tier 1 billing queue | 412 s | not above 445 s (+8%), no point above the 468 s UCL | OD-…'. Then reconcile the 450 s in line 123 with it.

### L104 · UNFOLLOWABLE · medium

> `13-hypothesis-test-log.xlsx`, which picks the test and prints the decision rule

CONFIRMED in substance, with one half of the report overstated. The sentence instructs the reader to 'run it [a two-proportion test] in 13-hypothesis-test-log.xlsx'. That workbook has two sheets, 'How to use this' and 'Test log', and computes no test statistic: 'How to use this' B11 says 'Type the p-value, the effect size and the practical threshold, and the sheet decides'. Nor does it pick the test — its own C8 says 'WHICH TEST GOES IN THE TEST COLUMN — the log never named one, and eight tools in the library send you here', then lists options for the analyst to choose from. (The report's claim that it does 'neither of the two things claimed' is half wrong: column N does apply and print the decision rule.) No workbook in the pack computes a two-proportion p-value — 19-black-belt-calculators.xlsx has sheets for sigma level, kappa, SLA capability, backlog, process efficiency, staffing, two benefit sheets and ROI; 30-regression.xlsx has simple, multiple and logistic regression. A reader opens the file expecting a calculator, finds a register, and has nowhere in the pack to get the number the practical-significance test depends on.

**Fix.** Rewrite as: 'Compute the two-proportion p-value, effect size and 95% CI in your statistics tool (Minitab: Stat > Basic Statistics > 2 Proportions), then record the test, p-value, effect size and practical threshold in 13-hypothesis-test-log.xlsx, whose "Above threshold?" column applies the decision rule.' If the pack is meant to be self-sufficient, add a two-proportion sheet to 19-black-belt-calculators.xlsx and point at that.

### L127 · UNFOLLOWABLE · medium

> Signed by affected ops leader: ____________________  Date: __________

CONFIRMED. One signature line sits under a table naming three different scorecard owners — R. Okonjo (Tier 1), A. Okafor (Billing Ops), L. Haddad (QA) — with three different names in the 'Agreed by' column (R. Mehta, A. Okafor, L. Haddad). The reader cannot tell whose signature makes the disclosure valid, and this is not a soft point: the curriculum page (line 1244) makes the metric-impact disclosure a mandatory charter clause and closes with 'Unsigned, the project does not start.' A reader collects one signature, believes the clause is satisfied, and two leaders have not agreed to the target changes their teams will be measured against.

**Fix.** Replace the single line with one signature row per affected scorecard, keyed to the table above ('| Scorecard | Leader | Signature | Date |'), under the instruction 'Every leader named in the Owner column above signs. An unsigned row means the project does not start.'

### L143 · WRONG · medium

> *If it cannot move, anything raised after 17:00 still waits overnight and the 960-minute wait survives the project*

CONFIRMED. The 960 minutes belongs to a different step with a different owner. In 10-value-stream-map.xlsx, 'Value stream' sheet, step 6 (row 15) is 'Waits for the nightly adjustment batch', F15 = 720 minutes, note 'Cut-off is 18:00; miss it and you wait another day'. Step 8 (row 17) is 'Waits for the customer to confirm', F17 = 960 minutes, note 'Nothing chases the customer; this is the longest single wait'; the waiting-states block repeats it at E44 as 'the single largest block of lead time in the whole stream', owner 'Nobody'. The charter attaches the largest number in the stream to the vendor's batch — the one wait it has no authority over — and never mentions the longer wait that is inside the team's control and costs nothing to fix. A reader sizing this risk trades a contract negotiation for what they believe is 960 minutes when it is 720.

**Fix.** Correct the figure ('…the 720-minute batch wait survives the project') and add the customer-confirmation wait as its own risk row — 960 minutes, in scope, mitigation a chase/reminder, owner Tier 1 — since nothing in the charter currently names the longest wait in the process.

## 02-sipoc.md

### L60 · CONTRADICTION · high

> *Owned by the billing platform vendor and fixed in the run schedule; a second run needs a contract change, so treat it as fixed here*

CONFIRMED. The SIPOC ticks the batch window as SOP-fixed and tells the reader to treat it as immovable. The charter for the same project records the opposite at line 143: 'Change request raised at Define, not at Improve. Fallback agreed with the vendor: a second 14:00 run for adjustments under $250' — the change request is in and the vendor has already agreed a second run. The classification is load-bearing: the curriculum page (line 2276) says 'For each input, classify it controllable / noise / SOP-fixed — this seeds your x list' and 'The input classification becomes the first draft of your Y = f(x) equation.' So the SIPOC removes from the improvement search the input that 09-baseline-document.md lines 86 and 88 show carries 37% + 33% = 70% of the reopen gap, and it never reaches 11-cause-effect-xy-matrix.xlsx.

**Fix.** Reclassify as Controllable with the note: 'Owned by the billing platform vendor. Moving it needs a contract change, so it is slow, not fixed — a change request is in and a second 14:00 run is agreed as a fallback (see the charter risk table). Carry it into the X-Y matrix.' If exclusion is genuinely intended, delete the vendor fallback from charter line 143 so the two documents stop disagreeing about whether the biggest lever can move.

### L43 · CONTRADICTION · medium

> *Adjustments up to the $250 Billing Ops authority limit, including the ones Tier 1 hands over because they exceed $50*

CONFIRMED. This caps in-scope work at $250. The charter — which its own line 6 says nothing in the project may contradict — puts 'Billing adjustments, all channels, all sites' in scope (line 79) and lists only fraud holds, collections and manual refund cheques out (line 80). Adjustments above $250 must exist, since Tier 1 escalates above $50 and Billing Ops stops at $250, yet no template in the pack routes them: grep across templates/*.md finds $250 only in this line, in the SIPOC process step 3 and input table, and in the charter's vendor fallback. SIPOC step 3 ends at 'approves or rejects', so an over-limit request has nowhere to go. Two documents going to the same tollgate carry different boundaries, which is the exact argument the SIPOC's own purpose statement (line 6, 'settles what is in scope before anyone argues about it in week six') claims to settle.

**Fix.** Make the two agree and show the exception. Either add 'Adjustments above the $250 Billing Ops authority limit — they route to Finance delegation and follow a different approval chain' to the OUT list here AND to charter line 80, or drop the cap here. Either way, add a line to the process column showing where an over-limit adjustment goes.

### L44 · CONTRADICTION · medium

> *The nightly 02:00 posting batch and the wait in front of it — anything raised after 17:00 misses that night's run*

CONFIRMED on both counts. (a) The cut-off disagrees with the value stream map for the same process: 10-value-stream-map.xlsx step 6 (row 15) records 'Cut-off is 18:00; miss it and you wait another day', while 01-project-charter.md line 143 and the whole stratified baseline in 09-baseline-document.md lines 85-88 use 17:00. Three documents say 17:00, one says 18:00, and the 09 stratification that assigns 70% of the gap turns on exactly that boundary. (b) The rule is asserted without its mechanism — a batch that runs at 02:00 does not obviously exclude work raised at 17:30, nine hours earlier — and the VSM's own step 4 has Billing Ops pulling the queue once a day at 10:00, which would bite long before 17:00. That matters because the charter's fallback (line 143, 'a second 14:00 run') moves the RUN time, which does nothing for work that arrives after a file cut-off; the reader cannot tell which of the two is the lever.

**Fix.** State the mechanism and reconcile the time: 'The nightly posting batch and the wait in front of it — approved adjustments are cut into the batch file at 18:00 and the batch runs at 02:00, so anything approved after the cut-off waits for the following night.' Use one cut-off across 01, 02, 09 and step 6 of 10-value-stream-map.xlsx, and make the mitigation name whichever of run time or cut-off is actually being changed.

### L59 · UNFOLLOWABLE · medium

> *A toggle in the agent desktop, and the cheapest of the three changes to switch on — worth 22 s*

CONFIRMED. 'the three changes' has no referent. 'three' appears exactly once in the whole 64-line file — in this note — and no set of three changes is listed here or in the charter or the baseline document. The table classifies five inputs, of which two are ticked Controllable (this row and the routing rule at line 57), so a reader looking for the third candidate to compare against finds nothing. The same note also ranks a candidate change in seconds of handle time ('worth 22 s', and '29 s' on line 57) when the project's Y is the 7-day reopen rate — so the only comparison the classification offers is made on a metric the project is not trying to move and which charter line 123 says will get worse.

**Fix.** Name the set or drop the comparison: 'A toggle in the agent desktop — the cheapest of the controllable inputs to switch on, and the only one that needs no vendor involvement.' If a ranking belongs here, rank against the Y; otherwise say plainly that ranking happens in 11-cause-effect-xy-matrix.xlsx and use Notes to describe the input.

## 03-voc-ctq-tree.md

### L22 · UNFOLLOWABLE · medium

> *Only 14% respond — survivorship*

The Who column carries a bias or method note in all six rows and never names anybody: "Only 14% respond — survivorship", "Topic-modelled, then read 200 by hand", "Recruited from reopens, so biased to failure", "Small n, high signal". Bias already has its own column at the far right, and the sampling approach that belongs under Sample plan has been pushed into Who, leaving Sample plan holding durations ("12 weeks", "4 weeks") that the When column then repeats. The pack's own collection-plan workbook shows what the column is for: 05-data-collection-plan.xlsx, sheet "Collection plan", has "Who collects" = "Analytics" and "Owner" = "M. Berenji". A reader who copies the worked example here produces a collection plan in which no method has an owner.

**Fix.** Put a named person or team in Who (*R. Patel, Insight*), move the sampling approach into Sample plan (*Topic model all 8,400, then hand-read a stratified 200*), and leave the dates in When.

### L41 · CONTRADICTION · medium

> | Need | Must-be | Performance | Delighter | Evidence |

Three category columns, where the pack's own Kano workbook returns six. 23-kano-analysis.xlsx, sheet "Kano analysis", rows A28–A33 list "Must-haves", "Performance", "Delighters", "Indifferent — stop spending here", "Reverse — you are actively annoying people", "Questionable — the answers contradict; re-ask", and the sheet's Category column is derived automatically from the functional/dysfunctional pair. A reader whose need comes back Indifferent or Reverse has no column to record it — and the workbook says those are the verdicts the exercise exists to produce (its own worked row A14, "A survey after every single contact", is a Reverse). The document never names the workbook, so the reader also has no pointer to where the categories come from, in a pack whose other templates do cross-reference their workbooks.

**Fix.** Add Indifferent, Reverse and Questionable columns, and one line under the heading: "Categories come from `23-kano-analysis.xlsx`, which derives them from the paired functional/dysfunctional answers — copy its Category column into this table." Do not rename "Must-be": the curriculum page uses Must-be and the workbook uses Must-have, so the naming needs settling across all three, not changing here alone.

### L61 · CONTRADICTION · medium

> *Warehouse query OD-BIL-004*

Rows 1 and 3 of the CTQ tree are the same measurement — a 7-day reopen rate on all billing tickets, census, spec <= 8.0% — but row 1 cites OD-BIL-004 and row 3 cites OD-BIL-004 v2. The version is load-bearing in this pack: 04-operational-definition.md line 44 records that v1 counted same-reason reopens only until it was settled in favour of any reason on 2026-04-24 and the baseline was recut. Everywhere else the project Y is cited only as v2 (01-project-charter.md lines 48 and 89, 06-data-lineage.md line 50, 09-baseline-document.md line 25, and this document's own line 72). The table defines the primary metric twice against two different definitions and so fails the completion test printed at line 65; a reviewer cannot tell which version the 8.0% target was set against.

**Fix.** Keep one row for the 7-day reopen rate citing *OD-BIL-004 v2*, and list both needs against it ("Do not make me chase it" / "Do not make me repeat myself"). Delete the duplicate row so the table carries three distinct CTQs.

### L62 · CONTRADICTION · medium

> *QA audit item 7*

CTQ 2 ("Share of contacts with a commitment logged") is to be measured by QA audit item 7. In the same worked example, 07-msa-attribute-agreement.md line 87 records "Item 7 — empathy demonstrated" at kappa 0.58, verdict "Unacceptable (<0.60)", action "Write a partial-credit rule with worked examples, or drop the item." No item in 07's rubric table (items 1, 2, 3, 4 and 7) is about a commitment date. So the reference either points at the wrong item, or specifies the CTQ against the one item the pack's own MSA has condemned — an item two analysts demonstrably score differently, which is what the completion test at line 65 forbids. The reader cannot follow the reference and cannot defend the CTQ if a reviewer reads both templates.

**Fix.** Name the rubric item by its wording rather than its number: *QA rubric item "commitment date logged"*, and add a line under the table: "Any CTQ measured by QA scoring needs a passing attribute agreement study (07-msa-attribute-agreement.md) before its spec is used."

### L73 · CONTRADICTION · medium

> | *Share of adjustments confirmed posted before the case is closed* | *9* |

Section 5 weights four CTQs; only two of them exist in the section 4 CTQ tree. This one and Mean handle time have no spec, no measurement method, no population and no sampling anywhere in the document, yet they carry weights of 9 and 4 into the X-Y matrix. The "How to use this" sheet of 11-cause-effect-xy-matrix.xlsx states the rule this breaks, cell B14 verbatim: "Weights come from the CTQ tree, which came from customers. If the team invents the weights in the room, you have built an opinion aggregator, not a prioritisation." Its sheet 2 step 1 repeats it. The reader types two unmeasured requirements into the workbook and gets a cause ranking half of which rests on nothing.

**Fix.** Either add these as rows 4 and 5 of the section 4 table with a spec, method, population and sampling, or delete from section 5 anything the tree does not carry. Add under the section 5 heading: "Every row here must already exist in section 4 — the weight is the tree's, not the room's."

### L75 · WRONG · medium

> | *Mean handle time* | *4* | *A guardrail rather than a goal: it is on the list so a fix cannot buy the reopen rate back with a longer call.

A metric the row itself calls "a guardrail rather than a goal" is given a weight in the table that "feeds the X-Y matrix". In 11-cause-effect-xy-matrix.xlsx the weight means something specific — sheet 1 B7: "Weight each one 1 to 10 by how much it matters to the customer" — and the cause scores carry no direction (sheet 2 row 13: "9 = strong · 6 = moderate · 3 = weak · 1 = none"). A candidate cause scored 9 against this column therefore gains 36 weighted points and climbs the test list, so the guardrail promotes exactly the causes it exists to police. The curriculum keeps the two apart: the Define tollgate asks for "Primary metric, secondary metrics and at least one counter-balancing metric defined", and 01-project-charter.md line 92 already carries a Counter-balancing row, which names CSAT, not handle time.

**Fix.** Remove Mean handle time from the weighting table and record it in the charter's metric hierarchy as a counter-balancing metric with its limit and the action on breach. Add to section 5: "Guardrails get no weight here — the X-Y matrix has no direction, so weighting a guardrail turns it into a goal."

### L27 · UNDEFINED · low

> Internal (VOB / VOE)

Neither abbreviation is expanded anywhere — not in this document, not in any other template, and not in the curriculum page's prose (grepping the non-template body of six-sigma-blackbelt-support-ops.html for "VOB", "VOE", "Voice of the Business" and "Voice of the Employee" returns nothing; only Voice of the Customer and voice of the process are spelled out). This is the only row that tells the reader to collect internal voice at all. A support manager who is the only Black Belt in the organisation has no way to decode the row and drops the only non-customer input in the plan. Note that the reporter's claim that the curriculum page spells them out in a module title is false — the gap is pack-wide, not a loss on download.

**Fix.** Write the row as "Internal — Voice of the Business (VOB) and Voice of the Employee (VOE)", and consider splitting it, since the agent forum is VOE and the QA notes are VOB, with different populations and different biases.

## 04-operational-definition.md

### L22 · CONTRADICTION · high

> | **What is counted (numerator)** | *Tickets with a reopen event 0<t<=168h after first Resolved* |

The numerator counts any reopen event and neither Inclusions, Exclusions nor Business rules says who may raise one; 06-data-lineage.md line 50 states the v2 formula the same way ("any reopen event"). The worked example at line 47 then excludes TCK-118455 because "The metric says the customer reopens it" — a restriction that exists only in the plain-language row at line 21 and in the example's own reasoning, not in the field an analyst turns into SQL. It is not a rare class: the auto-reopen fires when the nightly posting fails, which is the project's failure mode, so this rule decides whether the defect's own early warning lands in the numerator.

**Fix.** Change the numerator to *Tickets with a customer-raised reopen event 0<t<=168h after first Resolved*, and add to Exclusions: *Reopens raised by system or service accounts (e.g. the posting-failure job) — tracked separately as posting failures, and brought back in if auto-reopen ever notifies the customer.*

### L26 · CONTRADICTION · high

> | **Inclusions** | *All channels; all billing contact reasons; all tiers* |

Line 26 includes all channels; line 35 says "Excludes chat until the channel field is backfilled; understates by roughly 0.4 points". The same page tells an analyst both to include chat and that chat is out. 06-data-lineage.md line 50 settles it the other way — OD-BIL-004 v2 is "any reason, all channels", 14.2% — and line 57 records the chat filter as a defect on the Looker tile (hop 6), "Open, target 12 Jun", worth about 0.4 points, not as a property of the definition. Against a 6.2-point gap, 0.4 points is the difference between the charter's 14.2% and 14.6%; two analysts working from this page hand in two different baselines, the exact failure line 6 promises to prevent.

**Fix.** Make Inclusions read *All channels, chat included; all billing contact reasons; all tiers*, and rewrite Known limitations to place the exclusion where the lineage doc puts it: *The Ops weekly Looker tile still drops chat through a legacy filter (lineage doc, hop 6, open to 12 Jun). This definition does not — a figure 0.4 points lower is the tile, not this metric.*

### L20 · UNFOLLOWABLE · medium

> | **Metric name** | *7-day reopen rate, billing adjustments* |

Four other documents cite this metric by an identifier and a version — 01-project-charter.md lines 48 and 89, 03-voc-ctq-tree.md lines 63 and 72, 06-data-lineage.md line 50, 09-baseline-document.md lines 25 and 99, all "OD-BIL-004 v2", and 09 labels its field "Operational definition ref". This template has no field for either, and the string OD-BIL-004 appears nowhere on the page, so a reader holding the charter cannot confirm that this is the definition it points at, and a reader filling the template has nowhere to write the reference the rest of the pack cites. Line 56, "Definition revised? Yes / No", then produces a revision with no version to increment: the change recorded at line 55 (settled 2026-04-24, baseline recut) is exactly the v1 to v2 change, and nothing on the page records which version the recut baseline belongs to.

**Fix.** Add two rows above Metric name: "| **Definition ID** | *OD-BIL-004* |" and "| **Version / effective from** | *v2, effective 2026-04-24 — supersedes v1, which counted same-reason reopens only* |".

### L23 · UNFOLLOWABLE · medium

> | **Denominator / population** | *All billing tickets reaching Resolved in the window* |

"The window" is the only reporting period this page names, and the field directly below defines Time window as "Rolling 7 days from each ticket's first Resolved timestamp" — a window per ticket, not a reporting period. The one word carries two meanings in adjacent rows of the page whose stated job (line 6) is that two analysts working independently get the same number. Two analysts asked for the March figure must invent both the period and the rule for tickets resolved in the last seven days of it, whose reopens fall in April: truncate the window, hold the tickets back, or push them into April. Those three choices give three different March numbers from the same data.

**Fix.** Split the field: *Reporting period: calendar month (or the stated baseline window). Denominator: billing tickets whose first Resolved falls inside the reporting period.* Then add a business rule: *A ticket enters the denominator on its first Resolved date; its 168h window may run past the period end, so a period is not final until 7 days after it closes.*

### L31 · UNFOLLOWABLE · medium

> | **Business rules applied** | *First Resolved only; a second reopen does not double-count* |

The business rules cover first-Resolved-only and non-double-counting, and Exclusions (line 27) drop tickets merged into another, but nothing says what happens to a reopen event that arrived on the merged child. That single rule is the highest-impact finding in the lineage doc: 06-data-lineage.md line 56 records it as High severity, "Restored 21 reopens to March; the baseline was recut from 13.9% to the 14.2% now on the charter", closed 2026-05-06. The worked example at line 45 walks through a merge and addresses only timestamps. A reviewer who asks "does a reopen on the child count for the survivor?" gets no answer from the document whose whole job is to be the answer.

**Fix.** Add to Business rules: *A ticket merged into another leaves the denominator; its reopen events are carried onto the survivor and count against the survivor's first Resolved (fixed in stg_tickets 2026-05-06 — see the lineage doc).*

### L32 · WRONG · medium

> | **Refresh cadence** | *Nightly, 02:00 UTC; restated for 3 days as late events land* |

The observation window is 168 hours (line 24, rolling 7 days from each ticket's first Resolved) but the figure stops being restated after 3 days. A cohort is keyed on its resolve date — the denominator is tickets reaching Resolved — so any reopen landing on days 4 to 7 arrives after the last restatement of the cohort it belongs to and never reaches the numerator. The metric under-reports by construction, and it under-reports worst on the slow-posting cases the project exists to fix. Line 33, "Metric is final at T + ___", is the field that would have caught this and it is the one field left blank in an otherwise complete worked example.

**Fix.** Set the restatement to outlast the window: *Nightly, 02:00 UTC; restated for 8 days — one day past the 168h window — as late events land*, and fill line 33 as *T + 8 days*. If the 3-day restatement is fixed by the pipeline, say instead that a cohort is published only once its 168h window has closed.

### L36 · WRONG · medium

> | **Related metrics it must reconcile with** | *Contact rate (same denominator) and the Ops weekly reopen tile (currently 1.8 pts apart — see the lineage doc)* |

Contact rate does not share this metric's denominator. This metric's denominator is billing tickets reaching Resolved; the curriculum's own glossary defines contact rate as "How many contacts you get per customer per period", and its design-review guidance asks for "a forecast contact rate per active customer" — an install base of customers or accounts, not resolved billing tickets. The reader is told to reconcile two rates on a common base that does not exist and has no way to carry the check out. The Ops tile half of the row is sound: 14.2% against the tile's 12.4% in 06-data-lineage.md lines 48 and 50 is the 1.8 points quoted.

**Fix.** Name what is actually shared, or swap the metric: *Contact rate (shares the billing contact-reason filter, not the denominator — reconcile the count of billing contacts, not the rates)*, or replace it with first-contact resolution on billing tickets, which does share this denominator.

### L50 · WRONG · medium

> Two people independently applied this definition to the same 20 records.

The test reports raw agreement out of 20 (line 54, "Agreement ___ / 20") with no number that counts as a pass, on an unstratified sample — and the guidance at line 12 calls this test "not optional". The pack teaches the opposite on both counts: 07-msa-attribute-agreement.md line 12, "The mistake this prevents. Reporting percent agreement instead of kappa"; line 52, "Report raw agreement **and** kappa together. At high prevalence of one category, raw agreement can be 95% while kappa is near zero"; and lines 34–37, "Do not use a random sample... Deliberately load the sample with failures and ambiguous cases." Reopens run at about 14%, so 20 unstratified records hold roughly three of them; two observers who both say "not a reopen" to the other seventeen score 85% agreement without agreeing on a single case that matters. The reader writes 17/20, declares the definition operational, and has measured prevalence.

**Fix.** Load the sample and report kappa: *40 records, deliberately stratified — 10 clear reopens, 10 clear non-reopens, 20 borderline (near the 168h boundary, merged, system-raised).* Add rows for kappa and a pass threshold: *kappa >= 0.80 to pass, per 07-msa-attribute-agreement.md*. Tab "2 QA agreement (kappa)" of 19-black-belt-calculators.xlsx does the arithmetic from a raw grid.

## 06-data-lineage.md

### L26 · UNFOLLOWABLE · high

> | 1 | Event capture | *Event capture* | *Zendesk UI* | *Agent clicks Resolved* | *resolved_at is browser local time* | *Support Ops* | *Real time* |

CONFIRMED. The header at line 24 is `| # | Stage | System / object | Transformation, join or filter applied | Business rule | Owner | Refresh | Known gap |` — 8 columns. Every example row (26-31) repeats the stage label in the System/object cell and so runs one column late from there on. In row 1 the system "Zendesk UI" lands under Transformation, the business rule "Agent clicks Resolved" under Business rule by luck, the known gap "resolved_at is browser local time" under Owner, the owner "Support Ops" under Refresh, and the cadence "Real time" under Known gap. Row 2 (line 27) files "zendesk.tickets" as a transformation, "Data Eng" as a refresh and "Hourly" as a known gap; rows 3-6 repeat it. Consequence: across all six hops the Known gap column contains only cadences (Real time, Hourly, 02:00, 02:40, 03:10, 06:00) and the Owner column contains only defects — so not one hop records a known gap, even though the Findings table below cites gaps at hops 1, 3, 4 and 6, and the curriculum's mandatory deliverable (line 1461) is explicitly "every join and filter, every business rule, refresh cadence, known gaps, and the owner of each hop". A reader copies the pattern and hands a data engineer a lineage whose owner column holds cadences.

**Fix.** Re-lay every row against the header, dropping the duplicated stage label. Row 1: `| 1 | Event capture | *Zendesk UI* | *Agent clicks Resolved; writes resolved_at* | *Resolved means the agent marked it solved, not that the customer agreed* | *Support Ops* | *Real time* | *resolved_at is written in browser local time, not UTC* |`. Row 2: `| 2 | Source table | *zendesk.tickets* | *Hourly copy, no transformation* | *None* | *Data Eng* | *Hourly* | *Timezone converted here, not at capture* |`. Apply the same shift to rows 3-6 so the last three columns hold a team, a cadence and a defect.

### L38 · HOLLOW · high

> | Source table | *zendesk.tickets* | *replicated hourly* | *timezone converted to UTC here* |

CONFIRMED. The section is headed "Single-record walkthrough" and the document's purpose statement at lines 18-19 is "trace one record from the event that created it to the number on the dashboard", but the worked example names no record and shows no value. Under the header `| Stage | Value at this stage | Matches previous? | If not, why |`, "Value at this stage" holds object names (zendesk.tickets, stg_tickets, warehouse.tickets, Ops weekly reopen tile) and "Matches previous?" — a yes/no question — is answered with mechanisms (replicated hourly, dbt run 02:00, Looker, 02:40). The result is a shorter, less informative copy of the hop table above it. The curriculum's instruction for this tool is explicit: "Pick one real record. Note its value at the source event... Where the value changes, establish why." The two changes this document is built around — the timezone shift (line 58) and the merged child's reopen being dropped (line 56) — are invisible here, so a reader has no model of a filled-in walkthrough and reproduces the same empty shape. The table also skips hop 5, the semantic layer, which is where the 168-hour rule is actually applied.

**Fix.** Name the record above the table — "Record traced: *TCK-118204*, first Resolved 4 Mar" — and put that record's actual value in the value column at each stage: Event capture *resolved_at 2026-03-04 23:12 (agent local)* / — / *browser local time, no zone stored*; Source table *2026-03-05 04:12 UTC* / *No* / *converted at replication, so the ticket moves to the next day*; ETL output *2026-03-05 04:12 UTC, survivor of merge with 118205* / *Yes* / —; Metric build *reopen at 71h, flagged* / *Yes* / —; Dashboard *not shown* / *No* / *chat-excluded tile drops it*. Add the missing semantic-layer row so all six hops appear.

### L50 · CONTRADICTION · medium

> *The agreed definition: any reason, all channels, 7 days rolling from each ticket's own Resolved timestamp. This is the one the baseline is cut on; the other two are reported, not defined*

CONFIRMED against the other document. This row describes OD-BIL-004 v2 / warehouse.reopen_daily, value 14.2%, as "all channels". 04-operational-definition.md line 35 records as a known limitation of that same definition: "Excludes chat until the channel field is backfilled; understates by roughly 0.4 points" — while its own Inclusions row (line 26) says "All channels". The 0.4 points is the same figure this document attributes solely to the Looker tile at hop 6 (line 57), and this document's decomposition of the 1.8-point gap at line 48 assigns ~0.4 of it to the tile's chat filter — which only works if warehouse.reopen_daily itself includes chat. So 04 and 06 give opposite answers to the one question a reader must settle before signing: does the 14.2% on the charter include chat or not? 04-operational-definition.md line 36 explicitly points at this document to reconcile them, and it does not.

**Fix.** Reconcile the two documents and say where the chat exclusion actually bites. If the exclusion is at hop 6 only, rewrite 04's known limitation to read "the Ops weekly tile excludes chat; the baseline query does not". If warehouse.reopen_daily also excludes chat, change this cell to "*The agreed definition: any reason, 7 days rolling from each ticket's own Resolved timestamp. Voice and email only — chat is excluded until the channel field is backfilled, worth about 0.4 points (finding 2 below)*" and restate the 1.8-point decomposition at line 48, which currently double-counts that 0.4.

### L30 · CONTRADICTION · low

> *Reopen flagged where reopened_at - resolved_at <= 168h*

CONFIRMED, though narrower than reported. Hop 5 states the metric rule with the upper bound only; line 50 of this same document writes it "0 < t <= 168h" and 04-operational-definition.md line 22 writes it "0<t<=168h". As written at hop 5 the filter also admits events stamped at or before the resolve timestamp — clock skew and same-instant system writes. (The reporter's second example is wrong: the batch service-account reopen at 04 line 47 is excluded for being system-generated, 9.5 hours after resolve, not by the lower bound.) The document states the project's own rule two ways two tables apart, in a template whose stated purpose is teaching the reader to notice exactly that, and the discrepancy is not recorded in the Findings table.

**Fix.** Make hop 5 read `*Reopen flagged where 0 < reopened_at - resolved_at <= 168h, first Resolved only*` so it matches line 50 and OD-BIL-004 v2 — or, if the deployed SQL genuinely omits the lower bound, leave it and add a Low-severity row to the Findings table saying so.

## 07-msa-attribute-agreement.md

### L46 · UNFOLLOWABLE · high

> | Fleiss' / Cohen's kappa | *0.41* | see below | *>= 0.80* |

CONFIRMED. Under the header `| Measure | Result | Threshold | Verdict |` this row puts "see below" in Threshold and a threshold, ">= 0.80", in Verdict — so the single most important number in the study is the only row of four with no pass/fail; the three rows above it all read "Fail". The ">= 0.80" bar matches neither the 0.75 boundary stated two lines later (line 48) nor the 0.60 boundary used in section 4, so the reader is handed a third cut-off with no source. (It comes from cell B18 of tab 2 of the workbook, "Acceptable 0.8", which the document never mentions.) The curriculum grades this exact figure — 0.41 from 4 appraisers × 50 stratified tickets × 2 replicates — at HTML line 2356: "Fleiss' kappa (overall) 0.41 → MARGINAL, not usable as-is". That is the sentence the reader needs and cannot find here.

**Fix.** `| Fleiss' kappa (overall) | *0.41* | *>= 0.75 usable · >= 0.90 good* | *Marginal — not usable as-is; remediate the failing rubric items and re-test before any figure from this rubric is used* |`

### L63 · WRONG · high

> does the same arithmetic from a raw pass/fail grid, including Fleiss' kappa for more

CONFIRMED by opening the workbook. Tab "2 QA agreement (kappa)" of 19-black-belt-calculators.xlsx takes exactly four inputs — B5 Both said PASS, B6 A passed/B failed, B7 A failed/B passed, B8 Both said FAIL — and computes B11 raw agreement, B12 chance agreement, then B13 labelled COHEN'S KAPPA = (B11-B12)/(1-B12). I grepped every XML part of the workbook: the string "Fleiss" appears nowhere in it, and there is no cell, column or formula for a third appraiser. The sentence therefore sends a reader to a tool that cannot produce the number the template's own headline row (line 46, "Fleiss' / Cohen's kappa") and the curriculum (six-sigma-blackbelt-support-ops.html line 1414, "Fleiss' kappa overall and per-rubric-item") both demand, for a study the same page designs with 4 appraisers (line 24) and the curriculum sets at "minimum 3" (line 1408). A reader either averages pairwise Cohen's kappas and calls the result Fleiss' — which is not Fleiss' kappa and generally reads high because it discards the between-pair variability Fleiss pools over — or arrives at the tollgate with no overall kappa.

**Fix.** Replace with: "Tab **2 QA agreement (kappa)** of `19-black-belt-calculators.xlsx` does the same arithmetic from a raw pass/fail grid for **two** appraisers (Cohen's kappa). With three or more appraisers you need Fleiss' kappa, which that tab does not compute: use Minitab (*Stat -> Quality Tools -> Attribute Agreement Analysis*) or Python (`from statsmodels.stats.inter_rater import fleiss_kappa, aggregate_raters`). Do not average pairwise Cohen's kappas and report the average as Fleiss'."

### L64 · UNFOLLOWABLE · high

> than two appraisers; the sample size, and the power it buys you, come from the sample

CONFIRMED by opening the workbook. The sentence ends "size calculator in `05-data-collection-plan.xlsx`". That tab ("Sample size calculator") is headed "COMPARING TWO RATES (FCR, SLA met, QA pass, reopen)"; its inputs are C5 current rate, C6 change to detect, C7 alpha, C8 power, and C13 is "SAMPLE SIZE PER GROUP" = ROUNDUP((z_a/2+z_b)^2*(p1(1-p1)+p2(1-p2))/d^2). It is a two-proportion comparison sizer. It has no notion of items, appraisers or replicates, and power is an input (C8) — nothing in the tab returns the power a fixed n buys you, so "the power it buys you" cannot be read off it at all. At the values it ships with (0.72, 0.03, 0.05, 0.80) it returns ~3,394 per group, against this template's own 50-item example at line 25. A reader following the pointer either sizes an attribute agreement study at thousands of scored contacts or gives up. The guidance they actually need is already in the pack, in cell D10 of tab 2 of 19-black-belt-calculators.xlsx: "Below about 50 items kappa bounces around too much to act on, and below 30 it is not worth calculating."

**Fix.** Delete the pointer and state the design directly: "Size the study from the design, not from a power calculation: 50 items stratified 20 clear pass / 20 clear fail / 10 genuinely ambiguous, every appraiser who scores that queue (minimum 3), 2 replicates each. Below about 50 items kappa is too unstable to act on and below 30 it is not worth computing — see the note on tab 2 of `19-black-belt-calculators.xlsx`. The sample size calculator in `05-data-collection-plan.xlsx` sizes rate comparisons, not agreement studies; do not use it here."

### L87 · CONTRADICTION · high

> | *Item 7 — empathy demonstrated* | *0.58* | *84%* | *Unacceptable (<0.60)* | *Write a partial-credit rule with worked examples, or drop the item. More calibration meetings on the current wording will not move it* |

CONFIRMED. Section 4 grades on Good >0.80 / Marginal 0.60-0.80 / Unacceptable <0.60 (lines 83-87). Lines 48-50 of the same document state ">0.90 excellent · 0.75-0.90 good · 0.40-0.75 marginal (do not use for individual performance management) · <0.40 unacceptable (halt any use of this data in decisions)", which is also the curriculum's table verbatim (HTML lines 1418-1421) and the verdict formula in the workbook the reader is sent to (cell B14 of tab 2: >0.9 EXCELLENT, >0.75 GOOD, >0.4 MARGINAL, else UNACCEPTABLE). So kappa 0.52 (line 86) and 0.58 (line 87) are stamped "Unacceptable" eleven lines after the document says numbers in that band are marginal and reserves "unacceptable — halt any use of this data in decisions" for <0.40. 01-project-charter.md line 144 describes the same 0.52 as analysts who "agree only moderately". The two labels carry opposite instructions, and section 5 forces the reader to tick one box: Marginal ("usable for aggregate analysis only") or Unacceptable ("remediate and re-test before using this data anywhere"). With an overall 0.41 and two items branded unacceptable, the reader cannot tell which box is correct.

**Fix.** Use one scale throughout. Relabel section 4 against lines 48-50: Item 3 (0.71) and Items 4 (0.52) and 7 (0.58) all "Marginal (0.40-0.75)", Items 1 (0.89) and 2 (0.84) "Good (0.75-0.90)". If the intent is that the item the primary metric is read off must clear a higher bar than the generic scale, say so explicitly in Item 4's Action cell rather than introducing a second set of bands.

### L103 · UNFOLLOWABLE · high

> | Rubric items rewritten | *Items 4 and 7* | *QA manager* | *2026-05-22* |

CONFIRMED. The header at line 101 is `| Action taken | Date | Re-test kappa | New verdict |`, but this row and all four below it (104-107) fill Date with a detail, Re-test kappa with an owner, and New verdict with a date. There is an owner in every row of the data and no Owner column in the header; and no row anywhere in section 6 records a re-test kappa or a new verdict, which is the only thing the section exists to prove. The Measure tollgate checklist (HTML line 1512) reads "MSA result is acceptable, or a documented remediation was performed and re-tested". A reader copying this shape walks into the tollgate with a list of things they did and no evidence any of it worked — while the one re-test number in the document (0.84) sits stranded in the Owner column of section 7 at line 115.

**Fix.** Widen the header to `| Action taken | Detail | Owner | Date | Re-test kappa | New verdict |` and complete the example, e.g. `| Rubric items rewritten | Items 4 and 7 | QA manager | 2026-05-22 | 0.84 | Good — usable |`, carrying the 0.84 from line 115 into this table.

### L26 · UNFOLLOWABLE · medium

> | Sample stratification | ___ clear pass · ___ clear fail · ___ genuinely ambiguous |

CONFIRMED. Three blanks with no target mix and no total, and the appraiser row at line 24 gives no minimum. The document's own convention elsewhere in this table is to put the standard in the cell in roman type: "(minimum 2)" for replicates, "(minimum 5 days)" for separation, "**Must be No**" for showing the standard. Only the two rows that determine whether kappa means anything omit it. The box at lines 34-37 says "Deliberately load the sample with failures and ambiguous cases" without saying how many of each. The curriculum specifies both (HTML lines 1404-1408): "50 contacts, deliberately stratified — 20 clear pass, 20 clear fail, 10 genuinely ambiguous" and "Appraisers: all QA analysts scoring that queue, minimum 3". Neither survives into the downloaded .md, where the only trace is the italic worked example ("4", "50") that line 14 instructs the reader to delete. A lone Black Belt has to guess the composition of the study, and the composition is exactly what the prevalence-paradox warning three lines below is about.

**Fix.** `| Appraisers (n, names/IDs) | *4 — QA analysts QA-01 to QA-04* (every appraiser who scores this queue; minimum 3) |` and `| Sample stratification | ___ clear pass · ___ clear fail · ___ genuinely ambiguous (target 20 / 20 / 10 in a 50-item study) |`. Add the total to the box at line 34: "Fewer than 50 items and kappa bounces around too much to act on; fewer than 30 and it is not worth computing."

### L113 · UNFOLLOWABLE · medium

> | Calibration session | *2026-06-12* | *Complete* |

CONFIRMED. The header at line 111 is `| Control | Frequency | Owner |`, and all three rows (113-115) supply a one-off date in Frequency and a status or a result in Owner. No frequency and no owner appear anywhere in section 7, so the "Ongoing control" handed to the QA manager has neither a cadence nor anyone accountable — the two things that make it ongoing. It also contradicts line 107 of the same document, which has already set calibration at "Fortnightly, 45 minutes, all analysts". Line 115 puts the re-test result "kappa 0.84 — passed" under Owner, which is the number section 6 is missing.

**Fix.** `| Calibration session | *Fortnightly, 45 min* | *QA manager* |`, `| Blind re-score audit | *Monthly, 10 contacts per analyst* | *QA leads* |`, `| Kappa re-measurement | *Quarterly, and after any rubric change* | *Black Belt until handover, then the process owner* |`. Move "kappa 0.84, 2026-07-10" into the re-test column of section 6.

## 08-msa-gage-rr.md

### L12 · WRONG · high

> If every sampled contact is a routine one, %study variation flatters itself and the gage looks better than it is.

The direction is inverted, in the one sentence headed "The mistake this prevents." %study variation is SD(Gage R&R) / SD(total), and 29-msa-gage-rr.xlsx builds the total from the study's own parts (B59 = B55 Gage R&R + B58 part-to-part). Narrow the part range and the part-to-part term collapses, the denominator shrinks, and %study variation goes UP while ndc goes DOWN (B64 = 1.41 x SD part-to-part / SD Gage R&R). On the worked data part-to-part is 91.9% of total variance; strip it out and the same gage error reads 70-80% instead of 28.4%. So ten routine contacts condemn a sound gage, they do not flatter it. The reader is taught the bias backwards and will misread their own failing study as "worse than it looks" — or will deliberately sample routine contacts to get a clean answer and get the opposite.

**Fix.** Replace with: "Accepting a study whose parts do not span the real range. Ten near-identical contacts leave almost no part-to-part variation for the gage to be measured against, so %study variation is inflated and ndc understated — you condemn a measurement system that is fine, while still learning nothing about whether it holds up on the long, complex contacts." The same inversion sits in cell C6 of 29-msa-gage-rr.xlsx ("Sampling ten routine contacts is the single most common way a study flatters the gage.") and must be corrected with it.

### L23 · UNFOLLOWABLE · medium

> crossed ANOVA: type the 90 readings into the yellow grid and every number in the tables

Two wrong pointers. (1) There is no yellow grid in 29-msa-gage-rr.xlsx: the yellow cells (fill FFFFF9E3) are B5:B9, five study-design fields, and the 90 readings live in the green block B13:J22 (fill FFECFAEF). The workbook's own caption at A2 says so: "The green block is a worked study — overwrite the 90 readings with your own. The yellow cells above it describe your study." (The same slip is repeated on the workbook's "How to use this" tab, cell B5, so both need fixing.) (2) "every number in the tables below" is untrue of section 3 — the workbook computes nothing for bias, linearity or stability, so a reader hunts for outputs that do not exist. It also silently drops the one output the workbook produces that the .md has no row for: %Tolerance (B65 = 41.8% on the worked study, unacceptable on the same bands).

**Fix.** "overwrite the 90 green readings with your own — the yellow cells above them are the five study-design settings — and sections 1 and 2 below fill themselves. Section 3 is not in the workbook; run those three checks separately. If you entered a tolerance the workbook also returns % Tolerance (41.8% in the worked study, unacceptable on the same bands) — record it with your verdict."

### L59 · CONTRADICTION · medium

> | — Reproducibility (appraiser) | *0.5886* | *6.8%* | *26.1% — the analysts disagree more than the tool does* |

Line 28 promises a four-way split — "parts, appraisers, part x appraiser and repeatability" — but the results table has three rows and no place for the interaction, and it labels reproducibility "(appraiser)". The workbook prices the interaction on its own ANOVA row (B49, df 18) and folds it into reproducibility: B57 = MAX(0,(D48-D49)/30) + MAX(0,(D49-D50)/3), i.e. appraiser term plus interaction term. In this worked study the interaction component is negative (I recomputed it from the 90 readings: (MSi - MSe)/3 = -0.0009, floored to zero), so 0.5886 happens to be pure appraiser and nothing shows. A reader whose interaction is real has nowhere to record it, will report the combined figure under a row labelled "appraiser", and will conclude the analysts disagree in general — when the workbook is telling them the analysts disagree about particular contacts, which has a different fix.

**Fix.** Relabel the row "— Reproducibility (appraiser + interaction)" and add beneath it "| — of which part x appraiser | *0* | *0%* | *0%* |". Add to the reading note at line 68: "Split reproducibility again. A large appraiser term means someone is consistently high or low — calibrate. A large interaction means they only disagree on particular contacts — go and look at those contacts, because the definition is ambiguous exactly there."

### L76 · UNFOLLOWABLE · medium

> | Bias | Compare mean measurement to a reference value | *+0.8 min* | *Two analysts consistently round after-call work up* |

No reference value is obtainable from anything in this file. Line 18 rules out the obvious candidate ("not the CRM timestamp, which is a different gage and has to be validated separately"), nothing else is offered, and the worked +0.8 min appears from nowhere. The programme does define the reference elsewhere — the curriculum glossary entry for Bias says "Compare each analyst against an agreed standard set of adjudicated items, not against the group average", and 07-msa-attribute-agreement.md carries a "Standard established by (senior panel consensus, agreed before the study)" field — but neither is reachable from this page. Then the "Acceptable?" column, the only thing a tollgate reads, is answered with a cause rather than a verdict in the model row, and with "—" in the other two, so the worked example teaches the reader to leave the verdict column unanswered.

**Fix.** State the reference the way the programme defines it: Method = "Senior panel times 10 recorded contacts by consensus; those agreed times are the reference. Compare each analyst's mean against them." Result = "+0.8 min". Acceptable? = "No — a 10% systematic offset on an 8-minute mean." Move "Two analysts consistently round after-call work up" into a fourth column headed Notes / cause, and give the linearity and stability rows real verdicts rather than "—".

### L6 · UNDEFINED · low

> **What it is for.** The continuous-data equivalent: how much of the variation you are about to analyse is the measurement rather than the process.

"The continuous-data equivalent" has no antecedent anywhere in the file — the referent (the attribute agreement study) exists only in the curriculum page's ordering, and this template never mentions 07-msa-attribute-agreement.md. In a downloaded .md this is the first sentence the reader meets, and it leaves them unable to tell that an attribute counterpart exists or when to use which — the live risk being a reader running a crossed Gage R&R on a pass/fail QA judgement, which is exactly what 07 is for.

**Fix.** "**What it is for.** The continuous-data counterpart of the attribute agreement study in `07-msa-attribute-agreement.md`: use that one when the measurement is a human judgement scored pass/fail or into categories, this one when it is a number on a scale. It answers how much of the variation you are about to analyse is the measurement rather than the process."

## 09-baseline-document.md

### L39 · WRONG · high

> | UCL / LCL | *17.1% / 11.3%* |

Line 37 declares a Laney p-prime chart with sigma z = 4.25 at ~5,100 tickets a week. 27-control-charts.xlsx computes Laney limits at cell K14 as p-bar + 3 x sigma_p x sigma_z, with sigma_p = SQRT(p(1-p)/n). Here sigma_p = SQRT(0.142 x 0.858 / 5100) = 0.489 points, so the limits are 14.2% +/- 3 x 0.489 x 4.25 = 14.2% +/- 6.2 points, i.e. 20.4% / 8.0%. The quoted +/-2.9 points implies sigma z = 2.0, not 4.25 (it is roughly what an I-MR chart on the 12 weekly rates would give). The narrow limits are the only thing manufacturing the special cause: on the chart the document says it used, the 18.9% release week (line 98) sits comfortably inside 20.4% and there is no signal at all. Lines 39, 41, 42, 43 and 98 are all downstream of a limit the declared chart does not produce.

**Fix.** Recompute from the declared chart — "*20.4% / 8.0% (Laney p-prime; 3 x sigma_p 0.49 pts x sigma z 4.25)*" — and rewrite "Special causes found" to "*None. The 18.9% release week is the highest point but sits inside the Laney limits; the widened limits are precisely why an ordinary p-chart would have called it a special cause.*" Alternatively state on line 36 the chart actually used and the sigma behind it. Lines 36-43 and 98 must come from one chart.

### L51 · CONTRADICTION · high

> | n | *61,400 tickets over the 12-week window (~5,100/week)* |

The metric is defined at line 24 as the 7-day reopen rate on billing adjustments, but the extract (line 27), the distribution (line 51) and the control chart (line 37, ~5,100/week) are all built on 61,400 billing tickets, while section 5 reconciles the identical 14.2% across 966 contacts and 137 reopens, and section 7 line 106 gives 966 billing-adjustment contacts a month — about 2,900 in a 12-week window. 14.2% of 61,400 would be 8,719 reopens, not 137. Nothing in the document says section 5 covers a different population or a shorter period (line 99 even ties the 966 to a two-week March event). A reviewer therefore cannot say what the baseline is built on, and neither the control limits (which depend on n per week, 5,100 vs ~240) nor the capability figures can be tied to a denominator.

**Fix.** Use one denominator and label everything to it. If the metric is billing adjustments: Records (n) = "*2,880 billing adjustments over the window, drawn from 61,400 billing tickets*"; recompute the section 2 justification at ~240 adjustments a week; head section 5 "*All strata, March 2026 (966 adjustments) — one month of the window, stratified*" so the reader can see why 966 is not the baseline n.

### L58 · WRONG · high

> *Probability plot near-linear; Anderson-Darling p = 0.03, which at 12 weekly points is not a concern*

The inference is inverted. A test's false-positive rate does not depend on n; its power does. With 12 points the Anderson-Darling test has very little power, so a significant result means the departure was large enough to be detected in spite of that — it deserves more weight, not less. The "do not over-read the p-value" caution belongs to large n, where trivial departures reach significance. As written the reader takes away a rule that lets any small sample dismiss a failed normality test, which bites immediately: section 4 fits a normal curve to these same 12 points to quote a fitted % outside specification, and the curriculum warns (HTML, capability module) that assuming normality on right-skewed support data understates the breaching tail "sometimes by a factor of two or more".

**Fix.** "*Probability plot near-linear apart from the release week; Anderson-Darling p = 0.03. With only 12 points the test has little power, so a significant result means the departure is real rather than negligible — it is the plot, not the p-value, that supports treating the weekly rates as near-symmetric, and the fitted figures in section 4 are quoted with that caveat.*"

### L72 · WRONG · high

> | **Capability index value** | *Ppu 0.42* |

Ppu = (USL - mean) / (3 x overall SD). On this document's own numbers — target/USL 8.0% (line 70 "only an upper limit exists"), mean 14.2% (line 52), SD 1.4 points (line 54) — that is (8.0 - 14.2) / 4.2 = -1.48, not +0.42. A positive 0.42 would require a USL of 16.0%. The sign matters: -1.48 says the mean sits 4.4 sigma the wrong side of the limit, +0.42 says the mean is inside spec with a wide spread. The two rows beneath inherit it — "58% of weeks above the 8.0% target" contradicts line 55, where p10 is 12.3%, i.e. all 12 weeks were above 8.0%; the fitted 61% should be >99.9% (z = -4.43). Tab "3 SLA capability" of 19-black-belt-calculators.xlsx returns B13 = -1.48 and B17 = "NOT CAPABLE — you are producing breaches" for these inputs. A reader copying the pattern carries a nearly-capable-looking index to a tollgate for a process that never once met target.

**Fix.** Capability index value: "*Ppu -1.48 — the mean sits 4.4 sigma the wrong side of the limit; not marginally incapable, entirely outside spec*". % outside specification (observed): "*100% — all 12 weeks, the lowest at 12.3%*". % outside specification (fitted): "*>99.9%*". Add to the index justification: "A negative Ppu is not an error — it means no amount of tightening the spread helps until the centre moves."

### L76 · WRONG · high

> | Opportunities per unit (program standard) | *5 — fixed at programme level, never renegotiated mid-project* |

The numerator and the denominator are on different bases. DPU 0.142 (line 75) is the reopen rate alone — one defect type — while the denominator multiplies every contact by five opportunities. The programme's own worked calculation (curriculum HTML line 1128-1141) sums all five defect types before dividing by five: misroutes 9,400 + reopens 7,800 + QA fails 4,100 + SLA breaches 5,200 + documentation fails 3,900 = 30,400 defects over 120,000 contacts x 5. Tab "1 Sigma level" of 19-black-belt-calculators.xlsx says the same in cell D7: "Every defect in the period across all your defect types — reopens, transfers, SLA breaches, QA fails." Counting reopens against five opportunities inflates the tollgate sigma by 0.83: reopens against the one opportunity they represent give DPMO 142,000, Z 1.07, sigma 2.57 — not 28,400 / 1.90 / 3.40.

**Fix.** Add to the row: "*5 — routing, diagnosis, resolution accuracy, communication, documentation. Fixed at programme level, never renegotiated mid-project. The opportunity count and the defect count must cover the same list: baselining reopens alone means 1 opportunity and sigma 2.57; keeping 5 means counting all five defect types in the numerator.*" Then correct the DPU / DPO / DPMO, Z and sigma level rows to whichever basis is chosen.

### L105 · CONTRADICTION · high

> *Charter's $425k/yr gross drops to $376k — the gap is 11% smaller than assumed*

The "Charter estimate" column contradicts the actual charter on every row. 01-project-charter.md records baseline 14.2% not 15.0% (line 89), 266,000 billing tickets a year not 1,100 contacts a month (line 47, which explicitly ties itself to this file: "the 61,400 in the baseline document is one quarter"), $6.80 fully-loaded per contact not $41.00 (line 51), and a gross annual benefit of $112,146 not $425k (line 52). 18-handover-and-benefit-validation.md prices its replication benefits on the same $6.80 (lines 41-43), so this document is the outlier in the pack, not the charter. The "Revised benefit" column is only the invented charter figure scaled by ratios, never rebuilt from this document's numbers: 966 contacts/month x 12 x 6.2 points x $38.60 is about $28k a year, not the $310k "gross benefit of record" Finance is asked to sign. Two benefit models for one project, an order of magnitude apart.

**Fix.** Rebuild the revised column from this document's own numbers with the arithmetic shown in the cell, the way 01-project-charter.md line 50 does ("266,000 x (14.2% less 8.0%)"), and make the Charter estimate column quote what the charter actually says: 14.2% -> 8.0%, 266,000 tickets a year, $6.80 a contact, $112,146 gross. If the two documents describe different populations (billing tickets vs billing adjustments), say so in the row.

### L10 · CONTRADICTION · medium

> **Who signs it.** Black Belt · Champion and Finance both sign the baseline value

The sign-off table at lines 112-117 has Black Belt, Process owner, Finance partner and Master Black Belt — there is no Champion row. The reader is told the Champion must sign the baseline value and has nowhere for them to sign, while two signatories who appear in the table are never mentioned in the guidance. In a programme where the Champion is the person a returned tollgate goes back to, a baseline submitted without their signature is the one that comes back.

**Fix.** Add "| Champion | | | |" to the sign-off table above the Finance partner row, and make line 10 name the same four roles: "**Who signs it.** Black Belt writes it · Process owner, Champion, Finance partner and Master Black Belt sign. Finance's signature is the one that starts the benefit clock."

### L26 · CONTRADICTION · medium

> | Period covered | (minimum 13 weeks; 12 months preferred) |

The worked example breaks the rule printed inside the field: 12 weeks throughout — line 51 "over the 12-week window", line 58 "at 12 weekly points", line 105 "12-week control chart centre line", and the section 6 events run 2026-01-05 to 2026-03-13 against an extract date of 2026-04-02. The curriculum states the same floor ("minimum 13 weeks to capture weekly seasonality", HTML line 1497), and 27-control-charts.xlsx warns on its "Pick your chart" tab, cell A15, "Twenty to twenty-five points is the working minimum. Fewer than that and the limits move every time you add a day." This is also the only row in section 1 with no example value, so the one place a reader looks for the pattern shows the rule being broken.

**Fix.** Give the row a worked value that obeys its own rule — "*2026-01-05 to 2026-06-28, 26 weeks*" — and extend the guidance: "(minimum 13 weeks so weekly seasonality is inside the window; 12 months preferred. A weekly control chart needs 20-25 points before its limits stop moving, so 13 weeks is the floor for the metric, not a comfortable baseline.)" Then reconcile lines 51, 58 and 105 to the same window.

### L40 · UNFOLLOWABLE · medium

> | σ_z (if attribute chart) | (near 1.0 = no overdispersion; >1.2 = use Laney) |

The row states a decision threshold for a quantity the document never defines or shows how to obtain — sigma z is Laney's overdispersion factor, the mean moving range of the standardised points divided by 1.128 (27-control-charts.xlsx, 'Laney p-prime' tab, B6/B7) — and the worked example then asserts sigma z = 4.25 at line 37 with no derivation. The same page goes on to ask for Laney limits, a probability plot and Anderson-Darling statistic, Ppu with an optional Box-Cox or Johnson transformation, DPU/DPO/DPMO, Z, sigma level and RTY, and never names a single workbook or sibling template, though this folder holds 27-control-charts.xlsx (tabs 'Pick your chart', 'Laney p-prime'), 19-black-belt-calculators.xlsx (tabs '1 Sigma level', '3 SLA capability') and 25-pareto-and-distribution.xlsx ('Shape and spread'). Templates 07, 08, 14 and 16 all carry a "How to work this out" pointer block; the template that demands the most computation carries none. (The reporter's claim that it is the pack's only .md with no references is false — 02, 03, 04, 06 and 18 also have none — but none of those asks the reader to compute anything.)

**Fix.** Add a "How to work this out" block in the house style of templates 07, 08, 14 and 16: "Sections 2 and 3: `27-control-charts.xlsx` — the 'Pick your chart' tab routes you; 'Laney p-prime' computes sigma z from the moving range of z and draws the limits as +/-3 x sigma_p x sigma z. Section 4: tab '3 SLA capability' of `19-black-belt-calculators.xlsx` for Ppu and the breach rate, tab '1 Sigma level' for DPU / DPO / DPMO and the sigma level. Percentiles and shape: tab 'Shape and spread' of `25-pareto-and-distribution.xlsx`."

### L43 · CONTRADICTION · medium

> | **Process stable?** | Yes / No |

The question the document exists to answer is left unanswered in the worked example, while section 2 records a point above the UCL that was deliberately not excluded (lines 41-42) and section 4 quotes a capability index anyway — directly beneath "Capability is meaningless on an unstable process" (line 45) and the mistake line 12 says this template prevents. 18-handover-and-benefit-validation.md answers its equivalent field explicitly (line 60, "*Yes — no points outside the limits, no runs of 8*"), so the omission is not house style. The reader with a signalling chart learns the warning is decorative and gets no model of the judgement that actually matters: when a retained, explained signal still permits a baseline. (The reporter's aside that this is the only blank cell in section 2 is wrong — lines 36 and 40 are also unfilled — but the substance stands.)

**Fix.** Answer it: "*Yes, with one explained signal retained — see section 6.*" and add under the blockquote at line 45: "A special cause you have identified, that is a standing feature of the process, and that you are keeping in the baseline does not block capability — but say so in this row in one line and expect the tollgate to test it. A signal you cannot explain does block it: find it or exclude it with a reason, and compute nothing in section 4 until you have."

## 14-root-cause-evidence-pack.md

### L40 · UNFOLLOWABLE · medium

> and it names the test and prints the decision rule. Comparing two reopen rates — a

13-hypothesis-test-log.xlsx does not name a test. I read the Test log tab: column B is "Business question" and column C is "Test used", both free-text cells the reader types into (row 11 has "2-proportion test" typed in C11), and there is no input anywhere that takes a description of what you are comparing. The workbook says so itself — cell C8 contains "WHICH TEST GOES IN THE TEST COLUMN — the log never named one, and eight tools in the library send you here", followed by the whole selection list, parked in a cell whose row label (A8) reads "Significance level (alpha)", where a reader hunting for a test chooser will not look. Only the second half of the claim holds: column N does apply a decision rule (NOT SIGNIFICANT / real and matters / significant but too small). A reader opens the file expecting to be told which test to run and finds a blank column waiting for the answer.

**Fix.** Say what the workbook does: "Open 13-hypothesis-test-log.xlsx: it does not choose the test for you, but the selection list is in cell C8 of the Test log tab, and once you type the p-value, effect size and threshold the verdict column decides whether the result is real, real-but-too-small, or nothing." The identical claim in 01-project-charter.md line 104 ("which picks the test and prints the decision rule") needs the same correction.

### L48 · HOLLOW · medium

> ### Key 2 — Mechanism

Key 2 is half of the rule this entire document exists to enforce ("Both, every time, or it does not go in the pack", line 12), and it is the only section with nowhere to write the thing it demands. Key 1 gets an eight-row table with a worked entry in every cell. Key 2 gets an instruction to "Describe *how* this cause produces the effect" and then jumps straight to the gemba verification table — which records who verified it and when, but never the mechanism statement itself. There is no field, no blank line, and no worked mechanism statement anywhere in the pack, so the reader has never seen what an acceptable one looks like, and a pack reaching the tollgate carries a fully evidenced Key 1 next to an unwritten Key 2.

**Fix.** Add a writable field with a worked example under the instruction: "**Mechanism statement:** ________" with the italic example "*An adjustment posts in the 02:00 vendor batch. Resolved can be set at any hour, so a closure made at 16:00 precedes the posting by up to 10 hours. The customer checks the account that evening, still sees the original charge, and reopens — the fix was real, the confirmation was not.*"

### L79 · UNFOLLOWABLE · medium

> | 1 | *Closure permitted before the posting confirms* | *Statistical + mechanism* | *4.9 pts* | *79%* | *Accepted* |

The cells do not match their headers (line 77: # | Root cause | Statistical evidence | Mechanism verified | % of gap | Accepted). "*4.9 pts*" — the contribution in points that the per-cause block on line 64 asks the reader to calculate — sits under "Mechanism verified", so as printed the summary says the mechanism of root cause 1 is 4.9 points. "*Statistical + mechanism*" answers a column headed "Statistical evidence" by naming which keys were met, and the header row has no column at all for the contribution in points. The totals row compounds it: on line 83 "**Total % of gap explained**" is a label parked in the "Mechanism verified" column with the cell that should carry the total left empty one column to its right. This is the one-page table a tollgate reviewer reads, and the column that records the second of the two keys holds a number instead of a verdict.

**Fix.** Give the table the six columns the rows need — "| # | Root cause | Both keys? | Contribution (pts) | % of gap | Accepted |" — and put the total under "% of gap": "| | | | **Total** | *97%* | |".

### L95 · CONTRADICTION · medium

> *2-proportion test, tickets closed before 17:00 vs after, 12 weeks of billing adjustments (n = 9,880 vs 4,720)*

9,880 plus 4,720 is 14,600 billing adjustments in 12 weeks, about 4,870 a month. The row directly below sizes the same population at "966 baseline-month billing-adjustment contacts" (line 96), and the row below that at "n = 137 vs 829" (line 98), which is that same 966 split into reopened and not — the figure signed off in 09-baseline-document.md lines 90 and 106. At 966 a month, 12 weeks is about 2,900 contacts, so this row names a population five times larger than the next two rows of the same table. (The identical 14,600 appears on line 30 called "billing tickets", which is a different and much larger population.) A reader working out how much data they need to reproduce this pack, or whether their own queue can support these tests, gets a different answer depending on which row they read.

**Fix.** Restate the 12-week samples against the signed baseline volume, or say explicitly that these tests ran on all billing tickets rather than on billing adjustments and name the wider population in the row. Whichever is true, lines 30 and 95 must use the same population name for the same 14,600.

### L52 · UNDEFINED · low

> **Verified at the gemba by:**

"Gemba" carries the whole of Key 2 — it appears in the two-key rule on line 19 and again as this heading — and it is never explained in the file. The curriculum page carries a glossary entry for it ("The actual place the work happens — sitting with an agent and watching, rather than reading a process document"), and grep across templates/*.md shows the word occurs only in these two lines, both unglossed. In the downloaded .md it is an unexplained Japanese loanword, and the reader most likely to be working alone is the one who cannot ask a colleague what it means. The four methods in the table below imply it, but the rule on line 19 is what a reader has to apply.

**Fix.** Gloss it on first use, on line 19: "...a described physical mechanism verified at the gemba — the place the work actually happens: on the floor, over the agent's shoulder, in the ticket and in the system config, not in a meeting room or an SOP."

## 16-pilot-protocol.md

### L57 · CONTRADICTION · high

> | **Practical significance threshold** | *1.5 percentage points — below this the benefit does not clear the cost* |

The charter derives a different threshold for the same worked project, and derives it from the money: "Finance will not book a project below $50,000 realized... a drop smaller than 3.3 points (14.2% to 10.9%) is a null result however small its p-value" (01-project-charter.md lines 99-101). I checked the arithmetic: 266,000 x 3.3 points x $6.80 x 0.85 = $50,737, so 3.3 points is exactly the charter's booking floor. Pre-registering 1.5 points with the claim that below it "the benefit does not clear the cost" asserts the opposite of the project's own finance model, and it is worse after realization decay — 1.5 pilot points x 0.85 is 1.3 points at rollout, well under half of what Finance will book. The same 1.5 is carried into 14-root-cause-evidence-pack.md lines 36 and 97 and 18-handover-and-benefit-validation.md line 125, so the charter is outvoted three to one by documents it is supposed to govern.

**Fix.** Derive the threshold from the charter and show the derivation in the row: "*3.3 percentage points — the smallest drop that delivers the $50,000 realized benefit Finance will book (charter section 5)*". Move 14-root-cause-evidence-pack.md lines 36 and 97 with it, or re-sign the charter's derivation first.

### L59 · CONTRADICTION · high

> | Power / required n per group | *80% power needs 6,900 per group; 8 weeks yields ~7,300* |

The primary metric is "7-day reopen rate, billing adjustments" (line 53), and this document's own line 85 sizes that population at "the 966 baseline-month adjustment contacts" — the figure signed off in 09-baseline-document.md lines 90 and 106. 966 a month over 8 weeks is 1,779 contacts across all four sites, and the treatment arm is two of the four, so about 889 per arm. "8 weeks yields ~7,300" per group overstates that by a factor of 8. It does not reconcile with the wider population either: at the charter's 266,000 billing tickets a year, two of four sites over 8 weeks is roughly 20,400 per arm. 7,300 matches no volume anywhere in the pack. A reader pre-registers a duration that cannot reach the n they committed to in the same row, and finds out eight weeks later.

**Fix.** Reconcile the volume before quoting either number. At 966 adjustment contacts a month, one arm accrues about 483 a month, so even the 1,685 in the paragraph below takes 3.5 months per arm and 6,900 takes over 14. Say so, then either widen the population (and change the metric row to say so), raise the detectable difference until required n and available volume meet, or drop the concurrent-control split for a switchback so both arms see the whole estate.

### L72 · UNFOLLOWABLE · high

> baseline 14.2%, detect a drop to 11%, alpha 0.05, power 80% — the calculator returns

These inputs cannot be entered in the tab named, and they do not produce 1,685. I read the sheet: C5 is captioned "Current rate", C6 "Change you want to detect", and C10 computes the second rate as =C5+C6, so the change is ADDED. The formula in C13 blanks the answer outright when C6 <= 0. A reader typing 14.2% and -3.2 gets an empty cell; typing 14.2% and +3.2 models a rise to 17.4% and returns 2,036. I reproduced 1,685 exactly only by entering 11% as the Current rate with +3.2 as the change — i.e. by typing the post-improvement rate into the baseline field, the opposite of the instruction given here.

**Fix.** State the entry the tab actually needs: "type the LOWER of the two rates as the current rate — here 11% — and 3.2 points as the change you want to detect; the tab adds them, so entering a drop as a negative returns a blank cell. It returns 1,685 per group, 3,370 across both arms." The same caveat belongs in 14-root-cause-evidence-pack.md line 44, which sends the reader to the same tab.

### L83 · CONTRADICTION · high

> *No more than +8% (445 s), and no point above the 468 s upper limit*

The pilot pre-registers a handle-time tolerance below the rise the project has already agreed to and predicted. 412 x 1.08 = 445.0 s. The charter's metric-impact disclosure (01-project-charter.md line 123) records the expected rise as "roughly 40 s to a 412 s contact" = 452 s, and the Tier 1 target formally moved "from 412 s to 450 s for the pilot quarter", signed by R. Mehta. Both sit above 445 s (450/412 = +9.2%, 452/412 = +9.7%). Section 5 line 97 then makes "Any counter-balancing metric breaches its stated tolerance" a kill criterion, and line 60 repeats the same 8% as an early-stopping trigger. The pilot is pre-registered to be killed for doing exactly what it was designed to do.

**Fix.** Set the tolerance to the level already negotiated in the charter: "*No more than 450 s — the Tier 1 target agreed for the pilot quarter (charter section 7) — and no point above the 468 s upper limit*", and change the 8% on line 60 to match. If 445 s is genuinely the limit, the charter's agreed target adjustment has to be renegotiated before this is circulated.

### L96 · WRONG · high

> - [ ] Primary metric moves in the wrong direction at any point

Two problems. First, it contradicts the stopping rule pre-registered 36 lines earlier, which the Champion signs: "Stop early only for harm: CSAT down more than 0.15 or handle time up more than 8%" (line 60). The word is "only". The reader holds two incompatible pre-registered rules and will be argued into whichever suits the room. Second, it is statistically unsound: at the volume this pilot actually has (about 110 adjustment contacts per arm per week on the 966-a-month population), the weekly difference between arms carries a standard error of roughly 4 points, so even against a true 4.9-point improvement the chance of at least one adverse week across a 7-week read is about two in three. Committing in advance to kill on that kills good solutions.

**Fix.** Replace with a rule that can only trip on signal and that matches line 60: "Primary metric worse than baseline by more than the practical threshold, sustained over two consecutive weeks after the excluded week 1".

### L105 · UNFOLLOWABLE · high

> | Primary: | *7-day reopen rate* | *14.2%* | *8.0%* | *1.5 pts* | *2-proportion* | *Weekly* |

Every cell sits one column right of where the header (line 103: Metric | Treatment | Control | Difference | 95% CI | p | Threshold met?) says it belongs: the metric name is under Treatment, the baseline under Control, the target under Difference, the practical threshold under 95% CI, the test name under p, and a reporting frequency, "Weekly", under "Threshold met?". Nothing in the row is a result. Lines 106 and 107 then repeat CSAT verbatim, so the two counter-balancing metrics registered in section 4 that are most likely to move — mean handle time and tickets open past 3 working days — have no row at all. This is the table the reader fills in to report the pilot outcome at the tollgate, and it cannot be filled in as headed.

**Fix.** Re-lay the rows against the headers, one row per metric registered in section 4, e.g. "| Primary: 7-day reopen rate | *9.3%* | *14.1%* | *-4.8 pts* | *-6.0 to -3.6* | *0.0001* | *Yes* |", then blank rows for "Counter-bal: mean handle time", "Counter-bal: CSAT" and "Counter-bal: open past 3 working days".

### L37 · WRONG · medium

> | Randomization / assignment mechanism | (agent-level / site-level / time-block / switchback) |

The rows above have already made this choice — sites A and C against sites B and D is site-level assignment with two clusters per arm — and two consequences go unstated. First, the row below lists "site" as a matching factor, which is impossible when site IS the assignment variable: anything differing between those four sites (supervisor, tenure mix, local release cadence — the very cadence cited on line 122) is perfectly confounded with treatment. Second, the power figures on line 59 are ticket-level, which assumes tickets are independent units. Under cluster assignment the unit assigned is the site, so with two sites per arm the effective sample size is closer to the number of sites than to 7,300, and the pre-registered precision is badly overstated. 18-handover-and-benefit-validation.md line 124 records this project discovering site-matching problems mid-analysis.

**Fix.** Fill the row in the worked example — "*site-level: A and C treated, B and D control*" — and add under the concurrent-control note: "Site-level assignment means the site, not the ticket, is the unit that was assigned. You cannot also match on site, and the ticket counts in section 3 overstate your precision. With fewer than about six sites per arm, prefer a switchback or time-block design so every site sees both conditions."

### L38 · UNFOLLOWABLE · medium

> | Matching factors | contact mix · tenure distribution · channel split · site · day-part |

The charter names this protocol as the mitigation for a specific named risk: "Adjustment volume roughly doubles over the billing cycle peak, the 12th to the 18th of each month... Pilot runs a full billing cycle and the read blocks on cycle week — protocol in 16-pilot-protocol.md" (01-project-charter.md line 145), and 02-sipoc.md line 61 repeats it ("block on cycle week in the analysis"). Nothing in this protocol blocks on cycle week: it is not in the matching factors, not in the stratification row on line 55 ("Contact reason and agent tenure band"), and not in the duration rule on line 41. A reader who follows the charter here to find the agreed mitigation does not find it, and runs a pilot in which the change is confounded with billing-cycle volume.

**Fix.** Add cycle week to both rows: "| Matching factors | contact mix · tenure distribution · channel split · site · day-part · billing-cycle week |" and "| Stratification to be applied | *Contact reason, agent tenure band and billing-cycle week* |", plus a duration note that the pilot must span whole billing cycles.

### L39 · CONTRADICTION · medium

> | Start date | *2026-06-01* |

The worked pilot starts before the tollgates that authorise it. This template is for "Improve, before the pilot runs" (line 8). The charter's milestone table puts the Measure tollgate actual at 2026-06-05 (baseline signed) and the Analyze tollgate at 2026-06-08 planned, 2026-07-24 actual, with Improve opening 2026-07-27 (01-project-charter.md lines 134-136) — the day this pilot ENDS (line 40). So the example pilots a solution four days before the baseline it is measured against was signed and weeks before the root causes it addresses were evidenced, which is the sequencing failure this template and 14-root-cause-evidence-pack.md exist to prevent.

**Fix.** Move the example dates after the Analyze tollgate the charter records — start 2026-07-27, end 2026-09-21 for eight whole weeks — so the worked example matches the milestone table in 01-project-charter.md and the "Improve, before the pilot runs" rule on line 8.

### L42 · CONTRADICTION · medium

> | **Weeks excluded from analysis** | (week 1 — learning curve is a confounder, not the steady state) |

Week 1 is thrown away, but the sample size on line 59 is quoted against all eight elapsed weeks: "8 weeks yields ~7,300". Seven analysed weeks yield about 6,388, below the 6,900 the same row says 80% power requires. The pilot is under-powered on its own two numbers, and the reader will not notice because the exclusion and the yield sit 17 lines apart in different sections and are never multiplied together.

**Fix.** Quote the yield on analysed weeks in the same row: "*80% power needs 6,900 per group; 8 weeks minus the excluded week 1 yields ~6,400 — short, extend to 10 weeks*". Add to the guidance block: "Size the pilot on analysed weeks, not elapsed weeks — week 1 is thrown away."

### L43 · UNDEFINED · medium

> | Blinding | (ambient / announced) |

The reader must choose between two words, one of which has a project-specific meaning that appears nowhere in this file. The curriculum page defines it in the M23 Hawthorne box — "use a blinded or ambient rollout (system change with no announcement) as the pilot mechanism" (six-sigma-blackbelt-support-ops.html line 1887) — and ties it directly to the realization discount in section 7, so the choice made here changes what factor is defensible on line 120. In the downloaded .md it is a bare parenthetical with no gloss and no worked-example entry, so it is a coin flip.

**Fix.** Spell out both options and the consequence: "| Blinding | (ambient — the system change ships with no announcement, so agents do not know they are in a pilot; or announced — they do, which inflates the effect and obliges a heavier realization discount in section 7) |"

### L73 · WRONG · medium

> 1,685 billing adjustments per group, 3,370 across both arms. The 6,900 in the table

The paragraph asserts 6,900 is "the same calculator asked a harder question", and it is not what that calculator returns. Running the sheet's own formula, n = (Z_a+Z_b)^2 x (p1q1 + p2q2) / d^2 at alpha 0.05, power 0.80 and a 1.5-point difference gives 8,118 (entering 12.7% as the current rate) or 8,868 (entering 14.2%) — never 6,900. The paragraph's own rule of thumb refutes it too: 1,685 at 3.2 points scaled by (3.2/1.5)^2 is 7,669. Because 6,900 is understated, "8 weeks yields ~7,300" reads as adequate when the pilot is below 80% power, and a null result gets reported as "the solution did not work" rather than "the pilot could not have seen it".

**Fix.** Recompute against the tab and print the inputs: "80% power at a 1.5-point difference needs 8,118 per group (current rate 11.5... entered as the lower rate 12.7%, change 1.5 points, alpha 0.05, power 0.80)". Then correct line 59, which no longer clears the requirement.

### L120 · CONTRADICTION · medium

> | Assumed realization factor | *0.85* |

The guidance immediately above says "Expect 20-40% of a pilot's measured gain to evaporate at full rollout" (line 113, matching the Hawthorne box at M23 of the curriculum page) — a factor of 0.60 to 0.80. The worked example then assumes 0.85, a 15% evaporation, outside the range it was just told to expect, and justifies it on line 122 with release cadence at sites B and D, which is an uptake-lag argument, not a Hawthorne one. 0.85 is also the number the charter uses for a different quantity entirely, the Finance harvest factor (01-project-charter.md line 53), under nearly the same row name ("Realization factor"). The reader cannot tell whether one discount or two applies, and the likeliest outcome is that the Hawthorne discount this section exists to enforce is never applied.

**Fix.** Use a factor inside the stated range and separate the two discounts: "| Assumed realization factor (Hawthorne decay) | *0.70 — mid-range of the 20-40% this template expects* |", with a note that the charter's 0.85 Finance harvest factor applies on top, not instead.

### L121 · CONTRADICTION · medium

> | **Forecast at full rollout** | *-4.2 points, worth $22,005 a year* |

The money contradicts the charter's own benefit model by a factor of three and has no derivation anywhere in the document. On the charter's basis (266,000 billing tickets a year at $6.80 a contact) 4.2 points is $75,970 gross and $64,575 after the 0.85 harvest factor; on the 966 adjustment contacts a month this document uses on line 85 it is about $3,300. $22,005 is neither. The charter also states that 3.3 points is worth $50,000 realized, so 4.2 points cannot be worth $22,005 unless one of the two is wrong. As printed, the worked example forecasts a benefit below the level the charter records as the floor "Finance will not book" beneath — in the section that teaches benefit forecasting. The reader cannot answer the first question Finance will ask, which is how the number was built.

**Fix.** Show the inputs in the row: "*-4.2 points x 266,000 billing tickets a year x $6.80 = $75,970 gross, $64,575 after the charter's 0.85 harvest factor*", and name which population the pilot generalises to. Check the result against the charter's $50,000 booking floor before circulating.

### L28 · UNDEFINED · low

> | Countermeasure hierarchy level | *2 — Design it out* |

The reader is asked for a level on a six-level ranking that is neither printed in this file nor pointed at. I found it on the "Countermeasure hierarchy" tab of 15-solution-selection-matrix.xlsx (1 eliminate the demand, 2 design it out, 3 guide it, 4 detect it, 5 standardise it, 6 train and remind, captioned "Best to worst"), and grep shows no .md in the pack prints it. Someone working from the downloaded file has only the worked example's "2" to reverse-engineer from and cannot tell whether 1 is the most durable or the least — which is the entire point of recording the level.

**Fix.** Point at the source and give the direction in the row: "| Countermeasure hierarchy level | *2 — Design it out* (1 eliminate the demand, 2 design it out, 3 guide it, 4 detect it, 5 standardise it, 6 train and remind; 1 is most durable — full ranking on the 'Countermeasure hierarchy' tab of 15-solution-selection-matrix.xlsx) |"

## 18-handover-and-benefit-validation.md

### L70 · CONTRADICTION · high

> | Mix-adjusted effect | *-4.7 points (unadjusted -4.9)* |

Verified three ways. (1) The block is headed "Required. An unadjusted before/after is not acceptable evidence" (line 63), so -4.7 is by the document's own rule the only admissible effect — yet the benefit four rows later is booked on 6.6 points (line 78), which is exactly 14.2% less 7.6%, the unadjusted before/after the section just outlawed. At 266,000 x $6.80 that is $119,381 claimed against $85,014 that the required evidence supports, 40% more. (2) The -4.9 is not a baseline-vs-post figure at all: I opened 13-hypothesis-test-log.xlsx row 11 and it is the pilot's two-proportion treatment-vs-control result — "-4.9 pts", CI "-6.1 to -3.7", n 7,420 vs 7,180, analyst M. Berenji, dated 2026-06-14, i.e. during the pilot and months before the 2026-08-04 control period. 16-pilot-protocol.md line 119 carries the same "-4.9 percentage points (CI -6.1 to -3.7)". So the mandatory section reports the pilot result while the money is calculated from the before/after. (3) It is also internally impossible: line 69 says "Adjustment method applied | *None required*", and if no adjustment was applied the adjusted and unadjusted effects cannot differ, yet they differ by 0.2 points. Part B compounds it — every replication estimate on lines 41-43 is priced off 6.6 points too.

**Fix.** Make both rows describe the same comparison as the benefit calculation, e.g. `| Unadjusted baseline-vs-post effect | *-6.6 points (14.2% to 7.6%)* |` and `| Mix-adjusted effect — the figure the benefit is booked on | *-6.3 points, standardised to the baseline contact-reason mix* |`, then flow that figure through lines 78-83. Add one sentence under line 63: "The Improvement row in the benefit calculation must be the mix-adjusted effect, not the difference between the two centre lines." Do not carry the pilot's treatment-vs-control effect into this section.

### L103 · UNFOLLOWABLE · high

> | 90-day | *2027-02-12* | *A. Okafor* | *7.9%* | *Held* | *No action* |

The data cells do not line up with the header on line 101, `| Checkpoint | Due date | Metric value | Booked benefit still valid? | Revision | Signed |`. A person's name, A. Okafor, lands under "Metric value"; the metric 7.9% lands under "Booked benefit still valid?"; "Held" under "Revision"; "No action" under "Signed". Line 104 is shifted identically. Both readings are consistent — either the header is missing an Owner column, or the data is missing a signature — and the reader cannot tell which, so they cannot know what to type where. This is the table the mandatory 180-day re-audit is recorded in (the blockquote on lines 106-109 makes it mandatory), and as printed no signature is ever captured for it. The due dates are also unanchored: I checked the arithmetic and 2027-02-12 is exactly 90 days after the Black Belt signature on line 94 while 2027-05-14 is exactly 180 days after the Champion signature on line 95 — two different clocks, neither stated. The document never says whether the clock starts at signature, at full implementation (2026-08-03, line 54) or at control period end. Under the curriculum's "Re-audit at 6 months" the mandatory re-audit would fall around 2027-02-03, which is the 90-day row's date, not the 180-day row's.

**Fix.** Give the header the columns the data actually uses and add the missing one: `| Checkpoint | Due date | Owner | Metric value | Booked benefit still valid? | Action taken | Signed |`, and fill Signed in the worked example. Add under the table: "Due dates run from the process owner's acceptance date in Part A."

### L59 · CONTRADICTION · medium

> | Post-period UCL / LCL | *9.1% / 6.1%* |

Three artifacts in this pack give three different limit sets for the same metric in the same worked example at the same moment. I opened 17-control-plan.xlsx: the Control plan sheet's first row is "7-day reopen rate, billing | <= 8.0% | ... | Laney p' (attribute, large n) | 0.086 | 0.104 | 0.068" — centre 8.6%, UCL 10.4%, LCL 6.8%. The curriculum page's M25 control-plan example gives a third pair: "Laney p' chart, weekly, UCL 9.4% / LCL 6.2%". This document says centre 7.6% with 9.1%/6.1%. That workbook is the artifact Part A line 20 tells the reader to hand over, and its own reaction trigger is "Any point above the UCL" — so the same observation fires a response at 9.1% in this document and stays silent until 10.4% in the plan the owner was handed. The reader ends up with two charts for one metric and no way to tell which limits the owner must react to. (One part of this I could not confirm: 8.4% at the 180-day re-audit on line 104 sits inside all three limit sets, so it is not a signal either way.)

**Fix.** Carry the limits that are written into 17-control-plan.xlsx and say so, e.g. `| Post-period metric (centre line) | *8.6% — the centre line and limits written into 17-control-plan.xlsx; there must be one chart for this metric, not two* |` and `| Post-period UCL / LCL | *10.4% / 6.8%* |`. Whichever of the three is wrong, fix it so this document, the workbook and the curriculum example agree.

### L60 · UNDEFINED · medium

> | Process stable in the control period? | *Yes — no points outside the limits, no runs of 8* |

"Runs of 8" is never explained here, and it is one of the two tests that decide whether the whole benefit claim is admissible. Eight of what, on which side, of what line? I grepped: the phrase appears in no other .md in the pack. Nor can the reader resolve it from the curriculum, which is itself split — the body says "eight points in a row on one side" while the Nelson rules glossary entry says "Nine points on one side of the centre line", and 17-control-plan.xlsx says "8 points under the centre line". The reader is also not told what chart to build the post period on, or whether to recompute limits from control-period data or carry the baseline limits forward. 09-baseline-document.md asks exactly this stability question and requires both "Chart type used" and "Chart type justification" (lines 36-37); this document asks for neither, and it is the one template in the pack that points at no workbook at all, while 27-control-charts.xlsx ships a "Laney p-prime" sheet that does precisely this job.

**Fix.** Add a row above it naming the chart and where it was built — Laney p' weekly, limits recomputed from control-period data, built in `27-control-charts.xlsx` — and spell the rule out in place of the shorthand: "no point outside the limits, and no run of 8 consecutive points on the same side of the centre line". Pick 8 or 9 and make the pack consistent.

### L67 · WRONG · medium

> | Contact-mix chi-square, baseline vs post (p) | *0.38 — no material mix shift* |

"Material" is decided from a p-value alone, which is the specific error the curriculum's chi-square tool card warns against. I read it: "Read the standardized residuals, cell by cell. The omnibus p-value tells you something changed; the residuals tell you what... Report Cramer's V as an effect size, because at support volumes almost everything is significant," and "Standardized residuals beyond +/-2 flag the cells driving the association." This section asks for neither and states no threshold at which a shift becomes material, so at 266,000 contacts a reader who gets p = 0.01 has no idea whether to adjust. Line 68, "Mix shift present? | *Checked: contact-reason mix chi-sq p = 0.38, no material shift*", restates line 67 with the same number, so the reader cannot tell what the second row wants that the first did not. And line 69, "Adjustment method applied | *None required*", means the one mandatory analytical step in the document is demonstrated by an example that skips it. I grepped the file: it references no workbook and no other template anywhere, and names no adjustment method, so a reader who does have a shift has nothing to do and nowhere to do it.

**Fix.** Collapse lines 67-68 into one row that carries the effect size as well as p ("chi-square p = 0.38; Cramer's V = 0.03; no reason with a standardised residual beyond +/-2"), state a materiality rule that is not the p-value (e.g. adjust whenever Cramer's V exceeds 0.10 or any reason's share of volume moves more than 3 points), and name the permitted adjustment methods in the row label — direct standardisation to the baseline reason mix, stratified rates weighted by the baseline mix, or logistic regression with reason as a covariate — with one of them ticked in the worked example.

### L79 · WRONG · medium

> | Annualized units affected | *17,556 reopens avoided — 266,000 x 6.6 points* |

This annualises an effect measured 2026-08-04 to roughly 2026-11-02, and the mandatory comparison section's only guard is a contact-reason chi-square, which cannot detect seasonality. Two documents in the same pack forbid this. 09-baseline-document.md line 96 keeps the January price-letter peak in the baseline precisely because "It happens every January, and the post-project comparison has to span the same season or it will read the calendar as an improvement"; 16-pilot-protocol.md lines 45-47 say "Before/after in support is contaminated by demand shifts, product releases, staffing changes and seasonality." The baseline window is Jan-Mar (extract 2026-04-02, 12 weeks, including 2026-01-05 to 2026-01-30 and the w/c 2026-02-16 release); the control period is Aug-Nov. So the benefit is annualised over a year containing a seasonal disputes peak the new process has never run through, and lines 65-70 certify the comparison as clean. In fairness the size is modest — the baseline document records the January reopen rate as 14.6% against a 14.2% mean, inside the control limits — but the reader is told the comparison is confounder-free when the pack's own rule says it has not been checked.

**Fix.** Add a row to the mix-adjusted comparison recording seasonal coverage — does the control period span the same season as the baseline window? — and answer it in the worked example ("No. Baseline Jan-Mar includes the January price-letter peak, 09-baseline-document.md section 6; control period Aug-Nov does not"). Then name the caveat on line 79 so the annualised figure is read as an upper bound re-checked at the 180-day re-audit, which does span January.

### L82 · WRONG · medium

> | Realization factor applied | *0.85* |

A realization factor discounts a pilot result to forecast a rollout result. This document's own Part E defines it that way on line 125: "Take the realization factor from a previous project's pilot-to-rollout decay and name the project it came from." 16-pilot-protocol.md line 120 has already applied this same 0.85 to the pilot effect to forecast -4.2 points. Here the identical factor is applied a second time — to 91 days of measured full-implementation performance. The programme benefit accounting policy on the curriculum page is explicit that this is not how it works: "Realization discount: benefits are booked at the 90-day measured rate, not the pilot rate. Typical realization is 60-80% of pilot." Once you have the 90-day measured rate you have the realized number; discounting it again haircuts a gain that has already been realized, here by $17,907. The document never defines the term, never asks for its basis, and Part E line 125 says the 0.85 "was settled by discussion rather than evidence, and Finance rightly pushed back on it" — while line 96 shows Finance signing. The reader cannot tell whether the factor they are being shown was accepted or rejected.

**Fix.** Either drop the row and set Realized annual benefit equal to gross, with a note that the benefit is booked at the 90-day measured rate so no pilot-to-rollout discount is taken; or, if the programme genuinely discounts at closure for partial harvest (as 01-project-charter.md line 53 frames it), say which of the two things the factor is and add a `| Basis for the realization factor |` row citing the policy section. As written the same 0.85 is used for two different jobs in one worked example.

### L85 · CONTRADICTION · medium

> | Harvest mechanism | *Hiring avoidance — two billing roles removed from the Q1 plan* |

01-project-charter.md lines 65-68 does this conversion explicitly for the same worked project and gets a different answer: "16,492 reopens avoided a year at 412 s of handle time is 1,887 agent hours, about 1.2 FTE at 1,530 handling hours a head. WFM removes 1.2 FTE from the Q4 Tier 1 requisition." I checked the arithmetic: 16,492 x 412 s = 1,887 h, 1,887/1,530 = 1.23 FTE. On the same arithmetic this document's 17,556 reopens is 2,009 agent hours, 1.31 FTE — so "two billing roles" is more than 50% above what the avoided volume can fund, and it names the Q1 plan where the charter names the Q4 Tier 1 requisition. The charter is the document whose own header (line 6) says "Nothing else in the project is allowed to contradict it," and the harvest mechanism is the line Finance validates against at closure. The worked example also skips the contacts-to-FTE step entirely, so a reader never sees how avoided contacts become a requisition line and cannot reproduce or defend the claim.

**Fix.** Show the conversion and match the charter: add `| Capacity freed (FTE) | *1.31 FTE — 17,556 reopens x 412 s = 2,009 agent hours, at 1,530 handling hours a head* |` immediately above, then `| Harvest mechanism | *Hiring avoidance — 1.3 FTE removed from the Q4 Tier 1 requisition, amended by WFM* |`. If the requisition genuinely moved from Q4 to Q1, say so rather than leaving the charter contradicted silently.

### L87 · UNFOLLOWABLE · low

> | Benefit claim period | 12 months from ____________ |

The document never says what date starts the clock and offers four plausible candidates on the same page: full implementation 2026-08-03 (line 54), control period start 2026-08-04 (line 55), control period end, and Finance sign-off 2026-11-20 (line 96). The spread between the first and last is nearly four months of claimed benefit. The programme policy settles it — I found it on the curriculum page: "Benefit claim period: 12 months from full implementation. No project claims benefit in perpetuity" — but I grepped all the templates and that rule appears in none of them, so the reader working from the downloaded .md cannot see it. The document is explicit about its other policy rules (the mandatory 6-month re-audit, "minimum 90 days", "an unadjusted before/after is not acceptable evidence"), so the omission of the one rule that bounds the money is conspicuous. (The reporter's claim that this is the only unfilled field in Part C is wrong — line 56 and line 84 are also unfilled.)

**Fix.** `| Benefit claim period | 12 months from the full implementation date above — *2026-08-03 to 2027-08-02*. Never from Finance sign-off, and never in perpetuity. |`

## Rejected

- '| Input (x) | Controllable | Noise | SOP-fixed | Notes |' — REJECTED. The header terms are each defined by demonstration in the Notes column of the same table, in the row that uses them: line 58 defines SOP-fixed ('Set by the Finance delegation-of-authority policy. Raising it is a policy request, not a process change') and line 61 defines Noise in the operative sense, not the noisy-data sense ('We cannot move when customers call, so block on cycle week in the analysis instead of trying to control it'). A reader can classify their own inputs from those examples without a glossary. The report's supporting claim that 'Every other section in this document carries a one-line rule; this one carries none' is false — the Scope boundaries table and both Explicitly IN/OUT lists carry no rule line either; only the SIPOC table does (line 32). What genuinely remains is that the section never states what the classification feeds (the x list for 11-cause-effect-xy-matrix.xlsx), which is a four-sentence addition to a boundary document aimed at a Black Belt audience — an improvement request, not something a reader stalls on. The proposed fix makes the file longer without making the checkboxes any easier to tick.
- '*No verbatim asks for it. The handful of agents who ring back off their own bat ' — The finding reads only the first sentence and calls the classification an inference from silence. The second sentence is the presence-side evidence it says is missing: when an agent does ring back unprompted, customers name them in CSAT free text. Absence tolerated plus unsolicited praise when present is the delighter signature, and it is exactly what separates a delighter from an indifferent — an indifferent produces no praise when present either. The pack's own Kano workbook independently agrees: 23-kano-analysis.xlsx, sheet "Kano analysis" row 11, classifies the same need ("Proactive notice before I notice the problem") from Like present / Live with it absent, and its comment ties it to the posting-confirmation fix. Requiring the functional/dysfunctional pair in the Evidence column would be a methodological upgrade to the whole table, not a correction of this row — every other row uses contact counts and interview evidence too, so the criticism is not specific to what it quotes.
- '## Hop-by-hop trace' — Naming quibble, not a blocker. The tollgate item is "Data lineage diagram complete for the primary metric" (HTML line 1513) and the mandatory deliverable at lines 1460-1461 is "a one-page lineage diagram... source system, every join and filter, every business rule, refresh cadence, known gaps, and the owner of each hop" — which is precisely the column set of the header at line 24. The curriculum itself equates the two: its tool card is titled "Data lineage trace", its "How to run it" describes this table step for step ("Pick one real record... At each hop record the transformation, join, filter and business rule applied, plus the owner"), and it links out to this exact file as "Template: Data Lineage Trace". A reader who fills this in has produced the required content; the proposed fix adds a paragraph of reassurance and an optional drawing instruction without changing what the reader must do. The real defect in this table is the column shift at line 26, reported separately.
- '| Number of distinct categories (ndc) | *4* | want ≥ 5 |' — The claim that a reader holding these results cannot tell which verdict box to tick is not supported by the file. Line 57 already states the verdict inline for the worked example ("*28.4% — marginal, investigate before use*"), line 65 maps the %study-variation bands directly onto the three boxes in section 4, and 29-msa-gage-rr.xlsx cell F55 prints the verdict string "MARGINAL — usable with stated caution" verbatim for anything between 10% and 30%, reading %study variation alone. The ndc criterion is worded "want >= 5", not "must", and the workbook's C64 note explains what ndc 4 means in practice. Adding a combination rule would restate what the document already resolves.
- '**Action:**' — This is house style, not a defect. 07-msa-attribute-agreement.md — the sibling MSA template — likewise leaves all three verdict checkboxes unticked in its section 5 and ends with the identical single "Study run by: ____________  Date: __________" line and no owner-acceptance field, so neither the unticked boxes nor the missing acceptance signature distinguishes this document. The interpretive guidance the reporter says is missing is present, just placed in section 2: lines 68-70 tell the reader that reproducibility dominating repeatability means the fix is the definition and "Buying a better timer would change nothing." What is left is a blank field a reader is meant to fill in, which is what a template is.
- '| 4 | *New-hire tenure under 90 days* | *Statistical only* | *0.4 pts* | *6%* | ' — The verdict glosses itself in the cell — "Held — no mechanism described yet" states both what it means and why it applies, against a two-key rule stated 70 lines above. The claim that the reader cannot tell whether a held cause counts toward the gate is wrong on the text: line 85 says "if the **accepted** root causes explain less than ~60%", which answers it. What remains is that the % of gap column sums to 103% across accepted, held and rejected rows — arithmetic reconciliation, which the machine pass already covers.
- '| 3 | *Reopen metric counts same-reason only* | *Mechanism only* | *—* | *—* | *' — The two tables have different jobs and both say so. The summary is a register of every cause the pack assessed — it has an "Accepted" column whose values include Rejected and Held, so rejected causes belong there by design. The table on line 90 is for candidate causes tested and ruled out, and its columns (How tested / Result / Why rejected) demand a test that cause 3 never had, since it failed for want of a statistical key. Wanting one canonical location is a structural preference, not something a reader is blocked by.
- '| Effect size + 95% CI | *−4.9 percentage points (CI −6.1 to −3.7)* |' — The direction is already stated: line 29 names the comparison as "deferred-close cohort vs control", and under the ordinary convention that "A vs B" means A minus B, a negative effect correctly says the cohort that waited for the posting reopened 4.9 points less. That is consistent with the +4.9 contribution on line 64, which is the effect of the opposite condition — closure permitted before posting. The document is coherent as written; the proposed fix adds a sentence restating a convention the row already implies.
- '| Benefit type | hard / soft / cost avoidance |' — The claimed contradiction with 01-project-charter.md is not one. The charter's six options are sub-types of exactly these three parents — four Hard, one Soft, one Cost avoidance — so a coarser but compatible taxonomy, not a conflicting one. The supporting claim that this is "the one field in a fully worked example left unticked" is false: line 56 (Control period end) and line 87 (Benefit claim period) are also unfilled, and the charter's own six checkboxes are unticked too, which is the pack's convention throughout. A reader who filled the charter has already met the sentence "Hard - hiring avoidance against an approved plan" and is not going to file the same mechanism under cost avoidance here.
- '**Total replication opportunity identified:** $____________' — The field name answers the question the finding says is unanswered: "identified" is not "committed", so the total is everything identified, $53k. The claimed three-way ambiguity between $18k, $44k and $53k is manufactured. Beyond that, this is a fill-in blank in a template — filling every blank with a worked value is a preference, and the fix adds a counting rule for a sum the reader can already do.
- '- [ ] Lessons learned documented and posted to the replication library' — Not UNDEFINED. "Replication library" is transparent in plain English, and Part B of this very document is the replication assessment, so the reader understands the concept without a definition. The real complaint is "my organisation may not have one yet", which is true of several items in this checklist and does not make the term a term of art a reader stalls on. The curriculum does put it at months 12-24, but a reader without one skips or improvises the box; nothing about the signature on line 29 is mechanically blocked.
- '**Who signs it.** Process owner accepts the controls · Finance validates the ben' — This is a pack-wide convention, not a defect in this document. Every template's "Who signs it" line is a thematic summary rather than an exhaustive roster, and they all differ from their own signature tables: 01-project-charter.md line 10 says "Champion, Process owner and Finance partner sign" while its table (lines 160-163) lists Champion, Black Belt, Finance partner and Master Black Belt with no Process owner; 09-baseline-document.md line 10 names the Champion, who appears nowhere in its sign-off table. The harm story is also speculative — the reader sees the full signature table the moment they open the document, and has already met the Master Black Belt row in the charter at Define.