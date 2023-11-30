"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_sales_vol接口
获取销售机构公募基金销售保有规模数据，本数据从2021年Q1开始公布，季度更新
数据接口-财富管理-基金销售行业数据-销售机构公募基金销售保有规模  https://tushare.pro/document/2?doc_id=266

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import fund_sales_vol_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareFundSalesVol(TutakeTableBase):
    __tablename__ = "tushare_fund_sales_vol"
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
        self.table_name = "tushare_fund_sales_vol"
        self.database = 'tutake.duckdb'
        self.database_dir = config.get_tutake_data_dir()
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareFundSalesVol.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareFundSalesVol)

        query_fields = ['year', 'quarter', 'name', 'limit', 'offset']
        self.tushare_fields = ["year", "quarter", "inst_name", "fund_scale", "scale", "rank"]
        entity_fields = ["year", "quarter", "inst_name", "fund_scale", "scale", "rank"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareFundSalesVol, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
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
         year(int)  年度 Y
         quarter(str)  季度 Y
         inst_name(str)  销售机构 Y
         fund_scale(float)  股票+混合公募基金保有规模（亿元） Y
         scale(float)  非货币市场公募基金保有规模(亿元) Y
         rank(int)  排名 Y
        
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append,
                                BatchWriter(self.engine, self.table_name, self.schema, self.database_dir), **kwargs)

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
                return self.tushare_query('fund_sales_vol', fields=self.tushare_fields, **kwargs)
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
        res.fields = self.entity_fields
        return res


extends_attr(FundSalesVol, fund_sales_vol_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fund_sales_vol())

    api = FundSalesVol(config)
    print(api.process())    # 同步增量数据
    print(api.fund_sales_vol())    # 数据查询接口
