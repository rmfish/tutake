"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare cn_m接口
获取货币供应量月度数据
数据接口-宏观经济-国内宏观-金融-货币供应量-货币供应量（月）  https://tushare.pro/document/2?doc_id=242

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.cn_m_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareCnM(Base):
    __tablename__ = "tushare_cn_m"
    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(String, comment='月份YYYYMM')
    m0 = Column(Float, comment='M0（亿元）')
    m0_yoy = Column(Float, comment='M0同比（%）')
    m0_mom = Column(Float, comment='M0环比（%）')
    m1 = Column(Float, comment='M1（亿元）')
    m1_yoy = Column(Float, comment='M1同比（%）')
    m1_mom = Column(Float, comment='M1环比（%）')
    m2 = Column(Float, comment='M2（亿元）')
    m2_yoy = Column(Float, comment='M2同比（%）')
    m2_mom = Column(Float, comment='M2环比（%）')


class CnM(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_cn_m"
        self.database = 'tushare_macroeconomic.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareCnM.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['m', 'start_m', 'end_m', 'limit', 'offset']
        self.tushare_fields = ["month", "m0", "m0_yoy", "m0_mom", "m1", "m1_yoy", "m1_mom", "m2", "m2_yoy", "m2_mom"]
        entity_fields = ["month", "m0", "m0_yoy", "m0_mom", "m1", "m1_yoy", "m1_mom", "m2", "m2_yoy", "m2_mom"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareCnM, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "cn_m", config)
        TuShareBase.__init__(self, "cn_m", config, 600)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "month",
            "type": "String",
            "comment": "月份YYYYMM"
        }, {
            "name": "m0",
            "type": "Float",
            "comment": "M0（亿元）"
        }, {
            "name": "m0_yoy",
            "type": "Float",
            "comment": "M0同比（%）"
        }, {
            "name": "m0_mom",
            "type": "Float",
            "comment": "M0环比（%）"
        }, {
            "name": "m1",
            "type": "Float",
            "comment": "M1（亿元）"
        }, {
            "name": "m1_yoy",
            "type": "Float",
            "comment": "M1同比（%）"
        }, {
            "name": "m1_mom",
            "type": "Float",
            "comment": "M1环比（%）"
        }, {
            "name": "m2",
            "type": "Float",
            "comment": "M2（亿元）"
        }, {
            "name": "m2_yoy",
            "type": "Float",
            "comment": "M2同比（%）"
        }, {
            "name": "m2_mom",
            "type": "Float",
            "comment": "M2环比（%）"
        }]

    def cn_m(self, fields='', **kwargs):
        """
        获取货币供应量月度数据
        | Arguments:
        | m(str):   月度（202001表示，2020年1月）
        | start_m(str):   开始月度
        | end_m(str):   结束月度
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         month(str)  月份YYYYMM Y
         m0(float)  M0（亿元） Y
         m0_yoy(float)  M0同比（%） Y
         m0_mom(float)  M0环比（%） Y
         m1(float)  M1（亿元） Y
         m1_yoy(float)  M1同比（%） Y
         m1_mom(float)  M1环比（%） Y
         m2(float)  M2（亿元） Y
         m2_yoy(float)  M2同比（%） Y
         m2_mom(float)  M2环比（%） Y
        
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append, BatchWriter(self.engine, self.table_name), **kwargs)

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
                self.logger.debug("Invoke pro.cn_m with args: {}".format(kwargs))
                return self.tushare_query('cn_m', fields=self.tushare_fields, **kwargs)
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


setattr(CnM, 'default_limit', default_limit_ext)
setattr(CnM, 'default_cron_express', default_cron_express_ext)
setattr(CnM, 'default_order_by', default_order_by_ext)
setattr(CnM, 'prepare', prepare_ext)
setattr(CnM, 'query_parameters', query_parameters_ext)
setattr(CnM, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.cn_m())

    api = CnM(config)
    print(api.process())    # 同步增量数据
    print(api.cn_m())    # 数据查询接口
