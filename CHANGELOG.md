# Changelog

Release notes for the program hub. These used to live inside the page itself, which meant every reader had to scroll past the maintenance history of a document they had only just opened. They belong here.

The live version is shown under the title on the page — check it against the top entry below to see whether you are looking at the current build.

## New in v3.0 — the templates produce something

- **Eight new workbooks, and a control-chart workbook that actually draws them.** The chart-selection table named seven chart types — I-MR, Laney p′, Laney u′, Xbar-R, EWMA, CUSUM, t/g — and nothing in the repo produced a single one. All seven now exist, one tab each, with a picker that sends you to the right one and every control limit written as a live formula so the constants (1.128, 2.66, 3.267, A2, D3, D4) are visible instead of buried. Also new: 5 Whys tree, cause-and-effect fishbone, stakeholder map and RACI, Kano analysis, DOE design matrix, Pareto and distribution, Kanban and WIP limits. **27 templates, 16 of them Excel workbooks.**
- **The original eight workbooks had no charts at all.** They computed the right answer and showed it as a column of numbers. There are now 32 charts across the 16 workbooks: touch time against waiting time per value-stream step, RPN before and after the action, p-values against alpha, controls by durability level, your DPMO against the sigma scale, your resolution-time distribution against the SLA limit, and the cumulative discounted position crossing zero at payback.
- **Tools no longer share a template that does not fit.** The Ishikawa diagram and the 5 Whys both linked to “Template: X-Y Matrix”, which is a scoring grid with no branches to fill and no chain to read back. Eleven tool links were retargeted and five tools that had no template at all now have one.
- **The Ishikawa is a fishbone again.** A table and a bar chart of counts is not an Ishikawa diagram. There is a real one now — spine, angled bones, the effect at the head — and every cause box is a formula reading the table, so you type in one place and the picture redraws.
- **Fixed: Kano was giving the opposite advice on the two most common answers.** Two cells of the published evaluation table were transposed, so Like/Dislike and Expect-it/Dislike returned each other's classification — “invest, more is better” on a table-stakes feature that earns nothing when present.
- **Fixed: the DOE effects chart drew nothing.** Its values are entirely negative and OOXML's `invertIfNegative` defaults on, so negative bars rendered blank while the axis scaled correctly beside them. Its factors were also labelled “@”, “A” and “B” against a design matrix with columns A, B and C.
- **Fixed: the 5 Whys asked four.** Its columns were “Why 1, Why 2, Why 3, Why 4 / 5”.
- **Worked examples you can learn from.** Every row-based template shipped one example row, so the value stream map's chart was a single bar and its Process Cycle Efficiency read 100% — the opposite of the lesson. One billing-dispute story now runs through six templates; the VSM lands at 26 minutes of touch time against 2,400 of waiting.
- **Release notes left the product.** Six of them sat between the contents and the first real section. They are in CHANGELOG.md now.
- **Fixed: explainers opened behind dialogs.** The glossary was at z-index 9999 and every modal is 10000 or above, so clicking a term inside a template preview hid the explanation behind it.
- **A quality audit that runs on every change.** `tools/qa_templates.py` checks that every chart resolves to live cells, every input says where its number comes from, and every workbook recalculates without an error value — then renders each one through LibreOffice so the charts can actually be looked at. That last layer found the defects no structural check could: axes crushing data into the top fifth of the plot, data labels reading “YOU; Column B; 50,667”, and a template grid collapsed into a single column.

## New in v2.9 — the jargon is actually explained

- **The glossary went from 97 entries to 253.** Six Sigma itself, Lean, non-parametric, transformation, ASQ, IASSC, QA, SOP, KPI, ROI, DOE, I-MR, rational subgrouping, Cohen’s and Fleiss’ kappa, USL and LSL, Poisson regression, negative binomial, overdispersion, deflection, swivel-chair work — all of it was used in the prose and none of it was defined.
- **The glossary never ran on anything rendered after page load.** Test-selector results, the wizard, template previews and the tool picker had *zero* links, so even defined terms were dead text there. Fixed — a template preview now carries 30–40 explainers.
- **Every one of the 28 statistical test results was a dead end.** Each named a test and linked to nothing. They now link to the tool that explains how to run it and the template you record it in.
- **Plurals resolve.** SLAs, CTQs, KPIs and SOPs used to match nothing at all.
- **Fixed: 21 terms were defined but never clickable.** A suppression list dating from the original build was hiding t-test, ANOVA, Chi-square, kappa, regression, Gemba, A3, tollgate, stratification and p90 from the prose entirely — they sat in the index and nowhere else. In a Six Sigma document none of those has an everyday meaning. **P&L** is now defined too, after appearing nine times without an explainer.
- **Fixed: the verb “push” was linking to the Lean pull system.** “Pull” and “Push” had been registered as synonyms, so ordinary sentences matched. Common verbs are no longer synonyms for anything.
- **Fixed: a stray capital *Z* was clickable.** “Z” had been added as a short name for Z-score, and a one-character alias matches every isolated capital letter in the page. Aliases shorter than two characters are now rejected outright.
- **The A–Z index is generated from the data** rather than hand-maintained, so it can never drift from the glossary again. 775 explainer links on the page, up from 388.

## In v2.6 — the tool library is navigable

- **“Not sure which tool you need?”** Two questions — where you are, and what you are actually trying to do — and you land on two or three tools. Every one of the 52 is reachable this way.
- **Thirteen tools now link to the calculator that runs them.** The kappa tool hands you a working kappa calculator; capability hands you Ppu and the breach rate; Laney, sample size, I-MR and Little's Law all do the same. Before this, a tool explained the arithmetic while a live calculator sat two sections away with nothing joining them.
- **Every tool has a link you can send.** Copy the link from any tool and it opens straight to it. Tools are grouped under DMAIC headings, badged with whether they come with a template, a calculator or Minitab steps, and there is an expand-all for reading or printing.
- **An A–Z index** of all 52, for when you already know the name and just want it. It jumps straight there and clears any filter that was hiding it.
- **The calculators link back.** Every one of the 14 live formula cards now names the tool that explains the method, so the link runs both ways rather than stranding you in the arithmetic.
- **The filters got out of the way.** Twenty-two category chips are now behind one control and can be combined, search highlights what it matched, and a dead-end filter offers a way back instead of a blank page. Press **/** to jump to search.

## In v2.4 — four more ways a support project makes money

- **Deflect to self-service or a cheaper channel.** The contact still happens, it just does not need a person. The benefit is the cost *difference*, never the whole contact cost — a distinction the old “eliminate a contact driver” model could not express.
- **Reduce agent attrition.** Recruiting, onboarding, training and the ramp you pay for twice. At 30–45% annual attrition this is often the largest number in a support P&L, and it is the only model here priced per person rather than per contact.
- **Cut the cost of poor quality.** Credits, refunds, goodwill and SLA penalties. Priced per incident, so a small defect-rate move can dwarf a big handle-time project — and the money is already in Finance's ledger, so you are not asking them to believe a model.
- **Protect revenue at risk.** The only revenue model rather than cost. Priced per customer, not per contact, because one customer raises several tickets — and the wizard now asks for customers so you cannot accidentally multiply the benefit by your contacts-per-customer ratio.

## In v2.3 — it now works everywhere, and from the keyboard

- **Fixed: the page did not work at all on Safari before 16.4** (and iOS before 16.4). The glossary used a regular-expression lookbehind, which those versions reject outright — and the failure took the formula cards, the wizard, the template previews and every download down with it. Rewritten to a form every browser understands.
- **The glossary works from the keyboard.** The 391 highlighted terms were reachable by Tab but could only be opened with a mouse, so keyboard and screen-reader users met 391 dead stops. Enter and Space now open them, Escape closes, and focus returns to where it was.
- **Both dialogs announce themselves** to screen readers, there is a skip-to-content link past the sidebar, a visible focus ring, and scripted scrolling now respects “reduce motion”.

## In v2.2 — every artifact is something you can actually send

- **The business case opens on screen** with a benefit bridge, discounted benefit by year, your cumulative position against breakeven, and NPV by scenario — and every arithmetic step printed out, so the number can be traced rather than taken on trust.
- **One button copies it into an email** with formatting intact. Another saves it as a web page.
- **Download it as Excel** and every figure is a live formula with native charts bound to the cells — change an assumption and the whole case moves. Finance can audit it, not just read it.
- **Every template downloads as Word or a web page** — Word for the documents you fill in and sign — and has an email version with each calculated cell showing its formula.
- **Corrected calculators.** The QA agreement verdict was reading chance agreement instead of kappa, and the SLA verdict was reading an empty cell — so it reported “not capable” for every input. Both are fixed, along with the value-stream, FMEA and ROI sheets.

## In v2.0 — built for people who are not statisticians

- **Every acronym is clickable.** Anything with a dotted underline opens a plain-English explainer: what it means, why it matters, and exactly where to get the number in your own systems.
- **52 tools with step-by-step instructions** — how to run each one, the Minitab menu path and the Python code, what output to read, and the decision rule.
- **14 live formula cards.** Change any number and the arithmetic redoes itself line by line.
- **A business case wizard** that walks you from “something is wrong” to a costed, downloadable case for Finance.
- **19 real templates** you can preview and download — including **8 Excel workbooks with live formulas**, dropdowns and conditional formatting. Not descriptions of templates.
