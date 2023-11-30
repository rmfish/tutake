"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_manager接口
获取公募基金经理数据，包括基金经理简历等数据
数据接口-公募基金-基金经理  https://tushare.pro/document/2?doc_id=208

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.fund_manager_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareFundManager(TutakeTableBase):
    __tablename__ = "tushare_fund_manager"
    ts_code = Column(String, index=True, comment='基金代码')
    ann_date = Column(String, index=True, comment='公告日期')
    name = Column(String, index=True, comment='基金经理姓名')
    gender = Column(String, comment='性别')
    birth_year = Column(String, comment='出生年份')
    edu = Column(String, comment='学历')
    nationality = Column(String, comment='国籍')
    begin_date = Column(String, comment='任职日期')
    end_date = Column(String, comment='历任日期')
    resume = Column(String, comment='简历')


class FundManager(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_fund_manager"
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
        TushareFundManager.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareFundManager)

        query_fields = ['ts_code', 'ann_date', 'name', 'offset', 'limit']
        self.tushare_fields = [
            "ts_code", "ann_date", "name", "gender", "birth_year", "edu", "nationality", "begin_date", "end_date",
            "resume"
        ]
        entity_fields = [
            "ts_code", "ann_date", "name", "gender", "birth_year", "edu", "nationality", "begin_date", "end_date",
            "resume"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareFundManager, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "fund_manager", config)
        TuShareBase.__init__(self, "fund_manager", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "基金代码"
        }, {
            "name": "ann_date",
            "type": "String",
            "comment": "公告日期"
        }, {
            "name": "name",
            "type": "String",
            "comment": "基金经理姓名"
        }, {
            "name": "gender",
            "type": "String",
            "comment": "性别"
        }, {
            "name": "birth_year",
            "type": "String",
            "comment": "出生年份"
        }, {
            "name": "edu",
            "type": "String",
            "comment": "学历"
        }, {
            "name": "nationality",
            "type": "String",
            "comment": "国籍"
        }, {
            "name": "begin_date",
            "type": "String",
            "comment": "任职日期"
        }, {
            "name": "end_date",
            "type": "String",
            "comment": "历任日期"
        }, {
            "name": "resume",
            "type": "String",
            "comment": "简历"
        }]

    def fund_manager(self, fields='', **kwargs):
        """
        获取公募基金经理数据，包括基金经理简历等数据
        | Arguments:
        | ts_code(str):   基金代码
        | ann_date(str):   公告日期
        | name(str):   基金经理姓名
        | offset(int):   开始行数
        | limit(int):   每页行数
        
        :return: DataFrame
         ts_code(str)  基金代码 Y
         ann_date(str)  公告日期 Y
         name(str)  基金经理姓名 Y
         gender(str)  性别 Y
         birth_year(str)  出生年份 Y
         edu(str)  学历 Y
         nationality(str)  国籍 Y
         begin_date(str)  任职日期 Y
         end_date(str)  历任日期 Y
         resume(str)  简历 Y
        
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
        init_args = {"ts_code": "", "ann_date": "", "name": "", "offset": "", "limit": ""}
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
                self.logger.debug("Invoke pro.fund_manager with args: {}".format(kwargs))
                return self.tushare_query('fund_manager', fields=self.tushare_fields, **kwargs)
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


setattr(FundManager, 'default_limit', default_limit_ext)
setattr(FundManager, 'default_cron_express', default_cron_express_ext)
setattr(FundManager, 'default_order_by', default_order_by_ext)
setattr(FundManager, 'prepare', prepare_ext)
setattr(FundManager, 'query_parameters', query_parameters_ext)
setattr(FundManager, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fund_manager())

    api = FundManager(config)
    print(api.process())    # 同步增量数据
    print(api.fund_manager())    # 数据查询接口
