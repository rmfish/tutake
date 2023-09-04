"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Xueqiu index_valuation接口
指数估值

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Boolean, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records, BaseDao
from tutake.api.process import DataProcess, ProcessException
from tutake.api.xq.index_valuation_ext import *
from tutake.api.xq.xueqiu_base import XueQiuBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class XueqiuIndexValuation(Base):
    __tablename__ = "xueqiu_index_valuation"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='股票代码')
    trade_date = Column(String, index=True, comment='交易日期')
    name = Column(String, comment='名称')
    ttype = Column(Integer, comment='类型')
    pe = Column(Float, comment='pe')
    pe_percentile = Column(Float, comment='pe百分位')
    peg = Column(Float, comment='预测peg')
    pb_percentile = Column(Float, comment='pb百分位')
    pb = Column(Float, comment='pb')
    roe = Column(String, comment='ROE')
    yeild = Column(Float, comment='股息率')
    eva_type = Column(String, comment='估值类型')


class IndexValuation(BaseDao, XueQiuBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "xueqiu_index_valuation"
        self.database = 'xueqiu.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_engine(self.database_url,
                                    connect_args={
                                        'check_same_thread': False,
                                        'timeout': config.get_sqlite_timeout()
                                    })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        XueqiuIndexValuation.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'offset', 'limit']
        entity_fields = [
            "ts_code", "trade_date", "name", "ttype", "pe", "pe_percentile", "peg", "pb_percentile", "pb", "roe",
            "yeild", "eva_type"
        ]
        BaseDao.__init__(self, self.engine, session_factory, XueqiuIndexValuation, self.database, self.table_name,
                         query_fields, entity_fields, config)
        DataProcess.__init__(self, "index_valuation", config)
        XueQiuBase.__init__(self, "index_valuation", config)

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
            "name": "name",
            "type": "String",
            "comment": "名称"
        }, {
            "name": "ttype",
            "type": "Integer",
            "comment": "类型"
        }, {
            "name": "pe",
            "type": "Float",
            "comment": "pe"
        }, {
            "name": "pe_percentile",
            "type": "Float",
            "comment": "pe百分位"
        }, {
            "name": "peg",
            "type": "Float",
            "comment": "预测peg"
        }, {
            "name": "pb_percentile",
            "type": "Float",
            "comment": "pb百分位"
        }, {
            "name": "pb",
            "type": "Float",
            "comment": "pb"
        }, {
            "name": "roe",
            "type": "String",
            "comment": "ROE"
        }, {
            "name": "yeild",
            "type": "Float",
            "comment": "股息率"
        }, {
            "name": "eva_type",
            "type": "String",
            "comment": "估值类型"
        }]

    def index_valuation(self, fields='', **kwargs):
        """
        指数估值
        | Arguments:
        | ts_code(str):   股票代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | offset(str):   开始行数
        | limit(str):   最大行数
        
        :return: DataFrame
         ts_code(str)  股票代码
         trade_date(str)  交易日期
         name(str)  名称
         ttype(int)  类型
         pe(float)  pe
         pe_percentile(float)  pe百分位
         peg(float)  预测peg
         pb_percentile(float)  pb百分位
         pb(float)  pb
         roe(str)  ROE
         yeild(float)  股息率
         eva_type(str)  估值类型
        
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
                self.logger.debug("Invoke pro.index_valuation with args: {}".format(kwargs))
                res = self.index_valuation_request(fields=self.entity_fields, **kwargs)
                res.to_sql('xueqiu_index_valuation',
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


setattr(IndexValuation, 'default_limit', default_limit_ext)
setattr(IndexValuation, 'default_cron_express', default_cron_express_ext)
setattr(IndexValuation, 'default_order_by', default_order_by_ext)
setattr(IndexValuation, 'prepare', prepare_ext)
setattr(IndexValuation, 'query_parameters', query_parameters_ext)
setattr(IndexValuation, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())

    api = IndexValuation(config)
    api.process()    # 同步增量数据
    print(api.index_valuation())    # 数据查询接口
