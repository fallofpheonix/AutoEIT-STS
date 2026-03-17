"""Tests for autoeit.core.text — normalization and helpers."""

import pytest
from autoeit.core.text import (
    normalize,
    tokenize,
    content_words,
    is_empty_response,
    is_english_response,
)


class TestNormalize:
    def test_strips_accents(self):
        assert normalize("niño") == "nino"
        assert normalize("está") == "esta"

    def test_removes_punctuation(self):
        assert normalize("¿Cómo estás?") == "como estas"

    def test_stimulus_removes_word_count_hint(self):
        result = normalize("La niña corre (3)", stimulus=True)
        assert result == "la nina corre"
        # transcriptions should keep it if present (it's rare but possible)

    def test_strips_brackets(self):
        assert normalize("[unintelligible] el gato") == "el gato"

    def test_empty_input(self):
        assert normalize("") == ""
        assert normalize(None) == ""  # type: ignore[arg-type]

    def test_already_clean(self):
        assert normalize("el gato corre") == "el gato corre"


class TestTokenize:
    def test_basic(self):
        assert tokenize("El gato corre") == ["el", "gato", "corre"]

    def test_stimulus_hint_stripped(self):
        toks = tokenize("La niña lee (4)", stimulus=True)
        assert "(4)" not in toks
        assert toks == ["la", "nina", "lee"]

    def test_empty(self):
        assert tokenize("") == []


class TestContentWords:
    def test_drops_function_words(self):
        toks = ["el", "gato", "negro", "de", "la", "casa"]
        cw = content_words(toks)
        assert "el" not in cw
        assert "de" not in cw
        assert "gato" in cw

    def test_drops_single_char_tokens(self):
        assert content_words(["a", "b", "gato"]) == ["gato"]

    def test_empty_input(self):
        assert content_words([]) == []


class TestIsEmptyResponse:
    def test_empty_string(self):
        assert is_empty_response("") is True

    def test_whitespace_only(self):
        assert is_empty_response("   ") is True

    def test_bracket_only(self):
        assert is_empty_response("[unintelligible]") is True

    def test_real_response(self):
        assert is_empty_response("el gato corre") is False

    def test_none_input(self):
        assert is_empty_response(None) is True  # type: ignore[arg-type]


class TestIsEnglishResponse:
    def test_en_ingles_lowercase(self):
        assert is_english_response("en ingles") is True

    def test_en_ingles_accented(self):
        assert is_english_response("en inglés") is True

    def test_embedded(self):
        assert is_english_response("I said it en inglés") is True

    def test_spanish_response(self):
        assert is_english_response("el gato corre rápido") is False

    def test_none_input(self):
        assert is_english_response(None) is False  # type: ignore[arg-type]
