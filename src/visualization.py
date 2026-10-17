"""Small, reusable Matplotlib/Seaborn charts for saved analysis outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Keep CLI/test runs safe on headless machines.

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", context="notebook")

MONTH_ORDER = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def _prepare_output(path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def _filter_region(data: pd.DataFrame, region: str | None) -> pd.DataFrame:
    frame = data.copy()
    if region is not None:
        frame = frame.loc[frame["region"].eq(region)].copy()
    if frame.empty:
        raise ValueError("There are no rows available for this chart.")
    return frame


def plot_annual_temperature(
    annual_data: pd.DataFrame,
    output_path: str | Path,
    *,
    region: str | None = None,
) -> Path:
    """Save annual mean temperature by region."""
    frame = _filter_region(annual_data, region)
    path = _prepare_output(output_path)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.lineplot(
        data=frame,
        x="year",
        y="mean_temperature_c",
        hue="region",
        marker="o",
        linewidth=2,
        ax=ax,
    )
    ax.set(title="Annual Mean Temperature", xlabel="Year", ylabel="Temperature (°C)")
    ax.legend(title="Region", loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def plot_monthly_rainfall(
    monthly_data: pd.DataFrame,
    output_path: str | Path,
    *,
    region: str | None = None,
) -> Path:
    """Save the average monthly rainfall profile across observed years."""
    frame = _filter_region(monthly_data, region)
    profile = (
        frame.groupby(["region", "month", "month_name"], as_index=False)
        .agg(mean_monthly_rainfall_mm=("total_rainfall_mm", "mean"))
        .sort_values(["region", "month"])
    )
    profile["month_name"] = pd.Categorical(
        profile["month_name"], categories=MONTH_ORDER, ordered=True
    )
    path = _prepare_output(output_path)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.lineplot(
        data=profile,
        x="month_name",
        y="mean_monthly_rainfall_mm",
        hue="region",
        marker="o",
        linewidth=2,
        ax=ax,
    )
    ax.set(title="Average Monthly Rainfall", xlabel="Month", ylabel="Rainfall (mm)")
    ax.tick_params(axis="x", rotation=35)
    ax.legend(title="Region", loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def plot_anomaly_detection(
    anomaly_data: pd.DataFrame,
    output_path: str | Path,
    *,
    region: str | None = None,
) -> Path:
    """Save observed temperature, rolling baseline, and detected anomalies."""
    frame = _filter_region(anomaly_data, region)
    path = _prepare_output(output_path)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    for region_name, group in frame.groupby("region", sort=True):
        group = group.sort_values("date")
        ax.plot(group["date"], group["temperature_c"], linewidth=0.8, alpha=0.45, label=f"{region_name} daily")
        ax.plot(
            group["date"],
            group["temperature_rolling_mean_c"],
            linewidth=2,
            label=f"{region_name} rolling mean",
        )
        detected = group.loc[group["temperature_anomaly_detected"]]
        if not detected.empty:
            ax.scatter(
                detected["date"],
                detected["temperature_c"],
                color="crimson",
                s=22,
                zorder=4,
                label=f"{region_name} anomaly",
            )
    ax.set(title="Rolling Z-Score Temperature Anomalies", xlabel="Date", ylabel="Temperature (°C)")
    ax.legend(loc="best", ncol=2)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def plot_temperature_projection(
    projection_data: pd.DataFrame,
    output_path: str | Path,
    *,
    region: str | None = None,
) -> Path:
    """Save historical annual means and dashed linear projections."""
    frame = _filter_region(projection_data, region)
    path = _prepare_output(output_path)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for region_name, group in frame.groupby("region", sort=True):
        group = group.sort_values("year")
        historical = group.loc[group["forecast_type"].eq("historical")]
        future = group.loc[group["forecast_type"].eq("projection")]
        (line,) = ax.plot(
            historical["year"],
            historical["projected_temperature_c"],
            marker="o",
            linewidth=2,
            label=f"{region_name} historical",
        )
        ax.plot(
            future["year"],
            future["projected_temperature_c"],
            linestyle="--",
            linewidth=2,
            color=line.get_color(),
            label=f"{region_name} projection",
        )
    ax.set(title="Simple Annual Temperature Projection", xlabel="Year", ylabel="Temperature (°C)")
    ax.legend(loc="best", ncol=2)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path
