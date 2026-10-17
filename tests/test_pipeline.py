"""Meaningful behavior checks for the Climate Trend Analyzer."""

from __future__ import annotations

import json

import pandas as pd

from src.analysis import detect_rolling_zscore_anomalies, project_annual_temperature
from src.config import AnalyzerConfig
from src.data_cleaning import clean_data, clean_data_with_report
from src.data_generator import generate_synthetic_data
from src.pipeline import run_pipeline


def small_config(tmp_path) -> AnalyzerConfig:
    return AnalyzerConfig(
        start_date="2020-01-01",
        end_date="2021-12-31",
        random_seed=7,
        output_dir=tmp_path,
    )


def test_generation_has_daily_regions_seasonality_and_injections() -> None:
    config = AnalyzerConfig(start_date="2020-01-01", end_date="2020-12-31", random_seed=11)
    data = generate_synthetic_data(config)

    assert len(data) == 366 * 3
    assert set(data["region"]) == {"North", "Central", "South"}
    assert data["date"].nunique() == 366
    assert {"Winter", "Spring", "Summer", "Autumn"}.issubset(set(data["season"]))
    assert int(data["is_injected_anomaly"].sum()) > 0
    assert int(data["is_missing_injected"].sum()) > 0


def test_cleaning_imputes_measurements_and_enforces_bounds() -> None:
    raw = generate_synthetic_data(
        AnalyzerConfig(start_date="2020-01-01", end_date="2020-12-31", random_seed=3)
    )
    cleaned, report = clean_data_with_report(raw)

    assert report.rows_before == report.rows_after
    assert report.imputed_rows > 0
    assert cleaned[["temperature_c", "rainfall_mm", "humidity_pct"]].isna().sum().sum() == 0
    assert (cleaned["rainfall_mm"] >= 0).all()
    assert cleaned["humidity_pct"].between(0, 100).all()
    assert clean_data(raw).equals(cleaned)


def test_analysis_detects_anomalies_and_projects_future_years() -> None:
    config = AnalyzerConfig(start_date="2018-01-01", end_date="2022-12-31", random_seed=5)
    cleaned = clean_data(generate_synthetic_data(config))
    anomalies = detect_rolling_zscore_anomalies(cleaned, window=30, threshold=2.5)
    assert "temperature_anomaly_detected" in anomalies.columns
    assert anomalies["temperature_anomaly_detected"].dtype == bool
    assert int(anomalies["temperature_anomaly_detected"].sum()) > 0

    annual = cleaned.assign(year=pd.to_datetime(cleaned["date"]).dt.year).groupby(
        ["region", "year"], as_index=False
    ).agg(mean_temperature_c=("temperature_c", "mean"))
    projection = project_annual_temperature(annual, years_ahead=3, region="North")
    assert projection["forecast_type"].eq("projection").sum() == 3
    assert projection["year"].max() == 2025


def test_pipeline_writes_requested_artifacts_and_supports_region(tmp_path) -> None:
    config = small_config(tmp_path)
    result = run_pipeline(config, region="North")

    assert set(result.annual_summary["region"]) == {"North"}
    assert set(result.trend_summary["region"]) == {"North"}
    assert set(result.raw_data["region"]) == {"North"}
    assert result.cleaning_report.rows_before == len(result.raw_data)
    expected_suffixes = {".csv", ".png", ".json", ".md"}
    assert expected_suffixes.issubset({path.suffix for path in result.output_paths.values()})
    for path in result.output_paths.values():
        assert path.exists()
        assert path.stat().st_size > 0

    report = json.loads(result.output_paths["report_json"].read_text(encoding="utf-8"))
    assert report["selected_region"] == "North"
    assert report["data_quality"]["missing_values_after"]["temperature_c"] == 0
