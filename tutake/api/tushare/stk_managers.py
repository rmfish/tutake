"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare stk_managers接口
数据接口-沪深股票-基础数据-上市公司管理层  https://tushare.pro/document/2?doc_id=193

@author: rmfish
"""
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.stk_managers_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_basic_data.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()


class TushareStkManagers(Base):
    __tablename__ = "tushare_stk_managers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='TS股票代码')
    ann_date = Column(String, index=True, comment='公告日期')
    name = Column(String, comment='姓名')
    gender = Column(String, comment='性别')
    lev = Column(String, comment='岗位类别')
    title = Column(String, comment='岗位')
    edu = Column(String, comment='学历')
    national = Column(String, comment='国籍')
    birthday = Column(String, comment='出生年份')
    begin_date = Column(String, comment='上任日期')
    end_date = Column(String, index=True, comment='离任日期')
    resume = Column(String, comment='个人简历')


TushareStkManagers.__table__.create(bind=engine, checkfirst=True)


class StkManagers(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = ['ts_code', 'ann_date', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = [
            "ts_code", "ann_date", "name", "gender", "lev", "title", "edu", "national", "birthday", "begin_date",
            "end_date", "resume"
        ]
        BaseDao.__init__(self, engine, session_factory, TushareStkManagers, 'tushare_stk_managers', query_fields,
                         entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "stk_managers")
        self.dao = DAO()

    def stk_managers(self, fields='', **kwargs):
        """
        上市公司管理层
        | Arguments:
        | ts_code(str):   股票代码
        | ann_date(str):   公告日期
        | start_date(str):   公告开始日期
        | end_date(str):   公告结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS股票代码
         ann_date(str)  公告日期
         name(str)  姓名
         gender(str)  性别
         lev(str)  岗位类别
         title(str)  岗位
         edu(str)  学历
         national(str)  国籍
         birthday(str)  出生年份
         begin_date(str)  上任日期
         end_date(str)  离任日期
         resume(str)  个人简历
        
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
        init_args = {"ts_code": "", "ann_date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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
            self.logger.debug("Invoke pro.stk_managers with args: {}".format(kwargs))
            res = self.tushare_api().stk_managers(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_stk_managers', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(StkManagers, 'default_limit', default_limit_ext)
setattr(StkManagers, 'default_order_by', default_order_by_ext)
setattr(StkManagers, 'prepare', prepare_ext)
setattr(StkManagers, 'tushare_parameters', tushare_parameters_ext)
setattr(StkManagers, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    api = StkManagers()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    api.process(ProcessType.INCREASE)    # 同步增量数据
    print(api.stk_managers())    # 数据查询接口
