import sqlite3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import duckdb
import numpy as np
import os

import sqlalchemy


# 你的SQLite数据库文件所在的目录


def sqlite_type_to_parquet_type(sqlite_type):
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


def migration():
    global name, table_name, columns, fields

    directory = 'D:\\Dataset\\quant\\tutake'

    # 获取目录下所有以.db结尾的文件
    db_files = [f for f in os.listdir(directory) if f.endswith('.db')]

    # 创建或打开DuckDB数据库
    con = duckdb.connect('tutake.duckdb')

    # 对于每个SQLite数据库文件，执行转换操作
    for db_file in db_files:
        # 连接到SQLite数据库
        conn = sqlite3.connect(os.path.join(directory, db_file))

        # 获取数据库中所有表的名称
        table_names = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        table_names = [name[0] for name in table_names]

        # 对于每个表，分块读取数据并写入Parquet文件
        for table_name in table_names:
            if table_name in ['checker_point']:
                continue
            print(f"Start {db_file}.{table_name}")
            cursor = con.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}'")
            table_exists = cursor.fetchone()[0] > 0

            if table_exists:
                duckdb_rows = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchall()[0][0]
                sqlite_rows = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchall()[0][0]
                if sqlite_rows > duckdb_rows:
                    con.execute(f"DROP TABLE {table_name}")
                else:
                    continue

            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            # 打印列的名称和类型
            # for column in columns:
            #     print(f"{column[1]}: {column[2]}")
            # 创建一个字段列表
            fields = [pa.field(column[1], sqlite_type_to_parquet_type(column[2])) for column in columns]
            # 创建一个模式
            schema = pa.schema(fields)

            parquet_file = f'{table_name}.parquet'
            writer = None
            total_rows = 0
            for chunk in pd.read_sql_query(f"SELECT * FROM {table_name}", conn, chunksize=50000):
                total_rows += len(chunk)
                table = pa.Table.from_pandas(df=chunk, schema=schema)
                if writer is None:
                    writer = pq.ParquetWriter(parquet_file, schema)
                writer.write_table(table)
            if writer:
                writer.close()
            # print(f"Table {table_name} in {db_file} contains {total_rows} rows.")

            if total_rows == 0:
                os.remove(parquet_file)
            else:
                # 将Parquet文件的数据读入到DuckDB数据库中的对应表
                con.execute(f"""
            CREATE TABLE {table_name} AS SELECT * FROM parquet_scan('{parquet_file}')
            """)
                # 删除Parquet文件
                os.remove(parquet_file)

                # 打印DuckDB中表的基本信息
                duckdb_rows = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchall()[0][0]
                print(f"Table {table_name} in DuckDB contains {duckdb_rows} rows.")

        conn.close()
    con.close()


# migration()

if __name__ == '__main__':
    engine = sqlalchemy.create_engine('duckdb:///D:\\Dataset\\quant\\tutake\\tutake.duckdb').connect()
    result = engine.execute("select * from tushare_adj_factor limit 10")
    # 打印查询结果
    for row in result:
        print(row)
