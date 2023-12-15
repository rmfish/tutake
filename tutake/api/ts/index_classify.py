"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare index_classify接口
获取申万行业分类，可以获取申万2014年版本（28个一级分类，104个二级分类，227个三级分类）和2021年本版（31个一级分类，134个二级分类，346个三级分类）列表信息
数据接口-指数-申万行业分类  https://tushare.pro/document/2?doc_id=181

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import index_classify_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareIndexClassify(TutakeTableBase):
    __tablename__ = "tushare_index_classify"
    index_code = Column(String, index=True, comment='指数代码')
    industry_name = Column(String, comment='行业名称')
    level = Column(String, index=True, comment='行业名称')
    industry_code = Column(String, comment='行业代码')
    is_pub = Column(String, comment='是否发布指数')
    parent_code = Column(String, index=True, comment='父级代码')
    src = Column(String, index=True, comment='行业分类（SW申万）')


class IndexClassify(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_index_classify"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareIndexClassify.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareIndexClassify),
                                  config.get_tutake_data_dir())

        query_fields = ['index_code', 'level', 'src', 'parent_code', 'limit', 'offset']
        self.tushare_fields = ["index_code", "industry_name", "level", "industry_code", "is_pub", "parent_code", "src"]
        entity_fields = ["index_code", "industry_name", "level", "industry_code", "is_pub", "parent_code", "src"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareIndexClassify, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "index_classify", config)
        TuShareBase.__init__(self, "index_classify", config, 2000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "index_code",
            "type": "String",
            "comment": "指数代码"
        }, {
            "name": "industry_name",
            "type": "String",
            "comment": "行业名称"
        }, {
            "name": "level",
            "type": "String",
            "comment": "行业名称"
        }, {
            "name": "industry_code",
            "type": "String",
            "comment": "行业代码"
        }, {
            "name": "is_pub",
            "type": "String",
            "comment": "是否发布指数"
        }, {
            "name": "parent_code",
            "type": "String",
            "comment": "父级代码"
        }, {
            "name": "src",
            "type": "String",
            "comment": "行业分类（SW申万）"
        }]

    def index_classify(self, fields='index_code,industry_name,level,industry_code,is_pub,parent_code', **kwargs):
        """
        获取申万行业分类，可以获取申万2014年版本（28个一级分类，104个二级分类，227个三级分类）和2021年本版（31个一级分类，134个二级分类，346个三级分类）列表信息
        | Arguments:
        | index_code(str):   指数代码
        | level(str):   行业分级（L1/L2/L3）
        | src(str):   指数来源（SW申万）
        | parent_code(str):   父级代码
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         index_code(str)  指数代码 Y
         industry_name(str)  行业名称 Y
         level(str)  行业名称 Y
         industry_code(str)  行业代码 Y
         is_pub(str)  是否发布指数 Y
         parent_code(str)  父级代码 Y
         src(str)  行业分类（SW申万） N
        
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
        init_args = {"index_code": "", "level": "", "src": "", "parent_code": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.index_classify with args: {}".format(kwargs))
                return self.tushare_query('index_classify', fields=self.tushare_fields, **kwargs)
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


extends_attr(IndexClassify, index_classify_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.index_classify())

    api = IndexClassify(config)
    print(api.process())    # 同步增量数据
    print(api.index_classify())    # 数据查询接口
