"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare hs_const接口
获取沪股通、深股通成分数据
数据接口-沪深股票-基础数据-沪深股通成分股  https://tushare.pro/document/2?doc_id=104

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.process import DataProcess
from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.hs_const_ext import *
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_basic_data.db'),
                       connect_args={'check_same_thread': False})
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()


class TushareHsConst(Base):
    __tablename__ = "tushare_hs_const"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, comment='TS代码')
    hs_type = Column(String, index=True, comment='沪深港通类型SH沪SZ深')
    in_date = Column(String, comment='纳入日期')
    out_date = Column(String, comment='剔除日期')
    is_new = Column(String, index=True, comment='是否最新')


TushareHsConst.__table__.create(bind=engine, checkfirst=True)


class HsConst(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = ['hs_type', 'is_new', 'limit', 'offset']
        entity_fields = ["ts_code", "hs_type", "in_date", "out_date", "is_new"]
        BaseDao.__init__(self, engine, session_factory, TushareHsConst, 'tushare_hs_const', query_fields, entity_fields)
        DataProcess.__init__(self, "hs_const")
        TuShareBase.__init__(self, "hs_const")
        self.dao = DAO()

    def hs_const(self, fields='', **kwargs):
        """
        获取沪股通、深股通成分数据
        | Arguments:
        | hs_type(str): required  类型SH沪股通SZ深股通
        | is_new(str):   是否最新1最新0不是
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS代码
         hs_type(str)  沪深港通类型SH沪SZ深
         in_date(str)  纳入日期
         out_date(str)  剔除日期
         is_new(str)  是否最新
        
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
        init_args = {"hs_type": "", "is_new": "", "limit": "", "offset": ""}
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
            kwargs['offset'] = str(offset_val)
            self.logger.debug("Invoke pro.hs_const with args: {}".format(kwargs))
            res = self.tushare_query('hs_const', fields=self.entity_fields, **kwargs)
            res.to_sql('tushare_hs_const', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(HsConst, 'default_limit', default_limit_ext)
setattr(HsConst, 'default_cron_express', default_cron_express_ext)
setattr(HsConst, 'default_order_by', default_order_by_ext)
setattr(HsConst, 'prepare', prepare_ext)
setattr(HsConst, 'tushare_parameters', tushare_parameters_ext)
setattr(HsConst, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    pro = ts.pro_api(tutake_config.get_tushare_token())
    print(pro.hs_const())

    api = HsConst()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    api.process(ProcessType.INCREASE)    # 同步增量数据
    print(api.hs_const())    # 数据查询接口
