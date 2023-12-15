"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fx_obasic接口
获取海外外汇基础信息，目前只有FXCM交易商的数据
数据接口-外汇-外汇基础信息（海外）  https://tushare.pro/document/2?doc_id=178

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import fx_obasic_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareFxObasic(TutakeTableBase):
    __tablename__ = "tushare_fx_obasic"
    ts_code = Column(String, index=True, comment='外汇代码')
    name = Column(String, comment='名称')
    classify = Column(String, index=True, comment='分类')
    exchange = Column(String, index=True, comment='FXCM/CFETS')
    min_unit = Column(Float, comment='最小交易单位')
    max_unit = Column(Float, comment='最大交易单位')
    pip = Column(Float, comment='最大交易单位')
    pip_cost = Column(Float, comment='点值')
    traget_spread = Column(Float, comment='目标差价')
    min_stop_distance = Column(Float, comment='最小止损距离（点子）')
    trading_hours = Column(String, comment='交易时间')
    break_time = Column(String, comment='休市时间')


class FxObasic(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_fx_obasic"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareFxObasic.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareFxObasic),
                                  config.get_tutake_data_dir())

        query_fields = ['exchange', 'classify', 'ts_code', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "name", "classify", "exchange", "min_unit", "max_unit", "pip", "pip_cost", "traget_spread",
            "min_stop_distance", "trading_hours", "break_time"
        ]
        entity_fields = [
            "ts_code", "name", "classify", "exchange", "min_unit", "max_unit", "pip", "pip_cost", "traget_spread",
            "min_stop_distance", "trading_hours", "break_time"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareFxObasic, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "fx_obasic", config)
        TuShareBase.__init__(self, "fx_obasic", config, 2000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "外汇代码"
        }, {
            "name": "name",
            "type": "String",
            "comment": "名称"
        }, {
            "name": "classify",
            "type": "String",
            "comment": "分类"
        }, {
            "name": "exchange",
            "type": "String",
            "comment": "FXCM/CFETS"
        }, {
            "name": "min_unit",
            "type": "Float",
            "comment": "最小交易单位"
        }, {
            "name": "max_unit",
            "type": "Float",
            "comment": "最大交易单位"
        }, {
            "name": "pip",
            "type": "Float",
            "comment": "最大交易单位"
        }, {
            "name": "pip_cost",
            "type": "Float",
            "comment": "点值"
        }, {
            "name": "traget_spread",
            "type": "Float",
            "comment": "目标差价"
        }, {
            "name": "min_stop_distance",
            "type": "Float",
            "comment": "最小止损距离（点子）"
        }, {
            "name": "trading_hours",
            "type": "String",
            "comment": "交易时间"
        }, {
            "name": "break_time",
            "type": "String",
            "comment": "休市时间"
        }]

    def fx_obasic(self, fields='', **kwargs):
        """
        获取海外外汇基础信息，目前只有FXCM交易商的数据
        | Arguments:
        | exchange(str):   交易商
        | classify(str):   分类
        | ts_code(str):   TS代码
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  外汇代码 Y
         name(str)  名称 Y
         classify(str)  分类 Y
         exchange(str)  FXCM/CFETS Y
         min_unit(float)  最小交易单位 Y
         max_unit(float)  最大交易单位 Y
         pip(float)  最大交易单位 Y
         pip_cost(float)  点值 Y
         traget_spread(float)  目标差价 Y
         min_stop_distance(float)  最小止损距离（点子） Y
         trading_hours(str)  交易时间 Y
         break_time(str)  休市时间 Y
        
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
        init_args = {"exchange": "", "classify": "", "ts_code": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.fx_obasic with args: {}".format(kwargs))
                return self.tushare_query('fx_obasic', fields=self.tushare_fields, **kwargs)
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


extends_attr(FxObasic, fx_obasic_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fx_obasic())

    api = FxObasic(config)
    print(api.process())    # 同步增量数据
    print(api.fx_obasic())    # 数据查询接口
