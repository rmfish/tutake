"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare margin接口
获取融资融券每日交易汇总数据,数据开始于2010年，每日9点更新
数据接口-沪深股票-市场参考数据-融资融券交易汇总  https://tushare.pro/document/2?doc_id=58

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import margin_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareMargin(TutakeTableBase):
    __tablename__ = "tushare_margin"
    trade_date = Column(String, index=True, comment='交易日期')
    exchange_id = Column(String, index=True, comment='交易所代码（SSE上交所SZSE深交所）')
    rzye = Column(Float, comment='融资余额(元)')
    rzmre = Column(Float, comment='融资买入额(元)')
    rzche = Column(Float, comment='融资偿还额(元)')
    rqye = Column(Float, comment='融券余额(元)')
    rqmcl = Column(Float, comment='融券卖出量(股,份,手)')
    rzrqye = Column(Float, comment='融资融券余额(元)')
    rqyl = Column(Float, comment='融券余量')


class Margin(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_margin"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareMargin.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareMargin),
                                  config.get_tutake_data_dir())

        query_fields = ['trade_date', 'exchange_id', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = ["trade_date", "exchange_id", "rzye", "rzmre", "rzche", "rqye", "rqmcl", "rzrqye", "rqyl"]
        entity_fields = ["trade_date", "exchange_id", "rzye", "rzmre", "rzche", "rqye", "rqmcl", "rzrqye", "rqyl"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareMargin, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "margin", config)
        TuShareBase.__init__(self, "margin", config, 600)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "exchange_id",
            "type": "String",
            "comment": "交易所代码（SSE上交所SZSE深交所）"
        }, {
            "name": "rzye",
            "type": "Float",
            "comment": "融资余额(元)"
        }, {
            "name": "rzmre",
            "type": "Float",
            "comment": "融资买入额(元)"
        }, {
            "name": "rzche",
            "type": "Float",
            "comment": "融资偿还额(元)"
        }, {
            "name": "rqye",
            "type": "Float",
            "comment": "融券余额(元)"
        }, {
            "name": "rqmcl",
            "type": "Float",
            "comment": "融券卖出量(股,份,手)"
        }, {
            "name": "rzrqye",
            "type": "Float",
            "comment": "融资融券余额(元)"
        }, {
            "name": "rqyl",
            "type": "Float",
            "comment": "融券余量"
        }]

    def margin(self, fields='', **kwargs):
        """
        获取融资融券每日交易汇总数据,数据开始于2010年，每日9点更新
        | Arguments:
        | trade_date(str):   交易日期
        | exchange_id(str):   交易所代码
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  交易日期 Y
         exchange_id(str)  交易所代码（SSE上交所SZSE深交所） Y
         rzye(float)  融资余额(元) Y
         rzmre(float)  融资买入额(元) Y
         rzche(float)  融资偿还额(元) Y
         rqye(float)  融券余额(元) Y
         rqmcl(float)  融券卖出量(股,份,手) Y
         rzrqye(float)  融资融券余额(元) Y
         rqyl(float)  融券余量 Y
        
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append, self.writer, **kwargs)

    def fetch_and_append(self, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        init_args = {"trade_date": "", "exchange_id": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
        is_test = kwargs.get('test') or False
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
                self.logger.debug("Invoke pro.margin with args: {}".format(kwargs))
                return self.tushare_query('margin', fields=self.tushare_fields, **kwargs)
            except Exception as err:
                raise ProcessException(kwargs, err)

        res = fetch_save(offset)
        size = res.size()
        offset += size
        res.fields = self.entity_fields
        if is_test:
            return res
        while kwargs['limit'] != "" and size == int(kwargs['limit']):
            result = fetch_save(offset)
            size = result.size()
            offset += size
            res.append(result)
        return res


extends_attr(Margin, margin_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.margin())

    api = Margin(config)
    print(api.process())    # 同步增量数据
    print(api.margin())    # 数据查询接口
