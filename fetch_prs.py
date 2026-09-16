import os
import httpx
import duckdb
import pandas as pd

token = os.environ.get("GH_TOKEN")
if not token:
    raise ValueError("GH_TOKEN not set. Run: export GH_TOKEN='your_token'")

owner = "octocat"
repo = "Hello-World"

url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
}
params = {"state": "all", "per_page": 100}

print(f"Fetching pull requests for {owner}/{repo}...")

response = httpx.get(url, headers=headers, params=params)
response.raise_for_status()  # will error clearly if something's wrong (bad token, wrong repo, etc.)

prs = response.json()
print(f"Found {len(prs)} pull requests.")

rows = []
for pr in prs:
    rows.append({
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

df = pd.DataFrame(rows)

con = duckdb.connect("dev.duckdb")
con.execute("CREATE SCHEMA IF NOT EXISTS raw")
con.execute("CREATE OR REPLACE TABLE raw.github_pull_requests AS SELECT * FROM df")

print("Data written to raw.github_pull_requests in dev.duckdb")
print(df.head())

con.close()
