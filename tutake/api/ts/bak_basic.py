"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare bak_basic接口
获取备用基础列表，数据从2016年开始
数据接口-沪深股票-基础数据-备用列表  https://tushare.pro/document/2?doc_id=262

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base
from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.bak_basic_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


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


class BakBasic(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_shared_engine(config.get_data_sqlite_driver_url('tushare_bak_basic.db'),
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareBakBasic.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['trade_date', 'ts_code', 'limit', 'offset']
        entity_fields = [
            "trade_date", "ts_code", "name", "industry", "area", "pe", "float_share", "total_share", "total_assets",
            "liquid_assets", "fixed_assets", "reserved", "reserved_pershare", "eps", "bvps", "pb", "list_date", "undp",
            "per_undp", "rev_yoy", "profit_yoy", "gpr", "npr", "holder_num"
        ]
        TushareDAO.__init__(self, self.engine, session_factory, TushareBakBasic, 'tushare_bak_basic.db',
                            'tushare_bak_basic', query_fields, entity_fields, config)
        DataProcess.__init__(self, "bak_basic", config)
        TuShareBase.__init__(self, "bak_basic", config, 120)
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
            "name": "industry",
            "type": "String",
            "comment": "行业"
        }, {
            "name": "area",
            "type": "String",
            "comment": "地域"
        }, {
            "name": "pe",
            "type": "Float",
            "comment": "市盈率（动）"
        }, {
            "name": "float_share",
            "type": "Float",
            "comment": "流通股本（万）"
        }, {
            "name": "total_share",
            "type": "Float",
            "comment": "总股本（万）"
        }, {
            "name": "total_assets",
            "type": "Float",
            "comment": "总资产（万）"
        }, {
            "name": "liquid_assets",
            "type": "Float",
            "comment": "流动资产（万）"
        }, {
            "name": "fixed_assets",
            "type": "Float",
            "comment": "固定资产（万）"
        }, {
            "name": "reserved",
            "type": "Float",
            "comment": "公积金"
        }, {
            "name": "reserved_pershare",
            "type": "Float",
            "comment": "每股公积金"
        }, {
            "name": "eps",
            "type": "Float",
            "comment": "每股收益"
        }, {
            "name": "bvps",
            "type": "Float",
            "comment": "每股净资产"
        }, {
            "name": "pb",
            "type": "Float",
            "comment": "市净率"
        }, {
            "name": "list_date",
            "type": "String",
            "comment": "上市日期"
        }, {
            "name": "undp",
            "type": "Float",
            "comment": "未分配利润"
        }, {
            "name": "per_undp",
            "type": "Float",
            "comment": "每股未分配利润"
        }, {
            "name": "rev_yoy",
            "type": "Float",
            "comment": "收入同比（%）"
        }, {
            "name": "profit_yoy",
            "type": "Float",
            "comment": "利润同比（%）"
        }, {
            "name": "gpr",
            "type": "Float",
            "comment": "毛利率（%）"
        }, {
            "name": "npr",
            "type": "Float",
            "comment": "净利润率（%）"
        }, {
            "name": "holder_num",
            "type": "Integer",
            "comment": "股东人数"
        }]

    def bak_basic(self, fields='', **kwargs):
        """
        获取备用基础列表，数据从2016年开始
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

    def process(self):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append)

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

        def fetch_save(offset_val=0):
            try:
                kwargs['offset'] = str(offset_val)
                self.logger.debug("Invoke pro.bak_basic with args: {}".format(kwargs))
                res = self.tushare_query('bak_basic', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_bak_basic',
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


setattr(BakBasic, 'default_limit', default_limit_ext)
setattr(BakBasic, 'default_cron_express', default_cron_express_ext)
setattr(BakBasic, 'default_order_by', default_order_by_ext)
setattr(BakBasic, 'prepare', prepare_ext)
setattr(BakBasic, 'query_parameters', query_parameters_ext)
setattr(BakBasic, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.bak_basic())

    api = BakBasic(config)
    api.process()    # 同步增量数据
    print(api.bak_basic())    # 数据查询接口
