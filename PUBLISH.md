# Publishing and updating this repo

## Current state

The repo already exists at
**https://github.com/Maniwar/six-sigma-blackbelt-support-ops**
with the first two commits pushed.

This folder is the current state. It holds commits that are **not on GitHub
yet** — the Excel workbooks, the template rebuild, the Pages auto-enable
workflow, and the formula fixes. Check what is unpushed with:

```bash
git log --oneline origin/main..HEAD
```

## Push

The remote is already configured and your local history is a clean fast-forward:

```bash
git push
```

If the push is rejected as non-fast-forward, you are probably in an older copy
of the folder. Use this one.

## GitHub Pages

Pages is configured as **Settings → Pages → Source: Deploy from a branch →
`main` / `/docs`**. Every push to `main` rebuilds the site automatically; there
is no workflow to watch and nothing to enable.

The site is live at
**https://maniwar.github.io/six-sigma-blackbelt-support-ops/**

The folder must stay `/docs`, not `/` — the repo root has no `index.html`, so a
root-published site serves a Jekyll-rendered README instead of the program.

Two things worth knowing:

- Only `docs/` is published. `templates/` is not reachable over HTTP, which does
  not matter: the page carries every template inside itself as base64 and makes
  no network calls. Template downloads work offline, from a file:// URL, and
  from any host.
- There is deliberately **no** Actions workflow. "Deploy from a branch" and
  "GitHub Actions" are mutually exclusive Pages sources; running both means one
  fails on every push. If you ever switch the source back to GitHub Actions, you
  will need to restore a deploy workflow that publishes `docs/`.

A build takes about a minute. A 404 straight afterwards usually just means the
CDN has not caught up yet.

## What's in here

| Path | What it is |
|---|---|
| `six-sigma-blackbelt-support-ops.html` | The whole program — one self-contained file, no dependencies |
| `docs/index.html` | Generated copy of the above, served by GitHub Pages |
| `templates/` | 33 project templates — 11 Markdown documents, 22 Excel workbooks |
| `tools/` | Build and test scripts for the templates (see below) |
| `README.md` | Repo front page |
| `LICENSE` | CC BY 4.0 |

## The generated business case

The wizard's final step builds a business case three ways from one model:
email-safe HTML (inline styles only, so it survives Outlook and Gmail), a
standalone `.html` file, and an `.xlsx` where every figure is a live formula
pointing at an Inputs sheet, with four native Excel charts bound to those cells.

The workbook is written in the browser by a small OOXML/ZIP writer near the
bottom of the `<script>` block — no library, no network call. Two things about
it are load-bearing:

- Charts are **inline-styled HTML tables**, not SVG, in the HTML rendering.
  Gmail and Outlook strip `<svg>`, which would defeat the point of a business
  case you can paste into an email.
- `workbook.xml` sets `fullCalcOnLoad="1"`. The writer cannot compute cached
  results, so Excel is told to recalculate everything the moment it opens.
  Remove that and every cell shows as blank until the user presses F9.

`tools/verify.py` extracts that JavaScript from the shipped HTML, runs it under
node for every problem archetype the wizard offers, and recalculates each
workbook to confirm it produces the same numbers the page displayed. The wizard
ships ten; three of them share a benefit shape, so the harness runs eight
distinct kinds. Both numbers are derived by the check rather than written here,
because this paragraph said "four" for long enough that nobody noticed. If you change the benefit
model, that test is what tells you whether the Excel still agrees with the
screen.

## Editing templates or formulas

Every workbook exists in **four** places: `templates/*.xlsx`, the base64 blob
embedded in the HTML, the preview table's formula tooltips, and
`docs/index.html`. Only the first is edited by hand — the rest are generated.
Keeping them in step by hand is what let a broken formula ship once already.

Formulas live in `tools/patch_workbooks.py`, which is the single source of truth
for every calculated cell. To change one:

```bash
python3 -m pip install openpyxl formulas
python3 tools/patch_workbooks.py   # apply the canonical formulas to templates/*.xlsx
python3 tools/sync_html.py         # re-embed workbooks, tooltips and docs/index.html
python3 tools/verify.py            # structure, arithmetic, four-way sync
```

`patch_workbooks.py` is idempotent — running it twice changes nothing. Do not
edit formulas directly in Excel: the next `patch_workbooks.py` run will
overwrite them, and `verify.py` will fail in the meantime.

`verify.py` is the largest gate but not the only one. Before you push, run all
of them; each reads something the others do not, and a green `verify` says
nothing about what the reader actually opens:

```bash
python3 tools/verify.py          # structure, arithmetic, four-way sync
python3 tools/qa_templates.py    # workbook structure, examples, chart rubric
python3 tools/qa_properties.py   # inputs actually move the outputs
python3 tools/qa_citations.py    # every cross-reference resolves to its figure
python3 tools/qa_visual.py       # drives the real page in a headless browser
python3 tools/qa_wordtables.py   # reads the produced .docx, not the source
python3 tools/qa_selftest.py     # mutation-tests the checks themselves
```

A run that skips a layer says so and fails; one you asked to skip (`--fast`,
`--skip-browser`, `--skip-optional`) exits clean but prints NOT RUN and never
counts the missing checks as passes.

## Correcting a claim that appears more than once

Read this before changing any figure or any sentence that states a rule.

Almost every defect this pack has had was one rule stated in several places and
corrected in some of them: acceptance bands wrong in seven places, a benefit
chain in three, a sampling bias in four. Twice a fix was reported complete while
a copy survived somewhere nobody had looked.

So when you correct a claim, **grep the whole pack for the old wording first** —
the page, `templates/*.md`, and the workbooks, whose prose lives in cell values
and cell comments and will not turn up in a plain grep. Then record it:

* the old wording goes in `RETIRED` in `tools/retired.py`, with why it is wrong
  and what replaced it;
* if the figure appears in more than one place, the new value goes in
  `CANONICAL` with a pattern that identifies a statement of that fact.

`verify.py` then refuses the old wording anywhere in any artefact, and requires
every statement of the fact to carry the same value. This is the step that turns
"I fixed it everywhere" from something you believe into something the build
checks. It is not optional bookkeeping: it is the fix.

## If you edit the HTML by hand

Anything outside the embedded template data can be edited directly in
`six-sigma-blackbelt-support-ops.html`. Then regenerate the Pages copy:

```bash
python3 tools/sync_html.py && python3 tools/verify.py
```

`verify.py` exits non-zero if the two HTML files have drifted, so it is worth
running before every commit.
