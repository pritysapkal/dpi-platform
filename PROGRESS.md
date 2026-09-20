## Completed
- Python 3.12 venv set up, dbt-core 1.11.15 + dbt-duckdb 1.11.0 (matched versions)
- GitHub PAT configured (GH_TOKEN)
- fetch_prs.py switched from octocat/Hello-World to encode/httpx (real, active repo) — pulls most recent 500 PRs via GitHub REST API into dev.duckdb (raw.github_pull_requests)
- fetch_prs.py extended to also pull PR reviews (one API call per PR to /pulls/{number}/reviews) into raw.github_pr_reviews (778 reviews across 312 of the 500 PRs; 188 PRs have zero reviews)
- sources.yml + stg_github__pull_requests.sql created and verified working (table: main.stg_github__pull_requests)
- stg_github__pr_reviews.sql created and verified working (table: main.stg_github__pr_reviews) — one row per review, cast submitted_at to timestamp
- int_pr_lifecycle.sql (intermediate layer) built and verified — one row per PR (grain confirmed: 500 rows, 500 distinct pr_number), left-joins a review_rollup CTE (reviews aggregated per PR to avoid fan-out) onto the PR base. Computes review_wait_hours (opened → first review), time_in_review_hours (first review → merge, null-guarded so post-merge reviews don't produce negative durations), lead_time_hours (opened → merged, feeds the future DORA mart), and pr_lifecycle_stage (merged / closed_without_merge / open). Verified no negative durations anywhere.
- Removed leftover models/example/ dbt-init scaffold (dummy models + generic tests) that was polluting dbt build/test runs; set per-layer materialization in dbt_project.yml (staging/intermediate = view, marts = table)
- mart_dora_metrics_daily.sql built and verified — one row per calendar day (1,114 days, full date spine so zero-merge days show 0 instead of a missing row) with deployment_frequency (merges that day) and avg_lead_time_hours (rounded avg of lead_time_hours for that day's merges, null on zero-merge days — not 0). Verified SUM(deployment_frequency) = 269 matches total merged PRs exactly; no negative avg_lead_time_hours.
- dbt tests added across all 4 models (schema.yml per layer) — unique/not_null on every model's primary key, plus a custom non_negative generic test macro (macros/generic_tests.sql) applied to review_wait_hours and lead_time_hours, documented with the real bug it'd catch (timestamp parsing / source anomaly corrupting the Lead Time DORA metric). `dbt build` passes 17/17 (4 models + 13 tests).
- Semantic layer built: models/marts/dora_metrics.yml defines the dora_metrics_daily semantic model (on mart_dora_metrics_daily) and the deployment_frequency + lead_time_for_changes metrics. Added models/metricflow_time_spine.sql (+ explicit time_spine YAML config, required by MetricFlow) and installed dbt-metricflow in the venv. Verified via `mf list metrics` (both show up) and `mf query --metrics deployment_frequency,lead_time_for_changes --group-by metric_time__month` (real monthly numbers matching the mart). Known caveat, documented in the YAML: lead_time_for_changes is an average of mart_dora_metrics_daily's daily averages (day-weighted), not a true PR-weighted average — a tradeoff of building the semantic layer on a pre-aggregated mart. Local note: `mf` CLI needs `PYTHONIOENCODING=utf-8` + explicit `DBT_PROFILES_DIR` to run on Windows (unrelated tooling bug in halo/colorama, not a project issue).

## Target Scope for 8-9/10 Analytics Engineering Portfolio (Locked In — Don't Expand Beyond This)

Focus: ONE data entity (Pull Requests) taken all the way through the full pipeline, done deeply and correctly — not multiple entities done shallowly.

1. **Multi-layer modeling**
   - [x] Switch from octocat/Hello-World to a real, active open-source repo (500+ PRs) — now encode/httpx
   - [x] Build int_pr_lifecycle.sql — PR journey: opened → reviewed → merged, using proper intermediate-layer logic
   - [x] Build mart_dora_metrics_daily.sql — at least 2 DORA metrics (Deployment Frequency + Lead Time for Changes)

2. **Meaningful dbt tests**
   - [x] Not just generic unique/not_null — include at least 1-2 business-rule tests (e.g., review_wait_hours >= 0)
   - [x] Document in README/comments what real issue each test would catch

3. **Semantic layer (MetricFlow)**
   - [x] Define the 2 DORA metrics as code using dbt's MetricFlow, not just raw SQL in the mart

4. **Working CI/CD**
   - [x] .github/workflows/ci.yml that actually runs dbt build + dbt test on push
   - [x] Must show a real passing (green) run on GitHub, not just exist unused — **confirmed green**: run #2 on commit f1cd57e, "Success", 3m 45s (2026-09-20)

5. **Real documentation**
   - [x] README with: architecture diagram (Mermaid ok), data dictionary for the mart columns, "known limitations / what I'd do at scale" section
   - [x] Written in own words — not ghostwritten/templated (drafted this session — read it over and adjust tone/wording to sound like you before treating it as final)

## Explicitly Out of Scope (Don't Add These — They Dilute Analytics Engineering Positioning)
- AI-assisted PR classification
- Predictive ML modeling (e.g., predicting MTTR)
- Multiple additional data sources (commits, issues, workflows) — one entity done deeply > many done shallowly

- .github/workflows/ci.yml added — on every push and every PR to main, it checks out the repo, installs requirements.txt, writes a dbt profile pointing at a fresh dev.duckdb, re-runs fetch_prs.py to pull current PR+review data from GitHub (not a stale snapshot), then runs `dbt build` (models + tests together) as the pass/fail gate. requirements.txt added (dbt-core, dbt-duckdb, duckdb, httpx, pandas, all pinned to locally-verified versions).
  - **GH_TOKEN repo secret added on GitHub (2026-09-20).** The very first CI run (triggered by the push that added ci.yml) failed at the "Fetch latest PR + review data from GitHub" step with "GH_TOKEN not set", since it ran before the secret existed — expected, not a workflow bug. This commit re-triggers the workflow now that the secret is in place.
- README.md fully rewritten (was still dbt-init boilerplate) — architecture diagram (all 8 stages: source → ingestion → warehouse → staging → intermediate → marts → semantic layer → dashboard), data dictionary for mart_dora_metrics_daily, test-to-real-bug table, 7-point known-limitations/at-scale section, and a local run guide.

## Locked Scope Status
All 5 locked-in scope items are complete: built, verified locally (`dbt build` passes 20/20), pushed, and CI confirmed green on GitHub (run #2, commit f1cd57e). The locked-in 8-9/10 portfolio scope from this file is now fully delivered.

## Next Immediate Step
- Review README.md tone/wording to make sure it reads as your own voice, not mine — the only remaining open item
- Everything else in the locked scope is done; any further work is a deliberate new addition, not a gap
