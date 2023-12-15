from pathlib import Path

import duckdb
import pandas as pd
from sqlalchemy.orm import DeclarativeMeta
from tutake.api.ts.daily import TushareDaily
import pyarrow as pa

from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


def parquet_type(sqlite_type):
    if sqlite_type in ['INT', 'INTEGER', 'TINYINT', 'SMALLINT', 'MEDIUMINT', 'BIGINT', 'UNSIGNED BIG INT', 'INT2',
                       'INT8']:
        return pa.int64()
    elif sqlite_type in ['TEXT', 'CHARACTER', 'VARCHAR', 'VARYING CHARACTER', 'NCHAR', 'NATIVE CHARACTER', 'NVARCHAR',
                         'TEXT', 'CLOB']:
        return pa.string()
    elif sqlite_type in ['REAL', 'DOUBLE', 'DOUBLE PRECISION', 'FLOAT']:
        return pa.float64()
    elif sqlite_type in ['BLOB']:
        return pa.binary()
    elif sqlite_type in ['BOOLEAN']:
        return pa.bool_()
    elif sqlite_type in ['DATETIME']:
        return pa.timestamp('s')  # 修改为 's'，表示秒
    else:
        raise ValueError(f"Unknown SQLite type: {sqlite_type}")


def parquet_schema(table: DeclarativeMeta):
    return [pa.field(column, parquet_type(str(table.__dict__.get(column).type))) for column in table.__dict__ if
            not column.startswith("_")]


if __name__ == '__main__':
    config = TutakeConfig(project_root())
    file = Path(config.get_tutake_data_dir(), "tutake.duckdb")
    conn = duckdb.connect(str(file))
    # conn.execute("DROP TABLE process_report")
    # conn.execute("ALTER TABLE checker_point ADD COLUMN check_type VARCHAR;")

    # query_result = conn.execute('SELECT * FROM checker_point')
    # print(query_result.fetchdf().to_pickle("test.pickle"))
    # test = pd.read_pickle("test.pickle")
    # test['check_type'] = "check"
    # print(test)
    # conn.register('test', test)
    # conn.execute('CREATE TABLE checker_point1 AS SELECT * FROM test')
    # conn.execute("ALTER TABLE checker_point RENAME TO checker_point2;")
    conn.execute("ALTER TABLE checker_point3 RENAME TO checker_point;")
    # conn.execute("COPY (SELECT * FROM checker_point) TO 'checker_point.parquet' (FORMAT 'parquet')")
    # conn.execute("Create table checker_point4 AS select * from 'checker_point.parquet'")
    # conn.execute("DROP TABLE checker_point")

    # conn.execute("ALTER TABLE checker_point DROP check_type;")
    conn.close()
