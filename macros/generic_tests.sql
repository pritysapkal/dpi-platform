{% test non_negative(model, column_name) %}

-- Fails if any row has a negative value in this column.
-- Applied to review_wait_hours and lead_time_hours in int_pr_lifecycle: both are
-- computed as date_diff(...) between two timestamps, so a negative value can only
-- mean a timestamp parsing bug or a source data anomaly (e.g. a merged_at earlier
-- than created_at). Left undetected, either would silently corrupt the DORA
-- Lead Time for Changes metric downstream in mart_dora_metrics_daily.

select *
from {{ model }}
where {{ column_name }} < 0

{% endtest %}
