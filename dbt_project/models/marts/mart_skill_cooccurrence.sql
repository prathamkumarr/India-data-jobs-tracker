select
    a.skill as skill_a,
    b.skill as skill_b,
    count(*) as n_jobs
from {{ ref('int_job_skills') }} a
join {{ ref('int_job_skills') }} b
  on a.job_id = b.job_id
 and a.skill < b.skill
group by 1, 2
order by n_jobs desc