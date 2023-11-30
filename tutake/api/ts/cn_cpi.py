"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare cn_cpi接口
获取CPI居民消费价格数据，包括全国、城市和农村的数据
数据接口-宏观经济-国内宏观-价格指数-居民消费价格指数（CPI）  https://tushare.pro/document/2?doc_id=228

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.cn_cpi_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareCnCpi(TutakeTableBase):
    __tablename__ = "tushare_cn_cpi"
    month = Column(String, comment='月份YYYYMM')
    nt_val = Column(Float, comment='全国当月至')
    nt_yoy = Column(Float, comment='全国同比（%）')
    nt_mom = Column(Float, comment='全国环比（%）')
    nt_accu = Column(Float, comment='全国累计值')
    town_val = Column(Float, comment='城市当值月')
    town_yoy = Column(Float, comment='城市同比（%）')
    town_mom = Column(Float, comment='城市环比（%）')
    town_accu = Column(Float, comment='城市累计值')
    cnt_val = Column(Float, comment='农村当月值')
    cnt_yoy = Column(Float, comment='农村同比（%）')
    cnt_mom = Column(Float, comment='农村环比（%）')
    cnt_accu = Column(Float, comment='农村累计值')


class CnCpi(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_cn_cpi"
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
        TushareCnCpi.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareCnCpi)

        query_fields = ['m', 'start_m', 'end_m', 'limit', 'offset']
        self.tushare_fields = [
            "month", "nt_val", "nt_yoy", "nt_mom", "nt_accu", "town_val", "town_yoy", "town_mom", "town_accu",
            "cnt_val", "cnt_yoy", "cnt_mom", "cnt_accu"
        ]
        entity_fields = [
            "month", "nt_val", "nt_yoy", "nt_mom", "nt_accu", "town_val", "town_yoy", "town_mom", "town_accu",
            "cnt_val", "cnt_yoy", "cnt_mom", "cnt_accu"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareCnCpi, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "cn_cpi", config)
        TuShareBase.__init__(self, "cn_cpi", config, 600)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "month",
            "type": "String",
            "comment": "月份YYYYMM"
        }, {
            "name": "nt_val",
            "type": "Float",
            "comment": "全国当月至"
        }, {
            "name": "nt_yoy",
            "type": "Float",
            "comment": "全国同比（%）"
        }, {
            "name": "nt_mom",
            "type": "Float",
            "comment": "全国环比（%）"
        }, {
            "name": "nt_accu",
            "type": "Float",
            "comment": "全国累计值"
        }, {
            "name": "town_val",
            "type": "Float",
            "comment": "城市当值月"
        }, {
            "name": "town_yoy",
            "type": "Float",
            "comment": "城市同比（%）"
        }, {
            "name": "town_mom",
            "type": "Float",
            "comment": "城市环比（%）"
        }, {
            "name": "town_accu",
            "type": "Float",
            "comment": "城市累计值"
        }, {
            "name": "cnt_val",
            "type": "Float",
            "comment": "农村当月值"
        }, {
            "name": "cnt_yoy",
            "type": "Float",
            "comment": "农村同比（%）"
        }, {
            "name": "cnt_mom",
            "type": "Float",
            "comment": "农村环比（%）"
        }, {
            "name": "cnt_accu",
            "type": "Float",
            "comment": "农村累计值"
        }]

    def cn_cpi(self, fields='', **kwargs):
        """
        获取CPI居民消费价格数据，包括全国、城市和农村的数据
        | Arguments:
        | m(str):   月份（YYYYMM，下同），支持多个月份同时输入，逗号分隔
        | start_m(str):   开始月份
        | end_m(str):   结束月份
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         month(str)  月份YYYYMM Y
         nt_val(float)  全国当月至 Y
         nt_yoy(float)  全国同比（%） Y
         nt_mom(float)  全国环比（%） Y
         nt_accu(float)  全国累计值 Y
         town_val(float)  城市当值月 Y
         town_yoy(float)  城市同比（%） Y
         town_mom(float)  城市环比（%） Y
         town_accu(float)  城市累计值 Y
         cnt_val(float)  农村当月值 Y
         cnt_yoy(float)  农村同比（%） Y
         cnt_mom(float)  农村环比（%） Y
         cnt_accu(float)  农村累计值 Y
        
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
        init_args = {"m": "", "start_m": "", "end_m": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.cn_cpi with args: {}".format(kwargs))
                return self.tushare_query('cn_cpi', fields=self.tushare_fields, **kwargs)
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


setattr(CnCpi, 'default_limit', default_limit_ext)
setattr(CnCpi, 'default_cron_express', default_cron_express_ext)
setattr(CnCpi, 'default_order_by', default_order_by_ext)
setattr(CnCpi, 'prepare', prepare_ext)
setattr(CnCpi, 'query_parameters', query_parameters_ext)
setattr(CnCpi, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.cn_cpi())

    api = CnCpi(config)
    print(api.process())    # 同步增量数据
    print(api.cn_cpi())    # 数据查询接口
