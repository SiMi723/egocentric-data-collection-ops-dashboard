"""Quick data-quality checks for the synthetic portfolio dataset.
Run from the project root: python validate_data.py
This checks the sample CSV; the Streamlit app still needs to be launched separately.
"""
from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).resolve().parent / "data" / "collection_operations.csv"
REQUIRED = {
    "collection_id", "date", "site_id", "partner_id", "worker_id", "camera_id",
    "scheduled_hours", "recorded_hours", "upload_deadline", "upload_timestamp",
    "upload_status", "quality_status", "consent_verified", "equipment_status",
    "downtime_minutes", "rework_required",
}


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    missing = REQUIRED.difference(df.columns)
    assert not missing, f"Missing columns: {sorted(missing)}"
    assert not df.empty, "Dataset is empty"
    assert df["collection_id"].is_unique, "collection_id must be unique"
    assert df["scheduled_hours"].gt(0).all(), "scheduled_hours must be positive"
    assert df["recorded_hours"].ge(0).all(), "recorded_hours cannot be negative"
    assert df["downtime_minutes"].ge(0).all(), "downtime_minutes cannot be negative"
    assert set(df["upload_status"]) <= {"On time", "Late", "Missing"}
    assert set(df["quality_status"]) <= {"Pass", "Needs review", "Fail", "Not reviewed"}
    missing_upload_timestamps = df.loc[df["upload_status"] == "Missing", "upload_timestamp"]
    assert (missing_upload_timestamps.isna() | missing_upload_timestamps.astype(str).str.strip().eq("")).all(), "Missing uploads must not have timestamps"
    assert df.loc[df["upload_status"] == "Missing", "quality_status"].eq("Not reviewed").all(), "Missing uploads cannot have a quality assessment"

    parsed_deadline = pd.to_datetime(df["upload_deadline"], errors="coerce")
    parsed_upload = pd.to_datetime(df["upload_timestamp"], errors="coerce")
    on_time = df["upload_status"].eq("On time")
    late = df["upload_status"].eq("Late")
    assert parsed_upload.loc[on_time].notna().all(), "On-time uploads need a timestamp"
    assert parsed_upload.loc[late].notna().all(), "Late uploads need a timestamp"
    assert parsed_upload.loc[on_time].le(parsed_deadline.loc[on_time]).all(), "On-time timestamps must meet deadline"
    assert parsed_upload.loc[late].gt(parsed_deadline.loc[late]).all(), "Late timestamps must be after deadline"

    sessions = len(df)
    total_scheduled = df["scheduled_hours"].sum()
    total_recorded = df["recorded_hours"].sum()
    assessed = df["quality_status"].isin(["Pass", "Needs review", "Fail"])
    quality_pass_rate = df["quality_status"].eq("Pass").sum() / assessed.sum() if assessed.sum() else 0
    on_time_rate = on_time.sum() / sessions
    consent_rate = df["consent_verified"].astype(str).str.lower().isin(["true", "1", "yes"]).sum() / sessions

    print("DATA VALIDATION PASSED")
    print(f"Rows: {sessions:,}; unique sessions: {df['collection_id'].nunique():,}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Sites: {df['site_id'].nunique()}; partners: {df['partner_id'].nunique()}; cameras: {df['camera_id'].nunique()}")
    print(f"Collection target achievement: {total_recorded / total_scheduled:.1%}")
    print(f"On-time upload rate (all sessions as denominator): {on_time_rate:.1%}")
    print(f"First-pass quality rate (assessed sessions only): {quality_pass_rate:.1%}")
    print(f"Consent verification rate: {consent_rate:.1%}")
    print("Reminder: these are synthetic demo metrics, not real operational findings.")


if __name__ == "__main__":
    main()
