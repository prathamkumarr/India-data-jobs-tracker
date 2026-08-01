select
    snapshot_date,
    count(distinct job_id) as live_postings
from {{ source('raw', 'daily_snapshots') }}
group by 1
order by 1