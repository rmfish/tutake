"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare ggt_top10接口
获取港股通每日成交数据，其中包括沪市、深市详细数据，每天18~20点之间完成当日更新
数据接口-沪深股票-行情数据-港股通十大成交股  https://tushare.pro/document/2?doc_id=49

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import ggt_top10_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareGgtTop10(TutakeTableBase):
    __tablename__ = "tushare_ggt_top10"
    trade_date = Column(String, index=True, comment='交易日期')
    ts_code = Column(String, index=True, comment='股票代码')
    name = Column(String, comment='股票名称')
    close = Column(Float, comment='收盘价')
    p_change = Column(Float, comment='涨跌幅')
    rank = Column(Integer, comment='资金排名')
    market_type = Column(Integer, index=True, comment='市场类型 2：港股通（沪） 4：港股通（深）')
    amount = Column(Float, comment='累计成交金额')
    net_amount = Column(Float, comment='净买入金额')
    sh_amount = Column(Float, comment='沪市成交金额')
    sh_net_amount = Column(Float, comment='沪市净买入金额')
    sh_buy = Column(Float, comment='沪市买入金额')
    sh_sell = Column(Float, comment='沪市卖出金额')
    sz_amount = Column(Float, comment='深市成交金额')
    sz_net_amount = Column(Float, comment='深市净买入金额')
    sz_buy = Column(Float, comment='深市买入金额')
    sz_sell = Column(Float, comment='深市卖出金额')


class GgtTop10(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_ggt_top10"
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
        TushareGgtTop10.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareGgtTop10)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'market_type', 'limit', 'offset']
        self.tushare_fields = [
            "trade_date", "ts_code", "name", "close", "p_change", "rank", "market_type", "amount", "net_amount",
            "sh_amount", "sh_net_amount", "sh_buy", "sh_sell", "sz_amount", "sz_net_amount", "sz_buy", "sz_sell"
        ]
        entity_fields = [
            "trade_date", "ts_code", "name", "close", "p_change", "rank", "market_type", "amount", "net_amount",
            "sh_amount", "sh_net_amount", "sh_buy", "sh_sell", "sz_amount", "sz_net_amount", "sz_buy", "sz_sell"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareGgtTop10, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "ggt_top10", config)
        TuShareBase.__init__(self, "ggt_top10", config, 5000)
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
            "name": "name",
            "type": "String",
            "comment": "股票名称"
        }, {
            "name": "close",
            "type": "Float",
            "comment": "收盘价"
        }, {
            "name": "p_change",
            "type": "Float",
            "comment": "涨跌幅"
        }, {
            "name": "rank",
            "type": "Integer",
            "comment": "资金排名"
        }, {
            "name": "market_type",
            "type": "Integer",
            "comment": "市场类型 2：港股通（沪） 4：港股通（深）"
        }, {
            "name": "amount",
            "type": "Float",
            "comment": "累计成交金额"
        }, {
            "name": "net_amount",
            "type": "Float",
            "comment": "净买入金额"
        }, {
            "name": "sh_amount",
            "type": "Float",
            "comment": "沪市成交金额"
        }, {
            "name": "sh_net_amount",
            "type": "Float",
            "comment": "沪市净买入金额"
        }, {
            "name": "sh_buy",
            "type": "Float",
            "comment": "沪市买入金额"
        }, {
            "name": "sh_sell",
            "type": "Float",
            "comment": "沪市卖出金额"
        }, {
            "name": "sz_amount",
            "type": "Float",
            "comment": "深市成交金额"
        }, {
            "name": "sz_net_amount",
            "type": "Float",
            "comment": "深市净买入金额"
        }, {
            "name": "sz_buy",
            "type": "Float",
            "comment": "深市买入金额"
        }, {
            "name": "sz_sell",
            "type": "Float",
            "comment": "深市卖出金额"
        }]

    def ggt_top10(self, fields='', **kwargs):
        """
        获取港股通每日成交数据，其中包括沪市、深市详细数据，每天18~20点之间完成当日更新
        | Arguments:
        | ts_code(str):   股票代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | market_type(str):   市场类型 2：港股通（沪） 4：港股通（深）
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  交易日期 Y
         ts_code(str)  股票代码 Y
         name(str)  股票名称 Y
         close(float)  收盘价 Y
         p_change(float)  涨跌幅 Y
         rank(int)  资金排名 Y
         market_type(int)  市场类型 2：港股通（沪） 4：港股通（深） Y
         amount(float)  累计成交金额 Y
         net_amount(float)  净买入金额 Y
         sh_amount(float)  沪市成交金额 Y
         sh_net_amount(float)  沪市净买入金额 Y
         sh_buy(float)  沪市买入金额 Y
         sh_sell(float)  沪市卖出金额 Y
         sz_amount(float)  深市成交金额 Y
         sz_net_amount(float)  深市净买入金额 Y
         sz_buy(float)  深市买入金额 Y
         sz_sell(float)  深市卖出金额 Y
        
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
        init_args = {
            "ts_code": "",
            "trade_date": "",
            "start_date": "",
            "end_date": "",
            "market_type": "",
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
                self.logger.debug("Invoke pro.ggt_top10 with args: {}".format(kwargs))
                return self.tushare_query('ggt_top10', fields=self.tushare_fields, **kwargs)
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


extends_attr(GgtTop10, ggt_top10_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.ggt_top10(ts_code='00700.HK'))

    api = GgtTop10(config)
    print(api.process())    # 同步增量数据
    print(api.ggt_top10(ts_code='00700.HK'))    # 数据查询接口
