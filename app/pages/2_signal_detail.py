from __future__ import annotations

from pathlib import Path

from jinja2 import Template
import streamlit as st

from state import ROOT, analysis_frames, initialize_state


st.set_page_config(page_title="SIGNAL DETAIL", layout="wide")
initialize_state()

st.title("SIGNAL DETAIL")

_, _, changes, events = analysis_frames()

if changes.empty:
    st.info("Add at least two years of filing text to inspect narrative changes.")
    st.stop()

display = changes.sort_values(["ticker", "section", "fiscal_year"])
choice_labels = [
    f"{row.ticker} | {row.section} | {row.previous_year} -> {row.fiscal_year}"
    for row in display.itertuples()
]
selected_label = st.selectbox("Narrative change", choice_labels)
row = display.iloc[choice_labels.index(selected_label)].to_dict()

metrics = st.columns(5)
metrics[0].metric("Similarity", f"{row['cosine_similarity']:.2f}")
metrics[1].metric("Similarity drop", f"{row['similarity_drop']:.2f}")
metrics[2].metric("Tone delta", f"{row['delta_net_tone']:.3f}")
metrics[3].metric("Fog delta", f"{row['delta_fog_index']:.1f}")
metrics[4].metric("Topic shift", f"{row['topic_shift_score']:.2f}")

if row["abnormal_change_flag"]:
    st.error(row["abnormal_change_reason"])
else:
    st.success(row["abnormal_change_reason"])

before, after = st.columns(2)
with before:
    st.subheader(f"Before: {row['previous_year']}")
    st.write(row["previous_excerpt"])
with after:
    st.subheader(f"After: {row['fiscal_year']}")
    st.write(row["current_excerpt"])

st.subheader("Likely Interpretation")
interpretation = (
    "The filing shows an abnormal narrative pattern. Review whether this aligns with leadership transition, "
    "financial pressure, portfolio restructuring, or strategic repositioning."
    if row["abnormal_change_flag"]
    else "The filing appears broadly stable versus the prior year, with no combined narrative signal crossing the alert threshold."
)
st.write(interpretation)

linked_events = events[(events["ticker"] == row["ticker"]) & (events["fiscal_year"] == row["fiscal_year"])]
st.subheader("Linked Leadership or Financial Event")
if linked_events.empty:
    st.caption("No leadership event linked to this fiscal year.")
else:
    st.dataframe(linked_events, use_container_width=True, hide_index=True)

template_path = ROOT / "reports" / "sample_report_template.html"
template = Template(template_path.read_text())
report_html = template.render(signal=row, interpretation=interpretation, events=linked_events.to_dict("records"))
st.download_button(
    "Export HTML report",
    data=report_html,
    file_name=f"{row['ticker']}_{row['fiscal_year']}_narrative_signal.html",
    mime="text/html",
)

report_dir = Path(ROOT / "reports" / "generated")
report_dir.mkdir(exist_ok=True)
(report_dir / f"{row['ticker']}_{row['fiscal_year']}_narrative_signal.html").write_text(report_html)
