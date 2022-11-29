"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_nav接口
获取公募基金净值数据
数据接口-公募基金-基金净值  https://tushare.pro/document/2?doc_id=119

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.fund_nav_ext import *
from tutake.api.ts.base_dao import BaseDao, Base
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareFundNav(Base):
    __tablename__ = "tushare_fund_nav"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='TS代码')
    ann_date = Column(String, comment='公告日期')
    nav_date = Column(String, index=True, comment='截止日期')
    unit_nav = Column(Float, comment='单位净值')
    accum_nav = Column(Float, comment='累计净值')
    accum_div = Column(Float, comment='累计分红')
    net_asset = Column(Float, comment='资产净值')
    total_netasset = Column(Float, comment='合计资产净值')
    adj_nav = Column(Float, comment='复权单位净值')
    update_flag = Column(String, comment='更新标识')


class FundNav(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine("%s/%s" % (config.get_data_sqlite_driver_url(), 'tushare_fund_nav.db'),
                                    connect_args={'check_same_thread': False})
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareFundNav.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'nav_date', 'offset', 'limit', 'market', 'start_date', 'end_date']
        entity_fields = [
            "ts_code", "ann_date", "nav_date", "unit_nav", "accum_nav", "accum_div", "net_asset", "total_netasset",
            "adj_nav", "update_flag"
        ]
        BaseDao.__init__(self, self.engine, session_factory, TushareFundNav, 'tushare_fund_nav', query_fields,
                         entity_fields, config)
        DataProcess.__init__(self, "fund_nav", config)
        TuShareBase.__init__(self, "fund_nav", config, 5000)
        self.api = TushareAPI(config)

    def fund_nav(self, fields='', **kwargs):
        """
        获取公募基金净值数据
        | Arguments:
        | ts_code(str):   TS基金代码
        | nav_date(str):   净值日期
        | offset(int):   
        | limit(int):   
        | market(str):   E场内O场外
        | start_date(str):   净值开始日期
        | end_date(str):   净值结束日期
        
        :return: DataFrame
         ts_code(str)  TS代码
         ann_date(str)  公告日期
         nav_date(str)  截止日期
         unit_nav(float)  单位净值
         accum_nav(float)  累计净值
         accum_div(float)  累计分红
         net_asset(float)  资产净值
         total_netasset(float)  合计资产净值
         adj_nav(float)  复权单位净值
         update_flag(str)  更新标识
        
        """
        return super().query(fields, **kwargs)

    def process(self, process_type: ProcessType = ProcessType.INCREASE):
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
            "nav_date": "",
            "offset": "",
            "limit": "",
            "market": "",
            "start_date": "",
            "end_date": ""
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
                self.logger.debug("Invoke pro.fund_nav with args: {}".format(kwargs))
                res = self.tushare_query('fund_nav', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_fund_nav',
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


setattr(FundNav, 'default_limit', default_limit_ext)
setattr(FundNav, 'default_cron_express', default_cron_express_ext)
setattr(FundNav, 'default_order_by', default_order_by_ext)
setattr(FundNav, 'prepare', prepare_ext)
setattr(FundNav, 'tushare_parameters', tushare_parameters_ext)
setattr(FundNav, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fund_nav(nav_date='20221111'))

    api = FundNav(config)
    api.process()    # 同步增量数据
    print(api.fund_nav(nav_date='20221111'))    # 数据查询接口
