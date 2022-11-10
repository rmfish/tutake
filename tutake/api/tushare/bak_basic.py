"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare bak_basic接口
数据接口-沪深股票-基础数据-备用列表  https://tushare.pro/document/2?doc_id=262

@author: rmfish
"""
import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.bak_basic_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_bak_basic.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.bak_basic')


class TushareBakBasic(Base):
    __tablename__ = "tushare_bak_basic"
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String, index=True, comment='交易日期')
    ts_code = Column(String, index=True, comment='TS股票代码')
    name = Column(String, comment='股票名称')
    industry = Column(String, comment='行业')
    area = Column(String, comment='地域')
    pe = Column(Float, comment='市盈率（动）')
    float_share = Column(Float, comment='流通股本（万）')
    total_share = Column(Float, comment='总股本（万）')
    total_assets = Column(Float, comment='总资产（万）')
    liquid_assets = Column(Float, comment='流动资产（万）')
    fixed_assets = Column(Float, comment='固定资产（万）')
    reserved = Column(Float, comment='公积金')
    reserved_pershare = Column(Float, comment='每股公积金')
    eps = Column(Float, comment='每股收益')
    bvps = Column(Float, comment='每股净资产')
    pb = Column(Float, comment='市净率')
    list_date = Column(String, comment='上市日期')
    undp = Column(Float, comment='未分配利润')
    per_undp = Column(Float, comment='每股未分配利润')
    rev_yoy = Column(Float, comment='收入同比（%）')
    profit_yoy = Column(Float, comment='利润同比（%）')
    gpr = Column(Float, comment='毛利率（%）')
    npr = Column(Float, comment='净利润率（%）')
    holder_num = Column(Integer, comment='股东人数')


TushareBakBasic.__table__.create(bind=engine, checkfirst=True)


class BakBasic(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = [
            'trade_date',
            'ts_code',
            'limit',
            'offset',
        ]
        entity_fields = [
            "trade_date", "ts_code", "name", "industry", "area", "pe", "float_share", "total_share", "total_assets",
            "liquid_assets", "fixed_assets", "reserved", "reserved_pershare", "eps", "bvps", "pb", "list_date", "undp",
            "per_undp", "rev_yoy", "profit_yoy", "gpr", "npr", "holder_num"
        ]
        BaseDao.__init__(self, engine, session_factory, TushareBakBasic, 'tushare_bak_basic', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "bak_basic")
        self.dao = DAO()

    def bak_basic(self, fields='', **kwargs):
        """
        备用基础信息
        | Arguments:
        | trade_date(str):   交易日期
        | ts_code(str):   股票代码
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  交易日期
         ts_code(str)  TS股票代码
         name(str)  股票名称
         industry(str)  行业
         area(str)  地域
         pe(float)  市盈率（动）
         float_share(float)  流通股本（万）
         total_share(float)  总股本（万）
         total_assets(float)  总资产（万）
         liquid_assets(float)  流动资产（万）
         fixed_assets(float)  固定资产（万）
         reserved(float)  公积金
         reserved_pershare(float)  每股公积金
         eps(float)  每股收益
         bvps(float)  每股净资产
         pb(float)  市净率
         list_date(str)  上市日期
         undp(float)  未分配利润
         per_undp(float)  每股未分配利润
         rev_yoy(float)  收入同比（%）
         profit_yoy(float)  利润同比（%）
         gpr(float)  毛利率（%）
         npr(float)  净利润率（%）
         holder_num(int)  股东人数
        
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
        init_args = {"trade_date": "", "ts_code": "", "limit": "", "offset": ""}
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
            logger.debug("Invoke pro.bak_basic with args: {}".format(kwargs))
            res = self.tushare_api().bak_basic(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_bak_basic', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(BakBasic, 'default_limit', default_limit_ext)
setattr(BakBasic, 'default_order_by', default_order_by_ext)
setattr(BakBasic, 'prepare', prepare_ext)
setattr(BakBasic, 'tushare_parameters', tushare_parameters_ext)
setattr(BakBasic, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)    # 显示列数
    pd.set_option('display.width', 1000)
    logger.setLevel(logging.INFO)
    api = BakBasic()
    api.process(ProcessType.HISTORY)    # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.bak_basic())    # 数据查询接口
