"""End-to-end orchestration and artifact writing."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from .analysis import (
    annual_summary,
    calculate_temperature_trends,
    detect_rolling_zscore_anomalies,
    monthly_summary,
    project_annual_temperature,
)
from .config import AnalyzerConfig
from .data_cleaning import CleaningReport, clean_data_with_report
from .data_generator import generate_synthetic_data
from .visualization import (
    plot_annual_temperature,
    plot_anomaly_detection,
    plot_monthly_rainfall,
    plot_temperature_projection,
)


@dataclass
class PipelineResult:
    """In-memory results and paths produced by :func:`run_pipeline`."""

    raw_data: pd.DataFrame
    cleaned_data: pd.DataFrame
    annual_summary: pd.DataFrame
    monthly_summary: pd.DataFrame
    trend_summary: pd.DataFrame
    anomaly_data: pd.DataFrame
    projection: pd.DataFrame
    cleaning_report: CleaningReport
    output_paths: dict[str, Path]
    report: dict[str, Any]


def _csv_ready(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()
    if "date" in frame.columns:
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return frame


def _records(data: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert pandas/numpy values to standard JSON-compatible values."""
    if data.empty:
        return []
    return json.loads(data.to_json(orient="records", date_format="iso"))


def _markdown_table(data: pd.DataFrame, columns: list[str], max_rows: int = 12) -> str:
    available = [column for column in columns if column in data.columns]
    if not available or data.empty:
        return "_No rows available._"
    view = data.loc[:, available].head(max_rows).copy()
    lines = [
        "| " + " | ".join(available) + " |",
        "| " + " | ".join("---" for _ in available) + " |",
    ]
    for row in view.itertuples(index=False, name=None):
        values: list[str] = []
        for value in row:
            if isinstance(value, float):
                values.append(f"{value:.3f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    if len(data) > max_rows:
        lines.append(f"\n_Showing the first {max_rows} rows._")
    return "\n".join(lines)


def _write_markdown_report(
    path: Path,
    *,
    config: AnalyzerConfig,
    selected_region: str | None,
    cleaning_report: CleaningReport,
    trends: pd.DataFrame,
    anomalies: pd.DataFrame,
    projection: pd.DataFrame,
    output_paths: dict[str, Path],
) -> None:
    detected_count = int(anomalies["temperature_anomaly_detected"].sum())
    injected_count = int(anomalies.get("is_injected_anomaly", pd.Series(dtype=bool)).sum())
    lines = [
        "# Climate Trend Analyzer Report",
        "",
        "This report uses deterministic synthetic, public-data-style daily observations. It demonstrates a reproducible workflow and should not be interpreted as a measured climate record.",
        "",
        "## Scope",
        f"- Dates: **{config.start_date}** through **{config.end_date}**",
        f"- Regions: **{selected_region or ', '.join(config.regions)}**",
        f"- Random seed: **{config.random_seed}**",
        "",
        "## Data quality",
        f"- Rows before cleaning: **{cleaning_report.rows_before}**",
        f"- Rows after cleaning: **{cleaning_report.rows_after}**",
        f"- Rows with at least one imputed measurement: **{cleaning_report.imputed_rows}**",
        f"- Missing measurements after cleaning: **{sum(cleaning_report.missing_values_after.values())}**",
        "",
        "## Linear temperature trends",
        "The slope is an ordinary least-squares estimate in °C per year using annual mean temperature.",
        _markdown_table(
            trends,
            ["region", "start_year", "end_year", "slope_c_per_year", "r_squared", "trend_direction"],
        ),
        "",
        "## Rolling anomaly detection",
        f"- Detected temperature anomalies: **{detected_count}**",
        f"- Injected anomaly rows available for comparison: **{injected_count}**",
        "",
        "## Annual projection",
        "The projection extends the same linear annual model five years beyond the last observed year.",
        _markdown_table(
            projection.loc[projection["forecast_type"].eq("projection")],
            ["region", "year", "projected_temperature_c", "forecast_type"],
        ),
        "",
        "## Saved artifacts",
    ]
    lines.extend(f"- `{label}`: `{artifact}`" for label, artifact in output_paths.items())
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_pipeline(
    config: AnalyzerConfig | None = None,
    *,
    region: str | None = None,
    output_dir: str | Path | None = None,
) -> PipelineResult:
    """Run generation, cleaning, analysis, visualization, and artifact writing."""
    config = config or AnalyzerConfig()
    if region is not None and region not in config.regions:
        available = ", ".join(config.regions)
        raise ValueError(f"Unknown region '{region}'. Choose one of: {available}")

    destination = Path(output_dir) if output_dir is not None else Path(config.output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    raw_data = generate_synthetic_data(config)
    selected_raw = raw_data if region is None else raw_data.loc[raw_data["region"].eq(region)].copy()

    # Filter before cleaning so region-specific runs report quality metrics for
    # the same rows that are actually written to the selected output directory.
    selected_cleaned, cleaning_report = clean_data_with_report(selected_raw)

    annual = annual_summary(selected_cleaned)
    monthly = monthly_summary(selected_cleaned)
    trends = calculate_temperature_trends(annual)
    anomalies = detect_rolling_zscore_anomalies(selected_cleaned)
    projection = project_annual_temperature(annual, years_ahead=5)

    output_paths: dict[str, Path] = {
        "raw_csv": destination / "synthetic_climate_data.csv",
        "cleaned_csv": destination / "cleaned_climate_data.csv",
        "annual_summary_csv": destination / "annual_summary.csv",
        "monthly_summary_csv": destination / "monthly_summary.csv",
        "trend_summary_csv": destination / "temperature_trends.csv",
        "anomalies_csv": destination / "temperature_anomalies.csv",
        "projection_csv": destination / "temperature_projection.csv",
        "annual_temperature_png": destination / "annual_temperature.png",
        "monthly_rainfall_png": destination / "monthly_rainfall.png",
        "anomalies_png": destination / "temperature_anomalies.png",
        "projection_png": destination / "temperature_projection.png",
        "report_json": destination / "analysis_report.json",
        "report_markdown": destination / "analysis_report.md",
    }

    _csv_ready(selected_raw).to_csv(output_paths["raw_csv"], index=False)
    _csv_ready(selected_cleaned).to_csv(output_paths["cleaned_csv"], index=False)
    annual.to_csv(output_paths["annual_summary_csv"], index=False)
    monthly.to_csv(output_paths["monthly_summary_csv"], index=False)
    trends.to_csv(output_paths["trend_summary_csv"], index=False)
    _csv_ready(anomalies).to_csv(output_paths["anomalies_csv"], index=False)
    projection.to_csv(output_paths["projection_csv"], index=False)

    plot_annual_temperature(annual, output_paths["annual_temperature_png"])
    plot_monthly_rainfall(monthly, output_paths["monthly_rainfall_png"])
    plot_anomaly_detection(anomalies, output_paths["anomalies_png"])
    plot_temperature_projection(projection, output_paths["projection_png"])

    report_config = config.as_dict()
    report_config["output_dir"] = str(destination)
    report: dict[str, Any] = {
        "config": report_config,
        "selected_region": region,
        "data_quality": cleaning_report.as_dict(),
        "summary_rows": {
            "annual": int(len(annual)),
            "monthly": int(len(monthly)),
            "anomalies": int(len(anomalies)),
            "projection": int(len(projection)),
        },
        "anomaly_counts": {
            "detected_temperature_anomalies": int(anomalies["temperature_anomaly_detected"].sum()),
            "injected_anomaly_rows": int(anomalies.get("is_injected_anomaly", pd.Series(dtype=bool)).sum()),
        },
        "trends": _records(trends),
        "projection_preview": _records(projection.loc[projection["forecast_type"].eq("projection")]),
        "outputs": {label: str(path) for label, path in output_paths.items()},
    }
    output_paths["report_json"].write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    _write_markdown_report(
        output_paths["report_markdown"],
        config=config,
        selected_region=region,
        cleaning_report=cleaning_report,
        trends=trends,
        anomalies=anomalies,
        projection=projection,
        output_paths=output_paths,
    )

    return PipelineResult(
        raw_data=selected_raw,
        cleaned_data=selected_cleaned,
        annual_summary=annual,
        monthly_summary=monthly,
        trend_summary=trends,
        anomaly_data=anomalies,
        projection=projection,
        cleaning_report=cleaning_report,
        output_paths=output_paths,
        report=report,
    )
