"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fina_audit接口
获取上市公司定期财务审计意见数据
数据接口-沪深股票-财务数据-财务审计意见  https://tushare.pro/document/2?doc_id=80

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import fina_audit_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareFinaAudit(TutakeTableBase):
    __tablename__ = "tushare_fina_audit"
    ts_code = Column(String, index=True, comment='TS股票代码')
    ann_date = Column(String, index=True, comment='公告日期')
    end_date = Column(String, index=True, comment='报告期')
    audit_result = Column(String, comment='审计结果')
    audit_fees = Column(Float, comment='审计总费用（元）')
    audit_agency = Column(String, comment='会计事务所')
    audit_sign = Column(String, comment='签字会计师')


class FinaAudit(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_fina_audit"
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
        TushareFinaAudit.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareFinaAudit)

        query_fields = ['ts_code', 'ann_date', 'start_date', 'end_date', 'period', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "ann_date", "end_date", "audit_result", "audit_fees", "audit_agency", "audit_sign"
        ]
        entity_fields = ["ts_code", "ann_date", "end_date", "audit_result", "audit_fees", "audit_agency", "audit_sign"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareFinaAudit, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "fina_audit", config)
        TuShareBase.__init__(self, "fina_audit", config, 500)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS股票代码"
        }, {
            "name": "ann_date",
            "type": "String",
            "comment": "公告日期"
        }, {
            "name": "end_date",
            "type": "String",
            "comment": "报告期"
        }, {
            "name": "audit_result",
            "type": "String",
            "comment": "审计结果"
        }, {
            "name": "audit_fees",
            "type": "Float",
            "comment": "审计总费用（元）"
        }, {
            "name": "audit_agency",
            "type": "String",
            "comment": "会计事务所"
        }, {
            "name": "audit_sign",
            "type": "String",
            "comment": "签字会计师"
        }]

    def fina_audit(self, fields='ts_code,ann_date,end_date,audit_result,audit_agency,audit_sign', **kwargs):
        """
        获取上市公司定期财务审计意见数据
        | Arguments:
        | ts_code(str): required  股票代码
        | ann_date(str):   公告日期
        | start_date(str):   公告开始日期
        | end_date(str):   公告结束日期
        | period(str):   报告期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS股票代码 Y
         ann_date(str)  公告日期 Y
         end_date(str)  报告期 Y
         audit_result(str)  审计结果 Y
         audit_fees(float)  审计总费用（元） N
         audit_agency(str)  会计事务所 Y
         audit_sign(str)  签字会计师 Y
        
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
        init_args = {
            "ts_code": "",
            "ann_date": "",
            "start_date": "",
            "end_date": "",
            "period": "",
            "limit": "",
            "offset": ""
        }
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
                self.logger.debug("Invoke pro.fina_audit with args: {}".format(kwargs))
                return self.tushare_query('fina_audit', fields=self.tushare_fields, **kwargs)
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


extends_attr(FinaAudit, fina_audit_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fina_audit())

    api = FinaAudit(config)
    print(api.process())    # 同步增量数据
    print(api.fina_audit())    # 数据查询接口
