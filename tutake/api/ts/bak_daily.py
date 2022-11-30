"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare bak_daily接口
获取备用行情，包括特定的行情指标。量比、换手率、成交量、流通市值、强弱度(%)...
数据接口-沪深股票-行情数据-备用行情  https://tushare.pro/document/2?doc_id=255

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.bak_daily_ext import *
from tutake.api.ts.base_dao import BaseDao, Base
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareBakDaily(Base):
    __tablename__ = "tushare_bak_daily"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='股票代码')
    trade_date = Column(String, index=True, comment='交易日期')
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


class BakDaily(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine("%s/%s" % (config.get_data_sqlite_driver_url(), 'tushare_bak_daily.db'),
                                    connect_args={'check_same_thread': False})
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareBakDaily.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'offset', 'limit']
        entity_fields = [
            "ts_code", "trade_date", "name", "pct_change", "close", "change", "open", "high", "low", "pre_close",
            "vol_ratio", "turn_over", "swing", "vol", "amount", "selling", "buying", "total_share", "float_share", "pe",
            "industry", "area", "float_mv", "total_mv", "avg_price", "strength", "activity", "avg_turnover", "attack",
            "interval_3", "interval_6"
        ]
        BaseDao.__init__(self, self.engine, session_factory, TushareBakDaily, 'tushare_bak_daily', query_fields,
                         entity_fields, config)
        DataProcess.__init__(self, "bak_daily", config)
        TuShareBase.__init__(self, "bak_daily", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "股票代码"
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "name",
            "type": "String",
            "comment": "股票名称"
        }, {
            "name": "pct_change",
            "type": "Float",
            "comment": "涨跌幅"
        }, {
            "name": "close",
            "type": "Float",
            "comment": "收盘价"
        }, {
            "name": "change",
            "type": "Float",
            "comment": "涨跌额"
        }, {
            "name": "open",
            "type": "Float",
            "comment": "开盘价"
        }, {
            "name": "high",
            "type": "Float",
            "comment": "最高价"
        }, {
            "name": "low",
            "type": "Float",
            "comment": "最低价"
        }, {
            "name": "pre_close",
            "type": "Float",
            "comment": "昨收价"
        }, {
            "name": "vol_ratio",
            "type": "Float",
            "comment": "量比"
        }, {
            "name": "turn_over",
            "type": "Float",
            "comment": "换手率"
        }, {
            "name": "swing",
            "type": "Float",
            "comment": "振幅"
        }, {
            "name": "vol",
            "type": "Float",
            "comment": "成交量"
        }, {
            "name": "amount",
            "type": "Float",
            "comment": "成交额"
        }, {
            "name": "selling",
            "type": "Float",
            "comment": "外盘"
        }, {
            "name": "buying",
            "type": "Float",
            "comment": "内盘"
        }, {
            "name": "total_share",
            "type": "Float",
            "comment": "总股本(万)"
        }, {
            "name": "float_share",
            "type": "Float",
            "comment": "流通股本(万)"
        }, {
            "name": "pe",
            "type": "Float",
            "comment": "市盈(动)"
        }, {
            "name": "industry",
            "type": "String",
            "comment": "所属行业"
        }, {
            "name": "area",
            "type": "String",
            "comment": "所属地域"
        }, {
            "name": "float_mv",
            "type": "Float",
            "comment": "流通市值"
        }, {
            "name": "total_mv",
            "type": "Float",
            "comment": "总市值"
        }, {
            "name": "avg_price",
            "type": "Float",
            "comment": "平均价"
        }, {
            "name": "strength",
            "type": "Float",
            "comment": "强弱度(%)"
        }, {
            "name": "activity",
            "type": "Float",
            "comment": "活跃度(%)"
        }, {
            "name": "avg_turnover",
            "type": "Float",
            "comment": "笔换手"
        }, {
            "name": "attack",
            "type": "Float",
            "comment": "攻击波(%)"
        }, {
            "name": "interval_3",
            "type": "Float",
            "comment": "近3月涨幅"
        }, {
            "name": "interval_6",
            "type": "Float",
            "comment": "近6月涨幅"
        }]

    def bak_daily(self, fields='', **kwargs):
        """
        获取备用行情，包括特定的行情指标。量比、换手率、成交量、流通市值、强弱度(%)...
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
        init_args = {"ts_code": "", "trade_date": "", "start_date": "", "end_date": "", "offset": "", "limit": ""}
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
                self.logger.debug("Invoke pro.bak_daily with args: {}".format(kwargs))
                res = self.tushare_query('bak_daily', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_bak_daily',
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


setattr(BakDaily, 'default_limit', default_limit_ext)
setattr(BakDaily, 'default_cron_express', default_cron_express_ext)
setattr(BakDaily, 'default_order_by', default_order_by_ext)
setattr(BakDaily, 'prepare', prepare_ext)
setattr(BakDaily, 'tushare_parameters', tushare_parameters_ext)
setattr(BakDaily, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.bak_daily())

    api = BakDaily(config)
    api.process()    # 同步增量数据
    print(api.bak_daily())    # 数据查询接口
