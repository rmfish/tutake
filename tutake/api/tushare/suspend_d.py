"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare suspend_d接口
每日停复牌信息
数据接口-沪深股票-行情数据-每日停复牌信息  https://tushare.pro/document/2?doc_id=214

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

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_suspend_d.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()


class TushareSuspendD(Base):
    __tablename__ = "tushare_suspend_d"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='TS代码')
    trade_date = Column(String, index=True, comment='停复牌日期')
    suspend_timing = Column(String, comment='日内停牌时间段')
    suspend_type = Column(String, index=True, comment='停复牌类型：S-停牌，R-复牌')


TushareSuspendD.__table__.create(bind=engine, checkfirst=True)


class SuspendD(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = ['ts_code', 'suspend_type', 'trade_date', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = ["ts_code", "trade_date", "suspend_timing", "suspend_type"]
        BaseDao.__init__(self, engine, session_factory, TushareSuspendD, 'tushare_suspend_d', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "suspend_d")
        self.dao = DAO()

    def suspend_d(self, fields='', **kwargs):
        """
        每日停复牌信息
        | Arguments:
        | ts_code(str):   股票代码(可输入多值)
        | suspend_type(str):   停复牌类型：S-停牌,R-复牌
        | trade_date(str):   停复牌日期
        | start_date(str):   停复牌查询开始日期
        | end_date(str):   停复牌查询结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS代码
         trade_date(str)  停复牌日期
         suspend_timing(str)  日内停牌时间段
         suspend_type(str)  停复牌类型：S-停牌，R-复牌
        
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
            "suspend_type": "",
            "trade_date": "",
            "start_date": "",
            "end_date": "",
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
            self.logger.debug("Invoke pro.suspend_d with args: {}".format(kwargs))
            res = self.tushare_api().suspend_d(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_suspend_d', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(SuspendD, 'default_limit', default_limit_ext)
setattr(SuspendD, 'default_cron_express', default_cron_express_ext)
setattr(SuspendD, 'default_order_by', default_order_by_ext)
setattr(SuspendD, 'prepare', prepare_ext)
setattr(SuspendD, 'tushare_parameters', tushare_parameters_ext)
setattr(SuspendD, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    api = SuspendD()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    api.process(ProcessType.INCREASE)    # 同步增量数据
    print(api.suspend_d())    # 数据查询接口
