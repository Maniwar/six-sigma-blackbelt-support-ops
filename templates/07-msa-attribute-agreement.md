# Measurement System Analysis — Attribute Agreement Study

<!-- guidance -->
## How to use this

**What it is for.** Proves your QA scoring, disposition coding or survey interpretation is a measurement system rather than a set of opinions.

**When.** Measure, before you baseline anything that depends on a human judgement.

**Who signs it.** Black Belt runs it · QA manager owns the remediation

**The mistake this prevents.** Reporting percent agreement instead of kappa. Two analysts who both pass 90% of calls agree 82% of the time by luck alone; kappa removes that and routinely lands at 0.35–0.60 where the organisation believed it was near 1.0.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 7-day reopen rate on in-scope billing adjustments of 14.2% against a target of 8%. That rate is the project's Y, defined separately as OD-BIL-004-ADJ and measured at 137 reopens in 966 in-scope adjustments in the baseline month (09-baseline-document.md:90). The whole Billing queue's 7-day reopen rate under OD-BIL-004 v2 is also 14.2%; it is a different quantity, and it is context only. Delete them as you fill your own in.*

---

**Measurement being validated:** <QA scoring / disposition coding / intent tagging / severity classification>

## 1. Study design

| Field | Value |
|---|---|
| Appraisers (n, names/IDs) | *4 — QA analysts QA-01 to QA-04* |
| Items sampled (n) | *50 recorded in-scope billing adjustment contacts — the OD-BIL-004-ADJ population, not the whole Billing queue* |
| Sample stratification | ___ clear pass · ___ clear fail · ___ genuinely ambiguous |
| Replicates per appraiser | (minimum 2) |
| Separation between replicates | (minimum 5 days) |
| Order randomized? | Yes / No |
| Appraisers blinded to prior score? | Yes / No |
| Standard established by | (senior panel consensus, agreed before the study) |
| Standard shown to appraisers? | **Must be No** |

> **Do not use a random sample.** With a random sample and a high pass rate you will
> have almost no power to detect disagreement, and kappa will collapse to near zero
> through the prevalence paradox. Deliberately load the sample with failures and
> ambiguous cases.

## 2. Results — overall

| Measure | Result | Threshold | Verdict |
|---|---|---|---|
| Within-appraiser agreement (repeatability) | *78%* | *>= 90%* | *Fail — QA-03 at 62%* |
| Between-appraiser agreement (reproducibility) | *64%* | *>= 90%* | *Fail* |
| Agreement with the standard (accuracy) | *71%* | *>= 90%* | *Fail* |
| Fleiss' / Cohen's kappa | *0.41* | *>0.80* | *Fail — unacceptable (<0.60): halt any use of this data in decisions* |

**Kappa interpretation:** >0.80 good · 0.60–0.80 marginal (do not use for individual
performance management) · <0.60 unacceptable (halt any use of this data in decisions).
One scale, and it is the one section 4 applies item by item: the pass bar in the table
above is >0.80, so a kappa of exactly 0.80 is marginal and not a pass, and <0.60 is what
blocked the reopen figure at item 4.

> Report raw agreement **and** kappa together. At high prevalence of one category, raw
> agreement can be 95% while kappa is near zero.

**How to work this out.** The formula is one line:
kappa = (observed agreement − expected agreement) / (1 − expected agreement).
Expected agreement is what two analysts would have hit by luck alone, given how often
each of them says "pass". *Worked on the "resolution confirmed" item below: both
analysts pass about 70% of contacts, so luck alone gets them to 0.70 × 0.70 + 0.30 ×
0.30 = 0.58. They actually agreed on 80% of the 50 contacts. kappa = (0.80 − 0.58) /
(1 − 0.58) = 0.22 / 0.42 = 0.52 — 80% agreement, of which nearly three-quarters was
luck.* Tab **2 QA agreement (kappa)** of `19-black-belt-calculators.xlsx` in this pack
does the same arithmetic from a raw pass/fail grid — Cohen's kappa, from the four
counts two appraisers produce, which is what that tab takes. **The pack does not compute
Fleiss' kappa.** With more than two appraisers, run the tab once per pair and report the
spread as well as the mean: four appraisers is six runs, and one pair sitting well below
the others is the finding. For an exact Fleiss' kappa use Minitab's *Attribute Agreement
Analysis*, or `statsmodels.stats.inter_rater.fleiss_kappa` in Python. The sample size
calculator in `05-data-collection-plan.xlsx` sizes a comparison of two rates — you give
it the power you want and it returns the sample size per group — so it does not size an
attribute study, which is items x appraisers x replicates. The overall figures above are for
the contact-level pass/fail verdict, which is why they sit below the per-item numbers
in section 4 — the verdict flips whenever any single item does.

## 3. Results — by appraiser

| Appraiser | Within-appraiser % | vs standard % | Bias direction (lenient / strict) |
|---|---|---|---|
| *QA-01* | *88% (44 of the 50 re-scores matched)* | *80%* | *Strict — fails "resolution confirmed" unless the closing note quotes the customer back* |
| *QA-02* | *84% (42 of 50)* | *76%* | *Lenient — accepts the agent's own note that the customer was happy as confirmation* |
| *QA-03* | *62% (31 of 50)* | *62%* | *No stable direction — the 19 contacts scored differently on the re-score split both ways* |
| *QA-04* | *78% (39 of 50)* | *66%* | *Lenient — treats an adjustment raised but not yet posted as confirmed* |

## 4. Results — by rubric item / category
**This is the actionable table.** Rubric items are not equally reliable.

| Rubric item / category | Kappa | Agreement % | Verdict | Action |
|---|---|---|---|---|
| *Item 1 — customer identity verified* | *0.89* | *98%* | *Good (>0.80)* | *No change. Use it as the calibration anchor — it is the item analysts already agree on* |
| *Item 2 — adjustment amount matches the disputed charge* | *0.84* | *96%* | *Good (>0.80)* | *No change. Re-measure quarterly with the blind re-score audit* |
| *Item 3 — correct reason code applied* | *0.71* | *82%* | *Marginal (0.60–0.80)* | *Collapse the five reason codes. This study prescribed three; the handbook records them as having been rewritten into four (`six-sigma-blackbelt-support-ops.html`, Measure section), so the count actually in force is unsettled and the QA manager must state the final code list here before the next re-test. "Proration misunderstood" and "wrong plan applied" are picked interchangeably; merge or write a decision rule that separates them* |
| *Item 4 — resolution confirmed* | *0.52* | *80%* | *Unacceptable (<0.60)* | *Rewrite the item. "Confirmed" must mean the adjustment is visible as posted on the account, not that the agent said the customer was happy. Re-test before any in-scope-adjustment reopen figure (OD-BIL-004-ADJ) is used in a decision — this is the item the whole project rests on* |
| *Item 7 — empathy demonstrated* | *0.58* | *84%* | *Unacceptable (<0.60)* | *Write a partial-credit rule with worked examples, or drop the item. More calibration meetings on the current wording will not move it* |

> Typical pattern: objective items ("verified customer identity") score >0.9;
> subjective items ("demonstrated empathy") score 0.2–0.4. The fix for an unmeasurable
> item is not more calibration meetings — it is rewriting or removing the item.

## 5. Verdict

- [ ] **Acceptable** — proceed, monitor with periodic calibration
- [ ] **Marginal** — usable for aggregate analysis only; not for individual performance
- [ ] **Unacceptable** — remediate and re-test before using this data anywhere

## 6. Remediation and re-test

| Action taken | Detail | Owner | Date | Re-test kappa | New verdict |
|---|---|---|---|---|---|
| Rubric items rewritten | *Items 4 and 7* | *QA manager* | *2026-05-22* | `<not recorded>` | `<not recorded>` |
| Decision rules added | *Written rule for partial credit on empathy* | *QA manager* | *2026-05-22* | `<not recorded>` | `<not recorded>` |
| Examples library built | *Six scored calls per rubric item* | *QA leads* | *2026-06-05* | `<not recorded>` | `<not recorded>` |
| Categories merged / removed | *Merged 'tone' into 'empathy' — never scored apart* | *QA manager* | *2026-05-29* | `<not recorded>` | `<not recorded>` |
| Calibration cadence set | *Fortnightly, 45 minutes, all analysts* | *QA manager* | *2026-06-01* | `<not recorded>` | `<not recorded>` |

> The last two columns read `<not recorded>` for a reason. None of the five rows above
> carries a re-measured kappa. The pack holds two post-remediation figures on this rubric
> and never says whether they are one re-test or two: the 0.84 dated 2026-07-10 in section
> 7, which names no item, and kappa 0.78 after the reopen-reason codes were rewritten
> (`six-sigma-blackbelt-support-ops.html`, Measure section), which answers the action
> section 4 sets on item 3 rather than any row here. Neither is tied to a row above. The QA
> manager, who owns four of the five rows, must re-run the study of section 1 after each
> action and record here, alongside the kappa, the statistic, the rubric item it applies
> to, the appraiser count and the sample size, before any in-scope-adjustment reopen figure
> (OD-BIL-004-ADJ) is used in a decision — that is the gate section 4 sets on item 4.

## 7. Ongoing control

| Control | Frequency | Owner | Last run | Result |
|---|---|---|---|---|
| Calibration session | *Fortnightly, 45 minutes* | *QA manager* | *2026-06-12* | *Complete* |
| Blind re-score audit | `<not recorded>` | `<not recorded>` | *2026-06-26* | *Complete* |
| Kappa re-measurement | `<not recorded>` | `<not recorded>` | *2026-07-10* | *kappa 0.84 — read the note below before calling it a pass* |

> **Frequency and owner are blank on the last two rows for a reason.** The pack records the
> date each of those controls last ran and nothing else: it states no cadence for either and
> assigns neither to a person. The "quarterly" at item 2 in section 4 is an instruction
> attached to that one rubric item's re-measurement, not a declared cadence for these
> controls — and the two dates above are fourteen days apart, so the two did not in fact run
> together. A. Okafor, control-plan owner (`18-handover-and-benefit-validation.md:65`), must
> state the cadence and the named owner of both controls before the 90-day checkpoint on
> 2027-02-12. The first row is filled because section 6 records that cadence and that owner
> at the "Calibration cadence set" action.
>
> **The 0.84 is not yet "the" post-remediation kappa.** It is recorded with no statistic
> (overall contact-level verdict, or one rubric item?), no item, no appraiser count and no
> sample size, so there is nothing to compare it with the 0.41 in section 2. The pack also
> carries a second post-remediation figure — kappa 0.78 after the reopen-reason codes were
> rewritten (`six-sigma-blackbelt-support-ops.html`, Measure section) — and never says
> whether that is this re-test or a different one on a different item. QA manager to
> restate each re-test in the form of section 1 — statistic, item, appraisers (n), items
> (n) — before either figure is used to clear the gate section 4 sets on item 4.

Study run by: ____________  Date: __________
