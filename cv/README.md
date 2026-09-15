# CV — built from the same data as the website

Both CV PDFs are generated from the `data/*.yml` files (the same ones that drive the website), so the CV and site never drift.

| File | Contents | Tracked in git? |
|---|---|---|
| `cv/cv.pdf` | Full CV, **including** confidential external tenure/promotion reviews | No — local only |
| `pdf/Bhamra-CV.pdf` | Public CV — identical minus that section. Linked from the website. | Yes |

## Rebuild

```bash
bash cv/build.sh        # regenerates both .tex files and compiles both PDFs
```

Requires a LaTeX install with `xelatex` (TeX Live / MacTeX) and Python 3 with `pyyaml`.

## How it works

- `build_cv.py` reads every file in `data/`, renders LaTeX, writes `cv.tex`. With `--public` it skips the confidential sections and writes `cv-public.tex` instead.
- `build.sh` runs both modes, compiles each with two `xelatex` passes, cleans up aux files, and moves the public PDF to `pdf/Bhamra-CV.pdf` so Quarto ships it with the site.
- Font: **Helvetica Neue** (macOS built-in); falls back to TeX Gyre Heros elsewhere.
- Accent color (navy `#1A3A5C`) matches the website.

## What's on the CV but NOT the website (by design)

- Full referee list, tenure/promotion case reviews, external examiner roles
- Year-of-birth, citizenship, languages, computer skills
- The complete Seminars & Conferences list (`data/seminars.yml`)
- Early-career scholarships and teaching-award nominations (`data/grants.yml` → `cv_only`)

## Updating content

Edit the relevant `data/*.yml` file, then rerun `bash cv/build.sh`. For example:

- New paper → `data/publications.yml`
- New seminar/conference presentation → `data/seminars.yml` (add under the year)
- New tenure/promotion review → `data/private/external_reviews.yml` (gitignored; full CV only)
