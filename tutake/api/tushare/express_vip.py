"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare express_vip接口
获取上市公司业绩快报
数据接口-沪深股票-财务数据-业绩快报  https://tushare.pro/document/2?doc_id=4600

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessType
from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.ggt_daily_ext import *
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_express_vip.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()


class TushareExpressVip(Base):
    __tablename__ = "tushare_express_vip"
    id = Column(Integer, primary_key=True, autoincrement=True)
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


TushareExpressVip.__table__.create(bind=engine, checkfirst=True)


class ExpressVip(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = ['ts_code', 'ann_date', 'start_date', 'end_date', 'period', 'limit', 'offset']
        entity_fields = [
            "ts_code", "ann_date", "end_date", "revenue", "operate_profit", "total_profit", "n_income", "total_assets",
            "total_hldr_eqy_exc_min_int", "diluted_eps", "diluted_roe", "yoy_net_profit", "bps", "yoy_sales", "yoy_op",
            "yoy_tp", "yoy_dedu_np", "yoy_eps", "yoy_roe", "growth_assets", "yoy_equity", "growth_bps", "or_last_year",
            "op_last_year", "tp_last_year", "np_last_year", "eps_last_year", "open_net_assets", "open_bps",
            "perf_summary", "is_audit", "remark"
        ]
        BaseDao.__init__(self, engine, session_factory, TushareExpressVip, 'tushare_express_vip', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "express_vip")
        self.dao = DAO()

    def express_vip(self, fields='', **kwargs):
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
         ts_code(str)  TS股票代码
         ann_date(str)  公告日期
         end_date(str)  报告期
         revenue(float)  营业收入(元)
         operate_profit(float)  营业利润(元)
         total_profit(float)  利润总额(元)
         n_income(float)  净利润(元)
         total_assets(float)  总资产(元)
         total_hldr_eqy_exc_min_int(float)  股东权益合计(不含少数股东权益)(元)
         diluted_eps(float)  每股收益(摊薄)(元)
         diluted_roe(float)  净资产收益率(摊薄)(%)
         yoy_net_profit(float)  去年同期修正后净利润
         bps(float)  每股净资产
         yoy_sales(float)  同比增长率:营业收入
         yoy_op(float)  同比增长率:营业利润
         yoy_tp(float)  同比增长率:利润总额
         yoy_dedu_np(float)  同比增长率:归属母公司股东的净利润
         yoy_eps(float)  同比增长率:基本每股收益
         yoy_roe(float)  同比增减:加权平均净资产收益率
         growth_assets(float)  比年初增长率:总资产
         yoy_equity(float)  比年初增长率:归属母公司的股东权益
         growth_bps(float)  比年初增长率:归属于母公司股东的每股净资产
         or_last_year(float)  去年同期营业收入
         op_last_year(float)  去年同期营业利润
         tp_last_year(float)  去年同期利润总额
         np_last_year(float)  去年同期净利润
         eps_last_year(float)  去年同期每股收益
         open_net_assets(float)  期初净资产
         open_bps(float)  期初每股净资产
         perf_summary(str)  业绩简要说明
         is_audit(int)  是否审计： 1是 0否
         remark(str)  备注
        
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
            "ann_date": "",
            "start_date": "",
            "end_date": "",
            "period": "",
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
            self.logger.debug("Invoke pro.express_vip with args: {}".format(kwargs))
            res = self.tushare_api().express_vip(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_express_vip', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(ExpressVip, 'default_limit', default_limit_ext)
setattr(ExpressVip, 'default_cron_express', default_cron_express_ext)
setattr(ExpressVip, 'default_order_by', default_order_by_ext)
setattr(ExpressVip, 'prepare', prepare_ext)
setattr(ExpressVip, 'tushare_parameters', tushare_parameters_ext)
setattr(ExpressVip, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    api = ExpressVip()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    api.process(ProcessType.INCREASE)    # 同步增量数据
    print(api.express_vip())    # 数据查询接口
