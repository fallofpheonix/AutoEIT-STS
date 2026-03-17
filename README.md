# AutoEIT-STS

Deterministic scoring engine for the **Spanish Elicited Imitation Task (EIT)**. Takes researcher-transcribed learner responses and assigns a meaning-based score (0–4) using a rule-based rubric — same input always produces same output.

## What it does

Reads an `.xlsx` workbook where each row is a (stimulus, transcription) pair, scores every utterance, and writes:
- An annotated copy of the workbook with colour-coded scores and rationale columns
- A flat CSV of all scores
- An audit log of utterances where the ambiguous 2/3 boundary rule was applied

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

For the Streamlit UI, also install:
```bash
pip install streamlit
```

## Run

**CLI:**
```bash
python -m autoeit.api.cli \
  --input input/workbooks/your_workbook.xlsx \
  --output-xlsx output/scored.xlsx \
  --output-csv output/scores.csv
```

**Streamlit UI:**
```bash
streamlit run autoeit/api/app.py
```

## Tests

```bash
pip install pytest
pytest
```

## Project structure

```
autoeit/
  config/     rubric thresholds
  core/       text normalization, features, scoring rubric
  services/   workbook I/O, pipeline orchestration
  api/        CLI and Streamlit interface
tests/
```

## Key design decisions

**Single scoring function** — `score_utterance` in `core/rubric.py` is intentionally one long function. Splitting it across helpers would obscure the decision path, which needs to be auditable by linguists, not just engineers.

**Conservative boundary** — utterances that fall into the 2/3 ambiguous zone are downgraded to 2 by default. This matches the rubric guidance for inter-rater reliability. Disable with `RubricSettings(conservative_boundary=False)`.

**No ML** — the rubric is fully deterministic. This was a deliberate choice: researchers need to be able to trace every scoring decision back to a specific rule, and model drift would be a problem for longitudinal studies.

**Accent-insensitive comparison** — learner transcriptions are often typed without diacritics. Stripping accents before comparison is linguistically imprecise but practically necessary.
