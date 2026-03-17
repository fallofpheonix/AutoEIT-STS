"""Tests for autoeit.core.rubric — scoring decision tree.

Focused on the critical paths: gate checks, score-4 boundary, score-3
edge cases, and the ambiguous-boundary downgrade logic.
"""

import pytest
from autoeit.core.rubric import score_utterance
from autoeit.config.settings import RubricSettings


class TestGateChecks:
    def test_empty_string(self):
        score, _ = score_utterance("El gato corre", "")
        assert score == 0

    def test_none_transcription(self):
        score, _ = score_utterance("El gato corre", None)  # type: ignore[arg-type]
        assert score == 0

    def test_bracket_only(self):
        score, _ = score_utterance("El gato corre", "[unintelligible]")
        assert score == 0

    def test_english_flag(self):
        score, rationale = score_utterance("El gato corre", "en ingles")
        assert score == 0
        assert "English" in rationale

    def test_empty_stimulus(self):
        score, _ = score_utterance("", "el gato corre")
        assert score == 0


class TestScore4:
    def test_exact_match(self):
        s = "El gato negro corre rápido"
        score, rationale = score_utterance(s, s)
        assert score == 4
        assert "Exact" in rationale

    def test_accent_normalization(self):
        score, _ = score_utterance("El niño corre", "el nino corre")
        assert score == 4

    def test_single_token_deviation_high_overlap(self):
        score, _ = score_utterance(
            "El gato negro corre rapido fuerte",
            "El gato negro salta rapido fuerte",
        )
        assert score == 4


class TestScore3:
    def test_morphological_variant(self):
        score, _ = score_utterance(
            "El nino habla con su mama",
            "El nino hablo con su mama",
        )
        assert score == 3

    def test_ser_estar_short_sentence(self):
        # Short enough that overlap might not guarantee score 4
        score, rationale = score_utterance("es negro", "esta negro")
        assert score in (3, 4)
        assert isinstance(rationale, str)


class TestScore2:
    def test_partial_content(self):
        score, _ = score_utterance(
            "La profesora habla mucho durante la clase todos los dias",
            "la profesora habla",
        )
        assert score in (1, 2)


class TestScore0:
    def test_no_overlap(self):
        score, _ = score_utterance("El gato corre rapido", "perro duerme tranquilo noche")
        assert score in (0, 1)


class TestAmbiguousBoundary:
    def test_conservative_setting_downgrades(self):
        # Not testing exact thresholds — testing that the meta flag works
        conservative = RubricSettings(conservative_boundary=True)
        permissive = RubricSettings(conservative_boundary=False)

        stim = "El nino habla muy bien con todos durante la clase"
        # 3-word deviation with mid-range overlap — likely to hit boundary zone
        resp = "El nino habla con todos durante"

        score_c, _, downgraded_c = score_utterance(stim, resp, cfg=conservative, return_meta=True)
        score_p, _, downgraded_p = score_utterance(stim, resp, cfg=permissive, return_meta=True)

        # The conservative scorer should either downgrade or return the same score;
        # never return a higher score than permissive for the same input
        assert score_c <= score_p or not downgraded_c

    def test_return_meta_false_gives_two_tuple(self):
        result = score_utterance("El gato corre", "el gato corre")
        assert len(result) == 2

    def test_return_meta_true_gives_three_tuple(self):
        result = score_utterance("El gato corre", "el gato corre", return_meta=True)
        assert len(result) == 3
        assert isinstance(result[2], bool)
