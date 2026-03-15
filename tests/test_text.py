"""Tests for src.text — normalization and tokenization."""

import pytest

from src.text import (
    clean,
    content_words,
    is_no_response,
    is_wrong_language,
    normalize_stimulus_text,
    normalize_transcription_text,
    strip_accents,
    tokenise,
)


class TestStripAccents:
    def test_removes_acute(self):
        assert strip_accents("café") == "cafe"

    def test_removes_tilde(self):
        assert strip_accents("niño") == "nino"

    def test_no_change_plain_ascii(self):
        assert strip_accents("hello") == "hello"

    def test_empty_string(self):
        assert strip_accents("") == ""

    def test_multiple_accents(self):
        assert strip_accents("Ángel García") == "Angel Garcia"


class TestNormalizeStimulusText:
    def test_lowercases(self):
        assert normalize_stimulus_text("HOLA Mundo") == "hola mundo"

    def test_removes_word_count_hint(self):
        assert normalize_stimulus_text("El niño juega (4)") == "el nino juega"

    def test_removes_bracket_content(self):
        assert normalize_stimulus_text("El [noise] gato") == "el gato"

    def test_removes_punctuation(self):
        assert normalize_stimulus_text("¿Cómo estás?") == "como estas"

    def test_collapses_whitespace(self):
        assert normalize_stimulus_text("el   gato  negro") == "el gato negro"

    def test_non_string_returns_empty(self):
        assert normalize_stimulus_text(None) == ""  # type: ignore[arg-type]
        assert normalize_stimulus_text(42) == ""  # type: ignore[arg-type]


class TestNormalizeTranscriptionText:
    def test_lowercases_and_strips_accents(self):
        assert normalize_transcription_text("Él habló") == "el hablo"

    def test_removes_bracket_content(self):
        assert normalize_transcription_text("hola [unintelligible] mundo") == "hola mundo"

    def test_removes_punctuation(self):
        assert normalize_transcription_text("¡Hola!") == "hola"

    def test_non_string_returns_empty(self):
        assert normalize_transcription_text(None) == ""  # type: ignore[arg-type]


class TestClean:
    def test_stimulus_path(self):
        result = clean("El niño corre (3)", is_stimulus=True)
        assert result == normalize_stimulus_text("El niño corre (3)")

    def test_transcription_path(self):
        result = clean("El niño corre")
        assert result == normalize_transcription_text("El niño corre")


class TestTokenise:
    def test_basic_split(self):
        assert tokenise("el gato negro") == ["el", "gato", "negro"]

    def test_stimulus_strips_word_count(self):
        tokens = tokenise("El gato negro (3)", is_stimulus=True)
        assert tokens == ["el", "gato", "negro"]

    def test_empty_string(self):
        assert tokenise("") == []


class TestContentWords:
    def test_filters_function_words(self):
        tokens = ["el", "gato", "y", "la", "perro"]
        assert content_words(tokens) == ["gato", "perro"]

    def test_filters_single_char(self):
        tokens = ["a", "gato"]
        assert content_words(tokens) == ["gato"]

    def test_all_function_words(self):
        tokens = ["el", "la", "de", "y"]
        assert content_words(tokens) == []

    def test_empty(self):
        assert content_words([]) == []


class TestIsNoResponse:
    def test_empty_string(self):
        assert is_no_response("") is True

    def test_none(self):
        assert is_no_response(None) is True  # type: ignore[arg-type]

    def test_only_brackets(self):
        assert is_no_response("[unintelligible]") is True

    def test_only_punctuation(self):
        assert is_no_response("...") is True

    def test_real_content(self):
        assert is_no_response("el gato") is False


class TestIsWrongLanguage:
    def test_en_ingles_lower(self):
        assert is_wrong_language("en ingles") is True

    def test_en_inglés_accented(self):
        assert is_wrong_language("en inglés") is True

    def test_mixed_case(self):
        assert is_wrong_language("En Ingles") is True

    def test_spanish_response(self):
        assert is_wrong_language("el gato corre") is False

    def test_none(self):
        assert is_wrong_language(None) is False  # type: ignore[arg-type]
