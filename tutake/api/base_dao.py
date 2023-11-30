import logging
import os
import sqlite3
import tempfile
import threading
import time
from datetime import datetime
from operator import and_
from sqlite3 import Connection

import numpy as np
import pandas as pd
import sqlalchemy
from pandas import DataFrame
from pathlib import Path
from sqlalchemy import text, Column, Integer, PickleType, String, Boolean, DateTime
from sqlalchemy.orm import load_only, declarative_base, sessionmaker, DeclarativeMeta
import pyarrow as pa
import pyarrow.parquet as pq
from typing import Type

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


class DataChecker:

    def __init__(self, engine, name, session_factory, config):
        self.config = config
        self.engine = engine
        self.name = name
        self.session_factory: sessionmaker = session_factory
        TutakeCheckerPoint.__table__.create(bind=self.engine, checkfirst=True)

    def check_point(self) -> (dict, bool):
        session = self.session_factory()
        point = session.query(TutakeCheckerPoint).filter_by(table_name=self.name).order_by(
            TutakeCheckerPoint.update_time.desc()).first()
        if point is None:
            return None, True
        else:
            return point.points, point.error

    def _save(self, error: False, **points):
        session = self.session_factory()
        model = session.query(TutakeCheckerPoint).filter_by(table_name=self.name).first()
        if model:
            model.points = points
            model.update_time = datetime.now()
            session.merge(model)
        else:
            model = TutakeCheckerPoint(table_name=self.name, points=points, error=error, update_time=datetime.now())
            session.add(model)  # 执行插入操作
        session.commit()

    def save_point(self, **points):
        self._save(False, **points)

    def error_point(self, **points):
        self._save(True, **points)


class BaseDao(object):

    def __init__(self, engine, session_factory: sessionmaker, entities, database, table_name, query_fields,
                 entity_fields, column_mapping, config: TutakeConfig):
        self.engine = engine
        self.entities = entities
        self.database = database
        self.session_factory: sessionmaker = session_factory
        self.table_name = table_name
        self.query_fields = query_fields
        self.entity_fields = entity_fields
        self.column_mapping = column_mapping
        self.logger = logging.getLogger('tutake.dao.base.{}'.format(table_name))
        self.time_order = config.get_config("tutake.query.time_order")
        self.checker = DataChecker(self.engine, table_name, session_factory, config)

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

    def columns_meta(self):
        pass

    def delete_all(self):
        self.logger.warning("Delete all data of {}".format(self.table_name))
        session = self.session_factory()
        session.query(self.entities).delete()
        session.commit()

    def delete_by(self, **kwargs):
        self.logger.warning("Delete data from {} by {}".format(self.table_name, kwargs))
        session = self.session_factory()
        session.query(self.entities).filter_by(**kwargs).delete()
        session.commit()

    def get_ident(self, ident):
        session = self.session_factory()
        return session.query(self.entities).get(ident)

    def filter(self, **params):
        session = self.session_factory()
        query = session.query(self.entities).filter_by(**params)
        return query.commit()

    def column_data(self, columns: [], *criteria):
        if criteria:
            result = self.session_factory().query(self.entities).filter(*criteria).options(load_only(*columns)).all()
        else:
            result = self.session_factory().query(self.entities).options(load_only(*columns)).all()
        vals = list({key: i.__dict__[key] for key in columns} for i in result)
        return vals

    def max(self, column: str, condition: str = ""):
        return self._single_func(column, 'max', condition)

    def min(self, column: str, condition: str = ""):
        return self._single_func(column, 'min', condition)

    def count(self, condition: str = ""):
        return self._single_func('*', 'count', condition)

    def _single_func(self, column: str, func: str, condition: str = ""):
        with self.engine.connect() as con:
            if condition.strip() == '':
                sql = 'SELECT {}({}) FROM {}'.format(func, column, self.table_name)
            else:
                sql = 'SELECT {}({}) FROM {} WHERE {}'.format(func, column, self.table_name, condition)
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


class BatchWriter:

    def __init__(self, engine, table: str, schema, database_dir):
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
            conn.execute(f"""FORCE CHECKPOINT;""")
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
        data['id'] = range(self.max_id, self.max_id + len(data))
        data = data.reindex(columns=['id'] + list(data.columns[:-1]))
        table = pa.Table.from_pandas(df=data, schema=self.schema)
        self.writer.write_table(table)
        self.max_id = self.max_id + len(data)

    def close(self):
        self.max_id = 0
        if self.writer:
            self.writer.close()
            self.writer = None
        try:
            os.remove(self.parquet_file)
        except FileNotFoundError:
            return

