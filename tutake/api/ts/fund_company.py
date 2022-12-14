"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_company接口
获取公募基金管理人列表
数据接口-公募基金-基金管理人  https://tushare.pro/document/2?doc_id=118

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base
from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.fund_company_ext import *
from tutake.api.ts.tushare_dao import TushareDAO
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareFundCompany(Base):
    __tablename__ = "tushare_fund_company"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, comment='公司名称')
    shortname = Column(String, comment='简称')
    short_enname = Column(String, comment='英文缩写')
    province = Column(String, comment='省份')
    city = Column(String, comment='城市')
    address = Column(String, comment='注册地址')
    phone = Column(String, comment='电话')
    office = Column(String, comment='办公地址')
    website = Column(String, comment='公司网址')
    chairman = Column(String, comment='法人代表')
    manager = Column(String, comment='总经理')
    reg_capital = Column(Float, comment='注册资本')
    setup_date = Column(String, index=True, comment='成立日期')
    end_date = Column(String, comment='公司终止日期')
    employees = Column(Float, comment='员工总数')
    main_business = Column(String, comment='主要产品及业务')
    org_code = Column(String, comment='组织机构代码')
    credit_code = Column(String, comment='统一社会信用代码')


class FundCompany(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine(config.get_data_sqlite_driver_url('tushare_fund_company.db'),
                                    connect_args={'check_same_thread': False})
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareFundCompany.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['setup_date', 'limit', 'offset']
        entity_fields = [
            "name", "shortname", "short_enname", "province", "city", "address", "phone", "office", "website",
            "chairman", "manager", "reg_capital", "setup_date", "end_date", "employees", "main_business", "org_code",
            "credit_code"
        ]
        TushareDAO.__init__(self, self.engine, session_factory, TushareFundCompany, 'tushare_fund_company',
                            query_fields, entity_fields, config)
        DataProcess.__init__(self, "fund_company", config)
        TuShareBase.__init__(self, "fund_company", config, 1500)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "name",
            "type": "String",
            "comment": "公司名称"
        }, {
            "name": "shortname",
            "type": "String",
            "comment": "简称"
        }, {
            "name": "short_enname",
            "type": "String",
            "comment": "英文缩写"
        }, {
            "name": "province",
            "type": "String",
            "comment": "省份"
        }, {
            "name": "city",
            "type": "String",
            "comment": "城市"
        }, {
            "name": "address",
            "type": "String",
            "comment": "注册地址"
        }, {
            "name": "phone",
            "type": "String",
            "comment": "电话"
        }, {
            "name": "office",
            "type": "String",
            "comment": "办公地址"
        }, {
            "name": "website",
            "type": "String",
            "comment": "公司网址"
        }, {
            "name": "chairman",
            "type": "String",
            "comment": "法人代表"
        }, {
            "name": "manager",
            "type": "String",
            "comment": "总经理"
        }, {
            "name": "reg_capital",
            "type": "Float",
            "comment": "注册资本"
        }, {
            "name": "setup_date",
            "type": "String",
            "comment": "成立日期"
        }, {
            "name": "end_date",
            "type": "String",
            "comment": "公司终止日期"
        }, {
            "name": "employees",
            "type": "Float",
            "comment": "员工总数"
        }, {
            "name": "main_business",
            "type": "String",
            "comment": "主要产品及业务"
        }, {
            "name": "org_code",
            "type": "String",
            "comment": "组织机构代码"
        }, {
            "name": "credit_code",
            "type": "String",
            "comment": "统一社会信用代码"
        }]

    def fund_company(self, fields='', **kwargs):
        """
        获取公募基金管理人列表
        | Arguments:
        | setup_date(str):   成立日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         name(str)  公司名称
         shortname(str)  简称
         short_enname(str)  英文缩写
         province(str)  省份
         city(str)  城市
         address(str)  注册地址
         phone(str)  电话
         office(str)  办公地址
         website(str)  公司网址
         chairman(str)  法人代表
         manager(str)  总经理
         reg_capital(float)  注册资本
         setup_date(str)  成立日期
         end_date(str)  公司终止日期
         employees(float)  员工总数
         main_business(str)  主要产品及业务
         org_code(str)  组织机构代码
         credit_code(str)  统一社会信用代码
        
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
        init_args = {"setup_date": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.fund_company with args: {}".format(kwargs))
                res = self.tushare_query('fund_company', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_fund_company',
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


setattr(FundCompany, 'default_limit', default_limit_ext)
setattr(FundCompany, 'default_cron_express', default_cron_express_ext)
setattr(FundCompany, 'default_order_by', default_order_by_ext)
setattr(FundCompany, 'prepare', prepare_ext)
setattr(FundCompany, 'query_parameters', query_parameters_ext)
setattr(FundCompany, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fund_company())

    api = FundCompany(config)
    api.process()    # 同步增量数据
    print(api.fund_company())    # 数据查询接口
