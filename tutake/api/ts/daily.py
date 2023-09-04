"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare daily接口
交易日每天15点～16点之间入库。本接口是未复权行情，停牌期间不提供数据,获取股票行情数据，或通过通用行情接口获取数据，包含了前后复权数据,全部历史，交易日每日15点～17点之间更新
数据接口-沪深股票-行情数据-日线行情  https://tushare.pro/document/2?doc_id=27

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.daily_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareDaily(Base):
    __tablename__ = "tushare_daily"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='股票代码')
    trade_date = Column(String, index=True, comment='交易日期')
    open = Column(Float, comment='开盘价')
    high = Column(Float, comment='最高价')
    low = Column(Float, comment='最低价')
    close = Column(Float, comment='收盘价')
    pre_close = Column(Float, comment='昨收价')
    change = Column(Float, comment='涨跌额')
    pct_chg = Column(Float, comment='涨跌幅')
    vol = Column(Float, comment='成交量')
    amount = Column(Float, comment='成交额')


class Daily(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_daily"
        self.database = 'tushare_daily.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareDaily.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'offset', 'limit']
        entity_fields = [
            "ts_code", "trade_date", "open", "high", "low", "close", "pre_close", "change", "pct_chg", "vol", "amount"
        ]
        TushareDAO.__init__(self, self.engine, session_factory, TushareDaily, self.database, self.table_name,
                            query_fields, entity_fields, config)
        DataProcess.__init__(self, "daily", config)
        TuShareBase.__init__(self, "daily", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "股票代码"
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "open",
            "type": "Float",
            "comment": "开盘价"
        }, {
            "name": "high",
            "type": "Float",
            "comment": "最高价"
        }, {
            "name": "low",
            "type": "Float",
            "comment": "最低价"
        }, {
            "name": "close",
            "type": "Float",
            "comment": "收盘价"
        }, {
            "name": "pre_close",
            "type": "Float",
            "comment": "昨收价"
        }, {
            "name": "change",
            "type": "Float",
            "comment": "涨跌额"
        }, {
            "name": "pct_chg",
            "type": "Float",
            "comment": "涨跌幅"
        }, {
            "name": "vol",
            "type": "Float",
            "comment": "成交量"
        }, {
            "name": "amount",
            "type": "Float",
            "comment": "成交额"
        }]

    def daily(self, fields='', **kwargs):
        """
        交易日每天15点～16点之间入库。本接口是未复权行情，停牌期间不提供数据,获取股票行情数据，或通过通用行情接口获取数据，包含了前后复权数据,全部历史，交易日每日15点～17点之间更新
        | Arguments:
        | ts_code(str):   股票代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | offset(str):   开始行数
        | limit(str):   最大行数
        
        :return: DataFrame
         ts_code(str)  股票代码 Y
         trade_date(str)  交易日期 Y
         open(float)  开盘价 Y
         high(float)  最高价 Y
         low(float)  最低价 Y
         close(float)  收盘价 Y
         pre_close(float)  昨收价 Y
         change(float)  涨跌额 Y
         pct_chg(float)  涨跌幅 Y
         vol(float)  成交量 Y
         amount(float)  成交额 Y
        
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
        init_args = {"ts_code": "", "trade_date": "", "start_date": "", "end_date": "", "offset": "", "limit": ""}
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
                self.logger.debug("Invoke pro.daily with args: {}".format(kwargs))
                return self.tushare_query('daily', fields=self.entity_fields, **kwargs)
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


setattr(Daily, 'default_limit', default_limit_ext)
setattr(Daily, 'default_cron_express', default_cron_express_ext)
setattr(Daily, 'default_order_by', default_order_by_ext)
setattr(Daily, 'prepare', prepare_ext)
setattr(Daily, 'query_parameters', query_parameters_ext)
setattr(Daily, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.daily())

    api = Daily(config)
    print(api.process())    # 同步增量数据
    print(api.daily())    # 数据查询接口
