"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare hsgt_top10接口
数据接口-沪深股票-行情数据-沪深股通十大成交股  https://tushare.pro/document/2?doc_id=48

@author: rmfish
"""
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao, ProcessException, ProcessPercent
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.hsgt_top10_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_hsgt_top10.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.hsgt_top10')


class TushareHsgtTop10(Base):
    __tablename__ = "tushare_hsgt_top10"
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String, index=True, comment='交易日期')
    ts_code = Column(String, index=True, comment='股票代码')
    name = Column(String, comment='股票名称')
    close = Column(Float, comment='收盘价')
    change = Column(Float, comment='涨跌幅')
    rank = Column(String, comment='资金排名')
    market_type = Column(String, index=True, comment='市场类型（1：沪市 3：深市）')
    amount = Column(Float, comment='成交金额')
    net_amount = Column(Float, comment='净成交金额')
    buy = Column(Float, comment='买入金额')
    sell = Column(Float, comment='卖出金额')


TushareHsgtTop10.__table__.create(bind=engine, checkfirst=True)


class HsgtTop10(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        BaseDao.__init__(self, engine, session_factory, TushareHsgtTop10, 'tushare_hsgt_top10')
        TuShareBase.__init__(self)
        self.dao = DAO()
        self.query_fields = [
            n for n in [
                'ts_code',
                'trade_date',
                'start_date',
                'end_date',
                'market_type',
                'limit',
                'offset',
            ] if n not in ['limit', 'offset']
        ]
        self.entity_fields = [
            "trade_date", "ts_code", "name", "close", "change", "rank", "market_type", "amount", "net_amount", "buy",
            "sell"
        ]

    def hsgt_top10(self, fields='', **kwargs):
        """
        获取沪股通、深股通每日前十大成交股数据
        | Arguments:
        | ts_code(str):   股票代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | market_type(str):   市场类型（1：沪市 3：深市）
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        

        :return: DataFrame
         trade_date(str)  交易日期
         ts_code(str)  股票代码
         name(str)  股票名称
         close(float)  收盘价
         change(float)  涨跌幅
         rank(str)  资金排名
         market_type(str)  市场类型（1：沪市 3：深市）
         amount(float)  成交金额
         net_amount(float)  净成交金额
         buy(float)  买入金额
         sell(float)  卖出金额
        
        """
        params = {
            key: kwargs[key]
            for key in kwargs.keys()
            if key in self.query_fields and key is not None and kwargs[key] != ''
        }
        query = session_factory().query(TushareHsgtTop10).filter_by(**params)
        if fields != '':
            entities = (
                getattr(TushareHsgtTop10, f.strip()) for f in fields.split(',') if f.strip() in self.entity_fields)
            query = query.with_entities(*entities)
        query = query.order_by(text("trade_date desc,ts_code"))
        input_limit = 10000    # 默认10000条 避免导致数据库压力过大
        if kwargs.get('limit') and str(kwargs.get('limit')).isnumeric():
            input_limit = int(kwargs.get('limit'))
            query = query.limit(input_limit)
        if self.default_limit() != "":
            default_limit = int(self.default_limit())
            if default_limit < input_limit:
                query = query.limit(default_limit)
        if kwargs.get('offset') and str(kwargs.get('offset')).isnumeric():
            query = query.offset(int(kwargs.get('offset')))
        df = pd.read_sql(query.statement, query.session.bind)
        return df.drop(['id'], axis=1, errors='ignore')

    def default_limit(self) -> str:
        return ""

    def prepare(self, process_type: ProcessType):
        """
        同步历史数据准备工作
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
            percent = ProcessPercent(len(params))

            def action(param):
                new_param = self.param_loop_process(process_type, **param)
                if new_param is None:
                    logger.debug("[{}] Skip exec param: {}".format(percent.format(), param))
                    return
                try:
                    cnt = self.fetch_and_append(process_type, **new_param)
                    logger.info("[{}] Fetch and append {} data, cnt is {} . param is {}".format(
                        percent.format(), "hsgt_top10", cnt, param))
                except Exception as err:
                    if isinstance(err.args[0], str) and (err.args[0].startswith("抱歉，您没有访问该接口的权限")
                                                         or err.args[0].startswith("抱歉，您每天最多访问该接口")):
                        logger.error("Throw exception with param: {} err:{}".format(new_param, err))
                        raise Exception("Exit with tushare api flow limit. {}", err.args[0])
                    else:
                        logger.error("Execute fetch_and_append throw exp. {}".format(err))
                        return ProcessException(param=new_param, cause=err)

            with ThreadPoolExecutor(max_workers=tutake_config.get_process_thread_cnt()) as pool:
                repeat_params = []
                for result in pool.map(action, params):
                    percent.finish()
                    if isinstance(result, ProcessException):
                        repeat_params.append(result.param)
                    elif isinstance(result, Exception):
                        return
                # 过程中出现错误的，需要补偿执行
                cnt = len(repeat_params)
                if cnt > 0:
                    percent = ProcessPercent(cnt)
                    logger.warning("Failed process with exception.Cnt {}  All params is {}".format(cnt, repeat_params))
                    for p in repeat_params:
                        action(p)
                        percent.finish()

    def fetch_and_append(self, process_type: ProcessType, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        if len(kwargs.keys()) == 0:
            kwargs = {
                "ts_code": "",
                "trade_date": "",
                "start_date": "",
                "end_date": "",
                "market_type": "",
                "limit": "",
                "offset": ""
            }
        # 初始化offset和limit
        if not kwargs.get("limit"):
            kwargs['limit'] = self.default_limit()
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
                'market_type',
                'limit',
                'offset',
            ])
        }

        @sleep(timeout=61, time_append=60, retry=20, match="^抱歉，您每分钟最多访问该接口")
        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            logger.debug("Invoke pro.hsgt_top10 with args: {}".format(kwargs))
            res = self.tushare_api().hsgt_top10(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_hsgt_top10', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(HsgtTop10, 'default_limit', default_limit_ext)
setattr(HsgtTop10, 'prepare', prepare_ext)
setattr(HsgtTop10, 'tushare_parameters', tushare_parameters_ext)
setattr(HsgtTop10, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)    # 显示列数
    pd.set_option('display.width', 1000)
    logger.setLevel(logging.INFO)
    api = HsgtTop10()
    api.process(ProcessType.HISTORY)    # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.hsgt_top10())    # 数据查询接口
