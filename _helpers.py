"""Shared helpers used by Python chunks inside .qmd pages.

Reads data/*.yml and emits HTML/markdown snippets via stdout (Quarto's
`output: asis` mode), so each page stays declarative — no inline data.
"""

from __future__ import annotations
from pathlib import Path
import yaml

DATA_DIR = Path(__file__).resolve().parent / "data"


def load(name: str) -> dict | list:
    """Load data/<name>.yml. Caches per process (Quarto re-imports per chunk)."""
    with (DATA_DIR / f"{name}.yml").open() as f:
        return yaml.safe_load(f)


# ----------------------------------------------------------------------
# Author formatting
# ----------------------------------------------------------------------

def fmt_authors(authors: list[str], emphasize_self: bool = True) -> str:
    """Bhamra, A. and B. C. -> 'Bhamra, A., and B. C.' with Bhamra bolded."""
    fmt = []
    for a in authors:
        if emphasize_self and "Bhamra" in a:
            fmt.append(f"<b>{a}</b>")
        else:
            fmt.append(a)
    if len(fmt) == 1:
        return fmt[0]
    if len(fmt) == 2:
        return f"{fmt[0]} and {fmt[1]}"
    return ", ".join(fmt[:-1]) + ", and " + fmt[-1]


# ----------------------------------------------------------------------
# Citation formatting
# ----------------------------------------------------------------------

def fmt_journal(j: dict) -> str:
    """Render a journal citation block."""
    parts = [f"<em>{j['name']}</em>"]
    bits = []
    if j.get("volume") is not None:
        bits.append(str(j["volume"]))
    if j.get("issue") is not None:
        bits.append(f"({j['issue']})")
    if j.get("pages"):
        bits.append(j["pages"])
    if bits:
        parts.append(", ".join(bits) if len(bits) > 1 else bits[0])
    return ", ".join(parts)


def fmt_links(p: dict) -> str:
    """Render link row (Publisher · SSRN · PDF)."""
    out = []
    links = p.get("links", {}) or {}
    if links.get("publisher"):
        out.append(f'<a href="{links["publisher"]}">Publisher</a>')
    if links.get("ssrn"):
        out.append(f'<a href="{links["ssrn"]}">SSRN</a>')
    if links.get("pdf"):
        out.append(f'<a href="{links["pdf"]}">PDF</a>')
    if p.get("doi"):
        out.append(f'<a href="https://doi.org/{p["doi"]}">DOI</a>')
    return f'<div class="paper-links">{" · ".join(out)}</div>' if out else ""


def fmt_badges(p: dict) -> str:
    """Render award badges + status badges."""
    out = []
    for a in p.get("awards", []) or []:
        out.append(
            f'<span class="award-badge" title="{a.get("venue", "")} {a.get("year", "")}">'
            f'🏆 {a["name"]}, {a.get("venue", "")} {a.get("year", "")}</span>'
        )
    if p.get("status"):
        out.append(f'<span class="status-badge">{p["status"]}</span>')
    return "".join(out)


def render_paper(p: dict) -> str:
    """Render a single paper entry as one HTML block."""
    title = p["title"]
    authors = fmt_authors(p["authors"])
    badges = fmt_badges(p)
    meta_bits = []
    if "journal" in p:
        meta_bits.append(fmt_journal(p["journal"]))
        if p.get("year"):
            meta_bits.append(str(p["year"]))
    elif p.get("year"):
        meta_bits.append(str(p["year"]))
    if p.get("notes"):
        meta_bits.append(p["notes"])
    meta = ". ".join(meta_bits)
    links = fmt_links(p)
    return (
        f'<div class="paper-entry">'
        f'<div class="paper-title">{title}{badges}</div>'
        f'<div class="paper-meta">{authors}. {meta}.</div>'
        f'{links}'
        f'</div>'
    )


# ----------------------------------------------------------------------
# Discussions
# ----------------------------------------------------------------------

def render_discussion(d: dict) -> str:
    title = d.get("paper_title") or "<em style='color:#94a3b8'>[title to fill in]</em>"
    authors_list = d.get("paper_authors") or []
    authors = ", ".join(authors_list) if authors_list else ""
    date = d.get("date") or ""
    date_html = f' <span class="paper-meta">· {date}</span>' if date else ""
    links = []
    if d.get("pdf"):
        links.append(f'<a href="{d["pdf"]}">slides</a>')
    if d.get("video"):
        links.append(f'<a href="{d["video"]}">video</a>')
    links_html = " · ".join(links)
    return (
        f'<div class="paper-entry">'
        f'<div class="paper-title">{title}{date_html}</div>'
        f'<div class="paper-meta">{authors}</div>'
        f'<div class="paper-links">{links_html}</div>'
        f'</div>'
    )
