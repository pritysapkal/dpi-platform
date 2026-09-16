import duckdb
con = duckdb.connect('dev.duckdb')
print(con.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name = 'stg_github__pull_requests'").fetchall())
