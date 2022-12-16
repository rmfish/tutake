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
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base
from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.trade_cal_ext import *
from tutake.api.ts.tushare_dao import TushareDAO
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareTradeCal(Base):
    __tablename__ = "tushare_trade_cal"
    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange = Column(String, index=True, comment='交易所 SSE上交所 SZSE深交所')
    cal_date = Column(String, index=True, comment='日历日期')
    is_open = Column(String, index=True, comment='是否交易 0休市 1交易')
    pretrade_date = Column(String, comment='上一个交易日')


class TradeCal(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine(config.get_data_sqlite_driver_url('tushare_trade_cal.db'),
                                    connect_args={
                                        'check_same_thread': False,
                                        'timeout': config.get_sqlite_timeout()
                                    })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareTradeCal.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['exchange', 'cal_date', 'start_date', 'end_date', 'is_open', 'limit', 'offset']
        entity_fields = ["exchange", "cal_date", "is_open", "pretrade_date"]
        TushareDAO.__init__(self, self.engine, session_factory, TushareTradeCal, 'tushare_trade_cal', query_fields,
                            entity_fields, config)
        DataProcess.__init__(self, "trade_cal", config)
        TuShareBase.__init__(self, "trade_cal", config, 600)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "exchange",
            "type": "String",
            "comment": "交易所 SSE上交所 SZSE深交所"
        }, {
            "name": "cal_date",
            "type": "String",
            "comment": "日历日期"
        }, {
            "name": "is_open",
            "type": "String",
            "comment": "是否交易 0休市 1交易"
        }, {
            "name": "pretrade_date",
            "type": "String",
            "comment": "上一个交易日"
        }]

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

    def process(self):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append)

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
                res.to_sql('tushare_trade_cal',
                           con=self.engine,
                           if_exists='append',
                           index=False,
                           index_label=['ts_code'])
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
setattr(TradeCal, 'query_parameters', query_parameters_ext)
setattr(TradeCal, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.trade_cal())

    api = TradeCal(config)
    api.process()    # 同步增量数据
    print(api.trade_cal())    # 数据查询接口
