"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_daily接口
获取场内基金日线行情，类似股票日行情
数据接口-公募基金-基金行情  https://tushare.pro/document/2?doc_id=127

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.process import DataProcess
from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.fund_daily_ext import *
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_fund_daily.db'),
                       connect_args={'check_same_thread': False})
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()


class TushareFundDaily(Base):
    __tablename__ = "tushare_fund_daily"
    id = Column(Integer, primary_key=True, autoincrement=True)
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


TushareFundDaily.__table__.create(bind=engine, checkfirst=True)


class FundDaily(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = ['trade_date', 'start_date', 'end_date', 'ts_code', 'limit', 'offset']
        entity_fields = [
            "ts_code", "trade_date", "pre_close", "open", "high", "low", "close", "change", "pct_chg", "vol", "amount"
        ]
        BaseDao.__init__(self, engine, session_factory, TushareFundDaily, 'tushare_fund_daily', query_fields,
                         entity_fields)
        DataProcess.__init__(self, "fund_daily")
        TuShareBase.__init__(self, "fund_daily")
        self.dao = DAO()

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
         ts_code(str)  TS代码
         trade_date(str)  交易日期
         pre_close(float)  昨收盘价(元)
         open(float)  开盘价(元)
         high(float)  最高价(元)
         low(float)  最低价(元)
         close(float)  收盘价(元)
         change(float)  涨跌(元)
         pct_chg(float)  涨跌幅(%)
         vol(float)  成交量(手)
         amount(float)  成交金额(千元)
        
        """
        return super().query(fields, **kwargs)

    def process(self, process_type: ProcessType):
        """
        同步历史数据
        :return:
        """
        return super()._process(process_type, self.fetch_and_append)

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
            kwargs['offset'] = str(offset_val)
            self.logger.debug("Invoke pro.fund_daily with args: {}".format(kwargs))
            res = self.tushare_query('fund_daily', fields=self.entity_fields, **kwargs)
            res.to_sql('tushare_fund_daily', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(FundDaily, 'default_limit', default_limit_ext)
setattr(FundDaily, 'default_cron_express', default_cron_express_ext)
setattr(FundDaily, 'default_order_by', default_order_by_ext)
setattr(FundDaily, 'prepare', prepare_ext)
setattr(FundDaily, 'tushare_parameters', tushare_parameters_ext)
setattr(FundDaily, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    pro = ts.pro_api(tutake_config.get_tushare_token())
    print(pro.fund_daily(trade_date='20221117'))

    api = FundDaily()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    api.process(ProcessType.INCREASE)    # 同步增量数据
    print(api.fund_daily(trade_date='20221117'))    # 数据查询接口
