"""Feature extraction for AutoEIT-STS scoring.

Provides the :class:`FeatureBundle` dataclass that carries all computed
metrics for a single (stimulus, transcription) pair, and the
:func:`extract_features` factory function that populates it.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.text import (
    SER_FORMS,
    ESTAR_FORMS,
    content_words,
    tokenise,
)


@dataclass(frozen=True)
class FeatureBundle:
    """Immutable snapshot of all features derived from one utterance pair."""

    target_tokens: tuple[str, ...]
    learner_tokens: tuple[str, ...]
    edit_distance: int
    overlap: float
    learner_count: int
    target_count: int


def token_edit_distance(seq_a: list[str], seq_b: list[str]) -> int:
    """Compute the token-level Levenshtein edit distance between two sequences."""
    rows = len(seq_a) + 1
    cols = len(seq_b) + 1
    dp = list(range(cols))
    for row in range(1, rows):
        previous = dp[:]
        dp[0] = row
        for col in range(1, cols):
            if seq_a[row - 1] == seq_b[col - 1]:
                dp[col] = previous[col - 1]
            else:
                dp[col] = 1 + min(previous[col], dp[col - 1], previous[col - 1])
    return dp[-1]


def content_overlap_ratio(target_tokens: list[str], learner_tokens: list[str]) -> float:
    """Return the fraction of target content words reproduced by the learner."""
    target_content = content_words(target_tokens)
    learner_content = set(content_words(learner_tokens))
    if not target_content:
        return 1.0
    matched = sum(1 for token in target_content if token in learner_content)
    return matched / len(target_content)


def char_similarity(left: str, right: str) -> float:
    """Return character-level similarity (0–1) between two strings."""
    if left == right:
        return 1.0
    max_length = max(len(left), len(right), 1)
    return 1 - token_edit_distance(list(left), list(right)) / max_length


def morph_close(left: str, right: str, *, threshold: float = 0.72) -> bool:
    """Return True if two word forms are morphologically similar."""
    return char_similarity(left, right) >= threshold


def only_ser_estar_swap(target_tokens: list[str], learner_tokens: list[str]) -> bool:
    """Return True if the sole difference is a ser/estar substitution."""
    if len(target_tokens) != len(learner_tokens):
        return False
    differences = [
        (left, right)
        for left, right in zip(target_tokens, learner_tokens)
        if left != right
    ]
    if len(differences) != 1:
        return False
    left, right = differences[0]
    return (left in SER_FORMS and right in ESTAR_FORMS) or (
        left in ESTAR_FORMS and right in SER_FORMS
    )


def extract_features(target_raw: str, learner_raw: str) -> FeatureBundle:
    """Compute all scoring features for a (stimulus, transcription) pair.

    Parameters
    ----------
    target_raw:
        The raw stimulus sentence as it appears in the workbook.
    learner_raw:
        The raw learner transcription as it appears in the workbook.

    Returns
    -------
    :class:`FeatureBundle`
        An immutable bundle of all derived metrics.
    """
    target_tokens = tokenise(target_raw, is_stimulus=True)
    learner_tokens = tokenise(learner_raw)
    edit_distance = token_edit_distance(target_tokens, learner_tokens)
    overlap = content_overlap_ratio(target_tokens, learner_tokens)
    return FeatureBundle(
        target_tokens=tuple(target_tokens),
        learner_tokens=tuple(learner_tokens),
        edit_distance=edit_distance,
        overlap=overlap,
        learner_count=len(learner_tokens),
        target_count=len(target_tokens),
    )
