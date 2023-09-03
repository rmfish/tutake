"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare hsgt_top10接口
获取沪股通、深股通每日前十大成交股数据
数据接口-沪深股票-行情数据-沪深股通十大成交股  https://tushare.pro/document/2?doc_id=48

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.hsgt_top10_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareHsgtTop10(Base):
    __tablename__ = "tushare_hsgt_top10"
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String, index=True, comment='交易日期')
    ts_code = Column(String, index=True, comment='股票代码')
    name = Column(String, comment='股票名称')
    close = Column(Float, comment='收盘价')
    change = Column(Float, comment='涨跌幅')
    rank = Column(String, comment='资金排名')
    market_type = Column(String, index=True, comment='市场类型（1：沪市 3：深市）')
    amount = Column(Float, comment='成交金额')
    net_amount = Column(Float, comment='净成交金额')
    buy = Column(Float, comment='买入金额')
    sell = Column(Float, comment='卖出金额')


class HsgtTop10(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_hsgt_top10"
        self.database = 'tushare_hsgt_top10.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareHsgtTop10.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'market_type', 'limit', 'offset']
        entity_fields = [
            "trade_date", "ts_code", "name", "close", "change", "rank", "market_type", "amount", "net_amount", "buy",
            "sell"
        ]
        TushareDAO.__init__(self, self.engine, session_factory, TushareHsgtTop10, self.database, self.table_name,
                            query_fields, entity_fields, config)
        DataProcess.__init__(self, "hsgt_top10", config)
        TuShareBase.__init__(self, "hsgt_top10", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "ts_code",
            "type": "String",
            "comment": "股票代码"
        }, {
            "name": "name",
            "type": "String",
            "comment": "股票名称"
        }, {
            "name": "close",
            "type": "Float",
            "comment": "收盘价"
        }, {
            "name": "change",
            "type": "Float",
            "comment": "涨跌幅"
        }, {
            "name": "rank",
            "type": "String",
            "comment": "资金排名"
        }, {
            "name": "market_type",
            "type": "String",
            "comment": "市场类型（1：沪市 3：深市）"
        }, {
            "name": "amount",
            "type": "Float",
            "comment": "成交金额"
        }, {
            "name": "net_amount",
            "type": "Float",
            "comment": "净成交金额"
        }, {
            "name": "buy",
            "type": "Float",
            "comment": "买入金额"
        }, {
            "name": "sell",
            "type": "Float",
            "comment": "卖出金额"
        }]

    def hsgt_top10(self, fields='', **kwargs):
        """
        获取沪股通、深股通每日前十大成交股数据
        | Arguments:
        | ts_code(str):   股票代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | market_type(str):   市场类型（1：沪市 3：深市）
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  交易日期 Y
         ts_code(str)  股票代码 Y
         name(str)  股票名称 Y
         close(float)  收盘价 Y
         change(float)  涨跌幅 Y
         rank(str)  资金排名 Y
         market_type(str)  市场类型（1：沪市 3：深市） Y
         amount(float)  成交金额 Y
         net_amount(float)  净成交金额 Y
         buy(float)  买入金额 Y
         sell(float)  卖出金额 Y
        
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
        init_args = {
            "ts_code": "",
            "trade_date": "",
            "start_date": "",
            "end_date": "",
            "market_type": "",
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
                self.logger.debug("Invoke pro.hsgt_top10 with args: {}".format(kwargs))
                return self.tushare_query('hsgt_top10', fields=self.entity_fields, **kwargs)
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


setattr(HsgtTop10, 'default_limit', default_limit_ext)
setattr(HsgtTop10, 'default_cron_express', default_cron_express_ext)
setattr(HsgtTop10, 'default_order_by', default_order_by_ext)
setattr(HsgtTop10, 'prepare', prepare_ext)
setattr(HsgtTop10, 'query_parameters', query_parameters_ext)
setattr(HsgtTop10, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.hsgt_top10())

    api = HsgtTop10(config)
    api.process()    # 同步增量数据
    print(api.hsgt_top10())    # 数据查询接口
