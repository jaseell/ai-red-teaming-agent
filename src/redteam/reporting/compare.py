import argparse
import json
from pathlib import Path

from redteam.reporting.regression_comparison import (
    compare_regression_reports,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare two AI red-team regression reports."
    )
    parser.add_argument("previous", help="Path to the previous JSON report")
    parser.add_argument("current", help="Path to the current JSON report")
    parser.add_argument(
        "--output",
        default="reports/regression-comparison.json",
        help="Path to save the comparison JSON",
    )
    args = parser.parse_args()

    comparison = compare_regression_reports(args.previous, args.current)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(comparison, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Regression Report Comparison")
    print("=" * 32)
    for key, value in comparison["summary"].items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    print(f"\nComparison JSON: {output_path}")


if __name__ == "__main__":
    main()
