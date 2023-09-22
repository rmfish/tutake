"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_adj接口
获取基金复权因子，用于计算基金复权行情，每日17点更新
数据接口-公募基金-复权因子  https://tushare.pro/document/2?doc_id=199

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.fund_adj_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareFundAdj(Base):
    __tablename__ = "tushare_fund_adj"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='ts基金代码')
    trade_date = Column(String, index=True, comment='交易日期')
    adj_factor = Column(Float, comment='复权因子')
    discount_rate = Column(Float, comment='贴水率（%）')


class FundAdj(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_fund_adj"
        self.database = 'tushare_fund.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareFundAdj.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'offset', 'limit']
        self.tushare_fields = ["ts_code", "trade_date", "adj_factor", "discount_rate"]
        entity_fields = ["ts_code", "trade_date", "adj_factor", "discount_rate"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareFundAdj, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "fund_adj", config)
        TuShareBase.__init__(self, "fund_adj", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "ts基金代码"
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "adj_factor",
            "type": "Float",
            "comment": "复权因子"
        }, {
            "name": "discount_rate",
            "type": "Float",
            "comment": "贴水率（%）"
        }]

    def fund_adj(self, fields='ts_code,trade_date,adj_factor', **kwargs):
        """
        获取基金复权因子，用于计算基金复权行情，每日17点更新
        | Arguments:
        | ts_code(str):   TS基金代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | offset(str):   开始行数
        | limit(str):   最大行数
        
        :return: DataFrame
         ts_code(str)  ts基金代码 Y
         trade_date(str)  交易日期 Y
         adj_factor(float)  复权因子 Y
         discount_rate(float)  贴水率（%） N
        
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append, BatchWriter(self.engine, self.table_name), **kwargs)

    def fetch_and_append(self, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        init_args = {"ts_code": "", "trade_date": "", "start_date": "", "end_date": "", "offset": "", "limit": ""}
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
                self.logger.debug("Invoke pro.fund_adj with args: {}".format(kwargs))
                return self.tushare_query('fund_adj', fields=self.tushare_fields, **kwargs)
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


setattr(FundAdj, 'default_limit', default_limit_ext)
setattr(FundAdj, 'default_cron_express', default_cron_express_ext)
setattr(FundAdj, 'default_order_by', default_order_by_ext)
setattr(FundAdj, 'prepare', prepare_ext)
setattr(FundAdj, 'query_parameters', query_parameters_ext)
setattr(FundAdj, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fund_adj())

    api = FundAdj(config)
    print(api.process())    # 同步增量数据
    print(api.fund_adj())    # 数据查询接口
