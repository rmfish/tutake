"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare daily_basic接口
交易日每日15点～17点之间,获取全部股票每日重要的基本面指标，可用于选股分析、报表展示等。
数据接口-沪深股票-行情数据-每日指标  https://tushare.pro/document/2?doc_id=32

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.daily_basic_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareDailyBasic(Base):
    __tablename__ = "tushare_daily_basic"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='TS股票代码')
    trade_date = Column(String, index=True, comment='交易日期')
    close = Column(Float, comment='当日收盘价')
    turnover_rate = Column(Float, comment='换手率')
    turnover_rate_f = Column(Float, comment='换手率(自由流通股)')
    volume_ratio = Column(Float, comment='量比')
    pe = Column(Float, comment='市盈率（总市值/净利润）')
    pe_ttm = Column(Float, comment='市盈率（TTM）')
    pb = Column(Float, comment='市净率（总市值/净资产）')
    ps = Column(Float, comment='市销率')
    ps_ttm = Column(Float, comment='市销率（TTM）')
    dv_ratio = Column(Float, comment='股息率（%）')
    dv_ttm = Column(Float, comment='股息率（TTM） （%）')
    total_share = Column(Float, comment='总股本')
    float_share = Column(Float, comment='流通股本')
    free_share = Column(Float, comment='自由流通股本')
    total_mv = Column(Float, comment='总市值')
    circ_mv = Column(Float, comment='流通市值')
    limit_status = Column(Integer, comment='涨跌停状态')


class DailyBasic(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_daily_basic"
        self.database = 'tushare_daily_basic.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareDailyBasic.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = [
            "ts_code", "trade_date", "close", "turnover_rate", "turnover_rate_f", "volume_ratio", "pe", "pe_ttm", "pb",
            "ps", "ps_ttm", "dv_ratio", "dv_ttm", "total_share", "float_share", "free_share", "total_mv", "circ_mv",
            "limit_status"
        ]
        TushareDAO.__init__(self, self.engine, session_factory, TushareDailyBasic, self.database, self.table_name,
                            query_fields, entity_fields, config)
        DataProcess.__init__(self, "daily_basic", config)
        TuShareBase.__init__(self, "daily_basic", config, 2000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS股票代码"
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "close",
            "type": "Float",
            "comment": "当日收盘价"
        }, {
            "name": "turnover_rate",
            "type": "Float",
            "comment": "换手率"
        }, {
            "name": "turnover_rate_f",
            "type": "Float",
            "comment": "换手率(自由流通股)"
        }, {
            "name": "volume_ratio",
            "type": "Float",
            "comment": "量比"
        }, {
            "name": "pe",
            "type": "Float",
            "comment": "市盈率（总市值/净利润）"
        }, {
            "name": "pe_ttm",
            "type": "Float",
            "comment": "市盈率（TTM）"
        }, {
            "name": "pb",
            "type": "Float",
            "comment": "市净率（总市值/净资产）"
        }, {
            "name": "ps",
            "type": "Float",
            "comment": "市销率"
        }, {
            "name": "ps_ttm",
            "type": "Float",
            "comment": "市销率（TTM）"
        }, {
            "name": "dv_ratio",
            "type": "Float",
            "comment": "股息率（%）"
        }, {
            "name": "dv_ttm",
            "type": "Float",
            "comment": "股息率（TTM） （%）"
        }, {
            "name": "total_share",
            "type": "Float",
            "comment": "总股本"
        }, {
            "name": "float_share",
            "type": "Float",
            "comment": "流通股本"
        }, {
            "name": "free_share",
            "type": "Float",
            "comment": "自由流通股本"
        }, {
            "name": "total_mv",
            "type": "Float",
            "comment": "总市值"
        }, {
            "name": "circ_mv",
            "type": "Float",
            "comment": "流通市值"
        }, {
            "name": "limit_status",
            "type": "Integer",
            "comment": "涨跌停状态"
        }]

    def daily_basic(
            self,
            fields='ts_code,trade_date,close,turnover_rate,turnover_rate_f,volume_ratio,pe,pe_ttm,pb,ps,ps_ttm,dv_ratio,dv_ttm,total_share,float_share,free_share,total_mv,circ_mv',
            **kwargs):
        """
        交易日每日15点～17点之间,获取全部股票每日重要的基本面指标，可用于选股分析、报表展示等。
        | Arguments:
        | ts_code(str):   股票代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS股票代码 Y
         trade_date(str)  交易日期 Y
         close(number)  当日收盘价 Y
         turnover_rate(number)  换手率 Y
         turnover_rate_f(number)  换手率(自由流通股) Y
         volume_ratio(number)  量比 Y
         pe(number)  市盈率（总市值/净利润） Y
         pe_ttm(number)  市盈率（TTM） Y
         pb(number)  市净率（总市值/净资产） Y
         ps(number)  市销率 Y
         ps_ttm(number)  市销率（TTM） Y
         dv_ratio(number)  股息率（%） Y
         dv_ttm(number)  股息率（TTM） （%） Y
         total_share(number)  总股本 Y
         float_share(number)  流通股本 Y
         free_share(number)  自由流通股本 Y
         total_mv(number)  总市值 Y
         circ_mv(number)  流通市值 Y
         limit_status(int)  涨跌停状态 N
        
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append, BatchWriter(self.engine, self.table_name), **kwargs)

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
                self.logger.debug("Invoke pro.daily_basic with args: {}".format(kwargs))
                return self.tushare_query('daily_basic', fields=self.entity_fields, **kwargs)
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


setattr(DailyBasic, 'default_limit', default_limit_ext)
setattr(DailyBasic, 'default_cron_express', default_cron_express_ext)
setattr(DailyBasic, 'default_order_by', default_order_by_ext)
setattr(DailyBasic, 'prepare', prepare_ext)
setattr(DailyBasic, 'query_parameters', query_parameters_ext)
setattr(DailyBasic, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.daily_basic())

    api = DailyBasic(config)
    print(api.process())    # 同步增量数据
    print(api.daily_basic())    # 数据查询接口
