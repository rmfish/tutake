"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare suspend_d接口
每日停复牌信息
数据接口-沪深股票-行情数据-每日停复牌信息  https://tushare.pro/document/2?doc_id=214

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base
from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.suspend_d_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareSuspendD(Base):
    __tablename__ = "tushare_suspend_d"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='TS代码')
    trade_date = Column(String, index=True, comment='停复牌日期')
    suspend_timing = Column(String, comment='日内停牌时间段')
    suspend_type = Column(String, index=True, comment='停复牌类型：S-停牌，R-复牌')


class SuspendD(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_shared_engine(config.get_data_sqlite_driver_url('tushare_stock.db'),
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareSuspendD.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'suspend_type', 'trade_date', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = ["ts_code", "trade_date", "suspend_timing", "suspend_type"]
        TushareDAO.__init__(self, self.engine, session_factory, TushareSuspendD, 'tushare_stock.db',
                            'tushare_suspend_d', query_fields, entity_fields, config)
        DataProcess.__init__(self, "suspend_d", config)
        TuShareBase.__init__(self, "suspend_d", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS代码"
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": "停复牌日期"
        }, {
            "name": "suspend_timing",
            "type": "String",
            "comment": "日内停牌时间段"
        }, {
            "name": "suspend_type",
            "type": "String",
            "comment": "停复牌类型：S-停牌，R-复牌"
        }]

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

        def fetch_save(offset_val=0):
            try:
                kwargs['offset'] = str(offset_val)
                self.logger.debug("Invoke pro.suspend_d with args: {}".format(kwargs))
                res = self.tushare_query('suspend_d', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_suspend_d',
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


setattr(SuspendD, 'default_limit', default_limit_ext)
setattr(SuspendD, 'default_cron_express', default_cron_express_ext)
setattr(SuspendD, 'default_order_by', default_order_by_ext)
setattr(SuspendD, 'prepare', prepare_ext)
setattr(SuspendD, 'query_parameters', query_parameters_ext)
setattr(SuspendD, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.suspend_d())

    api = SuspendD(config)
    api.process()    # 同步增量数据
    print(api.suspend_d())    # 数据查询接口
