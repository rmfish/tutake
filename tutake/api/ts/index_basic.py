"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare index_basic接口
获取指数基础信息。
数据接口-指数-指数基本信息  https://tushare.pro/document/2?doc_id=94

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import index_basic_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareIndexBasic(TutakeTableBase):
    __tablename__ = "tushare_index_basic"
    ts_code = Column(String, index=True, comment='TS代码')
    name = Column(String, index=True, comment='简称')
    fullname = Column(String, comment='指数全称')
    market = Column(String, index=True, comment='市场')
    publisher = Column(String, index=True, comment='发布方')
    index_type = Column(String, comment='指数风格')
    category = Column(String, index=True, comment='指数类别')
    base_date = Column(String, comment='基期')
    base_point = Column(Float, comment='基点')
    list_date = Column(String, comment='发布日期')
    weight_rule = Column(String, comment='加权方式')
    desc = Column(String, comment='描述')
    exp_date = Column(String, comment='终止日期')


class IndexBasic(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_index_basic"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareIndexBasic.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareIndexBasic),
                                  config.get_tutake_data_dir())

        query_fields = ['ts_code', 'market', 'publisher', 'category', 'name', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "name", "fullname", "market", "publisher", "index_type", "category", "base_date", "base_point",
            "list_date", "weight_rule", "desc", "exp_date"
        ]
        entity_fields = [
            "ts_code", "name", "fullname", "market", "publisher", "index_type", "category", "base_date", "base_point",
            "list_date", "weight_rule", "desc", "exp_date"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareIndexBasic, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "index_basic", config)
        TuShareBase.__init__(self, "index_basic", config, 200)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS代码"
        }, {
            "name": "name",
            "type": "String",
            "comment": "简称"
        }, {
            "name": "fullname",
            "type": "String",
            "comment": "指数全称"
        }, {
            "name": "market",
            "type": "String",
            "comment": "市场"
        }, {
            "name": "publisher",
            "type": "String",
            "comment": "发布方"
        }, {
            "name": "index_type",
            "type": "String",
            "comment": "指数风格"
        }, {
            "name": "category",
            "type": "String",
            "comment": "指数类别"
        }, {
            "name": "base_date",
            "type": "String",
            "comment": "基期"
        }, {
            "name": "base_point",
            "type": "Float",
            "comment": "基点"
        }, {
            "name": "list_date",
            "type": "String",
            "comment": "发布日期"
        }, {
            "name": "weight_rule",
            "type": "String",
            "comment": "加权方式"
        }, {
            "name": "desc",
            "type": "String",
            "comment": "描述"
        }, {
            "name": "exp_date",
            "type": "String",
            "comment": "终止日期"
        }]

    def index_basic(self, fields='ts_code,name,market,publisher,category,base_date,base_point,list_date', **kwargs):
        """
        获取指数基础信息。
        | Arguments:
        | ts_code(str):   指数代码
        | market(str):   交易所或服务商
        | publisher(str):   发布商
        | category(str):   指数类别
        | name(str):   指数名称
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS代码 Y
         name(str)  简称 Y
         fullname(str)  指数全称 N
         market(str)  市场 Y
         publisher(str)  发布方 Y
         index_type(str)  指数风格 N
         category(str)  指数类别 Y
         base_date(str)  基期 Y
         base_point(float)  基点 Y
         list_date(str)  发布日期 Y
         weight_rule(str)  加权方式 N
         desc(str)  描述 N
         exp_date(str)  终止日期 N
        
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
            "market": "",
            "publisher": "",
            "category": "",
            "name": "",
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
                self.logger.debug("Invoke pro.index_basic with args: {}".format(kwargs))
                return self.tushare_query('index_basic', fields=self.tushare_fields, **kwargs)
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


extends_attr(IndexBasic, index_basic_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.index_basic())

    api = IndexBasic(config)
    print(api.process())    # 同步增量数据
    print(api.index_basic())    # 数据查询接口
