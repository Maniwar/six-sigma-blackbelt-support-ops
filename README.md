# Six Sigma Black Belt Program for Customer Support Operations

**A complete, deployable Lean Six Sigma Black Belt program — full ASQ/IASSC body of knowledge, taught entirely through the data a support organization actually generates.**

[**▶ Open the live program hub**](https://maniwar.github.io/six-sigma-blackbelt-support-ops/) &nbsp;·&nbsp; [Download the single HTML file](../../raw/main/six-sigma-blackbelt-support-ops.html)

![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-informational)
![Format: single-file HTML](https://img.shields.io/badge/Format-single--file%20HTML-success)
![BOK: ASQ CSSBB + IASSC](https://img.shields.io/badge/BOK-ASQ%20CSSBB%20%2B%20IASSC-blue)
![No dependencies](https://img.shields.io/badge/Dependencies-none-lightgrey)

---

## What this is

Most Black Belt training is written for a factory. Copy it into a contact center unchanged and it fails in predictable ways: the measurement system is human, almost no support data is normal, demand is exogenous, the definition of "defect" is contested, and improvements decay under attrition.

This is a full Black Belt program rebuilt around those five realities — without cutting any statistical rigor. It covers the complete ASQ CSSBB and IASSC Black Belt bodies of knowledge, including MSA, capability analysis, the full hypothesis-test set, regression and logistic regression, full and fractional factorial DOE, SPC, and DFSS. Every tool is introduced against a support problem: tickets, handle times, transfers, reopens, QA scores, CSAT.

It ships as **one self-contained HTML file** with no build step, no dependencies and no network calls. Open it in a browser, or host it anywhere that serves static files.

## What's inside

### Phase 1 — Curriculum
26 modules across four five-day waves, spaced four to five weeks apart with a live project and a tollgate between each.

| Wave | Focus | Modules |
|---|---|---|
| 1 | Define, deployment, team leadership | M01–M07 |
| 2 | Measure — data, MSA, capability, baseline | M08–M13 |
| 3 | Analyze — inference, hypothesis testing, regression | M14–M19 |
| 4 | Improve, Control, DFSS | M20–M26 |

Every module carries its BOK mapping, learning objectives, the support-specific application, an exercise, and the pitfall that module reliably produces. Certification requires a live project with Finance-validated benefit and 90 days of control data — not just an exam.

### Phase 2 — Participant toolkit
- **DMAIC field roadmap** — what you are actually doing in each phase, with tools and required outputs
- **Tool library — 52 tools, each one runnable.** Not a reference table: every tool has numbered steps for how to run it, the Minitab menu path, the Python/R equivalent, what output to read, the decision rule, and the support-specific trap.
- **Interactive statistical test selector** — six branches down to the exact test plus its caveat
- **Business case & ROI wizard** — seven guided steps from "something is wrong" to a costed business case, with every field explaining where the number comes from. The finished case opens on screen with four charts — benefit bridge, discounted benefit by year, cumulative position against breakeven, and NPV by scenario — and every arithmetic step printed as `input × input = result`. One button copies it formatted straight into an email; another saves it as a standalone page; a third downloads **an Excel workbook where every figure is a live formula and the charts are native Excel charts bound to the cells**. Finance can change any assumption and watch the whole case move.
- **A full worked project** — charter through 6-month re-audit, including the measurement-system finding that redirected it
- **33 templates you can actually download** — including **22 real Excel workbooks with live formulas**, data-validation dropdowns and conditional formatting. RPN, weighted scores, Process Cycle Efficiency, kappa, sigma level and ROI all calculate themselves. Every workbook has a "how to use this" tab, a worked example row, and a legend telling you which cells to fill in. Download offers a **format** rather than assuming one: Word for the documents you fill in and sign, a web page, or the Excel workbook itself. Every template also has an **Email version** — one click renders it as email-safe HTML you can paste into Outlook or Gmail with formatting intact, with each calculated cell showing its formula underneath the value.

### Every workbook produces a picture, not just a number

43 native Excel charts across the 22 workbooks — bound to the cells, so they move when you change an
assumption. A value stream map that shows touch time against waiting time step by step. An FMEA with RPN
before and after the action. Seven control chart types — I-MR, Laney p′, Laney u′, Xbar-R, EWMA, CUSUM and
t/g — each on its own tab with a picker that sends you to the right one, and every control limit written as
a live formula so the constants are visible rather than buried. A real Ishikawa diagram, spine and bones,
where each cause box reads the table so the picture redraws as you type.

**And you can see them without opening Excel.** Every chart is redrawn into the on-page preview as inline
SVG, from the same recalculated cells the table above it shows — combo series, reference lines, secondary
axes and all. Preview a template and you see what you are about to download.

`tools/qa_templates.py` audits all of it on every change: that each chart resolves to live cells, that each
input says where its number comes from, that each workbook recalculates without an error value — and it
renders every workbook through LibreOffice so the charts get looked at rather than assumed.

It audits the eleven **markdown** templates to the same standard, which it did not always do: every layer
globbed `*.xlsx`, so no check had ever opened a document. A column the worked example declares and then
leaves empty on every row fails, and so does a document that asks for a kappa, a p-value or a variance
component without saying anywhere how to get one.

Two further harnesses exist because the audit alone kept passing things a reader would not:

- **`tools/qa_properties.py`** perturbs the inputs. A workbook is a function, not the one example shipped
  inside it, and every axis, divisor and chart range has to survive somebody pasting numbers of a different
  magnitude.
- **`tools/qa_selftest.py`** reintroduces each defect the repo has actually shipped and asserts the audit
  still catches it. A check that has passed for months is either guarding a solved problem or unable to
  fire, and those look identical from a green run. 309 mutants, all killed, or the build fails.

### Built for people who are not statisticians
- **Every acronym is clickable.** 276 glossary entries, matched in either case. Anything with a dotted underline opens a plain-English explainer: what it means, why it matters, and exactly where to find the number in your own systems.
- **14 live formula cards.** Change any input and the arithmetic redoes itself line by line — you see the substitution, not just the answer. Each one ends with what the result actually means for your operation.
- **"Where does this number come from?" on every input** — the calculators, the wizard, the glossary, and every yellow cell in every workbook.

### The Black Belt Calculator Workbook

One of the thirty-three templates is a nine-tab Excel workbook: sigma level and DPMO, QA analyst agreement (kappa), SLA capability and breach rate, backlog and lead time, process cycle efficiency, staffing, two benefit models, and ROI / payback / NPV. Change the yellow cells; everything else recalculates, and each tab carries a chart — your DPMO against the sigma scale, your resolution-time distribution against the SLA limit, the cumulative discounted position crossing zero at payback. Every input carries a note naming the system that number lives in and the trap to watch for when you pull it.

### Phase 3 — Deployment
24-month rollout sequence, two-year investment and return model, the benefit accounting policy to agree with Finance before you start, project pipeline sources and a weighted selection matrix, governance forums and role definitions, ten program health KPIs, and a failure-mode register.

### Reference
A metric dictionary with the measurement trap attached to each metric, and a formula sheet covering defects and yield, capability, flow and queueing, MSA, control limits, sample size and benefit calculation.

---

## Three things this does differently

**1. Attribute Agreement Analysis gets a full day and is framed as the highest-value tool in the program.**
In support, the measurement system is human — a QA analyst scores a call, an agent picks a disposition code, a customer answers a survey. All three are subjective instruments with real repeatability and reproducibility error. Most support organizations have never validated theirs. First-pass kappa between QA analysts is routinely 0.35–0.60 where the org believed it was near 1.0. Everything downstream of an unvalidated measurement system is an opinion with decimal places.

**2. The Laney p′ chart is taught as the *default* attribute chart, not an advanced footnote.**
At n = 8,000 contacts per day, a standard p-chart's binomial limits around a 72% FCR are roughly ±1.5 points. Real daily FCR moves ±4 points from contact mix and staffing — none of it binomial noise. The result is a chart where most points are "out of control," the team stops looking at it, and SPC is discredited in the organization within a month. The Laney adjustment fixes this and almost no support-oriented curriculum mentions it.

**3. Every AHT benefit claim requires a named harvest mechanism.**
"We cut 12 seconds across 4M contacts, therefore we saved $X" is only true if the capacity is actually harvested. If schedules are unchanged, the saving becomes occupancy reduction — real for agents, invisible to the P&L. Charters here must state the harvest mechanism (headcount reduction, hiring avoidance, outsourcer renegotiation, or absorbed growth), signed by Finance and WFM.

---

## Using it

**As a program owner.** Start at Phase 3. Agree the benefit accounting policy with Finance and build the project pipeline *before* you book a classroom — training first and pipeline later is the most common sequencing error, and it produces a first-year benefit number that will not justify a second year.

**As an instructor.** Phase 1 is the syllabus. Each module has enough structure to build slides against, and the "common pitfall" notes are what to watch for in the room. The tollgate checklists are the scoring rubric.

**As a candidate.** Live in Phase 2 between waves. The test selector and calculators are meant to be used during real analysis, not read once.

**As an ops leader who is not running a program.** The metric dictionary, the translation table, and the "why support ops breaks textbook Six Sigma" section stand on their own.

## Customizing it

The file is plain HTML with an inline `<style>` block and one `<script>` at the bottom — no framework, and nothing to build to *use* it. To adapt it:

- **Benchmarks** — the figures cited (≈80% of calls answered in 20 seconds; FCR 70–75%; shrinkage 26–30%; occupancy ceilings in the mid-80s) are industry conventions, not standards. Replace them with your own measured values. A benchmark used as a target is how support organizations end up optimizing for someone else's business.
- **Certification thresholds** — the $150k benefit hurdle, 90-day control period and belt ratios are sized for a 500–2,000 FTE support organization. Scale them.
- **Colors** — edit the CSS custom properties in `:root` at the top of the file.
- **Opportunity count** — the DPMO examples assume 5 opportunities per contact. Fix this at program level for your org and never renegotiate it mid-project, or benefits become uncomparable across projects.

The Excel templates are the one exception: each workbook is embedded in the HTML as well as shipped in `templates/`, so it is generated rather than hand-edited. Formulas live in `tools/patch_workbooks.py`; `tools/sync_html.py` propagates them and `tools/verify.py` checks the copies agree. See [PUBLISH.md](PUBLISH.md).

## Body of knowledge coverage

Modules map to both certification tracks; the mapping is printed inside each module.

- **ASQ Certified Six Sigma Black Belt (CSSBB)** — nine sections covering organization-wide planning and deployment, organizational process management and measures, team management, Define, Measure, Analyze, Improve, Control, and Design for Six Sigma. Certification requires three years of on-the-job experience plus one completed project with a signed affidavit (or two projects with affidavits). The exam is 165 questions (150 scored), 4 hours 18 minutes, open book.
- **IASSC Lean Six Sigma Black Belt** — Define, Measure, Analyze, Improve and Control per the IASSC body of knowledge. Exam only, no project requirement — which is why this program requires a project regardless.

## Sources

- [ASQ — Certified Six Sigma Black Belt (CSSBB)](https://www.asq.org/cert/six-sigma-black-belt)
- [IASSC — Lean Six Sigma Black Belt Body of Knowledge](https://iassc.org/body-of-knowledge/black-belt-body-of-knowledge/)
- [PeopleCert — Lean Six Sigma Black Belt syllabus](https://www.peoplecert.org/-/media/folders-reorganized/pdfs/sylabus/lsspeoplecertbbsyllabusenv11.pdf)
- [ASQ — CSSBB Body of Knowledge map, 2015 to 2022](https://www.asq.org/cert/resource/pdf/certification/2022-SSBB-BoK-Map.pdf)
- [Call Centre Helper — industry standard contact centre metrics](https://www.callcentrehelper.com/industry-standards-metrics-125584.htm)

## License

[Creative Commons Attribution 4.0 International](LICENSE) — use it, adapt it, run it commercially, just credit the source.

---

<sub>Not affiliated with, endorsed by, or certified by ASQ or IASSC. "Six Sigma", "ASQ", "CSSBB" and "IASSC" are the marks of their respective owners; they are referenced here to describe body-of-knowledge coverage.</sub>
