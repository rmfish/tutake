"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_basic接口
获取公募基金数据列表，包括场内和场外基金
数据接口-公募基金-基金列表  https://tushare.pro/document/2?doc_id=19

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import fund_basic_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareFundBasic(TutakeTableBase):
    __tablename__ = "tushare_fund_basic"
    ts_code = Column(String, primary_key=True, comment='基金代码')
    name = Column(String, index=True, comment='简称')
    management = Column(String, comment='管理人')
    custodian = Column(String, comment='托管人')
    fund_type = Column(String, comment='投资类型')
    found_date = Column(String, comment='成立日期')
    due_date = Column(String, comment='到期日期')
    list_date = Column(String, comment='上市时间')
    issue_date = Column(String, comment='发行日期')
    delist_date = Column(String, comment='退市日期')
    issue_amount = Column(Float, comment='发行份额(亿份)')
    m_fee = Column(Float, comment='管理费')
    c_fee = Column(Float, comment='托管费')
    duration_year = Column(Float, comment='存续期')
    p_value = Column(Float, comment='面值')
    min_amount = Column(Float, comment='起点金额(万元)')
    exp_return = Column(Float, comment='预期收益率')
    benchmark = Column(String, comment='业绩比较基准')
    status = Column(String, index=True, comment='存续状态D摘牌 I发行 L已上市')
    invest_type = Column(String, comment='投资风格')
    type = Column(String, comment='基金类型')
    trustee = Column(String, comment='受托人')
    purc_startdate = Column(String, comment='日常申购起始日')
    redm_startdate = Column(String, comment='日常赎回起始日')
    market = Column(String, index=True, comment='E场内O场外')


class FundBasic(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_fund_basic"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareFundBasic.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareFundBasic),
                                  config.get_tutake_data_dir())

        query_fields = ['ts_code', 'market', 'update_flag', 'offset', 'limit', 'status', 'name']
        self.tushare_fields = [
            "ts_code", "name", "management", "custodian", "fund_type", "found_date", "due_date", "list_date",
            "issue_date", "delist_date", "issue_amount", "m_fee", "c_fee", "duration_year", "p_value", "min_amount",
            "exp_return", "benchmark", "status", "invest_type", "type", "trustee", "purc_startdate", "redm_startdate",
            "market"
        ]
        entity_fields = [
            "ts_code", "name", "management", "custodian", "fund_type", "found_date", "due_date", "list_date",
            "issue_date", "delist_date", "issue_amount", "m_fee", "c_fee", "duration_year", "p_value", "min_amount",
            "exp_return", "benchmark", "status", "invest_type", "type", "trustee", "purc_startdate", "redm_startdate",
            "market"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareFundBasic, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "fund_basic", config)
        TuShareBase.__init__(self, "fund_basic", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "基金代码"
        }, {
            "name": "name",
            "type": "String",
            "comment": "简称"
        }, {
            "name": "management",
            "type": "String",
            "comment": "管理人"
        }, {
            "name": "custodian",
            "type": "String",
            "comment": "托管人"
        }, {
            "name": "fund_type",
            "type": "String",
            "comment": "投资类型"
        }, {
            "name": "found_date",
            "type": "String",
            "comment": "成立日期"
        }, {
            "name": "due_date",
            "type": "String",
            "comment": "到期日期"
        }, {
            "name": "list_date",
            "type": "String",
            "comment": "上市时间"
        }, {
            "name": "issue_date",
            "type": "String",
            "comment": "发行日期"
        }, {
            "name": "delist_date",
            "type": "String",
            "comment": "退市日期"
        }, {
            "name": "issue_amount",
            "type": "Float",
            "comment": "发行份额(亿份)"
        }, {
            "name": "m_fee",
            "type": "Float",
            "comment": "管理费"
        }, {
            "name": "c_fee",
            "type": "Float",
            "comment": "托管费"
        }, {
            "name": "duration_year",
            "type": "Float",
            "comment": "存续期"
        }, {
            "name": "p_value",
            "type": "Float",
            "comment": "面值"
        }, {
            "name": "min_amount",
            "type": "Float",
            "comment": "起点金额(万元)"
        }, {
            "name": "exp_return",
            "type": "Float",
            "comment": "预期收益率"
        }, {
            "name": "benchmark",
            "type": "String",
            "comment": "业绩比较基准"
        }, {
            "name": "status",
            "type": "String",
            "comment": "存续状态D摘牌 I发行 L已上市"
        }, {
            "name": "invest_type",
            "type": "String",
            "comment": "投资风格"
        }, {
            "name": "type",
            "type": "String",
            "comment": "基金类型"
        }, {
            "name": "trustee",
            "type": "String",
            "comment": "受托人"
        }, {
            "name": "purc_startdate",
            "type": "String",
            "comment": "日常申购起始日"
        }, {
            "name": "redm_startdate",
            "type": "String",
            "comment": "日常赎回起始日"
        }, {
            "name": "market",
            "type": "String",
            "comment": "E场内O场外"
        }]

    def fund_basic(self, fields='', **kwargs):
        """
        获取公募基金数据列表，包括场内和场外基金
        | Arguments:
        | ts_code(str):   TS基金代码
        | market(str):   交易市场
        | update_flag(str):   更新标志
        | offset(int):   
        | limit(int):   
        | status(str):   存续状态
        | name(str):   
        
        :return: DataFrame
         ts_code(str)  基金代码 Y
         name(str)  简称 Y
         management(str)  管理人 Y
         custodian(str)  托管人 Y
         fund_type(str)  投资类型 Y
         found_date(str)  成立日期 Y
         due_date(str)  到期日期 Y
         list_date(str)  上市时间 Y
         issue_date(str)  发行日期 Y
         delist_date(str)  退市日期 Y
         issue_amount(float)  发行份额(亿份) Y
         m_fee(float)  管理费 Y
         c_fee(float)  托管费 Y
         duration_year(float)  存续期 Y
         p_value(float)  面值 Y
         min_amount(float)  起点金额(万元) Y
         exp_return(float)  预期收益率 Y
         benchmark(str)  业绩比较基准 Y
         status(str)  存续状态D摘牌 I发行 L已上市 Y
         invest_type(str)  投资风格 Y
         type(str)  基金类型 Y
         trustee(str)  受托人 Y
         purc_startdate(str)  日常申购起始日 Y
         redm_startdate(str)  日常赎回起始日 Y
         market(str)  E场内O场外 Y
        
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append, self.writer, **kwargs)

    def fetch_and_append(self, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        init_args = {
            "ts_code": "",
            "market": "",
            "update_flag": "",
            "offset": "",
            "limit": "",
            "status": "",
            "name": ""
        }
        is_test = kwargs.get('test') or False
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
                self.logger.debug("Invoke pro.fund_basic with args: {}".format(kwargs))
                return self.tushare_query('fund_basic', fields=self.tushare_fields, **kwargs)
            except Exception as err:
                raise ProcessException(kwargs, err)

        res = fetch_save(offset)
        size = res.size()
        offset += size
        res.fields = self.entity_fields
        if is_test:
            return res
        while kwargs['limit'] != "" and size == int(kwargs['limit']):
            result = fetch_save(offset)
            size = result.size()
            offset += size
            res.append(result)
        return res


extends_attr(FundBasic, fund_basic_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fund_basic())

    api = FundBasic(config)
    print(api.process())    # 同步增量数据
    print(api.fund_basic())    # 数据查询接口
