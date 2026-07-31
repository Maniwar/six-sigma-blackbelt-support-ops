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
| `templates/` | 19 project templates — 11 Markdown documents, 8 Excel workbooks |
| `tools/` | Build and test scripts for the templates (see below) |
| `README.md` | Repo front page |
| `LICENSE` | CC BY 4.0 |

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
python3 tools/verify.py            # 93 checks: structure, arithmetic, four-way sync
```

`patch_workbooks.py` is idempotent — running it twice changes nothing. Do not
edit formulas directly in Excel: the next `patch_workbooks.py` run will
overwrite them, and `verify.py` will fail in the meantime.

## If you edit the HTML by hand

Anything outside the embedded template data can be edited directly in
`six-sigma-blackbelt-support-ops.html`. Then regenerate the Pages copy:

```bash
python3 tools/sync_html.py && python3 tools/verify.py
```

`verify.py` exits non-zero if the two HTML files have drifted, so it is worth
running before every commit.
