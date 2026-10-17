"""Streamlit dashboard for the synthetic Climate Trend Analyzer."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Make ``streamlit run app/streamlit_app.py`` work from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis import (  # noqa: E402
    annual_summary,
    calculate_temperature_trends,
    detect_rolling_zscore_anomalies,
    monthly_summary,
    project_annual_temperature,
)
from src.config import AnalyzerConfig, DEFAULT_REGIONS  # noqa: E402
from src.data_cleaning import clean_data  # noqa: E402
from src.data_generator import generate_synthetic_data  # noqa: E402


@st.cache_data(show_spinner=False)
def build_dashboard_data(start_date: str, end_date: str, seed: int) -> dict[str, pd.DataFrame]:
    """Generate the dashboard dataset once per set of sidebar controls."""
    config = AnalyzerConfig(start_date=start_date, end_date=end_date, random_seed=seed)
    raw = generate_synthetic_data(config)
    cleaned = clean_data(raw)
    annual = annual_summary(cleaned)
    monthly = monthly_summary(cleaned)
    anomalies = detect_rolling_zscore_anomalies(cleaned)
    trends = calculate_temperature_trends(annual)
    projection = project_annual_temperature(annual)
    return {
        "raw": raw,
        "cleaned": cleaned,
        "annual": annual,
        "monthly": monthly,
        "anomalies": anomalies,
        "trends": trends,
        "projection": projection,
    }


def _filter_region(data: pd.DataFrame, region: str) -> pd.DataFrame:
    if region == "All regions":
        return data
    return data.loc[data["region"].eq(region)].copy()


def main() -> None:
    st.set_page_config(page_title="Climate Trend Analyzer", page_icon="🌍", layout="wide")
    st.title("🌍 Climate Trend Analyzer")
    st.caption("A reproducible synthetic climate workflow: clean, summarize, detect, and project.")

    with st.sidebar:
        st.header("Controls")
        region = st.selectbox("Region", ["All regions", *DEFAULT_REGIONS])
        start_date = st.date_input("Start date", value=pd.Timestamp("2015-01-01").date())
        end_date = st.date_input("End date", value=pd.Timestamp("2024-12-31").date())
        seed = st.number_input("Random seed", min_value=0, value=42, step=1)
        st.info("The data is simulated for learning and demonstration; it is not an observed climate record.")

    if start_date > end_date:
        st.error("Start date must be on or before end date.")
        st.stop()

    data = build_dashboard_data(start_date.isoformat(), end_date.isoformat(), int(seed))
    annual = _filter_region(data["annual"], region)
    monthly = _filter_region(data["monthly"], region)
    anomalies = _filter_region(data["anomalies"], region)
    trends = _filter_region(data["trends"], region)
    projection = _filter_region(data["projection"], region)
    cleaned = _filter_region(data["cleaned"], region)

    metric_columns = st.columns(4)
    metric_columns[0].metric("Cleaned observations", f"{len(cleaned):,}")
    metric_columns[1].metric("Average temperature", f"{cleaned['temperature_c'].mean():.1f} °C")
    metric_columns[2].metric("Rainfall total", f"{cleaned['rainfall_mm'].sum():,.0f} mm")
    metric_columns[3].metric(
        "Detected anomalies",
        f"{int(anomalies['temperature_anomaly_detected'].sum()):,}",
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Annual temperature")
        annual_chart = annual.pivot(index="year", columns="region", values="mean_temperature_c")
        st.line_chart(annual_chart)
    with right:
        st.subheader("Average monthly rainfall")
        rainfall_chart = (
            monthly.groupby(["month", "month_name", "region"], as_index=False)
            .agg(mean_rainfall_mm=("total_rainfall_mm", "mean"))
            .sort_values("month")
            .pivot(index="month_name", columns="region", values="mean_rainfall_mm")
        )
        st.line_chart(rainfall_chart)

    st.subheader("Linear temperature trends")
    st.dataframe(trends, use_container_width=True, hide_index=True)

    st.subheader("Annual temperature projection")
    projection_chart = projection.pivot(
        index="year", columns="region", values="projected_temperature_c"
    )
    st.line_chart(projection_chart)

    st.subheader("Rolling z-score anomalies")
    st.dataframe(
        anomalies.loc[
            anomalies["temperature_anomaly_detected"],
            ["date", "region", "temperature_c", "temperature_z_score"],
        ].tail(25),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Download cleaned data")
    st.download_button(
        "Download CSV",
        data["cleaned"].to_csv(index=False).encode("utf-8"),
        file_name="cleaned_climate_data.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
