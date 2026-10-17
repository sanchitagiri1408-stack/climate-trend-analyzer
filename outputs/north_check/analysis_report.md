# Climate Trend Analyzer Report

This report uses deterministic synthetic, public-data-style daily observations. It demonstrates a reproducible workflow and should not be interpreted as a measured climate record.

## Scope
- Dates: **2015-01-01** through **2024-12-31**
- Regions: **North**
- Random seed: **42**

## Data quality
- Rows before cleaning: **3653**
- Rows after cleaning: **3653**
- Rows with at least one imputed measurement: **132**
- Missing measurements after cleaning: **0**

## Linear temperature trends
The slope is an ordinary least-squares estimate in °C per year using annual mean temperature.
| region | start_year | end_year | slope_c_per_year | r_squared | trend_direction |
| --- | --- | --- | --- | --- | --- |
| North | 2015 | 2024 | 0.060 | 0.642 | warming |

## Rolling anomaly detection
- Detected temperature anomalies: **20**
- Injected anomaly rows available for comparison: **29**

## Annual projection
The projection extends the same linear annual model five years beyond the last observed year.
| region | year | projected_temperature_c | forecast_type |
| --- | --- | --- | --- |
| North | 2025 | 14.497 | projection |
| North | 2026 | 14.558 | projection |
| North | 2027 | 14.618 | projection |
| North | 2028 | 14.679 | projection |
| North | 2029 | 14.739 | projection |

## Saved artifacts
- `raw_csv`: `outputs/north_check/synthetic_climate_data.csv`
- `cleaned_csv`: `outputs/north_check/cleaned_climate_data.csv`
- `annual_summary_csv`: `outputs/north_check/annual_summary.csv`
- `monthly_summary_csv`: `outputs/north_check/monthly_summary.csv`
- `trend_summary_csv`: `outputs/north_check/temperature_trends.csv`
- `anomalies_csv`: `outputs/north_check/temperature_anomalies.csv`
- `projection_csv`: `outputs/north_check/temperature_projection.csv`
- `annual_temperature_png`: `outputs/north_check/annual_temperature.png`
- `monthly_rainfall_png`: `outputs/north_check/monthly_rainfall.png`
- `anomalies_png`: `outputs/north_check/temperature_anomalies.png`
- `projection_png`: `outputs/north_check/temperature_projection.png`
- `report_json`: `outputs/north_check/analysis_report.json`
- `report_markdown`: `outputs/north_check/analysis_report.md`
