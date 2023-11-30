"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare index_dailybasic接口
大盘指数每日指标，目前只提供上证综指，深证成指，上证50，中证500，中小板指，创业板指的每日指标数据
数据接口-指数-大盘指数每日指标  https://tushare.pro/document/2?doc_id=128

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import index_dailybasic_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareIndexDailybasic(TutakeTableBase):
    __tablename__ = "tushare_index_dailybasic"
    ts_code = Column(String, index=True, comment='TS代码')
    trade_date = Column(String, index=True, comment='交易日期')
    total_mv = Column(Float, comment='当日总市值')
    float_mv = Column(Float, comment='当日流通市值')
    total_share = Column(Float, comment='当日总股本')
    float_share = Column(Float, comment='当日流通股本')
    free_share = Column(Float, comment='当日自由流通股本')
    turnover_rate = Column(Float, comment='换手率')
    turnover_rate_f = Column(Float, comment='换手率(自由流通股本)')
    pe = Column(Float, comment='市盈率')
    pe_ttm = Column(Float, comment='市盈率TTM')
    pb = Column(Float, comment='市净率')


class IndexDailybasic(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_index_dailybasic"
        self.database = 'tutake.duckdb'
        self.database_dir = config.get_tutake_data_dir()
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareIndexDailybasic.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareIndexDailybasic)

        query_fields = ['trade_date', 'ts_code', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "trade_date", "total_mv", "float_mv", "total_share", "float_share", "free_share",
            "turnover_rate", "turnover_rate_f", "pe", "pe_ttm", "pb"
        ]
        entity_fields = [
            "ts_code", "trade_date", "total_mv", "float_mv", "total_share", "float_share", "free_share",
            "turnover_rate", "turnover_rate_f", "pe", "pe_ttm", "pb"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareIndexDailybasic, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "index_dailybasic", config)
        TuShareBase.__init__(self, "index_dailybasic", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS代码"
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "total_mv",
            "type": "Float",
            "comment": "当日总市值"
        }, {
            "name": "float_mv",
            "type": "Float",
            "comment": "当日流通市值"
        }, {
            "name": "total_share",
            "type": "Float",
            "comment": "当日总股本"
        }, {
            "name": "float_share",
            "type": "Float",
            "comment": "当日流通股本"
        }, {
            "name": "free_share",
            "type": "Float",
            "comment": "当日自由流通股本"
        }, {
            "name": "turnover_rate",
            "type": "Float",
            "comment": "换手率"
        }, {
            "name": "turnover_rate_f",
            "type": "Float",
            "comment": "换手率(自由流通股本)"
        }, {
            "name": "pe",
            "type": "Float",
            "comment": "市盈率"
        }, {
            "name": "pe_ttm",
            "type": "Float",
            "comment": "市盈率TTM"
        }, {
            "name": "pb",
            "type": "Float",
            "comment": "市净率"
        }]

    def index_dailybasic(self, fields='', **kwargs):
        """
        大盘指数每日指标，目前只提供上证综指，深证成指，上证50，中证500，中小板指，创业板指的每日指标数据
        | Arguments:
        | trade_date(str):   交易日期
        | ts_code(str):   TS指数代码
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS代码 Y
         trade_date(str)  交易日期 Y
         total_mv(float)  当日总市值 Y
         float_mv(float)  当日流通市值 Y
         total_share(float)  当日总股本 Y
         float_share(float)  当日流通股本 Y
         free_share(float)  当日自由流通股本 Y
         turnover_rate(float)  换手率 Y
         turnover_rate_f(float)  换手率(自由流通股本) Y
         pe(float)  市盈率 Y
         pe_ttm(float)  市盈率TTM Y
         pb(float)  市净率 Y
        
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append,
                                BatchWriter(self.engine, self.table_name, self.schema, self.database_dir), **kwargs)

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
                self.logger.debug("Invoke pro.index_dailybasic with args: {}".format(kwargs))
                return self.tushare_query('index_dailybasic', fields=self.tushare_fields, **kwargs)
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


extends_attr(IndexDailybasic, index_dailybasic_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.index_dailybasic(ts_code='000001.SH'))

    api = IndexDailybasic(config)
    print(api.process())    # 同步增量数据
    print(api.index_dailybasic(ts_code='000001.SH'))    # 数据查询接口
