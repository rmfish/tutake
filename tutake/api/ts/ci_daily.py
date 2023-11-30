"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare ci_daily接口
获取国际主要指数日线行情
数据接口-指数-中信行业指数日行情  https://tushare.pro/document/2?doc_id=308

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import ci_daily_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareCiDaily(TutakeTableBase):
    __tablename__ = "tushare_ci_daily"
    ts_code = Column(String, index=True, comment='指数代码')
    trade_date = Column(String, index=True, comment='交易日期')
    open = Column(Float, comment='开盘点位')
    low = Column(Float, comment='最低点位')
    high = Column(Float, comment='最高点位')
    close = Column(Float, comment='收盘点位')
    pre_close = Column(Float, comment='昨日收盘点位')
    change = Column(Float, comment='涨跌点位')
    pct_change = Column(Float, comment='涨跌幅')
    vol = Column(Float, comment='成交量（万股）')
    amount = Column(Float, comment='成交额（万元）')


class CiDaily(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_ci_daily"
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
        TushareCiDaily.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareCiDaily)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "trade_date", "open", "low", "high", "close", "pre_close", "change", "pct_change", "vol",
            "amount"
        ]
        entity_fields = [
            "ts_code", "trade_date", "open", "low", "high", "close", "pre_close", "change", "pct_change", "vol",
            "amount"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareCiDaily, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "ci_daily", config)
        TuShareBase.__init__(self, "ci_daily", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "指数代码"
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "open",
            "type": "Float",
            "comment": "开盘点位"
        }, {
            "name": "low",
            "type": "Float",
            "comment": "最低点位"
        }, {
            "name": "high",
            "type": "Float",
            "comment": "最高点位"
        }, {
            "name": "close",
            "type": "Float",
            "comment": "收盘点位"
        }, {
            "name": "pre_close",
            "type": "Float",
            "comment": "昨日收盘点位"
        }, {
            "name": "change",
            "type": "Float",
            "comment": "涨跌点位"
        }, {
            "name": "pct_change",
            "type": "Float",
            "comment": "涨跌幅"
        }, {
            "name": "vol",
            "type": "Float",
            "comment": "成交量（万股）"
        }, {
            "name": "amount",
            "type": "Float",
            "comment": "成交额（万元）"
        }]

    def ci_daily(self, fields='', **kwargs):
        """
        获取国际主要指数日线行情
        | Arguments:
        | ts_code(str):   行业代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  指数代码 Y
         trade_date(str)  交易日期 Y
         open(float)  开盘点位 Y
         low(float)  最低点位 Y
         high(float)  最高点位 Y
         close(float)  收盘点位 Y
         pre_close(float)  昨日收盘点位 Y
         change(float)  涨跌点位 Y
         pct_change(float)  涨跌幅 Y
         vol(float)  成交量（万股） Y
         amount(float)  成交额（万元） Y
        
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
        init_args = {"ts_code": "", "trade_date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.ci_daily with args: {}".format(kwargs))
                return self.tushare_query('ci_daily', fields=self.tushare_fields, **kwargs)
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


extends_attr(CiDaily, ci_daily_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.ci_daily())

    api = CiDaily(config)
    print(api.process())    # 同步增量数据
    print(api.ci_daily())    # 数据查询接口
