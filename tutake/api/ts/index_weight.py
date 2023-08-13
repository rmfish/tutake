"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare index_weight接口
获取各类指数成分和权重，月度数据 。
数据接口-指数-指数成分和权重  https://tushare.pro/document/2?doc_id=96

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base
from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.index_weight_ext import *
from tutake.api.ts.tushare_dao import TushareDAO
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareIndexWeight(Base):
    __tablename__ = "tushare_index_weight"
    id = Column(Integer, primary_key=True, autoincrement=True)
    index_code = Column(String, index=True, comment='指数代码')
    con_code = Column(String, comment='成分代码')
    trade_date = Column(String, index=True, comment='交易日期')
    weight = Column(Float, comment='权重')


class IndexWeight(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine(config.get_data_sqlite_driver_url('tushare_index_weight.db'),
                                    connect_args={
                                        'check_same_thread': False,
                                        'timeout': config.get_sqlite_timeout()
                                    })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareIndexWeight.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['index_code', 'trade_date', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = ["index_code", "con_code", "trade_date", "weight"]
        TushareDAO.__init__(self, self.engine, session_factory, TushareIndexWeight, 'tushare_index_weight.db',
                            'tushare_index_weight', query_fields, entity_fields, config)
        DataProcess.__init__(self, "index_weight", config)
        TuShareBase.__init__(self, "index_weight", config, 2000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "index_code",
            "type": "String",
            "comment": "指数代码"
        }, {
            "name": "con_code",
            "type": "String",
            "comment": "成分代码"
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "weight",
            "type": "Float",
            "comment": "权重"
        }]

    def index_weight(self, fields='', **kwargs):
        """
        获取各类指数成分和权重，月度数据 。
        | Arguments:
        | index_code(str):   指数代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         index_code(str)  指数代码
         con_code(str)  成分代码
         trade_date(str)  交易日期
         weight(float)  权重
        
        """
        return super().query(fields, **kwargs)

    def process(self):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append)

    def fetch_and_append(self, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        init_args = {"index_code": "", "trade_date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.index_weight with args: {}".format(kwargs))
                res = self.tushare_query('index_weight', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_index_weight',
                           con=self.engine,
                           if_exists='append',
                           index=False,
                           index_label=['ts_code'])
                return res
            except Exception as err:
                raise ProcessException(kwargs, err)

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(IndexWeight, 'default_limit', default_limit_ext)
setattr(IndexWeight, 'default_cron_express', default_cron_express_ext)
setattr(IndexWeight, 'default_order_by', default_order_by_ext)
setattr(IndexWeight, 'prepare', prepare_ext)
setattr(IndexWeight, 'query_parameters', query_parameters_ext)
setattr(IndexWeight, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.index_weight(index_code='000905.SH'))
    # print(pro.index_weight(trade_date='20050415'))
    # print(pro.index_weight(trade_date='20230811'))
    #
    api = IndexWeight(config)
    api.process()    # 同步增量数据
    print(api.index_weight())    # 数据查询接口
