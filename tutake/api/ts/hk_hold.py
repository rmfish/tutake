"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare hk_hold接口
获取沪深港股通持股明细，数据来源港交所。下个交易日8点更新
数据接口-沪深股票-特色数据-沪深股通持股明细  https://tushare.pro/document/2?doc_id=188

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.hk_hold_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareHkHold(Base):
    __tablename__ = "tushare_hk_hold"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, index=True, comment='原始代码')
    trade_date = Column(String, index=True, comment='交易日期')
    ts_code = Column(String, index=True, comment='TS代码')
    name = Column(String, comment='股票名称')
    vol = Column(Integer, comment='持股数量')
    ratio = Column(Float, comment='持股占比')
    exchange = Column(String, index=True, comment='类型：SH沪股通SZ深港通')


class HkHold(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_hk_hold"
        self.database = 'tushare_stock.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareHkHold.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['code', 'ts_code', 'trade_date', 'start_date', 'end_date', 'exchange', 'limit', 'offset']
        self.tushare_fields = ["code", "trade_date", "ts_code", "name", "vol", "ratio", "exchange"]
        entity_fields = ["code", "trade_date", "ts_code", "name", "vol", "ratio", "exchange"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareHkHold, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "hk_hold", config)
        TuShareBase.__init__(self, "hk_hold", config, 2000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "code",
            "type": "String",
            "comment": "原始代码"
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "ts_code",
            "type": "String",
            "comment": "TS代码"
        }, {
            "name": "name",
            "type": "String",
            "comment": "股票名称"
        }, {
            "name": "vol",
            "type": "Integer",
            "comment": "持股数量"
        }, {
            "name": "ratio",
            "type": "Float",
            "comment": "持股占比"
        }, {
            "name": "exchange",
            "type": "String",
            "comment": "类型：SH沪股通SZ深港通"
        }]

    def hk_hold(self, fields='', **kwargs):
        """
        获取沪深港股通持股明细，数据来源港交所。下个交易日8点更新
        | Arguments:
        | code(str):   交易所代码
        | ts_code(str):   TS股票代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | exchange(str):   SH沪股通SZ深股通
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         code(str)  原始代码 Y
         trade_date(str)  交易日期 Y
         ts_code(str)  TS代码 Y
         name(str)  股票名称 Y
         vol(int)  持股数量 Y
         ratio(float)  持股占比 Y
         exchange(str)  类型：SH沪股通SZ深港通 Y
        
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
            "code": "",
            "ts_code": "",
            "trade_date": "",
            "start_date": "",
            "end_date": "",
            "exchange": "",
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
                self.logger.debug("Invoke pro.hk_hold with args: {}".format(kwargs))
                return self.tushare_query('hk_hold', fields=self.tushare_fields, **kwargs)
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


setattr(HkHold, 'default_limit', default_limit_ext)
setattr(HkHold, 'default_cron_express', default_cron_express_ext)
setattr(HkHold, 'default_order_by', default_order_by_ext)
setattr(HkHold, 'prepare', prepare_ext)
setattr(HkHold, 'query_parameters', query_parameters_ext)
setattr(HkHold, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.hk_hold())

    api = HkHold(config)
    print(api.process())    # 同步增量数据
    print(api.hk_hold())    # 数据查询接口
