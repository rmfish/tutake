"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare trade_cal接口
数据接口-沪深股票-基础数据-交易日历  https://tushare.pro/document/2?doc_id=26

@author: rmfish
"""

import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.trade_cal_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (config['database']['driver_url'], 'tushare_basic_data.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.trade_cal')


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
        BaseDao.__init__(self, engine, session_factory, TushareTradeCal, 'tushare_trade_cal')
        TuShareBase.__init__(self)
        self.dao = DAO()
        self.query_fields = [
            n for n in [
                'exchange',
                'cal_date',
                'start_date',
                'end_date',
                'is_open',
                'limit',
                'offset',
            ] if n not in ['limit', 'offset']
        ]
        self.entity_fields = ["exchange", "cal_date", "is_open", "pretrade_date"]

    def trade_cal(self, fields='', **kwargs):
        """
        
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
        params = {
            key: kwargs[key]
            for key in kwargs.keys()
            if key in self.query_fields and key is not None and kwargs[key] != ''
        }
        query = session_factory().query(TushareTradeCal).filter_by(**params)
        if fields != '':
            entities = (
                getattr(TushareTradeCal, f.strip()) for f in fields.split(',') if f.strip() in self.entity_fields)
            query = query.with_entities(*entities)

        input_limit = 10000    # 默认10000条 避免导致数据库压力过大
        if kwargs.get('limit') and str(kwargs.get('limit')).isnumeric():
            input_limit = int(kwargs.get('limit'))
            query = query.limit(input_limit)
        if "" != "":
            default_limit = int("")
            if default_limit < input_limit:
                query = query.limit(default_limit)
        if kwargs.get('offset') and str(kwargs.get('offset')).isnumeric():
            query = query.offset(int(kwargs.get('offset')))
        df = pd.read_sql(query.statement, query.session.bind)
        return df.drop(['id'], axis=1, errors='ignore')

    def prepare(self, process_type: ProcessType):
        """
        同步历史数据准备工作
        """

    def tushare_parameters(self, process_type: ProcessType):
        """
        同步历史数据调用的参数
        :return: list(dict)
        """
        return [{}]

    def param_loop_process(self, process_type: ProcessType, **params):
        """
        每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
        """
        return params

    def process(self, process_type: ProcessType):
        """
        同步历史数据
        :return:
        """
        self.prepare(process_type)
        params = self.tushare_parameters(process_type)
        logger.debug("Process tushare params is {}".format(params))
        if params:
            for param in params:
                new_param = self.param_loop_process(process_type, **param)
                if new_param is None:
                    logger.debug("Skip exec param: {}".format(param))
                    continue
                try:
                    cnt = self.fetch_and_append(process_type, **new_param)
                    logger.debug("Fetch and append {} data, cnt is {}".format("daily", cnt))
                except Exception as err:
                    if err.args[0].startswith("抱歉，您没有访问该接口的权限") or err.args[0].startswith("抱歉，您每天最多访问该接口"):
                        logger.error("Throw exception with param: {} err:{}".format(new_param, err))
                        return
                    else:
                        logger.error("Execute fetch_and_append throw exp. {}".format(err))
                        continue

    def fetch_and_append(self, process_type: ProcessType, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        if len(kwargs.keys()) == 0:
            kwargs = {
                "exchange": "",
                "cal_date": "",
                "start_date": "",
                "end_date": "",
                "is_open": "",
                "limit": "",
                "offset": ""
            }
        # 初始化offset和limit
        if not kwargs.get("limit"):
            kwargs['limit'] = ""
        init_offset = 0
        offset = 0
        if kwargs.get('offset'):
            offset = int(kwargs['offset'])
            init_offset = offset

        kwargs = {
            key: kwargs[key] for key in kwargs.keys() & list([
                'exchange',
                'cal_date',
                'start_date',
                'end_date',
                'is_open',
                'limit',
                'offset',
            ])
        }

        @sleep(timeout=5, time_append=30, retry=20, match="^抱歉，您每分钟最多访问该接口")
        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            logger.debug("Invoke pro.trade_cal with args: {}".format(kwargs))
            res = pro.trade_cal(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_trade_cal', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        pro = self.tushare_api()
        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(TradeCal, 'prepare', prepare_ext)
setattr(TradeCal, 'tushare_parameters', tushare_parameters_ext)
setattr(TradeCal, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)    # 显示列数
    pd.set_option('display.width', 1000)
    logger.setLevel(logging.DEBUG)
    api = TradeCal()
    api.process(ProcessType.HISTORY)    # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.trade_cal())    # 数据查询接口
