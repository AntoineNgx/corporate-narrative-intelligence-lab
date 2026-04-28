from __future__ import annotations

import plotly.express as px
import streamlit as st

from state import analysis_frames, initialize_state


st.set_page_config(page_title="Narrative Dashboard", layout="wide")
initialize_state()

st.title("Narrative Dashboard")

filings, metrics, changes, events = analysis_frames()

if filings.empty:
    st.info("Add filing text on the landing page to build the dashboard.")
    st.stop()

ticker = st.selectbox("Company", sorted(filings["ticker"].unique()))
section = st.selectbox("Section", sorted(filings.loc[filings["ticker"] == ticker, "section"].unique()))

company_metrics = metrics[(metrics["ticker"] == ticker) & (metrics["section"] == section)].sort_values("fiscal_year")
company_changes = changes[(changes["ticker"] == ticker) & (changes["section"] == section)].sort_values("fiscal_year")
company_events = events[events["ticker"] == ticker].sort_values("fiscal_year")

summary_cols = st.columns(4)
summary_cols[0].metric("Years analyzed", len(company_metrics))
summary_cols[1].metric("Abnormal alerts", int(company_changes["abnormal_change_flag"].sum()) if not company_changes.empty else 0)
summary_cols[2].metric("Latest topic", company_metrics.iloc[-1]["topic_label"])
summary_cols[3].metric("Leadership events", len(company_events))

chart_cols = st.columns(2)
with chart_cols[0]:
    st.plotly_chart(
        px.line(company_changes, x="fiscal_year", y="cosine_similarity", markers=True, title="Narrative Stability"),
        use_container_width=True,
    )
with chart_cols[1]:
    st.plotly_chart(
        px.line(company_metrics, x="fiscal_year", y="net_tone", markers=True, title="Tone Evolution"),
        use_container_width=True,
    )

chart_cols = st.columns(2)
with chart_cols[0]:
    st.plotly_chart(
        px.line(company_metrics, x="fiscal_year", y="fog_index", markers=True, title="Readability Evolution"),
        use_container_width=True,
    )
with chart_cols[1]:
    st.plotly_chart(
        px.line(company_changes, x="fiscal_year", y="topic_shift_score", markers=True, title="Topic Shift Evolution"),
        use_container_width=True,
    )

st.subheader("Abnormal Change Alerts")
if company_changes.empty:
    st.info("Add at least two years of filing text to compute year-over-year change.")
else:
    alerts = company_changes[company_changes["abnormal_change_flag"]]
    if alerts.empty:
        st.success("No abnormal narrative changes detected for this company and section.")
    else:
        st.dataframe(
            alerts[
                [
                    "fiscal_year",
                    "previous_year",
                    "abnormal_change_score",
                    "similarity_drop",
                    "delta_net_tone",
                    "delta_fog_index",
                    "topic_shift_score",
                    "abnormal_change_reason",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

st.subheader("Event Timeline")
if company_events.empty:
    st.caption("No leadership events added.")
else:
    st.dataframe(
        company_events[
            [
                "event_date",
                "fiscal_year",
                "event_type",
                "turnover_type",
                "successor_origin",
                "event_description",
                "classification_rationale",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )
