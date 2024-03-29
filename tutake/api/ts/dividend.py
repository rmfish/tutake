"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare dividend接口
分红送股数据
数据接口-沪深股票-财务数据-分红送股数据  https://tushare.pro/document/2?doc_id=103

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import dividend_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareDividend(TutakeTableBase):
    __tablename__ = "tushare_dividend"
    ts_code = Column(String, index=True, comment='TS代码')
    end_date = Column(String, index=True, comment='分送年度')
    ann_date = Column(String, index=True, comment='预案公告日（董事会）')
    div_proc = Column(String, comment='实施进度')
    stk_div = Column(Float, comment='每股送转')
    stk_bo_rate = Column(Float, comment='每股送股比例')
    stk_co_rate = Column(Float, comment='每股转增比例')
    cash_div = Column(Float, comment='每股分红（税后）')
    cash_div_tax = Column(Float, comment='每股分红（税前）')
    record_date = Column(String, index=True, comment='股权登记日')
    ex_date = Column(String, index=True, comment='除权除息日')
    pay_date = Column(String, comment='派息日')
    div_listdate = Column(String, comment='红股上市日')
    imp_ann_date = Column(String, index=True, comment='实施公告日')
    base_date = Column(String, comment='基准日')
    base_share = Column(Float, comment='实施基准股本（万）')
    update_flag = Column(String, comment='是否变更过（1表示变更）')


class Dividend(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_dividend"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareDividend.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareDividend),
                                  config.get_tutake_data_dir())

        query_fields = ['ts_code', 'ann_date', 'end_date', 'record_date', 'ex_date', 'imp_ann_date', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "end_date", "ann_date", "div_proc", "stk_div", "stk_bo_rate", "stk_co_rate", "cash_div",
            "cash_div_tax", "record_date", "ex_date", "pay_date", "div_listdate", "imp_ann_date", "base_date",
            "base_share", "update_flag"
        ]
        entity_fields = [
            "ts_code", "end_date", "ann_date", "div_proc", "stk_div", "stk_bo_rate", "stk_co_rate", "cash_div",
            "cash_div_tax", "record_date", "ex_date", "pay_date", "div_listdate", "imp_ann_date", "base_date",
            "base_share", "update_flag"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareDividend, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "dividend", config)
        TuShareBase.__init__(self, "dividend", config, 800)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS代码"
        }, {
            "name": "end_date",
            "type": "String",
            "comment": "分送年度"
        }, {
            "name": "ann_date",
            "type": "String",
            "comment": "预案公告日（董事会）"
        }, {
            "name": "div_proc",
            "type": "String",
            "comment": "实施进度"
        }, {
            "name": "stk_div",
            "type": "Float",
            "comment": "每股送转"
        }, {
            "name": "stk_bo_rate",
            "type": "Float",
            "comment": "每股送股比例"
        }, {
            "name": "stk_co_rate",
            "type": "Float",
            "comment": "每股转增比例"
        }, {
            "name": "cash_div",
            "type": "Float",
            "comment": "每股分红（税后）"
        }, {
            "name": "cash_div_tax",
            "type": "Float",
            "comment": "每股分红（税前）"
        }, {
            "name": "record_date",
            "type": "String",
            "comment": "股权登记日"
        }, {
            "name": "ex_date",
            "type": "String",
            "comment": "除权除息日"
        }, {
            "name": "pay_date",
            "type": "String",
            "comment": "派息日"
        }, {
            "name": "div_listdate",
            "type": "String",
            "comment": "红股上市日"
        }, {
            "name": "imp_ann_date",
            "type": "String",
            "comment": "实施公告日"
        }, {
            "name": "base_date",
            "type": "String",
            "comment": "基准日"
        }, {
            "name": "base_share",
            "type": "Float",
            "comment": "实施基准股本（万）"
        }, {
            "name": "update_flag",
            "type": "String",
            "comment": "是否变更过（1表示变更）"
        }]

    def dividend(
            self,
            fields='ts_code,end_date,ann_date,div_proc,stk_div,stk_bo_rate,stk_co_rate,cash_div,cash_div_tax,record_date,ex_date,pay_date,div_listdate,imp_ann_date',
            **kwargs):
        """
        分红送股数据
        | Arguments:
        | ts_code(str):   TS代码
        | ann_date(str):   公告日
        | end_date(str):   分红年度
        | record_date(str):   股权登记日期
        | ex_date(str):   除权除息日
        | imp_ann_date(str):   除权除息日
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS代码 Y
         end_date(str)  分送年度 Y
         ann_date(str)  预案公告日（董事会） Y
         div_proc(str)  实施进度 Y
         stk_div(float)  每股送转 Y
         stk_bo_rate(float)  每股送股比例 Y
         stk_co_rate(float)  每股转增比例 Y
         cash_div(float)  每股分红（税后） Y
         cash_div_tax(float)  每股分红（税前） Y
         record_date(str)  股权登记日 Y
         ex_date(str)  除权除息日 Y
         pay_date(str)  派息日 Y
         div_listdate(str)  红股上市日 Y
         imp_ann_date(str)  实施公告日 Y
         base_date(str)  基准日 N
         base_share(float)  实施基准股本（万） N
         update_flag(str)  是否变更过（1表示变更） N
        
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
            "ann_date": "",
            "end_date": "",
            "record_date": "",
            "ex_date": "",
            "imp_ann_date": "",
            "limit": "",
            "offset": ""
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
                self.logger.debug("Invoke pro.dividend with args: {}".format(kwargs))
                return self.tushare_query('dividend', fields=self.tushare_fields, **kwargs)
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


extends_attr(Dividend, dividend_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.dividend(ts_code='000002.SZ'))

    api = Dividend(config)
    print(api.process())    # 同步增量数据
    print(api.dividend(ts_code='000002.SZ'))    # 数据查询接口
