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
| Fleiss' / Cohen's kappa | | see below | |

**Kappa interpretation:** >0.90 excellent · 0.75–0.90 good · 0.40–0.75 marginal (do not
use for individual performance management) · <0.40 unacceptable (halt any use of this
data in decisions).

> Report raw agreement **and** kappa together. At high prevalence of one category, raw
> agreement can be 95% while kappa is near zero.

## 3. Results — by appraiser

| Appraiser | Within-appraiser % | vs standard % | Bias direction (lenient / strict) |
|---|---|---|---|
| | | | |

## 4. Results — by rubric item / category
**This is the actionable table.** Rubric items are not equally reliable.

| Rubric item / category | Kappa | Agreement % | Verdict | Action |
|---|---|---|---|---|
| | | | | |
| | | | | |
| | | | | |

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
