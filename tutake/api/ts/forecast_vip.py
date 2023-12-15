"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare forecast_vip接口
获取业绩预告数据
数据接口-沪深股票-财务数据-业绩预告  https://tushare.pro/document/2?doc_id=4500

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import forecast_vip_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareForecastVip(TutakeTableBase):
    __tablename__ = "tushare_forecast_vip"
    ts_code = Column(String, index=True, comment='TS股票代码')
    ann_date = Column(String, index=True, comment='公告日期')
    end_date = Column(String, index=True, comment='报告期')
    type = Column(String, index=True, comment='业绩预告类型')
    p_change_min = Column(Float, comment='预告净利润变动幅度下限（%）')
    p_change_max = Column(Float, comment='预告净利润变动幅度上限（%）')
    net_profit_min = Column(Float, comment='预告净利润下限（万元）')
    net_profit_max = Column(Float, comment='预告净利润上限（万元）')
    last_parent_net = Column(Float, comment='上年同期归属母公司净利润')
    notice_times = Column(Integer, comment='公布次数')
    first_ann_date = Column(String, comment='首次公告日')
    summary = Column(String, comment='业绩预告摘要')
    change_reason = Column(String, comment='业绩变动原因')


class ForecastVip(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_forecast_vip"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareForecastVip.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareForecastVip),
                                  config.get_tutake_data_dir())

        query_fields = ['ts_code', 'ann_date', 'start_date', 'end_date', 'period', 'type', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "ann_date", "end_date", "type", "p_change_min", "p_change_max", "net_profit_min",
            "net_profit_max", "last_parent_net", "notice_times", "first_ann_date", "summary", "change_reason"
        ]
        entity_fields = [
            "ts_code", "ann_date", "end_date", "type", "p_change_min", "p_change_max", "net_profit_min",
            "net_profit_max", "last_parent_net", "notice_times", "first_ann_date", "summary", "change_reason"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareForecastVip, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "forecast_vip", config)
        TuShareBase.__init__(self, "forecast_vip", config, 5000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS股票代码"
        }, {
            "name": "ann_date",
            "type": "String",
            "comment": "公告日期"
        }, {
            "name": "end_date",
            "type": "String",
            "comment": "报告期"
        }, {
            "name": "type",
            "type": "String",
            "comment": "业绩预告类型"
        }, {
            "name": "p_change_min",
            "type": "Float",
            "comment": "预告净利润变动幅度下限（%）"
        }, {
            "name": "p_change_max",
            "type": "Float",
            "comment": "预告净利润变动幅度上限（%）"
        }, {
            "name": "net_profit_min",
            "type": "Float",
            "comment": "预告净利润下限（万元）"
        }, {
            "name": "net_profit_max",
            "type": "Float",
            "comment": "预告净利润上限（万元）"
        }, {
            "name": "last_parent_net",
            "type": "Float",
            "comment": "上年同期归属母公司净利润"
        }, {
            "name": "notice_times",
            "type": "Integer",
            "comment": "公布次数"
        }, {
            "name": "first_ann_date",
            "type": "String",
            "comment": "首次公告日"
        }, {
            "name": "summary",
            "type": "String",
            "comment": "业绩预告摘要"
        }, {
            "name": "change_reason",
            "type": "String",
            "comment": "业绩变动原因"
        }]

    def forecast_vip(
            self,
            fields='ts_code,ann_date,end_date,type,p_change_min,p_change_max,net_profit_min,net_profit_max,last_parent_net,first_ann_date,summary,change_reason',
            **kwargs):
        """
        获取业绩预告数据
        | Arguments:
        | ts_code(str):   股票代码
        | ann_date(str):   公告日期
        | start_date(str):   公告开始日期
        | end_date(str):   公告结束日期
        | period(str):   报告期
        | type(str):   预告类型
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS股票代码 Y
         ann_date(str)  公告日期 Y
         end_date(str)  报告期 Y
         type(str)  业绩预告类型 Y
         p_change_min(float)  预告净利润变动幅度下限（%） Y
         p_change_max(float)  预告净利润变动幅度上限（%） Y
         net_profit_min(float)  预告净利润下限（万元） Y
         net_profit_max(float)  预告净利润上限（万元） Y
         last_parent_net(float)  上年同期归属母公司净利润 Y
         notice_times(int)  公布次数 N
         first_ann_date(str)  首次公告日 Y
         summary(str)  业绩预告摘要 Y
         change_reason(str)  业绩变动原因 Y
        
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
            "ann_date": "",
            "start_date": "",
            "end_date": "",
            "period": "",
            "type": "",
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
                self.logger.debug("Invoke pro.forecast_vip with args: {}".format(kwargs))
                return self.tushare_query('forecast_vip', fields=self.tushare_fields, **kwargs)
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


extends_attr(ForecastVip, forecast_vip_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.forecast_vip())

    api = ForecastVip(config)
    print(api.process())    # 同步增量数据
    print(api.forecast_vip())    # 数据查询接口
