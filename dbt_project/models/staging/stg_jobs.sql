with source as (
    select * from {{ source('raw', 'raw_jobs') }}
)
select
    job_id,
    trim(title)   as title,
    trim(company) as company,
    location_raw,
    case
        when location_raw ilike '%bengaluru%' or location_raw ilike '%bangalore%' then 'Bangalore'
        when location_raw ilike '%gurugram%'  or location_raw ilike '%gurgaon%'   then 'Gurugram'
        when location_raw ilike '%noida%'                                          then 'Noida'
        when location_raw ilike '%new delhi%' or location_raw ilike '%delhi%'      then 'Delhi'
        when location_raw ilike '%hyderabad%'                                      then 'Hyderabad'
        when location_raw ilike '%pune%'                                           then 'Pune'
        when location_raw ilike '%mumbai%'                                         then 'Mumbai'
        when location_raw ilike '%chennai%'                                         then 'Chennai'
        else 'Other / Remote'
    end as city,
    description,
    salary_min,
    salary_max,
    contract_type,
    category,
    created_at,
    first_seen_date,
    last_seen_date,
    (last_seen_date - first_seen_date) as days_live
from source