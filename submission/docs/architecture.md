# Architecture / Design

## Layered structure
- `autoeit/config` — rubric thresholds and tunable scoring constants.
- `autoeit/core` — deterministic domain logic:
  - text normalization,
  - feature extraction,
  - rubric decision tree.
- `autoeit/services` — orchestration and workbook I/O.
- `autoeit/api` — executable interfaces (CLI and Streamlit UI).
- `autoeit/utils` — narrow shared utilities (path helpers).
- `tests` — critical-path unit tests.

## Runtime flow
1. Load workbook rows (`services/workbook.py`).
2. Normalize and tokenize input (`core/text.py`).
3. Compute features (`core/features.py`).
4. Score via rubric (`core/rubric.py`).
5. Aggregate metrics (`services/scoring.py`).
6. Export workbook + CSV outputs (`services/workbook.py`).

## Design choices
- Deterministic scoring over ML: reproducible and auditable for research workflows.
- Single explicit scoring decision tree: easier rubric traceability.
- Conservative ambiguous-boundary handling: reduces inflated scores around the 2/3 boundary.
