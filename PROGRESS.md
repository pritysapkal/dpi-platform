## Completed
- Python 3.12 venv set up, dbt-core 1.11.15 + dbt-duckdb 1.11.0 (matched versions)
- GitHub PAT configured (GH_TOKEN)
- fetch_prs.py pulls PR data from octocat/Hello-World via GitHub REST API into dev.duckdb (raw.github_pull_requests)
- sources.yml + stg_github__pull_requests.sql created and verified working (table: main.stg_github__pull_requests)

## Next Steps
- Build int_pr_lifecycle.sql (intermediate layer)
- Build mart_dora_metrics_daily.sql
- Add dbt tests
- Point ingestion at a busier repo (not just octocat/Hello-World) for more realistic data
