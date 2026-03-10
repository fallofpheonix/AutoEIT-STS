# AutoEIT-STS

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python autoeit_scorer.py
```

Default input auto-detection order:
1. `./Example_EIT Transcription and Scoring Sheet.xlsx`
2. `./Example_EIT_Transcription_and_Scoring_Sheet.xlsx`
3. `/mnt/user-data/uploads/Example_EIT_Transcription_and_Scoring_Sheet.xlsx`

Default outputs:
- `./AutoEIT_Sample_Transcriptions_Scored.xlsx`
- `./AutoEIT_scores.csv`

## Custom paths

```bash
python autoeit_scorer.py \
  --source "/absolute/path/input.xlsx" \
  --output-xlsx "/absolute/path/AutoEIT_Sample_Transcriptions_Scored.xlsx" \
  --output-csv "/absolute/path/AutoEIT_scores.csv"
```
