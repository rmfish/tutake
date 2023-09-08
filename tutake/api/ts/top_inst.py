"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare top_inst接口
龙虎榜机构交易明细数据,数据开始于2005年，每日晚8点更新
数据接口-沪深股票-市场参考数据-龙虎榜机构交易明细  https://tushare.pro/document/2?doc_id=107

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.top_inst_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareTopInst(Base):
    __tablename__ = "tushare_top_inst"
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String, index=True, comment='交易日期')
    ts_code = Column(String, index=True, comment='TS代码')
    exalter = Column(String, comment='营业部名称')
    buy = Column(Float, comment='买入额（万）')
    buy_rate = Column(Float, comment='买入占总成交比例')
    sell = Column(Float, comment='卖出额（万）')
    sell_rate = Column(Float, comment='卖出占总成交比例')
    net_buy = Column(Float, comment='净成交额（万）')
    side = Column(String, comment='买卖类型0买入1卖出')
    reason = Column(String, comment='上榜理由')


class TopInst(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_top_inst"
        self.database = 'tushare_stock_market.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareTopInst.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['trade_date', 'ts_code', 'limit', 'offset']
        self.tushare_fields = [
            "trade_date", "ts_code", "exalter", "buy", "buy_rate", "sell", "sell_rate", "net_buy", "side", "reason"
        ]
        entity_fields = [
            "trade_date", "ts_code", "exalter", "buy", "buy_rate", "sell", "sell_rate", "net_buy", "side", "reason"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareTopInst, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "top_inst", config)
        TuShareBase.__init__(self, "top_inst", config, 2000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "ts_code",
            "type": "String",
            "comment": "TS代码"
        }, {
            "name": "exalter",
            "type": "String",
            "comment": "营业部名称"
        }, {
            "name": "buy",
            "type": "Float",
            "comment": "买入额（万）"
        }, {
            "name": "buy_rate",
            "type": "Float",
            "comment": "买入占总成交比例"
        }, {
            "name": "sell",
            "type": "Float",
            "comment": "卖出额（万）"
        }, {
            "name": "sell_rate",
            "type": "Float",
            "comment": "卖出占总成交比例"
        }, {
            "name": "net_buy",
            "type": "Float",
            "comment": "净成交额（万）"
        }, {
            "name": "side",
            "type": "String",
            "comment": "买卖类型0买入1卖出"
        }, {
            "name": "reason",
            "type": "String",
            "comment": "上榜理由"
        }]

    def top_inst(self, fields='', **kwargs):
        """
        龙虎榜机构交易明细数据,数据开始于2005年，每日晚8点更新
        | Arguments:
        | trade_date(str): required  交易日期
        | ts_code(str):   TS代码
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  交易日期 Y
         ts_code(str)  TS代码 Y
         exalter(str)  营业部名称 Y
         buy(float)  买入额（万） Y
         buy_rate(float)  买入占总成交比例 Y
         sell(float)  卖出额（万） Y
         sell_rate(float)  卖出占总成交比例 Y
         net_buy(float)  净成交额（万） Y
         side(str)  买卖类型0买入1卖出 Y
         reason(str)  上榜理由 Y
        
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
        init_args = {"trade_date": "", "ts_code": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.top_inst with args: {}".format(kwargs))
                return self.tushare_query('top_inst', fields=self.tushare_fields, **kwargs)
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


setattr(TopInst, 'default_limit', default_limit_ext)
setattr(TopInst, 'default_cron_express', default_cron_express_ext)
setattr(TopInst, 'default_order_by', default_order_by_ext)
setattr(TopInst, 'prepare', prepare_ext)
setattr(TopInst, 'query_parameters', query_parameters_ext)
setattr(TopInst, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.top_inst())

    api = TopInst(config)
    print(api.process())    # 同步增量数据
    print(api.top_inst())    # 数据查询接口
