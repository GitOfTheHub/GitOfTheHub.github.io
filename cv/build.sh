#!/bin/bash
# Build both CV PDFs from data/*.yml.
#
# Usage:  bash cv/build.sh
# Output:
#   cv/cv.pdf            full CV — includes confidential external tenure/promotion
#                        reviews from data/private/. Gitignored: local use only.
#   pdf/Bhamra-CV.pdf    public CV — identical minus those confidential sections.
#                        This is the file the website links to.

set -euo pipefail
cd "$(dirname "$0")"

compile () {  # compile <basename>
  xelatex -interaction=nonstopmode -halt-on-error "$1.tex" >/dev/null
  xelatex -interaction=nonstopmode -halt-on-error "$1.tex" >/dev/null
  rm -f "$1.aux" "$1.log" "$1.out" "$1.toc" "$1.synctex.gz"
}

echo "[1/4] Generating cv.tex (full) from data/..."
python3 build_cv.py

echo "[2/4] Compiling cv.pdf..."
compile cv

echo "[3/4] Generating cv-public.tex (no confidential sections)..."
python3 build_cv.py --public

echo "[4/4] Compiling public CV -> pdf/Bhamra-CV.pdf..."
compile cv-public
mkdir -p ../pdf
mv cv-public.pdf ../pdf/Bhamra-CV.pdf

echo "Done. cv/cv.pdf (private, full) and pdf/Bhamra-CV.pdf (public, linked from the site)."
