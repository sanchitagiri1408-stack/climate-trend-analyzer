# Data directory

This directory intentionally does not contain a government or sensor dataset.

## Current data policy

The project creates its input in memory with `src/data_generator.py`. The generator produces deterministic, synthetic daily observations for the configured date range and regions. The default configuration is:

- dates: `2015-01-01` through `2024-12-31`, inclusive;
- regions: `North`, `Central`, and `South`; and
- random seed: `42`.

The default CLI command is:

```bash
python main.py --all
```

It writes generated artifacts to `outputs/`, not to this directory. The main generated tables are:

- `outputs/synthetic_climate_data.csv` for the simulated values before cleaning;
- `outputs/cleaned_climate_data.csv` for the cleaned values and imputation markers;
- `outputs/annual_summary.csv` and `outputs/monthly_summary.csv` for aggregates;
- `outputs/temperature_anomalies.csv` for rolling anomaly statistics; and
- `outputs/temperature_projection.csv` for historical values and five projection years.

Generated output is ignored by `.gitignore` so large, reproducible artifacts do not become accidental source data or repository noise.

## Synthetic schema

The generator creates these key columns:

| Column | Description |
| --- | --- |
| `date` | Daily observation date |
| `region` | Configured region name |
| `temperature_c` | Simulated temperature in degrees Celsius |
| `rainfall_mm` | Simulated rainfall in millimeters |
| `humidity_pct` | Simulated relative humidity percentage |
| `season` | Simple Northern Hemisphere season label |
| `year`, `month`, `month_name`, `quarter`, `day_of_year` | Calendar features |
| `is_injected_anomaly` | Ground-truth flag for simulator-injected unusual events |
| `is_missing_injected` | Row-level flag for injected missing measurements |

The cleaner also adds `was_imputed` and measurement-specific imputation flags. It validates the date, region, and three measurement columns before processing.

## Optional public-data starting points

If you later want to add a real-data adapter, begin with a small, documented extract from one of these public sources. Check the current terms, units, and download format before using any source in a report:

| Source | Useful starting point | Typical use |
| --- | --- | --- |
| NOAA NCEI GHCN-Daily | [Global Historical Climatology Network-Daily](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily) | Station-level daily temperature and precipitation |
| NASA GISS | [GISTEMP data](https://data.giss.nasa.gov/gistemp/) | Global or regional temperature anomalies |
| Berkeley Earth | [Data downloads](https://berkeleyearth.org/data/) | Gridded and station-based temperature series |
| Our World in Data | [Climate change data](https://ourworldindata.org/climate-change) | Accessible country-level indicators and metadata |

For a beginner, use one small CSV and write an adapter that maps its columns to `date`, `region`, `temperature_c`, `rainfall_mm`, and `humidity_pct` (allowing unavailable fields to remain optional until the analysis contract is updated). Preserve the raw file outside Git when licensing or size is unclear, and commit the citation/provenance note instead of silently mixing it with the simulator.

## If real data is added later

Use a separate, documented ingestion step. Record the source URL or citation, license, download date, units, geographic meaning of each region, timezone, missing-value codes, and any transformations. Do not replace the synthetic workflow without updating the README, report language, tests, and limitations.

Real data files can be large or restricted. Prefer a documented download instruction or a small licensed sample rather than committing an unknown or copyrighted file. Keep credentials and private exports out of this directory.

## Important limitation

The synthetic values are suitable for demos, tests, and learning. They are not government observations, a measured climate record, or evidence for real-world regional warming.

