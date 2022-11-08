"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare index_classify接口
数据接口-指数-申万行业分类  https://tushare.pro/document/2?doc_id=181

@author: rmfish
"""
import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.index_classify_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_index_classify.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.index_classify')


class TushareIndexClassify(Base):
    __tablename__ = "tushare_index_classify"
    id = Column(Integer, primary_key=True, autoincrement=True)
    index_code = Column(String, index=True, comment='指数代码')
    industry_name = Column(String, comment='行业名称')
    level = Column(String, index=True, comment='行业名称')
    industry_code = Column(String, comment='行业代码')
    is_pub = Column(String, comment='是否发布指数')
    parent_code = Column(String, index=True, comment='父级代码')
    src = Column(String, index=True, comment='行业分类（SW申万）')


TushareIndexClassify.__table__.create(bind=engine, checkfirst=True)


class IndexClassify(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = [
            n for n in [
                'index_code',
                'level',
                'src',
                'parent_code',
                'limit',
                'offset',
            ] if n not in ['limit', 'offset']
        ]
        entity_fields = ["index_code", "industry_name", "level", "industry_code", "is_pub", "parent_code", "src"]
        BaseDao.__init__(self, engine, session_factory, TushareIndexClassify, 'tushare_index_classify', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "index_classify")
        self.dao = DAO()

    def index_classify(self, fields='', **kwargs):
        """
        申万行业分类
        | Arguments:
        | index_code(str):   指数代码
        | level(str):   行业分级（L1/L2/L3）
        | src(str):   指数来源（SW申万）
        | parent_code(str):   父级代码
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         index_code(str)  指数代码
         industry_name(str)  行业名称
         level(str)  行业名称
         industry_code(str)  行业代码
         is_pub(str)  是否发布指数
         parent_code(str)  父级代码
         src(str)  行业分类（SW申万）
        
        """
        return super().query(fields, **kwargs)

    def process(self, process_type: ProcessType):
        """
        同步历史数据
        :return:
        """
        return super()._process(process_type, self.fetch_and_append)

    def fetch_and_append(self, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        init_args = {"index_code": "", "level": "", "src": "", "parent_code": "", "limit": "", "offset": ""}
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

        @sleep(timeout=61, time_append=60, retry=20, match="^抱歉，您每分钟最多访问该接口")
        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            logger.debug("Invoke pro.index_classify with args: {}".format(kwargs))
            res = self.tushare_api().index_classify(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_index_classify', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(IndexClassify, 'default_limit', default_limit_ext)
setattr(IndexClassify, 'default_order_by', default_order_by_ext)
setattr(IndexClassify, 'prepare', prepare_ext)
setattr(IndexClassify, 'tushare_parameters', tushare_parameters_ext)
setattr(IndexClassify, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)    # 显示列数
    pd.set_option('display.width', 1000)
    logger.setLevel(logging.INFO)
    api = IndexClassify()
    api.process(ProcessType.HISTORY)    # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.index_classify())    # 数据查询接口
