"""Deterministic rubric scoring engine for AutoEIT-STS.

This module contains the sole scoring function :func:`score_utterance`, which
maps a (stimulus, transcription) pair to a score in {0, 1, 2, 3, 4} and a
human-readable rationale string.  All thresholds are defined as module-level
constants so that the decision logic is fully transparent and auditable.
"""

from __future__ import annotations

from src.features import (
    FeatureBundle,
    extract_features,
    morph_close,
    only_ser_estar_swap,
)
from src.text import is_no_response, is_wrong_language

# ---------------------------------------------------------------------------
# Rubric thresholds
# ---------------------------------------------------------------------------

AMBIGUOUS_TO_2: bool = True
"""When True, borderline cases at the 2/3 boundary are conservatively assigned 2."""

AMBIGUOUS_EDIT_MIN: int = 2
AMBIGUOUS_EDIT_MAX: int = 4
AMBIGUOUS_OVERLAP_MIN: float = 0.60
AMBIGUOUS_OVERLAP_MAX: float = 0.78


def is_ambiguous_meaning_case(edit_distance: int, overlap: float) -> bool:
    """Return True if the utterance falls within the ambiguous 2/3 boundary zone."""
    return (
        AMBIGUOUS_TO_2
        and AMBIGUOUS_EDIT_MIN <= edit_distance <= AMBIGUOUS_EDIT_MAX
        and AMBIGUOUS_OVERLAP_MIN <= overlap <= AMBIGUOUS_OVERLAP_MAX
    )


def score_utterance(
    target_raw: str,
    learner_raw: str,
    *,
    return_meta: bool = False,
) -> tuple[int, str] | tuple[int, str, bool]:
    """Assign a deterministic score (0–4) to one learner utterance.

    Parameters
    ----------
    target_raw:
        Raw stimulus sentence from the workbook.
    learner_raw:
        Raw learner transcription from the workbook.
    return_meta:
        When True, return a three-tuple ``(score, rationale, ambiguous_downgraded)``
        instead of the default two-tuple.

    Returns
    -------
    ``(score, rationale)`` or ``(score, rationale, ambiguous_downgraded)``
    """
    ambiguous_downgraded = False

    def _ret(score: int, rationale: str):
        if return_meta:
            return score, rationale, ambiguous_downgraded
        return score, rationale

    # --- Gate checks ---------------------------------------------------------
    if is_wrong_language(learner_raw):
        return _ret(0, "Response in wrong language [en ingles]")
    if is_no_response(learner_raw):
        return _ret(0, "No response or empty transcription")

    features: FeatureBundle = extract_features(target_raw, learner_raw)

    target_tokens = list(features.target_tokens)
    learner_tokens = list(features.learner_tokens)
    edit_distance = features.edit_distance
    overlap = features.overlap
    learner_count = features.learner_count
    target_count = features.target_count

    if not target_tokens:
        return _ret(0, "Target sentence is empty")

    # --- Score 4 rules -------------------------------------------------------
    if edit_distance == 0:
        return _ret(4, "Exact reproduction after normalization")
    if edit_distance == 1 and overlap >= 0.67:
        return _ret(4, f"1-word deviation, meaning preserved (overlap={overlap:.2f})")
    if edit_distance == 2 and overlap >= 0.80:
        return _ret(4, f"2-word deviation consistent with disfluency artifact (overlap={overlap:.2f})")
    if edit_distance == 3 and overlap >= 0.85:
        return _ret(4, f"3-word deviation with near-complete content retention (overlap={overlap:.2f})")

    # --- Score 3 rules -------------------------------------------------------
    if only_ser_estar_swap(target_tokens, learner_tokens):
        return _ret(3, "ser/estar substitution with preserved meaning")
    if edit_distance == 1 and overlap >= 0.50:
        differences = [
            (left, right)
            for left, right in zip(target_tokens, learner_tokens)
            if left != right
        ]
        if differences:
            left, right = differences[0]
            if morph_close(left, right):
                return _ret(3, f"Morphological variant '{left}' -> '{right}' with preserved meaning")
        return _ret(3, f"Single-word deviation with preserved meaning (overlap={overlap:.2f})")
    if edit_distance == 2 and overlap >= 0.70 and learner_count >= target_count - 1:
        return _ret(3, f"Near-accurate response with high content retention (overlap={overlap:.2f})")
    if edit_distance == 2 and overlap >= 0.50 and learner_count >= target_count - 1:
        if is_ambiguous_meaning_case(edit_distance, overlap):
            ambiguous_downgraded = True
            return _ret(2, f"Ambiguous meaning boundary downgraded to 2 (edit={edit_distance}, overlap={overlap:.2f})")
        return _ret(3, f"Near-accurate response with limited omission/substitution (overlap={overlap:.2f})")
    if edit_distance in (2, 3) and overlap >= 0.65:
        if is_ambiguous_meaning_case(edit_distance, overlap):
            ambiguous_downgraded = True
            return _ret(2, f"Ambiguous meaning boundary downgraded to 2 (edit={edit_distance}, overlap={overlap:.2f})")
        return _ret(3, f"Minor structural deviation with preserved meaning (edit={edit_distance}, overlap={overlap:.2f})")
    if edit_distance <= 4 and overlap >= 0.75:
        if is_ambiguous_meaning_case(edit_distance, overlap):
            ambiguous_downgraded = True
            return _ret(2, f"Ambiguous meaning boundary downgraded to 2 (edit={edit_distance}, overlap={overlap:.2f})")
        return _ret(3, f"High content retention despite structural deviation (edit={edit_distance}, overlap={overlap:.2f})")

    # --- Score 1 (fragmentary) -----------------------------------------------
    if learner_count < 3 and edit_distance >= 4 and overlap > 0:
        return _ret(1, f"Fragmentary response only (edit={edit_distance}, overlap={overlap:.2f})")

    # --- Score 2 rules -------------------------------------------------------
    if overlap >= 0.35 and learner_count >= max(2, int(target_count * 0.30)):
        return _ret(2, f"Partial meaning retained (edit={edit_distance}, overlap={overlap:.2f})")
    if overlap >= 0.25 and learner_count >= 2:
        return _ret(2, f"Partial response with some retained content (overlap={overlap:.2f})")

    # --- Score 1 / 0 fallback ------------------------------------------------
    if overlap > 0:
        return _ret(1, f"Minimal fragmentary meaning only (overlap={overlap:.2f})")
    return _ret(0, f"No meaning preserved (edit={edit_distance}, overlap={overlap:.2f})")
