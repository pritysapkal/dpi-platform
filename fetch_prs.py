import os
import time
import httpx
import duckdb
import pandas as pd

token = os.environ.get("GH_TOKEN")
if not token:
    raise ValueError("GH_TOKEN not set. Run: export GH_TOKEN='your_token'")

owner = "encode"
repo = "httpx"
pr_limit = 500

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
}


def fetch_recent_prs(owner, repo, limit):
    """Page through /pulls, newest first, until `limit` PRs are collected."""
    prs = []
    page = 1
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"

    while len(prs) < limit:
        params = {
            "state": "all",
            "sort": "created",
            "direction": "desc",
            "per_page": 100,
            "page": page,
        }
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break  # ran out of PRs before hitting the limit
        prs.extend(batch)
        page += 1

    return prs[:limit]


def fetch_reviews_for_pr(owner, repo, pr_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    response = httpx.get(url, headers=headers, params={"per_page": 100})
    response.raise_for_status()
    return response.json()


print(f"Fetching pull requests for {owner}/{repo}...")
raw_prs = fetch_recent_prs(owner, repo, pr_limit)
print(f"Found {len(raw_prs)} pull requests.")

pr_rows = []
for pr in raw_prs:
    pr_rows.append({
        "number": pr["number"],
        "title": pr["title"],
        "state": pr["state"],
        "merged": pr.get("merged_at") is not None,
        "author": pr["user"]["login"] if pr.get("user") else None,
        "created_at": pr["created_at"],
        "updated_at": pr["updated_at"],
        "merged_at": pr.get("merged_at"),
        "closed_at": pr.get("closed_at"),
    })

pr_df = pd.DataFrame(pr_rows)

print("Fetching reviews for each pull request (one API call per PR)...")
review_rows = []
for i, pr in enumerate(raw_prs):
    pr_number = pr["number"]
    for review in fetch_reviews_for_pr(owner, repo, pr_number):
        review_rows.append({
            "pr_number": pr_number,
            "review_id": review["id"],
            "reviewer_login": review["user"]["login"] if review.get("user") else None,
            "review_state": review["state"],
            "submitted_at": review.get("submitted_at"),
        })

    if (i + 1) % 50 == 0:
        print(f"  ...reviews fetched for {i + 1}/{len(raw_prs)} PRs")

    time.sleep(0.05)  # stay polite to GitHub's secondary rate limits

reviews_df = pd.DataFrame(review_rows)
print(f"Found {len(reviews_df)} reviews across {len(raw_prs)} pull requests.")

con = duckdb.connect("dev.duckdb")
con.execute("CREATE SCHEMA IF NOT EXISTS raw")
con.execute("CREATE OR REPLACE TABLE raw.github_pull_requests AS SELECT * FROM pr_df")
con.execute("CREATE OR REPLACE TABLE raw.github_pr_reviews AS SELECT * FROM reviews_df")

print("Data written to raw.github_pull_requests and raw.github_pr_reviews in dev.duckdb")
print(pr_df.head())
print(reviews_df.head())

con.close()
