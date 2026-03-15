# GSoC 2026 Proposal: Deterministic and Reproducible Automated Scoring Engine for the Spanish Elicited Imitation Task (AutoEIT)

## 1. Project Title
**Deterministic and Reproducible Automated Scoring Engine for the Spanish Elicited Imitation Task (AutoEIT)**

## 2. Abstract / Overview
The Spanish Elicited Imitation Task (EIT) is a critical tool for measuring language proficiency, yet its reliance on human raters makes it labor-intensive and hard to scale. Current AI-driven scoring approaches often exhibit non-deterministic behavior, producing inconsistent results for identical inputs, which undermines their utility in research. 

This project aims to bridge this gap by developing a robust, rule-driven, and deterministic scoring engine. By transforming transcriptions into objective, rubric-compliant scores, we will eliminate variability and provide a reproducible foundation for large-scale language acquisition studies. The solution includes a core scoring engine, a comprehensive evaluation suite, and a researchers' interface, ensuring 90% agreement with expert human raters.

## 3. Problem Statement
The current manual scoring process for the Spanish EIT is a bottleneck in linguistic research. It requires significant time from trained experts and often necessitates multi-rater reconciliation to maintain consistency. While Large Language Models (LLMs) offer a potential shortcut, their stochastic nature makes them unsuitable for research-grade scoring where reproducibility is paramount.

The technical challenge lies in the nature of learner speech, which is frequently non-target-like:
*   **Surface Variation:** Distinguishing between minor morphological errors (which may preserve meaning) and significant semantic shifts.
*   **Transcription Noise:** Handling disfluencies, false starts, and hesitations without penalizing the underlying linguistic competence.
*   **Rubric Complexity:** The EIT meaning-based rubric is not a simple string-matching task; it requires nuanced hierarchy-based interpretation.

Without a standardized, automated tool, researchers are limited in the volume of data they can process and the reliability of the comparisons they can make across different sessions and studies.

## 4. Project Constraints and Assumptions
*   **Determinism:** The system must produce identical outputs for identical inputs (same version).
*   **Input Format:** The primary data source consists of transcribed learner utterances and their corresponding prompt sentences.
*   **Language Scope:** Specifically optimized for Spanish, with an extensible architecture for other languages.
*   **Accuracy Target:** 90% sentence-level agreement with human raters; <10 point difference on a 120-point scale.
*   **Interpretability:** Decisions must be accompanied by rationales to allow for researcher audits.
*   **Dependencies:** Built using standard Python libraries (pandas, openpyxl) to minimize environment overhead.

## 5. Proposed Solution
The proposed system, **AutoEIT-STS (Scoring & Transcription Suite)**, is a layered architecture designed for stability and transparency.

### Core Components
1.  **Normalization Layer:** Cleans raw transcriptions by removing non-linguistic annotations (e.g., bracketed noise), normalizing case, and handling Spanish-specific diacritics.
2.  **Linguistic Feature Extractor:** Computes metrics that reflect meaning preservation, such as content-word overlap, edit distance at the token level, and length ratios.
3.  **Deterministic Rubric Engine:** A hierarchical decision tree that maps extracted features to the 0-4 scale. It includes an "Ambiguity Boundary" policy that defaults to the lower score in borderline cases, ensuring conservative and consistent rating.
4.  **Rationale Generator:** For every score, the engine outputs the specific rule triggered, facilitating manual verification.

### System Architecture & Data Flow
*   **Ingestion:** Reads `.xlsx` or `.csv` files containing participant responses.
*   **Processing:** The engine processes each sentence through the normalization and feature extraction modules.
*   **Scoring:** The Rubric Engine applies versioned rules to assign scores.
*   **Reporting:** Generates a "Scored Workbook" and an "Anomaly Log" for cases that fell into ambiguity thresholds.

## 6. Technical Methodology
### System Modules
*   `src.io`: Handles workbook parsing and standardized output.
*   `src.text`: Core NLP logic for Spanish tokenization and normalization.
*   `src.scorer`: The central logic applying the 0-4 rubric.
*   `src.evaluation`: Tools to compare system output against expert human scores.

### Technologies
*   **Python 3.11+:** Modern, stable base.
*   **OpenPyXL & Pandas:** For robust data handling of Excel-based research files.
*   **GitHub Actions:** For automated regression testing to ensure code changes don't disrupt scoring stability.

### Implementation Strategy
The project follows a "Baseline-First" approach. We will first implement a rigid rule-based system that captures 80% of cases perfectly. We will then iteratively refine the "Ambiguity Layer" using heuristic analysis of human-rater disagreements to reach the 90% target without sacrificing determinism.

## 7. Implementation Plan
*   **Phase 1 – Research and System Design:** Formalizing the rubric into machine-readable logic and finalizing data contracts.
*   **Phase 2 – Core Implementation:** Building the engine, feature extractors, and CLI tools.
*   **Phase 3 – Feature Integration:** Adding rationale generation and summary reporting.
*   **Phase 4 – Optimization:** Refining thresholds based on the test dataset provided in the GSoC application.
*   **Phase 5 – Testing and Documentation:** Completing the test suite and user manual for researchers.

## 8. Project Roadmap (GSoC Timeline)
*   **Community Bonding (May):** Finalize rubric interpretations with mentors.
*   **Weeks 1-3:** Building the I/O and Normalization infrastructure.
*   **Weeks 4-6:** **Milestone 1:** Baseline scoring engine functional (scores 0-4).
*   **Weeks 7-9:** **Milestone 2:** Refined ambiguity handling and evaluation suite implemented.
*   **Weeks 10-12:** **Final Deliverable:** Integrated CLI/Web interface, full documentation, and validated benchmark report.

## 9. Repository README Draft
*(See the project's README.md for the professional repository landing page)*

## 10. Expected Outcomes and Impact
*   **Deliverable:** A production-ready Python package for EIT scoring.
*   **Impact:** Reduces scoring time from hours/days to seconds.
*   **Growth:** Provides a standardized benchmark for future Spanish language acquisition research.

## 11. Risks and Mitigation Strategies
*   **Risk:** Edge cases in the rubric. **Mitigation:** Comprehensive logging and "Ambiguity Downgrade" flags.
*   **Risk:** Small sample size for testing. **Mitigation:** Use cross-validation techniques and focus on rule-based rather than over-fit ML approaches.

## 12. Future Work
*   Integration with live audio-to-text engines.
*   Expansion to the English EIT rubric.
*   A hosted web platform for collaborative research.
