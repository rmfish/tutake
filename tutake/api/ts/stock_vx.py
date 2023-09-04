"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare stock_vx接口
小沛估值因子
数据接口  https://tushare.pro/document/2?doc_id=303

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.stock_vx_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareStockVx(Base):
    __tablename__ = "tushare_stock_vx"
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String, index=True, comment='交易日期')
    ts_code = Column(String, index=True, comment='股票代码')
    level1 = Column(String, comment='4评级：1(便宜)、2(合理)、3(贵)、4(很贵)')
    level2 = Column(String, comment='8评级：1,2(便宜)、3,4(合理)、5,6(贵)、7,8(很贵)')
    vx_life_v_l4 = Column(String, comment='估值长优4条线，根据level1的评级，公司上市后每一天的估值评级平均')
    vx_3excellent_v_l4 = Column(String,
                                comment='估值3优4条线，根据level1的评级，最新季度的估值评级、近5季度的估值评级平均、上市后的估值评级平均，短中长的估值评级再取一次平均形成三优指标')
    vx_past_5q_avg_l4 = Column(String, comment='估值4条线近5季平均，根据level1的评级，最近五季度估值评级平均')
    vx_grow_worse_v_l4 = Column(String, comment='估值进退步-估值4条线,根据level1的评级，最新的估值评级与最近5Q平均的比')
    vx_life_v_l8 = Column(String, comment='估值长优8条线,根据level2的评级，公司上市后每一季度的估值评级平均')
    vx_3excellent_v_l8 = Column(String,
                                comment='估值3优8条线,根据level2的评级，最新季度的估值评级、近5季度的估值评级平均、上市后的估值评级平均，短中长的估值评级再取一次平均形成三优指标')
    vx_past_5q_avg_l8 = Column(String, comment='估值8条线近5季平均,根据level2的评级，最近五季度估值评级平均')
    vx_grow_worse_v_l8 = Column(String, comment='估值进退步-估值8条线,根据level2的评级，最新的估值评级与最近5Q平均的比较')
    vxx = Column(String, comment='个股最新估值与亚洲同类股票相较后的标准差，按因子排序，数值越大代表估值越贵')
    vs = Column(String, comment='个股最新估值与亚洲同类股票自己相较后的标准差，按因子排序，数值越大代表估值越贵')
    vz11 = Column(String, comment='个股最新估值与亚洲同类股票主行业相较后的标准差，按因子排序，数值越大代表估值越贵')
    vz24 = Column(String, comment='个股最新估值与亚洲同类股票次行业相较后的标准差，按因子排序，数值越大代表估值越贵')
    vz_lms = Column(String, comment='个股最新估值与亚洲同类股票市值分类相较后的标准差，按因子排序，数值越大代表估值越贵')


class StockVx(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_stock_vx"
        self.database = 'tushare_xiaopei.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareStockVx.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'offset', 'limit']
        entity_fields = [
            "trade_date", "ts_code", "level1", "level2", "vx_life_v_l4", "vx_3excellent_v_l4", "vx_past_5q_avg_l4",
            "vx_grow_worse_v_l4", "vx_life_v_l8", "vx_3excellent_v_l8", "vx_past_5q_avg_l8", "vx_grow_worse_v_l8",
            "vxx", "vs", "vz11", "vz24", "vz_lms"
        ]
        TushareDAO.__init__(self, self.engine, session_factory, TushareStockVx, self.database, self.table_name,
                            query_fields, entity_fields, config)
        DataProcess.__init__(self, "stock_vx", config)
        TuShareBase.__init__(self, "stock_vx", config, 5000)
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
            "name": "level1",
            "type": "String",
            "comment": "4评级：1(便宜)、2(合理)、3(贵)、4(很贵)"
        }, {
            "name": "level2",
            "type": "String",
            "comment": "8评级：1,2(便宜)、3,4(合理)、5,6(贵)、7,8(很贵)"
        }, {
            "name": "vx_life_v_l4",
            "type": "String",
            "comment": "估值长优4条线，根据level1的评级，公司上市后每一天的估值评级平均"
        }, {
            "name": "vx_3excellent_v_l4",
            "type": "String",
            "comment": "估值3优4条线，根据level1的评级，最新季度的估值评级、近5季度的估值评级平均、上市后的估值评级平均，短中长的估值评级再取一次平均形成三优指标"
        }, {
            "name": "vx_past_5q_avg_l4",
            "type": "String",
            "comment": "估值4条线近5季平均，根据level1的评级，最近五季度估值评级平均"
        }, {
            "name": "vx_grow_worse_v_l4",
            "type": "String",
            "comment": "估值进退步-估值4条线,根据level1的评级，最新的估值评级与最近5Q平均的比"
        }, {
            "name": "vx_life_v_l8",
            "type": "String",
            "comment": "估值长优8条线,根据level2的评级，公司上市后每一季度的估值评级平均"
        }, {
            "name": "vx_3excellent_v_l8",
            "type": "String",
            "comment": "估值3优8条线,根据level2的评级，最新季度的估值评级、近5季度的估值评级平均、上市后的估值评级平均，短中长的估值评级再取一次平均形成三优指标"
        }, {
            "name": "vx_past_5q_avg_l8",
            "type": "String",
            "comment": "估值8条线近5季平均,根据level2的评级，最近五季度估值评级平均"
        }, {
            "name": "vx_grow_worse_v_l8",
            "type": "String",
            "comment": "估值进退步-估值8条线,根据level2的评级，最新的估值评级与最近5Q平均的比较"
        }, {
            "name": "vxx",
            "type": "String",
            "comment": "个股最新估值与亚洲同类股票相较后的标准差，按因子排序，数值越大代表估值越贵"
        }, {
            "name": "vs",
            "type": "String",
            "comment": "个股最新估值与亚洲同类股票自己相较后的标准差，按因子排序，数值越大代表估值越贵"
        }, {
            "name": "vz11",
            "type": "String",
            "comment": "个股最新估值与亚洲同类股票主行业相较后的标准差，按因子排序，数值越大代表估值越贵"
        }, {
            "name": "vz24",
            "type": "String",
            "comment": "个股最新估值与亚洲同类股票次行业相较后的标准差，按因子排序，数值越大代表估值越贵"
        }, {
            "name": "vz_lms",
            "type": "String",
            "comment": "个股最新估值与亚洲同类股票市值分类相较后的标准差，按因子排序，数值越大代表估值越贵"
        }]

    def stock_vx(self, fields='', **kwargs):
        """
        小沛估值因子
        | Arguments:
        | ts_code(str):   股票代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | offset(str):   开始行数
        | limit(str):   最大行数
        
        :return: DataFrame
         trade_date(str)  交易日期 Y
         ts_code(str)  股票代码 Y
         level1(str)  4评级：1(便宜)、2(合理)、3(贵)、4(很贵) Y
         level2(str)  8评级：1,2(便宜)、3,4(合理)、5,6(贵)、7,8(很贵) Y
         vx_life_v_l4(str)  估值长优4条线，根据level1的评级，公司上市后每一天的估值评级平均 Y
         vx_3excellent_v_l4(str)  估值3优4条线，根据level1的评级，最新季度的估值评级、近5季度的估值评级平均、上市后的估值评级平均，短中长的估值评级再取一次平均形成三优指标 Y
         vx_past_5q_avg_l4(str)  估值4条线近5季平均，根据level1的评级，最近五季度估值评级平均 Y
         vx_grow_worse_v_l4(str)  估值进退步-估值4条线,根据level1的评级，最新的估值评级与最近5Q平均的比 Y
         vx_life_v_l8(str)  估值长优8条线,根据level2的评级，公司上市后每一季度的估值评级平均 Y
         vx_3excellent_v_l8(str)  估值3优8条线,根据level2的评级，最新季度的估值评级、近5季度的估值评级平均、上市后的估值评级平均，短中长的估值评级再取一次平均形成三优指标 Y
         vx_past_5q_avg_l8(str)  估值8条线近5季平均,根据level2的评级，最近五季度估值评级平均 Y
         vx_grow_worse_v_l8(str)  估值进退步-估值8条线,根据level2的评级，最新的估值评级与最近5Q平均的比较 Y
         vxx(str)  个股最新估值与亚洲同类股票相较后的标准差，按因子排序，数值越大代表估值越贵 Y
         vs(str)  个股最新估值与亚洲同类股票自己相较后的标准差，按因子排序，数值越大代表估值越贵 Y
         vz11(str)  个股最新估值与亚洲同类股票主行业相较后的标准差，按因子排序，数值越大代表估值越贵 Y
         vz24(str)  个股最新估值与亚洲同类股票次行业相较后的标准差，按因子排序，数值越大代表估值越贵 Y
         vz_lms(str)  个股最新估值与亚洲同类股票市值分类相较后的标准差，按因子排序，数值越大代表估值越贵 Y
        
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append, BatchWriter(self.engine, self.table_name), **kwargs)

    def fetch_and_append(self, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        init_args = {"ts_code": "", "trade_date": "", "start_date": "", "end_date": "", "offset": "", "limit": ""}
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
                self.logger.debug("Invoke pro.stock_vx with args: {}".format(kwargs))
                return self.tushare_query('stock_vx', fields=self.entity_fields, **kwargs)
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
        return res


setattr(StockVx, 'default_limit', default_limit_ext)
setattr(StockVx, 'default_cron_express', default_cron_express_ext)
setattr(StockVx, 'default_order_by', default_order_by_ext)
setattr(StockVx, 'prepare', prepare_ext)
setattr(StockVx, 'query_parameters', query_parameters_ext)
setattr(StockVx, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.stock_vx())

    api = StockVx(config)
    print(api.process())    # 同步增量数据
    print(api.stock_vx())    # 数据查询接口
