"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare dividend接口
数据接口-沪深股票-财务数据-分红送股数据  https://tushare.pro/document/2?doc_id=103

@author: rmfish
"""
import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.dividend_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_dividend.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.dividend')


class TushareDividend(Base):
    __tablename__ = "tushare_dividend"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='TS代码')
    end_date = Column(String, index=True, comment='分送年度')
    ann_date = Column(String, index=True, comment='预案公告日（董事会）')
    div_proc = Column(String, comment='实施进度')
    stk_div = Column(Float, comment='每股送转')
    stk_bo_rate = Column(Float, comment='每股送股比例')
    stk_co_rate = Column(Float, comment='每股转增比例')
    cash_div = Column(Float, comment='每股分红（税后）')
    cash_div_tax = Column(Float, comment='每股分红（税前）')
    record_date = Column(String, index=True, comment='股权登记日')
    ex_date = Column(String, index=True, comment='除权除息日')
    pay_date = Column(String, comment='派息日')
    div_listdate = Column(String, comment='红股上市日')
    imp_ann_date = Column(String, index=True, comment='实施公告日')
    base_date = Column(String, comment='基准日')
    base_share = Column(Float, comment='实施基准股本（万）')
    update_flag = Column(String, comment='是否变更过（1表示变更）')


TushareDividend.__table__.create(bind=engine, checkfirst=True)


class Dividend(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = ['ts_code', 'ann_date', 'end_date', 'record_date', 'ex_date', 'imp_ann_date', 'limit', 'offset']
        entity_fields = [
            "ts_code", "end_date", "ann_date", "div_proc", "stk_div", "stk_bo_rate", "stk_co_rate", "cash_div",
            "cash_div_tax", "record_date", "ex_date", "pay_date", "div_listdate", "imp_ann_date", "base_date",
            "base_share", "update_flag"
        ]
        BaseDao.__init__(self, engine, session_factory, TushareDividend, 'tushare_dividend', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "dividend")
        self.dao = DAO()

    def dividend(self, fields='', **kwargs):
        """
        
        | Arguments:
        | ts_code(str):   TS代码
        | ann_date(str):   公告日
        | end_date(str):   分红年度
        | record_date(str):   股权登记日期
        | ex_date(str):   除权除息日
        | imp_ann_date(str):   除权除息日
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS代码
         end_date(str)  分送年度
         ann_date(str)  预案公告日（董事会）
         div_proc(str)  实施进度
         stk_div(float)  每股送转
         stk_bo_rate(float)  每股送股比例
         stk_co_rate(float)  每股转增比例
         cash_div(float)  每股分红（税后）
         cash_div_tax(float)  每股分红（税前）
         record_date(str)  股权登记日
         ex_date(str)  除权除息日
         pay_date(str)  派息日
         div_listdate(str)  红股上市日
         imp_ann_date(str)  实施公告日
         base_date(str)  基准日
         base_share(float)  实施基准股本（万）
         update_flag(str)  是否变更过（1表示变更）
        
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
            "ann_date": "",
            "end_date": "",
            "record_date": "",
            "ex_date": "",
            "imp_ann_date": "",
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
            logger.debug("Invoke pro.dividend with args: {}".format(kwargs))
            res = self.tushare_api().dividend(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_dividend', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(Dividend, 'default_limit', default_limit_ext)
setattr(Dividend, 'default_order_by', default_order_by_ext)
setattr(Dividend, 'prepare', prepare_ext)
setattr(Dividend, 'tushare_parameters', tushare_parameters_ext)
setattr(Dividend, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)    # 显示列数
    pd.set_option('display.width', 1000)
    logger.setLevel(logging.INFO)
    api = Dividend()
    api.process(ProcessType.HISTORY)    # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.dividend())    # 数据查询接口
