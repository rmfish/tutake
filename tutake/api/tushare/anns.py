"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare anns接口
获取上市公司公告数据及原文文本，数据从2000年开始。
数据接口-另类数据-上市公司公告原文  https://tushare.pro/document/2?doc_id=176

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessType
from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.anns_ext import *
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_anns.db'),
                       connect_args={'check_same_thread': False})
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()


class TushareAnns(Base):
    __tablename__ = "tushare_anns"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='股票代码')
    ann_date = Column(String, index=True, comment='公告日期')
    ann_type = Column(String, comment='公告类型')
    title = Column(String, comment='公告标题')
    content = Column(String, comment='公告内容')
    pub_time = Column(String, comment='公告发布时间')
    src_url = Column(String, comment='pdf原文URL')
    filepath = Column(String, comment='pdf原文')


TushareAnns.__table__.create(bind=engine, checkfirst=True)


class Anns(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = ['ts_code', 'ann_date', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = ["ts_code", "ann_date", "ann_type", "title", "content", "pub_time", "src_url", "filepath"]
        BaseDao.__init__(self, engine, session_factory, TushareAnns, 'tushare_anns', query_fields, entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "anns")
        self.dao = DAO()

    def anns(self, fields='', **kwargs):
        """
        获取上市公司公告数据及原文文本，数据从2000年开始。
        | Arguments:
        | ts_code(str):   股票代码
        | ann_date(str):   公告日期
        | start_date(str):   公告开始日期
        | end_date(str):   公告结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  股票代码
         ann_date(str)  公告日期
         ann_type(str)  公告类型
         title(str)  公告标题
         content(str)  公告内容
         pub_time(str)  公告发布时间
         src_url(str)  pdf原文URL
         filepath(str)  pdf原文
        
        """
        return super().query(fields, **kwargs)

    def process(self, process_type: ProcessType):
        """
        同步历史数据
        :return:
        """
        return super()._process(process_type, self.fetch_and_append)

    def fetch_and_append(self, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        init_args = {"ts_code": "", "ann_date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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

        @sleep(timeout=61, time_append=60, retry=20, match="^抱歉，您每分钟最多访问该接口")
        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            self.logger.debug("Invoke pro.anns with args: {}".format(kwargs))
            res = self.tushare_api().anns(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_anns', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(Anns, 'default_limit', default_limit_ext)
setattr(Anns, 'default_cron_express', default_cron_express_ext)
setattr(Anns, 'default_order_by', default_order_by_ext)
setattr(Anns, 'prepare', prepare_ext)
setattr(Anns, 'tushare_parameters', tushare_parameters_ext)
setattr(Anns, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    api = Anns()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    api.process(ProcessType.INCREASE)    # 同步增量数据
    print(api.anns())    # 数据查询接口
