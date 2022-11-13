"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare stock_basic接口
数据接口-沪深股票-基础数据-股票列表  https://tushare.pro/document/2?doc_id=25

@author: rmfish
"""
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.stock_basic_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_basic_data.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()


class TushareStockBasic(Base):
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


TushareStockBasic.__table__.create(bind=engine, checkfirst=True)


class StockBasic(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = ['ts_code', 'name', 'exchange', 'market', 'is_hs', 'list_status', 'limit', 'offset']
        entity_fields = [
            "ts_code", "symbol", "name", "area", "industry", "fullname", "enname", "cnspell", "market", "exchange",
            "curr_type", "list_status", "list_date", "delist_date", "is_hs"
        ]
        BaseDao.__init__(self, engine, session_factory, TushareStockBasic, 'tushare_stock_basic', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "stock_basic")
        self.dao = DAO()

    def stock_basic(self, fields='', **kwargs):
        """
        
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
         ts_code(str)  TS代码
         symbol(str)  股票代码
         name(str)  股票名称
         area(str)  地域
         industry(str)  所属行业
         fullname(str)  股票全称
         enname(str)  英文全称
         cnspell(str)  拼音缩写
         market(str)  市场类型
         exchange(str)  交易所代码
         curr_type(str)  交易货币
         list_status(str)  上市状态 L上市 D退市 P暂停上市
         list_date(str)  上市日期
         delist_date(str)  退市日期
         is_hs(str)  是否沪深港通标的，N否 H沪股通 S深股通
        
        """
        return super().query(fields, **kwargs)

    def process(self, process_type: ProcessType):
        """
        同步历史数据
        :return:
        """
        return super()._process(process_type, self.fetch_and_append)

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

        @sleep(timeout=61, time_append=60, retry=20, match="^抱歉，您每分钟最多访问该接口")
        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            self.logger.debug("Invoke pro.stock_basic with args: {}".format(kwargs))
            res = self.tushare_api().stock_basic(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_stock_basic', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(StockBasic, 'default_limit', default_limit_ext)
setattr(StockBasic, 'default_order_by', default_order_by_ext)
setattr(StockBasic, 'prepare', prepare_ext)
setattr(StockBasic, 'tushare_parameters', tushare_parameters_ext)
setattr(StockBasic, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    api = StockBasic()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    api.process(ProcessType.INCREASE)    # 同步增量数据
    print(api.stock_basic())    # 数据查询接口
