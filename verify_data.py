import duckdb
con = duckdb.connect('dev.duckdb')
print(con.execute('SELECT COUNT(*) FROM raw.github_pull_requests').fetchall())
print(con.execute('SELECT number, title, state FROM raw.github_pull_requests LIMIT 5').fetchall())
con.close()
