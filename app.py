import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Corporate Narrative Intelligence Lab",
    layout="wide"
)

st.title("Corporate Narrative Intelligence Lab")
st.caption("Detecting strategic signals from corporate disclosure narratives")

df = pd.read_csv("data/sample_change.csv")

company = st.selectbox("Select company", sorted(df["company"].unique()))
section = st.selectbox("Select filing section", sorted(df["section"].unique()))

filtered = df[(df["company"] == company) & (df["section"] == section)]

st.subheader("Narrative Signal Dashboard")

col1, col2, col3 = st.columns(3)

largest_drop = filtered["similarity_drop"].max()
abnormal_years = filtered[filtered["abnormal_flag"] == True]["year"].tolist()
avg_similarity = filtered["cosine_similarity"].mean()

col1.metric("Largest similarity drop", f"{largest_drop:.2f}")
col2.metric("Average similarity", f"{avg_similarity:.2f}")
col3.metric("Abnormal years", len(abnormal_years))

st.divider()

fig_similarity = px.line(
    filtered,
    x="year",
    y="cosine_similarity",
    markers=True,
    title="Year-over-year textual similarity"
)
st.plotly_chart(fig_similarity, use_container_width=True)

fig_readability = px.line(
    filtered,
    x="year",
    y="fog_index",
    markers=True,
    title="Readability complexity, Fog Index"
)
st.plotly_chart(fig_readability, use_container_width=True)

fig_tone = px.line(
    filtered,
    x="year",
    y="finbert_sentiment",
    markers=True,
    title="Contextual sentiment trend"
)
st.plotly_chart(fig_tone, use_container_width=True)

st.subheader("Flagged narrative shifts")

flagged = filtered[filtered["abnormal_flag"] == True]

if flagged.empty:
    st.success("No abnormal narrative shift detected for this selection.")
else:
    for _, row in flagged.iterrows():
        st.warning(f"Abnormal narrative shift detected in {int(row['year'])}")
        st.write(row["interpretation"])
        st.write(
            f"Similarity drop: {row['similarity_drop']:.2f}, "
            f"Fog Index change: {row['delta_fog_index']:.2f}, "
            f"Topic shift score: {row['topic_shift_score']:.2f}"
        )

st.divider()

st.subheader("Method summary")
st.write(
    """
    This demo uses a hybrid textual analysis approach:
    dictionary tone, contextual sentiment, readability, textual similarity,
    topic shift, and abnormal-change detection.
    """
)