"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare namechange接口
历史名称变更记录
数据接口-沪深股票-基础数据-股票曾用名  https://tushare.pro/document/2?doc_id=100

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import namechange_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareNamechange(TutakeTableBase):
    __tablename__ = "tushare_namechange"
    ts_code = Column(String, index=True, comment='TS代码')
    name = Column(String, comment='证券名称')
    start_date = Column(String, index=True, comment='开始日期')
    end_date = Column(String, index=True, comment='结束日期')
    ann_date = Column(String, comment='公告日期')
    change_reason = Column(String, comment='变更原因')


class Namechange(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_namechange"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareNamechange.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareNamechange),
                                  config.get_tutake_data_dir())

        query_fields = ['ts_code', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = ["ts_code", "name", "start_date", "end_date", "ann_date", "change_reason"]
        entity_fields = ["ts_code", "name", "start_date", "end_date", "ann_date", "change_reason"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareNamechange, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "namechange", config)
        TuShareBase.__init__(self, "namechange", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS代码"
        }, {
            "name": "name",
            "type": "String",
            "comment": "证券名称"
        }, {
            "name": "start_date",
            "type": "String",
            "comment": "开始日期"
        }, {
            "name": "end_date",
            "type": "String",
            "comment": "结束日期"
        }, {
            "name": "ann_date",
            "type": "String",
            "comment": "公告日期"
        }, {
            "name": "change_reason",
            "type": "String",
            "comment": "变更原因"
        }]

    def namechange(self, fields='', **kwargs):
        """
        历史名称变更记录
        | Arguments:
        | ts_code(str):   TS代码
        | start_date(str):   公告开始日期
        | end_date(str):   公告结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS代码 Y
         name(str)  证券名称 Y
         start_date(str)  开始日期 Y
         end_date(str)  结束日期 Y
         ann_date(str)  公告日期 Y
         change_reason(str)  变更原因 Y
        
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
        init_args = {"ts_code": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.namechange with args: {}".format(kwargs))
                return self.tushare_query('namechange', fields=self.tushare_fields, **kwargs)
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


extends_attr(Namechange, namechange_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.namechange())

    api = Namechange(config)
    print(api.process())    # 同步增量数据
    print(api.namechange())    # 数据查询接口
