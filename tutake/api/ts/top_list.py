"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare top_list接口
龙虎榜每日交易明细,数据开始于2005年，每日晚8点更新
数据接口-沪深股票-市场参考数据-龙虎榜每日明细  https://tushare.pro/document/2?doc_id=106

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import top_list_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareTopList(TutakeTableBase):
    __tablename__ = "tushare_top_list"
    trade_date = Column(String, index=True, comment='交易日期')
    ts_code = Column(String, index=True, comment='TS代码')
    name = Column(String, comment='名称')
    close = Column(Float, comment='收盘价')
    pct_change = Column(Float, comment='涨跌幅')
    turnover_rate = Column(Float, comment='换手率')
    amount = Column(Float, comment='总成交额')
    l_sell = Column(Float, comment='龙虎榜卖出额')
    l_buy = Column(Float, comment='龙虎榜买入额')
    l_amount = Column(Float, comment='龙虎榜成交额')
    net_amount = Column(Float, comment='龙虎榜净买入额')
    net_rate = Column(Float, comment='龙虎榜净买额占比')
    amount_rate = Column(Float, comment='龙虎榜成交额占比')
    float_values = Column(Float, comment='当日流通市值')
    reason = Column(String, comment='上榜理由')


class TopList(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_top_list"
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
        TushareTopList.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareTopList)

        query_fields = ['trade_date', 'ts_code', 'limit', 'offset']
        self.tushare_fields = [
            "trade_date", "ts_code", "name", "close", "pct_change", "turnover_rate", "amount", "l_sell", "l_buy",
            "l_amount", "net_amount", "net_rate", "amount_rate", "float_values", "reason"
        ]
        entity_fields = [
            "trade_date", "ts_code", "name", "close", "pct_change", "turnover_rate", "amount", "l_sell", "l_buy",
            "l_amount", "net_amount", "net_rate", "amount_rate", "float_values", "reason"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareTopList, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "top_list", config)
        TuShareBase.__init__(self, "top_list", config, 2000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "ts_code",
            "type": "String",
            "comment": "TS代码"
        }, {
            "name": "name",
            "type": "String",
            "comment": "名称"
        }, {
            "name": "close",
            "type": "Float",
            "comment": "收盘价"
        }, {
            "name": "pct_change",
            "type": "Float",
            "comment": "涨跌幅"
        }, {
            "name": "turnover_rate",
            "type": "Float",
            "comment": "换手率"
        }, {
            "name": "amount",
            "type": "Float",
            "comment": "总成交额"
        }, {
            "name": "l_sell",
            "type": "Float",
            "comment": "龙虎榜卖出额"
        }, {
            "name": "l_buy",
            "type": "Float",
            "comment": "龙虎榜买入额"
        }, {
            "name": "l_amount",
            "type": "Float",
            "comment": "龙虎榜成交额"
        }, {
            "name": "net_amount",
            "type": "Float",
            "comment": "龙虎榜净买入额"
        }, {
            "name": "net_rate",
            "type": "Float",
            "comment": "龙虎榜净买额占比"
        }, {
            "name": "amount_rate",
            "type": "Float",
            "comment": "龙虎榜成交额占比"
        }, {
            "name": "float_values",
            "type": "Float",
            "comment": "当日流通市值"
        }, {
            "name": "reason",
            "type": "String",
            "comment": "上榜理由"
        }]

    def top_list(self, fields='', **kwargs):
        """
        龙虎榜每日交易明细,数据开始于2005年，每日晚8点更新
        | Arguments:
        | trade_date(str): required  交易日期
        | ts_code(str):   股票代码
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  交易日期 Y
         ts_code(str)  TS代码 Y
         name(str)  名称 Y
         close(float)  收盘价 Y
         pct_change(float)  涨跌幅 Y
         turnover_rate(float)  换手率 Y
         amount(float)  总成交额 Y
         l_sell(float)  龙虎榜卖出额 Y
         l_buy(float)  龙虎榜买入额 Y
         l_amount(float)  龙虎榜成交额 Y
         net_amount(float)  龙虎榜净买入额 Y
         net_rate(float)  龙虎榜净买额占比 Y
         amount_rate(float)  龙虎榜成交额占比 Y
         float_values(float)  当日流通市值 Y
         reason(str)  上榜理由 Y
        
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
        init_args = {"trade_date": "", "ts_code": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.top_list with args: {}".format(kwargs))
                return self.tushare_query('top_list', fields=self.tushare_fields, **kwargs)
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


extends_attr(TopList, top_list_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.top_list())

    api = TopList(config)
    print(api.process())    # 同步增量数据
    print(api.top_list())    # 数据查询接口
