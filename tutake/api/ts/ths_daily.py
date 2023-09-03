"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare ths_daily接口
获取同花顺板块指数行情。
数据接口-指数-同花顺概念和行业指数行情  https://tushare.pro/document/2?doc_id=260

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.ths_daily_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareThsDaily(Base):
    __tablename__ = "tushare_ths_daily"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='TS指数代码')
    trade_date = Column(String, index=True, comment='交易日')
    close = Column(Float, comment='收盘点位')
    open = Column(Float, comment='开盘点位')
    high = Column(Float, comment='最高点位')
    low = Column(Float, comment='最低点位')
    pre_close = Column(Float, comment='昨日收盘点')
    avg_price = Column(Float, comment='平均点位')
    change = Column(Float, comment='涨跌点位')
    pct_change = Column(Float, comment='涨跌幅')
    vol = Column(Float, comment='成交量')
    turnover_rate = Column(Float, comment='换手率')
    total_mv = Column(Float, comment='总市值')
    float_mv = Column(Float, comment='流通市值')
    pe_ttm = Column(Float, comment='PE TTM')
    pb_mrq = Column(Float, comment='PB MRQ')


class ThsDaily(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_ths_daily"
        self.database = 'tushare_ths.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareThsDaily.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = [
            "ts_code", "trade_date", "close", "open", "high", "low", "pre_close", "avg_price", "change", "pct_change",
            "vol", "turnover_rate", "total_mv", "float_mv", "pe_ttm", "pb_mrq"
        ]
        TushareDAO.__init__(self, self.engine, session_factory, TushareThsDaily, self.database, self.table_name,
                            query_fields, entity_fields, config)
        DataProcess.__init__(self, "ths_daily", config)
        TuShareBase.__init__(self, "ths_daily", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS指数代码"
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": "交易日"
        }, {
            "name": "close",
            "type": "Float",
            "comment": "收盘点位"
        }, {
            "name": "open",
            "type": "Float",
            "comment": "开盘点位"
        }, {
            "name": "high",
            "type": "Float",
            "comment": "最高点位"
        }, {
            "name": "low",
            "type": "Float",
            "comment": "最低点位"
        }, {
            "name": "pre_close",
            "type": "Float",
            "comment": "昨日收盘点"
        }, {
            "name": "avg_price",
            "type": "Float",
            "comment": "平均点位"
        }, {
            "name": "change",
            "type": "Float",
            "comment": "涨跌点位"
        }, {
            "name": "pct_change",
            "type": "Float",
            "comment": "涨跌幅"
        }, {
            "name": "vol",
            "type": "Float",
            "comment": "成交量"
        }, {
            "name": "turnover_rate",
            "type": "Float",
            "comment": "换手率"
        }, {
            "name": "total_mv",
            "type": "Float",
            "comment": "总市值"
        }, {
            "name": "float_mv",
            "type": "Float",
            "comment": "流通市值"
        }, {
            "name": "pe_ttm",
            "type": "Float",
            "comment": "PE TTM"
        }, {
            "name": "pb_mrq",
            "type": "Float",
            "comment": "PB MRQ"
        }]

    def ths_daily(
            self,
            fields='ts_code,trade_date,close,open,high,low,pre_close,avg_price,change,pct_change,vol,turnover_rate',
            **kwargs):
        """
        获取同花顺板块指数行情。
        | Arguments:
        | ts_code(str):   指数代码
        | trade_date(str):   交易日期（YYYYMMDD格式，下同）
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS指数代码 Y
         trade_date(str)  交易日 Y
         close(float)  收盘点位 Y
         open(float)  开盘点位 Y
         high(float)  最高点位 Y
         low(float)  最低点位 Y
         pre_close(float)  昨日收盘点 Y
         avg_price(float)  平均点位 Y
         change(float)  涨跌点位 Y
         pct_change(float)  涨跌幅 Y
         vol(float)  成交量 Y
         turnover_rate(float)  换手率 Y
         total_mv(float)  总市值 N
         float_mv(float)  流通市值 N
         pe_ttm(float)  PE TTM N
         pb_mrq(float)  PB MRQ N
        
        """
        return super().query(fields, **kwargs)

    def process(self):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append, BatchWriter(self.engine, self.table_name))

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
                self.logger.debug("Invoke pro.ths_daily with args: {}".format(kwargs))
                return self.tushare_query('ths_daily', fields=self.entity_fields, **kwargs)
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


setattr(ThsDaily, 'default_limit', default_limit_ext)
setattr(ThsDaily, 'default_cron_express', default_cron_express_ext)
setattr(ThsDaily, 'default_order_by', default_order_by_ext)
setattr(ThsDaily, 'prepare', prepare_ext)
setattr(ThsDaily, 'query_parameters', query_parameters_ext)
setattr(ThsDaily, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.ths_daily())

    api = ThsDaily(config)
    api.process()    # 同步增量数据
    print(api.ths_daily())    # 数据查询接口
