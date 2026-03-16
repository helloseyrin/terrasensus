-- Mart: daily aggregated soil health per plot
-- Powers Looker Studio management reports and Grafana daily trend charts.

select
    plot_id,
    date(reading_at)            as reading_date,
    round(avg(moisture_pct), 2) as avg_moisture_pct,
    round(min(moisture_pct), 2) as min_moisture_pct,
    round(avg(temperature_c), 2) as avg_temperature_c,
    round(avg(ph), 2)           as avg_ph,
    round(avg(nitrogen_mg_kg), 2) as avg_nitrogen,
    round(avg(phosphorus_mg_kg), 2) as avg_phosphorus,
    round(avg(potassium_mg_kg), 2) as avg_potassium,
    round(avg(ec_ds_m), 3)      as avg_ec,
    count(*)                    as reading_count

from {{ ref('stg_sensor_readings') }}
group by plot_id, reading_date
order by plot_id, reading_date desc
