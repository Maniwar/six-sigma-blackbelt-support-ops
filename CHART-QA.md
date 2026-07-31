# The chart quality bar

A chart in these workbooks has to clear a higher bar than "it plots the data".
Anyone can select two columns and press the chart button in ten seconds. If that
is all a template offers, the template is not worth downloading.

So every chart is held to six dimensions. Three are gates — fail one and the
chart does not ship. Three are scored, and the shipping bar is near the top of
each. `tools/chart_rubric.py` enforces all of it; `python3 tools/qa_templates.py
--rubric` prints the scorecard.

---

## Gate 1 — CORRECT

The chart plots what it claims to.

- Every series resolves to a real sheet and a real range.
- No series reads a merged-shadow cell, which is always empty.
- Categories and values are the same length, or Excel silently drops the overhang.
- The workbook recalculates with no error value anywhere.
- Negative values actually render (`invertIfNegative` explicitly off).

## Gate 2 — RIGHT CHART

The form matches the question. A ranked comparison drawn as a line chart implies
a trend through categories that have no order, and that is a lie about the data.

| The question | The form |
|---|---|
| Is this stable over time? | Line, with the limits as flat reference series |
| Which of these is biggest? | Bar |
| How do a few named quantities compare? | Bar, one per quantity |
| Where did the time go, step by step? | Stacked bar |
| Did it change, before against after? | Clustered bar, two series |
| How do two variables relate across entities? | Scatter |
| When does this cross a threshold? | Line, with the threshold as a series |
| What shape is this data? | Line or bar over bins |

## Gate 3 — READABLE

- A title that states the conclusion or asks the question. "Sales by month" is a
  caption; "Individuals — is the process stable?" tells you what to do with it.
- Both axes visible. openpyxl hides them unless told otherwise.
- Axis bounds frame the data. Values between 396 and 442 on a 0–500 axis put
  every point in the top fifth and hide the variation you came to see.
- Category labels thinned to what fits — 24 labels on a 15cm axis is a smear.
- Data labels show the value only, never "YOU; Column B; 50,667".
- A legend when there is more than one series, and none when there is one.
- Every series has an explicit colour, and the colours mean the same thing
  everywhere: red is a limit or a breach, green is a target or the good case,
  amber is you, blue is the data.

---

## Scored: WORTH IT — 0 to 4, ship at 3

The honest test: **would you rather use this than spend two minutes making your
own?** A bar chart of a column you already have is worth nothing. Points for:

- **+1 A reference the user would not have added.** Control limits, a spec
  limit, the 80% line, breakeven, the sigma scale, alpha. This is most of the
  value: the chart brings the standard to the data.
- **+1 Live, not pasted.** Every series bound to cells, so changing an
  assumption moves the picture.
- **+1 A decision encoded visually.** A threshold that splits acceptable from
  not, or per-point colour that marks which bar is you.
- **+1 It answers its own title.** No further arithmetic between looking at it
  and knowing what to do.

## Scored: EXAMPLE — 0 to 3, ship at 3

A chart with one bar teaches nothing and looks broken.

- **+1 Enough plotted points** — five or more, or every category filled when
  there are fewer.
- **+1 No holes.** An empty cell inside the plotted range leaves a gap or, worse,
  drags a cumulative line flat across the rest of the chart.
- **+1 The example shows the lesson.** Three or more distinct values, so the
  shape is visible. A value stream map whose Process Cycle Efficiency reads 100%
  is demonstrating the opposite of the point.

## Scored: GUIDANCE — 0 to 2, ship at 2

- **+1 Every input feeding the chart says where its number comes from** — in its
  column header for a table, or its own note for a standalone cell.
- **+1 The sheet says what to look at.** A line near the chart naming the signal,
  not just the metric.

---

## The shipping bar

    Gates 1–3        all pass
    WORTH IT         >= 3 / 4
    EXAMPLE          == 3 / 3
    GUIDANCE         == 2 / 2

Anything below that is a finding, not a preference.
