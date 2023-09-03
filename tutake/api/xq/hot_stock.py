"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Xueqiu hot_stock接口
热门的股票ETF数据 热门类型（etf_query: 热门ETF, etf_1h:1小时热门ETF, etf_follow:热门关注ETF, stock_query:热门股票, stock_increase: 热门股票飙升, stock_comment:热评股票, stock_follow：热门关注股票, cube:热门组合）

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Boolean, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records, BaseDao
from tutake.api.process import DataProcess, ProcessException
from tutake.api.xq.hot_stock_ext import *
from tutake.api.xq.xueqiu_base import XueQiuBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class XueqiuHotStock(Base):
    __tablename__ = "xueqiu_hot_stock"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='股票代码')
    trade_date = Column(String, index=True, comment='交易日期')
    hot_type = Column(
        String,
        index=True,
        comment=
        '热门类型（etf_query: 热门ETF, etf_1h:1小时热门ETF, etf_follow:热门关注ETF, stock_query:热门股票, stock_increase: 热门股票飙升, stock_comment:热评股票, stock_follow：热门关注股票, cube:热门组合）'
    )
    name = Column(String, comment='股票名称')
    value = Column(Float, comment='数值')
    increment = Column(Float, comment='数值增加或减少')
    rank = Column(Integer, comment='排名')


class HotStock(BaseDao, XueQiuBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "xueqiu_hot_stock"
        self.database = 'xueqiu.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_engine(self.database_url,
                                    connect_args={
                                        'check_same_thread': False,
                                        'timeout': config.get_sqlite_timeout()
                                    })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        XueqiuHotStock.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'hot_type', 'trade_date', 'start_date', 'end_date', 'offset', 'limit']
        entity_fields = ["ts_code", "trade_date", "hot_type", "name", "value", "increment", "rank"]
        BaseDao.__init__(self, self.engine, session_factory, XueqiuHotStock, self.database, self.table_name,
                         query_fields, entity_fields, config)
        DataProcess.__init__(self, "hot_stock", config)
        XueQiuBase.__init__(self, "hot_stock", config)

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
                "hot_type",
            "type":
                "String",
            "comment":
                "热门类型（etf_query: 热门ETF, etf_1h:1小时热门ETF, etf_follow:热门关注ETF, stock_query:热门股票, stock_increase: 热门股票飙升, stock_comment:热评股票, stock_follow：热门关注股票, cube:热门组合）"
        }, {
            "name": "name",
            "type": "String",
            "comment": "股票名称"
        }, {
            "name": "value",
            "type": "Float",
            "comment": "数值"
        }, {
            "name": "increment",
            "type": "Float",
            "comment": "数值增加或减少"
        }, {
            "name": "rank",
            "type": "Integer",
            "comment": "排名"
        }]

    def hot_stock(self, fields='', **kwargs):
        """
        热门的股票ETF数据 热门类型（etf_query: 热门ETF, etf_1h:1小时热门ETF, etf_follow:热门关注ETF, stock_query:热门股票, stock_increase: 热门股票飙升, stock_comment:热评股票, stock_follow：热门关注股票, cube:热门组合）
        | Arguments:
        | ts_code(str):   股票代码
        | hot_type(str): required  热门类型
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | offset(str):   开始行数
        | limit(str):   最大行数
        
        :return: DataFrame
         ts_code(str)  股票代码
         trade_date(str)  交易日期
         hot_type(str)  热门类型（etf_query: 热门ETF, etf_1h:1小时热门ETF, etf_follow:热门关注ETF, stock_query:热门股票, stock_increase: 热门股票飙升, stock_comment:热评股票, stock_follow：热门关注股票, cube:热门组合）
         name(str)  股票名称
         value(float)  数值
         increment(float)  数值增加或减少
         rank(int)  排名
        
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
        init_args = {
            "ts_code": "",
            "hot_type": "",
            "trade_date": "",
            "start_date": "",
            "end_date": "",
            "offset": "",
            "limit": ""
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
                self.logger.debug("Invoke pro.hot_stock with args: {}".format(kwargs))
                res = self.hot_stock_request(fields=self.entity_fields, **kwargs)
                res.to_sql('xueqiu_hot_stock',
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


setattr(HotStock, 'default_limit', default_limit_ext)
setattr(HotStock, 'default_cron_express', default_cron_express_ext)
setattr(HotStock, 'default_order_by', default_order_by_ext)
setattr(HotStock, 'prepare', prepare_ext)
setattr(HotStock, 'query_parameters', query_parameters_ext)
setattr(HotStock, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())

    api = HotStock(config)
    api.process()    # 同步增量数据
    print(api.hot_stock())    # 数据查询接口
    print(api.sql("select distinct(trade_date) from {table}"))
