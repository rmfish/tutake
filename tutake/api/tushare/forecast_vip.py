"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare forecast_vip接口
数据接口-沪深股票-财务数据-业绩预告  https://tushare.pro/document/2?doc_id=4500

@author: rmfish
"""
import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.forecast_vip_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_forecast_vip.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.forecast_vip')


class TushareForecastVip(Base):
    __tablename__ = "tushare_forecast_vip"
    id = Column(Integer, primary_key=True, autoincrement=True)
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


TushareForecastVip.__table__.create(bind=engine, checkfirst=True)


class ForecastVip(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = ['ts_code', 'ann_date', 'start_date', 'end_date', 'period', 'type', 'limit', 'offset']
        entity_fields = [
            "ts_code", "ann_date", "end_date", "type", "p_change_min", "p_change_max", "net_profit_min",
            "net_profit_max", "last_parent_net", "notice_times", "first_ann_date", "summary", "change_reason"
        ]
        BaseDao.__init__(self, engine, session_factory, TushareForecastVip, 'tushare_forecast_vip', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "forecast_vip")
        self.dao = DAO()

    def forecast_vip(self, fields='', **kwargs):
        """
        
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
         ts_code(str)  TS股票代码
         ann_date(str)  公告日期
         end_date(str)  报告期
         type(str)  业绩预告类型
         p_change_min(float)  预告净利润变动幅度下限（%）
         p_change_max(float)  预告净利润变动幅度上限（%）
         net_profit_min(float)  预告净利润下限（万元）
         net_profit_max(float)  预告净利润上限（万元）
         last_parent_net(float)  上年同期归属母公司净利润
         notice_times(int)  公布次数
         first_ann_date(str)  首次公告日
         summary(str)  业绩预告摘要
         change_reason(str)  业绩变动原因
        
        """
        return super().query(fields, **kwargs)

    def process(self, process_type: ProcessType):
        """
        同步历史数据
        :return:
        """
        return super()._process(process_type, self.fetch_and_append)

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

        @sleep(timeout=61, time_append=60, retry=20, match="^抱歉，您每分钟最多访问该接口")
        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            logger.debug("Invoke pro.forecast_vip with args: {}".format(kwargs))
            res = self.tushare_api().forecast_vip(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_forecast_vip', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(ForecastVip, 'default_limit', default_limit_ext)
setattr(ForecastVip, 'default_order_by', default_order_by_ext)
setattr(ForecastVip, 'prepare', prepare_ext)
setattr(ForecastVip, 'tushare_parameters', tushare_parameters_ext)
setattr(ForecastVip, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)    # 显示列数
    pd.set_option('display.width', 1000)
    logger.setLevel(logging.INFO)
    api = ForecastVip()
    api.process(ProcessType.HISTORY)    # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.forecast_vip())    # 数据查询接口
