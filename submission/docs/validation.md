# Test Cases / Validation Proof

## Automated tests
Command executed:
```bash
pytest -q
```

Coverage focus:
- text normalization and language/no-response detection,
- feature extraction and similarity behavior,
- rubric scoring gates and boundary behavior,
- workbook parsing and schema validation.

## End-to-end execution
Command executed:
```bash
python -m autoeit.api.cli \
  --input "input/workbooks/AutoEIT Sample Transcriptions for Scoring.xlsx" \
  --output-xlsx output/AutoEIT_Sample_Transcriptions_Scored.xlsx \
  --output-csv output/AutoEIT_scores.csv
```

Result:
- scorer completed without runtime errors,
- output workbook and CSV artifacts generated successfully.

## Platform notes
- This submission targets Python (desktop/server) execution.
- iOS/Android app compatibility is not applicable to this repository.
