"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare sz_daily_info接口
获取深圳市场每日交易概况
数据接口-指数-深圳市场每日交易情况  https://tushare.pro/document/2?doc_id=268

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base
from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.sz_daily_info_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareSzDailyInfo(Base):
    __tablename__ = "tushare_sz_daily_info"
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String, index=True, comment='')
    ts_code = Column(String, index=True, comment='市场类型')
    count = Column(Integer, comment='股票个数')
    amount = Column(Float, comment='成交金额')
    vol = Column(Float, comment='成交量')
    total_share = Column(Float, comment='总股本')
    total_mv = Column(Float, comment='总市值')
    float_share = Column(Float, comment='流通股票')
    float_mv = Column(Float, comment='流通市值')


class SzDailyInfo(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_shared_engine(config.get_data_sqlite_driver_url('tushare_sz_daily_info.db'),
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareSzDailyInfo.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['trade_date', 'ts_code', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = [
            "trade_date", "ts_code", "count", "amount", "vol", "total_share", "total_mv", "float_share", "float_mv"
        ]
        TushareDAO.__init__(self, self.engine, session_factory, TushareSzDailyInfo, 'tushare_sz_daily_info.db',
                            'tushare_sz_daily_info', query_fields, entity_fields, config)
        DataProcess.__init__(self, "sz_daily_info", config)
        TuShareBase.__init__(self, "sz_daily_info", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "trade_date",
            "type": "String",
            "comment": ""
        }, {
            "name": "ts_code",
            "type": "String",
            "comment": "市场类型"
        }, {
            "name": "count",
            "type": "Integer",
            "comment": "股票个数"
        }, {
            "name": "amount",
            "type": "Float",
            "comment": "成交金额"
        }, {
            "name": "vol",
            "type": "Float",
            "comment": "成交量"
        }, {
            "name": "total_share",
            "type": "Float",
            "comment": "总股本"
        }, {
            "name": "total_mv",
            "type": "Float",
            "comment": "总市值"
        }, {
            "name": "float_share",
            "type": "Float",
            "comment": "流通股票"
        }, {
            "name": "float_mv",
            "type": "Float",
            "comment": "流通市值"
        }]

    def sz_daily_info(self, fields='', **kwargs):
        """
        获取深圳市场每日交易概况
        | Arguments:
        | trade_date(str):   交易日期
        | ts_code(str):   板块代码
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  
         ts_code(str)  市场类型
         count(int)  股票个数
         amount(float)  成交金额
         vol(float)  成交量
         total_share(float)  总股本
         total_mv(float)  总市值
         float_share(float)  流通股票
         float_mv(float)  流通市值
        
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
        init_args = {"trade_date": "", "ts_code": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.sz_daily_info with args: {}".format(kwargs))
                res = self.tushare_query('sz_daily_info', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_sz_daily_info',
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


setattr(SzDailyInfo, 'default_limit', default_limit_ext)
setattr(SzDailyInfo, 'default_cron_express', default_cron_express_ext)
setattr(SzDailyInfo, 'default_order_by', default_order_by_ext)
setattr(SzDailyInfo, 'prepare', prepare_ext)
setattr(SzDailyInfo, 'query_parameters', query_parameters_ext)
setattr(SzDailyInfo, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.sz_daily_info())

    api = SzDailyInfo(config)
    api.process()    # 同步增量数据
    print(api.sz_daily_info())    # 数据查询接口
