from __future__ import annotations

from datetime import date

import streamlit as st

from state import (
    add_event,
    add_financial,
    add_uploaded_filing,
    analysis_frames,
    initialize_state,
)
from data.loader import DEMO_COMPANIES

st.set_page_config(page_title="MAIN")

st.set_page_config(
    page_title="Corporate Narrative Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .metric-card {
        background: #F0F4F8;
        border-radius: 10px;
        padding: 20px 24px;
        border-left: 4px solid #1D4E89;
        margin-bottom: 8px;
    }
    .metric-card h4 { margin: 0 0 4px 0; font-size: 13px; color: #4A5568; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-card p  { margin: 0; font-size: 22px; font-weight: 700; color: #0F172A; }
    .metric-card small { color: #718096; font-size: 12px; }
    .company-card {
        border: 1px solid #CBD5E0;
        border-radius: 10px;
        padding: 20px;
        background: white;
        height: 100%;
    }
    .company-card h3 { margin: 0 0 4px 0; color: #1D4E89; font-size: 18px; }
    .company-card .ticker { color: #718096; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
    .company-card .story { color: #4A5568; font-size: 13px; margin-top: 10px; line-height: 1.5; }
    .alert-pill {
        display: inline-block;
        background: #FEF3C7;
        color: #92400E;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 11px;
        font-weight: 600;
        margin-top: 8px;
    }
    .section-label {
        font-size: 11px;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        margin-bottom: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

initialize_state()

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("Corporate Narrative Intelligence Lab")
st.markdown(
    "**Detecting strategic disclosure shifts in US biopharma 10-K filings** · "
    "MD&A narrative · Tone · Readability · Topic · Cosine similarity"
)
st.divider()

# ── Pre-computed company snapshots ─────────────────────────────────────────────
with st.spinner("Computing narrative metrics across all filings…"):
    filings, metrics, changes, events = analysis_frames()

st.markdown('<p class="section-label">Pre-loaded companies · MDA section · Real 10-K filings</p>', unsafe_allow_html=True)

cols = st.columns(3, gap="medium")
tickers = list(DEMO_COMPANIES.keys())

for col, ticker in zip(cols, tickers):
    cfg = DEMO_COMPANIES[ticker]
    co_changes = changes[changes["ticker"] == ticker]
    co_metrics = metrics[metrics["ticker"] == ticker].sort_values("fiscal_year")
    n_alerts = int(co_changes["abnormal_change_flag"].sum()) if not co_changes.empty else 0
    latest_tone = co_metrics.iloc[-1]["net_tone"] if not co_metrics.empty else 0
    years = sorted(co_metrics["fiscal_year"].unique())
    year_range = f"{years[0]}–{years[-1]}" if len(years) >= 2 else str(years[0]) if years else "—"

    with col:
        alert_pill = f'<span class="alert-pill">⚠ {n_alerts} alert{"s" if n_alerts != 1 else ""}</span>' if n_alerts else '<span class="alert-pill" style="background:#D1FAE5;color:#065F46;">✓ No alerts</span>'
        st.markdown(
            f"""
            <div class="company-card">
                <div class="ticker">{ticker} · {cfg['sector']}</div>
                <h3>{cfg['company_name']}</h3>
                <div class="story">{cfg['story']}</div>
                {alert_pill}
                <div style="margin-top:14px; display:flex; gap:24px;">
                    <div><div class="section-label">Years</div><strong>{year_range}</strong></div>
                    <div><div class="section-label">Latest tone</div><strong>{latest_tone:+.3f}</strong></div>
                    <div><div class="section-label">Filings</div><strong>{len(years)}</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("")
_, center, _ = st.columns([1, 1.2, 1])
with center:
    if st.button("Explore Full Analysis →", type="primary", use_container_width=True):
        st.switch_page("pages/1_Narrative Dashboard.py")

st.divider()

# ── Research context ────────────────────────────────────────────────────────────
with st.expander("About this research", expanded=False):
    st.markdown(
        """
        This tool is built on doctoral research examining how **cyclical financial performance** and
        **top management team changes** affect narrative strategy in annual report disclosures.

        **Data:** US biopharma 10-K filings (Item 1 Business Description, Item 7 MD&A), with financial
        data from S&P Global. Sections are extracted from EDGAR filings and analyzed at the firm-year level.

        **Key signals measured:**
        - **Cosine similarity** — How much the text changes year-over-year
        - **Sentiment Analysis** — Changes of Text Sentiment over years
        - **Readability** — Changes of reading text over years
        - **Topic shift** — keyword-set distance between adjacent years
        - **Abnormal change score** — weighted combination of the above, cross-referenced with ROA and leadership events
        """
    )

# ── Add your own data ────────────────────────────────────────────────────────────
with st.expander("Add your own company data", expanded=False):
    st.subheader("Add filing narrative")
    with st.form("upload_filing_form"):
        c1, c2, c3 = st.columns([2, 1, 1])
        company_name = c1.text_input("Company name")
        ticker = c2.text_input("Ticker")
        fiscal_year = c3.number_input("Fiscal year", min_value=1990, max_value=2100, value=2023, step=1)

        section = st.selectbox("Filing section", ["mda", "business_description", "both"])
        uploaded_file = st.file_uploader("Upload filing text (.txt or .md)", type=["txt", "md"])
        pasted_text = st.text_area("Or paste narrative text", height=160)

        cf1, cf2 = st.columns(2)
        total_assets = cf1.number_input("Total assets (optional)", min_value=0.0, value=0.0, step=1_000_000.0)
        roa = cf2.number_input("ROA (optional)", value=0.0, step=0.001, format="%.4f")

        submitted = st.form_submit_button("Add filing year", type="primary")
        if submitted:
            text = pasted_text
            if uploaded_file is not None:
                text = uploaded_file.read().decode("utf-8", errors="ignore")
            if text.strip():
                add_uploaded_filing(company_name, ticker, int(fiscal_year), section, text)
                if total_assets > 0 or roa != 0.0:
                    add_financial(company_name, ticker, int(fiscal_year), total_assets, roa)
                st.success(f"Added {ticker.upper()} {int(fiscal_year)} filing. Head to the Dashboard to see the analysis.")
                st.cache_data.clear()
            else:
                st.warning("Provide text via file upload or paste.")

    st.subheader("Add leadership event")
    with st.form("event_form"):
        ec1, ec2, ec3, ec4 = st.columns([2, 1, 1, 1])
        event_company = ec1.text_input("Company name")
        event_ticker = ec2.text_input("Ticker")
        event_year = ec3.number_input("Fiscal year", min_value=1990, max_value=2100, value=2023, step=1)
        event_date = ec4.date_input("Event date", value=date.today())
        event_description = st.text_area("Event description (leadership change)", height=90)
        event_submitted = st.form_submit_button("Add event", type="primary")
        if event_submitted:
            if event_description.strip():
                add_event(event_company, event_ticker, int(event_year), str(event_date), event_description)
                st.success("Event added and classified.")
                st.cache_data.clear()
            else:
                st.warning("Enter an event description.")
