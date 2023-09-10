"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare daily_info接口
获取交易所股票交易统计，包括各板块明细
数据接口-指数-沪深市场每日交易统计  https://tushare.pro/document/2?doc_id=215

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.daily_info_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareDailyInfo(Base):
    __tablename__ = "tushare_daily_info"
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String, index=True, comment='交易日期')
    ts_code = Column(String, index=True, comment='市场代码')
    ts_name = Column(String, comment='市场名称')
    com_count = Column(Integer, comment='挂牌数')
    total_share = Column(Float, comment='总股本（亿股）')
    float_share = Column(Float, comment='流通股本（亿股）')
    total_mv = Column(Float, comment='总市值（亿元）')
    float_mv = Column(Float, comment='流通市值（亿元）')
    amount = Column(Float, comment='交易金额（亿元）')
    vol = Column(Float, comment='成交量（亿股）')
    trans_count = Column(Integer, comment='成交笔数（万笔）')
    pe = Column(Float, comment='平均市盈率')
    tr = Column(Float, comment='换手率（％）')
    exchange = Column(String, index=True, comment='交易所')


class DailyInfo(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_daily_info"
        self.database = 'tushare_stock.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareDailyInfo.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['trade_date', 'ts_code', 'exchange', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = [
            "trade_date", "ts_code", "ts_name", "com_count", "total_share", "float_share", "total_mv", "float_mv",
            "amount", "vol", "trans_count", "pe", "tr", "exchange"
        ]
        entity_fields = [
            "trade_date", "ts_code", "ts_name", "com_count", "total_share", "float_share", "total_mv", "float_mv",
            "amount", "vol", "trans_count", "pe", "tr", "exchange"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareDailyInfo, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "daily_info", config)
        TuShareBase.__init__(self, "daily_info", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "ts_code",
            "type": "String",
            "comment": "市场代码"
        }, {
            "name": "ts_name",
            "type": "String",
            "comment": "市场名称"
        }, {
            "name": "com_count",
            "type": "Integer",
            "comment": "挂牌数"
        }, {
            "name": "total_share",
            "type": "Float",
            "comment": "总股本（亿股）"
        }, {
            "name": "float_share",
            "type": "Float",
            "comment": "流通股本（亿股）"
        }, {
            "name": "total_mv",
            "type": "Float",
            "comment": "总市值（亿元）"
        }, {
            "name": "float_mv",
            "type": "Float",
            "comment": "流通市值（亿元）"
        }, {
            "name": "amount",
            "type": "Float",
            "comment": "交易金额（亿元）"
        }, {
            "name": "vol",
            "type": "Float",
            "comment": "成交量（亿股）"
        }, {
            "name": "trans_count",
            "type": "Integer",
            "comment": "成交笔数（万笔）"
        }, {
            "name": "pe",
            "type": "Float",
            "comment": "平均市盈率"
        }, {
            "name": "tr",
            "type": "Float",
            "comment": "换手率（％）"
        }, {
            "name": "exchange",
            "type": "String",
            "comment": "交易所"
        }]

    def daily_info(self, fields='', **kwargs):
        """
        获取交易所股票交易统计，包括各板块明细
        | Arguments:
        | trade_date(str):   交易日期
        | ts_code(str):   板块代码
        | exchange(str):   股票市场
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  交易日期 Y
         ts_code(str)  市场代码 Y
         ts_name(str)  市场名称 Y
         com_count(int)  挂牌数 Y
         total_share(float)  总股本（亿股） Y
         float_share(float)  流通股本（亿股） Y
         total_mv(float)  总市值（亿元） Y
         float_mv(float)  流通市值（亿元） Y
         amount(float)  交易金额（亿元） Y
         vol(float)  成交量（亿股） Y
         trans_count(int)  成交笔数（万笔） Y
         pe(float)  平均市盈率 Y
         tr(float)  换手率（％） Y
         exchange(str)  交易所 Y
        
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
        init_args = {
            "trade_date": "",
            "ts_code": "",
            "exchange": "",
            "start_date": "",
            "end_date": "",
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
                self.logger.debug("Invoke pro.daily_info with args: {}".format(kwargs))
                return self.tushare_query('daily_info', fields=self.tushare_fields, **kwargs)
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
        res.fields = self.entity_fields
        return res


setattr(DailyInfo, 'default_limit', default_limit_ext)
setattr(DailyInfo, 'default_cron_express', default_cron_express_ext)
setattr(DailyInfo, 'default_order_by', default_order_by_ext)
setattr(DailyInfo, 'prepare', prepare_ext)
setattr(DailyInfo, 'query_parameters', query_parameters_ext)
setattr(DailyInfo, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.daily_info())

    api = DailyInfo(config)
    print(api.process())    # 同步增量数据
    print(api.daily_info())    # 数据查询接口
