"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_company接口
获取公募基金管理人列表
数据接口-公募基金-基金管理人  https://tushare.pro/document/2?doc_id=118

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import fund_company_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareFundCompany(TutakeTableBase):
    __tablename__ = "tushare_fund_company"
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
        self.table_name = "tushare_fund_company"
        self.database = 'tutake.duckdb'
        self.database_dir = config.get_tutake_data_dir()
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareFundCompany.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareFundCompany)

        query_fields = ['setup_date', 'limit', 'offset']
        self.tushare_fields = [
            "name", "shortname", "short_enname", "province", "city", "address", "phone", "office", "website",
            "chairman", "manager", "reg_capital", "setup_date", "end_date", "employees", "main_business", "org_code",
            "credit_code"
        ]
        entity_fields = [
            "name", "shortname", "short_enname", "province", "city", "address", "phone", "office", "website",
            "chairman", "manager", "reg_capital", "setup_date", "end_date", "employees", "main_business", "org_code",
            "credit_code"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareFundCompany, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
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

    def fund_company(
            self,
            fields='name,shortname,province,city,address,phone,office,website,chairman,manager,reg_capital,setup_date,end_date,employees,main_business,org_code,credit_code',
            **kwargs):
        """
        获取公募基金管理人列表
        | Arguments:
        | setup_date(str):   成立日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         name(str)  公司名称 Y
         shortname(str)  简称 Y
         short_enname(str)  英文缩写 N
         province(str)  省份 Y
         city(str)  城市 Y
         address(str)  注册地址 Y
         phone(str)  电话 Y
         office(str)  办公地址 Y
         website(str)  公司网址 Y
         chairman(str)  法人代表 Y
         manager(str)  总经理 Y
         reg_capital(float)  注册资本 Y
         setup_date(str)  成立日期 Y
         end_date(str)  公司终止日期 Y
         employees(float)  员工总数 Y
         main_business(str)  主要产品及业务 Y
         org_code(str)  组织机构代码 Y
         credit_code(str)  统一社会信用代码 Y
        
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append,
                                BatchWriter(self.engine, self.table_name, self.schema, self.database_dir), **kwargs)

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
                return self.tushare_query('fund_company', fields=self.tushare_fields, **kwargs)
            except Exception as err:
                raise ProcessException(kwargs, err)

        res = fetch_save(offset)
        size = res.size()
        offset += size
        while kwargs['limit'] != "" and size == int(kwargs['limit']):
            result = fetch_save(offset)
            size = result.size()
            offset += size
            res.append(result)
        res.fields = self.entity_fields
        return res


extends_attr(FundCompany, fund_company_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fund_company())

    api = FundCompany(config)
    print(api.process())    # 同步增量数据
    print(api.fund_company())    # 数据查询接口
