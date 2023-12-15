"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare limit_list_d接口
获取沪深A股每日涨跌停、炸板数据情况，数据从2020年开始
数据接口-沪深股票-特色数据-涨跌停和炸板数据  https://tushare.pro/document/2?doc_id=298

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import limit_list_d_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareLimitListD(TutakeTableBase):
    __tablename__ = "tushare_limit_list_d"
    trade_date = Column(String, index=True, comment='交易日期')
    ts_code = Column(String, index=True, comment='股票代码')
    industry = Column(String, comment='所属行业')
    name = Column(String, comment='股票名称')
    close = Column(Float, comment='收盘价')
    pct_chg = Column(Float, comment='涨跌幅')
    swing = Column(Float, comment='振幅')
    amount = Column(Float, comment='成交额')
    limit_amount = Column(Float, comment='板上成交金额')
    float_mv = Column(Float, comment='流通市值')
    total_mv = Column(Float, comment='总市值')
    turnover_ratio = Column(Float, comment='换手率')
    fd_amount = Column(Float, comment='封单金额')
    first_time = Column(String, comment='首次封板时间')
    last_time = Column(String, comment='最后封板时间')
    open_times = Column(Integer, comment='炸板次数')
    up_stat = Column(String, comment='涨停统计')
    limit_times = Column(Integer, comment='连板数')
    limits = Column(String, index=True, comment='D跌停U涨停Z炸板')


class LimitListD(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_limit_list_d"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareLimitListD.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareLimitListD),
                                  config.get_tutake_data_dir())

        query_fields = [
            'trade_date', 'ts_code', 'limit_type', 'exchange', 'start_date', 'end_date', 'test', 'limit', 'offset'
        ]
        self.tushare_fields = [
            "trade_date", "ts_code", "industry", "name", "close", "pct_chg", "swing", "amount", "limit_amount",
            "float_mv", "total_mv", "turnover_ratio", "fd_amount", "first_time", "last_time", "open_times", "up_stat",
            "limit_times", "limit"
        ]
        entity_fields = [
            "trade_date", "ts_code", "industry", "name", "close", "pct_chg", "swing", "amount", "limit_amount",
            "float_mv", "total_mv", "turnover_ratio", "fd_amount", "first_time", "last_time", "open_times", "up_stat",
            "limit_times", "limits"
        ]
        column_mapping = {'limits': 'limit'}
        TushareDAO.__init__(self, self.engine, session_factory, TushareLimitListD, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "limit_list_d", config)
        TuShareBase.__init__(self, "limit_list_d", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "ts_code",
            "type": "String",
            "comment": "股票代码"
        }, {
            "name": "industry",
            "type": "String",
            "comment": "所属行业"
        }, {
            "name": "name",
            "type": "String",
            "comment": "股票名称"
        }, {
            "name": "close",
            "type": "Float",
            "comment": "收盘价"
        }, {
            "name": "pct_chg",
            "type": "Float",
            "comment": "涨跌幅"
        }, {
            "name": "swing",
            "type": "Float",
            "comment": "振幅"
        }, {
            "name": "amount",
            "type": "Float",
            "comment": "成交额"
        }, {
            "name": "limit_amount",
            "type": "Float",
            "comment": "板上成交金额"
        }, {
            "name": "float_mv",
            "type": "Float",
            "comment": "流通市值"
        }, {
            "name": "total_mv",
            "type": "Float",
            "comment": "总市值"
        }, {
            "name": "turnover_ratio",
            "type": "Float",
            "comment": "换手率"
        }, {
            "name": "fd_amount",
            "type": "Float",
            "comment": "封单金额"
        }, {
            "name": "first_time",
            "type": "String",
            "comment": "首次封板时间"
        }, {
            "name": "last_time",
            "type": "String",
            "comment": "最后封板时间"
        }, {
            "name": "open_times",
            "type": "Integer",
            "comment": "炸板次数"
        }, {
            "name": "up_stat",
            "type": "String",
            "comment": "涨停统计"
        }, {
            "name": "limit_times",
            "type": "Integer",
            "comment": "连板数"
        }, {
            "name": "limit",
            "type": "String",
            "comment": "D跌停U涨停Z炸板"
        }]

    def limit_list_d(
            self,
            fields='trade_date,ts_code,industry,name,close,pct_chg,amount,limit_amount,float_mv,total_mv,turnover_ratio,fd_amount,first_time,last_time,open_times,up_stat,limit_times,limits',
            **kwargs):
        """
        获取沪深A股每日涨跌停、炸板数据情况，数据从2020年开始
        | Arguments:
        | trade_date(str):   交易日期
        | ts_code(str):   股票代码
        | limit_type(str):   涨跌停类型U涨停D跌停Z炸板
        | exchange(str):   交易所（SH上交所SZ深交所BJ北交所）
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | test(float):   
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  交易日期 Y
         ts_code(str)  股票代码 Y
         industry(str)  所属行业 Y
         name(str)  股票名称 Y
         close(float)  收盘价 Y
         pct_chg(float)  涨跌幅 Y
         swing(float)  振幅 N
         amount(float)  成交额 Y
         limit_amount(float)  板上成交金额 Y
         float_mv(float)  流通市值 Y
         total_mv(float)  总市值 Y
         turnover_ratio(float)  换手率 Y
         fd_amount(float)  封单金额 Y
         first_time(str)  首次封板时间 Y
         last_time(str)  最后封板时间 Y
         open_times(int)  炸板次数 Y
         up_stat(str)  涨停统计 Y
         limit_times(int)  连板数 Y
         limit(str)  D跌停U涨停Z炸板 Y
        
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
        init_args = {
            "trade_date": "",
            "ts_code": "",
            "limit_type": "",
            "exchange": "",
            "start_date": "",
            "end_date": "",
            "test": "",
            "limit": "",
            "offset": ""
        }
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
                self.logger.debug("Invoke pro.limit_list_d with args: {}".format(kwargs))
                return self.tushare_query('limit_list_d', fields=self.tushare_fields, **kwargs)
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


extends_attr(LimitListD, limit_list_d_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.limit_list_d())

    api = LimitListD(config)
    print(api.process())    # 同步增量数据
    print(api.limit_list_d())    # 数据查询接口
