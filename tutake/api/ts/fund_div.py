"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_div接口
获取公募基金分红数据
数据接口-公募基金-基金分红  https://tushare.pro/document/2?doc_id=120

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.fund_div_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareFundDiv(TutakeTableBase):
    __tablename__ = "tushare_fund_div"
    ts_code = Column(String, index=True, comment='TS代码')
    ann_date = Column(String, index=True, comment='公告日期')
    imp_anndate = Column(String, comment='分红实施公告日')
    base_date = Column(String, comment='分配收益基准日')
    div_proc = Column(String, comment='方案进度')
    record_date = Column(String, comment='权益登记日')
    ex_date = Column(String, index=True, comment='除息日')
    pay_date = Column(String, index=True, comment='派息日')
    earpay_date = Column(String, comment='收益支付日')
    net_ex_date = Column(String, comment='净值除权日')
    div_cash = Column(Float, comment='每股派息(元)')
    base_unit = Column(Float, comment='基准基金份额(万份)')
    ear_distr = Column(Float, comment='可分配收益(元)')
    ear_amount = Column(Float, comment='收益分配金额(元)')
    account_date = Column(String, comment='红利再投资到账日')
    base_year = Column(String, comment='份额基准年度')
    update_flag = Column(String, comment='更新标识')


class FundDiv(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_fund_div"
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
        TushareFundDiv.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareFundDiv)

        query_fields = ['ann_date', 'ex_date', 'pay_date', 'ts_code', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "ann_date", "imp_anndate", "base_date", "div_proc", "record_date", "ex_date", "pay_date",
            "earpay_date", "net_ex_date", "div_cash", "base_unit", "ear_distr", "ear_amount", "account_date",
            "base_year", "update_flag"
        ]
        entity_fields = [
            "ts_code", "ann_date", "imp_anndate", "base_date", "div_proc", "record_date", "ex_date", "pay_date",
            "earpay_date", "net_ex_date", "div_cash", "base_unit", "ear_distr", "ear_amount", "account_date",
            "base_year", "update_flag"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareFundDiv, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "fund_div", config)
        TuShareBase.__init__(self, "fund_div", config, 800)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS代码"
        }, {
            "name": "ann_date",
            "type": "String",
            "comment": "公告日期"
        }, {
            "name": "imp_anndate",
            "type": "String",
            "comment": "分红实施公告日"
        }, {
            "name": "base_date",
            "type": "String",
            "comment": "分配收益基准日"
        }, {
            "name": "div_proc",
            "type": "String",
            "comment": "方案进度"
        }, {
            "name": "record_date",
            "type": "String",
            "comment": "权益登记日"
        }, {
            "name": "ex_date",
            "type": "String",
            "comment": "除息日"
        }, {
            "name": "pay_date",
            "type": "String",
            "comment": "派息日"
        }, {
            "name": "earpay_date",
            "type": "String",
            "comment": "收益支付日"
        }, {
            "name": "net_ex_date",
            "type": "String",
            "comment": "净值除权日"
        }, {
            "name": "div_cash",
            "type": "Float",
            "comment": "每股派息(元)"
        }, {
            "name": "base_unit",
            "type": "Float",
            "comment": "基准基金份额(万份)"
        }, {
            "name": "ear_distr",
            "type": "Float",
            "comment": "可分配收益(元)"
        }, {
            "name": "ear_amount",
            "type": "Float",
            "comment": "收益分配金额(元)"
        }, {
            "name": "account_date",
            "type": "String",
            "comment": "红利再投资到账日"
        }, {
            "name": "base_year",
            "type": "String",
            "comment": "份额基准年度"
        }, {
            "name": "update_flag",
            "type": "String",
            "comment": "更新标识"
        }]

    def fund_div(
            self,
            fields='ts_code,ann_date,imp_anndate,base_date,div_proc,record_date,ex_date,pay_date,earpay_date,net_ex_date,div_cash,base_unit,ear_distr,ear_amount,account_date,base_year',
            **kwargs):
        """
        获取公募基金分红数据
        | Arguments:
        | ann_date(str):   公告日
        | ex_date(str):   公告日
        | pay_date(str):   公告日
        | ts_code(str):   公告日
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS代码 Y
         ann_date(str)  公告日期 Y
         imp_anndate(str)  分红实施公告日 Y
         base_date(str)  分配收益基准日 Y
         div_proc(str)  方案进度 Y
         record_date(str)  权益登记日 Y
         ex_date(str)  除息日 Y
         pay_date(str)  派息日 Y
         earpay_date(str)  收益支付日 Y
         net_ex_date(str)  净值除权日 Y
         div_cash(float)  每股派息(元) Y
         base_unit(float)  基准基金份额(万份) Y
         ear_distr(float)  可分配收益(元) Y
         ear_amount(float)  收益分配金额(元) Y
         account_date(str)  红利再投资到账日 Y
         base_year(str)  份额基准年度 Y
         update_flag(str)  更新标识 N
        
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
        init_args = {"ann_date": "", "ex_date": "", "pay_date": "", "ts_code": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.fund_div with args: {}".format(kwargs))
                return self.tushare_query('fund_div', fields=self.tushare_fields, **kwargs)
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


setattr(FundDiv, 'default_limit', default_limit_ext)
setattr(FundDiv, 'default_cron_express', default_cron_express_ext)
setattr(FundDiv, 'default_order_by', default_order_by_ext)
setattr(FundDiv, 'prepare', prepare_ext)
setattr(FundDiv, 'query_parameters', query_parameters_ext)
setattr(FundDiv, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fund_div(ts_code='500001.SH'))

    api = FundDiv(config)
    print(api.process())    # 同步增量数据
    print(api.fund_div(ts_code='500001.SH'))    # 数据查询接口
