{{ config(materialized='table') }}

-- Required by MetricFlow for time-based aggregation (e.g. summing deployment_count
-- by week/month). Spans well beyond the PR data's actual date range on purpose —
-- it's a generic calendar, not something re-generated per dataset.
select unnest(generate_series(cast('2000-01-01' as date), cast('2035-12-31' as date), interval 1 day)) as date_day
