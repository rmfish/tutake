"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare top10_floatholders接口
获取上市公司前十大流通股东数据。
数据接口-沪深股票-市场参考数据-前十大流通股东  https://tushare.pro/document/2?doc_id=62

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.top10_floatholders_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareTop10Floatholders(Base):
    __tablename__ = "tushare_top10_floatholders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='TS股票代码')
    ann_date = Column(String, index=True, comment='公告日期')
    end_date = Column(String, index=True, comment='报告期')
    holder_name = Column(String, comment='股东名称')
    hold_amount = Column(Float, comment='持有数量')


class Top10Floatholders(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_top10_floatholders"
        self.database = 'tushare_report.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareTop10Floatholders.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'period', 'ann_date', 'start_date', 'end_date', 'offset', 'limit']
        self.tushare_fields = ["ts_code", "ann_date", "end_date", "holder_name", "hold_amount"]
        entity_fields = ["ts_code", "ann_date", "end_date", "holder_name", "hold_amount"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareTop10Floatholders, self.database,
                            self.table_name, query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "top10_floatholders", config)
        TuShareBase.__init__(self, "top10_floatholders", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS股票代码"
        }, {
            "name": "ann_date",
            "type": "String",
            "comment": "公告日期"
        }, {
            "name": "end_date",
            "type": "String",
            "comment": "报告期"
        }, {
            "name": "holder_name",
            "type": "String",
            "comment": "股东名称"
        }, {
            "name": "hold_amount",
            "type": "Float",
            "comment": "持有数量"
        }]

    def top10_floatholders(self, fields='', **kwargs):
        """
        获取上市公司前十大流通股东数据。
        | Arguments:
        | ts_code(str):   TS代码
        | period(str):   报告期
        | ann_date(str):   公告日期
        | start_date(str):   报告期开始日期
        | end_date(str):   报告期结束日期
        | offset(str):   
        | limit(str):   
        
        :return: DataFrame
         ts_code(str)  TS股票代码 Y
         ann_date(str)  公告日期 Y
         end_date(str)  报告期 Y
         holder_name(str)  股东名称 Y
         hold_amount(float)  持有数量 Y
        
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
        init_args = {
            "ts_code": "",
            "period": "",
            "ann_date": "",
            "start_date": "",
            "end_date": "",
            "offset": "",
            "limit": ""
        }
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
                self.logger.debug("Invoke pro.top10_floatholders with args: {}".format(kwargs))
                return self.tushare_query('top10_floatholders', fields=self.tushare_fields, **kwargs)
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


setattr(Top10Floatholders, 'default_limit', default_limit_ext)
setattr(Top10Floatholders, 'default_cron_express', default_cron_express_ext)
setattr(Top10Floatholders, 'default_order_by', default_order_by_ext)
setattr(Top10Floatholders, 'prepare', prepare_ext)
setattr(Top10Floatholders, 'query_parameters', query_parameters_ext)
setattr(Top10Floatholders, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.top10_floatholders())

    api = Top10Floatholders(config)
    print(api.process())    # 同步增量数据
    print(api.top10_floatholders())    # 数据查询接口
