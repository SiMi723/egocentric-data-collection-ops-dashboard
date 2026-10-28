from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "collection_operations.csv"

st.set_page_config(
    page_title="Data Collection Operations Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Portfolio-only demo. The dashboard must never imply access to company data.
st.markdown(
    """
    <style>
      .block-container {padding-top: 1.35rem; padding-bottom: 2rem; max-width: 1550px;}
      .eyebrow {text-transform: uppercase; letter-spacing: .12em; font-size: .74rem; color: #64748b; font-weight: 700;}
      .page-title {font-size: 2rem; line-height: 1.15; font-weight: 750; color: #17243a; margin-bottom: .25rem;}
      .sub-title {color: #58677d; margin-bottom: .9rem;}
      div[data-testid="stMetric"] {background: white; border: 1px solid #e3e8ef; border-radius: 12px; padding: 12px 14px;}
      [data-testid="stSidebar"] {background: #f7f9fc;}
      .section-title {font-size: 1.1rem; font-weight: 700; color: #1e2d45; margin: .2rem 0 .35rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="eyebrow">Operations intelligence · Portfolio project</div>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Egocentric Data Collection Operations</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Monitor collection targets, upload timeliness, recording quality, consent checks, and equipment readiness across simulated sites.</div>',
    unsafe_allow_html=True,
)
st.warning(
    "Synthetic portfolio demo: all sites, workers, partners, cameras, and outcomes are fictional. This is not Aktoria Robotics data, does not represent its policies or performance, and is not affiliated with the company.",
    icon="ℹ️",
)


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["date", "upload_deadline", "upload_timestamp"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in ["scheduled_hours", "recorded_hours", "downtime_minutes"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    for col in ["consent_verified", "rework_required"]:
        if df[col].dtype != bool:
            df[col] = df[col].astype(str).str.strip().str.lower().map({"true": True, "1": True, "yes": True, "false": False, "0": False, "no": False}).fillna(False)
        else:
            df[col] = df[col].fillna(False)
    expected = {
        "collection_id", "date", "site_id", "partner_id", "worker_id", "camera_id",
        "scheduled_hours", "recorded_hours", "upload_deadline", "upload_timestamp",
        "upload_status", "quality_status", "consent_verified", "equipment_status",
        "downtime_minutes", "rework_required",
    }
    missing = expected.difference(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")
    return df


def build_exceptions(df: pd.DataFrame) -> pd.DataFrame:
    """Flag sessions that deserve follow-up; thresholds are illustrative demo rules."""
    result = df.copy()
    reasons, actions, severities = [], [], []
    for row in result.itertuples(index=False):
        flags = []
        recommended = []
        levels = []
        target_ratio = row.recorded_hours / row.scheduled_hours if row.scheduled_hours > 0 else 0

        if not row.consent_verified:
            flags.append("Consent not verified")
            recommended.append("Hold from approved-use workflow; verify consent record")
            levels.append("Critical")
        if row.upload_status == "Missing":
            flags.append("Upload missing")
            recommended.append("Contact partner and check upload queue/connectivity")
            levels.append("Critical")
        elif row.upload_status == "Late":
            flags.append("Upload late")
            recommended.append("Check upload delay and confirm receipt")
            levels.append("Medium")
        if row.quality_status == "Fail":
            flags.append("Quality failed")
            recommended.append("Quarantine and review recording; request recollection if needed")
            levels.append("High")
        elif row.quality_status == "Needs review":
            flags.append("Quality review")
            recommended.append("Review sample before accepting recording")
            levels.append("Medium")
        if row.equipment_status == "Repair required":
            flags.append("Equipment repair")
            recommended.append("Remove camera from rotation and log repair")
            levels.append("High")
        elif row.equipment_status == "Battery issue":
            flags.append("Battery issue")
            recommended.append("Charge or replace battery before next session")
            levels.append("Medium")
        if target_ratio < 0.80:
            flags.append("Below 80% of recording target")
            recommended.append("Check staffing, task availability, and equipment downtime")
            levels.append("High" if target_ratio < 0.60 else "Medium")
        if row.rework_required and row.quality_status == "Pass":
            flags.append("Rework requested")
            recommended.append("Review rework reason and close the follow-up")
            levels.append("Medium")

        severity = "Critical" if "Critical" in levels else "High" if "High" in levels else "Medium" if levels else "—"
        reasons.append("; ".join(flags))
        actions.append("; ".join(dict.fromkeys(recommended)))
        severities.append(severity)

    result["exception_types"] = reasons
    result["recommended_action"] = actions
    result["severity"] = severities
    result["target_achievement_pct"] = (result["recorded_hours"] / result["scheduled_hours"].replace(0, pd.NA) * 100).fillna(0)
    return result


try:
    data = load_data(str(DATA_PATH))
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

if data.empty:
    st.error("The dataset is empty. Use generate_data.py to regenerate it.")
    st.stop()

# Sidebar filtering
st.sidebar.title("Dashboard filters")
min_date = data["date"].min().date()
max_date = data["date"].max().date()
date_range = st.sidebar.date_input("Collection date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range if date_range else min_date

sites = sorted(data["site_id"].dropna().unique().tolist())
partners = sorted(data["partner_id"].dropna().unique().tolist())
cameras = sorted(data["camera_id"].dropna().unique().tolist())
selected_sites = st.sidebar.multiselect("Collection site", sites, default=sites)
selected_partners = st.sidebar.multiselect("Collection partner", partners, default=partners)
selected_cameras = st.sidebar.multiselect("Camera", cameras, default=cameras)
st.sidebar.caption("Clear a filter selection to compare subsets. All rates are recalculated from the filtered records.")

filtered = data[
    data["date"].dt.date.between(start_date, end_date)
    & data["site_id"].isin(selected_sites)
    & data["partner_id"].isin(selected_partners)
    & data["camera_id"].isin(selected_cameras)
].copy()

if filtered.empty:
    st.info("No sessions match these filters. Select a wider date range or more sites, partners, or cameras.")
    st.stop()

filtered = build_exceptions(filtered)
total_sessions = len(filtered)
scheduled_hours = float(filtered["scheduled_hours"].sum())
recorded_hours = float(filtered["recorded_hours"].sum())
target_achievement = recorded_hours / scheduled_hours if scheduled_hours else 0.0
on_time_rate = float((filtered["upload_status"] == "On time").sum() / total_sessions)
quality_reviewed = int(filtered["quality_status"].isin(["Pass", "Needs review", "Fail"]).sum())
quality_pass_rate = float((filtered["quality_status"] == "Pass").sum() / quality_reviewed) if quality_reviewed else 0.0
equipment_ready_rate = float((filtered["equipment_status"] == "Ready").sum() / total_sessions)
consent_rate = float(filtered["consent_verified"].sum() / total_sessions)
exception_sessions = int((filtered["exception_types"] != "").sum())

st.caption(
    f"Showing {total_sessions:,} collection sessions · {filtered['date'].min().date():%d %b %Y}–{filtered['date'].max().date():%d %b %Y} · {filtered['site_id'].nunique()} sites"
)

kpi_cols = st.columns(3)
metrics = [
    ("Collection target achievement", f"{target_achievement:.1%}", f"{recorded_hours:,.0f} recorded / {scheduled_hours:,.0f} scheduled hours"),
    ("On-time upload rate", f"{on_time_rate:.1%}", "On-time sessions ÷ all scheduled sessions"),
    ("First-pass quality rate", f"{quality_pass_rate:.1%}", f"Pass ÷ quality-reviewed sessions ({quality_reviewed:,})"),
    ("Equipment readiness", f"{equipment_ready_rate:.1%}", "Sessions reporting equipment as ready"),
    ("Consent verification", f"{consent_rate:.1%}", "Verified sessions ÷ all sessions"),
    ("Sessions needing action", f"{exception_sessions:,}", "Distinct sessions with one or more flags"),
]
for idx, (label, value, help_text) in enumerate(metrics):
    with kpi_cols[idx % 3]:
        st.metric(label, value, help=help_text)
    if idx == 2:
        kpi_cols = st.columns(3)

st.divider()
left, right = st.columns([1.4, 1])
with left:
    st.markdown('<div class="section-title">Daily collection target vs actual</div>', unsafe_allow_html=True)
    daily_data = filtered.assign(collection_date=filtered["date"].dt.date)
    daily = daily_data.groupby("collection_date", as_index=False).agg(
        scheduled_hours=("scheduled_hours", "sum"), recorded_hours=("recorded_hours", "sum")
    )
    daily_long = daily.melt(id_vars="collection_date", value_vars=["scheduled_hours", "recorded_hours"], var_name="Measure", value_name="Hours")
    daily_long["Measure"] = daily_long["Measure"].map({"scheduled_hours": "Scheduled hours", "recorded_hours": "Recorded hours"})
    fig = px.line(daily_long, x="collection_date", y="Hours", color="Measure", markers=False, template="plotly_white",
                  color_discrete_sequence=["#64748b", "#2563eb"])
    fig.update_layout(height=330, margin=dict(l=8, r=8, t=12, b=8), legend_title_text="", hovermode="x unified",
                      xaxis_title="Collection date", yaxis=dict(gridcolor="#edf0f4"))
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown('<div class="section-title">Upload status</div>', unsafe_allow_html=True)
    upload_summary = filtered["upload_status"].value_counts().rename_axis("Upload status").reset_index(name="Sessions")
    fig = px.pie(upload_summary, names="Upload status", values="Sessions", hole=0.52, template="plotly_white")
    fig.update_layout(height=330, margin=dict(l=8, r=8, t=12, b=8), legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

left2, right2 = st.columns([1.15, 1])
with left2:
    st.markdown('<div class="section-title">Site-level target achievement</div>', unsafe_allow_html=True)
    site_summary = filtered.groupby("site_id", as_index=False).agg(
        scheduled_hours=("scheduled_hours", "sum"), recorded_hours=("recorded_hours", "sum"),
        sessions=("collection_id", "nunique"), consent_verified=("consent_verified", "sum")
    )
    site_summary["Target achievement (%)"] = site_summary["recorded_hours"] / site_summary["scheduled_hours"].replace(0, pd.NA) * 100
    site_summary["Consent verification (%)"] = site_summary["consent_verified"] / site_summary["sessions"].replace(0, pd.NA) * 100
    site_long = site_summary.melt(id_vars="site_id", value_vars=["Target achievement (%)", "Consent verification (%)"], var_name="Metric", value_name="Rate")
    fig = px.bar(site_long, x="site_id", y="Rate", color="Metric", barmode="group", template="plotly_white",
                 color_discrete_sequence=["#2563eb", "#0f9f8f"])
    fig.update_layout(height=320, margin=dict(l=8, r=8, t=12, b=8), legend_title_text="", yaxis_title="Percent", xaxis_title="Site", yaxis=dict(gridcolor="#edf0f4"))
    st.plotly_chart(fig, use_container_width=True)
with right2:
    st.markdown('<div class="section-title">Equipment status and downtime</div>', unsafe_allow_html=True)
    equipment_summary = filtered.groupby("equipment_status", as_index=False).agg(
        sessions=("collection_id", "nunique"), downtime_minutes=("downtime_minutes", "sum")
    ).sort_values("sessions", ascending=True)
    fig = px.bar(equipment_summary, x="sessions", y="equipment_status", orientation="h", color="equipment_status",
                 hover_data=["downtime_minutes"], template="plotly_white")
    fig.update_layout(height=320, margin=dict(l=8, r=8, t=12, b=8), showlegend=False, xaxis_title="Sessions", yaxis_title="", xaxis=dict(gridcolor="#edf0f4"))
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown('<div class="section-title">Operational exceptions queue</div>', unsafe_allow_html=True)
st.caption("Illustrative rules, not company policy: flag missing uploads, late uploads, unverified consent, failed/review quality, equipment issues, recording below 80% of scheduled hours, or rework. Any session with unverified consent should remain outside an approved-use workflow until verified.")
exceptions = filtered[filtered["exception_types"] != ""].copy()
if exceptions.empty:
    st.success("No sessions need action under the current illustrative rules.")
else:
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "—": 3}
    exceptions["severity_order"] = exceptions["severity"].map(severity_order).fillna(3)
    exceptions = exceptions.sort_values(["severity_order", "date", "site_id"], ascending=[True, False, True])
    show_cols = ["collection_id", "date", "site_id", "partner_id", "camera_id", "severity", "exception_types", "upload_status", "quality_status", "consent_verified", "equipment_status", "target_achievement_pct", "recommended_action"]
    display = exceptions[show_cols].copy()
    display["date"] = display["date"].dt.strftime("%Y-%m-%d")
    display["target_achievement_pct"] = display["target_achievement_pct"].map(lambda x: f"{x:.0f}%")
    st.dataframe(display, use_container_width=True, hide_index=True, height=380)
    export_cols = ["collection_id", "date", "site_id", "partner_id", "worker_id", "camera_id", "scheduled_hours", "recorded_hours", "upload_status", "quality_status", "consent_verified", "equipment_status", "downtime_minutes", "rework_required", "severity", "exception_types", "recommended_action"]
    export_df = exceptions[export_cols].copy()
    export_df["date"] = export_df["date"].dt.strftime("%Y-%m-%d")
    st.download_button(
        "Download filtered exceptions (CSV)",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name="collection_operations_exceptions.csv",
        mime="text/csv",
    )

with st.expander("Metric definitions, assumptions, and limitations"):
    st.markdown(
        """
        - **Collection target achievement** = total recorded hours ÷ total scheduled hours. It may exceed 100% if recorded hours exceed the plan.
        - **On-time upload rate** = sessions marked `On time` ÷ all sessions in the filtered data. Late and missing uploads count as not on time.
        - **First-pass quality rate** = sessions marked `Pass` ÷ sessions with an assessed quality status (`Pass`, `Needs review`, or `Fail`). Sessions with a missing upload are marked `Not reviewed` and excluded from this denominator.
        - **Equipment readiness** = sessions whose equipment status is `Ready` ÷ all sessions. This is a session-level indicator, not a hardware uptime calculation.
        - **Consent verification** = sessions with verified consent ÷ all sessions. Unverified records are flagged and should not be treated as compliant.
        - **Sessions needing action** = distinct collection sessions with one or more exception flags; one session can have multiple flags.

        **Limitations:** Data is synthetic and not from Aktoria Robotics. All exception thresholds are illustrative. A real deployment would require agreed definitions, approved data access, privacy safeguards, and validation with operations staff. The dataset is session-level, so these metrics are demonstrations rather than real-world performance estimates.
        """
    )
st.caption("Built as an independent portfolio project. All data is synthetic; no company affiliation or operational findings are implied.")
