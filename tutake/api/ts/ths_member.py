"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare ths_member接口
获取同花顺概念板块成分列表
数据接口-指数-同花顺概念和行业指数成分  https://tushare.pro/document/2?doc_id=261

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.ths_member_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareThsMember(Base):
    __tablename__ = "tushare_ths_member"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='指数代码')
    code = Column(String, index=True, comment='股票代码')
    name = Column(String, comment='股票名称')
    weight = Column(Float, comment='权重')
    in_date = Column(String, comment='纳入日期')
    out_date = Column(String, comment='剔除日期')
    is_new = Column(String, comment='是否最新Y是N否')


class ThsMember(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_ths_member"
        self.database = 'tushare_ths.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareThsMember.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'code', 'limit', 'offset']
        entity_fields = ["ts_code", "code", "name", "weight", "in_date", "out_date", "is_new"]
        TushareDAO.__init__(self, self.engine, session_factory, TushareThsMember, self.database, self.table_name,
                            query_fields, entity_fields, config)
        DataProcess.__init__(self, "ths_member", config)
        TuShareBase.__init__(self, "ths_member", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "指数代码"
        }, {
            "name": "code",
            "type": "String",
            "comment": "股票代码"
        }, {
            "name": "name",
            "type": "String",
            "comment": "股票名称"
        }, {
            "name": "weight",
            "type": "Float",
            "comment": "权重"
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
            "comment": "是否最新Y是N否"
        }]

    def ths_member(self, fields='ts_code,code,name', **kwargs):
        """
        获取同花顺概念板块成分列表
        | Arguments:
        | ts_code(str):   板块指数代码
        | code(str):   股票代码
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  指数代码 Y
         code(str)  股票代码 Y
         name(str)  股票名称 Y
         weight(float)  权重 N
         in_date(str)  纳入日期 N
         out_date(str)  剔除日期 N
         is_new(str)  是否最新Y是N否 N
        
        """
        return super().query(fields, **kwargs)

    def process(self):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append, BatchWriter(self.engine, self.table_name))

    def fetch_and_append(self, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        init_args = {"ts_code": "", "code": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.ths_member with args: {}".format(kwargs))
                return self.tushare_query('ths_member', fields=self.entity_fields, **kwargs)
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


setattr(ThsMember, 'default_limit', default_limit_ext)
setattr(ThsMember, 'default_cron_express', default_cron_express_ext)
setattr(ThsMember, 'default_order_by', default_order_by_ext)
setattr(ThsMember, 'prepare', prepare_ext)
setattr(ThsMember, 'query_parameters', query_parameters_ext)
setattr(ThsMember, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.ths_member())

    api = ThsMember(config)
    api.process()    # 同步增量数据
    print(api.ths_member())    # 数据查询接口
