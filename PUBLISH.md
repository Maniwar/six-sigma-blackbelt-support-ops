# Publishing and updating this repo

## Current state

The repo already exists at
**https://github.com/Maniwar/six-sigma-blackbelt-support-ops**
with the first two commits pushed.

This folder contains the full git history including one **newer commit** that is
not on GitHub yet — the Excel workbooks, the template rebuild, and the QA fixes.

## Push the new commit

The remote is already configured and your local history is a clean fast-forward,
so this is all it takes:

```bash
cd six-sigma-blackbelt-support-ops
git push
```

If git asks who you are, or the push is rejected as non-fast-forward, you are
probably in an older copy of the folder. Use this one instead — it is the
current state.

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
| `docs/index.html` | The same file, served by GitHub Pages |
| `templates/` | 19 project templates — 11 Markdown documents, 8 Excel workbooks |
| `README.md` | Repo front page |
| `LICENSE` | CC BY 4.0 |
| `.github/workflows/pages.yml` | Auto-enables and deploys Pages on every push to `main` |

## If you edit the HTML

`docs/index.html` is a copy, not a symlink. Update both:

```bash
cp six-sigma-blackbelt-support-ops.html docs/index.html
git add -A && git commit -m "Update program hub" && git push
```
