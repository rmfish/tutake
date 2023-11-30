from pathlib import Path

import duckdb
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
    conn.execute("DROP TABLE tushare_moneyflow_hsgt")
    conn.close()
