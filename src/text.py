"""Text normalization and tokenization utilities for AutoEIT-STS."""

from __future__ import annotations

import re
import unicodedata

FUNCTION_WORDS = {
    "a", "al", "como", "con", "cuya", "cuyo", "de", "del", "el", "ella",
    "ellos", "ellas", "en", "era", "eran", "es", "ese", "esa", "esos", "esas",
    "esta", "estan", "estar", "este", "estos", "fue", "fueron", "ha", "haber",
    "han", "hay", "he", "hemos", "la", "las", "le", "les", "lo", "los", "mas",
    "me", "mi", "mis", "muy", "ni", "no", "nos", "nosotros", "o", "para",
    "pero", "por", "que", "quien", "se", "ser", "si", "sin", "sobre", "son",
    "su", "sus", "te", "tener", "tu", "tus", "un", "una", "unos", "unas",
    "usted", "ustedes", "y", "ya", "yo",
}

SER_FORMS = {"es", "son", "era", "eran", "fue", "fueron", "sea", "sean", "ser", "soy", "somos"}
ESTAR_FORMS = {"esta", "estan", "estaba", "estaban", "estuvo", "estuvieron", "estar", "estoy", "estamos"}

BRACKET_CONTENT = re.compile(r"\[.*?\]")
PUNCTUATION = re.compile(r"[¿?¡!,.:;«»\"'\`´]")
WHITESPACE = re.compile(r"\s+")
WORD_COUNT_HINT = re.compile(r"\(\d+\)\s*$")


def strip_accents(text: str) -> str:
    """Remove diacritical marks from a Unicode string."""
    return "".join(
        char for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )


def normalize_stimulus_text(text: str) -> str:
    """Normalize a stimulus sentence for comparison."""
    if not isinstance(text, str):
        return ""
    normalized = WORD_COUNT_HINT.sub("", text)
    normalized = BRACKET_CONTENT.sub(" ", normalized)
    normalized = PUNCTUATION.sub("", normalized)
    normalized = strip_accents(normalized.lower())
    return WHITESPACE.sub(" ", normalized).strip()


def normalize_transcription_text(text: str) -> str:
    """Normalize a learner transcription for comparison."""
    if not isinstance(text, str):
        return ""
    normalized = BRACKET_CONTENT.sub(" ", text)
    normalized = PUNCTUATION.sub("", normalized)
    normalized = strip_accents(normalized.lower())
    return WHITESPACE.sub(" ", normalized).strip()


def clean(text: str, *, is_stimulus: bool = False) -> str:
    """Return normalized text, dispatching to the appropriate normalizer."""
    if is_stimulus:
        return normalize_stimulus_text(text)
    return normalize_transcription_text(text)


def tokenise(text: str, *, is_stimulus: bool = False) -> list[str]:
    """Return a list of normalized tokens for the given text."""
    return clean(text, is_stimulus=is_stimulus).split()


def content_words(tokens: list[str]) -> list[str]:
    """Filter out function words and single-character tokens."""
    return [token for token in tokens if token not in FUNCTION_WORDS and len(token) > 1]


def is_no_response(raw: str) -> bool:
    """Return True if the raw transcription is empty or contains no real content."""
    if not isinstance(raw, str) or not raw.strip():
        return True
    cleaned = BRACKET_CONTENT.sub("", raw).strip()
    cleaned = PUNCTUATION.sub("", cleaned).strip()
    return cleaned == ""


def is_wrong_language(raw: str) -> bool:
    """Return True if the learner explicitly indicated a response in English."""
    if not isinstance(raw, str):
        return False
    lowered = raw.lower()
    return "en ingles" in lowered or "en inglés" in lowered
