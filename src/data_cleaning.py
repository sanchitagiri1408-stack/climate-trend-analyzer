"""Validation and transparent missing-value treatment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .data_generator import MEASUREMENT_COLUMNS

REQUIRED_COLUMNS = {
    "date",
    "region",
    *MEASUREMENT_COLUMNS,
}


@dataclass(frozen=True)
class CleaningReport:
    """Small audit record describing the cleaning operation."""

    rows_before: int
    rows_after: int
    invalid_rows_dropped: int
    missing_values_before: dict[str, int]
    missing_values_after: dict[str, int]
    imputed_rows: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "rows_before": self.rows_before,
            "rows_after": self.rows_after,
            "invalid_rows_dropped": self.invalid_rows_dropped,
            "missing_values_before": dict(self.missing_values_before),
            "missing_values_after": dict(self.missing_values_after),
            "imputed_rows": self.imputed_rows,
        }


def validate_columns(data: pd.DataFrame) -> None:
    """Raise a clear error when an input table is missing required fields."""
    missing = sorted(REQUIRED_COLUMNS.difference(data.columns))
    if missing:
        raise ValueError(f"Input data is missing required columns: {', '.join(missing)}")


def clean_data_with_report(data: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """Clean observations and return the cleaned table plus an audit report.

    Numeric measurements are interpolated within each region in date order and
    then filled with the region/global median as a safe fallback. Physical bounds
    are enforced for rainfall and humidity after imputation.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    validate_columns(data)

    rows_before = len(data)
    missing_before = {
        column: int(data[column].isna().sum()) for column in MEASUREMENT_COLUMNS
    }
    cleaned = data.copy()
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    cleaned["region"] = cleaned["region"].astype("string").str.strip()
    invalid_mask = cleaned["date"].isna() | cleaned["region"].isna() | cleaned["region"].eq("")
    invalid_rows_dropped = int(invalid_mask.sum())
    cleaned = cleaned.loc[~invalid_mask].copy()
    cleaned = cleaned.sort_values(["region", "date"]).reset_index(drop=True)

    # Preserve an auditable row-level marker before any values are filled.
    cleaned["was_imputed"] = cleaned[list(MEASUREMENT_COLUMNS)].isna().any(axis=1)
    for column in MEASUREMENT_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
        cleaned[f"{column}_was_imputed"] = cleaned[column].isna()
        cleaned[column] = cleaned.groupby("region")[column].transform(
            lambda values: values.interpolate(method="linear", limit_direction="both")
        )
        cleaned[column] = cleaned.groupby("region")[column].transform(
            lambda values: values.fillna(values.median())
        )
        global_median = cleaned[column].median()
        fallback = {
            "temperature_c": 0.0,
            "rainfall_mm": 0.0,
            "humidity_pct": 50.0,
        }[column]
        if pd.isna(global_median):
            global_median = fallback
        cleaned[column] = cleaned[column].fillna(float(global_median))

    cleaned["rainfall_mm"] = cleaned["rainfall_mm"].clip(lower=0.0)
    cleaned["humidity_pct"] = cleaned["humidity_pct"].clip(lower=0.0, upper=100.0)
    for flag_column in ("is_injected_anomaly", "is_missing_injected"):
        if flag_column not in cleaned.columns:
            cleaned[flag_column] = False
        cleaned[flag_column] = cleaned[flag_column].fillna(False).astype(bool)
    cleaned["year"] = cleaned["date"].dt.year.astype(int)
    cleaned["month"] = cleaned["date"].dt.month.astype(int)
    cleaned["month_name"] = cleaned["date"].dt.strftime("%B")
    cleaned["quarter"] = cleaned["date"].dt.quarter.astype(int)
    cleaned["day_of_year"] = cleaned["date"].dt.dayofyear.astype(int)

    missing_after = {
        column: int(cleaned[column].isna().sum()) for column in MEASUREMENT_COLUMNS
    }
    report = CleaningReport(
        rows_before=rows_before,
        rows_after=len(cleaned),
        invalid_rows_dropped=invalid_rows_dropped,
        missing_values_before=missing_before,
        missing_values_after=missing_after,
        imputed_rows=int(cleaned["was_imputed"].sum()),
    )
    return cleaned, report


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Return only the cleaned table for callers that do not need the audit."""
    cleaned, _ = clean_data_with_report(data)
    return cleaned
