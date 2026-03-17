"""Deterministic scoring rubric for the Spanish EIT.

The scoring logic lives in a single function so the decision path can be
audited top-to-bottom without jumping across files.  Thresholds are pulled
from config so researchers can run A/B experiments without touching this file.

Score semantics (meaning-based rubric):
    4 — exact or near-exact reproduction
    3 — minor deviation, overall meaning preserved
    2 — partial meaning retained
    1 — fragmentary, minimal meaning
    0 — no response / unintelligible / wrong language
"""

from __future__ import annotations

from autoeit.config.settings import RubricSettings, defaults
from autoeit.core.features import (
    FeatureBundle,
    extract_features,
    morph_close,
    is_ser_estar_swap,
)
from autoeit.core.text import is_empty_response, is_english_response


def _in_ambiguous_zone(edit: int, overlap: float, cfg: RubricSettings) -> bool:
    return (
        cfg.conservative_boundary
        and cfg.ambiguous_edit_min <= edit <= cfg.ambiguous_edit_max
        and cfg.ambiguous_overlap_min <= overlap <= cfg.ambiguous_overlap_max
    )


def score_utterance(
    target_raw: str,
    learner_raw: str,
    *,
    cfg: RubricSettings = defaults,
    return_meta: bool = False,
) -> tuple[int, str] | tuple[int, str, bool]:
    """Assign a score (0–4) to a single learner utterance.

    Parameters
    ----------
    target_raw : stimulus sentence from the workbook
    learner_raw : learner transcription
    cfg : rubric thresholds — override only if running threshold experiments
    return_meta : if True, also return whether an ambiguous downgrade occurred
    """
    downgraded = False

    def _out(score: int, msg: str):
        if return_meta:
            return score, msg, downgraded
        return score, msg

    # Gate checks — these run before feature extraction to short-circuit early
    if is_english_response(learner_raw):
        return _out(0, "Response flagged as English [en ingles]")
    if is_empty_response(learner_raw):
        return _out(0, "No response or empty transcription")

    ft: FeatureBundle = extract_features(target_raw, learner_raw)
    t = list(ft.target_tokens)
    l = list(ft.learner_tokens)  # noqa: E741 — short name intentional here
    ed = ft.edit_distance
    ov = ft.overlap
    lc = ft.learner_count
    tc = ft.target_count

    if not t:
        return _out(0, "Stimulus is empty after normalization")

    # ---- Score 4 -------------------------------------------------------
    if ed == 0:
        return _out(4, "Exact reproduction after normalization")

    if ed == 1 and ov >= 0.67:
        return _out(4, f"Single-token deviation, meaning intact (ov={ov:.2f})")

    if ed == 2 and ov >= 0.80:
        return _out(4, f"Two-token deviation consistent with disfluency (ov={ov:.2f})")

    if ed == 3 and ov >= 0.85:
        return _out(4, f"Three-token deviation, near-complete content (ov={ov:.2f})")

    # ---- Score 3 -------------------------------------------------------
    if is_ser_estar_swap(t, l):
        return _out(3, "ser/estar substitution — meaning preserved")

    if ed == 1 and ov >= 0.50:
        diffs = [(a, b) for a, b in zip(t, l) if a != b]
        if diffs:
            a, b = diffs[0]
            if morph_close(a, b, threshold=cfg.morph_similarity_threshold):
                return _out(3, f"Morphological variant '{a}' → '{b}'")
        return _out(3, f"Single deviation, meaning preserved (ov={ov:.2f})")

    if ed == 2 and ov >= 0.70 and lc >= tc - 1:
        return _out(3, f"Near-accurate, high content retention (ov={ov:.2f})")

    if ed == 2 and ov >= 0.50 and lc >= tc - 1:
        if _in_ambiguous_zone(ed, ov, cfg):
            downgraded = True
            return _out(2, f"Ambiguous 2/3 boundary — conservatively scored 2 (ed={ed}, ov={ov:.2f})")
        return _out(3, f"Near-accurate, limited omission (ov={ov:.2f})")

    if ed in (2, 3) and ov >= 0.65:
        if _in_ambiguous_zone(ed, ov, cfg):
            downgraded = True
            return _out(2, f"Ambiguous 2/3 boundary — conservatively scored 2 (ed={ed}, ov={ov:.2f})")
        return _out(3, f"Minor structural deviation, meaning preserved (ed={ed}, ov={ov:.2f})")

    if ed <= 4 and ov >= 0.75:
        if _in_ambiguous_zone(ed, ov, cfg):
            downgraded = True
            return _out(2, f"Ambiguous 2/3 boundary — conservatively scored 2 (ed={ed}, ov={ov:.2f})")
        return _out(3, f"High content retention despite structural deviation (ed={ed}, ov={ov:.2f})")

    # ---- Fragment check (runs before score 2 to avoid over-rewarding) ----
    if lc < 3 and ed >= 4 and ov > 0:
        return _out(1, f"Fragmentary response (ed={ed}, ov={ov:.2f})")

    # ---- Score 2 -------------------------------------------------------
    if ov >= 0.35 and lc >= max(2, int(tc * 0.30)):
        return _out(2, f"Partial content retained (ed={ed}, ov={ov:.2f})")

    if ov >= 0.25 and lc >= 2:
        return _out(2, f"Partial response, some content present (ov={ov:.2f})")

    # ---- Score 1 / 0 ---------------------------------------------------
    if ov > 0:
        return _out(1, f"Minimal/fragmentary meaning only (ov={ov:.2f})")

    return _out(0, f"No meaning preserved (ed={ed}, ov={ov:.2f})")
