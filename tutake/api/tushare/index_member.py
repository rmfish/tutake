"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare index_member接口
申万行业成分构成
数据接口-指数-申万行业成分  https://tushare.pro/document/2?doc_id=182

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessType
from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.ggt_daily_ext import *
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_index_member.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()


class TushareIndexMember(Base):
    __tablename__ = "tushare_index_member"
    id = Column(Integer, primary_key=True, autoincrement=True)
    index_code = Column(String, index=True, comment='指数代码')
    index_name = Column(String, comment='指数名称')
    con_code = Column(String, comment='成分股票代码')
    con_name = Column(String, comment='成分股票名称')
    in_date = Column(String, comment='纳入日期')
    out_date = Column(String, comment='剔除日期')
    is_new = Column(String, index=True, comment='是否最新Y是N否')


TushareIndexMember.__table__.create(bind=engine, checkfirst=True)


class IndexMember(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = ['index_code', 'is_new', 'ts_code', 'limit', 'offset']
        entity_fields = ["index_code", "index_name", "con_code", "con_name", "in_date", "out_date", "is_new"]
        BaseDao.__init__(self, engine, session_factory, TushareIndexMember, 'tushare_index_member', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "index_member")
        self.dao = DAO()

    def index_member(self, fields='', **kwargs):
        """
        申万行业成分构成
        | Arguments:
        | index_code(str):   指数代码
        | is_new(str):   是否最新
        | ts_code(str):   股票代码
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         index_code(str)  指数代码
         index_name(str)  指数名称
         con_code(str)  成分股票代码
         con_name(str)  成分股票名称
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
        init_args = {"index_code": "", "is_new": "", "ts_code": "", "limit": "", "offset": ""}
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
            self.logger.debug("Invoke pro.index_member with args: {}".format(kwargs))
            res = self.tushare_api().index_member(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_index_member', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(IndexMember, 'default_limit', default_limit_ext)
setattr(IndexMember, 'default_cron_express', default_cron_express_ext)
setattr(IndexMember, 'default_order_by', default_order_by_ext)
setattr(IndexMember, 'prepare', prepare_ext)
setattr(IndexMember, 'tushare_parameters', tushare_parameters_ext)
setattr(IndexMember, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    api = IndexMember()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    api.process(ProcessType.INCREASE)    # 同步增量数据
    print(api.index_member())    # 数据查询接口
