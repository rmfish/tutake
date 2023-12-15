"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare shibor_lpr接口
LPR贷款基础利率 每日12点更新，贷款基础利率（Loan Prime Rate，简称LPR），是基于报价行自主报出的最优贷款利率计算并发布的贷款市场参考利率。目前，对社会公布1年期贷款基础利率。

LPR报价银行团现由10家商业银行组成。报价银行应符合财务硬约束条件和宏观审慎政策框架要求，系统重要性程度高、市场影响力大、综合实力强，已建立内部收益率曲线和内部转移定价机制，具有较强的自主定价能力，已制定本行贷款基础利率管理办法，以及有利于开展报价工作的其他条件。市场利率定价自律机制依据《贷款基础利率集中报价和发布规则》确定和调整报价行成员，监督和管理贷款基础利率运行，规范报价行与指定发布人行为。

全国银行间同业拆借中心受权贷款基础利率的报价计算和信息发布。每个交易日根据各报价行的报价，剔除最高、最低各1家报价，对其余报价进行加权平均计算后，得出贷款基础利率报价平均利率，并于11:30对外发布
数据接口-宏观经济-国内宏观-利率数据-LPR贷款基础利率  https://tushare.pro/document/2?doc_id=151

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import shibor_lpr_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareShiborLpr(TutakeTableBase):
    __tablename__ = "tushare_shibor_lpr"
    date = Column(String, index=True, comment='日期')
    t_1y = Column(Float, comment='1年贷款利率')
    t_5y = Column(Float, comment='5年贷款利率')


class ShiborLpr(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_shibor_lpr"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareShiborLpr.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareShiborLpr),
                                  config.get_tutake_data_dir())

        query_fields = ['date', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = ["date", "1y", "5y"]
        entity_fields = ["date", "t_1y", "t_5y"]
        column_mapping = {'t_1y': '1y', 't_5y': '5y'}
        TushareDAO.__init__(self, self.engine, session_factory, TushareShiborLpr, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "shibor_lpr", config)
        TuShareBase.__init__(self, "shibor_lpr", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "date",
            "type": "String",
            "comment": "日期"
        }, {
            "name": "1y",
            "type": "Float",
            "comment": "1年贷款利率"
        }, {
            "name": "5y",
            "type": "Float",
            "comment": "5年贷款利率"
        }]

    def shibor_lpr(self, fields='', **kwargs):
        """
        LPR贷款基础利率 每日12点更新，贷款基础利率（Loan Prime Rate，简称LPR），是基于报价行自主报出的最优贷款利率计算并发布的贷款市场参考利率。目前，对社会公布1年期贷款基础利率。

LPR报价银行团现由10家商业银行组成。报价银行应符合财务硬约束条件和宏观审慎政策框架要求，系统重要性程度高、市场影响力大、综合实力强，已建立内部收益率曲线和内部转移定价机制，具有较强的自主定价能力，已制定本行贷款基础利率管理办法，以及有利于开展报价工作的其他条件。市场利率定价自律机制依据《贷款基础利率集中报价和发布规则》确定和调整报价行成员，监督和管理贷款基础利率运行，规范报价行与指定发布人行为。

全国银行间同业拆借中心受权贷款基础利率的报价计算和信息发布。每个交易日根据各报价行的报价，剔除最高、最低各1家报价，对其余报价进行加权平均计算后，得出贷款基础利率报价平均利率，并于11:30对外发布
        | Arguments:
        | date(str):   日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         date(str)  日期 Y
         1y(float)  1年贷款利率 Y
         5y(float)  5年贷款利率 Y
        
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append, self.writer, **kwargs)

    def fetch_and_append(self, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        init_args = {"date": "", "start_date": "", "end_date": "", "limit": "", "offset": ""}
        is_test = kwargs.get('test') or False
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
                self.logger.debug("Invoke pro.shibor_lpr with args: {}".format(kwargs))
                return self.tushare_query('shibor_lpr', fields=self.tushare_fields, **kwargs)
            except Exception as err:
                raise ProcessException(kwargs, err)

        res = fetch_save(offset)
        size = res.size()
        offset += size
        res.fields = self.entity_fields
        if is_test:
            return res
        while kwargs['limit'] != "" and size == int(kwargs['limit']):
            result = fetch_save(offset)
            size = result.size()
            offset += size
            res.append(result)
        return res


extends_attr(ShiborLpr, shibor_lpr_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.shibor_lpr())

    api = ShiborLpr(config)
    print(api.process())    # 同步增量数据
    print(api.shibor_lpr())    # 数据查询接口
