"""Benchmark module for AutoEIT-STS evaluation.

Computes agreement statistics between AutoEIT automatic scores and human
scores stored in a transcription workbook, then checks them against
configurable pass thresholds.

Usage::

    python -m src.evaluation.benchmark \\
        --input-xlsx input/workbooks/AutoEIT\\ Sample\\ Transcriptions\\ for\\ Scoring.xlsx

Exit codes
----------
0 — all thresholds passed
1 — one or more thresholds not met
2 — no human-scored rows found (nothing to evaluate)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from src.pipeline import run_scoring_pipeline

# ---------------------------------------------------------------------------
# Default pass thresholds (can be overridden on the command line)
# ---------------------------------------------------------------------------

DEFAULT_EXACT_THRESHOLD: float = 50.0
"""Minimum acceptable exact-agreement rate (%)."""

DEFAULT_WITHIN1_THRESHOLD: float = 80.0
"""Minimum acceptable within-1 agreement rate (%)."""

DEFAULT_MAD_THRESHOLD: float = 1.5
"""Maximum acceptable mean absolute deviation."""


# ---------------------------------------------------------------------------
# Core metrics
# ---------------------------------------------------------------------------


def exact_agreement(auto: pd.Series, human: pd.Series) -> float:
    """Return exact agreement rate as a percentage (0–100)."""
    if len(auto) == 0:
        return 0.0
    return float((auto == human).sum()) / len(auto) * 100


def within_one_agreement(auto: pd.Series, human: pd.Series) -> float:
    """Return within-1 agreement rate as a percentage (0–100)."""
    if len(auto) == 0:
        return 0.0
    return float(((auto - human).abs() <= 1).sum()) / len(auto) * 100


def mean_absolute_deviation(auto: pd.Series, human: pd.Series) -> float:
    """Return mean absolute deviation between auto and human scores."""
    if len(auto) == 0:
        return 0.0
    return float((auto - human).abs().mean())


def confusion_matrix(auto: pd.Series, human: pd.Series) -> pd.DataFrame:
    """Return a cross-tabulation of human vs. auto scores."""
    return pd.crosstab(
        human.astype(int),
        auto.astype(int),
        rownames=["Human"],
        colnames=["Auto"],
    )


def compute_benchmark_metrics(frame: pd.DataFrame) -> dict[str, object]:
    """Compute all benchmark metrics from a scored DataFrame.

    Parameters
    ----------
    frame:
        Output of :func:`src.pipeline.run_scoring_pipeline`.  Must contain
        ``auto_score``, ``human_score``, and ``has_human_score`` columns.

    Returns
    -------
    dict
        Keys: ``n``, ``exact_pct``, ``within1_pct``, ``mad``,
        ``confusion_matrix``.
    """
    rated = frame[frame["has_human_score"]].copy()
    if rated.empty:
        return {}
    auto = rated["auto_score"].astype(int)
    human = rated["human_score"].astype(int)
    return {
        "n": len(rated),
        "exact_pct": round(exact_agreement(auto, human), 2),
        "within1_pct": round(within_one_agreement(auto, human), 2),
        "mad": round(mean_absolute_deviation(auto, human), 4),
        "confusion_matrix": confusion_matrix(auto, human),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AutoEIT-STS evaluation benchmark",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input-xlsx",
        type=Path,
        required=True,
        help="Path to a transcription workbook containing human scores to evaluate against.",
    )
    parser.add_argument(
        "--exact-threshold",
        type=float,
        default=DEFAULT_EXACT_THRESHOLD,
        metavar="PCT",
        help="Minimum exact-agreement %% to pass.",
    )
    parser.add_argument(
        "--within1-threshold",
        type=float,
        default=DEFAULT_WITHIN1_THRESHOLD,
        metavar="PCT",
        help="Minimum within-1 agreement %% to pass.",
    )
    parser.add_argument(
        "--mad-threshold",
        type=float,
        default=DEFAULT_MAD_THRESHOLD,
        metavar="VAL",
        help="Maximum mean absolute deviation to pass.",
    )
    return parser


def run_benchmark(
    input_xlsx: Path,
    exact_threshold: float = DEFAULT_EXACT_THRESHOLD,
    within1_threshold: float = DEFAULT_WITHIN1_THRESHOLD,
    mad_threshold: float = DEFAULT_MAD_THRESHOLD,
) -> int:
    """Run the full benchmark and print results.

    Returns
    -------
    int
        Exit code: 0 = pass, 1 = threshold(s) not met, 2 = no data.
    """
    frame = run_scoring_pipeline(input_xlsx)
    metrics = compute_benchmark_metrics(frame)

    if not metrics:
        print("ERROR: No human-scored rows found in the workbook.", file=sys.stderr)
        return 2

    print(f"{'=' * 60}")
    print(f"AutoEIT-STS Benchmark  |  n={metrics['n']} rated utterances")
    print(f"{'=' * 60}")
    print(f"  Exact agreement    : {metrics['exact_pct']:.2f} % "
          f"(threshold ≥ {exact_threshold:.1f} %)")
    print(f"  Within-1 agreement : {metrics['within1_pct']:.2f} % "
          f"(threshold ≥ {within1_threshold:.1f} %)")
    print(f"  Mean abs. deviation: {metrics['mad']:.4f} "
          f"(threshold ≤ {mad_threshold:.2f})")
    print(f"\nConfusion matrix (rows=Human, cols=Auto):")
    print(metrics["confusion_matrix"].to_string())
    print()

    failures: list[str] = []
    if metrics["exact_pct"] < exact_threshold:
        failures.append(
            f"  ✗ Exact agreement {metrics['exact_pct']:.2f}% < {exact_threshold:.1f}%"
        )
    if metrics["within1_pct"] < within1_threshold:
        failures.append(
            f"  ✗ Within-1 agreement {metrics['within1_pct']:.2f}% < {within1_threshold:.1f}%"
        )
    if metrics["mad"] > mad_threshold:
        failures.append(
            f"  ✗ MAD {metrics['mad']:.4f} > {mad_threshold:.2f}"
        )

    if failures:
        print("BENCHMARK FAILED:")
        for msg in failures:
            print(msg)
        return 1

    print("BENCHMARK PASSED ✓")
    return 0


def main() -> int:
    args = build_parser().parse_args()
    return run_benchmark(
        input_xlsx=args.input_xlsx,
        exact_threshold=args.exact_threshold,
        within1_threshold=args.within1_threshold,
        mad_threshold=args.mad_threshold,
    )


if __name__ == "__main__":
    raise SystemExit(main())
