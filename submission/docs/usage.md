# Demo / Usage Guide

## Quick demo
1. Create and activate a virtual environment.
2. Install dependencies and package:
   - `pip install -r requirements.txt`
   - `pip install streamlit`
   - `pip install -e .`
3. Run CLI with the included sample workbook.
4. Verify generated files under `output/`.

## Expected outputs after CLI run
- `output/AutoEIT_Sample_Transcriptions_Scored.xlsx`
- `output/AutoEIT_scores.csv`
- `output/AutoEIT_ambiguous_downgrades.csv`

## UI walkthrough
1. Run `streamlit run autoeit/api/app.py`.
2. Upload a workbook (`.xlsx`) with expected headers (`Sentence`, `Stimulus`).
3. Review score metrics and sentence-level rationales.
4. Filter by participant and download current table as CSV.
