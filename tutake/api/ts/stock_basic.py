"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare stock_basic接口
获取基础信息数据，包括股票代码、名称、上市日期、退市日期等
数据接口-沪深股票-基础数据-股票列表  https://tushare.pro/document/2?doc_id=25

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import stock_basic_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareStockBasic(TutakeTableBase):
    __tablename__ = "tushare_stock_basic"
    ts_code = Column(String, primary_key=True, comment='TS代码')
    symbol = Column(String, comment='股票代码')
    name = Column(String, index=True, comment='股票名称')
    area = Column(String, comment='地域')
    industry = Column(String, comment='所属行业')
    fullname = Column(String, comment='股票全称')
    enname = Column(String, comment='英文全称')
    cnspell = Column(String, comment='拼音缩写')
    market = Column(String, index=True, comment='市场类型')
    exchange = Column(String, index=True, comment='交易所代码')
    curr_type = Column(String, comment='交易货币')
    list_status = Column(String, index=True, comment='上市状态 L上市 D退市 P暂停上市')
    list_date = Column(String, comment='上市日期')
    delist_date = Column(String, comment='退市日期')
    is_hs = Column(String, index=True, comment='是否沪深港通标的，N否 H沪股通 S深股通')


class StockBasic(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_stock_basic"
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
        TushareStockBasic.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareStockBasic)

        query_fields = ['ts_code', 'name', 'exchange', 'market', 'is_hs', 'list_status', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "symbol", "name", "area", "industry", "fullname", "enname", "cnspell", "market", "exchange",
            "curr_type", "list_status", "list_date", "delist_date", "is_hs"
        ]
        entity_fields = [
            "ts_code", "symbol", "name", "area", "industry", "fullname", "enname", "cnspell", "market", "exchange",
            "curr_type", "list_status", "list_date", "delist_date", "is_hs"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareStockBasic, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "stock_basic", config)
        TuShareBase.__init__(self, "stock_basic", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS代码"
        }, {
            "name": "symbol",
            "type": "String",
            "comment": "股票代码"
        }, {
            "name": "name",
            "type": "String",
            "comment": "股票名称"
        }, {
            "name": "area",
            "type": "String",
            "comment": "地域"
        }, {
            "name": "industry",
            "type": "String",
            "comment": "所属行业"
        }, {
            "name": "fullname",
            "type": "String",
            "comment": "股票全称"
        }, {
            "name": "enname",
            "type": "String",
            "comment": "英文全称"
        }, {
            "name": "cnspell",
            "type": "String",
            "comment": "拼音缩写"
        }, {
            "name": "market",
            "type": "String",
            "comment": "市场类型"
        }, {
            "name": "exchange",
            "type": "String",
            "comment": "交易所代码"
        }, {
            "name": "curr_type",
            "type": "String",
            "comment": "交易货币"
        }, {
            "name": "list_status",
            "type": "String",
            "comment": "上市状态 L上市 D退市 P暂停上市"
        }, {
            "name": "list_date",
            "type": "String",
            "comment": "上市日期"
        }, {
            "name": "delist_date",
            "type": "String",
            "comment": "退市日期"
        }, {
            "name": "is_hs",
            "type": "String",
            "comment": "是否沪深港通标的，N否 H沪股通 S深股通"
        }]

    def stock_basic(self, fields='ts_code,symbol,name,area,industry,market,list_date', **kwargs):
        """
        获取基础信息数据，包括股票代码、名称、上市日期、退市日期等
        | Arguments:
        | ts_code(str):   TS股票代码
        | name(str):   名称
        | exchange(str):   交易所 SSE上交所 SZSE深交所 HKEX港交所
        | market(str):   市场类别
        | is_hs(str):   是否沪深港通标的，N否 H沪股通 S深股通
        | list_status(str):   上市状态 L上市 D退市 P暂停上市
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS代码 Y
         symbol(str)  股票代码 Y
         name(str)  股票名称 Y
         area(str)  地域 Y
         industry(str)  所属行业 Y
         fullname(str)  股票全称 N
         enname(str)  英文全称 N
         cnspell(str)  拼音缩写 N
         market(str)  市场类型 Y
         exchange(str)  交易所代码 N
         curr_type(str)  交易货币 N
         list_status(str)  上市状态 L上市 D退市 P暂停上市 N
         list_date(str)  上市日期 Y
         delist_date(str)  退市日期 N
         is_hs(str)  是否沪深港通标的，N否 H沪股通 S深股通 N
        
        """
        default_query_params = {'list_status': ['L', 'P']}
        kwargs = {**default_query_params, **kwargs}
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
            "name": "",
            "exchange": "",
            "market": "",
            "is_hs": "",
            "list_status": "",
            "limit": "",
            "offset": ""
        }
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
                self.logger.debug("Invoke pro.stock_basic with args: {}".format(kwargs))
                return self.tushare_query('stock_basic', fields=self.tushare_fields, **kwargs)
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


extends_attr(StockBasic, stock_basic_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.stock_basic())

    api = StockBasic(config)
    print(api.process())    # 同步增量数据
    print(api.stock_basic())    # 数据查询接口
