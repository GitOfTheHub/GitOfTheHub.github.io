#!/usr/bin/env python3
"""
Build cv.tex from the same YAML data files the website reads.

Usage:
    python3 cv/build_cv.py            # writes cv/cv.tex (full, private — local only)
    python3 cv/build_cv.py --public   # writes cv/cv-public.tex (no confidential sections)
    bash cv/build.sh                  # writes and compiles BOTH PDFs

Design: clean modern CV. Source Sans 3 body (matches website), thin section
rules in navy. Single column. Date-left, content-right entries.
"""
from __future__ import annotations
from pathlib import Path
from datetime import date
import sys
import yaml
import re

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent / "cv.tex"
OUT_PUBLIC = Path(__file__).resolve().parent / "cv-public.tex"


# ---- LaTeX escaping -------------------------------------------------------

LATEX_REPLACEMENTS = [
    ("\\", r"\textbackslash{}"),
    ("&", r"\&"),
    ("%", r"\%"),
    ("$", r"\$"),
    ("#", r"\#"),
    ("_", r"\_"),
    ("{", r"\{"),
    ("}", r"\}"),
    ("~", r"\textasciitilde{}"),
    ("^", r"\textasciicircum{}"),
]


def tex_escape(s) -> str:
    if s is None:
        return ""
    s = str(s)
    out = []
    i = 0
    while i < len(s):
        for orig, repl in LATEX_REPLACEMENTS:
            if s.startswith(orig, i):
                out.append(repl)
                i += len(orig)
                break
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def t(s) -> str:
    """Shorthand for tex_escape used inside f-strings."""
    return tex_escape(s)


# ---- Data loading ---------------------------------------------------------

def load(name: str):
    return yaml.safe_load((DATA / f"{name}.yml").read_text())


def load_private(name: str):
    """Load data/private/<name>.yml if present. Private files are gitignored and
    hold confidential material (external tenure/promotion reviews) that appears
    only in the printable CV PDF, never on the website or in the repo."""
    f = DATA / "private" / f"{name}.yml"
    return yaml.safe_load(f.read_text()) if f.exists() else {}


def all_data(public: bool = False):
    d = {n: load(n) for n in [
        "profile", "education", "employment", "publications",
        "discussions", "visits", "grants", "service", "students", "teaching",
        "seminars",
    ]}
    # Confidential external reviews live outside the repo; merge them in when present.
    # The public PDF (shipped with the website) never includes them.
    if not public:
        d["service"].update(load_private("external_reviews"))
    return d


# ---- Formatters -----------------------------------------------------------

def fmt_authors(authors: list[str]) -> str:
    """Citation-style author list, bolding Bhamra."""
    if not authors:
        return ""
    out = []
    for a in authors:
        a_esc = tex_escape(a)
        if "Bhamra" in a:
            out.append(rf"\textbf{{{a_esc}}}")
        else:
            out.append(a_esc)
    if len(out) == 1:
        return out[0]
    if len(out) == 2:
        return f"{out[0]} and {out[1]}"
    return ", ".join(out[:-1]) + ", and " + out[-1]


def fmt_journal_citation(p: dict) -> str:
    """Compact published-paper citation block."""
    j = p["journal"]
    parts = [rf"\emph{{{tex_escape(j['name'])}}}"]
    vol = j.get("volume")
    iss = j.get("issue")
    pages = j.get("pages")
    if vol is not None:
        bit = str(vol)
        if iss is not None:
            bit += f"({iss})"
        if pages:
            bit += f", {pages}"
        parts.append(bit)
    return ", ".join(parts)


def fmt_paper_published(p: dict) -> str:
    authors = fmt_authors(p["authors"])
    title = tex_escape(p["title"])
    cite = fmt_journal_citation(p)
    year = p["year"]
    notes = []
    if p.get("notes"):
        notes.append(tex_escape(p["notes"]))
    for a in p.get("awards") or []:
        nm = tex_escape(a["name"])
        ven = tex_escape(a.get("venue", ""))
        yr = a.get("year", "")
        notes.append(f"Winner — {nm}, {ven} {yr}".strip())
    extras = ""
    if notes:
        extras = " " + " ".join(rf"\hfill\textit{{({n})}}" for n in notes[:1])
        if len(notes) > 1:
            # multiple notes -> trail after period
            extras = " \\textit{(" + "; ".join(notes) + ")}"
    return f"{authors}, {year}, \\enquote{{{title},}} {cite}.{extras}"


def fmt_paper_unpublished(p: dict, status_label: str | None = None) -> str:
    authors = fmt_authors(p["authors"])
    title = tex_escape(p["title"])
    year = p["year"]
    bits = [f"{authors}, {year}, \\enquote{{{title}.}}"]
    if status_label:
        bits.append(rf" (\textit{{{tex_escape(status_label)}}})")
    if p.get("status") and not status_label:
        bits.append(rf" (\textit{{{tex_escape(p['status'])}}})")
    for a in p.get("awards") or []:
        nm = tex_escape(a["name"])
        ven = tex_escape(a.get("venue", ""))
        yr = a.get("year", "")
        bits.append(rf" \textit{{[Winner — {nm}, {ven} {yr}]}}")
    presentations = p.get("presentations") or []
    if presentations:
        venue_list = "; ".join(
            f"{tex_escape(pr['venue'])} {pr.get('year', '')}".strip()
            for pr in presentations
        )
        bits.append(rf" \textit{{[Presented at: {venue_list}]}}")
    if p.get("funding"):
        bits.append(rf" \textit{{[Funded: {tex_escape(p['funding'])}]}}")
    return "".join(bits)


# ---- Sections -------------------------------------------------------------

def section_header(profile: dict, today: str) -> str:
    p = profile
    full = tex_escape(p["name"]["full"])
    title = tex_escape(p["title"])
    aff = tex_escape(p["affiliation"]["long"])
    addr = tex_escape(p["contact"]["address"].strip()).replace("\n", r" \\ ")
    email = tex_escape(p["contact"]["email"])
    phone = tex_escape(p["contact"]["phone"])
    fellowships = "; ".join(
        f"{tex_escape(f['name'])} ({tex_escape(f['organization'])})"
        if f.get("organization") else tex_escape(f["name"])
        for f in (p.get("fellowships") or [])
    )

    return rf"""
\begin{{flushleft}}
{{\Huge\bfseries {full}}}\\[0.4em]
{{\large {title}, {aff}}}\\[0.4em]
{addr}\\[0.2em]
{{\small Email: \href{{mailto:{email}}}{{\texttt{{{email}}}}} \quad Phone: {phone}}}\\[0.2em]
{{\small {fellowships}.}}
\end{{flushleft}}

\hfill {{\footnotesize Last updated: {today}}}
\vspace{{0.5em}}
"""


def section_academic_employment(emp) -> str:
    out = [section_title("Academic Employment")]
    out.append(r"\begin{cvlist}")
    for j in emp["academic"]:
        end = j["end"] or "present"
        yrs = f"{j['start']}--{end}"
        title = tex_escape(j["title"])
        inst = tex_escape(j["institution"])
        loc = tex_escape(j["location"])
        out.append(rf"  \cventry{{{yrs}}}{{{title}, {inst}, {loc}.}}")
    out.append(r"\end{cvlist}")
    return "\n".join(out)


def section_education(edu) -> str:
    out = [section_title("Education")]
    out.append(r"\begin{cvlist}")
    for e in edu:
        yrs = tex_escape(e["years"])
        line = rf"{tex_escape(e['degree'])}"
        if e.get("field"):
            line += rf", {tex_escape(e['field'])}"
        line += rf", {tex_escape(e['institution'])}, {tex_escape(e.get('location', ''))}."
        if e.get("thesis"):
            th = e["thesis"]
            line += rf" Thesis: \emph{{{tex_escape(th['title'])}}}."
            if th.get("committee"):
                line += " Committee: " + ", ".join(tex_escape(c) for c in th["committee"]) + "."
        out.append(rf"  \cventry{{{yrs}}}{{{line}}}")
    out.append(r"\end{cvlist}")
    return "\n".join(out)


def section_publications(pubs) -> str:
    out = [section_title("Research")]

    for sec_key, sec_title, formatter in [
        ("published", "Published Papers", lambda p: fmt_paper_published(p)),
        ("under_review", "Under Review", lambda p: fmt_paper_unpublished(p)),
        ("working", "Completed Working Papers", lambda p: fmt_paper_unpublished(p)),
        ("in_progress", "Work in Progress", lambda p: fmt_paper_unpublished(p)),
    ]:
        items = pubs.get(sec_key, []) or []
        if not items:
            continue
        out.append(rf"\subsection*{{{sec_title}}}")
        out.append(r"\begin{enumerate}[leftmargin=*, itemsep=0.4em]")
        for p in items:
            out.append(rf"  \item {formatter(p)}")
        out.append(r"\end{enumerate}")
    return "\n".join(out)


def section_seminars(sem) -> str:
    by_year = sem.get("by_year") or {}
    if not by_year:
        return ""
    out = [section_title("Seminars and Conferences (by Academic Year)")]
    out.append(r"\begin{cvlist}")
    for year in sorted(by_year.keys(), reverse=True):
        venues = ", ".join(tex_escape(v) for v in by_year[year])
        out.append(rf"  \cventry{{{year}}}{{{venues}.}}")
    out.append(r"\end{cvlist}")
    return "\n".join(out)


def section_discussions(disc) -> str:
    cv_by_year = disc.get("cv_by_year") or {}
    if not cv_by_year:
        return ""
    out = [section_title("Conference Discussions")]
    out.append(r"\begin{cvlist}")
    for year in sorted(cv_by_year.keys(), reverse=True):
        venues = ", ".join(tex_escape(v) for v in cv_by_year[year])
        out.append(rf"  \cventry{{{year}}}{{{venues}.}}")
    out.append(r"\end{cvlist}")
    return "\n".join(out)


def section_service(s) -> str:
    out = [section_title("Service")]

    if s.get("editorial"):
        out.append(r"\subsection*{Editorial Work}")
        out.append(r"\begin{cvlist}")
        for e in s["editorial"]:
            yrs = f"{e['start']}--{e['end']}"
            out.append(rf"  \cventry{{{yrs}}}{{{tex_escape(e['role'])} for \emph{{{tex_escape(e['journal'])}}}.}}")
        out.append(r"\end{cvlist}")

    if s.get("program_committees"):
        out.append(r"\subsection*{Program Committees \& Reviewing}")
        out.append(r"\begin{itemize}[leftmargin=*, itemsep=0.1em]")
        for c in s["program_committees"]:
            line = tex_escape(c["committee"])
            if c.get("role"):
                line += f" — {tex_escape(c['role'])}"
            if c.get("note"):
                line += f" ({tex_escape(c['note'])})"
            elif c.get("start"):
                end = c.get("end") or "present"
                line += f", {c['start']}--{end}"
            out.append(rf"  \item {line}")
        out.append(r"\end{itemize}")

    if s.get("peer_review"):
        out.append(r"\subsection*{Peer Review Panels}")
        out.append(r"\begin{cvlist}")
        for r in s["peer_review"]:
            yrs = str(r["year"]) if r.get("year") else f"{r['start']}--{r.get('end') or 'present'}"
            out.append(rf"  \cventry{{{yrs}}}{{{tex_escape(r['name'])}.}}")
        out.append(r"\end{cvlist}")

    if s.get("external_reviews"):
        out.append(r"\subsection*{External Reviews — Tenure and Promotion Cases}")
        out.append(r"\begin{cvlist}")
        for r in s["external_reviews"]:
            yr = str(r.get("year") or "n.d.")
            kind = "Tenure" if r.get("type") == "tenure" else f"Promotion to {tex_escape(r.get('to_rank', '?'))}"
            line = rf"{tex_escape(r['candidate'])}, {tex_escape(r['institution'])} — {kind}."
            out.append(rf"  \cventry{{{yr}}}{{{line}}}")
        out.append(r"\end{cvlist}")

    if s.get("keynotes"):
        out.append(r"\subsection*{Keynote Speeches}")
        out.append(r"\begin{cvlist}")
        for k in s["keynotes"]:
            out.append(rf"  \cventry{{{k['date']}}}{{\emph{{{tex_escape(k['title'])}}} — {tex_escape(k['venue'])}.}}")
        out.append(r"\end{cvlist}")

    if s.get("referee_for"):
        out.append(r"\subsection*{Refereeing}")
        refs = ", ".join(tex_escape(r) for r in s["referee_for"])
        out.append(rf"Referee for: {refs}.")

    return "\n".join(out)


def section_teaching(t) -> str:
    out = [section_title("Teaching Experience")]
    out.append(r"\subsection*{Imperial College Business School — Current (" + tex_escape(t["current_year"]) + ")}")
    out.append(r"\begin{cvlist}")
    for c in t["current"]:
        out.append(rf"  \cventry{{{tex_escape(t['current_year'])}}}{{Lecturer, {tex_escape(c['course'])} ({tex_escape(c['program'])}).}}")
    out.append(r"\end{cvlist}")

    if t.get("past_imperial"):
        out.append(r"\subsection*{Imperial College Business School — Past}")
        out.append(r"\begin{cvlist}")
        for c in t["past_imperial"]:
            out.append(rf"  \cventry{{{tex_escape(c['year'])}}}{{Lecturer, {tex_escape(c['course'])} ({tex_escape(c['program'])}).}}")
        out.append(r"\end{cvlist}")

    if t.get("past_other"):
        out.append(r"\subsection*{Other Institutions}")
        out.append(r"\begin{cvlist}")
        for c in t["past_other"]:
            when = c.get("year") or c.get("years")
            role = tex_escape(c.get('role', 'Lecturer'))
            line = rf"{role}, {tex_escape(c['course'])} ({tex_escape(c['program'])}), {tex_escape(c['institution'])}."
            out.append(rf"  \cventry{{{tex_escape(when)}}}{{{line}}}")
        out.append(r"\end{cvlist}")
    return "\n".join(out)


def section_students(st) -> str:
    out = [section_title("PhD Students")]

    out.append(r"\subsection*{Main Advisor — Current}")
    out.append(r"\begin{cvlist}")
    for s in st["current_advisees"]:
        out.append(rf"  \cventry{{{s['start']}--}}{{{tex_escape(s['name'])}, {tex_escape(s['institution'])} ({tex_escape(s['field'])}).}}")
    out.append(r"\end{cvlist}")

    if st.get("past_advisees"):
        out.append(r"\subsection*{Main Advisor — Past}")
        out.append(r"\begin{cvlist}")
        for s in st["past_advisees"]:
            when = s.get("graduated") or s.get("years")
            line = rf"{tex_escape(s['name'])}, {tex_escape(s['institution'])} ({tex_escape(s['field'])})."
            if s.get("placement"):
                line += rf" {tex_escape(s['placement'])}."
            out.append(rf"  \cventry{{{tex_escape(str(when))}}}{{{line}}}")
        out.append(r"\end{cvlist}")

    if st.get("notable_committee_roles"):
        out.append(r"\subsection*{Committee Roles}")
        out.append(r"\begin{cvlist}")
        for s in st["notable_committee_roles"]:
            line = rf"{tex_escape(s['name'])}, {tex_escape(s['institution'])} ({tex_escape(s['field'])}) — {tex_escape(s.get('role', ''))}."
            if s.get("placement"):
                line += f" {tex_escape(s['placement'])}."
            out.append(rf"  \cventry{{{tex_escape(str(s.get('graduated', '')))}}}{{{line}}}")
        out.append(r"\end{cvlist}")

    if st.get("cv_only_examiner_roles"):
        out.append(r"\subsection*{External Examiner / Reviewer}")
        out.append(r"\begin{cvlist}")
        for r in st["cv_only_examiner_roles"]:
            line = rf"{tex_escape(r['role'])}, {tex_escape(r['candidate'])}, {tex_escape(r['institution'])}."
            out.append(rf"  \cventry{{{r['year']}}}{{{line}}}")
        out.append(r"\end{cvlist}")
    return "\n".join(out)


def section_grants(g) -> str:
    out = [section_title("Awards, Grants, and Fellowships")]
    for sec_key, sec_title in [("shown_on_website", "Current Fellowships and Grants"),
                                ("cv_only", "Other Awards, Grants, Scholarships")]:
        items = g.get(sec_key) or []
        if not items:
            continue
        out.append(rf"\subsection*{{{sec_title}}}")
        out.append(r"\begin{cvlist}")
        for item in items:
            if item.get("start"):
                yrs = f"{item['start']}--{item.get('end') or 'present'}"
            elif item.get("year"):
                yrs = str(item["year"])
            elif item.get("years"):
                yrs = tex_escape(item["years"])
            else:
                yrs = ""
            extras = ""
            if item.get("amount_gbp"):
                extras = rf"\ (\pounds{item['amount_gbp']:,})"
            elif item.get("amount_cad"):
                extras = rf"\ (CAD\ {item['amount_cad']:,})"
            extras += "."
            if item.get("role"):
                extras = rf"\ ({tex_escape(item['role'])})" + extras
            out.append(rf"  \cventry{{{yrs}}}{{{tex_escape(item['name'])}{extras}}}")
        out.append(r"\end{cvlist}")
    return "\n".join(out)


def section_visits(v) -> str:
    out = [section_title("Research Visits")]
    out.append(r"\begin{cvlist}")
    for r in v:
        line = rf"{tex_escape(r.get('role', 'Visitor'))}, {tex_escape(r['institution'])}, {tex_escape(r.get('location', ''))}."
        out.append(rf"  \cventry{{{tex_escape(str(r['date']))}}}{{{line}}}")
    out.append(r"\end{cvlist}")
    return "\n".join(out)


def section_industry(emp) -> str:
    items = emp.get("industry") or []
    if not items:
        return ""
    out = [section_title("Industry Experience")]
    out.append(r"\begin{cvlist}")
    for j in items:
        yrs = f"{j['start']}--{j['end']}"
        line = rf"{tex_escape(j['title'])}, {tex_escape(j['institution'])}, {tex_escape(j['location'])}."
        if j.get("description"):
            line += rf" {tex_escape(j['description'].strip())}"
        out.append(rf"  \cventry{{{yrs}}}{{{line}}}")
    out.append(r"\end{cvlist}")
    return "\n".join(out)


def section_personal(profile) -> str:
    per = profile.get("personal") or {}
    out = [section_title("Personal")]
    out.append(r"\begin{itemize}[leftmargin=*, itemsep=0.1em]")
    if per.get("year_of_birth"):
        out.append(rf"  \item Year of birth: {per['year_of_birth']}")
    if per.get("citizenship"):
        out.append(rf"  \item Citizenship: {tex_escape(per['citizenship'])}")
    if per.get("languages"):
        langs = ", ".join(rf"{tex_escape(l['language'])} ({tex_escape(l['level'])})" for l in per["languages"])
        out.append(rf"  \item Languages: {langs}")
    if per.get("computer_skills"):
        out.append(rf"  \item Computer skills: {tex_escape(', '.join(per['computer_skills']))}")
    out.append(r"\end{itemize}")
    return "\n".join(out)


def section_title(title: str) -> str:
    """Section header — bold uppercase with thin rule underneath."""
    return rf"""
\vspace{{1em}}
\section*{{{title}}}
\vspace{{-0.4em}}
\noindent\rule{{\textwidth}}{{0.5pt}}
\vspace{{-0.2em}}
"""


# ---- Top-of-file LaTeX preamble -------------------------------------------

PREAMBLE = r"""
\documentclass[11pt,a4paper]{article}

% Geometry — generous but not wasteful margins
\usepackage[margin=0.85in,top=0.75in,bottom=0.85in]{geometry}

% Fonts — Helvetica Neue (preinstalled on macOS). Falls back to TeX Gyre Heros
% on other systems, which is a Helvetica clone shipped with TeX Live.
\usepackage{fontspec}
\IfFontExistsTF{Helvetica Neue}{%
  \setmainfont{Helvetica Neue}[
    UprightFont = * Light,
    BoldFont    = * Medium,
    ItalicFont  = * Light Italic,
    BoldItalicFont = * Medium Italic,
  ]
}{%
  \setmainfont{TeX Gyre Heros}
}
\usepackage{microtype}

% Colors — navy accent matches website
\usepackage[dvipsnames]{xcolor}
\definecolor{accent}{HTML}{1A3A5C}
\definecolor{mid}{HTML}{5B6573}

% Hyperlinks — subtle, navy
\usepackage[hidelinks]{hyperref}
\hypersetup{
  colorlinks=true,
  linkcolor=accent,
  urlcolor=accent,
  pdfborder={0 0 0},
}

% Lists
\usepackage{enumitem}
\setlist[itemize]{leftmargin=*, itemsep=0.15em, topsep=0.2em}
\setlist[enumerate]{leftmargin=*, itemsep=0.15em, topsep=0.2em}

% Section headings
\usepackage{titlesec}
\titleformat{\section}
  {\normalfont\Large\bfseries\color{accent}}
  {}{0pt}{}
\titleformat{\subsection}
  {\normalfont\normalsize\bfseries\color{accent}}
  {}{0pt}{}
\titlespacing*{\section}{0pt}{1.2em}{0.3em}
\titlespacing*{\subsection}{0pt}{0.8em}{0.3em}

% Quotation marks
\usepackage{csquotes}

% Custom cventry: date column 80pt wide, content fills rest
\newcommand{\cventry}[2]{%
  \noindent
  \begin{minipage}[t]{80pt}\raggedright\small\color{mid}#1\end{minipage}%
  \hspace{8pt}%
  \begin{minipage}[t]{\dimexpr\textwidth-90pt\relax}#2\end{minipage}\\[0.3em]
}

\newenvironment{cvlist}{}{}

% Tighter paragraph spacing
\setlength{\parskip}{0.2em}
\setlength{\parindent}{0pt}

% No page numbers on first page
\pagestyle{empty}
"""


# ---- Assembly -------------------------------------------------------------

def build(public: bool = False) -> str:
    d = all_data(public=public)
    today = date.today().isoformat()

    parts = [PREAMBLE]
    parts.append(r"\begin{document}")
    parts.append(section_header(d["profile"], today))
    parts.append(section_academic_employment(d["employment"]))
    parts.append(section_education(d["education"]))
    parts.append(section_publications(d["publications"]))
    parts.append(section_seminars(d["seminars"]))
    parts.append(section_discussions(d["discussions"]))
    parts.append(section_service(d["service"]))
    parts.append(section_teaching(d["teaching"]))
    parts.append(section_students(d["students"]))
    parts.append(section_grants(d["grants"]))
    parts.append(section_visits(d["visits"]))
    parts.append(section_industry(d["employment"]))
    parts.append(section_personal(d["profile"]))
    parts.append(r"\end{document}")
    return "\n".join(p for p in parts if p)


def main() -> int:
    public = "--public" in sys.argv
    text = build(public=public)
    out = OUT_PUBLIC if public else OUT
    out.write_text(text)
    print(f"Wrote {out} ({len(text):,} chars){' [public]' if public else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
