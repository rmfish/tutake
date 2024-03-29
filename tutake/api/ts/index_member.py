"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare index_member接口
申万行业成分构成
数据接口-指数-申万行业成分  https://tushare.pro/document/2?doc_id=182

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import index_member_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareIndexMember(TutakeTableBase):
    __tablename__ = "tushare_index_member"
    index_code = Column(String, index=True, comment='指数代码')
    index_name = Column(String, comment='指数名称')
    con_code = Column(String, comment='成分股票代码')
    con_name = Column(String, comment='成分股票名称')
    in_date = Column(String, comment='纳入日期')
    out_date = Column(String, comment='剔除日期')
    is_new = Column(String, index=True, comment='是否最新Y是N否')


class IndexMember(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_index_member"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareIndexMember.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareIndexMember),
                                  config.get_tutake_data_dir())

        query_fields = ['index_code', 'is_new', 'ts_code', 'limit', 'offset']
        self.tushare_fields = ["index_code", "index_name", "con_code", "con_name", "in_date", "out_date", "is_new"]
        entity_fields = ["index_code", "index_name", "con_code", "con_name", "in_date", "out_date", "is_new"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareIndexMember, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "index_member", config)
        TuShareBase.__init__(self, "index_member", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "index_code",
            "type": "String",
            "comment": "指数代码"
        }, {
            "name": "index_name",
            "type": "String",
            "comment": "指数名称"
        }, {
            "name": "con_code",
            "type": "String",
            "comment": "成分股票代码"
        }, {
            "name": "con_name",
            "type": "String",
            "comment": "成分股票名称"
        }, {
            "name": "in_date",
            "type": "String",
            "comment": "纳入日期"
        }, {
            "name": "out_date",
            "type": "String",
            "comment": "剔除日期"
        }, {
            "name": "is_new",
            "type": "String",
            "comment": "是否最新Y是N否"
        }]

    def index_member(self, fields='index_code,con_code,in_date,out_date,is_new', **kwargs):
        """
        申万行业成分构成
        | Arguments:
        | index_code(str):   指数代码
        | is_new(str):   是否最新
        | ts_code(str):   股票代码
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         index_code(str)  指数代码 Y
         index_name(str)  指数名称 N
         con_code(str)  成分股票代码 Y
         con_name(str)  成分股票名称 N
         in_date(str)  纳入日期 Y
         out_date(str)  剔除日期 Y
         is_new(str)  是否最新Y是N否 Y
        
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
        init_args = {"index_code": "", "is_new": "", "ts_code": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.index_member with args: {}".format(kwargs))
                return self.tushare_query('index_member', fields=self.tushare_fields, **kwargs)
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


extends_attr(IndexMember, index_member_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.index_member())

    api = IndexMember(config)
    print(api.process())    # 同步增量数据
    print(api.index_member())    # 数据查询接口
