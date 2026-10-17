# Climate Trend Analyzer Report

This report uses deterministic synthetic, public-data-style daily observations. It demonstrates a reproducible workflow and should not be interpreted as a measured climate record.

## Scope
- Dates: **2020-01-01** through **2021-12-31**
- Regions: **North, Central, South**
- Random seed: **7**

## Data quality
- Rows before cleaning: **2193**
- Rows after cleaning: **2193**
- Rows with at least one imputed measurement: **55**
- Missing measurements after cleaning: **0**

## Linear temperature trends
The slope is an ordinary least-squares estimate in °C per year using annual mean temperature.
| region | start_year | end_year | slope_c_per_year | r_squared | trend_direction |
| --- | --- | --- | --- | --- | --- |
| Central | 2020 | 2021 | -0.063 | 1.000 | cooling |
| North | 2020 | 2021 | 0.007 | 1.000 | stable |
| South | 2020 | 2021 | 0.130 | 1.000 | warming |

## Rolling anomaly detection
- Detected temperature anomalies: **14**
- Injected anomaly rows available for comparison: **15**

## Annual projection
The projection extends the same linear annual model five years beyond the last observed year.
| region | year | projected_temperature_c | forecast_type |
| --- | --- | --- | --- |
| Central | 2022 | 17.945 | projection |
| Central | 2023 | 17.881 | projection |
| Central | 2024 | 17.818 | projection |
| Central | 2025 | 17.755 | projection |
| Central | 2026 | 17.691 | projection |
| North | 2022 | 13.785 | projection |
| North | 2023 | 13.792 | projection |
| North | 2024 | 13.799 | projection |
| North | 2025 | 13.805 | projection |
| North | 2026 | 13.812 | projection |
| South | 2022 | 22.154 | projection |
| South | 2023 | 22.284 | projection |

_Showing the first 12 rows._

## Saved artifacts
- `raw_csv`: `outputs\two_year_demo\synthetic_climate_data.csv`
- `cleaned_csv`: `outputs\two_year_demo\cleaned_climate_data.csv`
- `annual_summary_csv`: `outputs\two_year_demo\annual_summary.csv`
- `monthly_summary_csv`: `outputs\two_year_demo\monthly_summary.csv`
- `trend_summary_csv`: `outputs\two_year_demo\temperature_trends.csv`
- `anomalies_csv`: `outputs\two_year_demo\temperature_anomalies.csv`
- `projection_csv`: `outputs\two_year_demo\temperature_projection.csv`
- `annual_temperature_png`: `outputs\two_year_demo\annual_temperature.png`
- `monthly_rainfall_png`: `outputs\two_year_demo\monthly_rainfall.png`
- `anomalies_png`: `outputs\two_year_demo\temperature_anomalies.png`
- `projection_png`: `outputs\two_year_demo\temperature_projection.png`
- `report_json`: `outputs\two_year_demo\analysis_report.json`
- `report_markdown`: `outputs\two_year_demo\analysis_report.md`
