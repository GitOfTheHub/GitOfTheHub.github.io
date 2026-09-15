#!/usr/bin/env python3
"""
Ingest discussions from ~/Dropbox/.../02-Discussions/ into the webpage repo.

For each folder:
  - Copy the slide PDF to webpage/pdf/discussions/<slug>.pdf
  - Parse paper title + authors from the .tex source (best-effort)
  - Extract presentation date from filename

Output: rewrites data/discussions.yml in the canonical schema, then prints
a summary of any entries that need manual review (missing title, etc.).
"""
from __future__ import annotations
import re
import shutil
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = Path("/Users/hbhamra/Library/CloudStorage/Dropbox/20-MiscDocs-CV-RefReports-Discussions-Grants-References-etc/02-Discussions")
DST_PDF = ROOT / "pdf" / "discussions"
DST_YAML = ROOT / "data" / "discussions.yml"

TITLE_RE = re.compile(r"\\title\{((?:[^{}]|\{[^{}]*\})+)\}", re.DOTALL)
SUBTITLE_RE = re.compile(r"\\subtitle\{((?:[^{}]|\{[^{}]*\})+)\}", re.DOTALL)
DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
AUTHORS_PREFIX_RE = re.compile(r"^\s*(?:authors?|by|Authors?|By)\s*[: ]\s*", re.IGNORECASE)
DISCUSSION_PREFIX_RE = re.compile(r"^\s*discussion\s*(?:of|on|:)?\s*[:\-—]?\s*", re.IGNORECASE)
DISCUSSANT_SUFFIX_RE = re.compile(r"\s*\\?Discussant[\s:]*Harjoat[^,]*(?:,[^,]+)*$", re.IGNORECASE)
ALLCAPS_RE = re.compile(r"^[A-Z\s,&\-:'?!.]{20,}$")


def strip_latex(s: str) -> str:
    """Strip common LaTeX wrapping commands so the text is plain Unicode."""
    # \cmd{X} → X (one level, repeat)
    for _ in range(3):
        s = re.sub(r"\\(?:textbf|emph|small|large|Large|textit|texttt|textsc|textsf)\{([^{}]*)\}", r"\1", s)
    # Escapes
    s = s.replace("\\&", "&").replace("\\_", "_").replace("\\#", "#").replace("\\%", "%").replace("\\$", "$")
    s = s.replace("\\`{e}", "è").replace("\\'{e}", "é").replace("\\\"{e}", "ë")
    s = s.replace("\\`e", "è").replace("\\'e", "é").replace("\\\"e", "ë")
    s = s.replace("\\`{a}", "à").replace("\\'{a}", "á").replace("\\\"{a}", "ä")
    s = s.replace("\\`{o}", "ò").replace("\\'{o}", "ó").replace("\\\"{o}", "ö")
    s = s.replace("\\'{c}", "ć")
    s = s.replace("\\^{e}", "ê").replace("\\^{a}", "â").replace("\\^{o}", "ô").replace("\\^{i}", "î")
    # Line breaks
    s = re.sub(r"\\\\(?:\[\d+\w*\])?", " ", s)
    s = re.sub(r"\n+", " ", s)
    # Stray braces and command remnants
    s = re.sub(r"\{|\}", "", s)
    # Comments
    s = re.sub(r"%.*$", "", s, flags=re.MULTILINE)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_tex(tex_path: Path) -> tuple[str | None, list[str] | None]:
    """Return (paper_title, paper_authors) extracted from a .tex source."""
    try:
        txt = tex_path.read_text(errors="replace")
    except Exception:
        return None, None

    title = None
    authors_str = None

    if m := TITLE_RE.search(txt):
        title = strip_latex(m.group(1))
    if m := SUBTITLE_RE.search(txt):
        sub = strip_latex(m.group(1))
        sub = AUTHORS_PREFIX_RE.sub("", sub).strip()
        if sub:
            authors_str = sub

    # First: strip "Discussion:" / "Discussion of" prefix from title
    # (it refers to Bhamra's deck, not the paper)
    if title:
        title = DISCUSSION_PREFIX_RE.sub("", title).strip()

    # Strip "Discussant: Harjoat ..." suffix from titles (some old decks put it in \title)
    if title:
        title = DISCUSSANT_SUFFIX_RE.sub("", title).strip()

    # If title contains " by ", split into title + authors
    if title and " by " in title and not authors_str:
        idx = title.lower().rfind(" by ")
        cand_title = title[:idx].strip()
        cand_authors = title[idx + 4:].strip()
        # Sanity: authors should look like names (commas/and), not full sentence
        if len(cand_authors) < 200 and re.search(r"[A-Z][a-z]+", cand_authors):
            title = cand_title
            authors_str = cand_authors

    # If title is now empty or looks like just author names (commas, "&", "and"),
    # treat it as authors instead of title.
    if title and not authors_str:
        comma_count = title.count(",")
        and_count = len(re.findall(r"\s+(?:and|&)\s+", title))
        word_count = len(title.split())
        # Heuristic: short with commas and no verbs/articles → looks like an author list
        if word_count <= 12 and (comma_count + and_count) >= 1 and not re.search(r"\b(the|of|and|in|on|with|for|a|an|to|from|by)\b", title.lower().replace(" and ", " ").replace(" with ", " ").replace(" of ", " ")):
            # Probably just authors
            authors_str = title
            title = None

    # Normalize ALLCAPS titles to Title Case (some old decks used \MakeUppercase)
    if title and ALLCAPS_RE.match(title):
        title = title.title()
        # Re-capitalize 1-letter words and common acronyms after .title()
        title = re.sub(r"\bBkk\b", "BKK", title)

    # Strip trailing punctuation artifacts
    if title:
        title = title.rstrip(",;").strip()

    # Parse authors string into list
    authors = None
    if authors_str:
        # Normalize separators
        authors_str = re.sub(r"\s+&\s+", " and ", authors_str)
        authors_str = re.sub(r",\s+and\s+", ", ", authors_str)
        parts = re.split(r",\s*|\s+and\s+", authors_str)
        authors = [p.strip().rstrip(".,;") for p in parts if p.strip()]
        # Filter out obvious non-author tokens
        authors = [a for a in authors if len(a) > 1
                   and not a.lower().startswith(("the ", "and ", "discussion", "discussant"))
                   and "harjoat" not in a.lower()]
        # If a single "author" still has the form "X X. (some institution)", strip trailing parentheses
        authors = [re.sub(r"\s*\([^)]*\)\s*$", "", a).strip() for a in authors]
        # Drop empties after cleaning
        authors = [a for a in authors if a]
        if not authors:
            authors = None

    return title, authors


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[_\s]+", "-", s)
    s = re.sub(r"[^a-z0-9-]", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def find_slide_pdf(folder: Path) -> Path | None:
    candidates = list(folder.glob("*[Dd]iscussion*.pdf"))
    if not candidates:
        candidates = list(folder.glob("*.pdf"))
    if not candidates:
        return None
    # Prefer file containing "Discussion" in name; tiebreak by size (slides are usually 100KB+)
    candidates.sort(key=lambda p: (
        0 if "discussion" in p.name.lower() else 1,
        -p.stat().st_size,
    ))
    return candidates[0]


def find_tex(folder: Path) -> Path | None:
    candidates = [p for p in folder.glob("*.tex") if "Discussion" in p.name or "discussion" in p.name]
    if not candidates:
        candidates = list(folder.glob("*.tex"))
    if not candidates:
        return None
    candidates.sort(key=lambda p: (len(p.name), -p.stat().st_mtime))
    return candidates[0]


def extract_date(*names: str) -> str | None:
    for name in names:
        if not name:
            continue
        if m := DATE_RE.search(name):
            return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


def main() -> int:
    if not SRC.exists():
        sys.exit(f"Source not found: {SRC}")

    DST_PDF.mkdir(parents=True, exist_ok=True)

    discussions = []
    review_needed: list[str] = []

    for folder in sorted(p for p in SRC.iterdir() if p.is_dir()):
        slug = slugify(folder.name)
        pdf = find_slide_pdf(folder)
        tex = find_tex(folder)
        title, authors = parse_tex(tex) if tex else (None, None)
        date = extract_date(
            pdf.name if pdf else "",
            tex.name if tex else "",
            folder.name,
        )

        # Copy PDF into the repo (only if changed)
        pdf_rel = None
        if pdf:
            dst = DST_PDF / f"{slug}.pdf"
            if not dst.exists() or dst.stat().st_size != pdf.stat().st_size:
                shutil.copy2(pdf, dst)
            pdf_rel = str(dst.relative_to(ROOT))

        entry: dict = {
            "id": slug,
            "paper_title": title,
            "paper_authors": authors,
            "date": date,
        }
        if pdf_rel:
            entry["pdf"] = pdf_rel
        else:
            entry["pdf"] = None
            review_needed.append(f"{slug}: no PDF found in folder")

        # Flag missing fields for review
        if not title:
            review_needed.append(f"{slug}: missing paper_title (no .tex or unparseable)")
        if not authors:
            review_needed.append(f"{slug}: missing paper_authors (need manual fill)")
        if not date:
            review_needed.append(f"{slug}: missing date")

        discussions.append(entry)

    # Sort: most recent first (None dates last)
    discussions.sort(key=lambda d: d.get("date") or "0", reverse=True)

    # Preserve the CV-by-year summary block from existing yaml
    cv_by_year = {}
    if DST_YAML.exists():
        try:
            old = yaml.safe_load(DST_YAML.read_text())
            cv_by_year = (old or {}).get("cv_by_year", {})
        except Exception:
            pass

    out = {"discussions": discussions, "cv_by_year": cv_by_year}

    header = (
        "# Conference / seminar discussions. Rebuilt from\n"
        "# ~/Dropbox/.../02-Discussions/ folder by _scripts/ingest_discussions.py.\n"
        "# Edit data, not this file — re-run the ingest script after adding new folders.\n"
        "#\n"
        "# Schema:\n"
        "#   id              — slug derived from folder name\n"
        "#   paper_title     — title of the paper being discussed\n"
        "#   paper_authors   — list of original-paper authors\n"
        "#   date            — date of discussion (YYYY-MM-DD)\n"
        "#   pdf             — relative path to slides PDF inside the repo\n"
        "#\n"
        "# `null` fields need manual fill-in.\n\n"
    )

    DST_YAML.write_text(header + yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=200))

    print(f"Wrote {DST_YAML} with {len(discussions)} discussions.")
    print(f"PDFs in {DST_PDF}: {len(list(DST_PDF.glob('*.pdf')))}")
    if review_needed:
        print(f"\nReview needed ({len(review_needed)} items):")
        for line in review_needed:
            print(f"  - {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
