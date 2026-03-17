"""Pipeline orchestration: load → score → aggregate → write.

The two public functions here cover the common use-cases:
  - run_pipeline: score a workbook, return a DataFrame
  - score_and_export: end-to-end run including file output
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pandas as pd

from autoeit.core.rubric import score_utterance
from autoeit.services.workbook import load_workbook, save_workbook, save_csv_outputs
from autoeit.utils.paths import default_downgrade_path

MetricMap = dict[str, Any]


def run_pipeline(filepath: str | Path) -> pd.DataFrame:
    """Load a workbook and score every utterance row.

    Returns a DataFrame with all original columns plus:
    auto_score, rationale, ambiguous_downgraded, has_human_score,
    and — for rows that have human scores — agreement and score_diff.
    """
    frame = load_workbook(filepath)

    scored_rows: list[tuple[int, str, bool]] = []
    for row in frame.itertuples(index=False):
        result = cast(
            tuple[int, str, bool],
            score_utterance(
                getattr(row, "stimulus"),
                getattr(row, "transcription"),
                return_meta=True,
            ),
        )
        scored_rows.append(result)

    frame["auto_score"] = [row[0] for row in scored_rows]
    frame["rationale"] = [row[1] for row in scored_rows]
    frame["ambiguous_downgraded"] = [row[2] for row in scored_rows]
    frame["has_human_score"] = frame["human_score"].notna()

    rated = frame["has_human_score"]
    if rated.any():
        frame.loc[rated, "agreement"] = (
            frame.loc[rated, "auto_score"] == frame.loc[rated, "human_score"]
        )
        frame.loc[rated, "score_diff"] = (
            frame.loc[rated, "auto_score"] - frame.loc[rated, "human_score"]
        )

    return frame


def summarize_agreement(frame: pd.DataFrame) -> MetricMap:
    """Compute inter-rater agreement metrics for rows that have human scores.

    Returns an empty dict if there are no rated rows.
    """
    rated = frame[frame["has_human_score"]].copy()
    if rated.empty:
        return {}

    n = len(rated)
    exact_pct = float(rated["agreement"].sum()) / n * 100
    within1_pct = float((rated["score_diff"].abs() <= 1).sum()) / n * 100

    auto_totals = rated.groupby("sheet_name")["auto_score"].sum()
    human_totals = rated.groupby("sheet_name")["human_score"].sum()
    deviations = (auto_totals - human_totals).abs()

    return {
        "n_rated": n,
        "exact_agreement_pct": round(exact_pct, 2),
        "within1_agreement_pct": round(within1_pct, 2),
        "mean_participant_deviation": round(float(deviations.mean()), 2),
        "max_participant_deviation": int(deviations.max()),
        "pct_participants_within10": round(float((deviations <= 10).mean() * 100), 2),
        "n_participants": len(deviations),
        "n_ambiguous_downgraded": int(frame["ambiguous_downgraded"].sum()),
        "auto_score_dist": rated["auto_score"].value_counts().sort_index().to_dict(),
        "human_score_dist": rated["human_score"].value_counts().sort_index().to_dict(),
        # TODO: expose as a proper object rather than a raw crosstab
        "confusion_matrix": pd.crosstab(
            rated["human_score"], rated["auto_score"],
            rownames=["Human"], colnames=["Auto"],
        ),
    }


def score_and_export(
    *,
    source_path: str | Path,
    output_xlsx: str | Path,
    output_csv: str | Path,
    downgrades_csv: str | Path | None = None,
) -> tuple[pd.DataFrame, MetricMap, Path, Path, Path]:
    """Run the full pipeline and write all outputs.

    Returns (frame, metrics, xlsx_path, csv_path, downgrades_path).
    """
    frame = run_pipeline(source_path)
    metrics = summarize_agreement(frame)

    xlsx_path = save_workbook(frame, source_path=source_path, out_path=output_xlsx)
    dl_path = downgrades_csv or default_downgrade_path(output_csv)
    csv_path, dl_path = save_csv_outputs(
        frame, scores_path=output_csv, downgrades_path=dl_path
    )
    return frame, metrics, xlsx_path, csv_path, dl_path
