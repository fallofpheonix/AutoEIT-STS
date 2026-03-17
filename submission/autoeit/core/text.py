"""Text normalization for Spanish EIT transcriptions.

Handles the messiness that comes with real learner data: bracketed
annotations, inconsistent accent usage, stray punctuation. The two
normalization paths diverge slightly because stimulus texts sometimes carry a
word-count hint like "(12)" that should not carry over to comparison.
"""

from __future__ import annotations

import re
import unicodedata

# Closed-class words filtered out when computing content retention.
# Not exhaustive — covers the most common forms in the task corpus.
FUNCTION_WORDS: frozenset[str] = frozenset({
    "a", "al", "como", "con", "cuya", "cuyo", "de", "del", "el", "ella",
    "ellos", "ellas", "en", "era", "eran", "es", "ese", "esa", "esos", "esas",
    "esta", "estan", "estar", "este", "estos", "fue", "fueron", "ha", "haber",
    "han", "hay", "he", "hemos", "la", "las", "le", "les", "lo", "los", "mas",
    "me", "mi", "mis", "muy", "ni", "no", "nos", "nosotros", "o", "para",
    "pero", "por", "que", "quien", "se", "ser", "si", "sin", "sobre", "son",
    "su", "sus", "te", "tener", "tu", "tus", "un", "una", "unos", "unas",
    "usted", "ustedes", "y", "ya", "yo",
})

SER_FORMS: frozenset[str] = frozenset({
    "es", "son", "era", "eran", "fue", "fueron", "sea", "sean", "ser", "soy", "somos",
})

ESTAR_FORMS: frozenset[str] = frozenset({
    "esta", "estan", "estaba", "estaban", "estuvo", "estuvieron", "estar", "estoy", "estamos",
})

_BRACKET = re.compile(r"\[.*?\]")
_PUNCT = re.compile(r"[¿?¡!,.:;«»\"'\`´]")
_WHITESPACE = re.compile(r"\s+")
_WORD_COUNT_HINT = re.compile(r"\(\d+\)\s*$")


def _strip_diacritics(text: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFD", text)
        if unicodedata.category(ch) != "Mn"
    )


def normalize(text: str, *, stimulus: bool = False) -> str:
    """Return a clean, accent-stripped lowercase string ready for comparison.

    Stimulus texts get an extra pass to remove the word-count annotation that
    some workbook versions append.
    """
    if not isinstance(text, str):
        return ""
    s = _BRACKET.sub(" ", text)
    if stimulus:
        s = _WORD_COUNT_HINT.sub("", s)
    s = _PUNCT.sub("", s)
    s = _strip_diacritics(s.lower())
    return _WHITESPACE.sub(" ", s).strip()


def tokenize(text: str, *, stimulus: bool = False) -> list[str]:
    return normalize(text, stimulus=stimulus).split()


def content_words(tokens: list[str]) -> list[str]:
    """Drop function words and single-char tokens."""
    return [t for t in tokens if t not in FUNCTION_WORDS and len(t) > 1]


def is_empty_response(raw: str) -> bool:
    """True for blank strings and annotation-only responses like [unintelligible]."""
    if not isinstance(raw, str) or not raw.strip():
        return True
    stripped = _BRACKET.sub("", raw).strip()
    return _PUNCT.sub("", stripped).strip() == ""


def is_english_response(raw: str) -> bool:
    """Some learners write 'en inglés' to flag they answered in English."""
    if not isinstance(raw, str):
        return False
    lowered = raw.lower()
    return "en ingles" in lowered or "en inglés" in lowered
