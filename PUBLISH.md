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

The workflow in `.github/workflows/pages.yml` has `enablement: true`, so the
first successful run turns Pages on by itself and publishes the `docs/` folder.

After pushing:

1. Open the **Actions** tab and watch the "Deploy to GitHub Pages" run.
2. When it goes green, the site is live at
   **https://maniwar.github.io/six-sigma-blackbelt-support-ops/**

If the run fails with a permissions error, set it manually once:
**Settings → Pages → Source: GitHub Actions**, then re-run the workflow from the
Actions tab. You may also need **Settings → Actions → General → Workflow
permissions → Read and write permissions**.

First deployments can take a couple of minutes to appear after the run goes
green. A 404 immediately afterwards usually just means DNS/CDN hasn't caught up.

## What's in here

| Path | What it is |
|---|---|
| `six-sigma-blackbelt-support-ops.html` | The whole program — one self-contained file, no dependencies |
| `docs/index.html` | Generated copy of the above, served by GitHub Pages |
| `templates/` | 19 project templates — 11 Markdown documents, 8 Excel workbooks |
| `tools/` | Build and test scripts for the templates (see below) |
| `README.md` | Repo front page |
| `LICENSE` | CC BY 4.0 |
| `.github/workflows/pages.yml` | Auto-enables and deploys Pages on every push to `main` |

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
