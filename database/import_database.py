import os

import duckdb

if __name__ == '__main__':
    con = duckdb.connect('tutake.duckdb')
    for i,j,k in os.walk('./'):
        for file in k:
            if file.endswith('.parquet'):
                table = os.path.splitext(os.path.basename(file))[0]
                con.execute(f"DROP TABLE IF EXISTS {table};")
                con.execute(f"CREATE TABLE {table} AS SELECT * FROM read_parquet('{file}');")
                con.execute("FORCE CHECKPOINT;")
                print(table)
    con.close()
