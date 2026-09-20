from pathlib import Path

import duckdb
import streamlit as st

DB_PATH = Path(__file__).resolve().parent.parent / "dev.duckdb"

st.set_page_config(page_title="PR Lifecycle & DORA Metrics", layout="wide")


@st.cache_data(ttl=60)
def load_mart():
    # read_only=True so this never competes with dbt for a write lock on dev.duckdb
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute(
        "select * from main.mart_dora_metrics_daily order by metric_date"
    ).df()
    con.close()
    return df


@st.cache_data(ttl=60)
def load_summary():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    total_merged_prs, avg_lead_time_hours, days_tracked = con.execute("""
        select
            sum(deployment_frequency) as total_merged_prs,
            avg(avg_lead_time_hours) as avg_lead_time_hours,
            count(*) as days_tracked
        from main.mart_dora_metrics_daily
    """).fetchone()
    con.close()
    return total_merged_prs, avg_lead_time_hours, days_tracked


st.title("PR Lifecycle & DORA Metrics")
st.caption("encode/httpx — read live from mart_dora_metrics_daily in dev.duckdb")

total_merged_prs, avg_lead_time_hours, days_tracked = load_summary()

col1, col2, col3 = st.columns(3)
col1.metric("Total PRs Merged", f"{total_merged_prs:,}")
col2.metric("Avg Lead Time (hrs)", f"{avg_lead_time_hours:,.1f}")
col3.metric("Days Tracked", f"{days_tracked:,}")

st.divider()

mart = load_mart()

st.subheader("Deployment Frequency")
st.line_chart(mart, x="metric_date", y="deployment_frequency")
st.caption(
    "PRs merged per day (a merge is used as a proxy for a deployment — see README "
    "known limitations). A healthy trend is steady or rising activity without long "
    "silent gaps; a flat line at zero for weeks usually means the team stopped "
    "shipping, not that everything's fine."
)

st.subheader("Lead Time for Changes")
st.line_chart(mart, x="metric_date", y="avg_lead_time_hours")
st.caption(
    "Average hours from PR open to merge, for PRs merged that day (days with no "
    "merges show no point, not zero). A healthy trend stays low and stable or "
    "trends downward; sustained upward spikes usually mean PRs are sitting "
    "unreviewed, not that the work itself got harder."
)
