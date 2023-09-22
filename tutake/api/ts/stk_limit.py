"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare stk_limit接口
获取全市场（包含A/B股和基金）每日涨跌停价格，包括涨停价格，跌停价格等，每个交易日8点40左右更新当日股票涨跌停价格。交易日9点更新
数据接口-沪深股票-行情数据-每日涨跌停价格  https://tushare.pro/document/2?doc_id=183

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.stk_limit_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareStkLimit(Base):
    __tablename__ = "tushare_stk_limit"
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String, index=True, comment='交易日期')
    ts_code = Column(String, index=True, comment='TS股票代码')
    pre_close = Column(Float, comment='昨日收盘价')
    up_limit = Column(Float, comment='涨停价')
    down_limit = Column(Float, comment='跌停价')


class StkLimit(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_stk_limit"
        self.database = 'tushare_stk.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareStkLimit.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'offset', 'limit']
        self.tushare_fields = ["trade_date", "ts_code", "pre_close", "up_limit", "down_limit"]
        entity_fields = ["trade_date", "ts_code", "pre_close", "up_limit", "down_limit"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareStkLimit, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "stk_limit", config)
        TuShareBase.__init__(self, "stk_limit", config, 2000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "ts_code",
            "type": "String",
            "comment": "TS股票代码"
        }, {
            "name": "pre_close",
            "type": "Float",
            "comment": "昨日收盘价"
        }, {
            "name": "up_limit",
            "type": "Float",
            "comment": "涨停价"
        }, {
            "name": "down_limit",
            "type": "Float",
            "comment": "跌停价"
        }]

    def stk_limit(self, fields='trade_date,ts_code,up_limit,down_limit', **kwargs):
        """
        获取全市场（包含A/B股和基金）每日涨跌停价格，包括涨停价格，跌停价格等，每个交易日8点40左右更新当日股票涨跌停价格。交易日9点更新
        | Arguments:
        | ts_code(str):   股票代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | offset(int):   开始行数
        | limit(int):   每页最大条数
        
        :return: DataFrame
         trade_date(str)  交易日期 Y
         ts_code(str)  TS股票代码 Y
         pre_close(float)  昨日收盘价 N
         up_limit(float)  涨停价 Y
         down_limit(float)  跌停价 Y
        
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
                self.logger.debug("Invoke pro.stk_limit with args: {}".format(kwargs))
                return self.tushare_query('stk_limit', fields=self.tushare_fields, **kwargs)
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


setattr(StkLimit, 'default_limit', default_limit_ext)
setattr(StkLimit, 'default_cron_express', default_cron_express_ext)
setattr(StkLimit, 'default_order_by', default_order_by_ext)
setattr(StkLimit, 'prepare', prepare_ext)
setattr(StkLimit, 'query_parameters', query_parameters_ext)
setattr(StkLimit, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.stk_limit())

    api = StkLimit(config)
    print(api.process())    # 同步增量数据
    print(api.stk_limit())    # 数据查询接口
