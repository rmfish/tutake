"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare stock_company接口
数据接口-沪深股票-基础数据-上市公司基本信息  https://tushare.pro/document/2?doc_id=112

Created on 2022/11/05
@author: rmfish
"""

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

engine = create_engine("%s/%s" % (config['database']['driver_url'], 'tushare_basic_data.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.stock_company')


class TushareStockCompany(Base):
    __tablename__ = "tushare_stock_company"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='股票代码')
    exchange = Column(String, index=True, comment='交易所代码SSE上交所 SZSE深交所')
    chairman = Column(String, comment='法人代表')
    manager = Column(String, comment='总经理')
    secretary = Column(String, comment='董秘')
    reg_capital = Column(Float, comment='注册资本')
    setup_date = Column(String, comment='注册日期')
    province = Column(String, comment='所在省份')
    city = Column(String, comment='所在城市')
    introduction = Column(String, comment='公司介绍')
    website = Column(String, comment='公司主页')
    email = Column(String, comment='电子邮件')
    office = Column(String, comment='办公室')
    ann_date = Column(String, comment='公告日期')
    business_scope = Column(String, comment='经营范围')
    employees = Column(Integer, comment='员工人数')
    main_business = Column(String, comment='主要业务及产品')


TushareStockCompany.__table__.create(bind=engine, checkfirst=True)


class StockCompany(BaseDao, TuShareBase):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        BaseDao.__init__(self, engine, session_factory, TushareStockCompany, 'tushare_stock_company')
        TuShareBase.__init__(self)
        self.dao = DAO()
        self.query_fields = [
            n for n in [
                'ts_code',
                'exchange',
                'status',
                'limit',
                'offset',
            ] if n not in ['limit', 'offset']
        ]
        self.entity_fields = [
            "ts_code", "exchange", "chairman", "manager", "secretary", "reg_capital", "setup_date", "province", "city",
            "introduction", "website", "email", "office", "ann_date", "business_scope", "employees", "main_business"
        ]

    def stock_company(self, fields='', **kwargs):
        """
        
        | Arguments:
        | ts_code(str):   TS股票代码
        | exchange(str):   交易所代码
        | status(str):   状态
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        

        :return: DataFrame
         ts_code(str)  股票代码
         exchange(str)  交易所代码SSE上交所 SZSE深交所
         chairman(str)  法人代表
         manager(str)  总经理
         secretary(str)  董秘
         reg_capital(float)  注册资本
         setup_date(str)  注册日期
         province(str)  所在省份
         city(str)  所在城市
         introduction(str)  公司介绍
         website(str)  公司主页
         email(str)  电子邮件
         office(str)  办公室
         ann_date(str)  公告日期
         business_scope(str)  经营范围
         employees(int)  员工人数
         main_business(str)  主要业务及产品
        
        """
        params = {
            key: kwargs[key]
            for key in kwargs.keys()
            if key in self.query_fields and key is not None and kwargs[key] != ''
        }
        query = session_factory().query(TushareStockCompany).filter_by(**params)
        if fields != '':
            entities = (
                getattr(TushareStockCompany, f.strip()) for f in fields.split(',') if f.strip() in self.entity_fields)
            query = query.with_entities(*entities)
        query = query.order_by(text("ts_code"))
        input_limit = 10000    # 默认10000条 避免导致数据库压力过大
        if kwargs.get('limit') and str(kwargs.get('limit')).isnumeric():
            input_limit = int(kwargs.get('limit'))
            query = query.limit(input_limit)
        if "4500" != "":
            default_limit = int("4500")
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
            kwargs = {"ts_code": "", "exchange": "", "status": "", "limit": "", "offset": ""}
        # 初始化offset和limit
        if not kwargs.get("limit"):
            kwargs['limit'] = "4500"
        init_offset = 0
        offset = 0
        if kwargs.get('offset'):
            offset = int(kwargs['offset'])
            init_offset = offset

        kwargs = {
            key: kwargs[key] for key in kwargs.keys() & list([
                'ts_code',
                'exchange',
                'status',
                'limit',
                'offset',
            ])
        }

        @sleep(timeout=5, time_append=30, retry=20, match="^抱歉，您每分钟最多访问该接口")
        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            logger.debug("Invoke pro.stock_company with args: {}".format(kwargs))
            res = pro.stock_company(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_stock_company', con=engine, if_exists='append', index=False, index_label=['ts_code'])
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
    api = StockCompany()
    api.process(ProcessType.HISTORY)    # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.stock_company())    # 数据查询接口
