"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare moneyflow_hsgt接口
数据接口-沪深股票-行情数据-沪深港通资金流向  https://tushare.pro/document/2?doc_id=47

@author: rmfish
"""
import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.moneyflow_hsgt_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_moneyflow_hsgt.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.moneyflow_hsgt')


class TushareMoneyflowHsgt(Base):
    __tablename__ = "tushare_moneyflow_hsgt"
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String, index=True, comment='交易日期')
    ggt_ss = Column(String, comment='港股通（上海）')
    ggt_sz = Column(String, comment='港股通（深圳）')
    hgt = Column(String, comment='沪股通')
    sgt = Column(String, comment='深股通')
    north_money = Column(String, comment='北向资金')
    south_money = Column(String, comment='南向资金')


TushareMoneyflowHsgt.__table__.create(bind=engine, checkfirst=True)


class MoneyflowHsgt(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = [
            n for n in [
                'trade_date',
                'start_date',
                'end_date',
                'limit',
                'offset',
            ] if n not in ['limit', 'offset']
        ]
        entity_fields = ["trade_date", "ggt_ss", "ggt_sz", "hgt", "sgt", "north_money", "south_money"]
        BaseDao.__init__(self, engine, session_factory, TushareMoneyflowHsgt, 'tushare_moneyflow_hsgt', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "moneyflow_hsgt")
        self.dao = DAO()

    def moneyflow_hsgt(self, fields='', **kwargs):
        """
        
        | Arguments:
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  交易日期
         ggt_ss(str)  港股通（上海）
         ggt_sz(str)  港股通（深圳）
         hgt(str)  沪股通
         sgt(str)  深股通
         north_money(str)  北向资金
         south_money(str)  南向资金
        
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
        init_args = {"trade_date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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
            logger.debug("Invoke pro.moneyflow_hsgt with args: {}".format(kwargs))
            res = self.tushare_api().moneyflow_hsgt(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_moneyflow_hsgt', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(MoneyflowHsgt, 'default_limit', default_limit_ext)
setattr(MoneyflowHsgt, 'default_order_by', default_order_by_ext)
setattr(MoneyflowHsgt, 'prepare', prepare_ext)
setattr(MoneyflowHsgt, 'tushare_parameters', tushare_parameters_ext)
setattr(MoneyflowHsgt, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)    # 显示列数
    pd.set_option('display.width', 1000)
    logger.setLevel(logging.INFO)
    api = MoneyflowHsgt()
    api.process(ProcessType.HISTORY)    # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.moneyflow_hsgt())    # 数据查询接口