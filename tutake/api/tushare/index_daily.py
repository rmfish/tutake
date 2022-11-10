"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare index_daily接口
数据接口-期货-南华期货指数行情  https://tushare.pro/document/2?doc_id=155

@author: rmfish
"""
import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.index_daily_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_index_daily.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.index_daily')


class TushareIndexDaily(Base):
    __tablename__ = "tushare_index_daily"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='None')
    trade_date = Column(String, index=True, comment='None')
    close = Column(Float, comment='None')
    open = Column(Float, comment='None')
    high = Column(Float, comment='None')
    low = Column(Float, comment='None')
    pre_close = Column(Float, comment='None')
    change = Column(Float, comment='None')
    pct_chg = Column(Float, comment='None')
    vol = Column(Float, comment='None')
    amount = Column(Float, comment='None')


TushareIndexDaily.__table__.create(bind=engine, checkfirst=True)


class IndexDaily(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = [
            'ts_code',
            'trade_date',
            'start_date',
            'end_date',
            'limit',
            'offset',
        ]
        entity_fields = [
            "ts_code", "trade_date", "close", "open", "high", "low", "pre_close", "change", "pct_chg", "vol", "amount"
        ]
        BaseDao.__init__(self, engine, session_factory, TushareIndexDaily, 'tushare_index_daily', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "index_daily")
        self.dao = DAO()

    def index_daily(self, fields='', **kwargs):
        """
        南华期货指数行情
        | Arguments:
        | ts_code(str): required  指数代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  None
         trade_date(datetime)  None
         close(float)  None
         open(float)  None
         high(float)  None
         low(float)  None
         pre_close(float)  None
         change(float)  None
         pct_chg(float)  None
         vol(float)  None
         amount(float)  None
        
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
        init_args = {"ts_code": "", "trade_date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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

        @sleep(timeout=61, time_append=60, retry=20, match="^抱歉，您每分钟最多访问该接口")
        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            logger.debug("Invoke pro.index_daily with args: {}".format(kwargs))
            res = self.tushare_api().index_daily(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_index_daily', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(IndexDaily, 'default_limit', default_limit_ext)
setattr(IndexDaily, 'default_order_by', default_order_by_ext)
setattr(IndexDaily, 'prepare', prepare_ext)
setattr(IndexDaily, 'tushare_parameters', tushare_parameters_ext)
setattr(IndexDaily, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)    # 显示列数
    pd.set_option('display.width', 1000)
    logger.setLevel(logging.INFO)
    api = IndexDaily()
    api.process(ProcessType.HISTORY)    # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.index_daily())    # 数据查询接口
