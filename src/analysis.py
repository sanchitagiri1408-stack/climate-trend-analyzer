"""Summaries, transparent trends, projections, and anomaly detection."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def _with_calendar_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with date-derived fields needed by the aggregations."""
    frame = data.copy()
    if "date" not in frame.columns:
        raise ValueError("Input data must include a date column.")
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame = frame.loc[frame["date"].notna()].copy()
    frame["year"] = frame["date"].dt.year.astype(int)
    frame["month"] = frame["date"].dt.month.astype(int)
    frame["month_name"] = frame["date"].dt.strftime("%B")
    return frame


def _select_region(data: pd.DataFrame, region: str | None) -> pd.DataFrame:
    frame = data
    if region is not None:
        if "region" not in frame.columns:
            raise ValueError("Input data must include a region column.")
        frame = frame.loc[frame["region"].eq(region)].copy()
        if frame.empty:
            raise ValueError(f"No observations found for region: {region}")
    return frame


def annual_summary(data: pd.DataFrame, region: str | None = None) -> pd.DataFrame:
    """Aggregate observations to one row per region and year."""
    frame = _select_region(_with_calendar_columns(data), region)
    required = {"region", "temperature_c", "rainfall_mm", "humidity_pct"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Input data is missing required analysis columns: {', '.join(missing)}")
    aggregation: dict[str, tuple[str, str]] = {
        "mean_temperature_c": ("temperature_c", "mean"),
        "min_temperature_c": ("temperature_c", "min"),
        "max_temperature_c": ("temperature_c", "max"),
        "total_rainfall_mm": ("rainfall_mm", "sum"),
        "mean_humidity_pct": ("humidity_pct", "mean"),
        "records": ("date", "count"),
    }
    if "temperature_anomaly_detected" in frame.columns:
        aggregation["detected_anomalies"] = ("temperature_anomaly_detected", "sum")
    summary = frame.groupby(["region", "year"], as_index=False).agg(**aggregation)
    if "detected_anomalies" in summary.columns:
        summary["detected_anomalies"] = summary["detected_anomalies"].astype(int)
    return summary.sort_values(["region", "year"]).reset_index(drop=True)


def monthly_summary(data: pd.DataFrame, region: str | None = None) -> pd.DataFrame:
    """Aggregate observations to one row per region, year, and month."""
    frame = _select_region(_with_calendar_columns(data), region)
    required = {"region", "temperature_c", "rainfall_mm", "humidity_pct"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Input data is missing required analysis columns: {', '.join(missing)}")
    summary = (
        frame.groupby(["region", "year", "month", "month_name"], as_index=False)
        .agg(
            mean_temperature_c=("temperature_c", "mean"),
            total_rainfall_mm=("rainfall_mm", "sum"),
            mean_humidity_pct=("humidity_pct", "mean"),
            records=("date", "count"),
        )
        .sort_values(["region", "year", "month"])
        .reset_index(drop=True)
    )
    return summary


def linear_temperature_trend(
    annual_data: pd.DataFrame,
    region: str | None = None,
) -> dict[str, Any]:
    """Fit an ordinary least-squares line to annual mean temperature.

    The slope is expressed in degrees Celsius per year. Keeping the year as the
    single predictor makes the calculation easy to inspect and explain.
    """
    annual = annual_data if "mean_temperature_c" in annual_data.columns else annual_summary(annual_data)
    annual = _select_region(annual, region)
    regions = annual["region"].dropna().unique().tolist()
    if len(regions) != 1:
        raise ValueError("linear_temperature_trend requires one region at a time.")
    region_name = str(regions[0])
    annual = annual.sort_values("year")
    x = annual[["year"]].to_numpy(dtype=float)
    y = annual["mean_temperature_c"].to_numpy(dtype=float)
    if len(y) == 0:
        raise ValueError("At least one annual observation is required for a trend.")

    model = LinearRegression().fit(x, y)
    r_squared = float(model.score(x, y)) if len(y) > 1 else 0.0
    slope = float(model.coef_[0])
    return {
        "region": region_name,
        "start_year": int(annual["year"].min()),
        "end_year": int(annual["year"].max()),
        "years_in_model": int(len(annual)),
        "slope_c_per_year": slope,
        "intercept_c": float(model.intercept_),
        "r_squared": r_squared,
        "first_year_mean_temperature_c": float(y[0]),
        "last_year_mean_temperature_c": float(y[-1]),
        "trend_direction": "warming" if slope > 0.01 else "cooling" if slope < -0.01 else "stable",
    }


def calculate_temperature_trends(
    data: pd.DataFrame,
    region: str | None = None,
) -> pd.DataFrame:
    """Return one transparent linear trend record per selected region."""
    annual = data if "mean_temperature_c" in data.columns else annual_summary(data, region=region)
    if region is not None:
        annual = _select_region(annual, region)
    regions = sorted(str(value) for value in annual["region"].dropna().unique())
    return pd.DataFrame(
        [linear_temperature_trend(annual, region=name) for name in regions]
    )


def detect_rolling_zscore_anomalies(
    data: pd.DataFrame,
    *,
    window: int = 30,
    threshold: float = 3.0,
    metric: str = "temperature_c",
) -> pd.DataFrame:
    """Flag observations whose rolling z-score exceeds ``threshold``.

    Rolling statistics are calculated independently per region to avoid blending
    climates with different baselines. The first few rows use the observations
    available so far and a zero z-score when the rolling standard deviation is 0.
    """
    if window < 3:
        raise ValueError("window must be at least 3 observations.")
    if threshold <= 0:
        raise ValueError("threshold must be positive.")
    if metric not in data.columns:
        raise ValueError(f"Input data is missing the metric column: {metric}")
    if "region" not in data.columns or "date" not in data.columns:
        raise ValueError("Input data must include region and date columns.")

    frame = data.copy().sort_values(["region", "date"]).reset_index(drop=True)
    min_periods = max(3, window // 2)
    grouped = frame.groupby("region", sort=False)[metric]
    frame[f"{metric}_rolling_mean"] = grouped.transform(
        lambda values: values.rolling(window=window, min_periods=min_periods).mean()
    )
    frame[f"{metric}_rolling_std"] = grouped.transform(
        lambda values: values.rolling(window=window, min_periods=min_periods).std(ddof=0)
    )
    std = frame[f"{metric}_rolling_std"].replace(0.0, np.nan)
    frame[f"{metric}_z_score"] = (
        (frame[metric] - frame[f"{metric}_rolling_mean"]) / std
    ).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    frame[f"{metric}_anomaly_detected"] = (
        frame[f"{metric}_z_score"].abs() >= float(threshold)
    )
    if metric == "temperature_c":
        frame = frame.rename(
            columns={
                "temperature_c_rolling_mean": "temperature_rolling_mean_c",
                "temperature_c_rolling_std": "temperature_rolling_std_c",
                "temperature_c_z_score": "temperature_z_score",
                "temperature_c_anomaly_detected": "temperature_anomaly_detected",
            }
        )
    return frame


def project_annual_temperature(
    annual_data: pd.DataFrame,
    *,
    years_ahead: int = 5,
    region: str | None = None,
) -> pd.DataFrame:
    """Project annual mean temperature with the same transparent linear model."""
    if years_ahead < 1:
        raise ValueError("years_ahead must be at least 1.")
    annual = annual_data if "mean_temperature_c" in annual_data.columns else annual_summary(annual_data)
    annual = _select_region(annual, region)
    records: list[dict[str, Any]] = []
    for region_name, group in annual.groupby("region", sort=True):
        group = group.sort_values("year")
        x = group[["year"]].to_numpy(dtype=float)
        y = group["mean_temperature_c"].to_numpy(dtype=float)
        model = LinearRegression().fit(x, y)
        historical_years = group["year"].astype(int).tolist()
        for year, value in zip(historical_years, y):
            records.append(
                {
                    "region": str(region_name),
                    "year": int(year),
                    "projected_temperature_c": float(value),
                    "actual_temperature_c": float(value),
                    "forecast_type": "historical",
                }
            )
        last_year = int(group["year"].max())
        future_years = np.arange(last_year + 1, last_year + years_ahead + 1)
        future_values = model.predict(future_years.reshape(-1, 1))
        for year, value in zip(future_years, future_values):
            records.append(
                {
                    "region": str(region_name),
                    "year": int(year),
                    "projected_temperature_c": float(value),
                    "actual_temperature_c": np.nan,
                    "forecast_type": "projection",
                }
            )
    return pd.DataFrame(records).sort_values(["region", "year"]).reset_index(drop=True)
