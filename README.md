# AutoEIT-STS: Automated Scoring & Transcription Suite for Spanish EIT

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)

AutoEIT-STS is a deterministic scoring engine for the **Spanish Elicited Imitation Task (EIT)**. It provides researchers with a reliable, reproducible, and transparent way to automate the scoring of learner transcriptions according to official meaning-based rubrics.

## 🚀 Key Features

*   **Deterministic Scoring:** Identical inputs always yield identical scores (Levels 0-4).
*   **Linguistic Normalization:** Automatic handling of Spanish diacritics, transcription artifacts (bracketed noise), and case normalization.
*   **Transparent Rationales:** Every assigned score includes a rationale string explaining the specific rule used.
*   **Research Integration:** Seamlessly reads from and writes to Excel workbooks (.xlsx), preserving original metadata.
*   **Ambiguity Handling:** Explicit boundary logic for borderline cases (e.g., 2 vs. 3) to ensure conservative and consistent ratings.

## 🛠 Installation

```bash
# Clone the repository
git clone https://github.com/fallofpheonix/AutoEIT-STS.git
cd AutoEIT-STS/AutoEIT-STS-sync

# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
python -m pip install -r requirements.txt
```

## 📖 Usage

Run the scoring engine on a transcription workbook:

```bash
python -m src.run \
  --input-xlsx "input/workbooks/Example_EIT Transcription and Scoring Sheet.xlsx" \
  --output-xlsx "output/AutoEIT_Sample_Transcriptions_Scored.xlsx" \
  --output-csv "output/AutoEIT_scores.csv"
```

### Advanced Options
- `--config`: Path to custom rubric thresholds.
- `--verbose`: Include detailed feature extraction logs in the output.

## 🏗 System Architecture

The project is structured around a modular pipeline:
1.  **I/O Module:** Standardized workbook loading and saving.
2.  **Normalization Layer:** Cleaning and preparing text for comparison.
3.  **Feature Extractor:** Computing token-level and semantic overlap metrics.
4.  **Rubric Engine:** Hierarchical decision tree for score assignment.

## 🤝 Contributing

We welcome contributions from the linguistic and software engineering communities! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to get started.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Mentors & Contact

- **Mandy Faretta-Stutenberg** (Northern Illinois University)
- **Xabier Granja** (University of Alabama)

For inquiries regarding the AutoEIT project, please contact [human-ai@cern.ch](mailto:human-ai@cern.ch).
