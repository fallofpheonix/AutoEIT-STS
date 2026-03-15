# Contributing to AutoEIT-STS

Thank you for your interest in contributing to the Automated Scoring & Transcription Suite (AutoEIT-STS)! We aim to provide a robust and reproducible tool for the linguistics research community.

## 📝 Code of Conduct
Please be respectful and professional in all interactions within this project.

## 🛠 Getting Started
1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone https://github.com/YOUR_USERNAME/AutoEIT-STS.git
    ```
3.  **Create a branch** for your feature or bugfix:
    ```bash
    git checkout -b feature/your-feature-name
    ```

## 🏗 Development Standards
*   **Determinism is Key:** Any changes to the scoring logic must remain 100% deterministic. Avoid using stochastic models (like unconstrained LLMs) for core scoring decisions.
*   **Test-Driven Development:** Add unit tests for any new normalization rules or feature extractors in the `tests/` directory (or appropriate module).
*   **Documentation:** Update the `README.md` or internal documentation if your changes introduce new CLI parameters or workflow changes.

## 🧪 Testing
Before submitting a Pull Request, ensure that all tests pass:
```bash
pytest tests/
```
Also, run the benchmark script to ensure no regression in agreement with human ratings:
```bash
python -m src.evaluation.benchmark
```

## 📬 Submitting Changes
1.  **Commit your changes** with clear, descriptive messages.
2.  **Push to your fork** and submit a **Pull Request**.
3.  Provide a clear description of the problem you are solving and the verification steps you took.

## 🎓 GSoC Applicants
If you are contributing as part of a GSoC proposal, please clearly state this in your PR description. Focus on tasks identified in the [gsoc_proposal.md](gsoc_proposal.md) roadmap.
