"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare anns接口
获取上市公司公告数据及原文文本，数据从2000年开始。
数据接口-另类数据-上市公司公告原文  https://tushare.pro/document/2?doc_id=176

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base
from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.anns_ext import *
from tutake.api.ts.tushare_dao import TushareDAO
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


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


class Anns(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine(config.get_data_sqlite_driver_url('tushare_anns.db'),
                                    connect_args={
                                        'check_same_thread': False,
                                        'timeout': config.get_sqlite_timeout()
                                    })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareAnns.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'ann_date', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = ["ts_code", "ann_date", "ann_type", "title", "content", "pub_time", "src_url", "filepath"]
        TushareDAO.__init__(self, self.engine, session_factory, TushareAnns, 'tushare_anns.db', 'tushare_anns',
                            query_fields, entity_fields, config)
        DataProcess.__init__(self, "anns", config)
        TuShareBase.__init__(self, "anns", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "股票代码"
        }, {
            "name": "ann_date",
            "type": "String",
            "comment": "公告日期"
        }, {
            "name": "ann_type",
            "type": "String",
            "comment": "公告类型"
        }, {
            "name": "title",
            "type": "String",
            "comment": "公告标题"
        }, {
            "name": "content",
            "type": "String",
            "comment": "公告内容"
        }, {
            "name": "pub_time",
            "type": "String",
            "comment": "公告发布时间"
        }, {
            "name": "src_url",
            "type": "String",
            "comment": "pdf原文URL"
        }, {
            "name": "filepath",
            "type": "String",
            "comment": "pdf原文"
        }]

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

        def fetch_save(offset_val=0):
            try:
                kwargs['offset'] = str(offset_val)
                self.logger.debug("Invoke pro.anns with args: {}".format(kwargs))
                res = self.tushare_query('anns', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_anns', con=self.engine, if_exists='append', index=False, index_label=['ts_code'])
                return res
            except Exception as err:
                raise ProcessException(kwargs, err)

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
setattr(Anns, 'query_parameters', query_parameters_ext)
setattr(Anns, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.anns())

    api = Anns(config)
    api.process()    # 同步增量数据
    print(api.anns())    # 数据查询接口
