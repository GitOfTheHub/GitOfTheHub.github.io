#!/usr/bin/env python3
"""
Scan ~/Dropbox/20-MiscDocs.../02-Discussions/ and inventory each discussion folder.

Extracts from the .tex source where possible:
  - paper title (from \title{})
  - paper authors (from \subtitle{Authors: ...} if present)
  - presentation date (from .tex / .pdf filename like *-Discussion-YYYY-MM-DD.*)
  - slide PDF filename

Cross-references with existing data/discussions.yml to flag duplicates.
Emits a YAML proposal to stdout — user reviews before merging.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
import yaml

DISCUSSIONS_DIR = Path("/Users/hbhamra/Library/CloudStorage/Dropbox/20-MiscDocs-CV-RefReports-Discussions-Grants-References-etc/02-Discussions")
EXISTING_YAML = Path(__file__).resolve().parent.parent / "data" / "discussions.yml"

TITLE_RE = re.compile(r"\\title\{([^}]+(?:\}[^}]+)*?)\}", re.DOTALL)
SUBTITLE_RE = re.compile(r"\\subtitle\{([^}]+(?:\}[^}]+)*?)\}", re.DOTALL)
DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
AUTHORS_PREFIX_RE = re.compile(r"(?:authors?|by|Authors?:|By:)\s*[: ]\s*", re.IGNORECASE)


def clean_latex(s: str) -> str:
    """Strip simple LaTeX commands."""
    s = re.sub(r"\\textbf\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\emph\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\\\$", "", s)
    s = s.replace("\\&", "&").replace("\\_", "_").replace("\\#", "#")
    s = s.replace("\\\\", " ").replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_from_tex(tex_path: Path) -> dict:
    try:
        txt = tex_path.read_text(errors="replace")
    except Exception:
        return {}
    out = {}
    if m := TITLE_RE.search(txt):
        out["paper_title"] = clean_latex(m.group(1))
    if m := SUBTITLE_RE.search(txt):
        sub = clean_latex(m.group(1))
        sub = AUTHORS_PREFIX_RE.sub("", sub).strip()
        if sub:
            out["paper_authors_raw"] = sub
    return out


def extract_date(name: str) -> str | None:
    if m := DATE_RE.search(name):
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


def find_slide_pdf(folder: Path) -> Path | None:
    """Heuristic: prefer file matching *Discussion*.pdf, else any *.pdf."""
    candidates = list(folder.glob("*Discussion*.pdf"))
    if not candidates:
        candidates = list(folder.glob("*.pdf"))
    if not candidates:
        return None
    # If multiple, pick the most recently modified
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def find_tex(folder: Path) -> Path | None:
    candidates = list(folder.glob("*Discussion*.tex"))
    if not candidates:
        candidates = list(folder.glob("*.tex"))
    if not candidates:
        return None
    # Sort by name length (shorter names usually the main file, not _v2 etc.)
    candidates.sort(key=lambda p: (len(p.name), p.stat().st_mtime))
    return candidates[0]


def main():
    if not DISCUSSIONS_DIR.exists():
        sys.exit(f"Directory not found: {DISCUSSIONS_DIR}")

    existing = yaml.safe_load(EXISTING_YAML.read_text())
    existing_ids = {d["id"] for d in existing["discussions"]}

    inventory = []
    folders = sorted(p for p in DISCUSSIONS_DIR.iterdir() if p.is_dir())
    for folder in folders:
        slug = folder.name.lower().replace("_", "-")
        pdf = find_slide_pdf(folder)
        tex = find_tex(folder)
        meta = extract_from_tex(tex) if tex else {}
        date = extract_date(pdf.name if pdf else folder.name) or extract_date(tex.name if tex else "")
        entry = {
            "id": slug,
            "folder": folder.name,
            "paper_title": meta.get("paper_title"),
            "paper_authors_raw": meta.get("paper_authors_raw"),
            "date": date,
            "slide_pdf_path": str(pdf.relative_to(DISCUSSIONS_DIR.parent.parent)) if pdf else None,
            "in_existing_yaml": slug in existing_ids,
        }
        inventory.append(entry)

    new_count = sum(1 for i in inventory if not i["in_existing_yaml"])
    print(f"# Discovery: {len(inventory)} discussion folders found, {new_count} not yet in data/discussions.yml")
    print(f"# Existing entries in YAML: {len(existing_ids)}")
    print()
    print(yaml.safe_dump(inventory, sort_keys=False, allow_unicode=True, width=200))


if __name__ == "__main__":
    main()
