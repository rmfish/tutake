import logging

from sqlalchemy.orm import load_only

logger = logging.getLogger('dao.base')


class BaseDao:

    def __init__(self, engine, session_factory, entities, table_name):
        self.engine = engine
        self.entities = entities
        self.session_factory = session_factory
        self.table_name = table_name

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
