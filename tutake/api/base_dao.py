import logging
import os
import pathlib
import threading
import time
from datetime import datetime
from operator import and_
from pathlib import Path
from typing import Type

import duckdb
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import sqlalchemy
from pandas import DataFrame
from sqlalchemy import text, Column, Integer, PickleType, String, Boolean, DateTime
from sqlalchemy.orm import load_only, declarative_base, sessionmaker, DeclarativeMeta

from tutake.utils.config import TutakeConfig

Base = declarative_base()
checker_logger = logging.getLogger('tutake.checker')

id_seq = sqlalchemy.Sequence('id_seq')


class SqliteBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class DuckDBBase(Base):
    __abstract__ = True
    id = Column(Integer, id_seq, server_default=id_seq.next_value(), primary_key=True)


class TutakeTableBase(DuckDBBase):
    __abstract__ = True


class TutakeCheckerPoint(TutakeTableBase):
    __tablename__ = "checker_point"
    table_name = Column(String, index=True, comment='表名')
    points = Column(PickleType, comment='检测点')
    error = Column(Boolean, comment='是否错误的point')
    update_time = Column(DateTime, comment='更新时间', default=datetime.utcnow)
    check_type = Column(String, comment='检测类型')


class DataChecker:

    def __init__(self, engine, name, session_factory, config):
        self.config = config
        self.engine = engine
        self.name = name
        self.session_factory: sessionmaker = session_factory
        TutakeCheckerPoint.__table__.create(bind=self.engine, checkfirst=True)

    def check_point(self, check_type="check") -> (dict, bool):
        session = self.session_factory()
        point = session.query(TutakeCheckerPoint).filter_by(table_name=self.name, check_type=check_type).order_by(
            TutakeCheckerPoint.update_time.desc()).first()
        if point is None:
            return None, True, None
        else:
            return point.points, point.error, point.update_time

    def process_point(self):
        point = self.check_point('process')
        return point[0], point[2]

    def _save(self, error: False, check_type, **points):
        session = self.session_factory()
        model = session.query(TutakeCheckerPoint).filter_by(table_name=self.name, check_type=check_type).first()
        if model:
            model.points = points
            model.update_time = datetime.now()
            session.merge(model)
        else:
            model = TutakeCheckerPoint(table_name=self.name, points=points, error=error, update_time=datetime.now(),
                                       check_type=check_type)
            session.add(model)  # 执行插入操作
        session.commit()

    def save_process_point(self):
        self.save_point('process')

    def save_point(self, check_type="check", **points):
        self._save(False, check_type, **points)

    def error_point(self, check_type="check", **points):
        self._save(True, check_type, **points)


class BaseDao(object):
    """
    Class representing a BaseDao.

    Attributes:
    - engine: The engine used for database connection.
    - session_factory: The session factory for creating sessions.
    - entities: The entities used in the database.
    - database: The name of the database.
    - table_name: The name of the table.
    - query_fields: The fields to query.
    - entity_fields: The fields in the entity.
    - column_mapping: The mapping between columns and types.
    - logger: The logger for the class.
    - time_order: The time order for sorting.
    - checker: The data checker.
    - config: The configuration.
    """
    def __init__(self, engine, session_factory: sessionmaker, entities, database, table_name, query_fields,
                 entity_fields, column_mapping, config: TutakeConfig):
        self.engine = engine
        self.entities = entities
        self.database = database
        self.session_factory = session_factory
        self.table_name = table_name
        self.query_fields = query_fields
        self.entity_fields = entity_fields
        self.column_mapping = column_mapping
        self.logger = logging.getLogger(f'tutake.dao.base.{table_name}')
        self.time_order = config.get_config("tutake.query.time_order")
        self.checker = DataChecker(self.engine, table_name, session_factory, config)
        self.config = config

    def parquet_type(sqlite_type: str):
        if sqlite_type in ['INT', 'INTEGER', 'TINYINT', 'SMALLINT', 'MEDIUMINT', 'BIGINT', 'UNSIGNED BIG INT', 'INT2',
                           'INT8']:
            return pa.int64()
        elif sqlite_type in ['TEXT', 'CHARACTER', 'VARCHAR', 'VARYING CHARACTER', 'NCHAR', 'NATIVE CHARACTER',
                             'NVARCHAR',
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

    def parquet_schema(table_type: Type[DeclarativeMeta]):
        columns = [pa.field(column, BaseDao.parquet_type(str(table_type.__dict__.get(column).type))) for column in
                   table_type.__dict__ if (not column.startswith("_") and (not column == 'id'))]
        columns.insert(0, pa.field('id', pa.int64()))
        return pa.schema(columns)

    def export(self, condition=None, name_suffix=None, _dir=None):
        """
        Export method exports data from a table to a Parquet file.

        Parameters:
            condition (str, optional): SQL condition to filter the data before exporting (default: None)
            name_suffix (str, optional): Suffix to be added to the Parquet file name (default: None)
            _dir (str, optional): Directory where the Parquet file will be saved (default: None)

        Example usage:
            export()                                # Exports all data from the table to the default directory with the default file name
            export(condition="age > 18")            # Exports data from the table where age > 18 to the default directory with the default file name
            export(name_suffix="backup")            # Exports all data from the table to the default directory with a file name appended with '-backup'
            export(_dir="/path/to/directory")       # Exports all data from the table to the specified directory with the default file name
            export(condition="age > 18", _dir="/path/to/directory")   # Exports data from the table where age > 18 to the specified directory with the default file name

        Note:
            - If name_suffix is not provided, the Parquet file name will be generated based on the table name.
            - If _dir is not provided, the default directory will be obtained from the configuration.
            - If _dir is provided, the Parquet file will be saved in the specified directory.

        """
        if name_suffix is None:
            pq_file = f"{self.table_name}.parquet"
        else:
            pq_file = f"{self.table_name}-{name_suffix}.parquet"
        if _dir is None:
            _dir = self.config.get_tutake_data_dir()
        if _dir is not None:
            pq_file = pathlib.Path(_dir, pq_file)
        self.logger.warning(f"Export data of {self.table_name} to {pq_file}")
        conn = self.engine.connect()
        if condition is None:
            conn.execute(f"COPY (SELECT * FROM {self.table_name}) TO '{pq_file}' (FORMAT PARQUET, COMPRESSION 'ZSTD');")
        else:
            conn.execute(f"COPY (SELECT * FROM {self.table_name} where {condition}) TO '{pq_file}' (FORMAT PARQUET, COMPRESSION 'ZSTD');")
        conn.close()

    def columns_meta(self):
        pass

    def delete_all(self):
        """
        Delete all data from the specified table.

        This method deletes all rows from the table associated with the current instance of the class.
        It first logs a warning message indicating the table name, then creates a new session using the session factory.
        Using the session, it executes a query to delete all rows from the table.
        Finally, it commits the changes made in the session to persist the deletion.

        Note:
        - Make sure to use this method with caution, as it permanently deletes all data from the table.

        Example:
            self.delete_all()
        """
        self.logger.warning("Delete all data of {}".format(self.table_name))
        session = self.session_factory()
        session.query(self.entities).delete()
        session.commit()

    def delete_by(self, **kwargs) -> bool:
        """

        This method is used to delete data from a table in the database based on the given condition(s).

        Parameters:
            **kwargs (keyword arguments): A dictionary of column names and their corresponding values to specify the condition(s) for deletion.

        Returns:
            bool: True if deletion is successful, False otherwise.

        Example Usage:
            # Delete a row from the table 'employees' where the 'id' column is 10
            delete_by(table_name='employees', id=10)

        Note:
            - The table name and entity class are obtained from the instance variables of the class.
            - This method internally uses a session factory and commits the changes made to the database.

        """
        self.logger.warning("Delete data from {} by {}".format(self.table_name, kwargs))
        session = self.session_factory()
        session.query(self.entities).filter_by(**kwargs).delete()
        session.commit()
        return True

    def get_ident(self, ident):
        """
        Retrieve a record from the database based on the given ident.

        Parameters:
        - self: The instance of the class.
        - ident: The ident of the record to retrieve.

        Returns:
        - A single record from the database matching the given ident, or None if not found.

        Example:
        session = self.session_factory()
        record = session.query(self.entities).get(ident)
        return record
        """
        session = self.session_factory()
        return session.query(self.entities).get(ident)

    def filter(self, **params):
        session = self.session_factory()
        query = session.query(self.entities).filter_by(**params)
        return query.commit()

    def column_data(self, columns: [], *criteria):
        """
        Fetches column data from the specified table using given criteria.

        Parameters:
            - columns (list[str]): A list of column names to fetch data from.
            - *criteria (tuple): Optional. Criteria to filter the data. It can include multiple filter conditions.

        Returns:
            - list[dict]: A list of dictionaries, where each dictionary represents a row of column data. The keys of the dictionaries are the column names, and the values are the corresponding
        * values for each column.

        Example usage:
            columns = ['name', 'age', 'email']
            criteria = ('age > 18', 'email LIKE "%example.com"')
            data = column_data(columns, *criteria)

            Result:
            [
                {'name': 'John', 'age': 25, 'email': 'john@example.com'},
                {'name': 'Sarah', 'age': 32, 'email': 'sarah@example.com'},
                ...
            ]
        """
        if criteria:
            result = self.session_factory().query(self.entities).filter(*criteria).options(load_only(*columns)).all()
        else:
            result = self.session_factory().query(self.entities).options(load_only(*columns)).all()
        vals = list({key: i.__dict__[key] for key in columns} for i in result)
        return vals

    def distinct(self, column: str, condition: str = ""):
        return self._single_func(column, 'distinct', condition)

    def max(self, column: str, condition: str = ""):
        return self._single_func(column, 'max', condition)

    def min(self, column: str, condition: str = ""):
        return self._single_func(column, 'min', condition)

    def count(self, condition: str = ""):
        return self._single_func('*', 'count', condition)

    def _single_func(self, column: str, func: str, condition: str = ""):
        """

        Method: _single_func

        Description:
        This method performs a SQL query to execute an aggregate function on a specified column in a table. The result of the query is returned.

        Parameters:
        - column (str): The name of the column on which to execute the aggregate function.
        - func (str): The type of aggregate function to execute. Supported functions include "COUNT", "SUM", "MIN", "MAX", "AVG", etc.
        - condition (str): Optional parameter to filter the rows before executing the aggregate function. If not provided, all rows in the table are included in the calculation.

        Returns:
        - value: The result of the aggregate function.

        Example Usage:
        ```python
        result = obj._single_func('quantity', 'SUM', 'product_id = 12345')
        print(result)
        ```
        ```python
        result = obj._single_func('price', 'AVG')
        print(result)
        ```

        ```python
        result = obj._single_func('name', 'COUNT', 'category = "Books"')
        print(result)
        ```
        ```python
        result = obj._single_func('quantity', 'MIN')
        print(result)
        ```

        Note:
        - The method requires an active connection to the database.
        - The column name and function type should be passed as strings.
        - The condition parameter is optional, and if not provided, the aggregate function will be applied to all rows in the table.
        - The result of the aggregate function is returned as a single value.
        """
        with self.engine.connect() as con:
            if condition.strip() == '':
                sql = 'SELECT {}({}) FROM {}'.format(func, column, self.table_name)
            else:
                sql = 'SELECT {}({}) FROM {} WHERE {}'.format(func, column, self.table_name, condition)
            rs = con.execute(sql)
            for i in rs:
                return i[0]

    def select(self, select: str, condition: str = ""):
        with self.engine.connect() as con:
            if condition.strip() == '':
                sql = 'SELECT {} FROM {}'.format(select, self.table_name)
            else:
                sql = 'SELECT {} FROM {} WHERE {}'.format(select, self.table_name, condition)
            rs = con.execute(sql)
            for i in rs:
                return i[0]

    def default_order_by(self) -> str:
        """
            默认的查询排序
        """
        return ''

    def default_limit(self) -> str:
        """
         每次取数的limit
        """
        return ''

    def default_time_range(self) -> ():
        return None

    def filter_process(self, filter_criterion, filter_by):
        return filter_criterion, filter_by

    def _get_time_criterion_filter(self, **kwargs):
        time_range_query = self.default_time_range()
        criterion = None
        if time_range_query:
            start = kwargs.get(time_range_query[0])
            end = kwargs.get(time_range_query[1])
            time_field = time_range_query[2]
            if start and end:
                criterion = and_(time_field >= start, time_field <= end)
            elif end:
                criterion = time_field <= end
            elif start:
                criterion = time_field >= start
        return criterion

    def _get_query_fields(self, fields=''):
        if fields != '':
            return list(getattr(self.entities, f.strip()) for f in fields.split(',') if f.strip() in self.entity_fields)
        return None

    def _get_query_limit(self, **kwargs):
        limit = 10000000  # 默认200000000条 避免导致数据库压力过大
        if kwargs.get('limit') and str(kwargs.get('limit')).isnumeric():
            input_limit = int(kwargs.get('limit'))
            if input_limit < limit:
                return input_limit
            else:
                return limit
        elif self.default_limit() != "":
            default_limit = int(self.default_limit())
            if default_limit < limit:
                return default_limit
            else:
                return limit

        return None

    def _get_query_offset(self, **kwargs):
        if kwargs.get('offset') and str(kwargs.get('offset')).isnumeric():
            return kwargs.get('offset')
        return None

    def _get_order_by(self, **kwargs):
        if kwargs.get('order_by'):
            return kwargs.get('order_by')
        order_by = self.default_order_by()
        if self.time_order:
            time_range = self.default_time_range()
            if time_range:
                time_column = time_range[2]
                if order_by:
                    tokens = order_by.split(",")
                    n_order_by = []
                    for t in tokens:
                        if t.startswith(time_column.name):
                            n_order_by.append(f"{time_column.name} {self.time_order}")
                        else:
                            n_order_by.append(t)
                    return ",".join(n_order_by)
                else:
                    return f"{time_column.name} {self.time_order}"
        else:
            return order_by

    def query(self, fields='', **kwargs):
        filter_criterion = self._get_time_criterion_filter(**kwargs)
        filter_by = {
            key: kwargs[key]
            for key in kwargs.keys()
            if (key in self.entity_fields) and key is not None and kwargs[key] != ''
        }
        filter_criterion, filter_by = self.filter_process(filter_criterion, filter_by)
        order_by = self._get_order_by(**kwargs)
        limit = self._get_query_limit(**kwargs)
        offset = self._get_query_offset(**kwargs)
        df = self.direct_query(fields, filter_criterion, filter_by, order_by, limit, offset)
        if self.column_mapping is not None:
            df.rename(columns=self.column_mapping, inplace=True)
        return df

    def direct_query(self, fields: str = None, filter_criterion=None, filter_by: dict = None,
                     order_by: str = None, limit: int = None, offset: int = None):
        start = time.time()
        query = None
        if filter_criterion is not None:
            query = self.session_factory().query(self.entities).filter(filter_criterion)
        else:
            query = self.session_factory().query(self.entities)
        if filter_by:
            if query:
                query = query.filter_by(**filter_by)
            else:
                query = self.session_factory().query(self.entities).filter_by(**filter_by)
        if fields:
            query_fields = self._get_query_fields(fields)
            query = query.with_entities(*query_fields)
        if order_by:
            query = query.order_by(text(order_by))
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        df = pd.read_sql(query.statement, query.session.bind)
        df = df.drop(['id'], axis=1, errors='ignore')
        self.logger.debug(
            "Finished {} query, it costs {}s".format(self.entities.__name__, time.time() - start))
        return df

    def sql(self, sql):
        start = time.time()
        query = self.session_factory().query(self.entities)
        sql = sql.format(table=self.table_name).strip()
        if sql.split(" ")[0].upper().startswith("SELECT"):
            df = pd.read_sql(sql, query.session.bind)
            df = df.drop(['id'], axis=1, errors='ignore')
            self.logger.debug(
                "Finished {} query, sql is {} it costs {}s".format(self.entities.__name__, sql, time.time() - start))
            if self.column_mapping is not None:
                df.rename(columns=self.column_mapping, inplace=True)
            return df
        return pd.DataFrame()

    def meta(self):
        return {"table_name": self.table_name, "columns": self.columns_meta(),
                "default_order_by": self.default_order_by(),
                "default_limit": self.default_limit()}

    def uniq_check(self, columns):
        group = ','.join(columns)
        sql = "select " + group + " from {table} group by " + group + "  have count(*)>1"
        return self.sql(sql)


class Records:
    def __init__(self, fields=None, items=None):
        self.fields = fields
        if items is None:
            self.items = []
        else:
            self.items = items

    def data_frame(self):
        return pd.DataFrame(self.items, columns=self.fields)

    def size(self):
        if self.items is None:
            return 0
        else:
            return len(self.items)

    def append(self, records):
        if records is not None:
            if isinstance(records, DataFrame):
                if self.fields is None:
                    self.fields = records.columns.tolist()
                if self.size() == 0:
                    self.items = records.values
                else:
                    self.items = np.concatenate((self.items, records.values))
            else:
                if self.fields is None:
                    self.fields = records.fields
                self.items = self.items + records.items

    def __str__(self):
        return self.data_frame().__str__()


class BatchWriter:

    def __init__(self, engine, table: str, schema, database_dir=None):
        self.writer = None
        self.engine = engine
        self.table = table
        self.shared_resource_lock = threading.Lock()
        self.logger = logging.getLogger('tutake.dao.writer.{}'.format(table))
        self.schema = schema
        self.database_dir = database_dir
        self.parquet_file = None
        self.max_id = 0

    def _init_writer(self):
        if self.writer is None:
            self.parquet_file = Path(self.database_dir, f'{self.table}-{time.time()}.parquet')
            self.writer = pq.ParquetWriter(self.parquet_file, self.schema)
        return self.writer

    def start(self):
        if self.writer is None:
            self._init_writer()
            conn = self.engine.connect()
            result = conn.execute(f"""Select max(id) from {self.table}""").fetchone()
            if result is not None and result[0] is not None:
                self.max_id = int(result[0])

    def rollback(self):
        if self.writer:
            self.writer = None
        try:
            os.remove(self.parquet_file)
        except FileNotFoundError:
            return

    def commit(self):
        try:
            self.writer.close()
            self.shared_resource_lock.acquire()
            conn = self.engine.connect()
            conn.execute(f"""INSERT INTO {self.table} SELECT * FROM read_parquet('{self.parquet_file}')""")
            conn.close()
            self.shared_resource_lock.release()
            self.writer = None
        finally:
            try:
                os.remove(self.parquet_file)
            except FileNotFoundError:
                return

    def add_records(self, records):
        if isinstance(records, Records):
            data = records.data_frame()
        elif isinstance(records, DataFrame):
            data = records
        else:
            return

        self.start()
        data['id'] = range(self.max_id, self.max_id + len(data))
        data = data.reindex(columns=['id'] + list(data.columns[:-1]))
        table = pa.Table.from_pandas(df=data, schema=self.schema)
        self.writer.write_table(table)
        self.max_id = self.max_id + len(data)

    def flush(self):
        conn = self.engine.connect()
        conn.execute("FORCE CHECKPOINT;")
        conn.close()

    def close(self):
        self.max_id = 0
        if self.writer:
            self.writer.close()
            self.writer = None
        try:
            os.remove(self.parquet_file)
        except FileNotFoundError:
            return

    def count(self, condition: str = ""):
        return self._single_func('id', 'count', condition)

    def max(self, column: str, condition: str = ""):
        return self._single_func(column, 'max', condition)

    def min(self, column: str, condition: str = ""):
        return self._single_func(column, 'min', condition)

    def _single_func(self, column: str, func: str, condition: str = ""):
        if condition.strip() == '':
            sql = f"SELECT {func}({column}) FROM '{self.parquet_file}'"
        else:
            sql = f"SELECT {func}({column}) FROM '{self.parquet_file}' WHERE {condition}"
        self.writer.close()
        rs = duckdb.query(sql).fetchall()
        for i in rs:
            return i[0]
