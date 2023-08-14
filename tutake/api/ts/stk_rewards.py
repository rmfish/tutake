"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare stk_rewards接口
获取上市公司管理层薪酬和持股
数据接口-沪深股票-基础数据-管理层薪酬和持股  https://tushare.pro/document/2?doc_id=194

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base
from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.stk_rewards_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


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


class StkRewards(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_shared_engine(config.get_data_sqlite_driver_url('tushare_stk_rewards.db'),
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareStkRewards.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'end_date', 'limit', 'offset']
        entity_fields = ["ts_code", "ann_date", "end_date", "name", "title", "reward", "hold_vol"]
        TushareDAO.__init__(self, self.engine, session_factory, TushareStkRewards, 'tushare_stk_rewards.db',
                            'tushare_stk_rewards', query_fields, entity_fields, config)
        DataProcess.__init__(self, "stk_rewards", config)
        TuShareBase.__init__(self, "stk_rewards", config, 5000)
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
            "name": "name",
            "type": "String",
            "comment": "姓名"
        }, {
            "name": "title",
            "type": "String",
            "comment": "职务"
        }, {
            "name": "reward",
            "type": "Float",
            "comment": "报酬"
        }, {
            "name": "hold_vol",
            "type": "Float",
            "comment": "持股数"
        }]

    def stk_rewards(self, fields='', **kwargs):
        """
        获取上市公司管理层薪酬和持股
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

    def process(self):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append)

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

        def fetch_save(offset_val=0):
            try:
                kwargs['offset'] = str(offset_val)
                self.logger.debug("Invoke pro.stk_rewards with args: {}".format(kwargs))
                res = self.tushare_query('stk_rewards', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_stk_rewards',
                           con=self.engine,
                           if_exists='append',
                           index=False,
                           index_label=['ts_code'])
                return res
            except Exception as err:
                raise ProcessException(kwargs, err)

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(StkRewards, 'default_limit', default_limit_ext)
setattr(StkRewards, 'default_cron_express', default_cron_express_ext)
setattr(StkRewards, 'default_order_by', default_order_by_ext)
setattr(StkRewards, 'prepare', prepare_ext)
setattr(StkRewards, 'query_parameters', query_parameters_ext)
setattr(StkRewards, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.stk_rewards(ts_code='601179.SH'))

    api = StkRewards(config)
    api.process()    # 同步增量数据
    print(api.stk_rewards(ts_code='601179.SH'))    # 数据查询接口
