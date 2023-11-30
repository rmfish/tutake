"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare ggt_daily接口
获取港股通每日成交信息，数据从2014年开始
数据接口-沪深股票-行情数据-港股通每日成交统计  https://tushare.pro/document/2?doc_id=196

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.ggt_daily_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareGgtDaily(TutakeTableBase):
    __tablename__ = "tushare_ggt_daily"
    trade_date = Column(String, index=True, comment='交易日期')
    buy_amount = Column(Float, comment='买入成交金额（亿元）')
    buy_volume = Column(Float, comment='买入成交笔数（万笔）')
    sell_amount = Column(Float, comment='卖出成交金额（亿元）')
    sell_volume = Column(Float, comment='卖出成交笔数（万笔）')


class GgtDaily(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_ggt_daily"
        self.database = 'tutake.duckdb'
        self.database_dir = config.get_tutake_data_dir()
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareGgtDaily.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareGgtDaily)

        query_fields = ['trade_date', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = ["trade_date", "buy_amount", "buy_volume", "sell_amount", "sell_volume"]
        entity_fields = ["trade_date", "buy_amount", "buy_volume", "sell_amount", "sell_volume"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareGgtDaily, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "ggt_daily", config)
        TuShareBase.__init__(self, "ggt_daily", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "buy_amount",
            "type": "Float",
            "comment": "买入成交金额（亿元）"
        }, {
            "name": "buy_volume",
            "type": "Float",
            "comment": "买入成交笔数（万笔）"
        }, {
            "name": "sell_amount",
            "type": "Float",
            "comment": "卖出成交金额（亿元）"
        }, {
            "name": "sell_volume",
            "type": "Float",
            "comment": "卖出成交笔数（万笔）"
        }]

    def ggt_daily(self, fields='', **kwargs):
        """
        获取港股通每日成交信息，数据从2014年开始
        | Arguments:
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  交易日期 Y
         buy_amount(float)  买入成交金额（亿元） Y
         buy_volume(float)  买入成交笔数（万笔） Y
         sell_amount(float)  卖出成交金额（亿元） Y
         sell_volume(float)  卖出成交笔数（万笔） Y
        
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append,
                                BatchWriter(self.engine, self.table_name, self.schema, self.database_dir), **kwargs)

    def fetch_and_append(self, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        init_args = {"trade_date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.ggt_daily with args: {}".format(kwargs))
                return self.tushare_query('ggt_daily', fields=self.tushare_fields, **kwargs)
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


setattr(GgtDaily, 'default_limit', default_limit_ext)
setattr(GgtDaily, 'default_cron_express', default_cron_express_ext)
setattr(GgtDaily, 'default_order_by', default_order_by_ext)
setattr(GgtDaily, 'prepare', prepare_ext)
setattr(GgtDaily, 'query_parameters', query_parameters_ext)
setattr(GgtDaily, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.ggt_daily())

    api = GgtDaily(config)
    print(api.process())    # 同步增量数据
    print(api.ggt_daily())    # 数据查询接口
