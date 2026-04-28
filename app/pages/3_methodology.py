from __future__ import annotations

import streamlit as st


st.set_page_config(page_title="Methodology", layout="wide")

st.title("Methodology")

st.subheader("Hybrid Textual Analysis Model")
st.write(
    "The demo combines transparent text metrics with an AI-compatible sentiment interface. "
    "The current implementation runs offline and uses deterministic scoring so it can be deployed easily."
)

st.markdown(
    """
- **Tone:** finance-oriented positive, negative, and uncertainty word ratios.
- **AI sentiment:** FinBERT-compatible output schema with an offline proxy.
- **Readability:** Gunning Fog score.
- **Similarity:** TF-IDF cosine similarity between adjacent fiscal years.
- **Topics:** TF-IDF keyword extraction and keyword-set topic distance.
- **Abnormal detection:** weighted rule model combining narrative, topic, ROA, and leadership-event signals.
"""
)

st.subheader("Abnormal Change Logic")
st.write(
    "A year is flagged when several moderate signals or one very large narrative signal occur together. "
    "The threshold is intentionally transparent for portfolio review and can be replaced with a statistical "
    "or supervised model once labeled data exists."
)
