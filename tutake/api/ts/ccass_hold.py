"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare ccass_hold接口
获取中央结算系统持股汇总数据，覆盖全部历史数据，根据交易所披露时间，当日数据在下一交易日早上9点前完成入库
数据接口-沪深股票-特色数据-中央结算系统持股统计  https://tushare.pro/document/2?doc_id=295

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import ccass_hold_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareCcassHold(TutakeTableBase):
    __tablename__ = "tushare_ccass_hold"
    trade_date = Column(String, index=True, comment='交易日期')
    ts_code = Column(String, index=True, comment='股票代号')
    name = Column(String, comment='股票名称')
    shareholding = Column(String, comment='于中央结算系统的持股量(股)')
    hold_nums = Column(String, comment='参与者数目（个）')
    hold_ratio = Column(String, comment='占于上交所/深交所上市及交易的A股总数的百分比（%）')


class CcassHold(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_ccass_hold"
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
        TushareCcassHold.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareCcassHold)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'type', 'hk_hold', 'limit', 'offset']
        self.tushare_fields = ["trade_date", "ts_code", "name", "shareholding", "hold_nums", "hold_ratio"]
        entity_fields = ["trade_date", "ts_code", "name", "shareholding", "hold_nums", "hold_ratio"]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareCcassHold, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "ccass_hold", config)
        TuShareBase.__init__(self, "ccass_hold", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "trade_date",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "ts_code",
            "type": "String",
            "comment": "股票代号"
        }, {
            "name": "name",
            "type": "String",
            "comment": "股票名称"
        }, {
            "name": "shareholding",
            "type": "String",
            "comment": "于中央结算系统的持股量(股)"
        }, {
            "name": "hold_nums",
            "type": "String",
            "comment": "参与者数目（个）"
        }, {
            "name": "hold_ratio",
            "type": "String",
            "comment": "占于上交所/深交所上市及交易的A股总数的百分比（%）"
        }]

    def ccass_hold(self, fields='', **kwargs):
        """
        获取中央结算系统持股汇总数据，覆盖全部历史数据，根据交易所披露时间，当日数据在下一交易日早上9点前完成入库
        | Arguments:
        | ts_code(str):   股票代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | type(str):   类型
        | hk_hold(str):   港交所代码
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  交易日期 Y
         ts_code(str)  股票代号 Y
         name(str)  股票名称 Y
         shareholding(str)  于中央结算系统的持股量(股) Y
         hold_nums(str)  参与者数目（个） Y
         hold_ratio(str)  占于上交所/深交所上市及交易的A股总数的百分比（%） Y
        
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
            "type": "",
            "hk_hold": "",
            "limit": "",
            "offset": ""
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
                self.logger.debug("Invoke pro.ccass_hold with args: {}".format(kwargs))
                return self.tushare_query('ccass_hold', fields=self.tushare_fields, **kwargs)
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


extends_attr(CcassHold, ccass_hold_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.ccass_hold())

    api = CcassHold(config)
    print(api.process())    # 同步增量数据
    print(api.ccass_hold())    # 数据查询接口
