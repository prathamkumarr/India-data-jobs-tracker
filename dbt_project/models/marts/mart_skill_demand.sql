with live as (
    select job_id from {{ ref('stg_jobs') }}
    where last_seen_date >= current_date - 7
),
jobs_with_skills as (
    select distinct s.job_id
    from {{ ref('int_job_skills') }} s
    join live using (job_id)
),
counts as (
    select s.skill, count(*) as n_jobs
    from {{ ref('int_job_skills') }} s
    join live using (job_id)
    group by 1
)
select
    skill,
    n_jobs,
    round(100.0 * n_jobs / nullif((select count(*) from live), 0), 1) as pct_of_all_live,
    round(100.0 * n_jobs / nullif((select count(*) from jobs_with_skills), 0), 1) as pct_of_skilled_jobs
from counts
order by n_jobs desc