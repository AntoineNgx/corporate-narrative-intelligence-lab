from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.loader import DEMO_COMPANIES, all_event_rows, all_financials_rows, all_filings
from models.anomaly_detection import abnormal_change_score
from models.event_classifier import classify_event
from models.finbert_sentiment import score_finbert_sentiment
from models.lm_tone import score_lm_tone
from models.preprocessing import clean_text, excerpt, word_count
from models.readability import gunning_fog
from models.similarity import pairwise_similarity
from models.topics import top_keywords, topic_label, topic_shift


def initialize_state() -> None:
    if "filings" not in st.session_state:
        st.session_state.filings = all_filings()

    if "financials" not in st.session_state:
        st.session_state.financials = pd.DataFrame(all_financials_rows())

    if "events" not in st.session_state:
        event_rows = []
        for ev in all_event_rows():
            desc = ev["description"]
            classified = classify_event(desc)
            event_rows.append(
                {
                    "event_id": str(uuid4()),
                    "company_name": ev["company_name"],
                    "ticker": ev["ticker"],
                    "event_date": ev["event_date"],
                    "fiscal_year": ev["fiscal_year"],
                    "event_description": desc,
                    **classified,
                }
            )
        st.session_state.events = pd.DataFrame(event_rows) if event_rows else pd.DataFrame(
            columns=["event_id", "company_name", "ticker", "event_date", "fiscal_year",
                     "event_description", "event_type", "turnover_type", "successor_origin",
                     "classification_rationale"]
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
        [{"company_name": company_name, "ticker": ticker.upper(),
          "fiscal_year": int(fiscal_year), "total_assets": float(total_assets), "roa": float(roa)}]
    )
    st.session_state.financials = pd.concat([st.session_state.financials, row], ignore_index=True)
    st.session_state.financials = st.session_state.financials.drop_duplicates(
        subset=["ticker", "fiscal_year"], keep="last"
    )


def add_event(company_name: str, ticker: str, fiscal_year: int, event_date: str, event_description: str) -> None:
    classified = classify_event(event_description)
    row = pd.DataFrame(
        [{"event_id": str(uuid4()), "company_name": company_name, "ticker": ticker.upper(),
          "event_date": str(event_date), "fiscal_year": int(fiscal_year),
          "event_description": event_description, **classified}]
    )
    st.session_state.events = pd.concat([st.session_state.events, row], ignore_index=True)


def filings_frame() -> pd.DataFrame:
    return pd.DataFrame(st.session_state.filings).sort_values(["ticker", "section", "fiscal_year"])


@st.cache_data(show_spinner=False)
def _compute_metrics_cached(filing_records: tuple[tuple, ...]) -> pd.DataFrame:
    rows = []
    for rec in filing_records:
        d = dict(zip(
            ["filing_id", "company_name", "ticker", "fiscal_year", "section", "text"],
            rec,
        ))
        text = d["text"]
        keywords = top_keywords(text)
        rows.append(
            {
                "metric_id": str(uuid4()),
                "filing_id": d["filing_id"],
                "company_name": d["company_name"],
                "ticker": d["ticker"],
                "fiscal_year": int(d["fiscal_year"]),
                "section": d["section"],
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


def compute_textual_metrics(filings: pd.DataFrame) -> pd.DataFrame:
    records = tuple(
        (r["filing_id"], r["company_name"], r["ticker"], r["fiscal_year"], r["section"], r["text"])
        for _, r in filings.iterrows()
    )
    return _compute_metrics_cached(records)


def compute_narrative_change(filings: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    financials = st.session_state.financials.copy()
    financials["roa_change"] = (
        financials.sort_values("fiscal_year").groupby("ticker")["roa"].diff()
    )
    events = st.session_state.events.copy()

    for (ticker, section), group in filings.groupby(["ticker", "section"]):
        group = group.sort_values("fiscal_year")
        pairs = list(zip(group.iloc[:-1].to_dict("records"), group.iloc[1:].to_dict("records")))
        for previous, current in pairs:
            prev_m = metrics.loc[metrics["filing_id"] == previous["filing_id"]].iloc[0].to_dict()
            curr_m = metrics.loc[metrics["filing_id"] == current["filing_id"]].iloc[0].to_dict()
            current_year = int(current["fiscal_year"])
            event_match = events[
                (events["ticker"] == ticker) & (events["fiscal_year"] == current_year)
            ]
            fin_match = financials[
                (financials["ticker"] == ticker) & (financials["fiscal_year"] == current_year)
            ]
            roa_change = 0.0 if fin_match.empty else fin_match.iloc[0].get("roa_change", 0.0)
            similarity = pairwise_similarity(previous["text"], current["text"])
            row = {
                "change_id": str(uuid4()),
                "company_name": current["company_name"],
                "ticker": ticker,
                "company_id": ticker.lower(),
                "fiscal_year": current_year,
                "previous_year": int(previous["fiscal_year"]),
                "section": section,
                "cosine_similarity": similarity,
                "similarity_drop": 1 - similarity,
                "delta_net_tone": curr_m["net_tone"] - prev_m["net_tone"],
                "delta_finbert_sentiment": curr_m["finbert_net_sentiment"] - prev_m["finbert_net_sentiment"],
                "delta_fog_index": curr_m["fog_index"] - prev_m["fog_index"],
                "topic_shift_score": topic_shift(prev_m["topic_keywords"], curr_m["topic_keywords"]),
                "roa_change": 0.0 if pd.isna(roa_change) else float(roa_change),
                "has_leadership_event": not event_match.empty,
                "previous_excerpt": excerpt(previous["text"]),
                "current_excerpt": excerpt(current["text"]),
                "topic_label": curr_m["topic_label"],
            }
            flag, reason, score = abnormal_change_score(row)
            row["abnormal_change_flag"] = flag
            row["abnormal_change_reason"] = reason
            row["abnormal_change_score"] = score
            rows.append(row)
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def _full_analysis_cached(filing_records: tuple[tuple, ...], fin_hash: str, evt_hash: str):
    filings = pd.DataFrame(
        [dict(zip(["filing_id", "company_id", "company_name", "ticker", "fiscal_year", "section", "text"], r))
         for r in filing_records]
    )
    metrics = _compute_metrics_cached(filing_records)
    return filings, metrics


def analysis_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    filings = filings_frame()
    metrics = compute_textual_metrics(filings)
    changes = compute_narrative_change(filings, metrics)
    return filings, metrics, changes, st.session_state.events.copy()
