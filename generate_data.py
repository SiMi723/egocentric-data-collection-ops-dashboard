"""Generate a reproducible, synthetic dataset for the portfolio dashboard.

All sites, workers, partners, devices, and outcomes are fictional. No real or
company data is included. Re-run with: python generate_data.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "collection_operations.csv"
SEED = 20261028


def main() -> None:
    rng = np.random.default_rng(SEED)
    sites = ["Site North", "Site Central", "Site South", "Site West"]
    site_partners = {
        "Site North": ["Partner N1", "Partner N2"],
        "Site Central": ["Partner C1", "Partner C2"],
        "Site South": ["Partner S1", "Partner S2"],
        "Site West": ["Partner W1", "Partner W2"],
    }
    workers = {site: [f"W-{site.split()[-1][0]}{i:02d}" for i in range(1, 9)] for site in sites}
    cameras = {site: [f"CAM-{site.split()[-1][0]}{i:02d}" for i in range(1, 13)] for site in sites}

    # Fixed historical window for a stable, repeatable demo.
    end_date = pd.Timestamp("2026-10-27")
    dates = pd.date_range(end=end_date, periods=90, freq="D")
    rows = []
    collection_no = 1

    for day_idx, date in enumerate(dates):
        for site in sites:
            # Eight summarized collection sessions per site per day.
            for session_idx in range(8):
                partner = str(rng.choice(site_partners[site]))
                worker = str(rng.choice(workers[site]))
                camera = str(rng.choice(cameras[site]))
                scheduled_hours = float(rng.choice([3.0, 4.0, 5.0], p=[0.15, 0.65, 0.20]))

                # Inject a repeatable illustrative bottleneck at Site Central.
                issue_window = site == "Site Central" and 38 <= day_idx <= 53
                site_recording_penalty = {"Site North": 0.02, "Site Central": 0.08, "Site South": 0.04, "Site West": 0.025}[site]
                recording_fraction = float(np.clip(rng.normal(0.96 - site_recording_penalty - (0.14 if issue_window else 0), 0.13), 0.35, 1.12))
                recorded_hours = round(scheduled_hours * recording_fraction, 2)

                # A scheduled reporting deadline of 20:00 local time for each session date.
                upload_deadline = date + pd.Timedelta(hours=20)
                upload_status = str(rng.choice(["On time", "Late", "Missing"], p=[0.83, 0.12, 0.05]))
                if issue_window:
                    upload_status = str(rng.choice(["On time", "Late", "Missing"], p=[0.62, 0.25, 0.13]))
                if upload_status == "On time":
                    upload_timestamp = upload_deadline - pd.Timedelta(minutes=int(rng.integers(5, 360)))
                elif upload_status == "Late":
                    upload_timestamp = upload_deadline + pd.Timedelta(minutes=int(rng.integers(15, 720)))
                else:
                    upload_timestamp = pd.NaT

                # A missing upload cannot yet be assessed for recording quality.
                if upload_status == "Missing":
                    quality_status = "Not reviewed"
                else:
                    quality_probs = [0.82, 0.13, 0.05]  # Pass, Needs review, Fail
                    if issue_window:
                        quality_probs = [0.68, 0.22, 0.10]
                    quality_status = str(rng.choice(["Pass", "Needs review", "Fail"], p=quality_probs))

                consent_verified = bool(rng.random() < (0.965 if not issue_window else 0.93))
                equipment_status = str(rng.choice(["Ready", "Battery issue", "Repair required"], p=[0.89, 0.08, 0.03]))
                if issue_window:
                    equipment_status = str(rng.choice(["Ready", "Battery issue", "Repair required"], p=[0.78, 0.15, 0.07]))
                downtime_minutes = int(np.clip(rng.gamma(1.7, 11) + (15 if equipment_status == "Repair required" else 8 if equipment_status == "Battery issue" else 0), 0, scheduled_hours * 60 * 0.8))
                rework_required = False if quality_status == "Not reviewed" else bool(quality_status != "Pass" or (rng.random() < 0.025))
                if quality_status == "Fail":
                    rework_required = True

                rows.append({
                    "collection_id": f"COL-{collection_no:05d}",
                    "date": date.date().isoformat(),
                    "site_id": site,
                    "partner_id": partner,
                    "worker_id": worker,
                    "camera_id": camera,
                    "scheduled_hours": scheduled_hours,
                    "recorded_hours": recorded_hours,
                    "upload_deadline": upload_deadline.isoformat(sep=" "),
                    "upload_timestamp": upload_timestamp.isoformat(sep=" ") if pd.notna(upload_timestamp) else "",
                    "upload_status": upload_status,
                    "quality_status": quality_status,
                    "consent_verified": consent_verified,
                    "equipment_status": equipment_status,
                    "downtime_minutes": downtime_minutes,
                    "rework_required": rework_required,
                })
                collection_no += 1

    df = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Wrote {len(df):,} synthetic collection sessions to {OUT}")
    print("Reminder: all data is fictional and is not sourced from Aktoria Robotics.")


if __name__ == "__main__":
    main()
