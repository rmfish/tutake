"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_sales_vol接口
获取销售机构公募基金销售保有规模数据，本数据从2021年Q1开始公布，季度更新
数据接口-财富管理-基金销售行业数据-销售机构公募基金销售保有规模  https://tushare.pro/document/2?doc_id=266

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base
from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.fund_sales_vol_ext import *
from tutake.api.ts.tushare_dao import TushareDAO
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareFundSalesVol(Base):
    __tablename__ = "tushare_fund_sales_vol"
    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, index=True, comment='年度')
    quarter = Column(String, index=True, comment='季度')
    inst_name = Column(String, comment='销售机构')
    fund_scale = Column(Float, comment='股票+混合公募基金保有规模（亿元）')
    scale = Column(Float, comment='非货币市场公募基金保有规模(亿元)')
    rank = Column(Integer, comment='排名')


class FundSalesVol(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine(config.get_data_sqlite_driver_url('tushare_fund_sales_vol.db'),
                                    connect_args={'check_same_thread': False})
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareFundSalesVol.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['year', 'quarter', 'name', 'limit', 'offset']
        entity_fields = ["year", "quarter", "inst_name", "fund_scale", "scale", "rank"]
        TushareDAO.__init__(self, self.engine, session_factory, TushareFundSalesVol, 'tushare_fund_sales_vol',
                            query_fields, entity_fields, config)
        DataProcess.__init__(self, "fund_sales_vol", config)
        TuShareBase.__init__(self, "fund_sales_vol", config, 2000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "year",
            "type": "Integer",
            "comment": "年度"
        }, {
            "name": "quarter",
            "type": "String",
            "comment": "季度"
        }, {
            "name": "inst_name",
            "type": "String",
            "comment": "销售机构"
        }, {
            "name": "fund_scale",
            "type": "Float",
            "comment": "股票+混合公募基金保有规模（亿元）"
        }, {
            "name": "scale",
            "type": "Float",
            "comment": "非货币市场公募基金保有规模(亿元)"
        }, {
            "name": "rank",
            "type": "Integer",
            "comment": "排名"
        }]

    def fund_sales_vol(self, fields='', **kwargs):
        """
        获取销售机构公募基金销售保有规模数据，本数据从2021年Q1开始公布，季度更新
        | Arguments:
        | year(str):   年度
        | quarter(str):   季度
        | name(str):   机构名称
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         year(int)  年度
         quarter(str)  季度
         inst_name(str)  销售机构
         fund_scale(float)  股票+混合公募基金保有规模（亿元）
         scale(float)  非货币市场公募基金保有规模(亿元)
         rank(int)  排名
        
        """
        return super().query(fields, **kwargs)

    def process(self):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append)

    def fetch_and_append(self, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        init_args = {"year": "", "quarter": "", "name": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.fund_sales_vol with args: {}".format(kwargs))
                res = self.tushare_query('fund_sales_vol', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_fund_sales_vol',
                           con=self.engine,
                           if_exists='append',
                           index=False,
                           index_label=['ts_code'])
                return res
            except Exception as err:
                raise ProcessException(kwargs, err)

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(FundSalesVol, 'default_limit', default_limit_ext)
setattr(FundSalesVol, 'default_cron_express', default_cron_express_ext)
setattr(FundSalesVol, 'default_order_by', default_order_by_ext)
setattr(FundSalesVol, 'prepare', prepare_ext)
setattr(FundSalesVol, 'query_parameters', query_parameters_ext)
setattr(FundSalesVol, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fund_sales_vol())

    api = FundSalesVol(config)
    api.process()    # 同步增量数据
    print(api.fund_sales_vol())    # 数据查询接口
