"""Streamlit researcher interface for AutoEIT-STS.

Run with:
    streamlit run autoeit/api/app.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd

try:
    import streamlit as st
except ImportError:  # pragma: no cover
    raise SystemExit(
        "Streamlit is not installed.\n"
        "Run: pip install streamlit"
    )

from autoeit.services.scoring import run_pipeline, summarize_agreement

st.set_page_config(
    page_title="AutoEIT-STS",
    page_icon="🔬",
    layout="wide",
)

st.title("AutoEIT-STS — Researcher Scoring Interface")
st.caption(
    "Deterministic scorer for the Spanish Elicited Imitation Task. "
    "Scores are rule-based and fully reproducible."
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Upload Workbook")
    uploaded = st.file_uploader(
        "Choose a .xlsx transcription workbook",
        type=["xlsx"],
    )
    st.divider()
    st.markdown(
        "**Pipeline**\n"
        "1. Normalize text\n"
        "2. Extract features\n"
        "3. Apply rubric\n"
        "4. Generate rationale"
    )

if uploaded is None:
    st.info("Upload a workbook using the sidebar to get started.")
    st.stop()

# ---------------------------------------------------------------------------
# Scoring (cached by file content hash via tmp path)
# ---------------------------------------------------------------------------

@st.cache_data
def _score(path: str) -> pd.DataFrame:
    return run_pipeline(path)


with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
    tmp.write(uploaded.getbuffer())
    tmp_path = tmp.name

try:
    with st.spinner("Scoring…"):
        try:
            frame = _score(tmp_path)
        except ValueError as exc:
            st.error(str(exc))
            st.stop()
except Exception as exc:  # noqa: BLE001
    st.error(f"Unexpected error: {exc}")
    st.stop()

metrics = summarize_agreement(frame)

# ---------------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------------

if metrics:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Exact agreement", f"{metrics['exact_agreement_pct']:.1f}%")
    c2.metric("Within-1 agreement", f"{metrics['within1_agreement_pct']:.1f}%")
    c3.metric("Rated utterances", metrics["n_rated"])
    c4.metric("Ambiguous downgrades", metrics["n_ambiguous_downgraded"])

st.divider()

# ---------------------------------------------------------------------------
# Participant filter
# ---------------------------------------------------------------------------

participants = sorted(frame["participant_id"].unique())
selected = st.multiselect("Filter by participant", participants, default=participants)
view = frame[frame["participant_id"].isin(selected)]

# ---------------------------------------------------------------------------
# Results table
# ---------------------------------------------------------------------------

display_cols = [
    "participant_id", "version", "sentence_id",
    "stimulus", "transcription", "auto_score", "rationale",
]
if "human_score" in view.columns and view["has_human_score"].any():
    display_cols.insert(6, "human_score")

st.dataframe(view[display_cols], use_container_width=True, height=500)

# ---------------------------------------------------------------------------
# Score distribution
# ---------------------------------------------------------------------------

with st.expander("Score distribution"):
    dist = view["auto_score"].value_counts().sort_index().reset_index()
    dist.columns = ["Score", "Count"]
    st.bar_chart(dist.set_index("Score"))

# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

st.divider()
csv_bytes = view.to_csv(index=False).encode()
st.download_button("Download scores as CSV", csv_bytes, file_name="autoeit_scores.csv", mime="text/csv")
