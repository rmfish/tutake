"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare index_global接口
获取国际主要指数日线行情
数据接口-指数-国际主要指数  https://tushare.pro/document/2?doc_id=211

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.tushare.index_global_ext import *
from tutake.api.tushare.base_dao import BaseDao, Base
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareIndexGlobal(Base):
    __tablename__ = "tushare_index_global"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='TS指数代码')
    trade_date = Column(String, index=True, comment='交易日')
    open = Column(Float, comment='开盘点位')
    close = Column(Float, comment='收盘点位')
    high = Column(Float, comment='最高点位')
    low = Column(Float, comment='最低点位')
    pre_close = Column(Float, comment='昨日收盘点')
    change = Column(Float, comment='涨跌点位')
    pct_chg = Column(Float, comment='涨跌幅')
    swing = Column(Float, comment='振幅')
    vol = Column(Float, comment='成交量')
    amount = Column(Float, comment='成交额')


class IndexGlobal(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine("%s/%s" % (config.get_data_sqlite_driver_url(), 'tushare_index_global.db'),
                                    connect_args={'check_same_thread': False})
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareIndexGlobal.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = [
            "ts_code", "trade_date", "open", "close", "high", "low", "pre_close", "change", "pct_chg", "swing", "vol",
            "amount"
        ]
        BaseDao.__init__(self, self.engine, session_factory, TushareIndexGlobal, 'tushare_index_global', query_fields,
                         entity_fields)
        DataProcess.__init__(self, "index_global", config)
        TuShareBase.__init__(self, "index_global", config, 120)
        self.dao = DAO()

    def index_global(self, fields='', **kwargs):
        """
        获取国际主要指数日线行情
        | Arguments:
        | ts_code(str):   TS指数代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS指数代码
         trade_date(str)  交易日
         open(float)  开盘点位
         close(float)  收盘点位
         high(float)  最高点位
         low(float)  最低点位
         pre_close(float)  昨日收盘点
         change(float)  涨跌点位
         pct_chg(float)  涨跌幅
         swing(float)  振幅
         vol(float)  成交量
         amount(float)  成交额
        
        """
        return super().query(fields, **kwargs)

    def process(self, process_type: ProcessType = ProcessType.INCREASE):
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

        def fetch_save(offset_val=0):
            try:
                kwargs['offset'] = str(offset_val)
                self.logger.debug("Invoke pro.index_global with args: {}".format(kwargs))
                res = self.tushare_query('index_global', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_index_global',
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


setattr(IndexGlobal, 'default_limit', default_limit_ext)
setattr(IndexGlobal, 'default_cron_express', default_cron_express_ext)
setattr(IndexGlobal, 'default_order_by', default_order_by_ext)
setattr(IndexGlobal, 'prepare', prepare_ext)
setattr(IndexGlobal, 'tushare_parameters', tushare_parameters_ext)
setattr(IndexGlobal, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.index_global())

    api = IndexGlobal(config)
    api.process()    # 同步增量数据
    print(api.index_global())    # 数据查询接口
