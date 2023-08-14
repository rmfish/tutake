"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare moneyflow_hsgt接口
获取沪股通、深股通、港股通每日资金流向数据
数据接口-沪深股票-行情数据-沪深港通资金流向  https://tushare.pro/document/2?doc_id=47

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base
from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.moneyflow_hsgt_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareMoneyflowHsgt(Base):
    __tablename__ = "tushare_moneyflow_hsgt"
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String, index=True, comment='交易日期')
    ggt_ss = Column(String, comment='港股通（上海）')
    ggt_sz = Column(String, comment='港股通（深圳）')
    hgt = Column(String, comment='沪股通')
    sgt = Column(String, comment='深股通')
    north_money = Column(String, comment='北向资金')
    south_money = Column(String, comment='南向资金')


class MoneyflowHsgt(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_shared_engine(config.get_data_sqlite_driver_url('tushare_moneyflow.db'),
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareMoneyflowHsgt.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['trade_date', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = ["trade_date", "ggt_ss", "ggt_sz", "hgt", "sgt", "north_money", "south_money"]
        TushareDAO.__init__(self, self.engine, session_factory, TushareMoneyflowHsgt, 'tushare_moneyflow.db',
                            'tushare_moneyflow_hsgt', query_fields, entity_fields, config)
        DataProcess.__init__(self, "moneyflow_hsgt", config)
        TuShareBase.__init__(self, "moneyflow_hsgt", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "ggt_ss",
            "type": "String",
            "comment": "港股通（上海）"
        }, {
            "name": "ggt_sz",
            "type": "String",
            "comment": "港股通（深圳）"
        }, {
            "name": "hgt",
            "type": "String",
            "comment": "沪股通"
        }, {
            "name": "sgt",
            "type": "String",
            "comment": "深股通"
        }, {
            "name": "north_money",
            "type": "String",
            "comment": "北向资金"
        }, {
            "name": "south_money",
            "type": "String",
            "comment": "南向资金"
        }]

    def moneyflow_hsgt(self, fields='', **kwargs):
        """
        获取沪股通、深股通、港股通每日资金流向数据
        | Arguments:
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  交易日期
         ggt_ss(str)  港股通（上海）
         ggt_sz(str)  港股通（深圳）
         hgt(str)  沪股通
         sgt(str)  深股通
         north_money(str)  北向资金
         south_money(str)  南向资金
        
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
                self.logger.debug("Invoke pro.moneyflow_hsgt with args: {}".format(kwargs))
                res = self.tushare_query('moneyflow_hsgt', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_moneyflow_hsgt',
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


setattr(MoneyflowHsgt, 'default_limit', default_limit_ext)
setattr(MoneyflowHsgt, 'default_cron_express', default_cron_express_ext)
setattr(MoneyflowHsgt, 'default_order_by', default_order_by_ext)
setattr(MoneyflowHsgt, 'prepare', prepare_ext)
setattr(MoneyflowHsgt, 'query_parameters', query_parameters_ext)
setattr(MoneyflowHsgt, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.moneyflow_hsgt(trade_date='20221118'))

    api = MoneyflowHsgt(config)
    api.process()    # 同步增量数据
    print(api.moneyflow_hsgt(trade_date='20221118'))    # 数据查询接口
