"""Rubric thresholds and tunable constants.

All scoring decisions ultimately trace back to these values, which is why they
live in their own module rather than being scattered as magic numbers.  If you
want to experiment with a looser or stricter rubric, change them here and run
the benchmark to see the impact.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RubricSettings:
    # 2/3 ambiguous-boundary zone
    ambiguous_edit_min: int = 2
    ambiguous_edit_max: int = 4
    ambiguous_overlap_min: float = 0.60
    ambiguous_overlap_max: float = 0.78

    # when True, utterances inside the zone are scored 2 rather than 3
    conservative_boundary: bool = True

    # char-similarity floor for accepting morphological variants as equivalent
    morph_similarity_threshold: float = 0.72


# Import this rather than constructing your own instance unless you need a
# custom threshold profile (e.g., for A/B rubric experiments).
defaults = RubricSettings()
