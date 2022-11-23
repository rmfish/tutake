"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fund_manager接口
获取公募基金经理数据，包括基金经理简历等数据
数据接口-公募基金-基金经理  https://tushare.pro/document/2?doc_id=208

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.tushare.fund_manager_ext import *
from tutake.api.tushare.base_dao import BaseDao, Base
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareFundManager(Base):
    __tablename__ = "tushare_fund_manager"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='基金代码')
    ann_date = Column(String, index=True, comment='公告日期')
    name = Column(String, index=True, comment='基金经理姓名')
    gender = Column(String, comment='性别')
    birth_year = Column(String, comment='出生年份')
    edu = Column(String, comment='学历')
    nationality = Column(String, comment='国籍')
    begin_date = Column(String, comment='任职日期')
    end_date = Column(String, comment='历任日期')
    resume = Column(String, comment='简历')


class FundManager(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine("%s/%s" % (config.get_data_sqlite_driver_url(), 'tushare_fund_manager.db'),
                                    connect_args={'check_same_thread': False})
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareFundManager.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'ann_date', 'name', 'offset', 'limit']
        entity_fields = [
            "ts_code", "ann_date", "name", "gender", "birth_year", "edu", "nationality", "begin_date", "end_date",
            "resume"
        ]
        BaseDao.__init__(self, self.engine, session_factory, TushareFundManager, 'tushare_fund_manager', query_fields,
                         entity_fields)
        DataProcess.__init__(self, "fund_manager", config)
        TuShareBase.__init__(self, "fund_manager", config, 5000)
        self.dao = DAO()

    def fund_manager(self, fields='', **kwargs):
        """
        获取公募基金经理数据，包括基金经理简历等数据
        | Arguments:
        | ts_code(str):   基金代码
        | ann_date(str):   公告日期
        | name(str):   基金经理姓名
        | offset(int):   开始行数
        | limit(int):   每页行数
        
        :return: DataFrame
         ts_code(str)  基金代码
         ann_date(str)  公告日期
         name(str)  基金经理姓名
         gender(str)  性别
         birth_year(str)  出生年份
         edu(str)  学历
         nationality(str)  国籍
         begin_date(str)  任职日期
         end_date(str)  历任日期
         resume(str)  简历
        
        """
        return super().query(fields, **kwargs)

    def process(self, process_type: ProcessType = ProcessType.INCREASE):
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
        init_args = {"ts_code": "", "ann_date": "", "name": "", "offset": "", "limit": ""}
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
                self.logger.debug("Invoke pro.fund_manager with args: {}".format(kwargs))
                res = self.tushare_query('fund_manager', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_fund_manager',
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


setattr(FundManager, 'default_limit', default_limit_ext)
setattr(FundManager, 'default_cron_express', default_cron_express_ext)
setattr(FundManager, 'default_order_by', default_order_by_ext)
setattr(FundManager, 'prepare', prepare_ext)
setattr(FundManager, 'tushare_parameters', tushare_parameters_ext)
setattr(FundManager, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fund_manager())

    api = FundManager(config)
    api.process()    # 同步增量数据
    print(api.fund_manager())    # 数据查询接口
