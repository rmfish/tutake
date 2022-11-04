import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao
from tutake.api.dao import DAO
from tutake.api.process_type import ProcessType
from tutake.api.tushare_base import TuShareBase
from tutake.utils.config import config
from tutake.utils.decorator import sleep
"""
Tushare moneyflow接口
数据接口-沪深股票-行情数据-个股资金流向  https://tushare.pro/document/2?doc_id=170
"""

engine = create_engine("%s/%s" % (config['database']['driver_url'], 'tushare_moneyflow.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.moneyflow')


class TushareMoneyflow(Base):
    __tablename__ = "tushare_moneyflow"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, comment='TS代码')
    trade_date = Column(String, comment='交易日期')
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


TushareMoneyflow.__table__.create(bind=engine, checkfirst=True)


class Moneyflow(BaseDao, TuShareBase):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        BaseDao.__init__(self, engine, session_factory, TushareMoneyflow, 'tushare_moneyflow')
        TuShareBase.__init__(self)
        self.dao = DAO()

    def moneyflow(self, **kwargs):
        """
        个股资金流向

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
        args = [
            n for n in [
                'ts_code',
                'trade_date',
                'start_date',
                'end_date',
                'limit',
                'offset',
            ] if n not in ['limit', 'offset']
        ]
        params = {key: kwargs[key] for key in kwargs.keys() & args}
        query = session_factory().query(TushareMoneyflow).filter_by(**params)
        query = query.order_by(text("trade_date desc,ts_code"))
        input_limit = 10000    # 默认10000条 避免导致数据库压力过大
        if kwargs.get('limit') and str(kwargs.get('limit')).isnumeric():
            input_limit = int(kwargs.get('limit'))
            query = query.limit(input_limit)
        if "" != "":
            default_limit = int("")
            if default_limit < input_limit:
                query = query.limit(default_limit)
        if kwargs.get('offset') and str(kwargs.get('offset')).isnumeric():
            query = query.offset(int(kwargs.get('offset')))
        return pd.read_sql(query.statement, query.session.bind)

    def prepare(self, process_type: ProcessType):
        """
        同步历史数据准备工作
        :return:
        """

    def tushare_parameters(self, process_type: ProcessType):
        """
        同步历史数据调用的参数
        :return: list(dict)
        """
        return [{}]

    def param_loop_process(self, process_type: ProcessType, **params):
        """
        每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
        """
        return params

    def process(self, process_type: ProcessType):
        """
        同步历史数据
        :return:
        """
        self.prepare(process_type)
        params = self.tushare_parameters(process_type)
        logger.debug("Process tushare params is {}".format(params))
        if params:
            for param in params:
                new_param = self.param_loop_process(process_type, **param)
                if new_param is None:
                    logger.debug("Skip exec param: {}".format(param))
                    continue
                try:
                    cnt = self.fetch_and_append(process_type, **new_param)
                    logger.debug("Fetch and append {} data, cnt is {}".format("daily", cnt))
                except Exception as err:
                    if err.args[0].startswith("抱歉，您没有访问该接口的权限") or err.args[0].startswith("抱歉，您每天最多访问该接口"):
                        logger.error("Throw exception with param: {} err:{}".format(new_param, err))
                        return
                    else:
                        logger.error("Execute fetch_and_append throw exp. {}".format(err))
                        continue

    def fetch_and_append(self, process_type: ProcessType, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        if len(kwargs.keys()) == 0:
            kwargs = {"ts_code": "", "trade_date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
        # 初始化offset和limit
        if not kwargs.get("limit"):
            kwargs['limit'] = ""
        init_offset = 0
        offset = 0
        if kwargs.get('offset'):
            offset = int(kwargs['offset'])
            init_offset = offset

        kwargs = {
            key: kwargs[key] for key in kwargs.keys() & list([
                'ts_code',
                'trade_date',
                'start_date',
                'end_date',
                'limit',
                'offset',
            ])
        }

        @sleep(timeout=5, time_append=30, retry=20, match="^抱歉，您每分钟最多访问该接口")
        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            logger.debug("Invoke pro.moneyflow with args: {}".format(kwargs))
            fields = [
                "ts_code", "trade_date", "buy_sm_vol", "buy_sm_amount", "sell_sm_vol", "sell_sm_amount", "buy_md_vol",
                "buy_md_amount", "sell_md_vol", "sell_md_amount", "buy_lg_vol", "buy_lg_amount", "sell_lg_vol",
                "sell_lg_amount", "buy_elg_vol", "buy_elg_amount", "sell_elg_vol", "sell_elg_amount", "net_mf_vol",
                "net_mf_amount", "trade_count"
            ]
            res = pro.moneyflow(**kwargs, fields=fields)
            res.to_sql('tushare_moneyflow', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        pro = self.tushare_api()
        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    api = Moneyflow()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.moneyflow())    # 数据查询接口
