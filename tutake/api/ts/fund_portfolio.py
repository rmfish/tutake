"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_portfolio接口
获取公募基金持仓数据，季度更新
数据接口-公募基金-基金持仓  https://tushare.pro/document/2?doc_id=121

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base
from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.fund_portfolio_ext import *
from tutake.api.ts.tushare_dao import TushareDAO
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareFundPortfolio(Base):
    __tablename__ = "tushare_fund_portfolio"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='TS基金代码')
    ann_date = Column(String, index=True, comment='公告日期')
    end_date = Column(String, index=True, comment='截止日期')
    symbol = Column(String, comment='股票代码')
    mkv = Column(Float, comment='持有股票市值(元)')
    amount = Column(Float, comment='持有股票数量（股）')
    stk_mkv_ratio = Column(Float, comment='占股票市值比')
    stk_float_ratio = Column(Float, comment='占流通股本比例')


class FundPortfolio(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine(config.get_data_sqlite_driver_url('tushare_fund_portfolio.db'),
                                    connect_args={
                                        'check_same_thread': False,
                                        'timeout': config.get_sqlite_timeout()
                                    })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareFundPortfolio.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'ann_date', 'start_date', 'end_date', 'period', 'limit', 'offset']
        entity_fields = [
            "ts_code", "ann_date", "end_date", "symbol", "mkv", "amount", "stk_mkv_ratio", "stk_float_ratio"
        ]
        TushareDAO.__init__(self, self.engine, session_factory, TushareFundPortfolio, 'tushare_fund_portfolio',
                            query_fields, entity_fields, config)
        DataProcess.__init__(self, "fund_portfolio", config)
        TuShareBase.__init__(self, "fund_portfolio", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS基金代码"
        }, {
            "name": "ann_date",
            "type": "String",
            "comment": "公告日期"
        }, {
            "name": "end_date",
            "type": "String",
            "comment": "截止日期"
        }, {
            "name": "symbol",
            "type": "String",
            "comment": "股票代码"
        }, {
            "name": "mkv",
            "type": "Float",
            "comment": "持有股票市值(元)"
        }, {
            "name": "amount",
            "type": "Float",
            "comment": "持有股票数量（股）"
        }, {
            "name": "stk_mkv_ratio",
            "type": "Float",
            "comment": "占股票市值比"
        }, {
            "name": "stk_float_ratio",
            "type": "Float",
            "comment": "占流通股本比例"
        }]

    def fund_portfolio(self, fields='', **kwargs):
        """
        获取公募基金持仓数据，季度更新
        | Arguments:
        | ts_code(str):   基金代码
        | ann_date(str):   公告日期
        | start_date(str):   公告开始日期
        | end_date(str):   公告结束日期
        | period(str):   报告期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS基金代码
         ann_date(str)  公告日期
         end_date(str)  截止日期
         symbol(str)  股票代码
         mkv(float)  持有股票市值(元)
         amount(float)  持有股票数量（股）
         stk_mkv_ratio(float)  占股票市值比
         stk_float_ratio(float)  占流通股本比例
        
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

        def fetch_save(offset_val=0):
            try:
                kwargs['offset'] = str(offset_val)
                self.logger.debug("Invoke pro.fund_portfolio with args: {}".format(kwargs))
                res = self.tushare_query('fund_portfolio', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_fund_portfolio',
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


setattr(FundPortfolio, 'default_limit', default_limit_ext)
setattr(FundPortfolio, 'default_cron_express', default_cron_express_ext)
setattr(FundPortfolio, 'default_order_by', default_order_by_ext)
setattr(FundPortfolio, 'prepare', prepare_ext)
setattr(FundPortfolio, 'query_parameters', query_parameters_ext)
setattr(FundPortfolio, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fund_portfolio())

    api = FundPortfolio(config)
    api.process()    # 同步增量数据
    print(api.fund_portfolio())    # 数据查询接口
