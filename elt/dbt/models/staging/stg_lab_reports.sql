-- Staging: clean parsed lab report results

select
    cast(id as string)                      as report_id,
    cast(plot_id as string)                 as plot_id,
    cast(lab_name as string)                as lab_name,
    date(sample_date)                       as sample_date,
    cast(sample_depth_cm as int64)          as sample_depth_cm,
    cast(ph as float64)                     as ph,
    cast(nitrogen_mg_kg as float64)         as nitrogen_mg_kg,
    cast(phosphorus_mg_kg as float64)       as phosphorus_mg_kg,
    cast(potassium_mg_kg as float64)        as potassium_mg_kg,
    cast(ec_ds_m as float64)                as ec_ds_m,
    cast(organic_matter_pct as float64)     as organic_matter_pct,
    cast(cec_meq_100g as float64)           as cec_meq_100g

from {{ source('terrasensus_raw', 'lab_reports') }}
where plot_id is not null
  and status = 'complete'
