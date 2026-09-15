#!/usr/bin/env python3
"""
Apply manual corrections to data/discussions.yml.

The ingest script extracts title/authors/date from LaTeX sources where possible.
For entries where that fails (or extracts the wrong info), corrections live here.
Re-run this after running ingest_discussions.py.

Each override is a dict keyed by discussion `id`. Any fields present in the
override replace the corresponding fields in the loaded entry.
"""
from __future__ import annotations
from pathlib import Path
import sys
import yaml

YML = Path(__file__).resolve().parent.parent / "data" / "discussions.yml"

OVERRIDES: dict[str, dict] = {
    # --- Title + authors extracted from slide PDFs (first page) ---

    "liao": {
        "paper_title": "Credit Migration and Covered Interest Rate Parity",
        "paper_authors": ["Gordon Y. Liao"],
        "date": "2018-01",
    },
    "luo": {
        "paper_title": "Capital Heterogeneity, Time-To-Build, and Return Predictability",
        "paper_authors": ["Ding Luo"],
        "date": "2018-11-18",
    },
    "rinne": {
        "paper_title": "Do Open-market Share Repurchases Supply or Demand Immediacy?",
        "paper_authors": ["Jankovic", "Rinne"],
        "date": "2018-07-26",
    },
    "schmid": {
        "paper_title": "Risk-Adjusted Capital Allocation and Misallocation",
        "paper_authors": ["Joel David", "Lukas Schmid", "David Zeke"],
        "date": "2018-05-19",
    },
    "uppalzaffaroni": {
        "paper_title": "Portfolio Choice with Model Misspecification: A Foundation for Alpha and Beta Portfolios",
        "paper_authors": ["Raman Uppal", "Paolo Zaffaroni"],
        "date": "2018-08-23",
    },
    "routledge-zin": {
        "paper_title": "Generalized Disappointment Aversion and Asset Prices",
        "paper_authors": ["Bryan R. Routledge", "Stanley E. Zin"],
        "date": "2004-06",
    },
    "wangwhitedwuxiao": {
        "paper_title": "Bank Market Power and Monetary Policy Transmission: Evidence from a Structural Estimation",
        "paper_authors": ["Yifei Wang", "Toni M. Whited", "Yufeng Wu", "Kairong Xiao"],
        "date": "2019-02-15",
    },
    "li-li-yang": {
        "paper_title": "Sovereign CDS Spreads with Credit Rating",
        "paper_authors": ["Li", "Li", "Yang"],
        "date": "2016",
    },
    "prieto-hugonnier": {
        "paper_title": "Arbitrageurs, Bubbles and Credit Conditions",
        "paper_authors": ["Prieto", "Hugonnier"],
        "date": "2011",
    },
    "avernasvandeweyerparies": {
        "paper_title": "Unconventional Monetary Policy and Funding Liquidity Risk",
        "paper_authors": ["Adrien d'Avernas", "Quentin Vandeweyer", "Matthieu Darracq Pariès"],
        "date": "2019",
    },

    # --- Round 2 ---

    "ehling": {
        "paper_title": "Tax Collection from Realized Capital Gains on Equity",
        "paper_authors": ["Paul Ehling", "Stathis Tompaidis", "Chunyu Yang"],
        "date": "2018-10-09",
    },
    "detemple-tian": {
        "paper_title": "Debt with Endogenous Safety Covenants: Default and Corporate Securities",
        "paper_authors": ["Detemple", "Tian"],
        "date": "2007-09",
    },
    "hackbarth": {
        "paper_title": "Maturity Overhang: Evidence from M&A",
        "paper_authors": ["Chen", "Hackbarth", "Harford", "Luo"],
        "date": "2025",
    },
    "feng-luo-westerfield": {
        "paper_title": "The Optimal Schedules of Incentives and Cash Flows",
        "paper_authors": ["Feng", "Luo", "Westerfield"],
        # date in folder name says 2025-08-25, set it
        "date": "2025-08-25",
    },
    "cram-kung-lustig": {
        "paper_title": "Can U.S. Treasury Markets Add and Subtract?",
        "paper_authors": ["Roberto Gomez-Cram", "Howard Kung", "Hanno Lustig"],
        "date": "2024",
    },
    "cieslak-khorrami": {
        "paper_title": "Risk Premia, Subjective Beliefs, and Forward Guidance",
        "paper_authors": ["Anna Cieslak", "Paymon Khorrami"],
        "date": "2024-05-29",
    },
    "davydiukshalistovichyaron": {
        "paper_title": "How Risky are the U.S. Corporate Assets?",
        "paper_authors": ["Tetiana Davydiuk", "Scott Richard", "Ivan Shaliastovich", "Amir Yaron"],
        "date": "2019",
    },
    "buraschitebaldi": {
        "paper_title": "Asset Pricing Implications of Systemic Risk in Network Economies",
        "paper_authors": ["Andrea Buraschi", "Claudio Tebaldi"],
        "date": "2019",
    },
    "chen-joslin-tran": {
        # First page is text-only with title "Comments on Chen, Joslin and Tran" — no paper title shown.
        # Likely discussing the 2010 JF paper. Leave placeholder for user to confirm.
        "paper_title": "Discussion: Chen, Joslin & Tran",
        "paper_authors": ["Hui Chen", "Scott Joslin", "Ngoc-Khanh Tran"],
        "date": "2010-04-22",
    },

    # --- Round 3: dates / minor fills ---

    "martin": {
        "paper_title": "The Forward Premium Puzzle in a Two-Country World",
        "paper_authors": ["Ian Martin"],
        "date": "2014",
    },
    "maya": {
        "paper_title": "Financial Distortions and the Distribution of Global Volatility",
        "paper_authors": ["Maya Eden"],
        "date": "2010-10",
    },
    "isaenko": {
        "paper_title": "Dynamic Equilibrium in an Economy with an Illiquid Stock Market",
        "paper_authors": ["Sergei Isaenko"],
        "date": "2011-03",
    },
    "dumas-conference": {
        "paper_title": "Dynamic Noisy Rational Expectations Equilibrium with Information Production and Beliefs-Based Speculation",
        "paper_authors": ["Detemple", "Rindisbacher"],
        "date": "2016-06",
    },
    "detemple": {
        "paper_title": "Dynamic Noisy Rational Expectations Equilibrium with Information Production and Beliefs-Based Speculation",
        "paper_authors": ["Detemple", "Rindisbacher"],
        "date": "2016-06",
    },
    "lse-paul-woolley": {
        "paper_title": "A Dynamic Equilibrium Model of ETFs",
        "paper_authors": ["Semyon Malamud"],
        "date": "2016",
    },
    "lochstoer-lundeby-tancheva": {
        "paper_title": "Dynamic Trading and Asset Pricing with Time-Inconsistent Agents",
        "paper_authors": ["Lars A. Lochstoer", "Lundeby", "Tancheva"],
        "date": "2024-09-24",
    },
    "climatechange-piontek-hansen": {
        # User confirmed: keep as discussion of Piontek/Hansen's climate paper.
        # Bhamra used his own framing for the slide title.
        "paper_title": "Modeling Climate and Economic Dynamics: Optimist vs. Pessimist Views",
        "paper_authors": ["Piontek", "Hansen"],
        "date": "2024-05-01",
    },

    "andrei": {
        "paper_title": "The Redistributive Effects of Monetary Policy",
        "paper_authors": ["Daniel Andrei", "Bernard Herskovic", "Olivier Ledoit"],
        "date": "2015-06-29",   # folder mtime
    },

    "feldhuetter": {
        "paper_title": "The Credit Spread Puzzle — Myth or Reality?",
        "paper_authors": ["Peter Feldhütter", "Stephen Schaefer"],
        "date": "2015",
        "video": "https://www.youtube.com/watch?v=lzFMhfprMY8",
    },

    # --- Folder-name spelling / minor fixes ---

    "bansal-ward-yaron": {
        "paper_title": "Equilibrium Wealth Share Dynamics",
        "paper_authors": ["Ravi Bansal", "Colin Ward", "Amir Yaron"],
        "date": "2017",     # was UBC Winter 2017 per filename "UBCWinter2017-..."
    },
    "ai-li": {
        # Already has correct authors from .tex. Just ensure schema cleanliness.
        "paper_title": "Financial Intermediation and Capital Reallocation",
        "paper_authors": ["Hengjie Ai", "Kai Li", "Fang Yang"],
    },
    "malamud": {
        "paper_title": "A Dynamic Equilibrium Model of ETFs",
        "paper_authors": ["Semyon Malamud"],
        "date": "2016-06",
    },
    "martin-wagner": {
        "paper_title": "What is the Expected Return on a Stock?",
        "paper_authors": ["Ian Martin", "Christian Wagner"],
        "date": "2018",
    },
    "gallmeyer-hollifield-palomino-zin": {
        "paper_title": "Arbitrage-Free Bond Pricing With Dynamic Macroeconomic Models",
        "paper_authors": ["Michael Gallmeyer", "Burton Hollifield", "Francisco Palomino", "Stanley Zin"],
        "date": "2007-11",
    },
    "cooper": {
        # Earlier ingest captured complex author block — narrow to just Cooper's piece if applicable.
        # Leave as-is unless user clarifies.
    },
    "opp": {
        "paper_title": "Learning about Distress",
        "paper_authors": ["Christian C. Opp"],
        "date": "2015-09",
    },
    "bigio": {
        "paper_title": "Banks, Liquidity Management and Monetary Policy",
        "paper_authors": ["Javier Bianchi", "Saki Bigio"],
        "date": "2014-05-31",
    },
    "adrian-boyarchenko": {
        # Was extracted in ALLCAPS. Normalize.
        "paper_title": "Intermediary Leverage Cycles and Financial Stability",
        "paper_authors": ["Tobias Adrian", "Nina Boyarchenko"],
        "date": "2013-05-14",
    },
    "boediscussion": {
        # Folder name is non-descriptive; the paper is the Colacito et al currency-risk one.
        "paper_title": "Currency Risk Factors in a Recursive Multi-Country Economy",
        "paper_authors": ["Riccardo Colacito", "Max Croce", "Federico Gavazzoni", "Robert Ready"],
        "date": "2016-12-15",   # Bank of England event, folder dated Dec 2016
        "note": "Presented at Bank of England / CEPR International Finance Conference.",
    },
    "cole-greenwood-sanchez": {
        # Folder name had typo "Greenword"; fix author list.
        "paper_title": "Why Doesn't Technology Flow from Rich to Poor Countries?",
        "paper_authors": ["Harold L. Cole", "Jeremy Greenwood", "Juan M. Sanchez"],
    },
    "fais-santaclara": {
        # Authors had a stray "-- Clara" artifact.
        "paper_title": "Optimal Option Portfolio Strategies",
        "paper_authors": ["José Faias", "Pedro Santa-Clara"],
    },
    "bryzalgova": {
        # Folder name typo: actually "Bryzgalova".
        "paper_title": "Bayesian Solutions for the Factor Zoo: We Just Ran Two Quadrillion Models",
        "paper_authors": ["Svetlana Bryzgalova", "Jiantao Huang", "Christian Julliard"],
        "date": "2020-09-26",
    },
    "heyderdahi-lleditsch": {
        # Folder typo: "Heyerdahl-Illeditsch".
        "paper_title": "Demand Disagreement",
        "paper_authors": ["Christian Heyerdahl-Larsen", "Philipp Illeditsch"],
        "date": "2021-08-26",
    },

    # --- Bigio_Silva_Zilberman: looks like a misplaced project folder, not a discussion. ---
    "bigio-silva-zilberman": {
        "paper_title": None,
        "paper_authors": None,
        "note": "TODO: verify whether this is a real discussion. The folder contains "
                "BeliefsPermanentVolatility.pdf and Claude-style project files; the PDF "
                "first page shows Khorrami's 'A Model-Free Assessment of the Importance of "
                "Subjective Beliefs for Asset Pricing' (Mar 2026) — likely a research "
                "project folder mis-filed in the discussions directory.",
        "skip_website": True,
    },

    # --- albuquerque-nengwang: no PDF, no .tex ---
    "albuquerque-nengwang": {
        "paper_title": "Agency Conflicts, Investment and Asset Pricing",
        "paper_authors": ["Rui Albuquerque", "Neng Wang"],
        "date": "2007",
        "note": "TODO: locate slide PDF — folder has no extractable content.",
    },
}


def main() -> int:
    raw_text = YML.read_text()
    # Preserve YAML header comments
    header_lines = []
    for line in raw_text.splitlines():
        if line.startswith("#") or not line.strip():
            header_lines.append(line)
        else:
            break
    header = "\n".join(header_lines) + ("\n" if header_lines else "")

    data = yaml.safe_load(raw_text)
    updated = 0
    not_found = []
    for slug, patch in OVERRIDES.items():
        if not patch:
            continue
        match = next((d for d in data["discussions"] if d["id"] == slug), None)
        if match is None:
            not_found.append(slug)
            continue
        for k, v in patch.items():
            match[k] = v
        updated += 1

    # Re-sort by date (most recent first; None last)
    data["discussions"].sort(key=lambda d: d.get("date") or "0", reverse=True)

    YML.write_text(header + yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=200))

    print(f"Patched {updated} entries in {YML.name}.")
    if not_found:
        print(f"Skipped (slug not found): {', '.join(not_found)}")

    # Stats
    missing_title = sum(1 for d in data["discussions"] if not d.get("paper_title"))
    missing_authors = sum(1 for d in data["discussions"] if not d.get("paper_authors"))
    missing_date = sum(1 for d in data["discussions"] if not d.get("date"))
    print(f"After patch: {missing_title} missing title, {missing_authors} missing authors, {missing_date} missing date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
