"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare weekly接口
获取A股周线行情,全部历史，每周五15点～17点之间更新
数据接口-沪深股票-行情数据-周线行情  https://tushare.pro/document/2?doc_id=144

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import weekly_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareWeekly(TutakeTableBase):
    __tablename__ = "tushare_weekly"
    ts_code = Column(String, index=True, comment='')
    trade_date = Column(String, index=True, comment='')
    close = Column(Float, comment='')
    open = Column(Float, comment='')
    high = Column(Float, comment='')
    low = Column(Float, comment='')
    pre_close = Column(Float, comment='')
    change = Column(Float, comment='')
    pct_chg = Column(Float, comment='')
    vol = Column(Float, comment='')
    amount = Column(Float, comment='')


class Weekly(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_weekly"
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
        TushareWeekly.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareWeekly)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "trade_date", "close", "open", "high", "low", "pre_close", "change", "pct_chg", "vol", "amount"
        ]
        entity_fields = [
            "ts_code", "trade_date", "close", "open", "high", "low", "pre_close", "change", "pct_chg", "vol", "amount"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareWeekly, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "weekly", config)
        TuShareBase.__init__(self, "weekly", config, 600)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": ""
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": ""
        }, {
            "name": "close",
            "type": "Float",
            "comment": ""
        }, {
            "name": "open",
            "type": "Float",
            "comment": ""
        }, {
            "name": "high",
            "type": "Float",
            "comment": ""
        }, {
            "name": "low",
            "type": "Float",
            "comment": ""
        }, {
            "name": "pre_close",
            "type": "Float",
            "comment": ""
        }, {
            "name": "change",
            "type": "Float",
            "comment": ""
        }, {
            "name": "pct_chg",
            "type": "Float",
            "comment": ""
        }, {
            "name": "vol",
            "type": "Float",
            "comment": ""
        }, {
            "name": "amount",
            "type": "Float",
            "comment": ""
        }]

    def weekly(self, fields='', **kwargs):
        """
        获取A股周线行情,全部历史，每周五15点～17点之间更新
        | Arguments:
        | ts_code(str):   TS代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)   Y
         trade_date(str)   Y
         close(float)   Y
         open(float)   Y
         high(float)   Y
         low(float)   Y
         pre_close(float)   Y
         change(float)   Y
         pct_chg(float)   Y
         vol(float)   Y
         amount(float)   Y
        
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
        init_args = {"ts_code": "", "trade_date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
        is_test = kwargs.get('test') or False
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
                self.logger.debug("Invoke pro.weekly with args: {}".format(kwargs))
                return self.tushare_query('weekly', fields=self.tushare_fields, **kwargs)
            except Exception as err:
                raise ProcessException(kwargs, err)

        res = fetch_save(offset)
        size = res.size()
        offset += size
        res.fields = self.entity_fields
        if is_test:
            return res
        while kwargs['limit'] != "" and size == int(kwargs['limit']):
            result = fetch_save(offset)
            size = result.size()
            offset += size
            res.append(result)
        return res


extends_attr(Weekly, weekly_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.weekly())

    api = Weekly(config)
    print(api.process())    # 同步增量数据
    print(api.weekly())    # 数据查询接口
