import argparse

from redteam.core.session import SessionLocal
from redteam.reporting.security_summary import (
    write_security_summary_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate an AI red-team security summary report."
    )
    parser.add_argument(
        "--output",
        default="reports/security-summary.json",
        help="Path to save the JSON report",
    )
    args = parser.parse_args()

    with SessionLocal() as db_session:
        output_path = write_security_summary_report(
            db_session,
            args.output,
        )

    print("AI Red Teaming - Security Summary")
    print("=" * 36)
    print(f"JSON report: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
