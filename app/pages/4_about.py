from __future__ import annotations

import streamlit as st


st.set_page_config(page_title="About", layout="wide")

st.title("About")
st.write(
    "Corporate Narrative Intelligence is a portfolio demo for analyzing how public-company disclosure language "
    "changes over time. It is designed for biopharma annual report narratives but the architecture can be adapted "
    "to other sectors."
)

st.subheader("Product Boundaries")
st.write(
    "The demo does not include authentication, live SEC scraping, paid data feeds, real-time financial data, "
    "multi-user workspaces, or a full academic regression engine."
)

st.subheader("Intended Use")
st.write(
    "Use this project to demonstrate product thinking, text analytics, interpretable AI-assisted analysis, "
    "and dashboard storytelling. It is not financial advice."
)
