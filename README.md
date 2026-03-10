Readme · MD
Copy

# AutoEIT-STS

> **Automatic scoring engine for Spanish Elicited Imitation Task (EIT) — Specific Test II**

A reproducible, rule-based system for scoring learner transcriptions against target sentences on a **0–4 meaning-preservation scale**. Calibrated against 1,560 expert-annotated utterances (74% exact agreement, 96% within-1 agreement).

---

## Contents

- [Quickstart](#quickstart)
- [Scoring Rubric](#scoring-rubric)
- [How It Works](#how-it-works)
- [Input Format](#input-format)
- [Outputs](#outputs)
- [Custom Paths](#custom-paths)
- [Evaluation Metrics](#evaluation-metrics)
- [Performance](#performance)

---

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python autoeit_scorer.py
```

Place your input file in the project directory or at the default upload path. The script auto-detects the source in this order:

| Priority | Path |
|----------|------|
| 1 | `./Example_EIT Transcription and Scoring Sheet.xlsx` |
| 2 | `./Example_EIT_Transcription_and_Scoring_Sheet.xlsx` |
| 3 | `/mnt/user-data/uploads/Example_EIT_Transcription_and_Scoring_Sheet.xlsx` |

---

## Scoring Rubric

Scores are assigned on a **0–4 integer scale** based on meaning preservation:

| Score | Label | Criteria |
|-------|-------|----------|
| **4** | Accurate reproduction | Token edit distance ≤ 3; all deviations are disfluencies/repetition artefacts. Content overlap ≥ 0.67. |
| **3** | Near-accurate | Minor grammatical or morphological deviation (e.g. *ser↔estar* swap, conjugation change, dropped function word). Content overlap ≥ 0.65. |
| **2** | Partial meaning | Noticeable deviation but ≥ 35% of content words preserved. |
| **1** | Minimal meaning | Only isolated recognisable fragments; content overlap < 25%. |
| **0** | No meaning preserved | Wrong language, silence, or complete substitution with unrelated words. |

---

## How It Works

The scoring pipeline applies a **deterministic rule cascade** — no ML models or randomness:

1. **Normalise** both strings:
   - Strip stimulus word-count hints: `(7)`, `(12)` etc.
   - Remove bracketed annotations: `[false-start-]`, `[...]`
   - Strip punctuation and diacritics, lowercase, collapse whitespace

2. **Compute metrics**:
   - Token-level Levenshtein edit distance
   - Content-word overlap ratio (excluding Spanish function words)
   - Character-level morphological similarity for single-word substitutions

3. **Apply rubric rules** in order (Score 4 → 3 → 2 → 1 → 0), with special handling for:
   - *ser↔estar* substitutions (Score 3, not penalised as content change)
   - Morphological variants (e.g. *romancia → romance*)
   - Ambiguous meaning-change boundary (borderline 3→2 downgrade policy, configurable)

---

## Input Format

The input is an `.xlsx` workbook with one sheet per participant, named `{id}_v{A|B}` (e.g. `4_vA`, `18_vB`).

Each sheet has data from row 2 onwards:

| Column | Field | Notes |
|--------|-------|-------|
| A | `sentence_id` | Integer |
| B | `stimulus` | Target sentence (may include word-count hint) |
| C | `transcription` | Learner response (may include bracket annotations) |
| D | `human_score` | Optional — used for evaluation if present |

---

## Outputs

| File | Description |
|------|-------------|
| `AutoEIT_Sample_Transcriptions_Scored.xlsx` | Original workbook with two added columns per sheet: `AutoEIT_Score` (colour-coded) and `Rationale`. Includes a consolidated `AutoEIT_Summary` sheet. |
| `AutoEIT_scores.csv` | Flat CSV of all scored utterances with metadata. |
| `AutoEIT_ambiguous_downgrades.csv` | Log of utterances where the 3→2 ambiguity policy was applied. |

**Score colour coding in Excel:**

| Colour | Score |
|--------|-------|
| 🟢 Green | 4 |
| 🟡 Yellow | 3 |
| 🟠 Orange | 2 |
| 🔴 Light red | 1 |
| 🔴 Red | 0 |

---

## Custom Paths

```bash
python autoeit_scorer.py \
  --source      "/path/to/input.xlsx" \
  --output-xlsx "/path/to/AutoEIT_Sample_Transcriptions_Scored.xlsx" \
  --output-csv  "/path/to/AutoEIT_scores.csv"
```

---

## Evaluation Metrics

When human scores are present, the scorer reports:

- **Exact agreement rate** — sentence-level exact match %
- **Within-1 agreement rate** — % of scores differing by ≤ 1
- **Per-participant total deviation** — mean and max absolute difference in summed scores
- **% of participants within 10 points** of human total
- **Score distribution** — auto vs. human
- **Confusion matrix** — human (rows) × auto (columns) score classes

---

## Performance

Results on the included 1,560-utterance annotated dataset (29 participants, versions A & B):

| Metric | Value |
|--------|-------|
| Exact agreement | **74.0%** |
| Within-1 agreement | **96.2%** |
| Mean participant deviation | 7.3 points |
| Participants within 10 points | 76.9% |

Runtime scales as **O(U × L²)** per utterance count *U* and average sentence length *L* (dominated by token-level Levenshtein). Typical dataset scores in under 10 seconds.

---

## Requirements

```
pandas >= 2.0, < 3.0
openpyxl >= 3.1, < 4.0
```

Python 3.10+ required (uses `list[str]` type hints).
