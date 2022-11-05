# This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.process_type import ProcessType
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import config
from tutake.utils.decorator import sleep
"""
Tushare index_basic接口
数据接口-指数-指数基本信息  https://tushare.pro/document/2?doc_id=94
"""

engine = create_engine("%s/%s" % (config['database']['driver_url'], 'tushare_index_basic.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.index_basic')


class TushareIndexBasic(Base):
    __tablename__ = "tushare_index_basic"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='TS代码')
    name = Column(String, index=True, comment='简称')
    fullname = Column(String, comment='指数全称')
    market = Column(String, index=True, comment='市场')
    publisher = Column(String, index=True, comment='发布方')
    index_type = Column(String, comment='指数风格')
    category = Column(String, index=True, comment='指数类别')
    base_date = Column(String, comment='基期')
    base_point = Column(Float, comment='基点')
    list_date = Column(String, comment='发布日期')
    weight_rule = Column(String, comment='加权方式')
    desc = Column(String, comment='描述')
    exp_date = Column(String, comment='终止日期')


TushareIndexBasic.__table__.create(bind=engine, checkfirst=True)


class IndexBasic(BaseDao, TuShareBase):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        BaseDao.__init__(self, engine, session_factory, TushareIndexBasic, 'tushare_index_basic')
        TuShareBase.__init__(self)
        self.dao = DAO()

    def index_basic(self, **kwargs):
        """
        

        | Arguments:
        | ts_code(str):   指数代码
        | market(str):   交易所或服务商
        | publisher(str):   发布商
        | category(str):   指数类别
        | name(str):   指数名称
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        

        :return: DataFrame
         ts_code(str)  TS代码
         name(str)  简称
         fullname(str)  指数全称
         market(str)  市场
         publisher(str)  发布方
         index_type(str)  指数风格
         category(str)  指数类别
         base_date(str)  基期
         base_point(float)  基点
         list_date(str)  发布日期
         weight_rule(str)  加权方式
         desc(str)  描述
         exp_date(str)  终止日期
        
        """
        args = [
            n for n in [
                'ts_code',
                'market',
                'publisher',
                'category',
                'name',
                'limit',
                'offset',
            ] if n not in ['limit', 'offset']
        ]
        params = {key: kwargs[key] for key in kwargs.keys() & args}
        query = session_factory().query(TushareIndexBasic).filter_by(**params)
        query = query.order_by(text("ts_code"))
        input_limit = 10000    # 默认10000条 避免导致数据库压力过大
        if kwargs.get('limit') and str(kwargs.get('limit')).isnumeric():
            input_limit = int(kwargs.get('limit'))
            query = query.limit(input_limit)
        if "8000" != "":
            default_limit = int("8000")
            if default_limit < input_limit:
                query = query.limit(default_limit)
        if kwargs.get('offset') and str(kwargs.get('offset')).isnumeric():
            query = query.offset(int(kwargs.get('offset')))
        df = pd.read_sql(query.statement, query.session.bind)
        return df.drop(['id'], axis=1, errors='ignore')

    def prepare(self, process_type: ProcessType):
        """
        同步历史数据准备工作
        :return:
        """
        logger.warning("Delete all data of {}")
        self.delete_all()

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
            kwargs = {
                "ts_code": "",
                "market": "",
                "publisher": "",
                "category": "",
                "name": "",
                "limit": "",
                "offset": ""
            }
        # 初始化offset和limit
        if not kwargs.get("limit"):
            kwargs['limit'] = "8000"
        init_offset = 0
        offset = 0
        if kwargs.get('offset'):
            offset = int(kwargs['offset'])
            init_offset = offset

        kwargs = {
            key: kwargs[key] for key in kwargs.keys() & list([
                'ts_code',
                'market',
                'publisher',
                'category',
                'name',
                'limit',
                'offset',
            ])
        }

        @sleep(timeout=5, time_append=30, retry=20, match="^抱歉，您每分钟最多访问该接口")
        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            logger.debug("Invoke pro.index_basic with args: {}".format(kwargs))
            fields = [
                "ts_code", "name", "fullname", "market", "publisher", "index_type", "category", "base_date",
                "base_point", "list_date", "weight_rule", "desc", "exp_date"
            ]
            res = pro.index_basic(**kwargs, fields=fields)
            res.to_sql('tushare_index_basic', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        pro = self.tushare_api()
        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)    # 显示列数
    pd.set_option('display.width', 1000)
    logger.setLevel(logging.DEBUG)
    api = IndexBasic()
    api.process(ProcessType.HISTORY)    # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.index_basic())    # 数据查询接口
