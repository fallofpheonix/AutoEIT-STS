"""Feature extraction for a (stimulus, transcription) pair.

FeatureBundle is frozen so it can be passed around without risk of accidental
mutation downstream — useful if we ever add caching.
"""

from __future__ import annotations

from dataclasses import dataclass

from autoeit.core.text import SER_FORMS, ESTAR_FORMS, content_words, tokenize


@dataclass(frozen=True)
class FeatureBundle:
    target_tokens: tuple[str, ...]
    learner_tokens: tuple[str, ...]
    edit_distance: int
    overlap: float
    learner_count: int
    target_count: int


def _levenshtein(a: list[str], b: list[str]) -> int:
    """Token-level edit distance.

    Standard bottom-up DP, space-optimised to one row.  Not the fastest
    implementation possible but clear enough to verify against manual examples
    during rubric calibration sessions.
    """
    n, m = len(a), len(b)
    dp = list(range(m + 1))
    for i in range(1, n + 1):
        prev = dp[:]
        dp[0] = i
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[j] = prev[j - 1]
            else:
                dp[j] = 1 + min(prev[j], dp[j - 1], prev[j - 1])
    return dp[-1]


def _content_overlap(target_toks: list[str], learner_toks: list[str]) -> float:
    target_content = content_words(target_toks)
    if not target_content:
        return 1.0
    learner_set = set(content_words(learner_toks))
    hits = sum(1 for t in target_content if t in learner_set)
    return hits / len(target_content)


def char_similarity(a: str, b: str) -> float:
    if a == b:
        return 1.0
    longest = max(len(a), len(b), 1)
    return 1.0 - _levenshtein(list(a), list(b)) / longest


def morph_close(a: str, b: str, *, threshold: float = 0.72) -> bool:
    """Two forms are 'morphologically close' if char similarity clears the threshold.

    The 0.72 default was settled on during rubric calibration against the 2023
    scored dataset — high enough to reject unrelated words, lenient enough to
    accept most inflectional variants.
    """
    return char_similarity(a, b) >= threshold


def is_ser_estar_swap(target_toks: list[str], learner_toks: list[str]) -> bool:
    """True when the only difference between sequences is a ser↔estar substitution."""
    if len(target_toks) != len(learner_toks):
        return False
    diffs = [(a, b) for a, b in zip(target_toks, learner_toks) if a != b]
    if len(diffs) != 1:
        return False
    a, b = diffs[0]
    return (a in SER_FORMS and b in ESTAR_FORMS) or (a in ESTAR_FORMS and b in SER_FORMS)


def extract_features(target_raw: str, learner_raw: str) -> FeatureBundle:
    t_toks = tokenize(target_raw, stimulus=True)
    l_toks = tokenize(learner_raw)
    return FeatureBundle(
        target_tokens=tuple(t_toks),
        learner_tokens=tuple(l_toks),
        edit_distance=_levenshtein(t_toks, l_toks),
        overlap=_content_overlap(t_toks, l_toks),
        learner_count=len(l_toks),
        target_count=len(t_toks),
    )
