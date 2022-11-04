import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao
from tutake.api.dao import DAO
from tutake.api.process_type import ProcessType
from tutake.api.tushare_base import TuShareBase
from tutake.utils.config import config
"""
Tushare bak_daily接口
数据接口-沪深股票-行情数据-备用行情  https://tushare.pro/document/2?doc_id=255
"""

engine = create_engine(
    "%s/%s" % (config['database']['driver_url'], 'tushare_bak_daily.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.bak_daily')


class TushareBakDaily(Base):
    __tablename__ = "tushare_bak_daily"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, comment='股票代码')
    trade_date = Column(String, comment='交易日期')
    name = Column(String, comment='股票名称')
    pct_change = Column(Float, comment='涨跌幅')
    close = Column(Float, comment='收盘价')
    change = Column(Float, comment='涨跌额')
    open = Column(Float, comment='开盘价')
    high = Column(Float, comment='最高价')
    low = Column(Float, comment='最低价')
    pre_close = Column(Float, comment='昨收价')
    vol_ratio = Column(Float, comment='量比')
    turn_over = Column(Float, comment='换手率')
    swing = Column(Float, comment='振幅')
    vol = Column(Float, comment='成交量')
    amount = Column(Float, comment='成交额')
    selling = Column(Float, comment='外盘')
    buying = Column(Float, comment='内盘')
    total_share = Column(Float, comment='总股本(万)')
    float_share = Column(Float, comment='流通股本(万)')
    pe = Column(Float, comment='市盈(动)')
    industry = Column(String, comment='所属行业')
    area = Column(String, comment='所属地域')
    float_mv = Column(Float, comment='流通市值')
    total_mv = Column(Float, comment='总市值')
    avg_price = Column(Float, comment='平均价')
    strength = Column(Float, comment='强弱度(%)')
    activity = Column(Float, comment='活跃度(%)')
    avg_turnover = Column(Float, comment='笔换手')
    attack = Column(Float, comment='攻击波(%)')
    interval_3 = Column(Float, comment='近3月涨幅')
    interval_6 = Column(Float, comment='近6月涨幅')


TushareBakDaily.__table__.create(bind=engine, checkfirst=True)


class BakDaily(BaseDao, TuShareBase):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        BaseDao.__init__(self, engine, session_factory, TushareBakDaily,
                         'tushare_bak_daily')
        TuShareBase.__init__(self)
        self.dao = DAO()

    def bak_daily(self, **kwargs):
        """
        

        | Arguments:
        | ts_code(str):   股票代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | offset(str):   开始行数
        | limit(str):   最大行数
        

        :return: DataFrame
         ts_code(str)  股票代码
         trade_date(str)  交易日期
         name(str)  股票名称
         pct_change(float)  涨跌幅
         close(float)  收盘价
         change(float)  涨跌额
         open(float)  开盘价
         high(float)  最高价
         low(float)  最低价
         pre_close(float)  昨收价
         vol_ratio(float)  量比
         turn_over(float)  换手率
         swing(float)  振幅
         vol(float)  成交量
         amount(float)  成交额
         selling(float)  外盘
         buying(float)  内盘
         total_share(float)  总股本(万)
         float_share(float)  流通股本(万)
         pe(float)  市盈(动)
         industry(str)  所属行业
         area(str)  所属地域
         float_mv(float)  流通市值
         total_mv(float)  总市值
         avg_price(float)  平均价
         strength(float)  强弱度(%)
         activity(float)  活跃度(%)
         avg_turnover(float)  笔换手
         attack(float)  攻击波(%)
         interval_3(float)  近3月涨幅
         interval_6(float)  近6月涨幅
        
        """
        args = [
            n for n in [
                'ts_code',
                'trade_date',
                'start_date',
                'end_date',
                'offset',
                'limit',
            ] if n not in ['limit', 'offset']
        ]
        params = {key: kwargs[key] for key in kwargs.keys() & args}
        query = session_factory().query(TushareBakDaily).filter_by(**params)
        query = query.order_by(text("trade_date desc,ts_code"))
        input_limit = 10000  # 默认10000条 避免导致数据库压力过大
        if kwargs.get('limit') and str(kwargs.get('limit')).isnumeric():
            input_limit = int(kwargs.get('limit'))
            query = query.limit(input_limit)
        if "" != "":
            default_limit = int("")
            if default_limit < input_limit:
                query = query.limit(default_limit)
        if kwargs.get('offset') and str(kwargs.get('offset')).isnumeric():
            query = query.offset(int(kwargs.get('offset')))
        return pd.read_sql(query.statement, query.session.bind)

    def prepare(self, process_type: ProcessType):
        """
        同步历史数据准备工作
        :return:
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
                    logger.debug("Fetch and append {} data, cnt is {}".format(
                        "daily", cnt))
                except Exception as err:
                    if err.args[0].startswith("抱歉，您没有访问该接口的权限") or err.args[
                            0].startswith("抱歉，您每天最多访问该接口"):
                        logger.error(
                            "Throw exception with param: {} err:{}".format(
                                new_param, err))
                        return
                    continue

    def fetch_and_append(self, process_type: ProcessType, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        if len(kwargs.keys()) == 0:
            kwargs = {
                "ts_code": "",
                "trade_date": "",
                "start_date": "",
                "end_date": "",
                "offset": "",
                "limit": ""
            }
        # 初始化offset和limit
        if not kwargs.get("limit"):
            kwargs['limit'] = ""
        init_offset = 0
        offset = 0
        if kwargs.get('offset') and kwargs.get('offset').isnumeric():
            offset = int(kwargs['offset'])
            init_offset = offset

        kwargs = {
            key: kwargs[key]
            for key in kwargs.keys() & list([
                'ts_code',
                'trade_date',
                'start_date',
                'end_date',
                'offset',
                'limit',
            ])
        }

        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            logger.debug("Invoke pro.bak_daily with args: {}".format(kwargs))
            fields = [
                "ts_code", "trade_date", "name", "pct_change", "close",
                "change", "open", "high", "low", "pre_close", "vol_ratio",
                "turn_over", "swing", "vol", "amount", "selling", "buying",
                "total_share", "float_share", "pe", "industry", "area",
                "float_mv", "total_mv", "avg_price", "strength", "activity",
                "avg_turnover", "attack", "interval_3", "interval_6"
            ]
            res = pro.bak_daily(**kwargs, fields=fields)
            res.to_sql('tushare_bak_daily',
                       con=engine,
                       if_exists='append',
                       index=False,
                       index_label=['ts_code'])
            return res

        pro = self.tushare_api()
        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and df.shape[0] == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    api = BakDaily()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.bak_daily())  # 数据查询接口
