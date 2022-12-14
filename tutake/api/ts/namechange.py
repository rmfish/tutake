"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare namechange接口
历史名称变更记录
数据接口-沪深股票-基础数据-股票曾用名  https://tushare.pro/document/2?doc_id=100

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base
from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.namechange_ext import *
from tutake.api.ts.tushare_dao import TushareDAO
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareNamechange(Base):
    __tablename__ = "tushare_namechange"
    id = Column(Integer, primary_key=True, autoincrement=True)
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
        self.engine = create_engine(config.get_data_sqlite_driver_url('tushare_basic_data.db'),
                                    connect_args={'check_same_thread': False})
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareNamechange.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = ["ts_code", "name", "start_date", "end_date", "ann_date", "change_reason"]
        TushareDAO.__init__(self, self.engine, session_factory, TushareNamechange, 'tushare_namechange', query_fields,
                            entity_fields, config)
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
         ts_code(str)  TS代码
         name(str)  证券名称
         start_date(str)  开始日期
         end_date(str)  结束日期
         ann_date(str)  公告日期
         change_reason(str)  变更原因
        
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
        init_args = {"ts_code": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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
                res = self.tushare_query('namechange', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_namechange',
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


setattr(Namechange, 'default_limit', default_limit_ext)
setattr(Namechange, 'default_cron_express', default_cron_express_ext)
setattr(Namechange, 'default_order_by', default_order_by_ext)
setattr(Namechange, 'prepare', prepare_ext)
setattr(Namechange, 'query_parameters', query_parameters_ext)
setattr(Namechange, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.namechange())

    api = Namechange(config)
    api.process()    # 同步增量数据
    print(api.namechange())    # 数据查询接口
