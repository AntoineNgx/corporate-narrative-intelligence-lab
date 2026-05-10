from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from state import analysis_frames, initialize_state
from data.loader import DEMO_COMPANIES

st.set_page_config(page_title="NARRATIVE DASHBOARD", layout="wide")

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] a span {
    text-transform: uppercase;}
    .kpi-row { display: flex; gap: 16px; margin-bottom: 8px; }
    .kpi { flex: 1; background: #F0F4F8; border-radius: 8px; padding: 16px 20px; border-left: 3px solid #1D4E89; }
    .kpi .label { font-size: 11px; color: #718096; text-transform: uppercase; letter-spacing: 0.07em; }
    .kpi .value { font-size: 26px; font-weight: 700; color: #0F172A; margin: 4px 0 0; }
    .kpi .delta { font-size: 12px; color: #4A5568; }
    .alert-banner { background: #FFF3CD; border: 1px solid #F59E0B; border-radius: 8px; padding: 12px 16px; margin: 8px 0; }
    .ok-banner    { background: #D1FAE5; border: 1px solid #10B981; border-radius: 8px; padding: 12px 16px; margin: 8px 0; }
    .story-box { background: #EFF6FF; border-left: 4px solid #3B82F6; border-radius: 0 8px 8px 0; padding: 12px 16px; font-size: 14px; color: #1E3A5F; margin-bottom: 16px; }
    </style>
    """,
    unsafe_allow_html=True,
)

initialize_state()

st.title("Narrative Dashboard")
st.caption("Year-over-year disclosure signal analysis · US biopharma 10-K MD&A")

with st.spinner("Running text analysis…"):
    filings, metrics, changes, events = analysis_frames()

if filings.empty:
    st.info("Add filing text on the landing page to build the dashboard.")
    st.stop()

# ── Selectors ──────────────────────────────────────────────────────────────────
sel_col1, sel_col2 = st.columns([2, 1])
ticker = sel_col1.selectbox("Company", sorted(filings["ticker"].unique()))
section = sel_col2.selectbox(
    "Section",
    sorted(filings.loc[filings["ticker"] == ticker, "section"].unique()),
)

company_metrics = metrics[(metrics["ticker"] == ticker) & (metrics["section"] == section)].sort_values("fiscal_year")
company_changes = changes[(changes["ticker"] == ticker) & (changes["section"] == section)].sort_values("fiscal_year")
company_events = events[events["ticker"] == ticker].sort_values("fiscal_year")

# Story context banner
if ticker in DEMO_COMPANIES:
    story = DEMO_COMPANIES[ticker]["story"]
    st.markdown(f'<div class="story-box">📋 <strong>{DEMO_COMPANIES[ticker]["company_name"]}</strong> — {story}</div>', unsafe_allow_html=True)

# ── KPI row ────────────────────────────────────────────────────────────────────
n_alerts = int(company_changes["abnormal_change_flag"].sum()) if not company_changes.empty else 0
latest_tone = company_metrics.iloc[-1]["net_tone"] if not company_metrics.empty else 0
prev_tone = company_metrics.iloc[-2]["net_tone"] if len(company_metrics) >= 2 else latest_tone
tone_delta = latest_tone - prev_tone
latest_fog = company_metrics.iloc[-1]["fog_index"] if not company_metrics.empty else 0
latest_topic = company_metrics.iloc[-1]["topic_label"] if not company_metrics.empty else "—"

k1, k2, k3, k4 = st.columns(4)
k1.metric("Years analyzed", len(company_metrics))
k2.metric("Abnormal alerts", n_alerts)
k3.metric("Latest net tone", f"{latest_tone:+.4f}", f"{tone_delta:+.4f} vs prior year")
k4.metric("Latest Fog index", f"{latest_fog:.1f}", help="Gunning Fog: ≥12 = complex, ≥17 = very complex")

st.divider()

# ── Charts ─────────────────────────────────────────────────────────────────────
CHART_COLOR = "#1D4E89"
ALERT_COLOR = "#F59E0B"

chart_col1, chart_col2 = st.columns(2, gap="large")

with chart_col1:
    if not company_changes.empty:
        fig = go.Figure()
        fig.add_scatter(
            x=company_changes["fiscal_year"],
            y=company_changes["cosine_similarity"],
            mode="lines+markers",
            line=dict(color=CHART_COLOR, width=2.5),
            marker=dict(size=8, color=[
                ALERT_COLOR if f else CHART_COLOR
                for f in company_changes["abnormal_change_flag"]
            ]),
            name="Similarity",
            hovertemplate="FY%{x}: %{y:.3f}<extra></extra>",
        )
        fig.add_hline(y=0.75, line_dash="dot", line_color="#CBD5E0", annotation_text="Stable threshold")
        fig.update_layout(
            title="Narrative Stability (cosine similarity)",
            yaxis_title="Similarity to prior year",
            yaxis_range=[0, 1.05],
            xaxis_title="Fiscal year",
            showlegend=False,
            height=300,
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add ≥ 2 years of data to see stability chart.")

with chart_col2:
    if not company_metrics.empty:
        fig2 = px.bar(
            company_metrics,
            x="fiscal_year",
            y=["lm_positive_ratio", "lm_negative_ratio", "lm_uncertainty_ratio"],
            barmode="group",
            color_discrete_map={
                "lm_positive_ratio": "#10B981",
                "lm_negative_ratio": "#EF4444",
                "lm_uncertainty_ratio": "#F59E0B",
            },
            labels={
                "lm_positive_ratio": "Positive",
                "lm_negative_ratio": "Negative",
                "lm_uncertainty_ratio": "Uncertainty",
                "fiscal_year": "Fiscal year",
                "value": "Ratio",
            },
            title="Tone Composition (LM Dictionary)",
            height=300,
        )
        fig2.update_layout(margin=dict(l=0, r=0, t=40, b=0), legend_title="")
        st.plotly_chart(fig2, use_container_width=True)

chart_col3, chart_col4 = st.columns(2, gap="large")

with chart_col3:
    if not company_metrics.empty:
        fig3 = px.line(
            company_metrics,
            x="fiscal_year",
            y="fog_index",
            markers=True,
            title="Readability — Gunning Fog Index",
            labels={"fog_index": "Fog index", "fiscal_year": "Fiscal year"},
            color_discrete_sequence=[CHART_COLOR],
            height=280,
        )
        fig3.add_hline(y=12, line_dash="dot", line_color="#CBD5E0", annotation_text="Grade 12")
        fig3.update_traces(line_width=2.5, marker_size=8)
        fig3.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig3, use_container_width=True)

with chart_col4:
    if not company_changes.empty:
        fig4 = px.bar(
            company_changes,
            x="fiscal_year",
            y="topic_shift_score",
            title="Topic Shift Score (year-over-year)",
            labels={"topic_shift_score": "Shift score", "fiscal_year": "Fiscal year"},
            color="abnormal_change_flag",
            color_discrete_map={True: ALERT_COLOR, False: CHART_COLOR},
            height=280,
        )
        fig4.update_layout(
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=False,
        )
        st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Abnormal alerts ────────────────────────────────────────────────────────────
st.subheader("Abnormal Change Alerts")
if company_changes.empty:
    st.info("Add at least two years of filing text to compute year-over-year signals.")
else:
    alerts = company_changes[company_changes["abnormal_change_flag"]]
    if alerts.empty:
        st.success("No abnormal narrative changes detected.")
    else:
        st.warning(f"{len(alerts)} year{'s' if len(alerts) > 1 else ''} flagged as abnormal. Click **Signal Detail** in the sidebar to drill down.")
        st.dataframe(
            alerts[[
                "fiscal_year", "previous_year", "abnormal_change_score",
                "similarity_drop", "delta_net_tone", "delta_fog_index",
                "topic_shift_score", "has_leadership_event", "abnormal_change_reason",
            ]].rename(columns={
                "fiscal_year": "Year",
                "previous_year": "vs. Prior",
                "abnormal_change_score": "Score",
                "similarity_drop": "Sim. Drop",
                "delta_net_tone": "ΔTone",
                "delta_fog_index": "ΔFog",
                "topic_shift_score": "Topic Shift",
                "has_leadership_event": "Leadership Event",
                "abnormal_change_reason": "Reason",
            }),
            use_container_width=True,
            hide_index=True,
        )

# ── Full metrics table ────────────────────────────────────────────────────────
with st.expander("Full textual metrics by year"):
    if not company_metrics.empty:
        display_cols = ["fiscal_year", "word_count", "net_tone", "lm_positive_ratio",
                        "lm_negative_ratio", "lm_uncertainty_ratio", "fog_index", "topic_label"]
        st.dataframe(
            company_metrics[display_cols].rename(columns={
                "fiscal_year": "Year", "word_count": "Words", "net_tone": "Net Tone",
                "lm_positive_ratio": "Positive", "lm_negative_ratio": "Negative",
                "lm_uncertainty_ratio": "Uncertainty", "fog_index": "Fog Index",
                "topic_label": "Topic",
            }),
            use_container_width=True,
            hide_index=True,
        )

# ── Event timeline ────────────────────────────────────────────────────────────
if not company_events.empty:
    st.subheader("Leadership Event Timeline")
    st.dataframe(
        company_events[[
            "event_date", "fiscal_year", "event_type", "turnover_type",
            "successor_origin", "event_description", "classification_rationale",
        ]],
        use_container_width=True,
        hide_index=True,
    )
