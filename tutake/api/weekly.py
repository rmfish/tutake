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
Tushare weekly接口
数据接口-沪深股票-行情数据-周线行情  https://tushare.pro/document/2?doc_id=144
"""

engine = create_engine("%s/%s" % (config['database']['driver_url'], 'tushare_weekly.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()
logger = logging.getLogger('api.tushare.weekly')


class TushareWeekly(Base):
    __tablename__ = "tushare_weekly"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, comment='')
    trade_date = Column(String, comment='')
    close = Column(Float, comment='')
    open = Column(Float, comment='')
    high = Column(Float, comment='')
    low = Column(Float, comment='')
    pre_close = Column(Float, comment='')
    change = Column(Float, comment='')
    pct_chg = Column(Float, comment='')
    vol = Column(Float, comment='')
    amount = Column(Float, comment='')


TushareWeekly.__table__.create(bind=engine, checkfirst=True)


class Weekly(BaseDao, TuShareBase):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        BaseDao.__init__(self, engine, session_factory, TushareWeekly, 'tushare_weekly')
        TuShareBase.__init__(self)
        self.dao = DAO()

    def weekly(self, **kwargs):
        """
        周线行情

        | Arguments:
        | ts_code(str):   TS代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        

        :return: DataFrame
         ts_code(str)  
         trade_date(str)  
         close(float)  
         open(float)  
         high(float)  
         low(float)  
         pre_close(float)  
         change(float)  
         pct_chg(float)  
         vol(float)  
         amount(float)  
        
        """
        args = [
            n for n in [
                'ts_code',
                'trade_date',
                'start_date',
                'end_date',
                'limit',
                'offset',
            ] if n not in ['limit', 'offset']
        ]
        params = {key: kwargs[key] for key in kwargs.keys() & args}
        query = session_factory().query(TushareWeekly).filter_by(**params)
        query = query.order_by(text("trade_date desc,ts_code"))
        input_limit = 10000    # 默认10000条 避免导致数据库压力过大
        if kwargs.get('limit') and str(kwargs.get('limit')).isnumeric():
            input_limit = int(kwargs.get('limit'))
            query = query.limit(input_limit)
        if "4500" != "":
            default_limit = int("4500")
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

    def tushare_parameters(self, process_type: ProcessType):
        """
        同步历史数据调用的参数
        :return: list(dict)
        """
        return self.dao.stock_basic.column_data(['ts_code', 'list_date'])

    def param_loop_process(self, process_type: ProcessType, **params):
        """
        每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
        """
        from datetime import datetime, timedelta
        date_format = '%Y%m%d'
        if process_type == ProcessType.HISTORY:
            min_date = self.min("trade_date", "ts_code = '%s'" % params['ts_code'])
            if min_date is None:
                params['end_date'] = ""
            else:
                min_date = datetime.strptime(min_date, date_format)
                end_date = min_date - timedelta(days=7)
                if params.get('list_date'):
                    list_date = datetime.strptime(params.get('list_date'), date_format)
                    interval = (end_date - list_date).days
                    if interval < 0:
                        return None
                params['end_date'] = end_date.strftime(date_format)
            return params
        else:
            max_date = self.max("trade_date", "ts_code = '%s'" % params['ts_code'])
            if max_date is None:
                params['start_date'] = ""
            else:
                max_date = datetime.strptime(max_date, date_format)
                start_date = max_date + timedelta(days=7)
                if params.get('list_date'):
                    if (start_date - datetime.now()).days > 0:
                        return None
                    else:
                        params['start_date'] = start_date.strftime(date_format)
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
            kwargs = {"ts_code": "", "trade_date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
        # 初始化offset和limit
        if not kwargs.get("limit"):
            kwargs['limit'] = "4500"
        init_offset = 0
        offset = 0
        if kwargs.get('offset'):
            offset = int(kwargs['offset'])
            init_offset = offset

        kwargs = {
            key: kwargs[key] for key in kwargs.keys() & list([
                'ts_code',
                'trade_date',
                'start_date',
                'end_date',
                'limit',
                'offset',
            ])
        }

        @sleep(timeout=5, time_append=30, retry=20, match="^抱歉，您每分钟最多访问该接口")
        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            logger.debug("Invoke pro.weekly with args: {}".format(kwargs))
            fields = [
                "ts_code", "trade_date", "close", "open", "high", "low", "pre_close", "change", "pct_chg", "vol",
                "amount"
            ]
            res = pro.weekly(**kwargs, fields=fields)
            res.to_sql('tushare_weekly', con=engine, if_exists='append', index=False, index_label=['ts_code'])
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
    api = Weekly()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.weekly())    # 数据查询接口
