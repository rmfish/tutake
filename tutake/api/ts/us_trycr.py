"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare us_trycr接口
获取美国国债实际收益率曲线利率数据
数据接口-宏观经济-国际宏观-美国利率-国债实际收益率曲线利率  https://tushare.pro/document/2?doc_id=220

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.us_trycr_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareUsTrycr(Base):
    __tablename__ = "tushare_us_trycr"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, index=True, comment='日期')
    y5 = Column(Float, comment='5年期')
    y7 = Column(Float, comment='7年期')
    y10 = Column(Float, comment='10年期')
    y20 = Column(Float, comment='20年期')
    y30 = Column(Float, comment='30年期')


class UsTrycr(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_us_trycr"
        self.database = 'tushare_macroeconomic.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareUsTrycr.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['date', 'start_date', 'end_date', 'fields', 'limit', 'offset']
        entity_fields = ["date", "y5", "y7", "y10", "y20", "y30"]
        TushareDAO.__init__(self, self.engine, session_factory, TushareUsTrycr, self.database, self.table_name,
                            query_fields, entity_fields, config)
        DataProcess.__init__(self, "us_trycr", config)
        TuShareBase.__init__(self, "us_trycr", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "date",
            "type": "String",
            "comment": "日期"
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

    def us_trycr(self, fields='', **kwargs):
        """
        获取美国国债实际收益率曲线利率数据
        | Arguments:
        | date(str):   日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | fields(str):   指定字段
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         date(str)  日期 Y
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
        return super()._process(self.fetch_and_append, BatchWriter(self.engine, self.table_name), **kwargs)

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
                self.logger.debug("Invoke pro.us_trycr with args: {}".format(kwargs))
                return self.tushare_query('us_trycr', fields=self.entity_fields, **kwargs)
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
        return res


setattr(UsTrycr, 'default_limit', default_limit_ext)
setattr(UsTrycr, 'default_cron_express', default_cron_express_ext)
setattr(UsTrycr, 'default_order_by', default_order_by_ext)
setattr(UsTrycr, 'prepare', prepare_ext)
setattr(UsTrycr, 'query_parameters', query_parameters_ext)
setattr(UsTrycr, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.us_trycr())

    api = UsTrycr(config)
    print(api.process())    # 同步增量数据
    print(api.us_trycr())    # 数据查询接口
