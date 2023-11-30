"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare gz_index接口
广州民间借贷利率,广州民间金融街
数据接口-宏观经济-国内宏观-利率数据-广州民间借贷利率  https://tushare.pro/document/2?doc_id=174

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import gz_index_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareGzIndex(TutakeTableBase):
    __tablename__ = "tushare_gz_index"
    date = Column(String, index=True, comment='日期')
    d10_rate = Column(Float, comment='小额贷市场平均利率（十天）')
    m1_rate = Column(Float, comment='小额贷市场平均利率（一月期）')
    m3_rate = Column(Float, comment='小额贷市场平均利率（三月期）')
    m6_rate = Column(Float, comment='小额贷市场平均利率（六月期）')
    m12_rate = Column(Float, comment='小额贷市场平均利率（一年期）')
    long_rate = Column(Float, comment='小额贷市场平均利率（长期）')


class GzIndex(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_gz_index"
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
        TushareGzIndex.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareGzIndex)

        query_fields = ['date', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = ["date", "d10_rate", "m1_rate", "m3_rate", "m6_rate", "m12_rate", "long_rate"]
        entity_fields = ["date", "d10_rate", "m1_rate", "m3_rate", "m6_rate", "m12_rate", "long_rate"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareGzIndex, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "gz_index", config)
        TuShareBase.__init__(self, "gz_index", config, 2000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "date",
            "type": "String",
            "comment": "日期"
        }, {
            "name": "d10_rate",
            "type": "Float",
            "comment": "小额贷市场平均利率（十天）"
        }, {
            "name": "m1_rate",
            "type": "Float",
            "comment": "小额贷市场平均利率（一月期）"
        }, {
            "name": "m3_rate",
            "type": "Float",
            "comment": "小额贷市场平均利率（三月期）"
        }, {
            "name": "m6_rate",
            "type": "Float",
            "comment": "小额贷市场平均利率（六月期）"
        }, {
            "name": "m12_rate",
            "type": "Float",
            "comment": "小额贷市场平均利率（一年期）"
        }, {
            "name": "long_rate",
            "type": "Float",
            "comment": "小额贷市场平均利率（长期）"
        }]

    def gz_index(self, fields='', **kwargs):
        """
        广州民间借贷利率,广州民间金融街
        | Arguments:
        | date(str):   日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         date(str)  日期 Y
         d10_rate(float)  小额贷市场平均利率（十天） Y
         m1_rate(float)  小额贷市场平均利率（一月期） Y
         m3_rate(float)  小额贷市场平均利率（三月期） Y
         m6_rate(float)  小额贷市场平均利率（六月期） Y
         m12_rate(float)  小额贷市场平均利率（一年期） Y
         long_rate(float)  小额贷市场平均利率（长期） Y
        
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
        init_args = {"date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.gz_index with args: {}".format(kwargs))
                return self.tushare_query('gz_index', fields=self.tushare_fields, **kwargs)
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


extends_attr(GzIndex, gz_index_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.gz_index())

    api = GzIndex(config)
    print(api.process())    # 同步增量数据
    print(api.gz_index())    # 数据查询接口
