"""Local researcher interface for AutoEIT-STS (Streamlit).

Usage::

    streamlit run src/ui.py

Capabilities:
- Upload a transcription workbook
- View sentence-level scoring with rationales
- Filter by participant
- Inspect score distribution
- Download scored outputs
"""

from __future__ import annotations

import io
import tempfile
from pathlib import Path

import pandas as pd

try:
    import streamlit as st
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Streamlit is required to run the researcher UI.\n"
        "Install it with: pip install streamlit"
    ) from exc

from src.pipeline import run_scoring_pipeline, compute_metrics

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AutoEIT-STS Researcher Interface",
    page_icon="🔬",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🔬 AutoEIT-STS — Researcher Scoring Interface")
st.caption(
    "Deterministic scorer for the Spanish Elicited Imitation Task. "
    "All scores are rule-based and fully reproducible."
)

# ---------------------------------------------------------------------------
# Sidebar — Upload
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Upload Workbook")
    uploaded = st.file_uploader(
        "Choose an `.xlsx` transcription workbook",
        type=["xlsx"],
        help="The workbook must contain sheets with 'Sentence' and 'Stimulus' headers.",
    )
    st.divider()
    st.info(
        "**Pipeline:**\n"
        "1. Normalize text\n"
        "2. Extract features\n"
        "3. Apply rubric rules\n"
        "4. Produce rationale"
    )

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

if uploaded is None:
    st.info("👈 Upload a workbook using the sidebar to get started.")
    st.stop()

# --- Save to a temp file so pipeline can open it with openpyxl ---------------
with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
    tmp.write(uploaded.read())
    tmp_path = Path(tmp.name)

# --- Run pipeline ------------------------------------------------------------
with st.spinner("Scoring utterances…"):
    try:
        frame = run_scoring_pipeline(tmp_path)
    except ValueError as exc:
        st.error(f"Could not process workbook: {exc}")
        st.stop()

metrics = compute_metrics(frame)

# ---------------------------------------------------------------------------
# Metrics banner
# ---------------------------------------------------------------------------

if metrics:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rated utterances", metrics["n_rated_utterances"])
    col2.metric("Exact agreement", f"{metrics['exact_agreement_rate_pct']:.1f} %")
    col3.metric("Within-1 agreement", f"{metrics['within1_agreement_pct']:.1f} %")
    col4.metric("Ambiguous downgrades", metrics["n_ambiguous_downgraded"])
else:
    st.info("No human scores found in this workbook — agreement metrics are unavailable.")

st.divider()

# ---------------------------------------------------------------------------
# Participant filter
# ---------------------------------------------------------------------------

participants = sorted(frame["participant_id"].unique().tolist())
selected = st.multiselect(
    "Filter by participant",
    options=participants,
    default=participants,
    help="Select one or more participants to display.",
)

filtered = frame[frame["participant_id"].isin(selected)] if selected else frame

# ---------------------------------------------------------------------------
# Score distribution
# ---------------------------------------------------------------------------

with st.expander("📊 Score distribution", expanded=False):
    dist = (
        filtered["auto_score"]
        .value_counts()
        .sort_index()
        .rename_axis("Score")
        .reset_index(name="Count")
    )
    st.bar_chart(dist.set_index("Score"))

# ---------------------------------------------------------------------------
# Sentence-level table
# ---------------------------------------------------------------------------

st.subheader("Sentence-level scores")

display_cols = [
    "sheet_name", "participant_id", "sentence_id",
    "stimulus", "transcription",
    "auto_score", "rationale",
]
if "human_score" in filtered.columns and filtered["has_human_score"].any():
    display_cols.insert(5, "human_score")

st.dataframe(
    filtered[display_cols].rename(columns={
        "sheet_name": "Sheet",
        "participant_id": "Participant",
        "sentence_id": "#",
        "stimulus": "Stimulus",
        "transcription": "Transcription",
        "human_score": "Human Score",
        "auto_score": "AutoEIT Score",
        "rationale": "Rationale",
    }),
    use_container_width=True,
    height=500,
)

# ---------------------------------------------------------------------------
# Rationale inspector
# ---------------------------------------------------------------------------

st.subheader("🔍 Rationale inspector")
sentence_ids = filtered["sentence_id"].tolist()
sheet_names = filtered["sheet_name"].tolist()
labels = [f"{sn} — #{sid}" for sn, sid in zip(sheet_names, sentence_ids)]

if labels:
    selected_label = st.selectbox("Select an utterance to inspect", labels)
    idx = labels.index(selected_label)
    row = filtered.iloc[idx]

    c1, c2 = st.columns(2)
    c1.markdown(f"**Stimulus:** {row['stimulus']}")
    c1.markdown(f"**Transcription:** {row['transcription']}")
    c2.markdown(f"**AutoEIT Score:** `{int(row['auto_score'])}`")
    c2.markdown(f"**Rationale:** {row['rationale']}")
    if pd.notna(row.get("human_score")):
        c2.markdown(f"**Human Score:** `{int(row['human_score'])}`")

# ---------------------------------------------------------------------------
# Downloads
# ---------------------------------------------------------------------------

st.divider()
st.subheader("⬇️ Download scored output")

csv_buffer = io.StringIO()
frame[
    [
        "sheet_name", "participant_id", "version", "sentence_id",
        "stimulus", "transcription", "human_score", "auto_score",
        "ambiguous_downgraded", "rationale",
    ]
].to_csv(csv_buffer, index=False)

st.download_button(
    label="Download scores as CSV",
    data=csv_buffer.getvalue(),
    file_name="AutoEIT_scores.csv",
    mime="text/csv",
)
