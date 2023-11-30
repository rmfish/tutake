"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare new_share接口
获取新股上市列表数据,每日19点更新
数据接口-沪深股票-基础数据-IPO新股上市  https://tushare.pro/document/2?doc_id=123

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import new_share_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareNewShare(TutakeTableBase):
    __tablename__ = "tushare_new_share"
    ts_code = Column(String, comment='TS股票代码')
    sub_code = Column(String, comment='申购代码')
    name = Column(String, comment='名称')
    ipo_date = Column(String, comment='上网发行日期')
    issue_date = Column(String, comment='上市日期')
    amount = Column(Float, comment='发行总量（万股）')
    market_amount = Column(Float, comment='上网发行总量（万股）')
    price = Column(Float, comment='发行价格')
    pe = Column(Float, comment='市盈率')
    limit_amount = Column(Float, comment='个人申购上限（万股）')
    funds = Column(Float, comment='募集资金（亿元）')
    ballot = Column(Float, comment='中签率')


class NewShare(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_new_share"
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
        TushareNewShare.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareNewShare)

        query_fields = ['start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "sub_code", "name", "ipo_date", "issue_date", "amount", "market_amount", "price", "pe",
            "limit_amount", "funds", "ballot"
        ]
        entity_fields = [
            "ts_code", "sub_code", "name", "ipo_date", "issue_date", "amount", "market_amount", "price", "pe",
            "limit_amount", "funds", "ballot"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareNewShare, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "new_share", config)
        TuShareBase.__init__(self, "new_share", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS股票代码"
        }, {
            "name": "sub_code",
            "type": "String",
            "comment": "申购代码"
        }, {
            "name": "name",
            "type": "String",
            "comment": "名称"
        }, {
            "name": "ipo_date",
            "type": "String",
            "comment": "上网发行日期"
        }, {
            "name": "issue_date",
            "type": "String",
            "comment": "上市日期"
        }, {
            "name": "amount",
            "type": "Float",
            "comment": "发行总量（万股）"
        }, {
            "name": "market_amount",
            "type": "Float",
            "comment": "上网发行总量（万股）"
        }, {
            "name": "price",
            "type": "Float",
            "comment": "发行价格"
        }, {
            "name": "pe",
            "type": "Float",
            "comment": "市盈率"
        }, {
            "name": "limit_amount",
            "type": "Float",
            "comment": "个人申购上限（万股）"
        }, {
            "name": "funds",
            "type": "Float",
            "comment": "募集资金（亿元）"
        }, {
            "name": "ballot",
            "type": "Float",
            "comment": "中签率"
        }]

    def new_share(self, fields='', **kwargs):
        """
        获取新股上市列表数据,每日19点更新
        | Arguments:
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS股票代码 Y
         sub_code(str)  申购代码 Y
         name(str)  名称 Y
         ipo_date(str)  上网发行日期 Y
         issue_date(str)  上市日期 Y
         amount(float)  发行总量（万股） Y
         market_amount(float)  上网发行总量（万股） Y
         price(float)  发行价格 Y
         pe(float)  市盈率 Y
         limit_amount(float)  个人申购上限（万股） Y
         funds(float)  募集资金（亿元） Y
         ballot(float)  中签率 Y
        
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
        init_args = {"start_date": "", "end_date": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.new_share with args: {}".format(kwargs))
                return self.tushare_query('new_share', fields=self.tushare_fields, **kwargs)
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


extends_attr(NewShare, new_share_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.new_share())

    api = NewShare(config)
    print(api.process())    # 同步增量数据
    print(api.new_share())    # 数据查询接口
