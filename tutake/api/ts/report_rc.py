"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare report_rc接口
获取券商（卖方）每天研报的盈利预测数据，数据从2010年开始，每晚19~22点更新当日数据
数据接口-沪深股票-特色数据-券商盈利预测数据  https://tushare.pro/document/2?doc_id=292

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.report_rc_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareReportRc(TutakeTableBase):
    __tablename__ = "tushare_report_rc"
    ts_code = Column(String, index=True, comment='股票代码')
    name = Column(String, comment='股票名称')
    report_date = Column(String, index=True, comment='研报日期')
    report_title = Column(String, comment='报告标题')
    report_type = Column(String, comment='报告类型')
    classify = Column(String, comment='报告分类')
    org_name = Column(String, comment='机构名称')
    author_name = Column(String, comment='作者')
    quarter = Column(String, comment='预测报告期')
    op_rt = Column(Float, comment='预测营业收入（万元）')
    op_pr = Column(Float, comment='预测营业利润（万元）')
    tp = Column(Float, comment='预测利润总额（万元）')
    np = Column(Float, comment='预测净利润（万元）')
    eps = Column(Float, comment='预测每股收益（元）')
    pe = Column(Float, comment='预测市盈率（元）')
    rd = Column(Float, comment='预测股息率（元）')
    roe = Column(Float, comment='预测净资产收益率（元）')
    ev_ebitda = Column(Float, comment='预测EV/EBITDA')
    rating = Column(String, comment='卖方评级')
    max_price = Column(Float, comment='预测最高目标价')
    min_price = Column(Float, comment='预测最低目标价')
    imp_dg = Column(String, comment='机构关注度')
    create_time = Column(String, comment='TS数据更新时间')


class ReportRc(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_report_rc"
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
        TushareReportRc.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareReportRc)

        query_fields = ['ts_code', 'report_date', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "name", "report_date", "report_title", "report_type", "classify", "org_name", "author_name",
            "quarter", "op_rt", "op_pr", "tp", "np", "eps", "pe", "rd", "roe", "ev_ebitda", "rating", "max_price",
            "min_price", "imp_dg", "create_time"
        ]
        entity_fields = [
            "ts_code", "name", "report_date", "report_title", "report_type", "classify", "org_name", "author_name",
            "quarter", "op_rt", "op_pr", "tp", "np", "eps", "pe", "rd", "roe", "ev_ebitda", "rating", "max_price",
            "min_price", "imp_dg", "create_time"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareReportRc, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "report_rc", config)
        TuShareBase.__init__(self, "report_rc", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "股票代码"
        }, {
            "name": "name",
            "type": "String",
            "comment": "股票名称"
        }, {
            "name": "report_date",
            "type": "String",
            "comment": "研报日期"
        }, {
            "name": "report_title",
            "type": "String",
            "comment": "报告标题"
        }, {
            "name": "report_type",
            "type": "String",
            "comment": "报告类型"
        }, {
            "name": "classify",
            "type": "String",
            "comment": "报告分类"
        }, {
            "name": "org_name",
            "type": "String",
            "comment": "机构名称"
        }, {
            "name": "author_name",
            "type": "String",
            "comment": "作者"
        }, {
            "name": "quarter",
            "type": "String",
            "comment": "预测报告期"
        }, {
            "name": "op_rt",
            "type": "Float",
            "comment": "预测营业收入（万元）"
        }, {
            "name": "op_pr",
            "type": "Float",
            "comment": "预测营业利润（万元）"
        }, {
            "name": "tp",
            "type": "Float",
            "comment": "预测利润总额（万元）"
        }, {
            "name": "np",
            "type": "Float",
            "comment": "预测净利润（万元）"
        }, {
            "name": "eps",
            "type": "Float",
            "comment": "预测每股收益（元）"
        }, {
            "name": "pe",
            "type": "Float",
            "comment": "预测市盈率（元）"
        }, {
            "name": "rd",
            "type": "Float",
            "comment": "预测股息率（元）"
        }, {
            "name": "roe",
            "type": "Float",
            "comment": "预测净资产收益率（元）"
        }, {
            "name": "ev_ebitda",
            "type": "Float",
            "comment": "预测EV/EBITDA"
        }, {
            "name": "rating",
            "type": "String",
            "comment": "卖方评级"
        }, {
            "name": "max_price",
            "type": "Float",
            "comment": "预测最高目标价"
        }, {
            "name": "min_price",
            "type": "Float",
            "comment": "预测最低目标价"
        }, {
            "name": "imp_dg",
            "type": "String",
            "comment": "机构关注度"
        }, {
            "name": "create_time",
            "type": "String",
            "comment": "TS数据更新时间"
        }]

    def report_rc(
            self,
            fields='ts_code,name,report_date,report_title,report_type,classify,org_name,author_name,quarter,op_rt,op_pr,tp,np,eps,pe,rd,roe,ev_ebitda,rating,max_price,min_price',
            **kwargs):
        """
        获取券商（卖方）每天研报的盈利预测数据，数据从2010年开始，每晚19~22点更新当日数据
        | Arguments:
        | ts_code(str):   股票代码
        | report_date(str):   报告日期
        | start_date(str):   报告开始日期
        | end_date(str):   报告结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  股票代码 Y
         name(str)  股票名称 Y
         report_date(str)  研报日期 Y
         report_title(str)  报告标题 Y
         report_type(str)  报告类型 Y
         classify(str)  报告分类 Y
         org_name(str)  机构名称 Y
         author_name(str)  作者 Y
         quarter(str)  预测报告期 Y
         op_rt(float)  预测营业收入（万元） Y
         op_pr(float)  预测营业利润（万元） Y
         tp(float)  预测利润总额（万元） Y
         np(float)  预测净利润（万元） Y
         eps(float)  预测每股收益（元） Y
         pe(float)  预测市盈率（元） Y
         rd(float)  预测股息率（元） Y
         roe(float)  预测净资产收益率（元） Y
         ev_ebitda(float)  预测EV/EBITDA Y
         rating(str)  卖方评级 Y
         max_price(float)  预测最高目标价 Y
         min_price(float)  预测最低目标价 Y
         imp_dg(str)  机构关注度 N
         create_time(datetime)  TS数据更新时间 N
        
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
        init_args = {"ts_code": "", "report_date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.report_rc with args: {}".format(kwargs))
                return self.tushare_query('report_rc', fields=self.tushare_fields, **kwargs)
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


setattr(ReportRc, 'default_limit', default_limit_ext)
setattr(ReportRc, 'default_cron_express', default_cron_express_ext)
setattr(ReportRc, 'default_order_by', default_order_by_ext)
setattr(ReportRc, 'prepare', prepare_ext)
setattr(ReportRc, 'query_parameters', query_parameters_ext)
setattr(ReportRc, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.report_rc())

    api = ReportRc(config)
    print(api.process())    # 同步增量数据
    print(api.report_rc())    # 数据查询接口
