# Climate Trend Analyzer: short demo script

Use this 3-5 minute script for a recruiter screen, portfolio review, or class presentation. Keep the synthetic-data disclaimer visible.

## Before the demo

From the project root, activate the virtual environment and install dependencies. Then run:

```bash
python main.py --all
```

Have the project root and `outputs/analysis_report.md` ready to show. For the dashboard, start a second terminal and run:

```bash
streamlit run app/streamlit_app.py
```

## Talk track

### 1. Frame the project

“This is a reproducible climate-analysis workflow built in Python. The observations are synthetic, not government data. I use the simulator so the project is self-contained and can include known missing values and injected anomalies for testing.”

### 2. Show the pipeline

Point to the source tree and explain:

```text
generate -> clean and audit -> summarize -> trend/anomaly/project
         -> save CSV/PNG/JSON/Markdown -> explore in Streamlit
```

Mention that the CLI and dashboard reuse the same `src/` functions.

### 3. Run result

Show the terminal summary:

```text
Analyzed 10,959 cleaned daily observations.
Regions: Central, North, South
Detected anomalies: 67
```

Explain that the default run covers 2015-2024 for three regions with seed 42. The exact values come from the simulator and should not be presented as observed climate findings.

### 4. Show the artifacts

Open `outputs/analysis_report.md` and point out:

- cleaning counts and imputed rows;
- annual linear trend slopes and `r_squared` values;
- detected versus injected anomaly counts;
- five-year projection rows; and
- the saved-artifact list.

Then show one CSV such as `temperature_trends.csv` and one chart such as `annual_temperature.png`.

### 5. Show the dashboard

In Streamlit:

1. switch between North and South;
2. change the date range to 2020-2021;
3. change the seed and point out that the simulation changes; and
4. show the cleaned-data download button.

Call out the sidebar warning that the data is simulated.

### 6. Close with limitations and next step

“The current model is intentionally simple: annual linear regression, a rolling z-score anomaly rule, and synthetic inputs. My next step would be a documented real-data adapter with provenance and units, followed by uncertainty-aware validation. The current project proves the software workflow, not a scientific conclusion.”

## Questions to invite

- Why did you choose synthetic data?
- How did you make the run reproducible?
- How are missing values recorded and filled?
- What does the anomaly threshold mean?
- Why is the projection not a forecast?
- What would you change before using government observations?

For prepared answers, see the interview section in [`PROJECT_GUIDE.md`](PROJECT_GUIDE.md).

