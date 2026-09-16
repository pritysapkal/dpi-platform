## Completed
- Python 3.12 venv set up, dbt-core 1.11.15 + dbt-duckdb 1.11.0 (matched versions)
- GitHub PAT configured (GH_TOKEN)
- fetch_prs.py — pulls PR data from octocat/Hello-World via GitHub REST API into dev.duckdb (raw.github_pull_requests)
- sources.yml + stg_github__pull_requests.sql created and verified working (table: main.stg_github__pull_requests)

## Target Scope for 8-9/10 Analytics Engineering Portfolio (Locked In — Don't Expand Beyond This)

Focus: ONE data entity (Pull Requests) taken all the way through the full pipeline, done deeply and correctly — not multiple entities done shallowly.

1. **Multi-layer modeling**
   - Switch from octocat/Hello-World to a real, active open-source repo (500+ PRs)
   - Build int_pr_lifecycle.sql — PR journey: opened → reviewed → merged, using proper intermediate-layer logic
   - Build mart_dora_metrics_daily.sql — at least 2 DORA metrics (Deployment Frequency + Lead Time for Changes)

2. **Meaningful dbt tests**
   - Not just generic unique/not_null — include at least 1-2 business-rule tests (e.g., review_wait_hours >= 0)
   - Document in README/comments what real issue each test would catch

3. **Semantic layer (MetricFlow)**
   - Define the 2 DORA metrics as code using dbt's MetricFlow, not just raw SQL in the mart

4. **Working CI/CD**
   - .github/workflows/ci.yml that actually runs dbt build + dbt test on push
   - Must show a real passing (green) run on GitHub, not just exist unused

5. **Real documentation**
   - README with: architecture diagram (Mermaid ok), data dictionary for the mart columns, "known limitations / what I'd do at scale" section
   - Written in own words — not ghostwritten/templated

## Explicitly Out of Scope (Don't Add These — They Dilute Analytics Engineering Positioning)
- AI-assisted PR classification
- Predictive ML modeling (e.g., predicting MTTR)
- Multiple additional data sources (commits, issues, workflows) — one entity done deeply > many done shallowly

## Next Immediate Step
- Build int_pr_lifecycle.sql (intermediate layer) — this is the next file to write
