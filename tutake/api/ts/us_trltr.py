"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare us_trltr接口
获取美国国债长期利率平均值数据
数据接口-宏观经济-国际宏观-美国利率-国债长期利率平均值  https://tushare.pro/document/2?doc_id=223

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.us_trltr_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareUsTrltr(TutakeTableBase):
    __tablename__ = "tushare_us_trltr"
    date = Column(String, index=True, comment='日期')
    ltr_avg = Column(Float, comment='实际平均利率LT Real Average (10> Yrs)')


class UsTrltr(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_us_trltr"
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
        TushareUsTrltr.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareUsTrltr)

        query_fields = ['date', 'start_date', 'end_date', 'fields', 'limit', 'offset']
        self.tushare_fields = ["date", "ltr_avg"]
        entity_fields = ["date", "ltr_avg"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareUsTrltr, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "us_trltr", config)
        TuShareBase.__init__(self, "us_trltr", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "date",
            "type": "String",
            "comment": "日期"
        }, {
            "name": "ltr_avg",
            "type": "Float",
            "comment": "实际平均利率LT Real Average (10> Yrs)"
        }]

    def us_trltr(self, fields='', **kwargs):
        """
        获取美国国债长期利率平均值数据
        | Arguments:
        | date(str):   日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | fields(str):   指定字段
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         date(str)  日期 Y
         ltr_avg(float)  实际平均利率LT Real Average (10> Yrs) Y
        
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
        init_args = {"date": "", "start_date": "", "end_date": "", "fields": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.us_trltr with args: {}".format(kwargs))
                return self.tushare_query('us_trltr', fields=self.tushare_fields, **kwargs)
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


setattr(UsTrltr, 'default_limit', default_limit_ext)
setattr(UsTrltr, 'default_cron_express', default_cron_express_ext)
setattr(UsTrltr, 'default_order_by', default_order_by_ext)
setattr(UsTrltr, 'prepare', prepare_ext)
setattr(UsTrltr, 'query_parameters', query_parameters_ext)
setattr(UsTrltr, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.us_trltr())

    api = UsTrltr(config)
    print(api.process())    # 同步增量数据
    print(api.us_trltr())    # 数据查询接口
