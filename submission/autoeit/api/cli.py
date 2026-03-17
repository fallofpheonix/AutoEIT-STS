"""CLI entry point for AutoEIT-STS.

Usage:
    python -m autoeit score --input workbooks/file.xlsx --output-dir output/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from autoeit.services.scoring import score_and_export


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="autoeit",
        description="Deterministic scorer for the Spanish Elicited Imitation Task.",
    )
    p.add_argument("--input", required=True, type=Path, metavar="XLSX",
                   help="Path to the transcription workbook.")
    p.add_argument("--output-xlsx", required=True, type=Path, metavar="XLSX",
                   help="Where to write the annotated output workbook.")
    p.add_argument("--output-csv", required=True, type=Path, metavar="CSV",
                   help="Where to write the flat scores CSV.")
    p.add_argument("--downgrades-csv", type=Path, default=None,
                   help="Optional: separate path for the ambiguous-downgrade audit log.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    _, metrics, xlsx, csv_, dl = score_and_export(
        source_path=args.input,
        output_xlsx=args.output_xlsx,
        output_csv=args.output_csv,
        downgrades_csv=args.downgrades_csv,
    )

    print(f"  workbook  : {xlsx}")
    print(f"  scores    : {csv_}")
    print(f"  downgrades: {dl}")

    if metrics:
        print("\nAgreement metrics:")
        for k, v in metrics.items():
            if k == "confusion_matrix":
                print(f"\n{v}\n")
            else:
                print(f"  {k}: {v}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
