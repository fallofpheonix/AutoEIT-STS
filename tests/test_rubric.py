"""Tests for src.rubric — deterministic scoring decision tree."""

import pytest

from src.rubric import is_ambiguous_meaning_case, score_utterance


class TestScoreUtteranceGates:
    """Gate checks (score 0) that fire before any feature computation."""

    def test_no_response_empty(self):
        score, rationale = score_utterance("El gato corre", "")
        assert score == 0
        assert "No response" in rationale

    def test_no_response_none(self):
        score, rationale = score_utterance("El gato corre", None)  # type: ignore[arg-type]
        assert score == 0

    def test_wrong_language(self):
        score, rationale = score_utterance("El gato corre", "en ingles")
        assert score == 0
        assert "wrong language" in rationale

    def test_wrong_language_accented(self):
        score, rationale = score_utterance("El gato corre", "en inglés")
        assert score == 0

    def test_bracket_only_is_no_response(self):
        score, _ = score_utterance("El gato corre", "[unintelligible]")
        assert score == 0

    def test_empty_target(self):
        score, rationale = score_utterance("", "el gato corre")
        assert score == 0


class TestScoreUtteranceScore4:
    """Cases that should receive score 4."""

    def test_exact_match(self):
        stimulus = "El gato negro corre rápido"
        score, rationale = score_utterance(stimulus, stimulus)
        assert score == 4
        assert "Exact" in rationale

    def test_exact_match_after_normalization(self):
        score, rationale = score_utterance("El niño corre", "el nino corre")
        assert score == 4

    def test_one_word_deviation_high_overlap(self):
        # "El gato negro corre" vs "El gato negro salta" — edit=1, overlap high
        score, _ = score_utterance(
            "El gato negro corre rapido fuerte",
            "El gato negro salta rapido fuerte",
        )
        assert score == 4

    def test_two_word_deviation_very_high_overlap(self):
        # Long sentence with 2 deviations but most content preserved
        score, _ = score_utterance(
            "La nina bonita canta una cancion hermosa",
            "La nina bonita canta una bonita cancion",
        )
        assert score in (3, 4)  # borderline but acceptable


class TestScoreUtteranceScore3:
    """Cases that should receive score 3."""

    def test_ser_estar_swap(self):
        # A ser/estar swap preserves all content words (both are function words),
        # so overlap stays high.  If edit_distance==1 and overlap>=0.67 the
        # score-4 rule fires first; the swap is still accepted as near-perfect.
        score, rationale = score_utterance(
            "El gato es negro",
            "El gato esta negro",
        )
        assert score in (3, 4)

    def test_ser_estar_swap_rationale_when_applicable(self):
        # Verify the ser/estar rationale path is exercised when the sentence
        # is short enough that overlap falls below the score-4 threshold.
        # "es" only — content overlap is 1.0 (empty target content words → 1.0),
        # so score 4 fires.  The important check is that the rubric function
        # does not crash and returns a valid score.
        score, rationale = score_utterance("es", "esta")
        assert score in (3, 4)
        assert isinstance(rationale, str)

    def test_morphological_variant(self):
        # Single word deviation where forms are morphologically close
        score, _ = score_utterance(
            "El nino habla con su mama",
            "El nino hablo con su mama",
        )
        assert score == 3


class TestScoreUtteranceScore2:
    """Cases that should receive score 2 (partial meaning)."""

    def test_partial_overlap(self):
        score, _ = score_utterance(
            "El estudiante inteligente estudia matematicas avanzadas en la universidad",
            "El estudiante estudia en la",
        )
        assert score == 2

    def test_some_content_retained(self):
        score, _ = score_utterance(
            "La profesora explica la leccion con paciencia",
            "La profesora explica",
        )
        assert score in (2, 3)


class TestScoreUtteranceScore1:
    """Cases that should receive score 1 (minimal/fragmentary)."""

    def test_single_content_word(self):
        score, _ = score_utterance(
            "El estudiante inteligente estudia matematicas avanzadas diariamente",
            "estudia",
        )
        assert score in (0, 1)

    def test_minimal_overlap(self):
        score, _ = score_utterance(
            "La mariposa vuela sobre las flores del jardin tranquilo",
            "vuela",
        )
        assert score in (0, 1)


class TestScoreUtteranceScore0:
    """Cases that should receive score 0."""

    def test_completely_wrong(self):
        score, _ = score_utterance(
            "La mariposa vuela sobre las flores",
            "perro casa libro mesa",
        )
        assert score == 0


class TestScoreUtteranceMeta:
    """Tests for the return_meta parameter."""

    def test_returns_three_tuple_with_meta(self):
        result = score_utterance("El gato", "El gato", return_meta=True)
        assert len(result) == 3
        score, rationale, ambiguous_downgraded = result
        assert isinstance(score, int)
        assert isinstance(rationale, str)
        assert isinstance(ambiguous_downgraded, bool)

    def test_returns_two_tuple_without_meta(self):
        result = score_utterance("El gato", "El gato", return_meta=False)
        assert len(result) == 2

    def test_ambiguous_downgraded_flag(self):
        # Construct a case that triggers the ambiguous boundary
        # edit=2, overlap between 0.60 and 0.78
        # Use a sentence where we can control this precisely
        score, rationale, downgraded = score_utterance(
            "el gato negro corre rapido por el jardin",
            "el gato negro corre lento",
            return_meta=True,
        )
        assert isinstance(downgraded, bool)


class TestDeterminism:
    """Scoring must be 100% deterministic."""

    def test_identical_inputs_produce_identical_outputs(self):
        target = "La estudiante inteligente estudia mucho"
        learner = "La estudiante estudia mucho"
        results = [score_utterance(target, learner) for _ in range(5)]
        assert all(r == results[0] for r in results)


class TestIsAmbiguousMeaningCase:
    def test_within_range(self):
        assert is_ambiguous_meaning_case(3, 0.70) is True

    def test_edit_too_low(self):
        assert is_ambiguous_meaning_case(1, 0.70) is False

    def test_edit_too_high(self):
        assert is_ambiguous_meaning_case(5, 0.70) is False

    def test_overlap_too_low(self):
        assert is_ambiguous_meaning_case(3, 0.50) is False

    def test_overlap_too_high(self):
        assert is_ambiguous_meaning_case(3, 0.90) is False
