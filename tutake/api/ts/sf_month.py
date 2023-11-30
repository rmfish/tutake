"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare sf_month接口
获取月度社会融资数据
数据接口-宏观经济-国内宏观-金融-货币供应量-社融数据（月）  https://tushare.pro/document/2?doc_id=310

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import sf_month_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareSfMonth(TutakeTableBase):
    __tablename__ = "tushare_sf_month"
    month = Column(String, comment='月份YYYYMM')
    inc_month = Column(Float, comment='社融增量当月值(亿元)')
    inc_cumval = Column(Float, comment='社融增量累计值(亿元)')
    stk_endval = Column(Float, comment='社融增量期末值(亿元)')


class SfMonth(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_sf_month"
        self.database = 'tutake.duckdb'
        self.database_dir = config.get_tutake_data_dir()
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareSfMonth.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareSfMonth)

        query_fields = ['m', 'start_m', 'end_m', 'limit', 'offset']
        self.tushare_fields = ["month", "inc_month", "inc_cumval", "stk_endval"]
        entity_fields = ["month", "inc_month", "inc_cumval", "stk_endval"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareSfMonth, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "sf_month", config)
        TuShareBase.__init__(self, "sf_month", config, 2000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "month",
            "type": "String",
            "comment": "月份YYYYMM"
        }, {
            "name": "inc_month",
            "type": "Float",
            "comment": "社融增量当月值(亿元)"
        }, {
            "name": "inc_cumval",
            "type": "Float",
            "comment": "社融增量累计值(亿元)"
        }, {
            "name": "stk_endval",
            "type": "Float",
            "comment": "社融增量期末值(亿元)"
        }]

    def sf_month(self, fields='', **kwargs):
        """
        获取月度社会融资数据
        | Arguments:
        | m(str):   月度（202001表示，2020年1月）
        | start_m(str):   开始月度
        | end_m(str):   结束月度
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         month(str)  月份YYYYMM Y
         inc_month(float)  社融增量当月值(亿元) Y
         inc_cumval(float)  社融增量累计值(亿元) Y
         stk_endval(float)  社融增量期末值(亿元) Y
        
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append,
                                BatchWriter(self.engine, self.table_name, self.schema, self.database_dir), **kwargs)

    def fetch_and_append(self, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        init_args = {"m": "", "start_m": "", "end_m": "", "limit": "", "offset": ""}
        is_test = kwargs.get('test') or False
        if len(kwargs.keys()) == 0:
            kwargs = init_args
        # 初始化offset和limit
        if not kwargs.get("limit"):
            kwargs['limit'] = self.default_limit()
        init_offset = 0
        offset = 0
        if kwargs.get('offset'):
            offset = int(kwargs['offset'])
            init_offset = offset

        kwargs = {key: kwargs[key] for key in kwargs.keys() & init_args.keys()}

        def fetch_save(offset_val=0):
            try:
                kwargs['offset'] = str(offset_val)
                self.logger.debug("Invoke pro.sf_month with args: {}".format(kwargs))
                return self.tushare_query('sf_month', fields=self.tushare_fields, **kwargs)
            except Exception as err:
                raise ProcessException(kwargs, err)

        res = fetch_save(offset)
        size = res.size()
        offset += size
        res.fields = self.entity_fields
        if is_test:
            return res
        while kwargs['limit'] != "" and size == int(kwargs['limit']):
            result = fetch_save(offset)
            size = result.size()
            offset += size
            res.append(result)
        return res


extends_attr(SfMonth, sf_month_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.sf_month())

    api = SfMonth(config)
    print(api.process())    # 同步增量数据
    print(api.sf_month())    # 数据查询接口
