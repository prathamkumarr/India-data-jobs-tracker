with jobs as (
    select
        job_id,
        lower(coalesce(title, '') || ' ' || coalesce(description, '')) as blob
    from {{ ref('stg_jobs') }}
),
skills as (
    select skill, keyword from {{ ref('skill_dictionary') }}
)
select distinct
    j.job_id,
    s.skill
from jobs j
join skills s
  on j.blob ~* ('\y' || s.keyword || '\y')