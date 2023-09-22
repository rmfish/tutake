"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare eco_cal接口
获取全球财经日历、包括经济事件数据更新
数据接口-债券-全球财经事件  https://tushare.pro/document/2?doc_id=233

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.eco_cal_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareEcoCal(Base):
    __tablename__ = "tushare_eco_cal"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, index=True, comment='日期')
    time = Column(String, comment='时间')
    currency = Column(String, index=True, comment='货币代码')
    country = Column(String, index=True, comment='国家')
    event = Column(String, index=True, comment='经济事件')
    value = Column(String, comment='今值')
    pre_value = Column(String, comment='前值')
    fore_value = Column(String, comment='预测值')


class EcoCal(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_eco_cal"
        self.database = 'tushare_macroeconomic.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareEcoCal.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['date', 'start_date', 'end_date', 'currency', 'country', 'event', 'is_new', 'limit', 'offset']
        self.tushare_fields = ["date", "time", "currency", "country", "event", "value", "pre_value", "fore_value"]
        entity_fields = ["date", "time", "currency", "country", "event", "value", "pre_value", "fore_value"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareEcoCal, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "eco_cal", config)
        TuShareBase.__init__(self, "eco_cal", config, 2000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "date",
            "type": "String",
            "comment": "日期"
        }, {
            "name": "time",
            "type": "String",
            "comment": "时间"
        }, {
            "name": "currency",
            "type": "String",
            "comment": "货币代码"
        }, {
            "name": "country",
            "type": "String",
            "comment": "国家"
        }, {
            "name": "event",
            "type": "String",
            "comment": "经济事件"
        }, {
            "name": "value",
            "type": "String",
            "comment": "今值"
        }, {
            "name": "pre_value",
            "type": "String",
            "comment": "前值"
        }, {
            "name": "fore_value",
            "type": "String",
            "comment": "预测值"
        }]

    def eco_cal(self, fields='', **kwargs):
        """
        获取全球财经日历、包括经济事件数据更新
        | Arguments:
        | date(str):   日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | currency(str):   货币代码
        | country(str):   国家
        | event(str):   事件
        | is_new(str):   是否最新
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         date(str)  日期 Y
         time(str)  时间 Y
         currency(str)  货币代码 Y
         country(str)  国家 Y
         event(str)  经济事件 Y
         value(str)  今值 Y
         pre_value(str)  前值 Y
         fore_value(str)  预测值 Y
        
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
        init_args = {
            "date": "",
            "start_date": "",
            "end_date": "",
            "currency": "",
            "country": "",
            "event": "",
            "is_new": "",
            "limit": "",
            "offset": ""
        }
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
                self.logger.debug("Invoke pro.eco_cal with args: {}".format(kwargs))
                return self.tushare_query('eco_cal', fields=self.tushare_fields, **kwargs)
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


setattr(EcoCal, 'default_limit', default_limit_ext)
setattr(EcoCal, 'default_cron_express', default_cron_express_ext)
setattr(EcoCal, 'default_order_by', default_order_by_ext)
setattr(EcoCal, 'prepare', prepare_ext)
setattr(EcoCal, 'query_parameters', query_parameters_ext)
setattr(EcoCal, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.eco_cal())

    api = EcoCal(config)
    print(api.process())    # 同步增量数据
    print(api.eco_cal())    # 数据查询接口
