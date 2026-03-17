# AutoEIT-STS Submission

## Project overview
AutoEIT-STS is a deterministic scoring system for the Spanish Elicited Imitation Task (EIT). It scores transcribed learner utterances on a 0–4 rubric and exports both workbook and CSV outputs with rationale text for traceability.

## Dependencies
- Python 3.11+
- `pandas>=2.0,<3.0`
- `openpyxl>=3.1,<4.0`
- `streamlit>=1.30` (optional, for UI)

## Setup instructions
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install streamlit
pip install -e .
```

## Run instructions
### CLI
```bash
python -m autoeit.api.cli \
  --input "input/workbooks/AutoEIT Sample Transcriptions for Scoring.xlsx" \
  --output-xlsx output/AutoEIT_Sample_Transcriptions_Scored.xlsx \
  --output-csv output/AutoEIT_scores.csv
```

### Streamlit UI
```bash
streamlit run autoeit/api/app.py
```

## Validation
```bash
pytest -q
```

## Notes
- `output/AutoEIT_scores.csv` and `output/AutoEIT_ambiguous_downgrades.csv` are included as sample outputs.
- The sample workbook is included under `input/workbooks/` for reproducible execution.
