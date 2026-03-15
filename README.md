# Task II: Automated Scoring

## Goal
Assign deterministic sentence-level EIT scores from staged transcription workbooks using a rule-based 0-4 rubric implementation.

## Inputs
- Workbook: [input/workbooks/AutoEIT Sample Transcriptions for Scoring.xlsx](/Users/fallofpheonix/Project/Human AI/AutoEIT/task2/input/workbooks/AutoEIT%20Sample%20Transcriptions%20for%20Scoring.xlsx)
- Evaluation workbook: [input/workbooks/Example_EIT Transcription and Scoring Sheet.xlsx](/Users/fallofpheonix/Project/Human AI/AutoEIT/task2/input/workbooks/Example_EIT%20Transcription%20and%20Scoring%20Sheet.xlsx)
- Rubric references: [input/rubric](/Users/fallofpheonix/Project/Human AI/AutoEIT/task2/input/rubric)

## Command
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Then run:

```bash
python -m src.run \
  --input-xlsx "input/workbooks/Example_EIT Transcription and Scoring Sheet.xlsx" \
  --output-xlsx "output/AutoEIT_Sample_Transcriptions_Scored.xlsx" \
  --output-csv "output/AutoEIT_scores.csv"
```

## Output Contract
- Preserves original workbook sheets and appends `AutoEIT_Score` plus `Rationale`.
- Creates `AutoEIT_Summary` for flat review.
- Writes a flat CSV and an explicit ambiguous downgrade CSV.
- Remains deterministic for identical inputs and configuration.

## Notebook
- Notebook: [notebooks/task2_scoring.ipynb](/Users/fallofpheonix/Project/Human AI/AutoEIT/task2/notebooks/task2_scoring.ipynb)
- PDF: [output/AutoEIT_Task2_Notebook.pdf](/Users/fallofpheonix/Project/Human AI/AutoEIT/task2/output/AutoEIT_Task2_Notebook.pdf)
