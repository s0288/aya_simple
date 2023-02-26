-- fasten individual stats
select
    telegram_id,
    count(*) as anzahl_fasten,
    percentile_cont(0.5) within group (order by event_value) as median_dauer
from prod.aya_events
where event_name = 'fast_end'
group by telegram_id;

-- fasten group stats
select
    count(*) as anzahl_fasten,
    percentile_cont(0.5) within group (order by event_value) as median_dauer
from prod.aya_events
where
    event_name = 'fast_end'
    and extract(month from timestamp_saved) = extract(month from current_date)
;
