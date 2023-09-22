"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fx_daily接口
外汇日线行情
数据接口-外汇-外汇日线行情  https://tushare.pro/document/2?doc_id=179

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.fx_daily_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareFxDaily(Base):
    __tablename__ = "tushare_fx_daily"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='外汇代码')
    trade_date = Column(String, index=True, comment='交易日期')
    bid_open = Column(Float, comment='买入开盘价')
    bid_close = Column(Float, comment='买入收盘价')
    bid_high = Column(Float, comment='买入最高价')
    bid_low = Column(Float, comment='买入最低价')
    ask_open = Column(Float, comment='卖出开盘价')
    ask_close = Column(Float, comment='卖出收盘价')
    ask_high = Column(Float, comment='卖出最高价')
    ask_low = Column(Float, comment='卖出最低价')
    tick_qty = Column(Integer, comment='报价笔数')
    exchange = Column(String, index=True, comment='交易商')


class FxDaily(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_fx_daily"
        self.database = 'tushare_fx.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareFxDaily.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'exchange', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "trade_date", "bid_open", "bid_close", "bid_high", "bid_low", "ask_open", "ask_close",
            "ask_high", "ask_low", "tick_qty", "exchange"
        ]
        entity_fields = [
            "ts_code", "trade_date", "bid_open", "bid_close", "bid_high", "bid_low", "ask_open", "ask_close",
            "ask_high", "ask_low", "tick_qty", "exchange"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareFxDaily, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "fx_daily", config)
        TuShareBase.__init__(self, "fx_daily", config, 2000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "外汇代码"
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "bid_open",
            "type": "Float",
            "comment": "买入开盘价"
        }, {
            "name": "bid_close",
            "type": "Float",
            "comment": "买入收盘价"
        }, {
            "name": "bid_high",
            "type": "Float",
            "comment": "买入最高价"
        }, {
            "name": "bid_low",
            "type": "Float",
            "comment": "买入最低价"
        }, {
            "name": "ask_open",
            "type": "Float",
            "comment": "卖出开盘价"
        }, {
            "name": "ask_close",
            "type": "Float",
            "comment": "卖出收盘价"
        }, {
            "name": "ask_high",
            "type": "Float",
            "comment": "卖出最高价"
        }, {
            "name": "ask_low",
            "type": "Float",
            "comment": "卖出最低价"
        }, {
            "name": "tick_qty",
            "type": "Integer",
            "comment": "报价笔数"
        }, {
            "name": "exchange",
            "type": "String",
            "comment": "交易商"
        }]

    def fx_daily(
            self,
            fields='ts_code,trade_date,bid_open,bid_close,bid_high,bid_low,ask_open,ask_close,ask_high,ask_low,tick_qty',
            **kwargs):
        """
        外汇日线行情
        | Arguments:
        | ts_code(str):   TS代码
        | trade_date(str):   交易日期（GMT）
        | start_date(str):   开始日期（GMT）
        | end_date(str):   结束日期（GMT）
        | exchange(str):   交易商
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  外汇代码 Y
         trade_date(str)  交易日期 Y
         bid_open(float)  买入开盘价 Y
         bid_close(float)  买入收盘价 Y
         bid_high(float)  买入最高价 Y
         bid_low(float)  买入最低价 Y
         ask_open(float)  卖出开盘价 Y
         ask_close(float)  卖出收盘价 Y
         ask_high(float)  卖出最高价 Y
         ask_low(float)  卖出最低价 Y
         tick_qty(int)  报价笔数 Y
         exchange(str)  交易商 N
        
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
                self.logger.debug("Invoke pro.fx_daily with args: {}".format(kwargs))
                return self.tushare_query('fx_daily', fields=self.tushare_fields, **kwargs)
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


setattr(FxDaily, 'default_limit', default_limit_ext)
setattr(FxDaily, 'default_cron_express', default_cron_express_ext)
setattr(FxDaily, 'default_order_by', default_order_by_ext)
setattr(FxDaily, 'prepare', prepare_ext)
setattr(FxDaily, 'query_parameters', query_parameters_ext)
setattr(FxDaily, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fx_daily())

    api = FxDaily(config)
    print(api.process())    # 同步增量数据
    print(api.fx_daily())    # 数据查询接口
