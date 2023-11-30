"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare monthly接口
获取A股月线行情,全部历史，每月更新
数据接口-沪深股票-行情数据-月线行情  https://tushare.pro/document/2?doc_id=145

@author: rmfish
"""
import pandas as pd
import pendulum
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base, BatchWriter, Records, BaseDao, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.monthly_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareMonthlyAdj(TutakeTableBase):
    __tablename__ = "tushare_monthly_adj"
    ts_code = Column(String, index=True, comment='')
    trade_date = Column(String, index=True, comment='')
    close_adj = Column(Float, comment='')
    open_adj = Column(Float, comment='')


class MonthlyAdj(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_monthly_adj"
        self.database = 'tutake.duckdb'
        self.database_dir = config.get_tutake_data_dir()
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareMonthlyAdj.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareMonthlyAdj)

        query_fields = ['ts_code', 'trade_date', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "trade_date", "close_adj", "open_adj"
        ]
        entity_fields = [
            "ts_code", "trade_date", "close_adj", "open_adj"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareMonthlyAdj, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "monthly_adj", config)
        TuShareBase.__init__(self, "monthly_adj", config, 600)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": ""
        }, {
            "name": "trade_date",
            "type": "String",
            "comment": ""
        }, {
            "name": "close_adj",
            "type": "Float",
            "comment": ""
        }, {
            "name": "open_adj",
            "type": "Float",
            "comment": ""
        }]

    def monthly_adj(self, fields='', **kwargs):
        """
        获取A股月线行情,全部历史，每月更新
        | Arguments:
        | ts_code(str):   TS代码
        | trade_date(str):   交易日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)   Y
         trade_date(str)   Y
         close_adj(float)   Y
         open_adj(float)   Y
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append,
                                BatchWriter(self.engine, self.table_name, self.schema, self.database_dir), **kwargs)

    def fetch_and_append(self, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        trade_date = kwargs['trade_date']
        end = pendulum.parse(trade_date)
        start = end.start_of("month")
        monthly = self.api.monthly.query(trade_date=trade_date)
        adj_factor = self.api.adj_factor.query(start_date=start.format("YYYYMMDD"),
                                               end_date=end.format("YYYYMMDD"), limit=100000)

        # 按照'code'进行分组，并找到每个代码对应的最小和最大日期
        grouped_df = adj_factor.groupby('ts_code').agg({'trade_date': ['min', 'max']}).reset_index()

        # 重命名列
        grouped_df.columns = ['ts_code', 'min_date', 'max_date']

        # 根据最小和最大日期从原始 DataFrame 中提取相应的值
        result_df = pd.merge(adj_factor, grouped_df, on='ts_code')
        result_df = result_df[
            (result_df['trade_date'] == result_df['min_date']) | (result_df['trade_date'] == result_df['max_date'])]
        # 重命名列
        result_df.columns = ['ts_code', 'trade_date', 'adj_factor', 'min_date', 'max_date']

        # 提取最小和最大日期对应的值
        # 重命名列
        result_df.columns = ['ts_code', 'trade_date', 'adj_factor', 'min_date', 'max_date']

        # 提取最小和最大日期对应的值
        result_df = result_df.groupby(['ts_code', 'min_date', 'max_date']).agg(min_val=('adj_factor', 'min'),
                                                                               max_val=(
                                                                                   'adj_factor', 'max')).reset_index()

        print(result_df)
        # init_args = {"ts_code": "", "trade_date": "", "limit": "", "offset": ""}
        # if len(kwargs.keys()) == 0:
        #     kwargs = init_args
        # # 初始化offset和limit
        # if not kwargs.get("limit"):
        #     kwargs['limit'] = self.default_limit()
        # init_offset = 0
        # offset = 0
        # if kwargs.get('offset'):
        #     offset = int(kwargs['offset'])
        #     init_offset = offset
        #
        # kwargs = {key: kwargs[key] for key in kwargs.keys() & init_args.keys()}
        #
        # def fetch_save(offset_val=0):
        #     try:
        #         kwargs['offset'] = str(offset_val)
        #         self.logger.debug("Invoke pro.monthly with args: {}".format(kwargs))
        #         self.api.monthly(**kwargs)
        #         return self.tushare_query('monthly', fields=self.tushare_fields, **kwargs)
        #     except Exception as err:
        #         raise ProcessException(kwargs, err)
        #
        # res = fetch_save(offset)
        # size = res.size()
        # offset += size
        # while kwargs['limit'] != "" and size == int(kwargs['limit']):
        #     result = fetch_save(offset)
        #     size = result.size()
        #     offset += size
        #     res.append(result)
        # res.fields = self.entity_fields
        return None

    def query_parameters(self):
        """
        同步历史数据调用的参数
        :return: list(dict)
        """
        return m_by_m_params(self, '19901231')


if __name__ == '__main__':
    # pd.set_option('display.max_columns', 50)  # 显示列数
    # pd.set_option('display.width', 100)
    # config = TutakeConfig(project_root())
    #
    # api = MonthlyAdj(config)
    # print(api.process())  # 同步增量数据
    # print(api.monthly_adj(ts_code='000001.SZ'))  # 数据查询接口

    df = pd.DataFrame({
        'ts_code': ['A', 'A', 'A', 'B', 'B', 'B'],
        'trade_date': ['20210905', '20210912', '20210920', '20210908', '20210915', '20210922'],
        'adj_factor': [10, 20, 15, 30, 25, 35]
    })

    # 将日期列转换为日期对象
    # df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')

    # 按照'code'进行分组，并找到每个代码对应的最小和最大日期
    # grouped_df = df.groupby('ts_code').agg({'trade_date': ['min', 'max']}).reset_index()
    #
    # # 重命名列
    # grouped_df.columns = ['ts_code', 'min_date', 'max_date']
    #
    # # 根据最小和最大日期从原始 DataFrame 中提取相应的值
    # result_df = pd.merge(df, grouped_df, on='ts_code')
    # result_df = result_df[
    #     (result_df['trade_date'] == result_df['min_date']) | (result_df['trade_date'] == result_df['max_date'])]
    # # 重命名列
    # result_df.columns = ['ts_code', 'trade_date', 'adj_factor', 'min_date', 'max_date']
    #
    # # 提取最小和最大日期对应的值
    # # 重命名列
    # result_df.columns = ['ts_code', 'trade_date', 'adj_factor', 'min_date', 'max_date']
    #
    # print(result_df)

    # result_df = pd.DataFrame({'ts_code': ['A', 'A', 'B', 'B'], 'trade_date': ['10', '15', '30', '35'],
    #                           'min_date': ['20210905', '20210905', '20210908', '20210908'],
    #                           'max_date': ['20210920', '20210920', '20210922', '20210922'],
    #                           'adj_factor': [10, 15, 30, 35]})
    #
    #
    # # 提取最小和最大日期对应的值
    # # result_df = result_df.groupby(['ts_code', 'min_date', 'max_date']).agg(min_val=('adj_factor', 'min'),
    # #                                                                        max_val=('adj_factor', 'max')).reset_index()
    #
    # def func(df):
    #     print(df)
    #     print()
    #
    #
    # result_df = result_df.groupby(['ts_code', 'min_date', 'max_date']).agg(min_val=(['adj_factor', 'trade_date'], func),
    #                                                                        max_val=(['adj_factor', 'trade_date'],
    #                                                                                 func)).reset_index()
    # print(result_df)

    df = pd.DataFrame({
        'ts_code': ['A', 'A', 'A', 'B', 'B', 'B'],
        'trade_date': ['20210905', '20210912', '20210920', '20210908', '20210915', '20210922'],
        'adj_factor': [15, 20, 10, 30, 25, 35]
    })
    # 将日期列转换为日期对象
    # df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

    # 按照 'code' 进行分组，并根据 'date' 列计算最小值和最大值
    result_df = df.groupby('ts_code').agg(min_date=('trade_date', 'min'), max_date=('trade_date', 'max')).reset_index()
    # 使用 merge 将原始 DataFrame 与计算出的最小值和最大值 DataFrame 进行合并
    result_df = pd.merge(df, result_df, on='ts_code')
    result_df = result_df.loc[
        (result_df['trade_date'] == result_df['min_date']) | (result_df['trade_date'] == result_df['max_date'])]


    # print(result_df)

    # 按照 'code'、'min_date'、'max_date' 进行分组，并比较对应的最小和最大日期的 'val' 值，得到最小值和最大值
    def group_df(df):
        # df['min_val'] = df['adj_factor'][0]
        # df['max_val'] = df['adj_factor'][1]
        print(df)
        return df


    result_df = result_df.groupby(['ts_code', 'min_date', 'max_date']).transform(
        group_df).reset_index()
    # 打印结果
    print(result_df)
