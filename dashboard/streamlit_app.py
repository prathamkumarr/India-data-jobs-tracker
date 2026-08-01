import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

st.set_page_config(page_title="India Data Jobs Tracker", layout="wide")

@st.cache_resource
def get_engine():
    s = st.secrets["supabase"]
    return create_engine(URL.create(
        drivername="postgresql+psycopg2",
        username=s["user"],
        password=s["password"],
        host=s["host"],
        port=int(s["port"]),
        database=s["dbname"],
    ))

@st.cache_data(ttl=3600)
def q(sql):
    return pd.read_sql(sql, get_engine())

st.title("India Data-Analyst Job Market Tracker")
st.caption("Live pipeline · refreshed daily via GitHub Actions · source: Adzuna API")

# ---------- Headline metrics ----------
try:
    t = q("""
        select count(*) as jobs,
               max(last_seen_date) as latest,
               count(distinct company) as companies
        from analytics.stg_jobs
    """)
    c1, c2, c3 = st.columns(3)
    c1.metric("Postings tracked", f"{int(t['jobs'][0]):,}")
    c2.metric("Companies", f"{int(t['companies'][0]):,}")
    c3.metric("Last updated", str(t['latest'][0]))
except Exception as e:
    st.error(f"Could not load metrics: {e}")
    st.stop()

st.divider()

# ---------- Skill demand ----------
st.subheader("Most in-demand skills")
st.caption("Share of postings seen in the last 7 days that mention each skill")
sk = q("""
    select skill, n_jobs, pct_of_all_live
    from analytics.mart_skill_demand
    order by n_jobs desc limit 10
""")
st.bar_chart(sk.set_index("skill")["n_jobs"], height=400, horizontal=True)
with st.expander("See the numbers"):
    st.dataframe(sk, width='stretch', hide_index=True)

st.divider()

# ---------- Skill pairs ----------
st.subheader("Which skills are demanded together?")
st.caption("Employers rarely want one tool in isolation — these are the real skill bundles")
co = q("""
    select skill_a, skill_b, n_jobs
    from analytics.mart_skill_cooccurrence
    order by n_jobs desc limit 20
""")
st.dataframe(co, width='stretch', hide_index=True)

st.divider()

# ---------- City breakdown ----------
st.subheader("Where the jobs are")
city = q("""
    select city, n_jobs
    from analytics.mart_posting_longevity
    order by n_jobs desc
""")
st.bar_chart(city.set_index("city")["n_jobs"], height=400)

st.divider()

# ---------- Market velocity ----------
st.subheader("Market velocity")
st.caption("Distinct live postings observed each day — is the market heating or cooling?")
vel = q("""
    select snapshot_date, live_postings
    from analytics.mart_daily_velocity
    order by snapshot_date
""")
if len(vel) < 5:
    st.info(f"Only {len(vel)} days of history so far. This chart becomes meaningful after a few weeks of daily collection.")
st.line_chart(vel.set_index("snapshot_date")["live_postings"], height=350)

st.divider()

# ---------- Longevity ----------
st.subheader("How long do postings stay open?")
st.caption("Roles open 30+ days may indicate perpetual hiring or 'ghost jobs'")
lon = q("select * from analytics.mart_posting_longevity order by n_jobs desc")
st.dataframe(lon, width='stretch', hide_index=True)
st.caption("Note: longevity metrics require 30+ days of collection history to be meaningful.")

st.divider()
st.caption(
    "Data source: Adzuna API (a sample of the Indian market, not a census). "
    "Pipeline: Python → Postgres → dbt → Streamlit. "
    "Built by Pratham Kumar."
)