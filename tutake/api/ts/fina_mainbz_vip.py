"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fina_mainbz_vip接口
获得上市公司主营业务构成，分地区和产品两种方式
数据接口-沪深股票-财务数据-主营业务构成  https://tushare.pro/document/2?doc_id=81

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import fina_mainbz_vip_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareFinaMainbzVip(TutakeTableBase):
    __tablename__ = "tushare_fina_mainbz_vip"
    ts_code = Column(String, index=True, comment='TS代码')
    end_date = Column(String, index=True, comment='报告期')
    bz_item = Column(String, comment='主营业务项目')
    bz_code = Column(String, comment='项目代码')
    bz_sales = Column(Float, comment='主营业务收入(元)')
    bz_profit = Column(Float, comment='主营业务利润(元)')
    bz_cost = Column(Float, comment='主营业务成本(元)')
    curr_type = Column(String, comment='货币代码')
    update_flag = Column(String, comment='是否更新')


class FinaMainbzVip(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_fina_mainbz_vip"
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
        TushareFinaMainbzVip.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareFinaMainbzVip)

        query_fields = ['ts_code', 'period', 'type', 'start_date', 'end_date', 'is_publish', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "end_date", "bz_item", "bz_code", "bz_sales", "bz_profit", "bz_cost", "curr_type", "update_flag"
        ]
        entity_fields = [
            "ts_code", "end_date", "bz_item", "bz_code", "bz_sales", "bz_profit", "bz_cost", "curr_type", "update_flag"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareFinaMainbzVip, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "fina_mainbz_vip", config)
        TuShareBase.__init__(self, "fina_mainbz_vip", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS代码"
        }, {
            "name": "end_date",
            "type": "String",
            "comment": "报告期"
        }, {
            "name": "bz_item",
            "type": "String",
            "comment": "主营业务项目"
        }, {
            "name": "bz_code",
            "type": "String",
            "comment": "项目代码"
        }, {
            "name": "bz_sales",
            "type": "Float",
            "comment": "主营业务收入(元)"
        }, {
            "name": "bz_profit",
            "type": "Float",
            "comment": "主营业务利润(元)"
        }, {
            "name": "bz_cost",
            "type": "Float",
            "comment": "主营业务成本(元)"
        }, {
            "name": "curr_type",
            "type": "String",
            "comment": "货币代码"
        }, {
            "name": "update_flag",
            "type": "String",
            "comment": "是否更新"
        }]

    def fina_mainbz_vip(self, fields='ts_code,end_date,bz_item,bz_sales,bz_profit,bz_cost,curr_type', **kwargs):
        """
        获得上市公司主营业务构成，分地区和产品两种方式
        | Arguments:
        | ts_code(str): required  股票代码
        | period(str):   报告期
        | type(str):   类型：P按产品 D按地区
        | start_date(str):   报告期开始日期
        | end_date(str):   报告期结束日期
        | is_publish(str):   
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS代码 Y
         end_date(str)  报告期 Y
         bz_item(str)  主营业务项目 Y
         bz_code(str)  项目代码 N
         bz_sales(float)  主营业务收入(元) Y
         bz_profit(float)  主营业务利润(元) Y
         bz_cost(float)  主营业务成本(元) Y
         curr_type(str)  货币代码 Y
         update_flag(str)  是否更新 N
        
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
        init_args = {
            "ts_code": "",
            "period": "",
            "type": "",
            "start_date": "",
            "end_date": "",
            "is_publish": "",
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
            try:
                kwargs['offset'] = str(offset_val)
                self.logger.debug("Invoke pro.fina_mainbz_vip with args: {}".format(kwargs))
                return self.tushare_query('fina_mainbz_vip', fields=self.tushare_fields, **kwargs)
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


extends_attr(FinaMainbzVip, fina_mainbz_vip_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fina_mainbz_vip())

    api = FinaMainbzVip(config)
    print(api.process())    # 同步增量数据
    print(api.fina_mainbz_vip())    # 数据查询接口
