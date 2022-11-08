import logging
from abc import abstractmethod

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import load_only

from tutake.utils.decorator import sleep

logger = logging.getLogger('dao.base')


class BaseDao(object):

    def __init__(self, engine, session_factory, entities, table_name, query_fields, entity_fields):
        self.engine = engine
        self.entities = entities
        self.session_factory = session_factory
        self.table_name = table_name
        self.query_fields = query_fields
        self.entity_fields = entity_fields

    def delete_all(self):
        logger.warning("Delete all data of tushare_stock_basic")
        session = self.session_factory()
        session.query(self.entities).delete()
        session.commit()

    def get_ident(self, ident):
        session = self.session_factory()
        return session.query(self.entities).get(ident)

    def filter(self, **params):
        session = self.session_factory()
        query = session.query(self.entities).filter_by(params)
        return query.commit()

    def column_data(self, columns: [], **params):
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

    def query(self, fields='', **kwargs):
        params = {
            key: kwargs[key]
            for key in kwargs.keys()
            if key in self.query_fields and key is not None and kwargs[key] != ''
        }
        query = self.session_factory().query(self.entities).filter_by(**params)
        if fields != '':
            entities = (
                getattr(self.entities, f.strip()) for f in fields.split(',') if f.strip() in self.entity_fields)
            query = query.with_entities(*entities)
        ordr_by = self.default_order_by()
        if ordr_by:
            query = query.order_by(text(ordr_by))
        limit = 10000  # 默认10000条 避免导致数据库压力过大
        if kwargs.get('limit') and str(kwargs.get('limit')).isnumeric():
            input_limit = int(kwargs.get('limit'))
            if input_limit < limit:
                query = query.limit(input_limit)
            else:
                query = query.limit(limit)
        if self.default_limit() != "":
            default_limit = int(self.default_limit())
            if default_limit < limit:
                query = query.limit(default_limit)
            else:
                query = query.limit(limit)
        if kwargs.get('offset') and str(kwargs.get('offset')).isnumeric():
            query = query.offset(int(kwargs.get('offset')))
        df = pd.read_sql(query.statement, query.session.bind)
        return df.drop(['id'], axis=1, errors='ignore')
