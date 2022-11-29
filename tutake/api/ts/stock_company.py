"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare stock_company接口
获取上市公司基础信息
数据接口-沪深股票-基础数据-上市公司基本信息  https://tushare.pro/document/2?doc_id=112

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.stock_company_ext import *
from tutake.api.ts.base_dao import BaseDao, Base
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


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


class StockCompany(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine("%s/%s" % (config.get_data_sqlite_driver_url(), 'tushare_basic_data.db'),
                                    connect_args={'check_same_thread': False})
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareStockCompany.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'exchange', 'status', 'limit', 'offset']
        entity_fields = [
            "ts_code", "exchange", "chairman", "manager", "secretary", "reg_capital", "setup_date", "province", "city",
            "introduction", "website", "email", "office", "ann_date", "business_scope", "employees", "main_business"
        ]
        BaseDao.__init__(self, self.engine, session_factory, TushareStockCompany, 'tushare_stock_company', query_fields,
                         entity_fields, config)
        DataProcess.__init__(self, "stock_company", config)
        TuShareBase.__init__(self, "stock_company", config, 120)
        self.api = TushareAPI(config)

    def stock_company(self, fields='', **kwargs):
        """
        获取上市公司基础信息
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
        init_args = {"ts_code": "", "exchange": "", "status": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.stock_company with args: {}".format(kwargs))
                res = self.tushare_query('stock_company', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_stock_company',
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


setattr(StockCompany, 'default_limit', default_limit_ext)
setattr(StockCompany, 'default_cron_express', default_cron_express_ext)
setattr(StockCompany, 'default_order_by', default_order_by_ext)
setattr(StockCompany, 'prepare', prepare_ext)
setattr(StockCompany, 'tushare_parameters', tushare_parameters_ext)
setattr(StockCompany, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.stock_company())

    api = StockCompany(config)
    api.process()    # 同步增量数据
    print(api.stock_company())    # 数据查询接口
