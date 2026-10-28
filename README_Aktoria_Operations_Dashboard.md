# Egocentric Data Collection Operations Dashboard

An interactive Streamlit dashboard that demonstrates how a data-collection operation could monitor collection targets, upload timeliness, recording quality, consent verification, equipment readiness, and records needing follow-up.

> **Data disclaimer:** This is an independent portfolio project built with synthetic, fictional data. It is not Aktoria Robotics data, is not affiliated with Aktoria Robotics, and does not represent any real company's policies or operational performance.

## Features

- Filters by collection date, site, collection partner, and camera
- KPI cards for collection target achievement, on-time upload rate, first-pass quality, equipment readiness, consent verification, and sessions needing action
- Scheduled-versus-recorded-hours trend
- Upload-status and equipment-status visualizations
- Site-level comparisons
- Exception queue with severity and suggested follow-up actions
- CSV export for filtered exception records
- Reproducible synthetic data generator and dataset validation script

## Technology stack

- Python
- Pandas and NumPy
- Streamlit
- Plotly

## Repository structure

```text
egocentric-data-collection-ops-dashboard/
├── app.py
├── generate_data.py
├── validate_data.py
├── requirements.txt
├── README.md
├── .gitignore
├── START_DASHBOARD.bat        # Optional Windows launcher
└── data/
    └── collection_operations.csv
```

**Important:** `data/collection_operations.csv` must be committed to the repository. The app reads it from this exact path. If the CSV is missing or uploaded to the repository root instead of the `data/` folder, the app will not be able to load the dataset.

## Run locally on Windows

1. Install Python 3.10 or newer from [python.org](https://www.python.org/downloads/).
2. Download or clone this repository and open a terminal in the project root (the folder containing `app.py`).
3. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

4. Install dependencies:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

5. Validate the dataset:

   ```powershell
   .\.venv\Scripts\python.exe validate_data.py
   ```

6. Start the dashboard:

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```

7. Open the local URL printed in the terminal, usually `http://localhost:8501`.

On Windows, `START_DASHBOARD.bat` can also be used as a convenience launcher. Keep the terminal window open while the app is running; press `Ctrl+C` in that window to stop it.

## Regenerate the synthetic dataset

The CSV is included in the repository, so regeneration is optional. From the project root, run:

```powershell
.\.venv\Scripts\python.exe generate_data.py
```

This regenerates 2,880 fictional collection-session records across four simulated sites over a 90-day period. The data generator uses a fixed random seed for reproducibility.

## KPI definitions

- **Collection target achievement:** total recorded hours divided by total scheduled hours. It may exceed 100% if recorded hours exceed the target.
- **On-time upload rate:** sessions marked `On time` divided by all filtered sessions. Late or missing uploads are not counted as on time.
- **First-pass quality rate:** sessions marked `Pass` divided by sessions with an assessed quality status (`Pass`, `Needs review`, or `Fail`). Sessions with missing uploads are marked `Not reviewed` and excluded from this denominator.
- **Equipment readiness:** sessions with equipment status `Ready` divided by all filtered sessions. This is a session-level indicator, not a formal equipment uptime metric.
- **Consent verification:** sessions with verified consent divided by all filtered sessions. Unverified consent is flagged for follow-up and should not be treated as compliant.
- **Sessions needing action:** unique sessions with one or more exception flags. One session can trigger multiple flags.

Thresholds and recommended actions in the dashboard are illustrative examples, not actual company policies. Any real operational deployment would require validated metric definitions, accurate event timestamps, privacy and consent safeguards, and review with the people responsible for the process. Synthetic data cannot establish real-world root causes or business impact.

## Deploy on Streamlit Community Cloud

1. Push the project files, including `data/collection_operations.csv`, to a GitHub repository.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
3. Create a new app and select this repository, the intended branch, and `app.py` as the main file.
4. Deploy the app and use the generated public URL to share the demo.

The deployed demo will still use synthetic data. Do not upload personal, confidential, or company-owned data to this public repository.
