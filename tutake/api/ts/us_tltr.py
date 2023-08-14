"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare us_tltr接口
获取美国国债长期利率数据
数据接口-宏观经济-国际宏观-美国利率-国债长期利率  https://tushare.pro/document/2?doc_id=222

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base
from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.us_tltr_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareUsTltr(Base):
    __tablename__ = "tushare_us_tltr"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, index=True, comment='日期')
    ltc = Column(Float, comment='收益率 LT COMPOSITE (>10 Yrs)')
    cmt = Column(Float, comment='20年期CMT利率(TREASURY 20-Yr CMT)')
    e_factor = Column(Float, comment='外推因子EXTRAPOLATION FACTOR')


class UsTltr(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_shared_engine(config.get_data_sqlite_driver_url('tushare_macroeconomic.db'),
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareUsTltr.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['date', 'start_date', 'end_date', 'fields', 'limit', 'offset']
        entity_fields = ["date", "ltc", "cmt", "e_factor"]
        TushareDAO.__init__(self, self.engine, session_factory, TushareUsTltr, 'tushare_macroeconomic.db',
                            'tushare_us_tltr', query_fields, entity_fields, config)
        DataProcess.__init__(self, "us_tltr", config)
        TuShareBase.__init__(self, "us_tltr", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "date",
            "type": "String",
            "comment": "日期"
        }, {
            "name": "ltc",
            "type": "Float",
            "comment": "收益率 LT COMPOSITE (>10 Yrs)"
        }, {
            "name": "cmt",
            "type": "Float",
            "comment": "20年期CMT利率(TREASURY 20-Yr CMT)"
        }, {
            "name": "e_factor",
            "type": "Float",
            "comment": "外推因子EXTRAPOLATION FACTOR"
        }]

    def us_tltr(self, fields='', **kwargs):
        """
        获取美国国债长期利率数据
        | Arguments:
        | date(str):   日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | fields(str):   指定字段
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         date(str)  日期
         ltc(float)  收益率 LT COMPOSITE (>10 Yrs)
         cmt(float)  20年期CMT利率(TREASURY 20-Yr CMT)
         e_factor(float)  外推因子EXTRAPOLATION FACTOR
        
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
        init_args = {"date": "", "start_date": "", "end_date": "", "fields": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.us_tltr with args: {}".format(kwargs))
                res = self.tushare_query('us_tltr', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_us_tltr', con=self.engine, if_exists='append', index=False, index_label=['ts_code'])
                return res
            except Exception as err:
                raise ProcessException(kwargs, err)

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(UsTltr, 'default_limit', default_limit_ext)
setattr(UsTltr, 'default_cron_express', default_cron_express_ext)
setattr(UsTltr, 'default_order_by', default_order_by_ext)
setattr(UsTltr, 'prepare', prepare_ext)
setattr(UsTltr, 'query_parameters', query_parameters_ext)
setattr(UsTltr, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.us_tltr())

    api = UsTltr(config)
    api.process()    # 同步增量数据
    print(api.us_tltr())    # 数据查询接口
