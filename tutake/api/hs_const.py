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
from tutake.utils.decorator import sleep
"""
Tushare hs_const接口
数据接口-沪深股票-基础数据-沪深股通成分股  https://tushare.pro/document/2?doc_id=104
"""

engine = create_engine("%s/%s" % (config['database']['driver_url'], 'tushare_basic_data.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.hs_const')


class TushareHsConst(Base):
    __tablename__ = "tushare_hs_const"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, comment='TS代码')
    hs_type = Column(String, comment='沪深港通类型SH沪SZ深')
    in_date = Column(String, comment='纳入日期')
    out_date = Column(String, comment='剔除日期')
    is_new = Column(String, comment='是否最新')


TushareHsConst.__table__.create(bind=engine, checkfirst=True)


class HsConst(BaseDao, TuShareBase):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        BaseDao.__init__(self, engine, session_factory, TushareHsConst, 'tushare_hs_const')
        TuShareBase.__init__(self)
        self.dao = DAO()

    def hs_const(self, **kwargs):
        """
        

        | Arguments:
        | hs_type(str): required  类型SH沪股通SZ深股通
        | is_new(str):   是否最新1最新0不是
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        

        :return: DataFrame
         ts_code(str)  TS代码
         hs_type(str)  沪深港通类型SH沪SZ深
         in_date(str)  纳入日期
         out_date(str)  剔除日期
         is_new(str)  是否最新
        
        """
        args = [n for n in [
            'hs_type',
            'is_new',
            'limit',
            'offset',
        ] if n not in ['limit', 'offset']]
        params = {key: kwargs[key] for key in kwargs.keys() & args}
        query = session_factory().query(TushareHsConst).filter_by(**params)
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
        return [{"hs_type": "SH"}, {"hs_type": "SZ"}]

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
                    else:
                        logger.error("Execute fetch_and_append throw exp. {}".format(err))
                        continue

    def fetch_and_append(self, process_type: ProcessType, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        if len(kwargs.keys()) == 0:
            kwargs = {"hs_type": "", "is_new": "", "limit": "", "offset": ""}
        # 初始化offset和limit
        if not kwargs.get("limit"):
            kwargs['limit'] = ""
        init_offset = 0
        offset = 0
        if kwargs.get('offset'):
            offset = int(kwargs['offset'])
            init_offset = offset

        kwargs = {key: kwargs[key] for key in kwargs.keys() & list([
            'hs_type',
            'is_new',
            'limit',
            'offset',
        ])}

        @sleep(timeout=5, time_append=3, retry=20, match="^抱歉，您每分钟最多访问该接口")
        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            logger.debug("Invoke pro.hs_const with args: {}".format(kwargs))
            fields = ["ts_code", "hs_type", "in_date", "out_date", "is_new"]
            res = pro.hs_const(**kwargs, fields=fields)
            res.to_sql('tushare_hs_const', con=engine, if_exists='append', index=False, index_label=['ts_code'])
            return res

        pro = self.tushare_api()
        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    api = HsConst()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.hs_const())    # 数据查询接口
