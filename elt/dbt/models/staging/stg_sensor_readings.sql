-- Staging: clean raw sensor readings from Cloud SQL → BigQuery Datastream
-- Casts types, renames to snake_case, filters out null plot_ids.

select
    cast(id as string)                  as reading_id,
    cast(plot_id as string)             as plot_id,
    timestamp_micros(cast(created_at as int64))
                                        as reading_at,
    cast(moisture as float64)           as moisture_pct,
    cast(temperature as float64)        as temperature_c,
    cast(ph as float64)                 as ph,
    cast(nitrogen as float64)           as nitrogen_mg_kg,
    cast(phosphorus as float64)         as phosphorus_mg_kg,
    cast(potassium as float64)          as potassium_mg_kg,
    cast(ec as float64)                 as ec_ds_m

from {{ source('terrasensus_raw', 'sensor_readings') }}
where plot_id is not null
