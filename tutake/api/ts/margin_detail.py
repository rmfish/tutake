"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare margin_detail接口
获取沪深两市每日融资融券明细,数据开始于2010年，每日9点更新
数据接口-沪深股票-市场参考数据-融资融券交易明细  https://tushare.pro/document/2?doc_id=59

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.margin_detail_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareMarginDetail(Base):
    __tablename__ = "tushare_margin_detail"
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String, index=True, comment='交易日期')
    ts_code = Column(String, index=True, comment='TS股票代码')
    name = Column(String, comment='股票名称')
    rzye = Column(Float, comment='融资余额(元)')
    rqye = Column(Float, comment='融券余额(元)')
    rzmre = Column(Float, comment='融资买入额(元)')
    rqyl = Column(Float, comment='融券余量（手）')
    rzche = Column(Float, comment='融资偿还额(元)')
    rqchl = Column(Float, comment='融券偿还量(手)')
    rqmcl = Column(Float, comment='融券卖出量(股,份,手)')
    rzrqye = Column(Float, comment='融资融券余额(元)')


class MarginDetail(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_margin_detail"
        self.database = 'tushare_stock_market.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareMarginDetail.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['trade_date', 'ts_code', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = [
            "trade_date", "ts_code", "name", "rzye", "rqye", "rzmre", "rqyl", "rzche", "rqchl", "rqmcl", "rzrqye"
        ]
        entity_fields = [
            "trade_date", "ts_code", "name", "rzye", "rqye", "rzmre", "rqyl", "rzche", "rqchl", "rqmcl", "rzrqye"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareMarginDetail, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "margin_detail", config)
        TuShareBase.__init__(self, "margin_detail", config, 600)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "ts_code",
            "type": "String",
            "comment": "TS股票代码"
        }, {
            "name": "name",
            "type": "String",
            "comment": "股票名称"
        }, {
            "name": "rzye",
            "type": "Float",
            "comment": "融资余额(元)"
        }, {
            "name": "rqye",
            "type": "Float",
            "comment": "融券余额(元)"
        }, {
            "name": "rzmre",
            "type": "Float",
            "comment": "融资买入额(元)"
        }, {
            "name": "rqyl",
            "type": "Float",
            "comment": "融券余量（手）"
        }, {
            "name": "rzche",
            "type": "Float",
            "comment": "融资偿还额(元)"
        }, {
            "name": "rqchl",
            "type": "Float",
            "comment": "融券偿还量(手)"
        }, {
            "name": "rqmcl",
            "type": "Float",
            "comment": "融券卖出量(股,份,手)"
        }, {
            "name": "rzrqye",
            "type": "Float",
            "comment": "融资融券余额(元)"
        }]

    def margin_detail(self, fields='trade_date,ts_code,rzye,rqye,rzmre,rqyl,rzche,rqchl,rqmcl,rzrqye', **kwargs):
        """
        获取沪深两市每日融资融券明细,数据开始于2010年，每日9点更新
        | Arguments:
        | trade_date(str):   交易日期
        | ts_code(str):   TS代码
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  交易日期 Y
         ts_code(str)  TS股票代码 Y
         name(str)  股票名称 N
         rzye(float)  融资余额(元) Y
         rqye(float)  融券余额(元) Y
         rzmre(float)  融资买入额(元) Y
         rqyl(float)  融券余量（手） Y
         rzche(float)  融资偿还额(元) Y
         rqchl(float)  融券偿还量(手) Y
         rqmcl(float)  融券卖出量(股,份,手) Y
         rzrqye(float)  融资融券余额(元) Y
        
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
        init_args = {"trade_date": "", "ts_code": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.margin_detail with args: {}".format(kwargs))
                return self.tushare_query('margin_detail', fields=self.tushare_fields, **kwargs)
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


setattr(MarginDetail, 'default_limit', default_limit_ext)
setattr(MarginDetail, 'default_cron_express', default_cron_express_ext)
setattr(MarginDetail, 'default_order_by', default_order_by_ext)
setattr(MarginDetail, 'prepare', prepare_ext)
setattr(MarginDetail, 'query_parameters', query_parameters_ext)
setattr(MarginDetail, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.margin_detail())

    api = MarginDetail(config)
    print(api.process())    # 同步增量数据
    print(api.margin_detail())    # 数据查询接口
