"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare weekly接口
获取A股周线行情,全部历史，每周五15点～17点之间更新
数据接口-沪深股票-行情数据-周线行情  https://tushare.pro/document/2?doc_id=144

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.weekly_ext import *
from tutake.api.ts.base_dao import BaseDao, Base
from tutake.api.ts.dao import DAO
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareWeekly(Base):
    __tablename__ = "tushare_weekly"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='')
    trade_date = Column(String, index=True, comment='')
    close = Column(Float, comment='')
    open = Column(Float, comment='')
    high = Column(Float, comment='')
    low = Column(Float, comment='')
    pre_close = Column(Float, comment='')
    change = Column(Float, comment='')
    pct_chg = Column(Float, comment='')
    vol = Column(Float, comment='')
    amount = Column(Float, comment='')


class Weekly(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine("%s/%s" % (config.get_data_sqlite_driver_url(), 'tushare_weekly.db'),
                                    connect_args={'check_same_thread': False})
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareWeekly.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = [
            "ts_code", "trade_date", "close", "open", "high", "low", "pre_close", "change", "pct_chg", "vol", "amount"
        ]
        BaseDao.__init__(self, self.engine, session_factory, TushareWeekly, 'tushare_weekly', query_fields,
                         entity_fields, config)
        DataProcess.__init__(self, "weekly", config)
        TuShareBase.__init__(self, "weekly", config, 600)
        self.dao = DAO(config)

    def weekly(self, fields='', **kwargs):
        """
        获取A股周线行情,全部历史，每周五15点～17点之间更新
        | Arguments:
        | ts_code(str):   TS代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  
         trade_date(str)  
         close(float)  
         open(float)  
         high(float)  
         low(float)  
         pre_close(float)  
         change(float)  
         pct_chg(float)  
         vol(float)  
         amount(float)  
        
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
        init_args = {"ts_code": "", "trade_date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.weekly with args: {}".format(kwargs))
                res = self.tushare_query('weekly', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_weekly', con=self.engine, if_exists='append', index=False, index_label=['ts_code'])
                return res
            except Exception as err:
                raise ProcessException(kwargs, err)

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(Weekly, 'default_limit', default_limit_ext)
setattr(Weekly, 'default_cron_express', default_cron_express_ext)
setattr(Weekly, 'default_order_by', default_order_by_ext)
setattr(Weekly, 'prepare', prepare_ext)
setattr(Weekly, 'tushare_parameters', tushare_parameters_ext)
setattr(Weekly, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.weekly())

    api = Weekly(config)
    api.process()    # 同步增量数据
    print(api.weekly())    # 数据查询接口
