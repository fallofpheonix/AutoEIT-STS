"""End-to-end scoring pipeline for AutoEIT-STS.

Orchestrates text normalization, feature extraction, rubric scoring, and
output writing in a single top-level call (:func:`score_workbook`).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.io import load_dataset, write_csv_outputs, write_output_workbook
from src.rubric import score_utterance


def run_scoring_pipeline(filepath: str | Path) -> pd.DataFrame:
    """Load a workbook and compute auto-scores for every utterance.

    Returns a :class:`~pandas.DataFrame` with columns:
    ``sheet_name``, ``participant_id``, ``version``, ``sentence_id``,
    ``stimulus``, ``transcription``, ``human_score``, ``auto_score``,
    ``rationale``, ``ambiguous_downgraded``, ``has_human_score``,
    ``agreement`` (optional), ``score_diff`` (optional).
    """
    frame = load_dataset(filepath)
    scored = frame.apply(
        lambda row: score_utterance(row["stimulus"], row["transcription"], return_meta=True),
        axis=1,
    )
    frame["auto_score"] = scored.apply(lambda result: result[0])
    frame["rationale"] = scored.apply(lambda result: result[1])
    frame["ambiguous_downgraded"] = scored.apply(lambda result: result[2])
    frame["has_human_score"] = frame["human_score"].notna()
    frame.loc[frame["has_human_score"], "agreement"] = (
        frame.loc[frame["has_human_score"], "auto_score"]
        == frame.loc[frame["has_human_score"], "human_score"]
    )
    frame.loc[frame["has_human_score"], "score_diff"] = (
        frame.loc[frame["has_human_score"], "auto_score"]
        - frame.loc[frame["has_human_score"], "human_score"]
    )
    return frame


def compute_metrics(frame: pd.DataFrame) -> dict[str, object]:
    """Aggregate agreement statistics for rows that have human scores."""
    rated = frame[frame["has_human_score"]].copy()
    if rated.empty:
        return {}
    exact = float(rated["agreement"].sum()) / len(rated) * 100
    within_one = float((rated["score_diff"].abs() <= 1).sum()) / len(rated) * 100
    auto_totals = rated.groupby(["sheet_name"])["auto_score"].sum()
    human_totals = rated.groupby(["sheet_name"])["human_score"].sum()
    deviations = (auto_totals - human_totals).abs()
    return {
        "n_rated_utterances": len(rated),
        "exact_agreement_rate_pct": round(exact, 2),
        "within1_agreement_pct": round(within_one, 2),
        "mean_participant_deviation": round(float(deviations.mean()), 2),
        "max_participant_deviation": int(deviations.max()),
        "pct_participants_within10": round(float((deviations <= 10).mean() * 100), 2),
        "n_participants": int(len(deviations)),
        "n_ambiguous_downgraded": int(frame["ambiguous_downgraded"].sum()),
        "auto_score_distribution": rated["auto_score"].value_counts().sort_index().to_dict(),
        "human_score_distribution": rated["human_score"].value_counts().sort_index().to_dict(),
        "confusion_summary": pd.crosstab(
            rated["human_score"],
            rated["auto_score"],
            rownames=["Human"],
            colnames=["Auto"],
        ),
    }


def score_workbook(
    *,
    source_path: str | Path,
    output_xlsx: str | Path,
    output_csv: str | Path,
    downgrade_csv: str | Path | None = None,
) -> tuple[pd.DataFrame, dict[str, object], Path, Path, Path]:
    """Run the full pipeline and write all outputs.

    Returns
    -------
    ``(frame, metrics, workbook_path, csv_path, downgrade_path)``
    """
    frame = run_scoring_pipeline(source_path)
    metrics = compute_metrics(frame)
    workbook_path = write_output_workbook(frame, source_path=source_path, out_path=output_xlsx)
    downgrade_path = downgrade_csv or Path(output_csv).with_name("AutoEIT_ambiguous_downgrades.csv")
    csv_path, downgrade_path = write_csv_outputs(
        frame,
        output_csv=output_csv,
        downgrade_csv=downgrade_path,
    )
    return frame, metrics, workbook_path, csv_path, downgrade_path
