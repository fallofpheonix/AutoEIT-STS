"""Tests for src.features — FeatureBundle and extraction metrics."""

import pytest

from src.features import (
    FeatureBundle,
    char_similarity,
    content_overlap_ratio,
    extract_features,
    morph_close,
    only_ser_estar_swap,
    token_edit_distance,
)


class TestTokenEditDistance:
    def test_identical_sequences(self):
        assert token_edit_distance(["a", "b", "c"], ["a", "b", "c"]) == 0

    def test_one_substitution(self):
        assert token_edit_distance(["a", "b", "c"], ["a", "x", "c"]) == 1

    def test_one_deletion(self):
        assert token_edit_distance(["a", "b", "c"], ["a", "c"]) == 1

    def test_one_insertion(self):
        assert token_edit_distance(["a", "c"], ["a", "b", "c"]) == 1

    def test_empty_sequences(self):
        assert token_edit_distance([], []) == 0

    def test_one_empty(self):
        assert token_edit_distance(["a", "b"], []) == 2
        assert token_edit_distance([], ["a", "b"]) == 2

    def test_completely_different(self):
        assert token_edit_distance(["a", "b"], ["c", "d"]) == 2


class TestContentOverlapRatio:
    def test_full_overlap(self):
        target = ["el", "gato", "negro"]
        learner = ["el", "gato", "negro"]
        assert content_overlap_ratio(target, learner) == 1.0

    def test_empty_target(self):
        assert content_overlap_ratio([], ["gato"]) == 1.0

    def test_no_content_words_in_target(self):
        # only function words — treated as full overlap
        assert content_overlap_ratio(["el", "la"], ["gato"]) == 1.0

    def test_partial_overlap(self):
        target = ["el", "gato", "negro", "corre"]
        learner = ["el", "gato", "blanco", "duerme"]
        # content words in target: gato, negro, corre (3)
        # learner content words: gato, blanco, duerme
        # matched: gato (1 out of 3)
        ratio = content_overlap_ratio(target, learner)
        assert abs(ratio - 1 / 3) < 1e-9

    def test_zero_overlap(self):
        target = ["gato", "corre"]
        learner = ["perro", "duerme"]
        assert content_overlap_ratio(target, learner) == 0.0


class TestCharSimilarity:
    def test_identical(self):
        assert char_similarity("gato", "gato") == 1.0

    def test_one_char_diff(self):
        sim = char_similarity("gato", "dato")
        assert 0.0 < sim < 1.0

    def test_completely_different(self):
        assert char_similarity("abc", "xyz") < 0.5


class TestMorphClose:
    def test_same_word(self):
        assert morph_close("come", "come") is True

    def test_morphological_variant(self):
        # "comiendo" vs "comiendo" — identical
        assert morph_close("comiendo", "comiendo") is True

    def test_close_variant(self):
        # "habla" vs "habló" — similar but not identical
        assert morph_close("habla", "hablo") is True

    def test_unrelated_words(self):
        assert morph_close("gato", "perro") is False


class TestOnlySerEstarSwap:
    def test_ser_to_estar(self):
        assert only_ser_estar_swap(["el", "gato", "es", "negro"],
                                   ["el", "gato", "esta", "negro"]) is True

    def test_estar_to_ser(self):
        assert only_ser_estar_swap(["ella", "esta", "aqui"],
                                   ["ella", "es", "aqui"]) is True

    def test_no_swap(self):
        assert only_ser_estar_swap(["el", "gato", "corre"],
                                   ["el", "gato", "duerme"]) is False

    def test_different_lengths(self):
        assert only_ser_estar_swap(["el", "gato"],
                                   ["el", "gato", "es"]) is False

    def test_multiple_differences(self):
        assert only_ser_estar_swap(["el", "es", "bueno"],
                                   ["la", "esta", "mala"]) is False


class TestExtractFeatures:
    def test_returns_feature_bundle(self):
        bundle = extract_features("El gato corre rápido", "el gato corre rapido")
        assert isinstance(bundle, FeatureBundle)

    def test_identical_returns_zero_edit_distance(self):
        bundle = extract_features("El gato corre", "El gato corre")
        assert bundle.edit_distance == 0

    def test_token_counts(self):
        bundle = extract_features("El gato corre rapido", "el gato corre")
        assert bundle.target_count == 4
        assert bundle.learner_count == 3

    def test_feature_bundle_is_frozen(self):
        bundle = extract_features("El gato", "El gato")
        with pytest.raises((AttributeError, TypeError)):
            bundle.edit_distance = 99  # type: ignore[misc]

    def test_overlap_perfect(self):
        bundle = extract_features("El gato negro", "El gato negro")
        assert bundle.overlap == 1.0
