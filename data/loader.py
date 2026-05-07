from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILINGS_DIR = ROOT / "data" / "raw" / "filings"

# Three companies chosen to illustrate distinct narrative shift patterns:
#  AKRX  — peak performance → FDA data-integrity crisis (2018)
#  CLVS  — pre-commercial development → rucaparib approval (2016) → scaling
#  PBYI  — pure development stage → NERLYNX FDA approval (2017) → launch

DEMO_COMPANIES: dict[str, dict] = {
    "AKRX": {
        "company_name": "Akorn Inc.",
        "ticker": "AKRX",
        "sector": "Specialty Pharmaceuticals",
        "story": "Peak performance in 2016 followed by an FDA data-integrity investigation and governance crisis in 2018.",
        "mda_years": [2014, 2016, 2017, 2018],
        "financials": {
            2014: {"total_assets": 1_832_150_000, "roa": 0.008},
            2016: {"total_assets": 1_973_720_000, "roa": 0.093},
            2017: {"total_assets": 1_909_511_000, "roa": -0.013},
            2018: {"total_assets": 1_495_257_000, "roa": -0.269},
        },
        "events": [
            {
                "fiscal_year": 2018,
                "event_date": "2018-07-26",
                "description": (
                    "CEO Raj Rai resigned and the board appointed a new interim chief executive. "
                    "The company withdrew from its pending acquisition by Fresenius Kabi following "
                    "an FDA data-integrity investigation into manufacturing quality systems."
                ),
            }
        ],
    },
    "CLVS": {
        "company_name": "Clovis Oncology",
        "ticker": "CLVS",
        "sector": "Oncology",
        "story": "Rucaparib received accelerated FDA approval in December 2016, shifting narrative from development to commercialization.",
        "mda_years": [2015, 2016, 2017, 2018],
        "financials": {
            2015: {"total_assets": 685_000_000, "roa": -0.340},
            2016: {"total_assets": 812_000_000, "roa": -0.450},
            2017: {"total_assets": 901_000_000, "roa": -0.380},
            2018: {"total_assets": 944_000_000, "roa": -0.320},
        },
        "events": [],
    },
    "PBYI": {
        "company_name": "Puma Biotechnology",
        "ticker": "PBYI",
        "sector": "Oncology",
        "story": "NERLYNX (neratinib) received FDA approval in July 2017, transforming disclosure language from clinical-stage to commercial.",
        "mda_years": [2015, 2016, 2017, 2018],
        "financials": {
            2015: {"total_assets": 280_000_000, "roa": -0.480},
            2016: {"total_assets": 198_000_000, "roa": -0.720},
            2017: {"total_assets": 405_000_000, "roa": -0.380},
            2018: {"total_assets": 381_000_000, "roa": -0.180},
        },
        "events": [],
    },
}


def load_mda_text(ticker: str, fiscal_year: int) -> str:
    path = FILINGS_DIR / f"{ticker}_{fiscal_year}_mda.txt"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def all_filings() -> list[dict]:
    rows = []
    for ticker, cfg in DEMO_COMPANIES.items():
        for fy in cfg["mda_years"]:
            text = load_mda_text(ticker, fy)
            if text:
                rows.append(
                    {
                        "filing_id": f"{ticker}-{fy}-mda",
                        "company_id": ticker.lower(),
                        "company_name": cfg["company_name"],
                        "ticker": ticker,
                        "fiscal_year": fy,
                        "section": "mda",
                        "text": text,
                    }
                )
    return rows


def all_financials_rows() -> list[dict]:
    rows = []
    for ticker, cfg in DEMO_COMPANIES.items():
        for fy, fin in cfg["financials"].items():
            rows.append(
                {
                    "company_name": cfg["company_name"],
                    "ticker": ticker,
                    "fiscal_year": fy,
                    "total_assets": fin["total_assets"],
                    "roa": fin["roa"],
                }
            )
    return rows


def all_event_rows() -> list[dict]:
    rows = []
    for ticker, cfg in DEMO_COMPANIES.items():
        for ev in cfg["events"]:
            rows.append(
                {
                    "company_name": cfg["company_name"],
                    "ticker": ticker,
                    **ev,
                }
            )
    return rows
