# Climate Trend Analyzer: Beginner Project Guide

This guide explains the project from the first setup command through a polished GitHub presentation. It assumes you are comfortable opening a terminal and editing text files, but it does not assume prior pandas, scikit-learn, or Streamlit experience.

Use the README as the short project summary. Use this guide when you want to understand the project phase by phase, troubleshoot a setup issue, or prepare to explain the work to a recruiter or interviewer.

## 1. What you will learn

By the end, you should be able to:

- create an isolated Python environment;
- run a reproducible command-line data pipeline;
- describe how simulated data differs from an observed dataset;
- follow a DataFrame through validation, cleaning, aggregation, modeling, and export;
- open a dashboard backed by the same analysis functions;
- inspect generated CSV, JSON, Markdown, and PNG outputs;
- run the tests and explain what they protect;
- document limitations honestly; and
- turn the project into evidence for GitHub, a resume, LinkedIn, and interviews.

## Technology choices: three beginner-to-advanced options

| Option | Stack and analysis | Difficulty / GPU | Outcome |
| --- | --- | --- | --- |
| **Option A — easiest** | Python, pandas, NumPy, Matplotlib, Seaborn, Jupyter, CSV; descriptive statistics and a simple annual linear trend | Beginner; no GPU | One reproducible notebook with cleaned tables and a few charts |
| **Option B — selected for this repository** | Python modules, pandas, NumPy, Matplotlib, Seaborn, scikit-learn, Streamlit, pytest; linear trend, rolling z-score anomalies, five-year baseline projection | Beginner-to-intermediate; no GPU | A reusable CLI pipeline, test suite, saved artifacts, dashboard, and recruiter-friendly proof |
| **Option C — advanced** | Option B plus statsmodels ARIMA/ETS, Prophet or comparable forecasting, xarray/geopandas, satellite or gridded data, uncertainty intervals, Docker and CI | Intermediate-to-advanced; GPU usually unnecessary for classical time series, but useful for deep learning | A research-style or production-style system with stronger validation and spatial analysis |

Option B is the best student trade-off: it is still explainable line by line, but it demonstrates software structure, reproducibility, testing, visualization, and a usable interface. Start with B before adding ARIMA, Prophet, or neural networks.

## 2. Project phases at a glance

| Phase | Main question | Files or command |
| --- | --- | --- |
| 1. Orient | What is this project and what is the data policy? | `README.md`, `data/README.md` |
| 2. Set up | Can Python and the dependencies run in isolation? | `.venv`, `requirements.txt` |
| 3. Generate | How are the daily observations created? | `src/data_generator.py` |
| 4. Clean | How are missing and invalid values handled? | `src/data_cleaning.py` |
| 5. Analyze | How are summaries, trends, anomalies, and projections calculated? | `src/analysis.py` |
| 6. Export | Where do results go and how can another person inspect them? | `src/pipeline.py`, `outputs/` |
| 7. Explore | How can a user change dates and seed without editing code? | `app/streamlit_app.py` |
| 8. Prove | What evidence shows that the project works? | tests, terminal output, screenshots |
| 9. Present | How do you discuss the project without overstating it? | GitHub, resume, interview notes |

The sections below follow that order.

## 3. Phase 1: orient yourself in the repository

Start in the project root, the directory that contains `main.py`, `requirements.txt`, `src/`, `app/`, and `tests/`.

The most important files are:

- `main.py`: parses CLI arguments and prints the run summary.
- `src/config.py`: validates dates, regions, seed, and output directory.
- `src/data_generator.py`: creates the deterministic synthetic observations.
- `src/data_cleaning.py`: validates columns, imputes measurements, enforces bounds, and creates a cleaning report.
- `src/analysis.py`: computes summaries, linear trends, rolling anomalies, and projections.
- `src/visualization.py`: saves four charts as PNG files.
- `src/pipeline.py`: calls the stages in order and writes all artifacts.
- `app/streamlit_app.py`: provides interactive controls and charts.
- `tests/test_pipeline.py`: checks the core workflow and artifact contract.
- `data/README.md`: explains why no raw government dataset is checked into `data/`.

Read [`README.md`](../README.md) once before running anything. The key boundary is simple: this repository demonstrates data engineering and analysis techniques using simulated data. It does not claim to analyze observed climate change.

## 4. Phase 2: set up Python safely

### Windows PowerShell

From the project root:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -3 -m pip install -r requirements.txt
```

Check that the environment is active:

```powershell
python --version
python -m pip --version
```

The prompt usually shows `(.venv)` when the environment is active. The exact Python version is not pinned by this repository, so use a supported current Python 3 installation and record the version in your own project notes if you need a fully reproducible environment.

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Verify:

```bash
python --version
python -m pip --version
```

### What the requirements install

`requirements.txt` lists:

- NumPy for numerical simulation;
- pandas for tabular data;
- Matplotlib and Seaborn for charts;
- scikit-learn for `LinearRegression`;
- Streamlit for the dashboard; and
- pytest for tests.

Keep the environment active while following the rest of this guide. If you close the terminal, activate it again before running the project.

## 5. Phase 3: run the first complete simulation

The fastest proof that the setup works is the CLI:

```bash
python main.py --all
```

On Windows, this is also valid:

```powershell
py main.py --all
```

The default run uses:

- dates `2015-01-01` through `2024-12-31`, inclusive;
- regions `North`, `Central`, and `South`;
- random seed `42`; and
- output directory `outputs`.

The terminal prints a summary similar to:

```text
Analyzed 10,959 cleaned daily observations.
Regions: Central, North, South
Detected anomalies: 67
Saved artifacts:
  raw_csv: outputs/synthetic_climate_data.csv
  cleaned_csv: outputs/cleaned_climate_data.csv
  annual_summary_csv: outputs/annual_summary.csv
  monthly_summary_csv: outputs/monthly_summary.csv
  trend_summary_csv: outputs/temperature_trends.csv
  anomalies_csv: outputs/temperature_anomalies.csv
  projection_csv: outputs/temperature_projection.csv
  annual_temperature_png: outputs/annual_temperature.png
  monthly_rainfall_png: outputs/monthly_rainfall.png
  anomalies_png: outputs/temperature_anomalies.png
  projection_png: outputs/temperature_projection.png
  report_json: outputs/analysis_report.json
  report_markdown: outputs/analysis_report.md
```

The absolute path in your terminal may differ. The names and relative paths are the contract defined by `src/pipeline.py`.

### Why the run is reproducible

`AnalyzerConfig` passes the seed to NumPy's default random number generator. With the same date range, regions, seed, and compatible dependency versions, the generator produces the same simulated values and the analysis produces the same artifacts. Try running the command twice and compare a report or checksum if your operating system has a checksum tool.

PowerShell:

```powershell
Get-FileHash outputs/analysis_report.json
```

macOS/Linux:

```bash
sha256sum outputs/analysis_report.json
```

Do not interpret a changed checksum after changing the seed as a bug. A different seed is expected to create a different simulation.

## 6. Phase 4: understand the virtual simulation

The project calls its generated dataset synthetic. A useful mental model is a virtual weather station simulator, not a hidden source of real observations.

### 6.1 Dates and regions

`generate_synthetic_data()` creates a daily date range with pandas. It loops through each configured region and produces one row per date. The default range has 3,653 dates. Three regions therefore produce 10,959 rows.

The configured profile parameters intentionally create visible differences:

- North is cooler and has a larger temperature seasonal amplitude.
- Central is the baseline profile.
- South is warmer and has a smaller seasonal amplitude.

Custom region names are accepted by the lower-level generator with a neutral fallback profile, but the CLI validates `--region` against the configured default names. For the documented CLI workflow, use North, Central, or South.

### 6.2 Seasonal signals

Temperature uses a sine wave over the day of year. Rainfall uses a separate non-negative seasonal wave. Humidity responds to the rainfall wave and temperature, then receives random noise and a physical clip.

The code also adds a small positive time drift to temperature. It is an intentionally visible signal for the trend lesson; it is not calibrated to a scientific record.

### 6.3 Injected anomalies

For each region, about 0.8% of rows are selected. Those rows receive:

- a positive or negative temperature shift;
- a rainfall multiplier between 3 and 6; and
- a positive or negative humidity change, clipped to a safe range.

The `is_injected_anomaly` column is ground truth created by the simulator. It lets a learner compare known injected events with the independent rolling detector. It does not mean the detector is a validated classifier.

### 6.4 Injected missing values

For each of `temperature_c`, `rainfall_mm`, and `humidity_pct`, about 1.2% of cells are replaced with `NaN`. `is_missing_injected` marks rows where at least one measurement was affected.

This makes the cleaning stage visible. The simulator does not hide missingness inside an opaque fixture.

## 7. Phase 5: follow the cleaning stage

`clean_data_with_report()` returns both a cleaned DataFrame and a `CleaningReport`.

The cleaning sequence is:

1. Confirm the required columns exist: `date`, `region`, `temperature_c`, `rainfall_mm`, and `humidity_pct`.
2. Parse dates with invalid values becoming missing.
3. Convert region labels to trimmed strings.
4. Drop rows with invalid dates or empty region labels.
5. Sort by region and date.
6. Mark rows with at least one missing measurement using `was_imputed`.
7. Convert measurements to numeric values.
8. Interpolate within each region in date order.
9. Fill any values that interpolation cannot resolve with a region median, then a global median or safe fallback.
10. Enforce rainfall `>= 0` and humidity between `0` and `100`.
11. Ensure anomaly and missingness flags exist and are booleans.
12. Recreate year, month, month name, quarter, and day-of-year fields.

The default run drops zero rows because the generator creates valid identifiers and dates. That is a result of this simulation, not a guarantee for future input data.

Useful fields to inspect in `cleaned_climate_data.csv` include:

- `was_imputed`: row-level marker;
- `temperature_c_was_imputed`, `rainfall_mm_was_imputed`, and `humidity_pct_was_imputed`: measurement-level markers;
- `is_injected_anomaly`: simulator ground truth; and
- `is_missing_injected`: simulator missingness marker.

## 8. Phase 6: follow the analysis stage

### Annual and monthly summaries

Annual summaries group by region and year. They contain mean, minimum, and maximum temperature, total rainfall, mean humidity, record count, and detected anomaly count when anomaly flags are present.

Monthly summaries group by region, year, month, and month name. They contain mean temperature, total rainfall, mean humidity, and record count.

The default run creates 30 annual rows, three regions times ten years, and 360 monthly rows, three regions times ten years times twelve months.

### Linear trends

The trend model is ordinary least squares with one predictor: year. The output includes:

- region;
- start and end year;
- number of years used;
- slope in °C per year;
- intercept;
- `r_squared`;
- first and last annual mean temperatures; and
- a threshold-based direction label.

The direction label is `warming` when the slope is above `0.01`, `cooling` when it is below `-0.01`, and `stable` otherwise. This is a reporting rule, not a statistical significance test.

### Rolling anomaly detection

The default pipeline calls `detect_rolling_zscore_anomalies()` with a 30-observation window and threshold `3.0`. It calculates statistics independently for each region so the baseline for one region is not mixed with another region's climate profile.

The output includes rolling mean, rolling standard deviation, z-score, and a boolean anomaly flag. Early rows use the observations available so far. If the standard deviation is zero, the z-score is treated as zero.

### Five-year projection

The projection uses the same annual linear model. It keeps historical annual values and appends five rows per region with `forecast_type` equal to `projection`. The projected rows have a value in `projected_temperature_c` and no observed value in `actual_temperature_c`.

Treat this as an extrapolation exercise. It does not include uncertainty, changing emissions, feedbacks, physical constraints, or a comparison with observed future data.

## 9. Phase 7: inspect the output artifacts

After the CLI run, list the folder:

macOS/Linux:

```bash
ls -lh outputs
```

PowerShell:

```powershell
Get-ChildItem outputs
```

The artifact roles are:

| File | What to inspect |
| --- | --- |
| `synthetic_climate_data.csv` | Generated values and simulation flags before cleaning |
| `cleaned_climate_data.csv` | Imputed values, bounds, and audit markers |
| `annual_summary.csv` | Region/year aggregates |
| `monthly_summary.csv` | Region/year/month aggregates |
| `temperature_trends.csv` | Slope and `r_squared` per region |
| `temperature_anomalies.csv` | Daily rolling statistics and flags |
| `temperature_projection.csv` | Historical and projection rows |
| `*.png` | Four visual summaries |
| `analysis_report.json` | Machine-readable run metadata |
| `analysis_report.md` | Human-readable report generated by the pipeline |

You can inspect a few CSV rows without adding another dependency:

```bash
python -c "import pandas as pd; print(pd.read_csv('outputs/temperature_trends.csv').to_string(index=False))"
```

You can inspect report keys:

```bash
python -c "import json; from pathlib import Path; r=json.loads(Path('outputs/analysis_report.json').read_text()); print(r.keys()); print(r['anomaly_counts'])"
```

If you open the Markdown report, look for the scope, data-quality counts, trend table, anomaly counts, projection preview, and saved-artifact list.

## 10. Phase 8: run the tests

Run:

```bash
python -m pytest -q
```

The current suite has four tests. They check behavior instead of only checking that imports succeed:

1. The generator produces daily rows for the three regions, seasons, injected anomalies, and missingness.
2. Cleaning fills measurements, preserves row count for generated input, and enforces rainfall/humidity bounds.
3. Anomaly detection creates a boolean flag and projection creates the requested future years.
4. The pipeline writes non-empty CSV, PNG, JSON, and Markdown artifacts and honors a selected region.

If tests pass but the dashboard fails, the problem is probably in the local Streamlit launch or environment rather than in the tested CLI pipeline. If the CLI fails, read the first exception and compare your command with the documented defaults.

## 11. Phase 9: open the dashboard

From the project root with the environment active:

```bash
streamlit run app/streamlit_app.py
```

The app creates its data once per combination of start date, end date, and seed using Streamlit's cache. It then presents:

1. four metrics: cleaned observations, average temperature, rainfall total, and detected anomalies;
2. an annual temperature line chart;
3. an average monthly rainfall line chart;
4. a trend table;
5. an annual projection chart;
6. a table of the latest detected anomalies; and
7. a CSV download for cleaned data.

Try these small experiments:

- change the region to North, then South, and compare the average temperature;
- shorten the date range to 2020-01-01 through 2021-12-31;
- change the seed from 42 to 7 and observe that the random details change;
- use the same seed again and observe that the results return to the same simulation; and
- set the start date after the end date to see the validation message.

The sidebar warning is intentional: the data is simulated for learning and demonstration.

## 12. Troubleshooting

### `python` or `py` is not recognized

Install Python 3 from the official Python distribution for your operating system. On Windows, enable the Python launcher if the installer offers it. Then reopen the terminal and run:

```powershell
py --version
```

On macOS/Linux, check:

```bash
python3 --version
```

Use the command that exists on your machine consistently when creating the virtual environment.

### PowerShell blocks `.venv\Scripts\Activate.ps1`

You can allow the script for the current PowerShell process only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

This setting is temporary for that terminal process. If your organization manages execution policy, use Command Prompt and activate with `.venv\Scripts\activate.bat`, or ask your administrator for the approved approach.

### `ModuleNotFoundError` after installation

The environment may not be active, or pip may have installed into another Python. Check:

```bash
python -m pip --version
python -c "import pandas, numpy, sklearn, streamlit; print('imports ok')"
```

Then reinstall through the active interpreter:

```bash
python -m pip install -r requirements.txt
```

### `FileNotFoundError` for `main.py`

Change to the project root before running commands. Confirm the file exists:

macOS/Linux:

```bash
pwd
ls main.py
```

PowerShell:

```powershell
Get-Location
Get-ChildItem main.py
```

### Invalid date or reversed date range

Dates must use `YYYY-MM-DD`, for example:

```bash
python main.py --all --start-date 2020-01-01 --end-date 2021-12-31
```

The start date must be on or before the end date. The dashboard displays an error and stops when the order is invalid.

### Unknown region error

The CLI accepts the configured region names `North`, `Central`, and `South`:

```bash
python main.py --all --region North
```

The spelling and capitalization must match. Omit `--region` to analyze all three.

### `streamlit` is not recognized

Activate the virtual environment and install the requirements. You can also launch Streamlit through the active Python environment:

```bash
python -m streamlit run app/streamlit_app.py
```

If port 8501 is already in use, Streamlit will usually choose or report another port. Read the terminal URL rather than assuming the port.

### The browser page is blank or the app stops

Look at the terminal where Streamlit is running. The project expects to be launched from the root with:

```bash
streamlit run app/streamlit_app.py
```

Also confirm that `streamlit`, pandas, NumPy, and scikit-learn were installed in the active environment. Stop the server with `Ctrl+C`, then start it again.

### Generated files are missing

The pipeline writes files only after the command completes. Run:

```bash
python main.py --all
```

Then inspect `outputs/`. If you used `--output-dir`, inspect that custom directory instead. A selected-region run still writes the same filenames, but the tables contain only the selected region.

### The output folder is large

The daily anomaly CSV and cleaned CSV contain thousands of rows. This is expected. Generated `outputs/` is ignored by `.gitignore`; do not commit it just to prove the code ran. Commit a short terminal transcript or screenshot instead.

## 13. Phase 10: GitHub proof plan

The goal of a portfolio repository is to make the work easy to verify in a few minutes.

### Exact GitHub publishing commands

After replacing the author placeholders and checking the generated screenshots, run these commands from the project root. Replace the URL with your own repository URL; never commit an API key or `.env` file.

```bash
git init
git branch -M main
git add README.md docs data src app tests main.py requirements.txt .gitignore
git commit -m "feat: add reproducible climate trend analyzer"
git remote add origin https://github.com/<your-username>/climate-trend-analyzer.git
git push -u origin main
```

Recommended repository metadata:

- Repository name: `climate-trend-analyzer`
- Description: `Reproducible Python climate trend analysis with synthetic data, anomaly detection, projections, charts, and a Streamlit dashboard.`
- Topics: `python`, `data-analysis`, `climate-data`, `time-series`, `pandas`, `scikit-learn`, `streamlit`, `data-visualization`, `portfolio-project`
- Pin the repository after it contains the README, chart assets, passing test command, and a clean demo screenshot.

### Before publishing

1. Replace the author placeholders in `README.md`.
2. Run `python -m pytest -q` and save the passing result in your notes.
3. Run `python main.py --all` from a clean environment.
4. Open `outputs/analysis_report.md` and confirm it names the synthetic data boundary.
5. Launch the dashboard and capture one overview screenshot.
6. Capture one terminal screenshot showing the exact run command and artifact names.
7. Check that generated `outputs/` files are not staged.
8. Check that no API keys, `.env` files, or personal machine paths are committed.
9. Link the project from your portfolio or profile.

### Eight-day proof-building schedule

| Day | Commit and work | Evidence to save |
| --- | --- | --- |
| Day 1 | `chore: initialize climate analyzer project` — create the environment, folder structure, requirements, and README outline | Terminal showing Python version and the tree |
| Day 2 | `feat: add reproducible climate simulation` — add dates, regions, seasonality, missingness, and injected events | Raw CSV preview and generator code screenshot |
| Day 3 | `feat: add data cleaning and audit report` — impute measurements, enforce bounds, and record before/after counts | Missing-values table and cleaned CSV preview |
| Day 4 | `feat: add climate summaries and trend analysis` — annual/monthly summaries and OLS slopes | Annual temperature and rainfall charts |
| Day 5 | `feat: add rolling anomaly detection` — rolling mean, standard deviation, z-score, and event table | Anomaly chart and top anomaly rows |
| Day 6 | `feat: add baseline temperature projection` — historical versus five-year projection output | Projection chart and explanation of limitations |
| Day 7 | `feat: add Streamlit climate dashboard` — controls, metrics, charts, and download button | Dashboard screenshot or short GIF |
| Day 8 | `docs: publish reproducible climate analysis portfolio` — tests, README, screenshots, limitations, and GitHub metadata | GitHub repo screenshot, README preview, passing test output |

Keep a small note for each day: what changed, what command proved it, one insight, and one limitation. That note becomes useful material for a resume or LinkedIn post.

### Suggested commit sequence

If you initialize a Git repository, keep the history readable:

```text
docs: explain synthetic climate analysis workflow
feat: add reproducible climate simulation pipeline
test: cover generation cleaning and artifact outputs
docs: add dashboard screenshots and presentation notes
```

Use the commit names that match your actual changes. Do not claim a feature in a commit message if it is not present.

### Proof asset checklist

Capture and store these with stable names under `docs/assets/` or keep them as untracked evidence if they show a local terminal path:

- `dataset-preview.png` — first rows and schema;
- `data-quality-before-after.png` — missing counts before and after cleaning;
- `annual-temperature.png` — already generated by the default run;
- `monthly-rainfall.png` — seasonal pattern;
- `temperature-anomalies.png` — rolling baseline and flagged points;
- `yearly-comparison.png` — annual summary table or comparison chart;
- `temperature-projection.png` — five-year baseline projection;
- `dashboard-overview.png` — Streamlit metrics and charts;
- `cli-output.png` — terminal command plus artifact list;
- `github-repository.png` and `readme-preview.png` — final portfolio proof.

Reference curated images in Markdown with paths such as `![Annual temperature](docs/assets/annual-temperature.png)`. Label every chart as simulated data and avoid screenshots containing personal file paths, tokens, or private account information.

### README proof checklist

The first screen of the README should answer:

- What does this project do?
- Is the data real or simulated?
- How do I run it?
- What files and dashboard do I get?
- What skills does it demonstrate?
- What are the limitations?

The current README is structured around those questions. Keep screenshots close to the dashboard section and keep the honesty note visible near the top.

## 14. Resume guidance

Use a project bullet that is accurate about the data source. For example:

> Built a reproducible Python climate-analysis workflow that generates seeded synthetic daily observations, imputes missing measurements with audit flags, summarizes regional trends, detects rolling z-score anomalies, and exports CSV/PNG/JSON/Markdown artifacts plus a Streamlit dashboard.

Possible skills to list when you can explain them:

```text
Python, pandas, NumPy, scikit-learn, Matplotlib, Seaborn, Streamlit, pytest,
data cleaning, exploratory data analysis, reproducible simulation, Git/GitHub
```

Avoid saying:

- “Analyzed government climate records”;
- “Proved regional warming”; or
- “Built a production climate forecast.”

Those statements would not match the current repository.

## 15. LinkedIn guidance

A short project post can follow this structure:

> I built a Climate Trend Analyzer in Python to practice an end-to-end data workflow. The project generates reproducible synthetic daily observations for three regions, records injected missingness, cleans the data, calculates annual trends, flags rolling z-score anomalies, writes analysis artifacts, and exposes the workflow in Streamlit. The data is simulated rather than government-observed, so the focus is on transparent engineering and analysis choices. Next I would add a licensed real-data adapter and uncertainty-aware modeling.

Add one dashboard screenshot and one link to the repository. Label the screenshot as simulated data.

## 16. Interview preparation

### “What problem does it solve?”

It is a teaching and portfolio project showing how a repeatable data pipeline moves from generated daily rows to cleaned tables, summary metrics, anomaly flags, projections, charts, and a dashboard. It is not intended to answer a real climate-policy question with observed data.

### “Why use synthetic data?”

Synthetic data makes the repository self-contained and reproducible. It also lets the project include known injected anomalies and missing values so the cleaning and detection stages can be demonstrated without redistributing a third-party dataset. The trade-off is that the conclusions are not about the real climate.

### “How did you make the data reproducible?”

The configuration accepts an integer seed and the generator passes it to NumPy's random number generator. The date range, regions, seed, and output directory are explicit inputs. The report records the configuration used for the run.

### “How did you handle missing values?”

The cleaner records which rows and individual measurements were missing, interpolates within each region in date order, falls back to a region or global median, and reports before/after missingness. It also clips rainfall and humidity to sensible bounds.

### “How does anomaly detection work?”

The detector calculates rolling mean and population standard deviation independently per region. It flags observations whose absolute z-score is at least the threshold, with a 30-observation and 3.0 threshold in the pipeline. The injected anomaly flag is available for comparison, but it is not used as the detector's input.

### “Why linear regression?”

It is easy to inspect and explain: annual mean temperature is modeled as a function of year, and the slope is reported in °C per year. It is a baseline chosen for clarity, not a claim that climate trends are linear or that the projection is scientifically valid.

### “What would you improve next?”

First, add a documented real-data adapter with provenance and units. Then compare stronger time-series baselines, add uncertainty intervals and validation, add more tests around edge cases, and make the dashboard export more of its filtered views.

### “What is the most important limitation?”

The data is simulated. Even a clean trend, anomaly count, or projection from this repository describes the simulator's assumptions, not measured regional climate behavior.

## 17. Limitations to state clearly

Use this list when writing a report, presenting the project, or answering questions:

- The dataset is synthetic and hand-designed.
- The region profiles are illustrative, not geographic measurements.
- The trend contains a deliberately small simulated drift.
- Injected anomalies and missing values are teaching fixtures.
- Linear regression has one predictor and no uncertainty interval.
- The five-year projection is an extrapolation from a synthetic series.
- A rolling z-score can miss context-dependent or multi-variable events.
- No causal inference, spatial modeling, station calibration, or physical climate model is present.
- Dependency or platform differences can alter floating-point formatting or generated image bytes even when the workflow is logically the same.

## 18. A safe extension exercise

If you want to practice without changing the current source contract, make a copy of the repository or create a separate branch. A good first exercise is to add a new analysis notebook or script outside the existing pipeline that reads `outputs/annual_summary.csv` and prints the warmest region by final-year mean temperature. Keep the synthetic-data disclaimer in the output.

Another exercise is to add a documented real-data adapter in a separate change. Before using real observations, record the source, license, units, station or region definitions, date coverage, missing-value codes, and download date. Do not silently replace the simulator with a downloaded file.

## 19. Final pre-share checklist

```text
[ ] README says the data is synthetic/simulated.
[ ] Setup commands work on the target operating system.
[ ] `python -m pytest -q` passes.
[ ] `python main.py --all` writes the documented filenames.
[ ] Streamlit starts from the project root.
[ ] Screenshots are labeled as simulated data.
[ ] `outputs/` is ignored and not staged.
[ ] No secrets or personal paths are committed.
[ ] Author and portfolio placeholders are replaced.
[ ] Resume and LinkedIn wording does not imply government observations.
[ ] Limitations are easy to find.
```

