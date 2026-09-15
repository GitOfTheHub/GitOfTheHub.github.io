# harjoatbhamra.com — Quarto + GitHub Pages source

Source for [harjoatbhamra.com](https://harjoatbhamra.com). Built with [Quarto](https://quarto.org) from a set of YAML data files in `data/`. The same files also drive the LaTeX CV (when built; see `cv/`).

## Editing content

**Never edit `.qmd` files directly for content changes.** Edit the relevant file in `data/`:

| To change... | Edit |
|---|---|
| A paper title, author, journal, link | `data/publications.yml` |
| A discussion | `data/discussions.yml` |
| Bio paragraph, contact, profile links | `data/profile.yml` |
| Education entries | `data/education.yml` |
| Academic / industry employment | `data/employment.yml` |
| Research visits | `data/visits.yml` |
| Grants & fellowships | `data/grants.yml` |
| PhD students | `data/students.yml` |
| Service (AE roles, committees, keynotes) | `data/service.yml` |
| Teaching (current courses, past history) | `data/teaching.yml` |

Site pages (`.qmd` files) just render whatever is in `data/`. Layout/style changes belong in `styles.scss` or `_quarto.yml`.

## Local preview

Prereqs (one-time):

```bash
brew install quarto             # or download from quarto.org
pip3 install jupyter pyyaml     # required by Python chunks
```

Then in this directory:

```bash
quarto preview                  # live preview at http://localhost:4200
quarto render                   # build into _site/
```

## Deployment

GitHub Pages, from [`GitOfTheHub/GitOfTheHub.github.io`](https://github.com/GitOfTheHub/GitOfTheHub.github.io). Every push to `main` triggers `.github/workflows/publish.yml`, which installs Quarto + Jupyter, runs `quarto render`, and deploys `_site/` to Pages. Nothing is committed by the build — `_site/` stays gitignored.

Live at <https://gitofthehub.github.io> until the `harjoatbhamra.com` DNS is moved off Wix (see `DEPLOYMENT.md`).

## What is deliberately NOT in this repo

The repo is public, so two things are kept out of it and live only in this Dropbox folder:

- `data/private/external_reviews.yml` — confidential external tenure and promotion case reviews. `cv/build_cv.py` merges it in when building the *full* CV PDF.
- `cv/cv.pdf` and `cv/cv.tex` — the full CV, which contains that section. The public CV the site links to is `pdf/Bhamra-CV.pdf`, built by the same script with `--public` (identical minus the confidential section) and committed.

Also gitignored: the internal working notes (`migration-decisions.md`, `site-inventory.md`, `discussions-inventory.md`).

## Building the CV

```bash
bash cv/build.sh    # writes cv/cv.pdf (private, full) and pdf/Bhamra-CV.pdf (public)
```

Commit `pdf/Bhamra-CV.pdf` whenever CV content changes so the site's download link stays current.

## Migration notes

This site replaces the old Wix-built [harjoatbhamra.com](https://harjoatbhamra.com). See `migration-decisions.md` for the 16 content decisions made during migration (away from Wix). See `site-inventory.md` for the inventory of the old Wix content.
