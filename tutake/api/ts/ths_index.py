"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare ths_index接口
获取同花顺板块指数
数据接口-指数-同花顺概念和行业列表  https://tushare.pro/document/2?doc_id=259

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base
from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.ths_index_ext import *
from tutake.api.ts.tushare_dao import TushareDAO
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareThsIndex(Base):
    __tablename__ = "tushare_ths_index"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='代码')
    name = Column(String, comment='名称')
    count = Column(Integer, comment='成分个数')
    exchange = Column(String, index=True, comment='交易所')
    list_date = Column(String, comment='上市日期')
    type = Column(String, index=True, comment='N概念指数S特色指数')


class ThsIndex(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine(config.get_data_sqlite_driver_url('tushare_ths_index.db'),
                                    connect_args={
                                        'check_same_thread': False,
                                        'timeout': config.get_sqlite_timeout()
                                    })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareThsIndex.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'exchange', 'type', 'limit', 'offset']
        entity_fields = ["ts_code", "name", "count", "exchange", "list_date", "type"]
        TushareDAO.__init__(self, self.engine, session_factory, TushareThsIndex, 'tushare_ths_index', query_fields,
                            entity_fields, config)
        DataProcess.__init__(self, "ths_index", config)
        TuShareBase.__init__(self, "ths_index", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "代码"
        }, {
            "name": "name",
            "type": "String",
            "comment": "名称"
        }, {
            "name": "count",
            "type": "Integer",
            "comment": "成分个数"
        }, {
            "name": "exchange",
            "type": "String",
            "comment": "交易所"
        }, {
            "name": "list_date",
            "type": "String",
            "comment": "上市日期"
        }, {
            "name": "type",
            "type": "String",
            "comment": "N概念指数S特色指数"
        }]

    def ths_index(self, fields='', **kwargs):
        """
        获取同花顺板块指数
        | Arguments:
        | ts_code(str):   指数代码
        | exchange(str):   市场类型A-a股票 HK-港股 US-美股
        | type(str):   指数类型 N-板块指数 S-同花顺特色指数
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  代码
         name(str)  名称
         count(int)  成分个数
         exchange(str)  交易所
         list_date(str)  上市日期
         type(str)  N概念指数S特色指数
        
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
        init_args = {"ts_code": "", "exchange": "", "type": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.ths_index with args: {}".format(kwargs))
                res = self.tushare_query('ths_index', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_ths_index',
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


setattr(ThsIndex, 'default_limit', default_limit_ext)
setattr(ThsIndex, 'default_cron_express', default_cron_express_ext)
setattr(ThsIndex, 'default_order_by', default_order_by_ext)
setattr(ThsIndex, 'prepare', prepare_ext)
setattr(ThsIndex, 'query_parameters', query_parameters_ext)
setattr(ThsIndex, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.ths_index())

    api = ThsIndex(config)
    api.process()    # 同步增量数据
    print(api.ths_index())    # 数据查询接口
