"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare sz_daily_info接口
获取深圳市场每日交易概况
数据接口-指数-深圳市场每日交易情况  https://tushare.pro/document/2?doc_id=268

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import sz_daily_info_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareSzDailyInfo(TutakeTableBase):
    __tablename__ = "tushare_sz_daily_info"
    trade_date = Column(String, index=True, comment='')
    ts_code = Column(String, index=True, comment='市场类型')
    count = Column(Integer, comment='股票个数')
    amount = Column(Float, comment='成交金额')
    vol = Column(Float, comment='成交量')
    total_share = Column(Float, comment='总股本')
    total_mv = Column(Float, comment='总市值')
    float_share = Column(Float, comment='流通股票')
    float_mv = Column(Float, comment='流通市值')


class SzDailyInfo(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_sz_daily_info"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareSzDailyInfo.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareSzDailyInfo),
                                  config.get_tutake_data_dir())

        query_fields = ['trade_date', 'ts_code', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = [
            "trade_date", "ts_code", "count", "amount", "vol", "total_share", "total_mv", "float_share", "float_mv"
        ]
        entity_fields = [
            "trade_date", "ts_code", "count", "amount", "vol", "total_share", "total_mv", "float_share", "float_mv"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareSzDailyInfo, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "sz_daily_info", config)
        TuShareBase.__init__(self, "sz_daily_info", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "trade_date",
            "type": "String",
            "comment": ""
        }, {
            "name": "ts_code",
            "type": "String",
            "comment": "市场类型"
        }, {
            "name": "count",
            "type": "Integer",
            "comment": "股票个数"
        }, {
            "name": "amount",
            "type": "Float",
            "comment": "成交金额"
        }, {
            "name": "vol",
            "type": "Float",
            "comment": "成交量"
        }, {
            "name": "total_share",
            "type": "Float",
            "comment": "总股本"
        }, {
            "name": "total_mv",
            "type": "Float",
            "comment": "总市值"
        }, {
            "name": "float_share",
            "type": "Float",
            "comment": "流通股票"
        }, {
            "name": "float_mv",
            "type": "Float",
            "comment": "流通市值"
        }]

    def sz_daily_info(self, fields='', **kwargs):
        """
        获取深圳市场每日交易概况
        | Arguments:
        | trade_date(str):   交易日期
        | ts_code(str):   板块代码
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)   Y
         ts_code(str)  市场类型 Y
         count(int)  股票个数 Y
         amount(float)  成交金额 Y
         vol(float)  成交量 Y
         total_share(float)  总股本 Y
         total_mv(float)  总市值 Y
         float_share(float)  流通股票 Y
         float_mv(float)  流通市值 Y
        
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append, self.writer, **kwargs)

    def fetch_and_append(self, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        init_args = {"trade_date": "", "ts_code": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
        is_test = kwargs.get('test') or False
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
                self.logger.debug("Invoke pro.sz_daily_info with args: {}".format(kwargs))
                return self.tushare_query('sz_daily_info', fields=self.tushare_fields, **kwargs)
            except Exception as err:
                raise ProcessException(kwargs, err)

        res = fetch_save(offset)
        size = res.size()
        offset += size
        res.fields = self.entity_fields
        if is_test:
            return res
        while kwargs['limit'] != "" and size == int(kwargs['limit']):
            result = fetch_save(offset)
            size = result.size()
            offset += size
            res.append(result)
        return res


extends_attr(SzDailyInfo, sz_daily_info_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.sz_daily_info())

    api = SzDailyInfo(config)
    print(api.process())    # 同步增量数据
    print(api.sz_daily_info())    # 数据查询接口
