"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare express_vip接口
获取上市公司业绩快报
数据接口-沪深股票-财务数据-业绩快报  https://tushare.pro/document/2?doc_id=4600

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import express_vip_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareExpressVip(TutakeTableBase):
    __tablename__ = "tushare_express_vip"
    ts_code = Column(String, index=True, comment='TS股票代码')
    ann_date = Column(String, index=True, comment='公告日期')
    end_date = Column(String, index=True, comment='报告期')
    revenue = Column(Float, comment='营业收入(元)')
    operate_profit = Column(Float, comment='营业利润(元)')
    total_profit = Column(Float, comment='利润总额(元)')
    n_income = Column(Float, comment='净利润(元)')
    total_assets = Column(Float, comment='总资产(元)')
    total_hldr_eqy_exc_min_int = Column(Float, comment='股东权益合计(不含少数股东权益)(元)')
    diluted_eps = Column(Float, comment='每股收益(摊薄)(元)')
    diluted_roe = Column(Float, comment='净资产收益率(摊薄)(%)')
    yoy_net_profit = Column(Float, comment='去年同期修正后净利润')
    bps = Column(Float, comment='每股净资产')
    yoy_sales = Column(Float, comment='同比增长率:营业收入')
    yoy_op = Column(Float, comment='同比增长率:营业利润')
    yoy_tp = Column(Float, comment='同比增长率:利润总额')
    yoy_dedu_np = Column(Float, comment='同比增长率:归属母公司股东的净利润')
    yoy_eps = Column(Float, comment='同比增长率:基本每股收益')
    yoy_roe = Column(Float, comment='同比增减:加权平均净资产收益率')
    growth_assets = Column(Float, comment='比年初增长率:总资产')
    yoy_equity = Column(Float, comment='比年初增长率:归属母公司的股东权益')
    growth_bps = Column(Float, comment='比年初增长率:归属于母公司股东的每股净资产')
    or_last_year = Column(Float, comment='去年同期营业收入')
    op_last_year = Column(Float, comment='去年同期营业利润')
    tp_last_year = Column(Float, comment='去年同期利润总额')
    np_last_year = Column(Float, comment='去年同期净利润')
    eps_last_year = Column(Float, comment='去年同期每股收益')
    open_net_assets = Column(Float, comment='期初净资产')
    open_bps = Column(Float, comment='期初每股净资产')
    perf_summary = Column(String, comment='业绩简要说明')
    is_audit = Column(Integer, comment='是否审计： 1是 0否')
    remark = Column(String, comment='备注')


class ExpressVip(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_express_vip"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareExpressVip.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareExpressVip),
                                  config.get_tutake_data_dir())

        query_fields = ['ts_code', 'ann_date', 'start_date', 'end_date', 'period', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "ann_date", "end_date", "revenue", "operate_profit", "total_profit", "n_income", "total_assets",
            "total_hldr_eqy_exc_min_int", "diluted_eps", "diluted_roe", "yoy_net_profit", "bps", "yoy_sales", "yoy_op",
            "yoy_tp", "yoy_dedu_np", "yoy_eps", "yoy_roe", "growth_assets", "yoy_equity", "growth_bps", "or_last_year",
            "op_last_year", "tp_last_year", "np_last_year", "eps_last_year", "open_net_assets", "open_bps",
            "perf_summary", "is_audit", "remark"
        ]
        entity_fields = [
            "ts_code", "ann_date", "end_date", "revenue", "operate_profit", "total_profit", "n_income", "total_assets",
            "total_hldr_eqy_exc_min_int", "diluted_eps", "diluted_roe", "yoy_net_profit", "bps", "yoy_sales", "yoy_op",
            "yoy_tp", "yoy_dedu_np", "yoy_eps", "yoy_roe", "growth_assets", "yoy_equity", "growth_bps", "or_last_year",
            "op_last_year", "tp_last_year", "np_last_year", "eps_last_year", "open_net_assets", "open_bps",
            "perf_summary", "is_audit", "remark"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareExpressVip, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "express_vip", config)
        TuShareBase.__init__(self, "express_vip", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS股票代码"
        }, {
            "name": "ann_date",
            "type": "String",
            "comment": "公告日期"
        }, {
            "name": "end_date",
            "type": "String",
            "comment": "报告期"
        }, {
            "name": "revenue",
            "type": "Float",
            "comment": "营业收入(元)"
        }, {
            "name": "operate_profit",
            "type": "Float",
            "comment": "营业利润(元)"
        }, {
            "name": "total_profit",
            "type": "Float",
            "comment": "利润总额(元)"
        }, {
            "name": "n_income",
            "type": "Float",
            "comment": "净利润(元)"
        }, {
            "name": "total_assets",
            "type": "Float",
            "comment": "总资产(元)"
        }, {
            "name": "total_hldr_eqy_exc_min_int",
            "type": "Float",
            "comment": "股东权益合计(不含少数股东权益)(元)"
        }, {
            "name": "diluted_eps",
            "type": "Float",
            "comment": "每股收益(摊薄)(元)"
        }, {
            "name": "diluted_roe",
            "type": "Float",
            "comment": "净资产收益率(摊薄)(%)"
        }, {
            "name": "yoy_net_profit",
            "type": "Float",
            "comment": "去年同期修正后净利润"
        }, {
            "name": "bps",
            "type": "Float",
            "comment": "每股净资产"
        }, {
            "name": "yoy_sales",
            "type": "Float",
            "comment": "同比增长率:营业收入"
        }, {
            "name": "yoy_op",
            "type": "Float",
            "comment": "同比增长率:营业利润"
        }, {
            "name": "yoy_tp",
            "type": "Float",
            "comment": "同比增长率:利润总额"
        }, {
            "name": "yoy_dedu_np",
            "type": "Float",
            "comment": "同比增长率:归属母公司股东的净利润"
        }, {
            "name": "yoy_eps",
            "type": "Float",
            "comment": "同比增长率:基本每股收益"
        }, {
            "name": "yoy_roe",
            "type": "Float",
            "comment": "同比增减:加权平均净资产收益率"
        }, {
            "name": "growth_assets",
            "type": "Float",
            "comment": "比年初增长率:总资产"
        }, {
            "name": "yoy_equity",
            "type": "Float",
            "comment": "比年初增长率:归属母公司的股东权益"
        }, {
            "name": "growth_bps",
            "type": "Float",
            "comment": "比年初增长率:归属于母公司股东的每股净资产"
        }, {
            "name": "or_last_year",
            "type": "Float",
            "comment": "去年同期营业收入"
        }, {
            "name": "op_last_year",
            "type": "Float",
            "comment": "去年同期营业利润"
        }, {
            "name": "tp_last_year",
            "type": "Float",
            "comment": "去年同期利润总额"
        }, {
            "name": "np_last_year",
            "type": "Float",
            "comment": "去年同期净利润"
        }, {
            "name": "eps_last_year",
            "type": "Float",
            "comment": "去年同期每股收益"
        }, {
            "name": "open_net_assets",
            "type": "Float",
            "comment": "期初净资产"
        }, {
            "name": "open_bps",
            "type": "Float",
            "comment": "期初每股净资产"
        }, {
            "name": "perf_summary",
            "type": "String",
            "comment": "业绩简要说明"
        }, {
            "name": "is_audit",
            "type": "Integer",
            "comment": "是否审计： 1是 0否"
        }, {
            "name": "remark",
            "type": "String",
            "comment": "备注"
        }]

    def express_vip(
            self,
            fields='ts_code,ann_date,end_date,revenue,operate_profit,total_profit,n_income,total_assets,total_hldr_eqy_exc_min_int,diluted_eps,diluted_roe,yoy_net_profit,bps,perf_summary',
            **kwargs):
        """
        获取上市公司业绩快报
        | Arguments:
        | ts_code(str):   股票代码
        | ann_date(str):   公告日期
        | start_date(str):   公告开始日期
        | end_date(str):   公告结束日期
        | period(str):   报告期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS股票代码 Y
         ann_date(str)  公告日期 Y
         end_date(str)  报告期 Y
         revenue(float)  营业收入(元) Y
         operate_profit(float)  营业利润(元) Y
         total_profit(float)  利润总额(元) Y
         n_income(float)  净利润(元) Y
         total_assets(float)  总资产(元) Y
         total_hldr_eqy_exc_min_int(float)  股东权益合计(不含少数股东权益)(元) Y
         diluted_eps(float)  每股收益(摊薄)(元) Y
         diluted_roe(float)  净资产收益率(摊薄)(%) Y
         yoy_net_profit(float)  去年同期修正后净利润 Y
         bps(float)  每股净资产 Y
         yoy_sales(float)  同比增长率:营业收入 N
         yoy_op(float)  同比增长率:营业利润 N
         yoy_tp(float)  同比增长率:利润总额 N
         yoy_dedu_np(float)  同比增长率:归属母公司股东的净利润 N
         yoy_eps(float)  同比增长率:基本每股收益 N
         yoy_roe(float)  同比增减:加权平均净资产收益率 N
         growth_assets(float)  比年初增长率:总资产 N
         yoy_equity(float)  比年初增长率:归属母公司的股东权益 N
         growth_bps(float)  比年初增长率:归属于母公司股东的每股净资产 N
         or_last_year(float)  去年同期营业收入 N
         op_last_year(float)  去年同期营业利润 N
         tp_last_year(float)  去年同期利润总额 N
         np_last_year(float)  去年同期净利润 N
         eps_last_year(float)  去年同期每股收益 N
         open_net_assets(float)  期初净资产 N
         open_bps(float)  期初每股净资产 N
         perf_summary(str)  业绩简要说明 Y
         is_audit(int)  是否审计： 1是 0否 N
         remark(str)  备注 N
        
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
        init_args = {
            "ts_code": "",
            "ann_date": "",
            "start_date": "",
            "end_date": "",
            "period": "",
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
                self.logger.debug("Invoke pro.express_vip with args: {}".format(kwargs))
                return self.tushare_query('express_vip', fields=self.tushare_fields, **kwargs)
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


extends_attr(ExpressVip, express_vip_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.express_vip())

    api = ExpressVip(config)
    print(api.process())    # 同步增量数据
    print(api.express_vip())    # 数据查询接口
