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
"""
Tushare ggt_monthly接口
数据接口-沪深股票-行情数据-港股通每月成交统计  https://tushare.pro/document/2?doc_id=197
"""

engine = create_engine("%s/%s" % (config['database']['driver_url'], 'tushare_ggt_monthly.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.ggt_monthly')


class TushareGgtMonthly(Base):
    __tablename__ = "tushare_ggt_monthly"
    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(String, comment='交易日期')
    day_buy_amt = Column(Float, comment='当月日均买入成交金额（亿元）')
    day_buy_vol = Column(Float, comment='当月日均买入成交笔数（万笔）')
    day_sell_amt = Column(Float, comment='当月日均卖出成交金额（亿元）')
    day_sell_vol = Column(Float, comment='当月日均卖出成交笔数（万笔）')
    total_buy_amt = Column(Float, comment='总买入成交金额（亿元）')
    total_buy_vol = Column(Float, comment='总买入成交笔数（万笔）')
    total_sell_amt = Column(Float, comment='总卖出成交金额（亿元）')
    total_sell_vol = Column(Float, comment='总卖出成交笔数（万笔）')


TushareGgtMonthly.__table__.create(bind=engine, checkfirst=True)


class GgtMonthly(BaseDao, TuShareBase):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        BaseDao.__init__(self, engine, session_factory, TushareGgtMonthly, 'tushare_ggt_monthly')
        TuShareBase.__init__(self)
        self.dao = DAO()

    def ggt_monthly(self, **kwargs):
        """
        港股通每月成交统计

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
        args = [n for n in [
            'month',
            'start_month',
            'end_month',
            'limit',
            'offset',
        ] if n not in ['limit', 'offset']]
        params = {key: kwargs[key] for key in kwargs.keys() & args}
        query = session_factory().query(TushareGgtMonthly).filter_by(**params)

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
                    continue

    def fetch_and_append(self, process_type: ProcessType, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        if len(kwargs.keys()) == 0:
            kwargs = {"month": "", "start_month": "", "end_month": "", "limit": "", "offset": ""}
        # 初始化offset和limit
        if not kwargs.get("limit"):
            kwargs['limit'] = ""
        init_offset = 0
        offset = 0
        if kwargs.get('offset') and kwargs.get('offset').isnumeric():
            offset = int(kwargs['offset'])
            init_offset = offset

        kwargs = {
            key: kwargs[key] for key in kwargs.keys() & list([
                'month',
                'start_month',
                'end_month',
                'limit',
                'offset',
            ])
        }

        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            logger.debug("Invoke pro.ggt_monthly with args: {}".format(kwargs))
            fields = [
                "month", "day_buy_amt", "day_buy_vol", "day_sell_amt", "day_sell_vol", "total_buy_amt", "total_buy_vol",
                "total_sell_amt", "total_sell_vol"
            ]
            res = pro.ggt_monthly(**kwargs, fields=fields)
            res.to_sql('tushare_ggt_monthly', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        pro = self.tushare_api()
        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and df.shape[0] == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    api = GgtMonthly()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.ggt_monthly())    # 数据查询接口
