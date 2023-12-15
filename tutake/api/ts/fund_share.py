"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_share接口
获取基金规模数据，包含上海和深圳ETF基金
数据接口-公募基金-基金规模  https://tushare.pro/document/2?doc_id=207

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import fund_share_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareFundShare(TutakeTableBase):
    __tablename__ = "tushare_fund_share"
    ts_code = Column(String, index=True, comment='基金代码')
    trade_date = Column(String, index=True, comment='交易（变动）日期')
    fd_share = Column(Float, comment='基金份额（万）')
    total_share = Column(Float, comment='合计份额（万）')
    fund_type = Column(String, index=True, comment='基金类型')
    market = Column(String, index=True, comment='市场')


class FundShare(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_fund_share"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareFundShare.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareFundShare),
                                  config.get_tutake_data_dir())

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'market', 'fund_type', 'limit', 'offset']
        self.tushare_fields = ["ts_code", "trade_date", "fd_share", "total_share", "fund_type", "market"]
        entity_fields = ["ts_code", "trade_date", "fd_share", "total_share", "fund_type", "market"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareFundShare, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "fund_share", config)
        TuShareBase.__init__(self, "fund_share", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "基金代码"
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": "交易（变动）日期"
        }, {
            "name": "fd_share",
            "type": "Float",
            "comment": "基金份额（万）"
        }, {
            "name": "total_share",
            "type": "Float",
            "comment": "合计份额（万）"
        }, {
            "name": "fund_type",
            "type": "String",
            "comment": "基金类型"
        }, {
            "name": "market",
            "type": "String",
            "comment": "市场"
        }]

    def fund_share(self, fields='ts_code,trade_date,fd_share,fund_type,market', **kwargs):
        """
        获取基金规模数据，包含上海和深圳ETF基金
        | Arguments:
        | ts_code(str):   TS基金代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | market(str):   市场：SH/SZ
        | fund_type(str):   类型
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  基金代码 Y
         trade_date(str)  交易（变动）日期 Y
         fd_share(float)  基金份额（万） Y
         total_share(float)  合计份额（万） N
         fund_type(str)  基金类型 Y
         market(str)  市场 Y
        
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append, self.writer, **kwargs)

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
            "market": "",
            "fund_type": "",
            "limit": "",
            "offset": ""
        }
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
                self.logger.debug("Invoke pro.fund_share with args: {}".format(kwargs))
                return self.tushare_query('fund_share', fields=self.tushare_fields, **kwargs)
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


extends_attr(FundShare, fund_share_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fund_share())

    api = FundShare(config)
    print(api.process())    # 同步增量数据
    print(api.fund_share())    # 数据查询接口
