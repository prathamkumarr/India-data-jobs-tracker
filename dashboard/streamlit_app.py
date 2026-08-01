import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

st.set_page_config(
    page_title="India Data Jobs Tracker",
    page_icon="📡",
    layout="wide",
)

# ─────────────────────────── design tokens ───────────────────────────
INK     = "#12172B"
SLATE   = "#5A6485"
INDIGO  = "#4338CA"
INDIGO2 = "#818CF8"
AMBER   = "#F59E0B"
PAPER   = "#FBFBFD"
LINE    = "#E4E7F0"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');

.stApp {{ background: {PAPER}; }}
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

.masthead {{
    border-bottom: 2px solid {INK};
    padding-bottom: 1.1rem;
    margin-bottom: 2rem;
}}
.masthead h1 {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 2.9rem;
    line-height: 1.05;
    letter-spacing: -0.03em;
    color: {INK};
    margin: 0 0 .55rem 0;
}}
.eyebrow {{
    font-family: 'JetBrains Mono', monospace;
    font-size: .7rem;
    letter-spacing: .16em;
    text-transform: uppercase;
    color: {SLATE};
    margin-bottom: .5rem;
}}
.livedot {{
    display:inline-block; width:7px; height:7px; border-radius:50%;
    background:{AMBER}; margin-right:7px; vertical-align:middle;
    box-shadow:0 0 0 0 rgba(245,158,11,.7);
    animation: pulse 2.2s infinite;
}}
@keyframes pulse {{
    0%   {{ box-shadow:0 0 0 0 rgba(245,158,11,.65); }}
    70%  {{ box-shadow:0 0 0 9px rgba(245,158,11,0); }}
    100% {{ box-shadow:0 0 0 0 rgba(245,158,11,0); }}
}}
@media (prefers-reduced-motion: reduce) {{
    .livedot {{ animation: none; }}
}}

.statcard {{
    border: 1px solid {LINE};
    border-left: 3px solid {INDIGO};
    border-radius: 3px;
    padding: 1.1rem 1.3rem;
    background: #fff;
}}
.statcard .label {{
    font-family:'JetBrains Mono', monospace;
    font-size:.66rem; letter-spacing:.14em; text-transform:uppercase;
    color:{SLATE}; margin-bottom:.35rem;
}}
.statcard .value {{
    font-family:'JetBrains Mono', monospace;
    font-size:2.1rem; font-weight:700; color:{INK}; line-height:1;
}}

.sectionhead {{
    font-family:'Space Grotesk', sans-serif;
    font-weight:700; font-size:1.35rem; color:{INK};
    letter-spacing:-.015em; margin:2.6rem 0 .2rem 0;
}}
.sectionsub {{ color:{SLATE}; font-size:.9rem; margin-bottom:1.1rem; }}

footer, #MainMenu {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)


def section(title, sub=""):
    st.markdown(f'<div class="sectionhead">{title}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="sectionsub">{sub}</div>', unsafe_allow_html=True)


# ─────────────────────────── data ───────────────────────────
@st.cache_resource
def get_engine():
    s = st.secrets["supabase"]
    return create_engine(URL.create(
        drivername="postgresql+psycopg2",
        username=s["user"], password=s["password"],
        host=s["host"], port=int(s["port"]), database=s["dbname"],
    ))


@st.cache_data(ttl=3600)
def q(sql):
    return pd.read_sql(sql, get_engine())


PLOT_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=SLATE, size=12),
    margin=dict(l=0, r=10, t=10, b=0),
    xaxis=dict(gridcolor=LINE, zeroline=False),
    yaxis=dict(gridcolor=LINE, zeroline=False),
)

# ─────────────────────────── masthead ───────────────────────────
try:
    t = q("""
        select count(*) as jobs,
               max(last_seen_date) as latest,
               count(distinct company) as companies
        from analytics.stg_jobs
    """)
except Exception as e:
    st.error(f"Could not reach the database: {e}")
    st.stop()

st.markdown(f"""
<div class="masthead">
  <div class="eyebrow"><span class="livedot"></span>Live pipeline · updated {t['latest'][0]}</div>
  <h1>India Data-Analyst<br>Job Market Tracker</h1>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
for col, label, value in [
    (c1, "Postings tracked", f"{int(t['jobs'][0]):,}"),
    (c2, "Companies hiring", f"{int(t['companies'][0]):,}"),
    (c3, "Refresh cadence", "Daily"),
]:
    col.markdown(
        f'<div class="statcard"><div class="label">{label}</div>'
        f'<div class="value">{value}</div></div>',
        unsafe_allow_html=True)

# ─────────────────────────── skill demand ───────────────────────────
section("Most in-demand skills",
        "Postings seen in the last 7 days that mention each skill")

sk = q("""
    select skill, n_jobs from analytics.mart_skill_demand
    order by n_jobs desc limit 12
""").sort_values("n_jobs")

fig = px.bar(sk, x="n_jobs", y="skill", orientation="h",
             color="n_jobs", color_continuous_scale=[INDIGO2, INDIGO])
fig.update_layout(**PLOT_LAYOUT, height=460, showlegend=False,
                  coloraxis_showscale=False)
fig.update_traces(hovertemplate="<b>%{y}</b><br>%{x} postings<extra></extra>")
fig.update_xaxes(title=None)
fig.update_yaxes(title=None, tickfont=dict(size=13, color=INK))
st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────── skill pairs ───────────────────────────
section("Skills demanded together",
        "Employers hire for bundles, not single tools")

co = q("""
    select skill_a, skill_b, n_jobs from analytics.mart_skill_cooccurrence
    order by n_jobs desc limit 12
""")
co["pair"] = co["skill_a"] + "  ·  " + co["skill_b"]
co = co.sort_values("n_jobs")

fig2 = px.bar(co, x="n_jobs", y="pair", orientation="h")
fig2.update_traces(marker_color=INK,
                   hovertemplate="<b>%{y}</b><br>%{x} postings<extra></extra>")
fig2.update_layout(**PLOT_LAYOUT, height=440)
fig2.update_xaxes(title=None)
fig2.update_yaxes(title=None, tickfont=dict(size=12, color=INK))
st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────── cities ───────────────────────────
section("Where the roles are", "Postings by normalised city")

city = q("""
    select city, n_jobs from analytics.mart_posting_longevity
    order by n_jobs desc
""")
fig3 = px.bar(city, x="city", y="n_jobs")
fig3.update_traces(marker_color=INDIGO,
                   hovertemplate="<b>%{x}</b><br>%{y} postings<extra></extra>")
fig3.update_layout(**PLOT_LAYOUT, height=380)
fig3.update_xaxes(title=None, tickfont=dict(size=12, color=INK))
fig3.update_yaxes(title=None)
st.plotly_chart(fig3, use_container_width=True)

# ─────────────────────────── velocity ───────────────────────────
section("Market velocity",
        "Distinct live postings observed each day — is the market heating or cooling?")

vel = q("""
    select snapshot_date, live_postings from analytics.mart_daily_velocity
    order by snapshot_date
""")

if len(vel) < 7:
    st.info(f"{len(vel)} days of history so far. This chart sharpens after a few weeks of daily collection.")

fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=vel["snapshot_date"], y=vel["live_postings"],
    mode="lines+markers", line=dict(color=AMBER, width=2.5),
    marker=dict(size=7, color=AMBER),
    fill="tozeroy", fillcolor="rgba(245,158,11,0.10)",
    hovertemplate="<b>%{x|%d %b}</b><br>%{y} live postings<extra></extra>",
))
fig4.update_layout(**PLOT_LAYOUT, height=340)
st.plotly_chart(fig4, use_container_width=True)

# ─────────────────────────── longevity ───────────────────────────
section("How long postings stay open",
        "Roles open 30+ days may signal perpetual hiring or inactive listings")

lon = q("select * from analytics.mart_posting_longevity order by n_jobs desc")
st.dataframe(lon, width='stretch', hide_index=True)
st.caption("Longevity metrics need 30+ days of collection history to be meaningful.")

# ─────────────────────────── footer ───────────────────────────
st.markdown(f"""
<div style="border-top:1px solid {LINE}; margin-top:3rem; padding-top:1.2rem;
            font-size:.82rem; color:{SLATE}; line-height:1.7;">
<b style="color:{INK};">Method.</b> Job postings are collected daily from the Adzuna API,
deduplicated on posting ID, and stored with first-seen and last-seen dates so the market
can be measured over time. Transformations and data tests run in dbt.<br>
<b style="color:{INK};">Limitations.</b> Adzuna is a sample of the Indian market, not a census.
Descriptions are snippets, so skill detection undercounts. Salary is sparsely reported.<br>
<span style="font-family:'JetBrains Mono',monospace; font-size:.72rem; letter-spacing:.08em;">
PYTHON → POSTGRES → DBT → STREAMLIT · BUILT BY PRATHAM KUMAR</span>
</div>
""", unsafe_allow_html=True)