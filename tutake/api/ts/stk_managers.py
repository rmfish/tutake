"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare stk_managers接口
上市公司管理层
数据接口-沪深股票-基础数据-上市公司管理层  https://tushare.pro/document/2?doc_id=193

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.ts.stk_managers_ext import *
from tutake.api.ts.base_dao import BaseDao, Base
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


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


class StkManagers(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine("%s/%s" % (config.get_data_sqlite_driver_url(), 'tushare_stk_managers.db'),
                                    connect_args={'check_same_thread': False})
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareStkManagers.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['ts_code', 'ann_date', 'start_date', 'end_date', 'limit', 'offset']
        entity_fields = [
            "ts_code", "ann_date", "name", "gender", "lev", "title", "edu", "national", "birthday", "begin_date",
            "end_date", "resume"
        ]
        BaseDao.__init__(self, self.engine, session_factory, TushareStkManagers, 'tushare_stk_managers', query_fields,
                         entity_fields, config)
        DataProcess.__init__(self, "stk_managers", config)
        TuShareBase.__init__(self, "stk_managers", config, 5000)
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
            "name": "name",
            "type": "String",
            "comment": "姓名"
        }, {
            "name": "gender",
            "type": "String",
            "comment": "性别"
        }, {
            "name": "lev",
            "type": "String",
            "comment": "岗位类别"
        }, {
            "name": "title",
            "type": "String",
            "comment": "岗位"
        }, {
            "name": "edu",
            "type": "String",
            "comment": "学历"
        }, {
            "name": "national",
            "type": "String",
            "comment": "国籍"
        }, {
            "name": "birthday",
            "type": "String",
            "comment": "出生年份"
        }, {
            "name": "begin_date",
            "type": "String",
            "comment": "上任日期"
        }, {
            "name": "end_date",
            "type": "String",
            "comment": "离任日期"
        }, {
            "name": "resume",
            "type": "String",
            "comment": "个人简历"
        }]

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

        def fetch_save(offset_val=0):
            try:
                kwargs['offset'] = str(offset_val)
                self.logger.debug("Invoke pro.stk_managers with args: {}".format(kwargs))
                res = self.tushare_query('stk_managers', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_stk_managers',
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


setattr(StkManagers, 'default_limit', default_limit_ext)
setattr(StkManagers, 'default_cron_express', default_cron_express_ext)
setattr(StkManagers, 'default_order_by', default_order_by_ext)
setattr(StkManagers, 'prepare', prepare_ext)
setattr(StkManagers, 'tushare_parameters', tushare_parameters_ext)
setattr(StkManagers, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.stk_managers())

    api = StkManagers(config)
    api.process()    # 同步增量数据
    print(api.stk_managers())    # 数据查询接口
