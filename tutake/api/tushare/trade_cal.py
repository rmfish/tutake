"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare trade_cal接口
获取各大期货交易所交易日历数据，数据开始月1996年1月
数据接口-期货-期货交易日历  https://tushare.pro/document/2?doc_id=137

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.trade_cal_ext import *
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_trade_cal.db'),
                       connect_args={'check_same_thread': False})
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()


class TushareTradeCal(Base):
    __tablename__ = "tushare_trade_cal"
    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange = Column(String, index=True, comment='交易所 SSE上交所 SZSE深交所')
    cal_date = Column(String, index=True, comment='日历日期')
    is_open = Column(String, index=True, comment='是否交易 0休市 1交易')
    pretrade_date = Column(String, comment='上一个交易日')


TushareTradeCal.__table__.create(bind=engine, checkfirst=True)


class TradeCal(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = ['exchange', 'cal_date', 'start_date', 'end_date', 'is_open', 'limit', 'offset']
        entity_fields = ["exchange", "cal_date", "is_open", "pretrade_date"]
        BaseDao.__init__(self, engine, session_factory, TushareTradeCal, 'tushare_trade_cal', query_fields,
                         entity_fields)
        DataProcess.__init__(self, "trade_cal")
        TuShareBase.__init__(self, "trade_cal")
        self.dao = DAO()

    def trade_cal(self, fields='', **kwargs):
        """
        获取各大期货交易所交易日历数据，数据开始月1996年1月
        | Arguments:
        | exchange(str):   交易所 SSE上交所 SZSE深交所
        | cal_date(str):   日历日期
        | start_date(str):   
        | end_date(str):   
        | is_open(str):   是否交易 0休市 1交易
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         exchange(str)  交易所 SSE上交所 SZSE深交所
         cal_date(str)  日历日期
         is_open(str)  是否交易 0休市 1交易
         pretrade_date(str)  上一个交易日
        
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
        init_args = {
            "exchange": "",
            "cal_date": "",
            "start_date": "",
            "end_date": "",
            "is_open": "",
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
                self.logger.debug("Invoke pro.trade_cal with args: {}".format(kwargs))
                res = self.tushare_query('trade_cal', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_trade_cal', con=engine, if_exists='append', index=False, index_label=['ts_code'])
                return res
            except Exception as err:
                raise ProcessException(kwargs, err)

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(TradeCal, 'default_limit', default_limit_ext)
setattr(TradeCal, 'default_cron_express', default_cron_express_ext)
setattr(TradeCal, 'default_order_by', default_order_by_ext)
setattr(TradeCal, 'prepare', prepare_ext)
setattr(TradeCal, 'tushare_parameters', tushare_parameters_ext)
setattr(TradeCal, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    pro = ts.pro_api(tutake_config.get_tushare_token())
    print(pro.trade_cal())

    api = TradeCal()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    api.process(ProcessType.INCREASE)    # 同步增量数据
    print(api.trade_cal())    # 数据查询接口
