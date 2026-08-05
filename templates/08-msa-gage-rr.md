# Measurement System Analysis — Continuous Gage R&R

<!-- guidance -->
## How to use this

**What it is for.** The continuous-data equivalent: how much of the variation you are about to analyse is the measurement rather than the process.

**When.** Measure, before capability or any hypothesis test on a continuous metric.

**Who signs it.** Black Belt runs it · the system owner fixes what it finds

**The mistake this prevents.** Accepting a study whose parts do not span the real range — and then reading the result backwards. If every sampled contact is a routine one, part-to-part variation collapses, and %study variation measures the gage against the *total*, so the gage's share rises: a sound gage is condemned, and `ndc` falls with it. Narrow sampling does not flatter a gage, it fails one. The number that does not move with part spread is **%Tolerance** (B65 in the workbook), which measures the gage against the spec width instead — use it when you cannot get the range, and say which one you judged on.

*Italic entries below are a worked example from one project — billing adjustments closing before the posting confirms, driving a 7-day reopen rate on in-scope billing adjustments of 14.2% against a target of 8%. That rate is the project's Y, defined separately as OD-BIL-004-ADJ and measured at 137 reopens in 966 in-scope adjustments in the baseline month (09-baseline-document.md:90). The whole Billing queue's 7-day reopen rate under OD-BIL-004 v2 is also 14.2%; it is a different quantity, and it is context only. Delete them as you fill your own in.*

---

**Measurement being validated:** *handle time on an in-scope billing adjustment (the OD-BIL-004-ADJ population, not the whole Billing queue), in minutes, as the analyst clocks it — not the CRM timestamp, which is a different gage and has to be validated separately*

## How to work this out

You do not have to do this by hand. **`29-msa-gage-rr.xlsx`** in this same pack is the
crossed ANOVA: type the 90 readings into the green grid at B13:J22 and every number in the tables
below appears, with each sum of squares written as a formula you can point at.

The arithmetic it runs, so you know what you are signing:

- Split the total variation into **parts**, **appraisers**, **part × appraiser** and
  **repeatability**, using a sum of squares for each — `SS = DEVSQ(block)` in Excel terms.
- Turn each mean square into a **variance component**. Repeatability is the error mean
  square directly; the others are differences between mean squares, divided by how many
  readings sit behind each. A negative result means the term is not real, so it is set to
  zero and pooled into error.
- **Gage R&R** = repeatability + reproducibility. **Total** = Gage R&R + part-to-part.
- **% Contribution** compares variances: `component ÷ total`. **% Study variation**
  compares standard deviations: `√component ÷ √total`. That is why the two columns differ
  so much, and why the verdict is read off the second one.
- **ndc** = `1.41 × (SD part-to-part ÷ SD Gage R&R)`, truncated to a whole number.

If you are running this in Minitab it is *Stat → Quality Tools → Gage Study → Gage R&R
(Crossed)*, ANOVA method. The numbers below are from the workbook.

## 1. Study design (crossed, ANOVA method)

| Field | Value |
|---|---|
| Parts / items (n) | *10 — spanning 5.2 to 15.9 minutes, deliberately including the two slowest cases we could find* (minimum 10, spanning the real range) |
| Appraisers / observers (n) | *3 QA analysts, the three who score billing contacts* (minimum 3) |
| Replicates | *3* (minimum 2, ideally 3) |
| Order randomized? | *Yes* |
| Appraisers blinded to prior measurement? | *Yes* |

*The study recorded the range of the 10 parts but never their mean, so the 412 s mean
handle time the pack carries elsewhere (16-pilot-protocol.md:94) cannot be checked against
anything measured here. Mean handle time of the sampled parts: `<not recorded>`. The Black
Belt who ran the study must state it before the 412 s is described as validated by this
gage.*

## 2. Results

| Source | Variance component | % Contribution | % Study variation |
|---|---|---|---|
| Total Gage R&R | *0.6973* | *8.1%* | *28.4% — marginal, investigate before use* |
| — Repeatability (equipment) | *0.1088* | *1.3%* | *11.2%* |
| — Reproducibility (appraiser) | *0.5886* | *6.8%* | *26.1% — the analysts disagree more than the tool does* |
| Part-to-part | *7.9407* | *91.9%* | *95.9%* |
| **Total variation** | *8.6380* | 100% | 100% |

| Measure | Value | Verdict |
|---|---|---|
| % Study variation | *28.4%* | <10% acceptable · 10–30% marginal · >30% unacceptable |
| Number of distinct categories (ndc) | *4* | want ≥ 5 |

*Read the split, not just the headline. Reproducibility is more than double repeatability,
so the gage is not the problem — the three analysts are applying the definition
differently. Buying a better timer would change nothing.*

## 3. Bias, linearity and stability

| Check | Method | Result | Acceptable? |
|---|---|---|---|
| Bias | Compare mean measurement to a reference value | *+0.8 min* | *Two analysts consistently round after-call work up* |
| Linearity | Bias across the operating range | *No trend across the range* | *—* |
| Stability | Repeat measurement of the same item over time | *Re-measured after 4 weeks, no drift* | *—* |

*Size the gage in seconds before any handle-time result is read off it. The Gage R&R
standard deviation is √0.6973 = 0.84 min, about 50 s, and that spread on a single reading
is what stands between this gage and a small handle-time change. The +0.8 min (about 48 s)
in the row above is not that spread: it is a mean offset produced by two of the three
analysts rounding after-call work up, not a uniform error on every reading — §2 puts
reproducibility (26.1%) at more than double repeatability (11.2%). The linearity and
stability rows say that offset holds across the range and over four weeks, so it largely
cancels out of a before/after difference taken on this same gage; the 50 s spread does not
cancel. What this study cannot do is police the pilot's handle-time guardrail — 412 s,
rising no more than 8% to 445 s (16-pilot-protocol.md:60) — because the pack nowhere
states which gage that 412 s is read off, and the measurement validated at the top of this
file is the analyst's clock, not the CRM timestamp. Which gage the 412 s comes from:
`<not stated in the pack>`; R. Okonjo, who owns the AHT scorecard
(01-project-charter.md:173), must state it before any pilot handle-time result is read
against this study. How much handle time the fix adds: `<not measured in this study>` —
the charter's "roughly 40 s" (01-project-charter.md:173) is an expectation set at Define,
not a measurement, and R. Okonjo must state the measured figure from the pilot. The Black
Belt must re-run this study once the three analysts are re-calibrated, before this gage is
used for any handle-time result.*

## 4. Verdict and action

- [ ] Acceptable
- [ ] Marginal — usable with stated caution
- [ ] Unacceptable — remediate before use

**Action:**
>

Study run by: ____________  Date: __________
