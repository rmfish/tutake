"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare ggt_daily接口
获取港股通每日成交信息，数据从2014年开始
数据接口-沪深股票-行情数据-港股通每日成交统计  https://tushare.pro/document/2?doc_id=196

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.ggt_daily_ext import *
from tutake.api.ts.base_dao import BaseDao, Base
from tutake.api.ts.dao import DAO
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareGgtDaily(Base):
    __tablename__ = "tushare_ggt_daily"
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String, index=True, comment='交易日期')
    buy_amount = Column(Float, comment='买入成交金额（亿元）')
    buy_volume = Column(Float, comment='买入成交笔数（万笔）')
    sell_amount = Column(Float, comment='卖出成交金额（亿元）')
    sell_volume = Column(Float, comment='卖出成交笔数（万笔）')


class GgtDaily(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine("%s/%s" % (config.get_data_sqlite_driver_url(), 'tushare_ggt_daily.db'),
                                    connect_args={'check_same_thread': False})
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareGgtDaily.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['trade_date', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = ["trade_date", "buy_amount", "buy_volume", "sell_amount", "sell_volume"]
        BaseDao.__init__(self, self.engine, session_factory, TushareGgtDaily, 'tushare_ggt_daily', query_fields,
                         entity_fields)
        DataProcess.__init__(self, "ggt_daily", config)
        TuShareBase.__init__(self, "ggt_daily", config, 5000)
        self.dao = DAO(config)

    def ggt_daily(self, fields='', **kwargs):
        """
        获取港股通每日成交信息，数据从2014年开始
        | Arguments:
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  交易日期
         buy_amount(float)  买入成交金额（亿元）
         buy_volume(float)  买入成交笔数（万笔）
         sell_amount(float)  卖出成交金额（亿元）
         sell_volume(float)  卖出成交笔数（万笔）
        
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
        init_args = {"trade_date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.ggt_daily with args: {}".format(kwargs))
                res = self.tushare_query('ggt_daily', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_ggt_daily',
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


setattr(GgtDaily, 'default_limit', default_limit_ext)
setattr(GgtDaily, 'default_cron_express', default_cron_express_ext)
setattr(GgtDaily, 'default_order_by', default_order_by_ext)
setattr(GgtDaily, 'prepare', prepare_ext)
setattr(GgtDaily, 'tushare_parameters', tushare_parameters_ext)
setattr(GgtDaily, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.ggt_daily())

    api = GgtDaily(config)
    api.process()    # 同步增量数据
    print(api.ggt_daily())    # 数据查询接口
