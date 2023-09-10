"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare stock_mx接口
获取小佩数据动量因子数据，可以获取股票动能评级数据，包括最新及过去历史数据
数据接口  https://tushare.pro/document/2?doc_id=300

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.stock_mx_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareStockMx(Base):
    __tablename__ = "tushare_stock_mx"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='股票代码')
    trade_date = Column(String, index=True, comment='交易日期')
    mx_grade = Column(
        Integer,
        comment=
        '动能评级，综合动能指标后分成4个评等，1(高)、2(中)、3(低)、4(弱)。高：周、月、季、半年趋势方向一致，整体看多；中：周、月、季、半年趋势方向不一致，但整体偏多；低：周、月、季、半年趋势方向不一致，但整体偏多；弱：周、月、季、半年趋势方向一致，整体看空'
    )
    com_stock = Column(String, comment='行业轮动指标')
    evd_v = Column(String, comment='速度指标，衡量该个股股价变化的速度')
    zt_sum_z = Column(String, comment='极值，短期均线离差值')
    wma250_z = Column(String, comment='偏离指标，中期均线偏离度指标')


class StockMx(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_stock_mx"
        self.database = 'tushare_xiaopei.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareStockMx.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'offset', 'limit']
        self.tushare_fields = ["ts_code", "trade_date", "mx_grade", "com_stock", "evd_v", "zt_sum_z", "wma250_z"]
        entity_fields = ["ts_code", "trade_date", "mx_grade", "com_stock", "evd_v", "zt_sum_z", "wma250_z"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareStockMx, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "stock_mx", config)
        TuShareBase.__init__(self, "stock_mx", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "股票代码"
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name":
                "mx_grade",
            "type":
                "Integer",
            "comment":
                "动能评级，综合动能指标后分成4个评等，1(高)、2(中)、3(低)、4(弱)。高：周、月、季、半年趋势方向一致，整体看多；中：周、月、季、半年趋势方向不一致，但整体偏多；低：周、月、季、半年趋势方向不一致，但整体偏多；弱：周、月、季、半年趋势方向一致，整体看空"
        }, {
            "name": "com_stock",
            "type": "String",
            "comment": "行业轮动指标"
        }, {
            "name": "evd_v",
            "type": "String",
            "comment": "速度指标，衡量该个股股价变化的速度"
        }, {
            "name": "zt_sum_z",
            "type": "String",
            "comment": "极值，短期均线离差值"
        }, {
            "name": "wma250_z",
            "type": "String",
            "comment": "偏离指标，中期均线偏离度指标"
        }]

    def stock_mx(self, fields='', **kwargs):
        """
        获取小佩数据动量因子数据，可以获取股票动能评级数据，包括最新及过去历史数据
        | Arguments:
        | ts_code(str):   股票代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | offset(str):   开始行数
        | limit(str):   最大行数
        
        :return: DataFrame
         ts_code(str)  股票代码 Y
         trade_date(str)  交易日期 Y
         mx_grade(int)  动能评级，综合动能指标后分成4个评等，1(高)、2(中)、3(低)、4(弱)。高：周、月、季、半年趋势方向一致，整体看多；中：周、月、季、半年趋势方向不一致，但整体偏多；低：周、月、季、半年趋势方向不一致，但整体偏多；弱：周、月、季、半年趋势方向一致，整体看空 Y
         com_stock(str)  行业轮动指标 Y
         evd_v(str)  速度指标，衡量该个股股价变化的速度 Y
         zt_sum_z(str)  极值，短期均线离差值 Y
         wma250_z(str)  偏离指标，中期均线偏离度指标 Y
        
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
                self.logger.debug("Invoke pro.stock_mx with args: {}".format(kwargs))
                return self.tushare_query('stock_mx', fields=self.tushare_fields, **kwargs)
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


setattr(StockMx, 'default_limit', default_limit_ext)
setattr(StockMx, 'default_cron_express', default_cron_express_ext)
setattr(StockMx, 'default_order_by', default_order_by_ext)
setattr(StockMx, 'prepare', prepare_ext)
setattr(StockMx, 'query_parameters', query_parameters_ext)
setattr(StockMx, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.stock_mx())

    api = StockMx(config)
    print(api.process())    # 同步增量数据
    print(api.stock_mx())    # 数据查询接口
