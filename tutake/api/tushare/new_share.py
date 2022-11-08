"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare new_share接口
数据接口-沪深股票-基础数据-IPO新股上市  https://tushare.pro/document/2?doc_id=123

@author: rmfish
"""
import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.new_share_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_basic_data.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.new_share')


class TushareNewShare(Base):
    __tablename__ = "tushare_new_share"
    id = Column(Integer, primary_key=True, autoincrement=True)
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


TushareNewShare.__table__.create(bind=engine, checkfirst=True)


class NewShare(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = [n for n in [
            'start_date',
            'end_date',
            'limit',
            'offset',
        ] if n not in ['limit', 'offset']]
        entity_fields = [
            "ts_code", "sub_code", "name", "ipo_date", "issue_date", "amount", "market_amount", "price", "pe",
            "limit_amount", "funds", "ballot"
        ]
        BaseDao.__init__(self, engine, session_factory, TushareNewShare, 'tushare_new_share', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "new_share")
        self.dao = DAO()

    def new_share(self, fields='', **kwargs):
        """
        新股上市
        | Arguments:
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS股票代码
         sub_code(str)  申购代码
         name(str)  名称
         ipo_date(str)  上网发行日期
         issue_date(str)  上市日期
         amount(float)  发行总量（万股）
         market_amount(float)  上网发行总量（万股）
         price(float)  发行价格
         pe(float)  市盈率
         limit_amount(float)  个人申购上限（万股）
         funds(float)  募集资金（亿元）
         ballot(float)  中签率
        
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
        init_args = {"start_date": "", "end_date": "", "limit": "", "offset": ""}
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
            logger.debug("Invoke pro.new_share with args: {}".format(kwargs))
            res = self.tushare_api().new_share(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_new_share', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(NewShare, 'default_limit', default_limit_ext)
setattr(NewShare, 'default_order_by', default_order_by_ext)
setattr(NewShare, 'prepare', prepare_ext)
setattr(NewShare, 'tushare_parameters', tushare_parameters_ext)
setattr(NewShare, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)    # 显示列数
    pd.set_option('display.width', 1000)
    logger.setLevel(logging.INFO)
    api = NewShare()
    api.process(ProcessType.HISTORY)    # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.new_share())    # 数据查询接口
