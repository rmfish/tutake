"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare index_daily接口
指数日线行情,每日15~17点更新
数据接口-期货-南华期货指数行情  https://tushare.pro/document/2?doc_id=155

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.index_daily_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareIndexDaily(Base):
    __tablename__ = "tushare_index_daily"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='None')
    trade_date = Column(String, index=True, comment='None')
    close = Column(Float, comment='None')
    open = Column(Float, comment='None')
    high = Column(Float, comment='None')
    low = Column(Float, comment='None')
    pre_close = Column(Float, comment='None')
    change = Column(Float, comment='None')
    pct_chg = Column(Float, comment='None')
    vol = Column(Float, comment='None')
    amount = Column(Float, comment='None')


class IndexDaily(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_index_daily"
        self.database = 'tushare_index.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareIndexDaily.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "trade_date", "close", "open", "high", "low", "pre_close", "change", "pct_chg", "vol", "amount"
        ]
        entity_fields = [
            "ts_code", "trade_date", "close", "open", "high", "low", "pre_close", "change", "pct_chg", "vol", "amount"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareIndexDaily, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "index_daily", config)
        TuShareBase.__init__(self, "index_daily", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "None"
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": "None"
        }, {
            "name": "close",
            "type": "Float",
            "comment": "None"
        }, {
            "name": "open",
            "type": "Float",
            "comment": "None"
        }, {
            "name": "high",
            "type": "Float",
            "comment": "None"
        }, {
            "name": "low",
            "type": "Float",
            "comment": "None"
        }, {
            "name": "pre_close",
            "type": "Float",
            "comment": "None"
        }, {
            "name": "change",
            "type": "Float",
            "comment": "None"
        }, {
            "name": "pct_chg",
            "type": "Float",
            "comment": "None"
        }, {
            "name": "vol",
            "type": "Float",
            "comment": "None"
        }, {
            "name": "amount",
            "type": "Float",
            "comment": "None"
        }]

    def index_daily(self, fields='', **kwargs):
        """
        指数日线行情,每日15~17点更新
        | Arguments:
        | ts_code(str): required  指数代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  None Y
         trade_date(datetime)  None Y
         close(float)  None Y
         open(float)  None Y
         high(float)  None Y
         low(float)  None Y
         pre_close(float)  None Y
         change(float)  None Y
         pct_chg(float)  None Y
         vol(float)  None Y
         amount(float)  None Y
        
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
                self.logger.debug("Invoke pro.index_daily with args: {}".format(kwargs))
                return self.tushare_query('index_daily', fields=self.tushare_fields, **kwargs)
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


setattr(IndexDaily, 'default_limit', default_limit_ext)
setattr(IndexDaily, 'default_cron_express', default_cron_express_ext)
setattr(IndexDaily, 'default_order_by', default_order_by_ext)
setattr(IndexDaily, 'prepare', prepare_ext)
setattr(IndexDaily, 'query_parameters', query_parameters_ext)
setattr(IndexDaily, 'param_loop_process', param_loop_process_ext)
setattr(IndexDaily, 'check', check_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.index_daily(ts_code='000001.SH'))

    api = IndexDaily(config)
    print(api.process())    # 同步增量数据
    print(api.index_daily(ts_code='000001.SH'))    # 数据查询接口
