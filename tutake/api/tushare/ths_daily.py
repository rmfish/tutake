"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare ths_daily接口
数据接口-指数-同花顺概念和行业指数行情  https://tushare.pro/document/2?doc_id=260

@author: rmfish
"""
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.ths_daily_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_ths_daily.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()


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


TushareThsDaily.__table__.create(bind=engine, checkfirst=True)


class ThsDaily(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = [
            "ts_code", "trade_date", "close", "open", "high", "low", "pre_close", "avg_price", "change", "pct_change",
            "vol", "turnover_rate", "total_mv", "float_mv", "pe_ttm", "pb_mrq"
        ]
        BaseDao.__init__(self, engine, session_factory, TushareThsDaily, 'tushare_ths_daily', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "ths_daily")
        self.dao = DAO()

    def ths_daily(self, fields='', **kwargs):
        """
        同花顺行情
        | Arguments:
        | ts_code(str):   指数代码
        | trade_date(str):   交易日期（YYYYMMDD格式，下同）
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS指数代码
         trade_date(str)  交易日
         close(float)  收盘点位
         open(float)  开盘点位
         high(float)  最高点位
         low(float)  最低点位
         pre_close(float)  昨日收盘点
         avg_price(float)  平均点位
         change(float)  涨跌点位
         pct_change(float)  涨跌幅
         vol(float)  成交量
         turnover_rate(float)  换手率
         total_mv(float)  总市值
         float_mv(float)  流通市值
         pe_ttm(float)  PE TTM
         pb_mrq(float)  PB MRQ
        
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
            self.logger.debug("Invoke pro.ths_daily with args: {}".format(kwargs))
            res = self.tushare_api().ths_daily(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_ths_daily', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(ThsDaily, 'default_limit', default_limit_ext)
setattr(ThsDaily, 'default_order_by', default_order_by_ext)
setattr(ThsDaily, 'prepare', prepare_ext)
setattr(ThsDaily, 'tushare_parameters', tushare_parameters_ext)
setattr(ThsDaily, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    api = ThsDaily()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    api.process(ProcessType.INCREASE)    # 同步增量数据
    print(api.ths_daily())    # 数据查询接口
