"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_basic接口
数据接口-公募基金-基金列表  https://tushare.pro/document/2?doc_id=19

@author: rmfish
"""
import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.fund_basic_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_fund_basic.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.fund_basic')


class TushareFundBasic(Base):
    __tablename__ = "tushare_fund_basic"
    ts_code = Column(String, primary_key=True, comment='基金代码')
    name = Column(String, index=True, comment='简称')
    management = Column(String, comment='管理人')
    custodian = Column(String, comment='托管人')
    fund_type = Column(String, comment='投资类型')
    found_date = Column(String, comment='成立日期')
    due_date = Column(String, comment='到期日期')
    list_date = Column(String, comment='上市时间')
    issue_date = Column(String, comment='发行日期')
    delist_date = Column(String, comment='退市日期')
    issue_amount = Column(Float, comment='发行份额(亿份)')
    m_fee = Column(Float, comment='管理费')
    c_fee = Column(Float, comment='托管费')
    duration_year = Column(Float, comment='存续期')
    p_value = Column(Float, comment='面值')
    min_amount = Column(Float, comment='起点金额(万元)')
    exp_return = Column(Float, comment='预期收益率')
    benchmark = Column(String, comment='业绩比较基准')
    status = Column(String, index=True, comment='存续状态D摘牌 I发行 L已上市')
    invest_type = Column(String, comment='投资风格')
    type = Column(String, comment='基金类型')
    trustee = Column(String, comment='受托人')
    purc_startdate = Column(String, comment='日常申购起始日')
    redm_startdate = Column(String, comment='日常赎回起始日')
    market = Column(String, index=True, comment='E场内O场外')


TushareFundBasic.__table__.create(bind=engine, checkfirst=True)


class FundBasic(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = [
            n for n in [
                'ts_code',
                'market',
                'update_flag',
                'offset',
                'limit',
                'status',
                'name',
            ] if n not in ['limit', 'offset']
        ]
        entity_fields = [
            "ts_code", "name", "management", "custodian", "fund_type", "found_date", "due_date", "list_date",
            "issue_date", "delist_date", "issue_amount", "m_fee", "c_fee", "duration_year", "p_value", "min_amount",
            "exp_return", "benchmark", "status", "invest_type", "type", "trustee", "purc_startdate", "redm_startdate",
            "market"
        ]
        BaseDao.__init__(self, engine, session_factory, TushareFundBasic, 'tushare_fund_basic', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "fund_basic")
        self.dao = DAO()

    def fund_basic(self, fields='', **kwargs):
        """
        公募基金列表
        | Arguments:
        | ts_code(str):   TS基金代码
        | market(str):   交易市场
        | update_flag(str):   更新标志
        | offset(int):   
        | limit(int):   
        | status(str):   存续状态
        | name(str):   
        
        :return: DataFrame
         ts_code(str)  基金代码
         name(str)  简称
         management(str)  管理人
         custodian(str)  托管人
         fund_type(str)  投资类型
         found_date(str)  成立日期
         due_date(str)  到期日期
         list_date(str)  上市时间
         issue_date(str)  发行日期
         delist_date(str)  退市日期
         issue_amount(float)  发行份额(亿份)
         m_fee(float)  管理费
         c_fee(float)  托管费
         duration_year(float)  存续期
         p_value(float)  面值
         min_amount(float)  起点金额(万元)
         exp_return(float)  预期收益率
         benchmark(str)  业绩比较基准
         status(str)  存续状态D摘牌 I发行 L已上市
         invest_type(str)  投资风格
         type(str)  基金类型
         trustee(str)  受托人
         purc_startdate(str)  日常申购起始日
         redm_startdate(str)  日常赎回起始日
         market(str)  E场内O场外
        
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
            "market": "",
            "update_flag": "",
            "offset": "",
            "limit": "",
            "status": "",
            "name": ""
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
            logger.debug("Invoke pro.fund_basic with args: {}".format(kwargs))
            res = self.tushare_api().fund_basic(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_fund_basic', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(FundBasic, 'default_limit', default_limit_ext)
setattr(FundBasic, 'default_order_by', default_order_by_ext)
setattr(FundBasic, 'prepare', prepare_ext)
setattr(FundBasic, 'tushare_parameters', tushare_parameters_ext)
setattr(FundBasic, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)    # 显示列数
    pd.set_option('display.width', 1000)
    logger.setLevel(logging.INFO)
    api = FundBasic()
    api.process(ProcessType.HISTORY)    # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.fund_basic())    # 数据查询接口
