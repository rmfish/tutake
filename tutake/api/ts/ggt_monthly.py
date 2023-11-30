"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare ggt_monthly接口
港股通每月成交信息，数据从2014年开始
数据接口-沪深股票-行情数据-港股通每月成交统计  https://tushare.pro/document/2?doc_id=197

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import ggt_monthly_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareGgtMonthly(TutakeTableBase):
    __tablename__ = "tushare_ggt_monthly"
    month = Column(String, index=True, comment='交易日期')
    day_buy_amt = Column(Float, comment='当月日均买入成交金额（亿元）')
    day_buy_vol = Column(Float, comment='当月日均买入成交笔数（万笔）')
    day_sell_amt = Column(Float, comment='当月日均卖出成交金额（亿元）')
    day_sell_vol = Column(Float, comment='当月日均卖出成交笔数（万笔）')
    total_buy_amt = Column(Float, comment='总买入成交金额（亿元）')
    total_buy_vol = Column(Float, comment='总买入成交笔数（万笔）')
    total_sell_amt = Column(Float, comment='总卖出成交金额（亿元）')
    total_sell_vol = Column(Float, comment='总卖出成交笔数（万笔）')


class GgtMonthly(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_ggt_monthly"
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
        TushareGgtMonthly.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareGgtMonthly)

        query_fields = ['month', 'start_month', 'end_month', 'limit', 'offset']
        self.tushare_fields = [
            "month", "day_buy_amt", "day_buy_vol", "day_sell_amt", "day_sell_vol", "total_buy_amt", "total_buy_vol",
            "total_sell_amt", "total_sell_vol"
        ]
        entity_fields = [
            "month", "day_buy_amt", "day_buy_vol", "day_sell_amt", "day_sell_vol", "total_buy_amt", "total_buy_vol",
            "total_sell_amt", "total_sell_vol"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareGgtMonthly, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "ggt_monthly", config)
        TuShareBase.__init__(self, "ggt_monthly", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "month",
            "type": "String",
            "comment": "交易日期"
        }, {
            "name": "day_buy_amt",
            "type": "Float",
            "comment": "当月日均买入成交金额（亿元）"
        }, {
            "name": "day_buy_vol",
            "type": "Float",
            "comment": "当月日均买入成交笔数（万笔）"
        }, {
            "name": "day_sell_amt",
            "type": "Float",
            "comment": "当月日均卖出成交金额（亿元）"
        }, {
            "name": "day_sell_vol",
            "type": "Float",
            "comment": "当月日均卖出成交笔数（万笔）"
        }, {
            "name": "total_buy_amt",
            "type": "Float",
            "comment": "总买入成交金额（亿元）"
        }, {
            "name": "total_buy_vol",
            "type": "Float",
            "comment": "总买入成交笔数（万笔）"
        }, {
            "name": "total_sell_amt",
            "type": "Float",
            "comment": "总卖出成交金额（亿元）"
        }, {
            "name": "total_sell_vol",
            "type": "Float",
            "comment": "总卖出成交笔数（万笔）"
        }]

    def ggt_monthly(self, fields='', **kwargs):
        """
        港股通每月成交信息，数据从2014年开始
        | Arguments:
        | month(str):   月度
        | start_month(str):   开始月度
        | end_month(str):   结束月度
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         month(str)  交易日期 Y
         day_buy_amt(float)  当月日均买入成交金额（亿元） Y
         day_buy_vol(float)  当月日均买入成交笔数（万笔） Y
         day_sell_amt(float)  当月日均卖出成交金额（亿元） Y
         day_sell_vol(float)  当月日均卖出成交笔数（万笔） Y
         total_buy_amt(float)  总买入成交金额（亿元） Y
         total_buy_vol(float)  总买入成交笔数（万笔） Y
         total_sell_amt(float)  总卖出成交金额（亿元） Y
         total_sell_vol(float)  总卖出成交笔数（万笔） Y
        
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
        init_args = {"month": "", "start_month": "", "end_month": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.ggt_monthly with args: {}".format(kwargs))
                return self.tushare_query('ggt_monthly', fields=self.tushare_fields, **kwargs)
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


extends_attr(GgtMonthly, ggt_monthly_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.ggt_monthly())

    api = GgtMonthly(config)
    print(api.process())    # 同步增量数据
    print(api.ggt_monthly())    # 数据查询接口
