"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare ths_member接口
数据接口-指数-同花顺概念和行业指数成分  https://tushare.pro/document/2?doc_id=261

@author: rmfish
"""
import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.ths_member_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_ths_member.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.ths_member')


class TushareThsMember(Base):
    __tablename__ = "tushare_ths_member"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='指数代码')
    code = Column(String, index=True, comment='股票代码')
    name = Column(String, comment='股票名称')
    weight = Column(Float, comment='权重')
    in_date = Column(String, comment='纳入日期')
    out_date = Column(String, comment='剔除日期')
    is_new = Column(String, comment='是否最新Y是N否')


TushareThsMember.__table__.create(bind=engine, checkfirst=True)


class ThsMember(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = [
            'ts_code',
            'code',
            'limit',
            'offset',
        ]
        entity_fields = ["ts_code", "code", "name", "weight", "in_date", "out_date", "is_new"]
        BaseDao.__init__(self, engine, session_factory, TushareThsMember, 'tushare_ths_member', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "ths_member")
        self.dao = DAO()

    def ths_member(self, fields='', **kwargs):
        """
        
        | Arguments:
        | ts_code(str):   板块指数代码
        | code(str):   股票代码
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  指数代码
         code(str)  股票代码
         name(str)  股票名称
         weight(float)  权重
         in_date(str)  纳入日期
         out_date(str)  剔除日期
         is_new(str)  是否最新Y是N否
        
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
        init_args = {"ts_code": "", "code": "", "limit": "", "offset": ""}
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
            logger.debug("Invoke pro.ths_member with args: {}".format(kwargs))
            res = self.tushare_api().ths_member(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_ths_member', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(ThsMember, 'default_limit', default_limit_ext)
setattr(ThsMember, 'default_order_by', default_order_by_ext)
setattr(ThsMember, 'prepare', prepare_ext)
setattr(ThsMember, 'tushare_parameters', tushare_parameters_ext)
setattr(ThsMember, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)    # 显示列数
    pd.set_option('display.width', 1000)
    logger.setLevel(logging.INFO)
    api = ThsMember()
    api.process(ProcessType.HISTORY)    # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.ths_member())    # 数据查询接口
