"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare new_share接口
数据接口-沪深股票-基础数据-IPO新股上市  https://tushare.pro/document/2?doc_id=123

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
from tutake.api.tushare.extends.new_share_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_basic_data.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.new_share')


class TushareNewShare(Base):
    __tablename__ = "tushare_new_share"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, comment='TS股票代码')
    sub_code = Column(String, comment='申购代码')
    name = Column(String, comment='名称')
    ipo_date = Column(String, comment='上网发行日期')
    issue_date = Column(String, comment='上市日期')
    amount = Column(Float, comment='发行总量（万股）')
    market_amount = Column(Float, comment='上网发行总量（万股）')
    price = Column(Float, comment='发行价格')
    pe = Column(Float, comment='市盈率')
    limit_amount = Column(Float, comment='个人申购上限（万股）')
    funds = Column(Float, comment='募集资金（亿元）')
    ballot = Column(Float, comment='中签率')


TushareNewShare.__table__.create(bind=engine, checkfirst=True)


class NewShare(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        BaseDao.__init__(self, engine, session_factory, TushareNewShare, 'tushare_new_share')
        TuShareBase.__init__(self)
        self.dao = DAO()
        self.query_fields = [n for n in [
            'start_date',
            'end_date',
            'limit',
            'offset',
        ] if n not in ['limit', 'offset']]
        self.entity_fields = [
            "ts_code", "sub_code", "name", "ipo_date", "issue_date", "amount", "market_amount", "price", "pe",
            "limit_amount", "funds", "ballot"
        ]

    def new_share(self, fields='', **kwargs):
        """
        新股上市
        | Arguments:
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        

        :return: DataFrame
         ts_code(str)  TS股票代码
         sub_code(str)  申购代码
         name(str)  名称
         ipo_date(str)  上网发行日期
         issue_date(str)  上市日期
         amount(float)  发行总量（万股）
         market_amount(float)  上网发行总量（万股）
         price(float)  发行价格
         pe(float)  市盈率
         limit_amount(float)  个人申购上限（万股）
         funds(float)  募集资金（亿元）
         ballot(float)  中签率
        
        """
        params = {
            key: kwargs[key]
            for key in kwargs.keys()
            if key in self.query_fields and key is not None and kwargs[key] != ''
        }
        query = session_factory().query(TushareNewShare).filter_by(**params)
        if fields != '':
            entities = (
                getattr(TushareNewShare, f.strip()) for f in fields.split(',') if f.strip() in self.entity_fields)
            query = query.with_entities(*entities)
        query = query.order_by(text("ts_code"))
        input_limit = 10000    # 默认10000条 避免导致数据库压力过大
        if kwargs.get('limit') and str(kwargs.get('limit')).isnumeric():
            input_limit = int(kwargs.get('limit'))
            query = query.limit(input_limit)
        if "2000" != "":
            default_limit = int("2000")
            if default_limit < input_limit:
                query = query.limit(default_limit)
        if kwargs.get('offset') and str(kwargs.get('offset')).isnumeric():
            query = query.offset(int(kwargs.get('offset')))
        df = pd.read_sql(query.statement, query.session.bind)
        return df.drop(['id'], axis=1, errors='ignore')

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
                        percent.format(), "new_share", cnt, param))
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
            kwargs = {"start_date": "", "end_date": "", "limit": "", "offset": ""}
        # 初始化offset和limit
        if not kwargs.get("limit"):
            kwargs['limit'] = "2000"
        init_offset = 0
        offset = 0
        if kwargs.get('offset'):
            offset = int(kwargs['offset'])
            init_offset = offset

        kwargs = {key: kwargs[key] for key in kwargs.keys() & list([
            'start_date',
            'end_date',
            'limit',
            'offset',
        ])}

        @sleep(timeout=5, time_append=30, retry=20, match="^抱歉，您每分钟最多访问该接口")
        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            logger.debug("Invoke pro.new_share with args: {}".format(kwargs))
            res = pro.new_share(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_new_share', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        pro = self.tushare_api()
        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(NewShare, 'prepare', prepare_ext)
setattr(NewShare, 'tushare_parameters', tushare_parameters_ext)
setattr(NewShare, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)    # 显示列数
    pd.set_option('display.width', 1000)
    logger.setLevel(logging.INFO)
    api = NewShare()
    api.process(ProcessType.HISTORY)    # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.new_share())    # 数据查询接口
