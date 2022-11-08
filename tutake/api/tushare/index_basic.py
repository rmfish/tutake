"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare index_basic接口
数据接口-指数-指数基本信息  https://tushare.pro/document/2?doc_id=94

@author: rmfish
"""
import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.index_basic_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_index_basic.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.index_basic')


class TushareIndexBasic(Base):
    __tablename__ = "tushare_index_basic"
    id = Column(Integer, primary_key=True, autoincrement=True)
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


TushareIndexBasic.__table__.create(bind=engine, checkfirst=True)


class IndexBasic(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = [
            n for n in [
                'ts_code',
                'market',
                'publisher',
                'category',
                'name',
                'limit',
                'offset',
            ] if n not in ['limit', 'offset']
        ]
        entity_fields = [
            "ts_code", "name", "fullname", "market", "publisher", "index_type", "category", "base_date", "base_point",
            "list_date", "weight_rule", "desc", "exp_date"
        ]
        BaseDao.__init__(self, engine, session_factory, TushareIndexBasic, 'tushare_index_basic', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "index_basic")
        self.dao = DAO()

    def index_basic(self, fields='', **kwargs):
        """
        
        | Arguments:
        | ts_code(str):   指数代码
        | market(str):   交易所或服务商
        | publisher(str):   发布商
        | category(str):   指数类别
        | name(str):   指数名称
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS代码
         name(str)  简称
         fullname(str)  指数全称
         market(str)  市场
         publisher(str)  发布方
         index_type(str)  指数风格
         category(str)  指数类别
         base_date(str)  基期
         base_point(float)  基点
         list_date(str)  发布日期
         weight_rule(str)  加权方式
         desc(str)  描述
         exp_date(str)  终止日期
        
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
        init_args = {
            "ts_code": "",
            "market": "",
            "publisher": "",
            "category": "",
            "name": "",
            "limit": "",
            "offset": ""
        }
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
            logger.debug("Invoke pro.index_basic with args: {}".format(kwargs))
            res = self.tushare_api().index_basic(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_index_basic', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(IndexBasic, 'default_limit', default_limit_ext)
setattr(IndexBasic, 'default_order_by', default_order_by_ext)
setattr(IndexBasic, 'prepare', prepare_ext)
setattr(IndexBasic, 'tushare_parameters', tushare_parameters_ext)
setattr(IndexBasic, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)    # 显示列数
    pd.set_option('display.width', 1000)
    logger.setLevel(logging.INFO)
    api = IndexBasic()
    api.process(ProcessType.HISTORY)    # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.index_basic())    # 数据查询接口