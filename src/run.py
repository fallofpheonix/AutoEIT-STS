"""CLI entrypoint for Task II."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.scorer import score_workbook


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AutoEIT Task II deterministic scorer")
    parser.add_argument("--input-xlsx", type=Path, required=True)
    parser.add_argument("--output-xlsx", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--downgrade-csv", type=Path, default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    _, metrics, workbook_path, csv_path, downgrade_path = score_workbook(
        source_path=args.input_xlsx,
        output_xlsx=args.output_xlsx,
        output_csv=args.output_csv,
        downgrade_csv=args.downgrade_csv,
    )
    print(f"Workbook: {workbook_path}")
    print(f"CSV: {csv_path}")
    print(f"Ambiguous downgrade log: {downgrade_path}")
    if metrics:
        print("Metrics:")
        for key, value in metrics.items():
            if key == "confusion_summary":
                print(f"{key}:\n{value}")
            else:
                print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
