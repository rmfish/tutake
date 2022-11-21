"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_share接口
获取基金规模数据，包含上海和深圳ETF基金
数据接口-公募基金-基金规模  https://tushare.pro/document/2?doc_id=207

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
from tutake.api.tushare.extends.fund_share_ext import *
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_fund_share.db'),
                       connect_args={'check_same_thread': False})
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()


class TushareFundShare(Base):
    __tablename__ = "tushare_fund_share"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='基金代码')
    trade_date = Column(String, index=True, comment='交易（变动）日期')
    fd_share = Column(Float, comment='基金份额（万）')
    total_share = Column(Float, comment='合计份额（万）')
    fund_type = Column(String, index=True, comment='基金类型')
    market = Column(String, index=True, comment='市场')


TushareFundShare.__table__.create(bind=engine, checkfirst=True)


class FundShare(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'market', 'fund_type', 'limit', 'offset']
        entity_fields = ["ts_code", "trade_date", "fd_share", "total_share", "fund_type", "market"]
        BaseDao.__init__(self, engine, session_factory, TushareFundShare, 'tushare_fund_share', query_fields,
                         entity_fields)
        DataProcess.__init__(self, "fund_share")
        TuShareBase.__init__(self, "fund_share")
        self.dao = DAO()

    def fund_share(self, fields='', **kwargs):
        """
        获取基金规模数据，包含上海和深圳ETF基金
        | Arguments:
        | ts_code(str):   TS基金代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | market(str):   市场：SH/SZ
        | fund_type(str):   类型
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  基金代码
         trade_date(str)  交易（变动）日期
         fd_share(float)  基金份额（万）
         total_share(float)  合计份额（万）
         fund_type(str)  基金类型
         market(str)  市场
        
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
            "trade_date": "",
            "start_date": "",
            "end_date": "",
            "market": "",
            "fund_type": "",
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

        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            self.logger.debug("Invoke pro.fund_share with args: {}".format(kwargs))
            res = self.tushare_query('fund_share', fields=self.entity_fields, **kwargs)
            res.to_sql('tushare_fund_share', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(FundShare, 'default_limit', default_limit_ext)
setattr(FundShare, 'default_cron_express', default_cron_express_ext)
setattr(FundShare, 'default_order_by', default_order_by_ext)
setattr(FundShare, 'prepare', prepare_ext)
setattr(FundShare, 'tushare_parameters', tushare_parameters_ext)
setattr(FundShare, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    pro = ts.pro_api(tutake_config.get_tushare_token())
    print(pro.fund_share())

    api = FundShare()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    api.process(ProcessType.INCREASE)    # 同步增量数据
    print(api.fund_share())    # 数据查询接口
