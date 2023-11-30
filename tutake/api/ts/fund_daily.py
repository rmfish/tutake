"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_daily接口
获取场内基金日线行情，类似股票日行情
数据接口-公募基金-基金行情  https://tushare.pro/document/2?doc_id=127

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.fund_daily_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareFundDaily(TutakeTableBase):
    __tablename__ = "tushare_fund_daily"
    ts_code = Column(String, index=True, comment='TS代码')
    trade_date = Column(String, index=True, comment='交易日期')
    pre_close = Column(Float, comment='昨收盘价(元)')
    open = Column(Float, comment='开盘价(元)')
    high = Column(Float, comment='最高价(元)')
    low = Column(Float, comment='最低价(元)')
    close = Column(Float, comment='收盘价(元)')
    change = Column(Float, comment='涨跌(元)')
    pct_chg = Column(Float, comment='涨跌幅(%)')
    vol = Column(Float, comment='成交量(手)')
    amount = Column(Float, comment='成交金额(千元)')


class FundDaily(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_fund_daily"
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
        TushareFundDaily.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareFundDaily)

        query_fields = ['trade_date', 'start_date', 'end_date', 'ts_code', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "trade_date", "pre_close", "open", "high", "low", "close", "change", "pct_chg", "vol", "amount"
        ]
        entity_fields = [
            "ts_code", "trade_date", "pre_close", "open", "high", "low", "close", "change", "pct_chg", "vol", "amount"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareFundDaily, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "fund_daily", config)
        TuShareBase.__init__(self, "fund_daily", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS代码"
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "pre_close",
            "type": "Float",
            "comment": "昨收盘价(元)"
        }, {
            "name": "open",
            "type": "Float",
            "comment": "开盘价(元)"
        }, {
            "name": "high",
            "type": "Float",
            "comment": "最高价(元)"
        }, {
            "name": "low",
            "type": "Float",
            "comment": "最低价(元)"
        }, {
            "name": "close",
            "type": "Float",
            "comment": "收盘价(元)"
        }, {
            "name": "change",
            "type": "Float",
            "comment": "涨跌(元)"
        }, {
            "name": "pct_chg",
            "type": "Float",
            "comment": "涨跌幅(%)"
        }, {
            "name": "vol",
            "type": "Float",
            "comment": "成交量(手)"
        }, {
            "name": "amount",
            "type": "Float",
            "comment": "成交金额(千元)"
        }]

    def fund_daily(self, fields='', **kwargs):
        """
        获取场内基金日线行情，类似股票日行情
        | Arguments:
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | ts_code(str):   基金代码
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS代码 Y
         trade_date(str)  交易日期 Y
         pre_close(float)  昨收盘价(元) Y
         open(float)  开盘价(元) Y
         high(float)  最高价(元) Y
         low(float)  最低价(元) Y
         close(float)  收盘价(元) Y
         change(float)  涨跌(元) Y
         pct_chg(float)  涨跌幅(%) Y
         vol(float)  成交量(手) Y
         amount(float)  成交金额(千元) Y
        
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
        init_args = {"trade_date": "", "start_date": "", "end_date": "", "ts_code": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.fund_daily with args: {}".format(kwargs))
                return self.tushare_query('fund_daily', fields=self.tushare_fields, **kwargs)
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


setattr(FundDaily, 'default_limit', default_limit_ext)
setattr(FundDaily, 'default_cron_express', default_cron_express_ext)
setattr(FundDaily, 'default_order_by', default_order_by_ext)
setattr(FundDaily, 'prepare', prepare_ext)
setattr(FundDaily, 'query_parameters', query_parameters_ext)
setattr(FundDaily, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fund_daily(trade_date='20221117'))

    api = FundDaily(config)
    print(api.process())    # 同步增量数据
    print(api.fund_daily(trade_date='20221117'))    # 数据查询接口
