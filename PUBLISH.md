# How to publish this repo

Everything is committed already — the git history is in this folder. You just need to
create the remote and push.

## Option A — with the GitHub CLI (one command)

```bash
cd six-sigma-blackbelt-support-ops
gh repo create six-sigma-blackbelt-support-ops \
  --public --source=. --remote=origin --push \
  --description "A complete, deployable Lean Six Sigma Black Belt program for customer support operations."
```

## Option B — from the web

1. Create an empty repo at https://github.com/new named `six-sigma-blackbelt-support-ops`
   (no README, no .gitignore, no licence — this folder already has them).
2. Then:

```bash
cd six-sigma-blackbelt-support-ops
git remote add origin https://github.com/Maniwar/six-sigma-blackbelt-support-ops.git
git push -u origin main
```

## Turn on GitHub Pages

Settings → Pages → Source: **GitHub Actions**.

The workflow in `.github/workflows/pages.yml` publishes the `docs/` folder on every push
to `main`. Your live URL will be:

    https://maniwar.github.io/six-sigma-blackbelt-support-ops/

## What's in here

| Path | What it is |
|---|---|
| `six-sigma-blackbelt-support-ops.html` | The whole program — one self-contained file, no dependencies |
| `docs/index.html` | Same file, served by GitHub Pages |
| `templates/` | The 18 project templates as Markdown and CSV |
| `README.md` | Repo front page |
| `LICENSE` | CC BY 4.0 |
| `.github/workflows/pages.yml` | Auto-deploys Pages on push |

If you change the HTML, copy it to `docs/index.html` too — or add a build step.
