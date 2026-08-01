select
    city,
    count(*) as n_jobs,
    round(avg(days_live), 1) as avg_days_live,
    percentile_cont(0.5) within group (order by days_live) as median_days_live,
    count(*) filter (where days_live >= 30) as jobs_live_30d_plus,
    round(100.0 * count(*) filter (where days_live >= 30)
          / nullif(count(*), 0), 1) as pct_open_30d_plus
from {{ ref('stg_jobs') }}
group by city
order by n_jobs desc