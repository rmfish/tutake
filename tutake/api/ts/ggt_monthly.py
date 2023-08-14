"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare ggt_monthly接口
港股通每月成交信息，数据从2014年开始
数据接口-沪深股票-行情数据-港股通每月成交统计  https://tushare.pro/document/2?doc_id=197

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base
from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.ggt_monthly_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareGgtMonthly(Base):
    __tablename__ = "tushare_ggt_monthly"
    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(String, index=True, comment='交易日期')
    day_buy_amt = Column(Float, comment='当月日均买入成交金额（亿元）')
    day_buy_vol = Column(Float, comment='当月日均买入成交笔数（万笔）')
    day_sell_amt = Column(Float, comment='当月日均卖出成交金额（亿元）')
    day_sell_vol = Column(Float, comment='当月日均卖出成交笔数（万笔）')
    total_buy_amt = Column(Float, comment='总买入成交金额（亿元）')
    total_buy_vol = Column(Float, comment='总买入成交笔数（万笔）')
    total_sell_amt = Column(Float, comment='总卖出成交金额（亿元）')
    total_sell_vol = Column(Float, comment='总卖出成交笔数（万笔）')


class GgtMonthly(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_shared_engine(config.get_data_sqlite_driver_url('tushare_ggt_monthly.db'),
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareGgtMonthly.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['month', 'start_month', 'end_month', 'limit', 'offset']
        entity_fields = [
            "month", "day_buy_amt", "day_buy_vol", "day_sell_amt", "day_sell_vol", "total_buy_amt", "total_buy_vol",
            "total_sell_amt", "total_sell_vol"
        ]
        TushareDAO.__init__(self, self.engine, session_factory, TushareGgtMonthly, 'tushare_ggt_monthly.db',
                            'tushare_ggt_monthly', query_fields, entity_fields, config)
        DataProcess.__init__(self, "ggt_monthly", config)
        TuShareBase.__init__(self, "ggt_monthly", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "month",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "day_buy_amt",
            "type": "Float",
            "comment": "当月日均买入成交金额（亿元）"
        }, {
            "name": "day_buy_vol",
            "type": "Float",
            "comment": "当月日均买入成交笔数（万笔）"
        }, {
            "name": "day_sell_amt",
            "type": "Float",
            "comment": "当月日均卖出成交金额（亿元）"
        }, {
            "name": "day_sell_vol",
            "type": "Float",
            "comment": "当月日均卖出成交笔数（万笔）"
        }, {
            "name": "total_buy_amt",
            "type": "Float",
            "comment": "总买入成交金额（亿元）"
        }, {
            "name": "total_buy_vol",
            "type": "Float",
            "comment": "总买入成交笔数（万笔）"
        }, {
            "name": "total_sell_amt",
            "type": "Float",
            "comment": "总卖出成交金额（亿元）"
        }, {
            "name": "total_sell_vol",
            "type": "Float",
            "comment": "总卖出成交笔数（万笔）"
        }]

    def ggt_monthly(self, fields='', **kwargs):
        """
        港股通每月成交信息，数据从2014年开始
        | Arguments:
        | month(str):   月度
        | start_month(str):   开始月度
        | end_month(str):   结束月度
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         month(str)  交易日期
         day_buy_amt(float)  当月日均买入成交金额（亿元）
         day_buy_vol(float)  当月日均买入成交笔数（万笔）
         day_sell_amt(float)  当月日均卖出成交金额（亿元）
         day_sell_vol(float)  当月日均卖出成交笔数（万笔）
         total_buy_amt(float)  总买入成交金额（亿元）
         total_buy_vol(float)  总买入成交笔数（万笔）
         total_sell_amt(float)  总卖出成交金额（亿元）
         total_sell_vol(float)  总卖出成交笔数（万笔）
        
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
        init_args = {"month": "", "start_month": "", "end_month": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.ggt_monthly with args: {}".format(kwargs))
                res = self.tushare_query('ggt_monthly', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_ggt_monthly',
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


setattr(GgtMonthly, 'default_limit', default_limit_ext)
setattr(GgtMonthly, 'default_cron_express', default_cron_express_ext)
setattr(GgtMonthly, 'default_order_by', default_order_by_ext)
setattr(GgtMonthly, 'prepare', prepare_ext)
setattr(GgtMonthly, 'query_parameters', query_parameters_ext)
setattr(GgtMonthly, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.ggt_monthly())

    api = GgtMonthly(config)
    api.process()    # 同步增量数据
    print(api.ggt_monthly())    # 数据查询接口
