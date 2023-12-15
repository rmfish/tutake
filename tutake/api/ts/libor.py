"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare libor接口
Libor拆借利率，每日12点更新，Libor（London Interbank Offered Rate ），即伦敦同业拆借利率，是指伦敦的第一流银行之间短期资金借贷的利率，是国际金融市场中大多数浮动利率的基础利率。作为银行从市场上筹集资金进行转贷的融资成本，贷款协议中议定的LIBOR通常是由几家指定的参考银行，在规定的时间（一般是伦敦时间上午11：00）报价的平均利率。
数据接口-宏观经济-国内宏观-利率数据-Libor利率  https://tushare.pro/document/2?doc_id=152

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import libor_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareLibor(TutakeTableBase):
    __tablename__ = "tushare_libor"
    date = Column(String, index=True, comment='日期')
    curr_type = Column(String, index=True, comment='货币')
    on_night = Column(Float, comment='隔夜')
    t_1w = Column(Float, comment='1周')
    t_1m = Column(Float, comment='1个月')
    t_2m = Column(Float, comment='2个月')
    t_3m = Column(Float, comment='3个月')
    t_6m = Column(Float, comment='6个月')
    t_12m = Column(Float, comment='12个月')


class Libor(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_libor"
        self.database = 'tutake.duckdb'
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareLibor.__table__.create(bind=self.engine, checkfirst=True)
        self.writer = BatchWriter(self.engine, self.table_name, BaseDao.parquet_schema(TushareLibor),
                                  config.get_tutake_data_dir())

        query_fields = ['date', 'start_date', 'end_date', 'curr_type', 'limit', 'offset']
        self.tushare_fields = ["date", "curr_type", "on", "1w", "1m", "2m", "3m", "6m", "12m"]
        entity_fields = ["date", "curr_type", "on_night", "t_1w", "t_1m", "t_2m", "t_3m", "t_6m", "t_12m"]
        column_mapping = {
            'on_night': 'on',
            't_1w': '1w',
            't_1m': '1m',
            't_2m': '2m',
            't_3m': '3m',
            't_6m': '6m',
            't_12m': '12m'
        }
        TushareDAO.__init__(self, self.engine, session_factory, TushareLibor, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "libor", config)
        TuShareBase.__init__(self, "libor", config, 120)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "date",
            "type": "String",
            "comment": "日期"
        }, {
            "name": "curr_type",
            "type": "String",
            "comment": "货币"
        }, {
            "name": "on",
            "type": "Float",
            "comment": "隔夜"
        }, {
            "name": "1w",
            "type": "Float",
            "comment": "1周"
        }, {
            "name": "1m",
            "type": "Float",
            "comment": "1个月"
        }, {
            "name": "2m",
            "type": "Float",
            "comment": "2个月"
        }, {
            "name": "3m",
            "type": "Float",
            "comment": "3个月"
        }, {
            "name": "6m",
            "type": "Float",
            "comment": "6个月"
        }, {
            "name": "12m",
            "type": "Float",
            "comment": "12个月"
        }]

    def libor(self, fields='', **kwargs):
        """
        Libor拆借利率，每日12点更新，Libor（London Interbank Offered Rate ），即伦敦同业拆借利率，是指伦敦的第一流银行之间短期资金借贷的利率，是国际金融市场中大多数浮动利率的基础利率。作为银行从市场上筹集资金进行转贷的融资成本，贷款协议中议定的LIBOR通常是由几家指定的参考银行，在规定的时间（一般是伦敦时间上午11：00）报价的平均利率。
        | Arguments:
        | date(str):   日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | curr_type(str):   货币代码
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         date(str)  日期 Y
         curr_type(str)  货币 Y
         on(float)  隔夜 Y
         1w(float)  1周 Y
         1m(float)  1个月 Y
         2m(float)  2个月 Y
         3m(float)  3个月 Y
         6m(float)  6个月 Y
         12m(float)  12个月 Y
        
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
        init_args = {"date": "", "start_date": "", "end_date": "", "curr_type": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.libor with args: {}".format(kwargs))
                return self.tushare_query('libor', fields=self.tushare_fields, **kwargs)
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


extends_attr(Libor, libor_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.libor())

    api = Libor(config)
    print(api.process())    # 同步增量数据
    print(api.libor())    # 数据查询接口
