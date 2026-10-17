"""Command-line entry point for the Climate Trend Analyzer."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from src.config import AnalyzerConfig
from src.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate and analyze synthetic daily climate observations."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Write the complete set of CSV, PNG, JSON, and Markdown artifacts (the default workflow).",
    )
    parser.add_argument(
        "--region",
        help="Analyze one configured region (North, Central, or South).",
    )
    parser.add_argument("--start-date", default="2015-01-01", help="First date, YYYY-MM-DD.")
    parser.add_argument("--end-date", default="2024-12-31", help="Last date, YYYY-MM-DD.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible data.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Directory for generated artifacts (default: outputs).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = AnalyzerConfig(
            start_date=args.start_date,
            end_date=args.end_date,
            random_seed=args.seed,
            output_dir=args.output_dir,
        )
        result = run_pipeline(config, region=args.region)
    except (TypeError, ValueError) as exc:
        parser.error(str(exc))

    # --all is intentionally explicit in the documented happy path, but the
    # pipeline remains useful without it for quick exploratory CLI runs.
    print(f"Analyzed {len(result.cleaned_data):,} cleaned daily observations.")
    print(f"Regions: {', '.join(sorted(result.cleaned_data['region'].unique()))}")
    print(f"Detected anomalies: {result.report['anomaly_counts']['detected_temperature_anomalies']}")
    print("Saved artifacts:")
    for label, path in result.output_paths.items():
        print(f"  {label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
