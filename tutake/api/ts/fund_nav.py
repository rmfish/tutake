"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_nav接口
获取公募基金净值数据
数据接口-公募基金-基金净值  https://tushare.pro/document/2?doc_id=119

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import fund_nav_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareFundNav(TutakeTableBase):
    __tablename__ = "tushare_fund_nav"
    ts_code = Column(String, index=True, comment='TS代码')
    ann_date = Column(String, comment='公告日期')
    nav_date = Column(String, index=True, comment='截止日期')
    unit_nav = Column(Float, comment='单位净值')
    accum_nav = Column(Float, comment='累计净值')
    accum_div = Column(Float, comment='累计分红')
    net_asset = Column(Float, comment='资产净值')
    total_netasset = Column(Float, comment='合计资产净值')
    adj_nav = Column(Float, comment='复权单位净值')
    update_flag = Column(String, comment='更新标识')


class FundNav(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_fund_nav"
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
        TushareFundNav.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareFundNav)

        query_fields = ['ts_code', 'nav_date', 'offset', 'limit', 'market', 'start_date', 'end_date']
        self.tushare_fields = [
            "ts_code", "ann_date", "nav_date", "unit_nav", "accum_nav", "accum_div", "net_asset", "total_netasset",
            "adj_nav", "update_flag"
        ]
        entity_fields = [
            "ts_code", "ann_date", "nav_date", "unit_nav", "accum_nav", "accum_div", "net_asset", "total_netasset",
            "adj_nav", "update_flag"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareFundNav, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "fund_nav", config)
        TuShareBase.__init__(self, "fund_nav", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS代码"
        }, {
            "name": "ann_date",
            "type": "String",
            "comment": "公告日期"
        }, {
            "name": "nav_date",
            "type": "String",
            "comment": "截止日期"
        }, {
            "name": "unit_nav",
            "type": "Float",
            "comment": "单位净值"
        }, {
            "name": "accum_nav",
            "type": "Float",
            "comment": "累计净值"
        }, {
            "name": "accum_div",
            "type": "Float",
            "comment": "累计分红"
        }, {
            "name": "net_asset",
            "type": "Float",
            "comment": "资产净值"
        }, {
            "name": "total_netasset",
            "type": "Float",
            "comment": "合计资产净值"
        }, {
            "name": "adj_nav",
            "type": "Float",
            "comment": "复权单位净值"
        }, {
            "name": "update_flag",
            "type": "String",
            "comment": "更新标识"
        }]

    def fund_nav(self, fields='', **kwargs):
        """
        获取公募基金净值数据
        | Arguments:
        | ts_code(str):   TS基金代码
        | nav_date(str):   净值日期
        | offset(int):   
        | limit(int):   
        | market(str):   E场内O场外
        | start_date(str):   净值开始日期
        | end_date(str):   净值结束日期
        
        :return: DataFrame
         ts_code(str)  TS代码 Y
         ann_date(str)  公告日期 Y
         nav_date(str)  截止日期 Y
         unit_nav(float)  单位净值 Y
         accum_nav(float)  累计净值 Y
         accum_div(float)  累计分红 Y
         net_asset(float)  资产净值 Y
         total_netasset(float)  合计资产净值 Y
         adj_nav(float)  复权单位净值 Y
         update_flag(str)  更新标识 Y
        
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
            "nav_date": "",
            "offset": "",
            "limit": "",
            "market": "",
            "start_date": "",
            "end_date": ""
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
                self.logger.debug("Invoke pro.fund_nav with args: {}".format(kwargs))
                return self.tushare_query('fund_nav', fields=self.tushare_fields, **kwargs)
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


extends_attr(FundNav, fund_nav_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fund_nav(nav_date='20221111'))

    api = FundNav(config)
    print(api.process())    # 同步增量数据
    print(api.fund_nav(nav_date='20221111'))    # 数据查询接口
