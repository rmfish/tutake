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


class ProcessException(BaseException):
    def __init__(self, param: dict, cause: Exception):  # real signature unknown
        super().__init__(param, cause)
        self.param = param
        self.cause = cause


class ProcessPercent(object):
    def __init__(self, total):
        self.total = total
        self.finished = 0

    def finish(self, cnt: int = 1):
        self.finished += cnt

    def percent(self):
        return self.finished / self.total

    def format(self):
        return '{}%'.format('%.2f' % (self.percent() * 100))


if __name__ == '__main__':
    percent = ProcessPercent(7)
    percent.finish()
    print(percent.percent() * 100)
    print(percent.format())

    err = ProcessException({"a": 'a'}, Exception())
    print("{}".format(err.param))
