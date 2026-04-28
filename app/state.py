from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.anomaly_detection import abnormal_change_score
from models.event_classifier import classify_event
from models.finbert_sentiment import score_finbert_sentiment
from models.lm_tone import score_lm_tone
from models.preprocessing import clean_text, excerpt, word_count
from models.readability import gunning_fog
from models.similarity import pairwise_similarity
from models.topics import top_keywords, topic_label, topic_shift


DEMO_TEXTS = {
    2021: """
    Our business is focused on developing differentiated therapies for patients with serious unmet medical needs.
    We advanced our lead clinical program, expanded manufacturing readiness, and maintained a disciplined capital
    allocation strategy. Collaboration with research partners improved development efficiency and created multiple
    opportunities for long-term growth.
    """,
    2022: """
    Our business continues to focus on differentiated therapies for patients with serious unmet medical needs.
    We advanced the lead clinical program and strengthened our regulatory planning. The company maintained
    resilience despite supply chain pressure and continued to invest in innovation, quality systems, and portfolio
    expansion.
    """,
    2023: """
    Following leadership transition, we undertook a strategic review of our development portfolio. The company
    discontinued selected programs, reduced external research commitments, and concentrated resources on a smaller
    set of late-stage assets. These changes may create uncertainty, execution risk, and near-term operational
    disruption while improving future capital efficiency.
    """,
}


def initialize_state() -> None:
    if "company" not in st.session_state:
        st.session_state.company = {
            "company_name": "Demo Biopharma",
            "ticker": "DEMO",
            "sector": "biopharma",
            "cik": "",
        }
    if "filings" not in st.session_state:
        st.session_state.filings = [
            {
                "filing_id": f"demo-{year}",
                "company_id": "demo",
                "company_name": "Demo Biopharma",
                "ticker": "DEMO",
                "fiscal_year": year,
                "section": "mda",
                "text": clean_text(text),
            }
            for year, text in DEMO_TEXTS.items()
        ]
    if "financials" not in st.session_state:
        st.session_state.financials = pd.DataFrame(
            [
                {"company_name": "Demo Biopharma", "ticker": "DEMO", "fiscal_year": 2021, "total_assets": 1200000000, "roa": 0.041},
                {"company_name": "Demo Biopharma", "ticker": "DEMO", "fiscal_year": 2022, "total_assets": 1340000000, "roa": 0.035},
                {"company_name": "Demo Biopharma", "ticker": "DEMO", "fiscal_year": 2023, "total_assets": 1480000000, "roa": 0.018},
            ]
        )
    if "events" not in st.session_state:
        st.session_state.events = pd.DataFrame(
            [
                {
                    "event_id": "evt-demo-2023",
                    "company_name": "Demo Biopharma",
                    "ticker": "DEMO",
                    "event_date": "2023-03-15",
                    "fiscal_year": 2023,
                    "event_description": "Chief executive officer retired and an external successor was appointed.",
                    **classify_event("Chief executive officer retired and an external successor was appointed."),
                }
            ]
        )


def add_uploaded_filing(company_name: str, ticker: str, fiscal_year: int, section: str, text: str) -> None:
    st.session_state.filings.append(
        {
            "filing_id": str(uuid4()),
            "company_id": ticker.lower() or "company",
            "company_name": company_name,
            "ticker": ticker.upper(),
            "fiscal_year": int(fiscal_year),
            "section": section,
            "text": clean_text(text),
        }
    )


def add_financial(company_name: str, ticker: str, fiscal_year: int, total_assets: float, roa: float) -> None:
    row = pd.DataFrame(
        [
            {
                "company_name": company_name,
                "ticker": ticker.upper(),
                "fiscal_year": int(fiscal_year),
                "total_assets": float(total_assets),
                "roa": float(roa),
            }
        ]
    )
    st.session_state.financials = pd.concat([st.session_state.financials, row], ignore_index=True)
    st.session_state.financials = st.session_state.financials.drop_duplicates(
        subset=["ticker", "fiscal_year"], keep="last"
    )


def add_event(company_name: str, ticker: str, fiscal_year: int, event_date: str, event_description: str) -> None:
    classified = classify_event(event_description)
    row = pd.DataFrame(
        [
            {
                "event_id": str(uuid4()),
                "company_name": company_name,
                "ticker": ticker.upper(),
                "event_date": str(event_date),
                "fiscal_year": int(fiscal_year),
                "event_description": event_description,
                **classified,
            }
        ]
    )
    st.session_state.events = pd.concat([st.session_state.events, row], ignore_index=True)


def filings_frame() -> pd.DataFrame:
    return pd.DataFrame(st.session_state.filings).sort_values(["ticker", "section", "fiscal_year"])


def compute_textual_metrics(filings: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, filing in filings.iterrows():
        text = filing["text"]
        keywords = top_keywords(text)
        rows.append(
            {
                "metric_id": str(uuid4()),
                "filing_id": filing["filing_id"],
                "company_name": filing["company_name"],
                "ticker": filing["ticker"],
                "fiscal_year": int(filing["fiscal_year"]),
                "section": filing["section"],
                "word_count": word_count(text),
                **score_lm_tone(text),
                **score_finbert_sentiment(text),
                "fog_index": gunning_fog(text),
                "topic_keywords": keywords,
                "topic_label": topic_label(keywords),
                "excerpt": excerpt(text),
            }
        )
    return pd.DataFrame(rows)


def compute_narrative_change(filings: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    financials = st.session_state.financials.copy()
    financials["roa_change"] = financials.sort_values("fiscal_year").groupby("ticker")["roa"].diff()
    events = st.session_state.events.copy()

    for (_, section), group in filings.groupby(["ticker", "section"]):
        group = group.sort_values("fiscal_year")
        for previous, current in zip(group.iloc[:-1].to_dict("records"), group.iloc[1:].to_dict("records")):
            prev_metrics = metrics.loc[metrics["filing_id"] == previous["filing_id"]].iloc[0].to_dict()
            curr_metrics = metrics.loc[metrics["filing_id"] == current["filing_id"]].iloc[0].to_dict()
            current_year = int(current["fiscal_year"])
            event_match = events[(events["ticker"] == current["ticker"]) & (events["fiscal_year"] == current_year)]
            financial_match = financials[
                (financials["ticker"] == current["ticker"]) & (financials["fiscal_year"] == current_year)
            ]
            roa_change = 0.0 if financial_match.empty else financial_match.iloc[0].get("roa_change", 0.0)
            similarity = pairwise_similarity(previous["text"], current["text"])
            row = {
                "change_id": str(uuid4()),
                "company_name": current["company_name"],
                "ticker": current["ticker"],
                "company_id": current["ticker"].lower(),
                "fiscal_year": current_year,
                "previous_year": int(previous["fiscal_year"]),
                "section": section,
                "cosine_similarity": similarity,
                "similarity_drop": 1 - similarity,
                "delta_net_tone": curr_metrics["net_tone"] - prev_metrics["net_tone"],
                "delta_finbert_sentiment": curr_metrics["finbert_net_sentiment"] - prev_metrics["finbert_net_sentiment"],
                "delta_fog_index": curr_metrics["fog_index"] - prev_metrics["fog_index"],
                "topic_shift_score": topic_shift(prev_metrics["topic_keywords"], curr_metrics["topic_keywords"]),
                "roa_change": 0.0 if pd.isna(roa_change) else float(roa_change),
                "has_leadership_event": not event_match.empty,
                "previous_excerpt": excerpt(previous["text"]),
                "current_excerpt": excerpt(current["text"]),
                "topic_label": curr_metrics["topic_label"],
            }
            flag, reason, score = abnormal_change_score(row)
            row["abnormal_change_flag"] = flag
            row["abnormal_change_reason"] = reason
            row["abnormal_change_score"] = score
            rows.append(row)
    return pd.DataFrame(rows)


def analysis_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    filings = filings_frame()
    metrics = compute_textual_metrics(filings)
    changes = compute_narrative_change(filings, metrics)
    return filings, metrics, changes, st.session_state.events.copy()
