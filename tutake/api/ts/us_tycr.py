"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare us_tycr接口
美国国债每日收益率曲线
数据接口-宏观经济-国际宏观-美国利率-国债收益率曲线利率  https://tushare.pro/document/2?doc_id=219

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.us_tycr_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareUsTycr(TutakeTableBase):
    __tablename__ = "tushare_us_tycr"
    date = Column(String, index=True, comment='日期')
    m1 = Column(Float, comment='1月期')
    m2 = Column(Float, comment='2月期')
    m3 = Column(Float, comment='3月期')
    m6 = Column(Float, comment='6月期')
    y1 = Column(Float, comment='1年期')
    y2 = Column(Float, comment='2年期')
    y3 = Column(Float, comment='3年期')
    y5 = Column(Float, comment='5年期')
    y7 = Column(Float, comment='7年期')
    y10 = Column(Float, comment='10年期')
    y20 = Column(Float, comment='20年期')
    y30 = Column(Float, comment='30年期')


class UsTycr(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_us_tycr"
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
        TushareUsTycr.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareUsTycr)

        query_fields = ['date', 'start_date', 'end_date', 'fields', 'limit', 'offset']
        self.tushare_fields = ["date", "m1", "m2", "m3", "m6", "y1", "y2", "y3", "y5", "y7", "y10", "y20", "y30"]
        entity_fields = ["date", "m1", "m2", "m3", "m6", "y1", "y2", "y3", "y5", "y7", "y10", "y20", "y30"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareUsTycr, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "us_tycr", config)
        TuShareBase.__init__(self, "us_tycr", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "date",
            "type": "String",
            "comment": "日期"
        }, {
            "name": "m1",
            "type": "Float",
            "comment": "1月期"
        }, {
            "name": "m2",
            "type": "Float",
            "comment": "2月期"
        }, {
            "name": "m3",
            "type": "Float",
            "comment": "3月期"
        }, {
            "name": "m6",
            "type": "Float",
            "comment": "6月期"
        }, {
            "name": "y1",
            "type": "Float",
            "comment": "1年期"
        }, {
            "name": "y2",
            "type": "Float",
            "comment": "2年期"
        }, {
            "name": "y3",
            "type": "Float",
            "comment": "3年期"
        }, {
            "name": "y5",
            "type": "Float",
            "comment": "5年期"
        }, {
            "name": "y7",
            "type": "Float",
            "comment": "7年期"
        }, {
            "name": "y10",
            "type": "Float",
            "comment": "10年期"
        }, {
            "name": "y20",
            "type": "Float",
            "comment": "20年期"
        }, {
            "name": "y30",
            "type": "Float",
            "comment": "30年期"
        }]

    def us_tycr(self, fields='', **kwargs):
        """
        美国国债每日收益率曲线
        | Arguments:
        | date(str):   日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | fields(str):   指定字段
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         date(str)  日期 Y
         m1(float)  1月期 Y
         m2(float)  2月期 Y
         m3(float)  3月期 Y
         m6(float)  6月期 Y
         y1(float)  1年期 Y
         y2(float)  2年期 Y
         y3(float)  3年期 Y
         y5(float)  5年期 Y
         y7(float)  7年期 Y
         y10(float)  10年期 Y
         y20(float)  20年期 Y
         y30(float)  30年期 Y
        
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
        init_args = {"date": "", "start_date": "", "end_date": "", "fields": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.us_tycr with args: {}".format(kwargs))
                return self.tushare_query('us_tycr', fields=self.tushare_fields, **kwargs)
            except Exception as err:
                raise ProcessException(kwargs, err)

        res = fetch_save(offset)
        size = res.size()
        offset += size
        while kwargs['limit'] != "" and size == int(kwargs['limit']):
            result = fetch_save(offset)
            size = result.size()
            offset += size
            res.append(result)
        res.fields = self.entity_fields
        return res


setattr(UsTycr, 'default_limit', default_limit_ext)
setattr(UsTycr, 'default_cron_express', default_cron_express_ext)
setattr(UsTycr, 'default_order_by', default_order_by_ext)
setattr(UsTycr, 'prepare', prepare_ext)
setattr(UsTycr, 'query_parameters', query_parameters_ext)
setattr(UsTycr, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.us_tycr())

    api = UsTycr(config)
    print(api.process())    # 同步增量数据
    print(api.us_tycr())    # 数据查询接口
