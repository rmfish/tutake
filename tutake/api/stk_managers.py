import pandas as pd
import logging
from sqlalchemy import Integer, String, Float, Column, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao
from tutake.api.dao import DAO
from tutake.api.process_type import ProcessType
from tutake.api.tushare_base import TuShareBase
from tutake.utils.config import config
"""
Tushare stk_managers接口
数据接口-沪深股票-基础数据-上市公司管理层  https://tushare.pro/document/2?doc_id=193
"""

engine = create_engine("%s/%s" % (config['database']['driver_url'], 'tushare_basic_data.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.stk_managers')


class TushareStkManagers(Base):
    __tablename__ = "tushare_stk_managers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, comment='TS股票代码')
    ann_date = Column(String, comment='公告日期')
    name = Column(String, comment='姓名')
    gender = Column(String, comment='性别')
    lev = Column(String, comment='岗位类别')
    title = Column(String, comment='岗位')
    edu = Column(String, comment='学历')
    national = Column(String, comment='国籍')
    birthday = Column(String, comment='出生年份')
    begin_date = Column(String, comment='上任日期')
    end_date = Column(String, comment='离任日期')
    resume = Column(String, comment='个人简历')


TushareStkManagers.__table__.create(bind=engine, checkfirst=True)


class StkManagers(BaseDao, TuShareBase):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        BaseDao.__init__(self, engine, session_factory, TushareStkManagers, 'tushare_stk_managers')
        TuShareBase.__init__(self)
        self.dao = DAO()

    def stk_managers(self, **kwargs):
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
        args = [
            n for n in [
                'ts_code',
                'ann_date',
                'start_date',
                'end_date',
                'limit',
                'offset',
            ] if n not in ['limit', 'offset']
        ]
        params = {key: kwargs[key] for key in kwargs.keys() & args}
        query = session_factory().query(TushareStkManagers).filter_by(**params)
        query = query.order_by(text("ts_code"))
        input_limit = 10000    # 默认10000条 避免导致数据库压力过大
        if kwargs.get('limit') and str(kwargs.get('limit')).isnumeric():
            input_limit = int(kwargs.get('limit'))
            query = query.limit(input_limit)
        if "" != "":
            default_limit = int("")
            if default_limit < input_limit:
                query = query.limit(default_limit)
        if kwargs.get('offset') and str(kwargs.get('offset')).isnumeric():
            query = query.offset(int(kwargs.get('offset')))
        return pd.read_sql(query.statement, query.session.bind)

    def prepare(self, process_type: ProcessType):
        """
        同步历史数据准备工作
        :return:
        """
        logger.warning("Delete all data of {}")
        self.delete_all()

    def tushare_parameters(self, process_type: ProcessType):
        """
        同步历史数据调用的参数
        :return: list(dict)
        """
        return [{}]

    def param_loop_process(self, process_type: ProcessType, **params):
        """
        每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
        """
        return params

    def process(self, process_type: ProcessType):
        """
        同步历史数据
        :return:
        """
        self.prepare(process_type)
        params = self.tushare_parameters(process_type)
        logger.debug("Process tushare params is {}".format(params))
        if params:
            for param in params:
                new_param = self.param_loop_process(process_type, **param)
                if new_param is None:
                    logger.debug("Skip exec param: {}".format(param))
                    continue
                try:
                    cnt = self.fetch_and_append(process_type, **new_param)
                    logger.debug("Fetch and append {} data, cnt is {}".format("daily", cnt))
                except Exception as err:
                    if err.args[0].startswith("抱歉，您没有访问该接口的权限") or err.args[0].startswith("抱歉，您每天最多访问该接口"):
                        logger.error("Throw exception with param: {} err:{}".format(new_param, err))
                        return
                    continue

    def fetch_and_append(self, process_type: ProcessType, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        if len(kwargs.keys()) == 0:
            kwargs = {"ts_code": "", "ann_date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
        # 初始化offset和limit
        if not kwargs.get("limit"):
            kwargs['limit'] = ""
        init_offset = 0
        offset = 0
        if kwargs.get('offset') and kwargs.get('offset').isnumeric():
            offset = int(kwargs['offset'])
            init_offset = offset

        kwargs = {
            key: kwargs[key] for key in kwargs.keys() & list([
                'ts_code',
                'ann_date',
                'start_date',
                'end_date',
                'limit',
                'offset',
            ])
        }

        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            logger.debug("Invoke pro.stk_managers with args: {}".format(kwargs))
            fields = [
                "ts_code", "ann_date", "name", "gender", "lev", "title", "edu", "national", "birthday", "begin_date",
                "end_date", "resume"
            ]
            res = pro.stk_managers(**kwargs, fields=fields)
            res.to_sql('tushare_stk_managers', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        pro = self.tushare_api()
        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and df.shape[0] == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    api = StkManagers()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.stk_managers())    # 数据查询接口
