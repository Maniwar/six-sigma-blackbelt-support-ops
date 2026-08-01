# Measurement System Analysis — Attribute Agreement Study

<!-- guidance -->
## How to use this

**What it is for.** Proves your QA scoring, disposition coding or survey interpretation is a measurement system rather than a set of opinions.

**When.** Measure, before you baseline anything that depends on a human judgement.

**Who signs it.** Black Belt runs it · QA manager owns the remediation

**The mistake this prevents.** Reporting percent agreement instead of kappa. Two analysts who both pass 90% of calls agree 82% of the time by luck alone; kappa removes that and routinely lands at 0.35–0.60 where the organisation believed it was near 1.0.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 14.2% 7-day reopen rate against a target of 8%. Delete them as you fill your own in.*

---

**Measurement being validated:** <QA scoring / disposition coding / intent tagging / severity classification>

## 1. Study design

| Field | Value |
|---|---|
| Appraisers (n, names/IDs) | *4 — QA analysts QA-01 to QA-04* |
| Items sampled (n) | *50 recorded billing contacts* |
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
| Fleiss' / Cohen's kappa | *0.41* | see below | *>= 0.80* |

**Kappa interpretation:** >0.90 excellent · 0.75–0.90 good · 0.40–0.75 marginal (do not
use for individual performance management) · <0.40 unacceptable (halt any use of this
data in decisions).

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
does the same arithmetic from a raw pass/fail grid, including Fleiss' kappa for more
than two appraisers; the sample size, and the power it buys you, come from the sample
size calculator in `05-data-collection-plan.xlsx`. The overall figures above are for
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
| *Item 3 — correct reason code applied* | *0.71* | *82%* | *Marginal (0.60–0.80)* | *Collapse the five reason codes to three. "Proration misunderstood" and "wrong plan applied" are picked interchangeably; merge or write a decision rule that separates them* |
| *Item 4 — resolution confirmed* | *0.52* | *80%* | *Unacceptable (<0.60)* | *Rewrite the item. "Confirmed" must mean the adjustment is visible as posted on the account, not that the agent said the customer was happy. Re-test before any reopen figure is used in a decision — this is the item the whole project rests on* |
| *Item 7 — empathy demonstrated* | *0.58* | *84%* | *Unacceptable (<0.60)* | *Write a partial-credit rule with worked examples, or drop the item. More calibration meetings on the current wording will not move it* |

> Typical pattern: objective items ("verified customer identity") score >0.9;
> subjective items ("demonstrated empathy") score 0.2–0.4. The fix for an unmeasurable
> item is not more calibration meetings — it is rewriting or removing the item.

## 5. Verdict

- [ ] **Acceptable** — proceed, monitor with periodic calibration
- [ ] **Marginal** — usable for aggregate analysis only; not for individual performance
- [ ] **Unacceptable** — remediate and re-test before using this data anywhere

## 6. Remediation and re-test

| Action taken | Date | Re-test kappa | New verdict |
|---|---|---|---|
| Rubric items rewritten | *Items 4 and 7* | *QA manager* | *2026-05-22* |
| Decision rules added | *Written rule for partial credit on empathy* | *QA manager* | *2026-05-22* |
| Examples library built | *Six scored calls per rubric item* | *QA leads* | *2026-06-05* |
| Categories merged / removed | *Merged 'tone' into 'empathy' — never scored apart* | *QA manager* | *2026-05-29* |
| Calibration cadence set | *Fortnightly, 45 minutes, all analysts* | *QA manager* | *2026-06-01* |

## 7. Ongoing control

| Control | Frequency | Owner |
|---|---|---|
| Calibration session | *2026-06-12* | *Complete* |
| Blind re-score audit | *2026-06-26* | *Complete* |
| Kappa re-measurement | *2026-07-10* | *kappa 0.84 — passed* |

Study run by: ____________  Date: __________
