"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare cn_gdp接口
获取国民经济之GDP数据
数据接口-宏观经济-国内宏观-国民经济-国内生产总值（GDP）  https://tushare.pro/document/2?doc_id=227

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.cn_gdp_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareCnGdp(Base):
    __tablename__ = "tushare_cn_gdp"
    id = Column(Integer, primary_key=True, autoincrement=True)
    quarter = Column(String, comment='季度')
    gdp = Column(Float, comment='GDP累计值（亿元）')
    gdp_yoy = Column(Float, comment='当季同比增速（%）')
    pi = Column(Float, comment='第一产业累计值（亿元）')
    pi_yoy = Column(Float, comment='第一产业同比增速（%）')
    si = Column(Float, comment='第二产业累计值（亿元）')
    si_yoy = Column(Float, comment='第二产业同比增速（%）')
    ti = Column(Float, comment='第三产业累计值（亿元）')
    ti_yoy = Column(Float, comment='第三产业同比增速（%）')


class CnGdp(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_cn_gdp"
        self.database = 'tushare_macroeconomic.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareCnGdp.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['q', 'start_q', 'end_q', 'limit', 'offset']
        entity_fields = ["quarter", "gdp", "gdp_yoy", "pi", "pi_yoy", "si", "si_yoy", "ti", "ti_yoy"]
        TushareDAO.__init__(self, self.engine, session_factory, TushareCnGdp, self.database, self.table_name,
                            query_fields, entity_fields, config)
        DataProcess.__init__(self, "cn_gdp", config)
        TuShareBase.__init__(self, "cn_gdp", config, 600)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "quarter",
            "type": "String",
            "comment": "季度"
        }, {
            "name": "gdp",
            "type": "Float",
            "comment": "GDP累计值（亿元）"
        }, {
            "name": "gdp_yoy",
            "type": "Float",
            "comment": "当季同比增速（%）"
        }, {
            "name": "pi",
            "type": "Float",
            "comment": "第一产业累计值（亿元）"
        }, {
            "name": "pi_yoy",
            "type": "Float",
            "comment": "第一产业同比增速（%）"
        }, {
            "name": "si",
            "type": "Float",
            "comment": "第二产业累计值（亿元）"
        }, {
            "name": "si_yoy",
            "type": "Float",
            "comment": "第二产业同比增速（%）"
        }, {
            "name": "ti",
            "type": "Float",
            "comment": "第三产业累计值（亿元）"
        }, {
            "name": "ti_yoy",
            "type": "Float",
            "comment": "第三产业同比增速（%）"
        }]

    def cn_gdp(self, fields='', **kwargs):
        """
        获取国民经济之GDP数据
        | Arguments:
        | q(str):   季度
        | start_q(str):   开始季度
        | end_q(str):   结束季度
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         quarter(str)  季度 Y
         gdp(float)  GDP累计值（亿元） Y
         gdp_yoy(float)  当季同比增速（%） Y
         pi(float)  第一产业累计值（亿元） Y
         pi_yoy(float)  第一产业同比增速（%） Y
         si(float)  第二产业累计值（亿元） Y
         si_yoy(float)  第二产业同比增速（%） Y
         ti(float)  第三产业累计值（亿元） Y
         ti_yoy(float)  第三产业同比增速（%） Y
        
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
        init_args = {"q": "", "start_q": "", "end_q": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.cn_gdp with args: {}".format(kwargs))
                return self.tushare_query('cn_gdp', fields=self.entity_fields, **kwargs)
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
        return res


setattr(CnGdp, 'default_limit', default_limit_ext)
setattr(CnGdp, 'default_cron_express', default_cron_express_ext)
setattr(CnGdp, 'default_order_by', default_order_by_ext)
setattr(CnGdp, 'prepare', prepare_ext)
setattr(CnGdp, 'query_parameters', query_parameters_ext)
setattr(CnGdp, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.cn_gdp())

    api = CnGdp(config)
    print(api.process())    # 同步增量数据
    print(api.cn_gdp())    # 数据查询接口
