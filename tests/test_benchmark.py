"""Tests for src.evaluation.benchmark — agreement metrics."""

import pandas as pd
import pytest

from src.evaluation.benchmark import (
    compute_benchmark_metrics,
    confusion_matrix,
    exact_agreement,
    mean_absolute_deviation,
    within_one_agreement,
)


def _make_frame(auto: list[int], human: list[int]) -> pd.DataFrame:
    """Build a minimal DataFrame that looks like pipeline output."""
    return pd.DataFrame({
        "auto_score": auto,
        "human_score": human,
        "has_human_score": [True] * len(auto),
    })


class TestExactAgreement:
    def test_perfect(self):
        auto = pd.Series([4, 3, 2, 1])
        human = pd.Series([4, 3, 2, 1])
        assert exact_agreement(auto, human) == 100.0

    def test_zero(self):
        auto = pd.Series([4, 3])
        human = pd.Series([0, 0])
        assert exact_agreement(auto, human) == 0.0

    def test_half(self):
        auto = pd.Series([4, 0])
        human = pd.Series([4, 4])
        assert exact_agreement(auto, human) == 50.0

    def test_empty(self):
        assert exact_agreement(pd.Series([], dtype=int), pd.Series([], dtype=int)) == 0.0


class TestWithinOneAgreement:
    def test_perfect(self):
        auto = pd.Series([4, 3, 2])
        human = pd.Series([4, 3, 2])
        assert within_one_agreement(auto, human) == 100.0

    def test_all_within_one(self):
        auto = pd.Series([4, 3, 2])
        human = pd.Series([3, 4, 1])
        assert within_one_agreement(auto, human) == 100.0

    def test_none_within_one(self):
        auto = pd.Series([0, 0])
        human = pd.Series([4, 4])
        assert within_one_agreement(auto, human) == 0.0

    def test_empty(self):
        assert within_one_agreement(pd.Series([], dtype=int), pd.Series([], dtype=int)) == 0.0


class TestMeanAbsoluteDeviation:
    def test_zero_deviation(self):
        auto = pd.Series([4, 3, 2])
        human = pd.Series([4, 3, 2])
        assert mean_absolute_deviation(auto, human) == 0.0

    def test_constant_deviation(self):
        auto = pd.Series([4, 3, 2])
        human = pd.Series([3, 2, 1])
        assert mean_absolute_deviation(auto, human) == 1.0

    def test_empty(self):
        assert mean_absolute_deviation(pd.Series([], dtype=int), pd.Series([], dtype=int)) == 0.0


class TestConfusionMatrix:
    def test_shape(self):
        auto = pd.Series([4, 3, 2, 1, 0])
        human = pd.Series([4, 3, 2, 1, 0])
        cm = confusion_matrix(auto, human)
        assert isinstance(cm, pd.DataFrame)
        assert cm.shape[0] == 5  # 5 human score levels

    def test_diagonal_for_perfect_agreement(self):
        auto = pd.Series([4, 3, 2])
        human = pd.Series([4, 3, 2])
        cm = confusion_matrix(auto, human)
        for val in [4, 3, 2]:
            assert cm.loc[val, val] == 1


class TestComputeBenchmarkMetrics:
    def test_basic(self):
        frame = _make_frame([4, 3, 2], [4, 3, 2])
        metrics = compute_benchmark_metrics(frame)
        assert metrics["exact_pct"] == 100.0
        assert metrics["within1_pct"] == 100.0
        assert metrics["mad"] == 0.0
        assert metrics["n"] == 3

    def test_empty_frame_returns_empty_dict(self):
        frame = pd.DataFrame({
            "auto_score": [],
            "human_score": [],
            "has_human_score": [],
        })
        metrics = compute_benchmark_metrics(frame)
        assert metrics == {}

    def test_no_human_scores(self):
        frame = pd.DataFrame({
            "auto_score": [4, 3],
            "human_score": [None, None],
            "has_human_score": [False, False],
        })
        metrics = compute_benchmark_metrics(frame)
        assert metrics == {}

    def test_confusion_matrix_present(self):
        frame = _make_frame([4, 3, 2], [4, 3, 2])
        metrics = compute_benchmark_metrics(frame)
        assert isinstance(metrics["confusion_matrix"], pd.DataFrame)
