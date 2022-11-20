"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_sales_ratio接口
获取各渠道公募基金销售保有规模占比数据，年度更新
数据接口-财富管理-基金销售行业数据-各渠道公募基金销售保有规模占比  https://tushare.pro/document/2?doc_id=265

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
from tutake.api.tushare.extends.fund_sales_ratio_ext import *
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_fund_sales_ratio.db'),
                       connect_args={'check_same_thread': False})
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()


class TushareFundSalesRatio(Base):
    __tablename__ = "tushare_fund_sales_ratio"
    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, comment='年度')
    bank = Column(Float, comment='商业银行（%）')
    sec_comp = Column(Float, comment='证券公司（%）')
    fund_comp = Column(Float, comment='基金公司直销（%）')
    indep_comp = Column(Float, comment='独立基金销售机构（%）')
    rests = Column(Float, comment='其他（%）')


TushareFundSalesRatio.__table__.create(bind=engine, checkfirst=True)


class FundSalesRatio(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = ['年份', 'limit', 'offset']
        entity_fields = ["year", "bank", "sec_comp", "fund_comp", "indep_comp", "rests"]
        BaseDao.__init__(self, engine, session_factory, TushareFundSalesRatio, 'tushare_fund_sales_ratio', query_fields,
                         entity_fields)
        DataProcess.__init__(self, "fund_sales_ratio")
        TuShareBase.__init__(self, "fund_sales_ratio")
        self.dao = DAO()

    def fund_sales_ratio(self, fields='', **kwargs):
        """
        获取各渠道公募基金销售保有规模占比数据，年度更新
        | Arguments:
        | 年份(str):   年度
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         year(int)  年度
         bank(float)  商业银行（%）
         sec_comp(float)  证券公司（%）
         fund_comp(float)  基金公司直销（%）
         indep_comp(float)  独立基金销售机构（%）
         rests(float)  其他（%）
        
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
        init_args = {"年份": "", "limit": "", "offset": ""}
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
            self.logger.debug("Invoke pro.fund_sales_ratio with args: {}".format(kwargs))
            res = self.tushare_query('fund_sales_ratio', fields=self.entity_fields, **kwargs)
            res.to_sql('tushare_fund_sales_ratio', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(FundSalesRatio, 'default_limit', default_limit_ext)
setattr(FundSalesRatio, 'default_cron_express', default_cron_express_ext)
setattr(FundSalesRatio, 'default_order_by', default_order_by_ext)
setattr(FundSalesRatio, 'prepare', prepare_ext)
setattr(FundSalesRatio, 'tushare_parameters', tushare_parameters_ext)
setattr(FundSalesRatio, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    pro = ts.pro_api(tutake_config.get_tushare_token())
    print(pro.fund_sales_ratio(offset=5))

    api = FundSalesRatio()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    api.process(ProcessType.INCREASE)    # 同步增量数据
    print(api.fund_sales_ratio())    # 数据查询接口
