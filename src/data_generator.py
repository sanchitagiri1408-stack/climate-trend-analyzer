"""Deterministic synthetic climate data generation.

The generator intentionally resembles a public daily observation table while making
its assumptions visible. It is suitable for demos, tests, and dashboard examples;
it is not a substitute for a measured climate data source.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

from .config import AnalyzerConfig

MEASUREMENT_COLUMNS: Final[tuple[str, ...]] = (
    "temperature_c",
    "rainfall_mm",
    "humidity_pct",
)

REGION_PROFILES: Final[dict[str, dict[str, float]]] = {
    "North": {
        "temperature_offset": -2.0,
        "temperature_amplitude": 13.0,
        "rainfall_factor": 1.15,
        "humidity_offset": 4.0,
    },
    "Central": {
        "temperature_offset": 2.0,
        "temperature_amplitude": 10.0,
        "rainfall_factor": 1.0,
        "humidity_offset": 0.0,
    },
    "South": {
        "temperature_offset": 6.0,
        "temperature_amplitude": 8.0,
        "rainfall_factor": 0.8,
        "humidity_offset": -4.0,
    },
}

MONTH_TO_SEASON: Final[dict[int, str]] = {
    1: "Winter",
    2: "Winter",
    3: "Spring",
    4: "Spring",
    5: "Spring",
    6: "Summer",
    7: "Summer",
    8: "Summer",
    9: "Autumn",
    10: "Autumn",
    11: "Autumn",
    12: "Winter",
}


def season_for_month(month: int) -> str:
    """Return a simple Northern Hemisphere season label."""
    try:
        return MONTH_TO_SEASON[int(month)]
    except KeyError as exc:
        raise ValueError(f"month must be between 1 and 12, got {month}") from exc


def _profile_for_region(region: str) -> dict[str, float]:
    """Use a neutral profile for custom region names in exploratory work."""
    return REGION_PROFILES.get(
        region,
        {
            "temperature_offset": 0.0,
            "temperature_amplitude": 10.0,
            "rainfall_factor": 1.0,
            "humidity_offset": 0.0,
        },
    )


def generate_synthetic_data(config: AnalyzerConfig | None = None) -> pd.DataFrame:
    """Generate daily observations for each configured region.

    The output includes seasonal calendar columns, ground-truth anomaly flags, and
    a missing-value injection flag so cleaning and anomaly detection can be taught
    and evaluated transparently.
    """
    config = config or AnalyzerConfig()
    dates = pd.date_range(config.start_date, config.end_date, freq="D")
    if dates.empty:
        raise ValueError("The configured date range contains no dates.")

    rng = np.random.default_rng(config.random_seed)
    date_years = dates.year.to_numpy(dtype=float)
    day_of_year = dates.dayofyear.to_numpy(dtype=float)
    elapsed_years = (date_years - float(config.start.year)) + (day_of_year - 1.0) / 365.25
    seasonal_wave = np.sin(2.0 * np.pi * (day_of_year - 80.0) / 365.25)
    rainfall_wave = np.maximum(0.0, np.sin(2.0 * np.pi * (day_of_year - 35.0) / 365.25))

    region_frames: list[pd.DataFrame] = []
    for region in config.regions:
        profile = _profile_for_region(region)
        temperature = (
            16.0
            + profile["temperature_offset"]
            + profile["temperature_amplitude"] * seasonal_wave
            + 0.035 * elapsed_years
            + rng.normal(0.0, 2.0, size=len(dates))
        )
        rainfall = (
            rng.gamma(shape=1.7, scale=2.6, size=len(dates))
            * profile["rainfall_factor"]
            * (0.65 + 0.9 * rainfall_wave)
        )
        humidity = np.clip(
            64.0
            + profile["humidity_offset"]
            + 11.0 * rainfall_wave
            - 0.22 * (temperature - 16.0)
            + rng.normal(0.0, 5.0, size=len(dates)),
            15.0,
            100.0,
        )

        # Inject a small number of deliberately obvious events per region.
        anomaly_count = max(1, int(len(dates) * 0.008))
        anomaly_indices = rng.choice(len(dates), size=anomaly_count, replace=False)
        injected_anomaly = np.zeros(len(dates), dtype=bool)
        injected_anomaly[anomaly_indices] = True
        temperature[anomaly_indices] += rng.choice(
            np.array([-1.0, 1.0]), size=anomaly_count
        ) * rng.uniform(6.0, 10.0, size=anomaly_count)
        rainfall[anomaly_indices] *= rng.uniform(3.0, 6.0, size=anomaly_count)
        humidity[anomaly_indices] = np.clip(
            humidity[anomaly_indices] + rng.choice(np.array([-1.0, 1.0]), size=anomaly_count) * 18.0,
            5.0,
            100.0,
        )

        frame = pd.DataFrame(
            {
                "date": dates,
                "region": region,
                "temperature_c": temperature,
                "rainfall_mm": rainfall,
                "humidity_pct": humidity,
                "season": [season_for_month(month) for month in dates.month],
                "year": dates.year.to_numpy(dtype=int),
                "month": dates.month.to_numpy(dtype=int),
                "month_name": dates.strftime("%B"),
                "quarter": dates.quarter.to_numpy(dtype=int),
                "day_of_year": dates.dayofyear.to_numpy(dtype=int),
                "is_injected_anomaly": injected_anomaly,
            }
        )
        region_frames.append(frame)

    data = pd.concat(region_frames, ignore_index=True)

    # Missingness is injected only into measurements, never identifiers or dates.
    missing_mask = np.zeros(len(data), dtype=bool)
    for column in MEASUREMENT_COLUMNS:
        column_mask = rng.random(len(data)) < 0.012
        data.loc[column_mask, column] = np.nan
        missing_mask |= column_mask
    data["is_missing_injected"] = missing_mask

    return data.sort_values(["region", "date"]).reset_index(drop=True)
