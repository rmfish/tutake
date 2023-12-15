"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare ccass_hold_detail接口
获取中央结算系统机构席位持股明细，数据覆盖全历史，根据交易所披露时间，当日数据在下一交易日早上9点前完成
数据接口-沪深股票-特色数据-中央结算系统持股明细  https://tushare.pro/document/2?doc_id=274

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import ccass_hold_detail_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareCcassHoldDetail(TutakeTableBase):
    __tablename__ = "tushare_ccass_hold_detail"
    trade_date = Column(String, index=True, comment='交易日期')
    ts_code = Column(String, index=True, comment='股票代号')
    name = Column(String, comment='股票名称')
    col_participant_id = Column(String, comment='参与者编号')
    col_participant_name = Column(String, comment='机构名称')
    col_shareholding = Column(String, comment='持股量(股)')
    col_shareholding_percent = Column(String, comment='占已发行股份/权证/单位百分比(%)')


class CcassHoldDetail(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_ccass_hold_detail"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareCcassHoldDetail.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareCcassHoldDetail),
                                  config.get_tutake_data_dir())

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'hk_code', 'limit', 'offset']
        self.tushare_fields = [
            "trade_date", "ts_code", "name", "col_participant_id", "col_participant_name", "col_shareholding",
            "col_shareholding_percent"
        ]
        entity_fields = [
            "trade_date", "ts_code", "name", "col_participant_id", "col_participant_name", "col_shareholding",
            "col_shareholding_percent"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareCcassHoldDetail, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "ccass_hold_detail", config)
        TuShareBase.__init__(self, "ccass_hold_detail", config, 5000)
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
            "name": "col_participant_id",
            "type": "String",
            "comment": "参与者编号"
        }, {
            "name": "col_participant_name",
            "type": "String",
            "comment": "机构名称"
        }, {
            "name": "col_shareholding",
            "type": "String",
            "comment": "持股量(股)"
        }, {
            "name": "col_shareholding_percent",
            "type": "String",
            "comment": "占已发行股份/权证/单位百分比(%)"
        }]

    def ccass_hold_detail(self, fields='', **kwargs):
        """
        获取中央结算系统机构席位持股明细，数据覆盖全历史，根据交易所披露时间，当日数据在下一交易日早上9点前完成
        | Arguments:
        | ts_code(str):   股票代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | hk_code(str):   港交所股份代码
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         trade_date(str)  交易日期 Y
         ts_code(str)  股票代号 Y
         name(str)  股票名称 Y
         col_participant_id(str)  参与者编号 Y
         col_participant_name(str)  机构名称 Y
         col_shareholding(str)  持股量(股) Y
         col_shareholding_percent(str)  占已发行股份/权证/单位百分比(%) Y
        
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
            "ts_code": "",
            "trade_date": "",
            "start_date": "",
            "end_date": "",
            "hk_code": "",
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
                self.logger.debug("Invoke pro.ccass_hold_detail with args: {}".format(kwargs))
                return self.tushare_query('ccass_hold_detail', fields=self.tushare_fields, **kwargs)
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


extends_attr(CcassHoldDetail, ccass_hold_detail_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.ccass_hold_detail())

    api = CcassHoldDetail(config)
    print(api.process())    # 同步增量数据
    print(api.ccass_hold_detail())    # 数据查询接口
