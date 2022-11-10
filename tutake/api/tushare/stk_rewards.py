"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare stk_rewards接口
数据接口-沪深股票-基础数据-管理层薪酬和持股  https://tushare.pro/document/2?doc_id=194

@author: rmfish
"""
import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.stk_rewards_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_basic_data.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.stk_rewards')


class TushareStkRewards(Base):
    __tablename__ = "tushare_stk_rewards"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='TS股票代码')
    ann_date = Column(String, comment='公告日期')
    end_date = Column(String, index=True, comment='报告期')
    name = Column(String, comment='姓名')
    title = Column(String, comment='职务')
    reward = Column(Float, comment='报酬')
    hold_vol = Column(Float, comment='持股数')


TushareStkRewards.__table__.create(bind=engine, checkfirst=True)


class StkRewards(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = [
            'ts_code',
            'end_date',
            'limit',
            'offset',
        ]
        entity_fields = ["ts_code", "ann_date", "end_date", "name", "title", "reward", "hold_vol"]
        BaseDao.__init__(self, engine, session_factory, TushareStkRewards, 'tushare_stk_rewards', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "stk_rewards")
        self.dao = DAO()

    def stk_rewards(self, fields='', **kwargs):
        """
        管理层薪酬和持股
        | Arguments:
        | ts_code(str): required  TS股票代码
        | end_date(str):   报告期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS股票代码
         ann_date(str)  公告日期
         end_date(str)  报告期
         name(str)  姓名
         title(str)  职务
         reward(float)  报酬
         hold_vol(float)  持股数
        
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
        init_args = {"ts_code": "", "end_date": "", "limit": "", "offset": ""}
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
            logger.debug("Invoke pro.stk_rewards with args: {}".format(kwargs))
            res = self.tushare_api().stk_rewards(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_stk_rewards', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(StkRewards, 'default_limit', default_limit_ext)
setattr(StkRewards, 'default_order_by', default_order_by_ext)
setattr(StkRewards, 'prepare', prepare_ext)
setattr(StkRewards, 'tushare_parameters', tushare_parameters_ext)
setattr(StkRewards, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)    # 显示列数
    pd.set_option('display.width', 1000)
    logger.setLevel(logging.INFO)
    api = StkRewards()
    api.process(ProcessType.HISTORY)    # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.stk_rewards())    # 数据查询接口
