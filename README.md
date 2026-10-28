# Egocentric Data Collection Operations Dashboard

An interactive portfolio project demonstrating how a robotics data-collection operation could monitor collection targets, upload timeliness, recording quality, consent verification, equipment readiness, and sessions requiring follow-up.

> **Important data disclaimer:** All data in this project is synthetic and fictional. It is not from Aktoria Robotics or any other real company and does not represent actual company performance, policies, customers, workers, or locations. This is an independent portfolio project with no company affiliation.

## Features

- Date, site, collection-partner, and camera filters
- KPIs for collection target achievement, on-time upload rate, first-pass quality rate, equipment readiness, consent verification, and sessions needing action
- Trend chart comparing scheduled and recorded hours
- Upload-status breakdown
- Site-level target and consent comparison
- Equipment status and downtime view
- Operational exceptions queue with severity and suggested follow-up
- CSV export of filtered exception records
- Explicit metric definitions, assumptions, and limitations in the app
- Deterministic generator for a repeatable dataset

## Files

```text
aktoria_data_collection_ops_dashboard/
├── app.py
├── generate_data.py
├── validate_data.py
├── requirements.txt
├── README.md
├── PROMPT_FOR_ANTIGRAVITY.md
├── RESUME_AND_INTERVIEW_NOTES.md
├── START_DASHBOARD.bat
├── .gitignore
└── data/
    └── collection_operations.csv
```

## Run on Windows (PowerShell)

1. Install Python 3.10 or newer from https://www.python.org/downloads/ if it is not already installed. During installation, enable the option to add Python to PATH if offered.
2. Extract the project ZIP.
3. Open Google Antigravity and open the extracted project folder.
4. Open its terminal panel and run these commands one at a time from the folder containing `app.py`:

```powershell
py --version
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Streamlit should display a local URL, usually `http://localhost:8501`. Open that URL if it does not open automatically. Keep the terminal open while using the dashboard.

Before launching, you can run a quick CSV validation check:

```powershell
.\.venv\Scripts\python.exe validate_data.py
```

This validates the included dataset and key timestamp/quality assumptions; it does not replace testing the dashboard UI.

If `py --version` fails, install Python from the official link above and reopen Antigravity. If installation or launch fails, copy the complete error message into Antigravity and ask it to diagnose the error without switching frameworks.

To stop the app, focus the terminal and press `Ctrl+C`.

## Regenerate the synthetic dataset

The CSV is already included, so this step is optional. From the project root:

```powershell
.\.venv\Scripts\python.exe generate_data.py
```

This regenerates 2,880 synthetic collection sessions across 4 fictional sites over 90 days with a fixed random seed. The dates are fixed to keep the demo reproducible.

## KPI definitions

- **Collection target achievement** = total recorded hours ÷ total scheduled hours. Can exceed 100% if recorded hours exceed the target.
- **On-time upload rate** = sessions marked `On time` ÷ all sessions in the filtered data. Late and missing uploads count as not on time.
- **First-pass quality rate** = sessions marked `Pass` ÷ sessions with an assessed quality status (`Pass`, `Needs review`, or `Fail`). Sessions with a missing upload are marked `Not reviewed` and excluded from this denominator.
- **Equipment readiness** = sessions with equipment status `Ready` ÷ all sessions. This is a session-level status indicator, not a production uptime measure.
- **Consent verification** = sessions with verified consent ÷ all sessions. Unverified consent must be investigated; these records are flagged and should not be treated as compliant.
- **Sessions needing action** = unique sessions with one or more exception flags. One session can have multiple flags.

All thresholds and recommended actions in the dashboard are illustrative and are not asserted to be real policies. Before real operational use, the definitions would need agreement with operators, review by relevant compliance/privacy stakeholders, and validation against authorized data.

## How to explain it in an interview

**Problem:** A data-collection operation needs a simple way to spot missed collection targets, late or missing uploads, quality problems, consent gaps, and equipment issues across sites.

**Solution:** I built an interactive Streamlit dashboard with filters, weighted aggregate KPIs, site comparisons, trend charts, an exception queue, and CSV export. The data is synthetic, so this project demonstrates the analysis workflow rather than reporting a real operation's performance.

**Why these metrics?** They cover delivery against target, timeliness, first-pass quality, equipment readiness, and a basic consent-verification control. The exception queue turns a summary view into a list of records that may need follow-up.

**Key limitation:** The dashboard cannot identify true root causes from synthetic session-level data. Real operations would require validated definitions, accurate timestamps, privacy/consent safeguards, and feedback from the people running the process.

## Suggested resume entry

Use only after running the app and checking that the features work:

**Egocentric Data Collection Operations Dashboard** | Python, Pandas, Streamlit, Plotly

- Built an interactive dashboard using 2,880 synthetic collection-session records to monitor collection targets, upload timeliness, recording quality, consent verification, and equipment readiness across simulated sites.
- Developed site-level comparisons and a prioritized exception queue to flag delayed or missing uploads, quality failures, unverified consent, and equipment issues.
- Implemented filters and CSV exports to support operational reporting and follow-up on records requiring attention.

Do not claim productivity improvements or findings about Aktoria Robotics. If you modify the dataset or features, update the resume bullets to match the final implementation and actual checks performed.
