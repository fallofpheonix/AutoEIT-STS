"""Backward-compatible re-export shim for AutoEIT-STS.

All scoring logic has been refactored into:
  - src.text      — normalization and tokenization
  - src.features  — FeatureBundle and feature extraction
  - src.rubric    — deterministic scoring decision tree
  - src.io        — workbook parsing and writing
  - src.pipeline  — end-to-end orchestration

This module re-exports the public API so that existing callers of
``src.scorer`` continue to work without modification.
"""

from __future__ import annotations

from src.features import (  # noqa: F401
    FeatureBundle,
    char_similarity,
    content_overlap_ratio,
    extract_features,
    morph_close,
    only_ser_estar_swap,
    token_edit_distance,
)
from src.io import (  # noqa: F401
    HEADER_FILL,
    HEADER_FONT,
    SCORE_FILLS,
    ensure_parent_dir,
    last_populated_header_column,
    load_dataset,
    parse_sheet_identity,
    validate_workbook_schema,
    write_csv_outputs,
    write_output_workbook,
)
from src.pipeline import (  # noqa: F401
    compute_metrics,
    run_scoring_pipeline,
    score_workbook,
)
from src.rubric import (  # noqa: F401
    AMBIGUOUS_EDIT_MAX,
    AMBIGUOUS_EDIT_MIN,
    AMBIGUOUS_OVERLAP_MAX,
    AMBIGUOUS_OVERLAP_MIN,
    AMBIGUOUS_TO_2,
    is_ambiguous_meaning_case,
    score_utterance,
)
from src.text import (  # noqa: F401
    BRACKET_CONTENT,
    ESTAR_FORMS,
    FUNCTION_WORDS,
    PUNCTUATION,
    SER_FORMS,
    WHITESPACE,
    WORD_COUNT_HINT,
    clean,
    content_words,
    is_no_response,
    is_wrong_language,
    normalize_stimulus_text,
    normalize_transcription_text,
    strip_accents,
    tokenise,
)
