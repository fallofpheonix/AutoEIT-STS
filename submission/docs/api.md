# API Documentation

This project provides interface APIs via CLI and Streamlit.

## CLI API
Module: `autoeit.api.cli`

Command:
```bash
python -m autoeit.api.cli \
  --input <path/to/input.xlsx> \
  --output-xlsx <path/to/scored.xlsx> \
  --output-csv <path/to/scores.csv> \
  [--downgrades-csv <path/to/downgrades.csv>]
```

### Arguments
- `--input` (required): source workbook path.
- `--output-xlsx` (required): scored workbook destination.
- `--output-csv` (required): flat scores CSV destination.
- `--downgrades-csv` (optional): explicit ambiguous-downgrade CSV destination.

### Outputs
- Workbook with appended `AutoEIT_Score` and `Rationale` columns.
- Main scores CSV.
- Ambiguous-downgrade audit CSV.

## UI API
Module: `autoeit.api.app`

Run:
```bash
streamlit run autoeit/api/app.py
```

UI capabilities:
- workbook upload,
- participant filtering,
- score distribution chart,
- CSV download from current filtered view.
