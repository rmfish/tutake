"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare shibor接口
Shibor利率，每日12点更新，上海银行间同业拆放利率（Shanghai Interbank Offered Rate，简称Shibor），以位于上海的全国银行间同业拆借中心为技术平台计算、发布并命名，是由信用等级较高的银行组成报价团自主报出的人民币同业拆出利率计算确定的算术平均利率，是单利、无担保、批发性利率。目前，对社会公布的Shibor品种包括隔夜、1周、2周、1个月、3个月、6个月、9个月及1年。

Shibor报价银行团现由18家商业银行组成。报价银行是公开市场一级交易商或外汇市场做市商，在中国货币市场上人民币交易相对活跃、信息披露比较充分的银行。中国人民银行成立Shibor工作小组，依据《上海银行间同业拆放利率（Shibor）实施准则》确定和调整报价银行团成员、监督和管理Shibor运行、规范报价行与指定发布人行为。

全国银行间同业拆借中心受权Shibor的报价计算和信息发布。每个交易日根据各报价行的报价，剔除最高、最低各4家报价，对其余报价进行算术平均计算后，得出每一期限品种的Shibor，并于11:00对外发布。
数据接口-宏观经济-国内宏观-利率数据-Shibor利率  https://tushare.pro/document/2?doc_id=149

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.shibor_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareShibor(Base):
    __tablename__ = "tushare_shibor"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, index=True, comment='日期')
    on_night = Column(Float, comment='隔夜')
    t_1w = Column(Float, comment='1周')
    t_2w = Column(Float, comment='2周')
    t_1m = Column(Float, comment='1月')
    t_3m = Column(Float, comment='3月')
    t_6m = Column(Float, comment='6月')
    t_9m = Column(Float, comment='9月')
    t_1y = Column(Float, comment='1年')


class Shibor(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_shibor"
        self.database = 'tushare_macroeconomic.db'
        self.database_url = config.get_data_sqlite_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareShibor.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = ['date', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = ["date", "on", "1w", "2w", "1m", "3m", "6m", "9m", "1y"]
        entity_fields = ["date", "on_night", "t_1w", "t_2w", "t_1m", "t_3m", "t_6m", "t_9m", "t_1y"]
        column_mapping = {
            'on_night': 'on',
            't_1w': '1w',
            't_2w': '2w',
            't_1m': '1m',
            't_3m': '3m',
            't_6m': '6m',
            't_9m': '9m',
            't_1y': '1y'
        }
        TushareDAO.__init__(self, self.engine, session_factory, TushareShibor, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "shibor", config)
        TuShareBase.__init__(self, "shibor", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "date",
            "type": "String",
            "comment": "日期"
        }, {
            "name": "on",
            "type": "Float",
            "comment": "隔夜"
        }, {
            "name": "1w",
            "type": "Float",
            "comment": "1周"
        }, {
            "name": "2w",
            "type": "Float",
            "comment": "2周"
        }, {
            "name": "1m",
            "type": "Float",
            "comment": "1月"
        }, {
            "name": "3m",
            "type": "Float",
            "comment": "3月"
        }, {
            "name": "6m",
            "type": "Float",
            "comment": "6月"
        }, {
            "name": "9m",
            "type": "Float",
            "comment": "9月"
        }, {
            "name": "1y",
            "type": "Float",
            "comment": "1年"
        }]

    def shibor(self, fields='', **kwargs):
        """
        Shibor利率，每日12点更新，上海银行间同业拆放利率（Shanghai Interbank Offered Rate，简称Shibor），以位于上海的全国银行间同业拆借中心为技术平台计算、发布并命名，是由信用等级较高的银行组成报价团自主报出的人民币同业拆出利率计算确定的算术平均利率，是单利、无担保、批发性利率。目前，对社会公布的Shibor品种包括隔夜、1周、2周、1个月、3个月、6个月、9个月及1年。

Shibor报价银行团现由18家商业银行组成。报价银行是公开市场一级交易商或外汇市场做市商，在中国货币市场上人民币交易相对活跃、信息披露比较充分的银行。中国人民银行成立Shibor工作小组，依据《上海银行间同业拆放利率（Shibor）实施准则》确定和调整报价银行团成员、监督和管理Shibor运行、规范报价行与指定发布人行为。

全国银行间同业拆借中心受权Shibor的报价计算和信息发布。每个交易日根据各报价行的报价，剔除最高、最低各4家报价，对其余报价进行算术平均计算后，得出每一期限品种的Shibor，并于11:00对外发布。
        | Arguments:
        | date(str):   日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         date(str)  日期 Y
         on(float)  隔夜 Y
         1w(float)  1周 Y
         2w(float)  2周 Y
         1m(float)  1月 Y
         3m(float)  3月 Y
         6m(float)  6月 Y
         9m(float)  9月 Y
         1y(float)  1年 Y
        
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append, BatchWriter(self.engine, self.table_name), **kwargs)

    def fetch_and_append(self, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        init_args = {"date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.shibor with args: {}".format(kwargs))
                return self.tushare_query('shibor', fields=self.tushare_fields, **kwargs)
            except Exception as err:
                raise ProcessException(kwargs, err)

        res = fetch_save(offset)
        size = res.size()
        offset += size
        while kwargs['limit'] != "" and size == int(kwargs['limit']):
            result = fetch_save(offset)
            size = result.size()
            offset += size
            res.append(result)
        res.fields = self.entity_fields
        return res


setattr(Shibor, 'default_limit', default_limit_ext)
setattr(Shibor, 'default_cron_express', default_cron_express_ext)
setattr(Shibor, 'default_order_by', default_order_by_ext)
setattr(Shibor, 'prepare', prepare_ext)
setattr(Shibor, 'query_parameters', query_parameters_ext)
setattr(Shibor, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.shibor())

    api = Shibor(config)
    print(api.process())    # 同步增量数据
    print(api.shibor())    # 数据查询接口
