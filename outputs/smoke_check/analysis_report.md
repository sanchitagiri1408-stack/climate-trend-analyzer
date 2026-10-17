# Climate Trend Analyzer Report

This report uses deterministic synthetic, public-data-style daily observations. It demonstrates a reproducible workflow and should not be interpreted as a measured climate record.

## Scope
- Dates: **2022-01-01** through **2022-12-31**
- Regions: **North, Central, South**
- Random seed: **1**

## Data quality
- Rows before cleaning: **1095**
- Rows after cleaning: **1095**
- Rows with at least one imputed measurement: **39**
- Missing measurements after cleaning: **0**

## Linear temperature trends
The slope is an ordinary least-squares estimate in °C per year using annual mean temperature.
| region | start_year | end_year | slope_c_per_year | r_squared | trend_direction |
| --- | --- | --- | --- | --- | --- |
| Central | 2022 | 2022 | 0.000 | 0.000 | stable |
| North | 2022 | 2022 | 0.000 | 0.000 | stable |
| South | 2022 | 2022 | 0.000 | 0.000 | stable |

## Rolling anomaly detection
- Detected temperature anomalies: **5**
- Injected anomaly rows available for comparison: **6**

## Annual projection
The projection extends the same linear annual model five years beyond the last observed year.
| region | year | projected_temperature_c | forecast_type |
| --- | --- | --- | --- |
| Central | 2023 | 18.125 | projection |
| Central | 2024 | 18.125 | projection |
| Central | 2025 | 18.125 | projection |
| Central | 2026 | 18.125 | projection |
| Central | 2027 | 18.125 | projection |
| North | 2023 | 13.784 | projection |
| North | 2024 | 13.784 | projection |
| North | 2025 | 13.784 | projection |
| North | 2026 | 13.784 | projection |
| North | 2027 | 13.784 | projection |
| South | 2023 | 22.087 | projection |
| South | 2024 | 22.087 | projection |

_Showing the first 12 rows._

## Saved artifacts
- `raw_csv`: `outputs/smoke_check/synthetic_climate_data.csv`
- `cleaned_csv`: `outputs/smoke_check/cleaned_climate_data.csv`
- `annual_summary_csv`: `outputs/smoke_check/annual_summary.csv`
- `monthly_summary_csv`: `outputs/smoke_check/monthly_summary.csv`
- `trend_summary_csv`: `outputs/smoke_check/temperature_trends.csv`
- `anomalies_csv`: `outputs/smoke_check/temperature_anomalies.csv`
- `projection_csv`: `outputs/smoke_check/temperature_projection.csv`
- `annual_temperature_png`: `outputs/smoke_check/annual_temperature.png`
- `monthly_rainfall_png`: `outputs/smoke_check/monthly_rainfall.png`
- `anomalies_png`: `outputs/smoke_check/temperature_anomalies.png`
- `projection_png`: `outputs/smoke_check/temperature_projection.png`
- `report_json`: `outputs/smoke_check/analysis_report.json`
- `report_markdown`: `outputs/smoke_check/analysis_report.md`
