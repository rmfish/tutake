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
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.fund_sales_ratio_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareFundSalesRatio(Base):
    __tablename__ = "tushare_fund_sales_ratio"
    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, comment='年度')
    bank = Column(Float, comment='商业银行（%）')
    sec_comp = Column(Float, comment='证券公司（%）')
    fund_comp = Column(Float, comment='基金公司直销（%）')
    indep_comp = Column(Float, comment='独立基金销售机构（%）')
    rests = Column(Float, comment='其他（%）')


class FundSalesRatio(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_fund_sales_ratio"
        self.database = 'tushare_fund.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareFundSalesRatio.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['年份', 'limit', 'offset']
        entity_fields = ["year", "bank", "sec_comp", "fund_comp", "indep_comp", "rests"]
        TushareDAO.__init__(self, self.engine, session_factory, TushareFundSalesRatio, self.database, self.table_name,
                            query_fields, entity_fields, config)
        DataProcess.__init__(self, "fund_sales_ratio", config)
        TuShareBase.__init__(self, "fund_sales_ratio", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "year",
            "type": "Integer",
            "comment": "年度"
        }, {
            "name": "bank",
            "type": "Float",
            "comment": "商业银行（%）"
        }, {
            "name": "sec_comp",
            "type": "Float",
            "comment": "证券公司（%）"
        }, {
            "name": "fund_comp",
            "type": "Float",
            "comment": "基金公司直销（%）"
        }, {
            "name": "indep_comp",
            "type": "Float",
            "comment": "独立基金销售机构（%）"
        }, {
            "name": "rests",
            "type": "Float",
            "comment": "其他（%）"
        }]

    def fund_sales_ratio(self, fields='', **kwargs):
        """
        获取各渠道公募基金销售保有规模占比数据，年度更新
        | Arguments:
        | 年份(str):   年度
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         year(int)  年度 Y
         bank(float)  商业银行（%） Y
         sec_comp(float)  证券公司（%） Y
         fund_comp(float)  基金公司直销（%） Y
         indep_comp(float)  独立基金销售机构（%） Y
         rests(float)  其他（%） Y
        
        """
        return super().query(fields, **kwargs)

    def process(self):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append, BatchWriter(self.engine, self.table_name))

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
            try:
                kwargs['offset'] = str(offset_val)
                self.logger.debug("Invoke pro.fund_sales_ratio with args: {}".format(kwargs))
                return self.tushare_query('fund_sales_ratio', fields=self.entity_fields, **kwargs)
            except Exception as err:
                raise ProcessException(kwargs, err)

        res = fetch_save(offset)
        size = res.size()
        offset += size
        while kwargs['limit'] != "" and size == int(kwargs['limit']):
            result = fetch_save(offset)
            size = result.size()
            offset += size
            res.append(result)
        return res


setattr(FundSalesRatio, 'default_limit', default_limit_ext)
setattr(FundSalesRatio, 'default_cron_express', default_cron_express_ext)
setattr(FundSalesRatio, 'default_order_by', default_order_by_ext)
setattr(FundSalesRatio, 'prepare', prepare_ext)
setattr(FundSalesRatio, 'query_parameters', query_parameters_ext)
setattr(FundSalesRatio, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fund_sales_ratio())

    api = FundSalesRatio(config)
    api.process()    # 同步增量数据
    print(api.fund_sales_ratio())    # 数据查询接口
