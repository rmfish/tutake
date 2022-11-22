import logging
import time
from operator import and_

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import load_only


class BaseDao(object):

    def __init__(self, engine, session_factory, entities, table_name, query_fields, entity_fields):
        self.engine = engine
        self.entities = entities
        self.session_factory = session_factory
        self.table_name = table_name
        self.query_fields = query_fields
        self.entity_fields = entity_fields
        self.logger = logging.getLogger('dao.base.{}'.format(table_name))

    def delete_all(self):
        self.logger.warning("Delete all data of {}".format(self.table_name))
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

        if self.table_name == 'tushare_trade_cal':
            return 'start_date', 'end_date', self.entities.cal_date
        elif self.table_name == 'tushare_new_share':
            return 'start_date', 'end_date', self.entities.ipo_date
        elif self.table_name == 'tushare_balancesheet_vip':
            return 'start_date', 'end_date', self.entities.end_date
        elif self.table_name == 'tushare_fund_nav':
            return 'start_date', 'end_date', self.entities.nav_date
        elif self.table_name in ['tushare_fund_portfolio', 'tushare_stk_managers', 'tushare_namechange',
                                 'tushare_anns', 'tushare_fina_indicator_vip', 'tushare_forecast_vip',
                                 'tushare_express_vip', 'tushare_cashflow_vip', 'tushare_income_vip']:
            return 'start_date', 'end_date', self.entities.ann_date
        elif 'start_date' in self.query_fields:
            return 'start_date', 'end_date', self.entities.trade_date
        elif 'start_month' in self.query_fields:
            return 'start_month', 'end_month', self.entities.month
        return None

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
        limit = 2000000  # 默认20000条 避免导致数据库压力过大
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

    def query(self, fields='', **kwargs):
        start = time.time()
        filter_criterion = self._get_time_criterion_filter(**kwargs)
        params = {
            key: kwargs[key]
            for key in kwargs.keys()
            if key in self.query_fields and key in self.entity_fields and key is not None and kwargs[key] != ''
        }
        query = self.session_factory().query(self.entities).filter_by(**params)
        if filter_criterion is not None:
            query = query.filter(filter_criterion)

        query_fields = self._get_query_fields(fields)
        if query_fields:
            query = query.with_entities(*query_fields)

        ordr_by = self.default_order_by()
        if ordr_by:
            query = query.order_by(text(ordr_by))

        query_limit = self._get_query_limit(**kwargs)
        if query_limit:
            query = query.limit(query_limit)

        query_offset = self._get_query_offset(**kwargs)
        if query_offset:
            query = query.offset(query_offset)

        df = pd.read_sql(query.statement, query.session.bind)
        df = df.drop(['id'], axis=1, errors='ignore')
        self.logger.info(
            "Finished {} query, it costs {}s".format(self.entities.__name__, time.time() - start))
        return df
