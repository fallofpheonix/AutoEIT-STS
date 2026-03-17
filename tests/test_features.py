"""Tests for autoeit.core.features — FeatureBundle and extraction."""

import pytest
from autoeit.core.features import (
    _levenshtein,
    _content_overlap,
    char_similarity,
    morph_close,
    is_ser_estar_swap,
    extract_features,
)


class TestLevenshtein:
    def test_identical(self):
        assert _levenshtein(["a", "b", "c"], ["a", "b", "c"]) == 0

    def test_one_sub(self):
        assert _levenshtein(["a", "b", "c"], ["a", "x", "c"]) == 1

    def test_deletion(self):
        assert _levenshtein(["a", "b", "c"], ["a", "c"]) == 1

    def test_insertion(self):
        assert _levenshtein(["a", "c"], ["a", "b", "c"]) == 1

    def test_both_empty(self):
        assert _levenshtein([], []) == 0

    def test_one_empty(self):
        assert _levenshtein(["x", "y"], []) == 2

    def test_completely_different(self):
        assert _levenshtein(["a", "b"], ["c", "d"]) == 2


class TestContentOverlap:
    def test_full_overlap(self):
        assert _content_overlap(["el", "gato", "negro"], ["el", "gato", "negro"]) == 1.0

    def test_empty_target(self):
        # no content words in target → default to 1.0 (nothing to miss)
        assert _content_overlap([], ["gato"]) == 1.0

    def test_function_words_only(self):
        assert _content_overlap(["el", "la"], ["gato"]) == 1.0

    def test_partial(self):
        # target content: gato, negro, corre; learner hits gato only
        ratio = _content_overlap(
            ["el", "gato", "negro", "corre"],
            ["el", "gato", "blanco", "duerme"],
        )
        assert abs(ratio - 1 / 3) < 1e-9

    def test_zero_overlap(self):
        assert _content_overlap(["gato", "corre"], ["perro", "duerme"]) == 0.0


class TestCharSimilarity:
    def test_identical(self):
        assert char_similarity("gato", "gato") == 1.0

    def test_partial(self):
        s = char_similarity("gato", "dato")
        assert 0.0 < s < 1.0

    def test_empty_strings(self):
        assert char_similarity("", "") == 1.0


class TestMorphClose:
    def test_same_word(self):
        assert morph_close("come", "come") is True

    def test_inflectional_variant(self):
        assert morph_close("habla", "hablo") is True

    def test_unrelated(self):
        assert morph_close("gato", "perro") is False


class TestIsSerEstarSwap:
    def test_ser_to_estar(self):
        assert is_ser_estar_swap(
            ["el", "gato", "es", "negro"],
            ["el", "gato", "esta", "negro"],
        ) is True

    def test_estar_to_ser(self):
        assert is_ser_estar_swap(
            ["el", "gato", "esta", "aqui"],
            ["el", "gato", "es", "aqui"],
        ) is True

    def test_length_mismatch(self):
        assert is_ser_estar_swap(["es"], ["esta", "alli"]) is False

    def test_multiple_diffs(self):
        assert is_ser_estar_swap(
            ["el", "gato", "es", "aqui"],
            ["la", "gata", "esta", "aqui"],
        ) is False

    def test_no_ser_estar(self):
        assert is_ser_estar_swap(["gato", "corre"], ["gato", "salta"]) is False


class TestExtractFeatures:
    def test_exact(self):
        ft = extract_features("El gato corre", "el gato corre")
        assert ft.edit_distance == 0
        assert ft.overlap == 1.0

    def test_empty_learner(self):
        ft = extract_features("El gato corre", "")
        assert ft.edit_distance > 0
        assert ft.learner_count == 0
