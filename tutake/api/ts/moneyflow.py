"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare moneyflow接口
获取沪深A股票资金流向数据，分析大单小单成交情况，用于判别资金动向，每日晚19点更新
数据接口-沪深股票-行情数据-个股资金流向  https://tushare.pro/document/2?doc_id=170

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base
from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.moneyflow_ext import *
from tutake.api.ts.tushare_dao import TushareDAO
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareMoneyflow(Base):
    __tablename__ = "tushare_moneyflow"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='TS代码')
    trade_date = Column(String, index=True, comment='交易日期')
    buy_sm_vol = Column(Integer, comment='小单买入量（手）')
    buy_sm_amount = Column(Float, comment='小单买入金额（万元）')
    sell_sm_vol = Column(Integer, comment='小单卖出量（手）')
    sell_sm_amount = Column(Float, comment='小单卖出金额（万元）')
    buy_md_vol = Column(Integer, comment='中单买入量（手）')
    buy_md_amount = Column(Float, comment='中单买入金额（万元）')
    sell_md_vol = Column(Integer, comment='中单卖出量（手）')
    sell_md_amount = Column(Float, comment='中单卖出金额（万元）')
    buy_lg_vol = Column(Integer, comment='大单买入量（手）')
    buy_lg_amount = Column(Float, comment='大单买入金额（万元）')
    sell_lg_vol = Column(Integer, comment='大单卖出量（手）')
    sell_lg_amount = Column(Float, comment='大单卖出金额（万元）')
    buy_elg_vol = Column(Integer, comment='特大单买入量（手）')
    buy_elg_amount = Column(Float, comment='特大单买入金额（万元）')
    sell_elg_vol = Column(Integer, comment='特大单卖出量（手）')
    sell_elg_amount = Column(Float, comment='特大单卖出金额（万元）')
    net_mf_vol = Column(Integer, comment='净流入量（手）')
    net_mf_amount = Column(Float, comment='净流入额（万元）')
    trade_count = Column(Integer, comment='交易笔数')


class Moneyflow(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine(config.get_data_sqlite_driver_url('tushare_moneyflow.db'),
                                    connect_args={'check_same_thread': False})
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareMoneyflow.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = [
            "ts_code", "trade_date", "buy_sm_vol", "buy_sm_amount", "sell_sm_vol", "sell_sm_amount", "buy_md_vol",
            "buy_md_amount", "sell_md_vol", "sell_md_amount", "buy_lg_vol", "buy_lg_amount", "sell_lg_vol",
            "sell_lg_amount", "buy_elg_vol", "buy_elg_amount", "sell_elg_vol", "sell_elg_amount", "net_mf_vol",
            "net_mf_amount", "trade_count"
        ]
        TushareDAO.__init__(self, self.engine, session_factory, TushareMoneyflow, 'tushare_moneyflow', query_fields,
                            entity_fields, config)
        DataProcess.__init__(self, "moneyflow", config)
        TuShareBase.__init__(self, "moneyflow", config, 2000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS代码"
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "buy_sm_vol",
            "type": "Integer",
            "comment": "小单买入量（手）"
        }, {
            "name": "buy_sm_amount",
            "type": "Float",
            "comment": "小单买入金额（万元）"
        }, {
            "name": "sell_sm_vol",
            "type": "Integer",
            "comment": "小单卖出量（手）"
        }, {
            "name": "sell_sm_amount",
            "type": "Float",
            "comment": "小单卖出金额（万元）"
        }, {
            "name": "buy_md_vol",
            "type": "Integer",
            "comment": "中单买入量（手）"
        }, {
            "name": "buy_md_amount",
            "type": "Float",
            "comment": "中单买入金额（万元）"
        }, {
            "name": "sell_md_vol",
            "type": "Integer",
            "comment": "中单卖出量（手）"
        }, {
            "name": "sell_md_amount",
            "type": "Float",
            "comment": "中单卖出金额（万元）"
        }, {
            "name": "buy_lg_vol",
            "type": "Integer",
            "comment": "大单买入量（手）"
        }, {
            "name": "buy_lg_amount",
            "type": "Float",
            "comment": "大单买入金额（万元）"
        }, {
            "name": "sell_lg_vol",
            "type": "Integer",
            "comment": "大单卖出量（手）"
        }, {
            "name": "sell_lg_amount",
            "type": "Float",
            "comment": "大单卖出金额（万元）"
        }, {
            "name": "buy_elg_vol",
            "type": "Integer",
            "comment": "特大单买入量（手）"
        }, {
            "name": "buy_elg_amount",
            "type": "Float",
            "comment": "特大单买入金额（万元）"
        }, {
            "name": "sell_elg_vol",
            "type": "Integer",
            "comment": "特大单卖出量（手）"
        }, {
            "name": "sell_elg_amount",
            "type": "Float",
            "comment": "特大单卖出金额（万元）"
        }, {
            "name": "net_mf_vol",
            "type": "Integer",
            "comment": "净流入量（手）"
        }, {
            "name": "net_mf_amount",
            "type": "Float",
            "comment": "净流入额（万元）"
        }, {
            "name": "trade_count",
            "type": "Integer",
            "comment": "交易笔数"
        }]

    def moneyflow(self, fields='', **kwargs):
        """
        获取沪深A股票资金流向数据，分析大单小单成交情况，用于判别资金动向，每日晚19点更新
        | Arguments:
        | ts_code(str):   股票代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS代码
         trade_date(str)  交易日期
         buy_sm_vol(int)  小单买入量（手）
         buy_sm_amount(float)  小单买入金额（万元）
         sell_sm_vol(int)  小单卖出量（手）
         sell_sm_amount(float)  小单卖出金额（万元）
         buy_md_vol(int)  中单买入量（手）
         buy_md_amount(float)  中单买入金额（万元）
         sell_md_vol(int)  中单卖出量（手）
         sell_md_amount(float)  中单卖出金额（万元）
         buy_lg_vol(int)  大单买入量（手）
         buy_lg_amount(float)  大单买入金额（万元）
         sell_lg_vol(int)  大单卖出量（手）
         sell_lg_amount(float)  大单卖出金额（万元）
         buy_elg_vol(int)  特大单买入量（手）
         buy_elg_amount(float)  特大单买入金额（万元）
         sell_elg_vol(int)  特大单卖出量（手）
         sell_elg_amount(float)  特大单卖出金额（万元）
         net_mf_vol(int)  净流入量（手）
         net_mf_amount(float)  净流入额（万元）
         trade_count(int)  交易笔数
        
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
                self.logger.debug("Invoke pro.moneyflow with args: {}".format(kwargs))
                res = self.tushare_query('moneyflow', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_moneyflow',
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


setattr(Moneyflow, 'default_limit', default_limit_ext)
setattr(Moneyflow, 'default_cron_express', default_cron_express_ext)
setattr(Moneyflow, 'default_order_by', default_order_by_ext)
setattr(Moneyflow, 'prepare', prepare_ext)
setattr(Moneyflow, 'query_parameters', query_parameters_ext)
setattr(Moneyflow, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.moneyflow(ts_code='000001.SH'))

    api = Moneyflow(config)
    api.process()    # 同步增量数据
    print(api.moneyflow(ts_code='000001.SH'))    # 数据查询接口
