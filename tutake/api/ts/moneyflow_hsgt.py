"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare moneyflow_hsgt接口
获取沪股通、深股通、港股通每日资金流向数据
数据接口-沪深股票-行情数据-沪深港通资金流向  https://tushare.pro/document/2?doc_id=47

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import moneyflow_hsgt_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareMoneyflowHsgt(TutakeTableBase):
    __tablename__ = "tushare_moneyflow_hsgt"
    trade_date = Column(String, index=True, comment='交易日期')
    ggt_ss = Column(Float, comment='港股通（上海）')
    ggt_sz = Column(Float, comment='港股通（深圳）')
    hgt = Column(Float, comment='沪股通')
    sgt = Column(Float, comment='深股通')
    north_money = Column(Float, comment='北向资金')
    south_money = Column(Float, comment='南向资金')


class MoneyflowHsgt(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_moneyflow_hsgt"
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
        TushareMoneyflowHsgt.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareMoneyflowHsgt)

        query_fields = ['trade_date', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = ["trade_date", "ggt_ss", "ggt_sz", "hgt", "sgt", "north_money", "south_money"]
        entity_fields = ["trade_date", "ggt_ss", "ggt_sz", "hgt", "sgt", "north_money", "south_money"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareMoneyflowHsgt, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "moneyflow_hsgt", config)
        TuShareBase.__init__(self, "moneyflow_hsgt", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "ggt_ss",
            "type": "Float",
            "comment": "港股通（上海）"
        }, {
            "name": "ggt_sz",
            "type": "Float",
            "comment": "港股通（深圳）"
        }, {
            "name": "hgt",
            "type": "Float",
            "comment": "沪股通"
        }, {
            "name": "sgt",
            "type": "Float",
            "comment": "深股通"
        }, {
            "name": "north_money",
            "type": "Float",
            "comment": "北向资金"
        }, {
            "name": "south_money",
            "type": "Float",
            "comment": "南向资金"
        }]

    def moneyflow_hsgt(self, fields='', **kwargs):
        """
        获取沪股通、深股通、港股通每日资金流向数据
        | Arguments:
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  交易日期 Y
         ggt_ss(float)  港股通（上海） Y
         ggt_sz(float)  港股通（深圳） Y
         hgt(float)  沪股通 Y
         sgt(float)  深股通 Y
         north_money(float)  北向资金 Y
         south_money(float)  南向资金 Y
        
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
        init_args = {"trade_date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.moneyflow_hsgt with args: {}".format(kwargs))
                return self.tushare_query('moneyflow_hsgt', fields=self.tushare_fields, **kwargs)
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


extends_attr(MoneyflowHsgt, moneyflow_hsgt_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.moneyflow_hsgt(trade_date='20221118'))

    api = MoneyflowHsgt(config)
    print(api.process())    # 同步增量数据
    print(api.moneyflow_hsgt(trade_date='20221118'))    # 数据查询接口
