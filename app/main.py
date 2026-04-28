from __future__ import annotations

from datetime import date

import streamlit as st

from state import add_event, add_financial, add_uploaded_filing, initialize_state


st.set_page_config(
    page_title="Corporate Narrative Intelligence",
    layout="wide",
)

initialize_state()

st.title("Corporate Narrative Intelligence")
st.caption("Annual report narrative analysis for abnormal strategic and governance signals.")

left, right = st.columns([1.2, 0.8])
with left:
    st.subheader("Detect strategic narrative shifts over time")
    st.write(
        "Corporate annual reports often appear stable, but sudden shifts in language structure, readability, "
        "tone, or topic focus may signal deeper strategic or governance changes."
    )
    st.page_link("pages/1_dashboard.py", label="Launch Demo")

with right:
    st.metric("Demo company", st.session_state.company["company_name"], st.session_state.company["ticker"])
    st.metric("Default sector", st.session_state.company["sector"])

st.divider()
st.subheader("Add company narrative data")

with st.form("upload_filing_form"):
    company_name = st.text_input("Company", value=st.session_state.company["company_name"])
    ticker = st.text_input("Ticker", value=st.session_state.company["ticker"])
    section = st.selectbox("Filing section", ["business_description", "mda", "both"], index=1)
    fiscal_year = st.number_input("Fiscal year", min_value=1990, max_value=2100, value=2024, step=1)
    uploaded_file = st.file_uploader("Upload filing text", type=["txt", "md"])
    pasted_text = st.text_area("Or paste narrative text", height=180)
    total_assets = st.number_input("Total assets", min_value=0.0, value=0.0, step=1000000.0)
    roa = st.number_input("ROA", value=0.0, step=0.001, format="%.4f")
    submitted = st.form_submit_button("Add filing year")

    if submitted:
        text = pasted_text
        if uploaded_file is not None:
            text = uploaded_file.read().decode("utf-8", errors="ignore")
        if text.strip():
            add_uploaded_filing(company_name, ticker, int(fiscal_year), section, text)
            add_financial(company_name, ticker, int(fiscal_year), total_assets, roa)
            st.success(f"Added {ticker.upper()} {int(fiscal_year)} narrative.")
        else:
            st.warning("Add text by uploading a file or pasting narrative content.")

st.subheader("Add top management change event")
with st.form("event_form"):
    event_company = st.text_input("Event company", value=st.session_state.company["company_name"])
    event_ticker = st.text_input("Event ticker", value=st.session_state.company["ticker"])
    event_year = st.number_input("Event fiscal year", min_value=1990, max_value=2100, value=2024, step=1)
    event_date = st.date_input("Event date", value=date.today())
    event_description = st.text_area("Event description", height=100)
    event_submitted = st.form_submit_button("Add leadership event")
    if event_submitted:
        if event_description.strip():
            add_event(event_company, event_ticker, int(event_year), str(event_date), event_description)
            st.success("Leadership event added and classified.")
        else:
            st.warning("Enter an event description.")
