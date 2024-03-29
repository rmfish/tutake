"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare hs_const接口
获取沪股通、深股通成分数据
数据接口-沪深股票-基础数据-沪深股通成分股  https://tushare.pro/document/2?doc_id=104

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import hs_const_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareHsConst(TutakeTableBase):
    __tablename__ = "tushare_hs_const"
    ts_code = Column(String, comment='TS代码')
    hs_type = Column(String, index=True, comment='沪深港通类型SH沪SZ深')
    in_date = Column(String, comment='纳入日期')
    out_date = Column(String, comment='剔除日期')
    is_new = Column(String, index=True, comment='是否最新')


class HsConst(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_hs_const"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareHsConst.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareHsConst),
                                  config.get_tutake_data_dir())

        query_fields = ['hs_type', 'is_new', 'limit', 'offset']
        self.tushare_fields = ["ts_code", "hs_type", "in_date", "out_date", "is_new"]
        entity_fields = ["ts_code", "hs_type", "in_date", "out_date", "is_new"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareHsConst, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "hs_const", config)
        TuShareBase.__init__(self, "hs_const", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS代码"
        }, {
            "name": "hs_type",
            "type": "String",
            "comment": "沪深港通类型SH沪SZ深"
        }, {
            "name": "in_date",
            "type": "String",
            "comment": "纳入日期"
        }, {
            "name": "out_date",
            "type": "String",
            "comment": "剔除日期"
        }, {
            "name": "is_new",
            "type": "String",
            "comment": "是否最新"
        }]

    def hs_const(self, fields='', **kwargs):
        """
        获取沪股通、深股通成分数据
        | Arguments:
        | hs_type(str): required  类型SH沪股通SZ深股通
        | is_new(str):   是否最新1最新0不是
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS代码 Y
         hs_type(str)  沪深港通类型SH沪SZ深 Y
         in_date(str)  纳入日期 Y
         out_date(str)  剔除日期 Y
         is_new(str)  是否最新 Y
        
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
        init_args = {"hs_type": "", "is_new": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.hs_const with args: {}".format(kwargs))
                return self.tushare_query('hs_const', fields=self.tushare_fields, **kwargs)
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


extends_attr(HsConst, hs_const_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.hs_const(hs_type='SH'))

    api = HsConst(config)
    print(api.process())    # 同步增量数据
    print(api.hs_const(hs_type='SH'))    # 数据查询接口
