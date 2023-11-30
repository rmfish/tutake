"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare cn_ppi接口
获取PPI工业生产者出厂价格指数数据
数据接口-宏观经济-国内宏观-价格指数-工业生产者出厂价格指数（PPI）  https://tushare.pro/document/2?doc_id=245

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts.cn_ppi_ext import *
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareCnPpi(TutakeTableBase):
    __tablename__ = "tushare_cn_ppi"
    month = Column(String, comment='月份YYYYMM')
    ppi_yoy = Column(Float, comment='PPI：全部工业品：当月同比')
    ppi_mp_yoy = Column(Float, comment='PPI：生产资料：当月同比')
    ppi_mp_qm_yoy = Column(Float, comment='PPI：生产资料：采掘业：当月同比')
    ppi_mp_rm_yoy = Column(Float, comment='PPI：生产资料：原料业：当月同比')
    ppi_mp_p_yoy = Column(Float, comment='PPI：生产资料：加工业：当月同比')
    ppi_cg_yoy = Column(Float, comment='PPI：生活资料：当月同比')
    ppi_cg_f_yoy = Column(Float, comment='PPI：生活资料：食品类：当月同比')
    ppi_cg_c_yoy = Column(Float, comment='PPI：生活资料：衣着类：当月同比')
    ppi_cg_adu_yoy = Column(Float, comment='PPI：生活资料：一般日用品类：当月同比')
    ppi_cg_dcg_yoy = Column(Float, comment='PPI：生活资料：耐用消费品类：当月同比')
    ppi_mom = Column(Float, comment='PPI：全部工业品：环比')
    ppi_mp_mom = Column(Float, comment='PPI：生产资料：环比')
    ppi_mp_qm_mom = Column(Float, comment='PPI：生产资料：采掘业：环比')
    ppi_mp_rm_mom = Column(Float, comment='PPI：生产资料：原料业：环比')
    ppi_mp_p_mom = Column(Float, comment='PPI：生产资料：加工业：环比')
    ppi_cg_mom = Column(Float, comment='PPI：生活资料：环比')
    ppi_cg_f_mom = Column(Float, comment='PPI：生活资料：食品类：环比')
    ppi_cg_c_mom = Column(Float, comment='PPI：生活资料：衣着类：环比')
    ppi_cg_adu_mom = Column(Float, comment='PPI：生活资料：一般日用品类：环比')
    ppi_cg_dcg_mom = Column(Float, comment='PPI：生活资料：耐用消费品类：环比')
    ppi_accu = Column(Float, comment='PPI：全部工业品：累计同比')
    ppi_mp_accu = Column(Float, comment='PPI：生产资料：累计同比')
    ppi_mp_qm_accu = Column(Float, comment='PPI：生产资料：采掘业：累计同比')
    ppi_mp_rm_accu = Column(Float, comment='PPI：生产资料：原料业：累计同比')
    ppi_mp_p_accu = Column(Float, comment='PPI：生产资料：加工业：累计同比')
    ppi_cg_accu = Column(Float, comment='PPI：生活资料：累计同比')
    ppi_cg_f_accu = Column(Float, comment='PPI：生活资料：食品类：累计同比')
    ppi_cg_c_accu = Column(Float, comment='PPI：生活资料：衣着类：累计同比')
    ppi_cg_adu_accu = Column(Float, comment='PPI：生活资料：一般日用品类：累计同比')
    ppi_cg_dcg_accu = Column(Float, comment='PPI：生活资料：耐用消费品类：累计同比')


class CnPpi(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_cn_ppi"
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
        TushareCnPpi.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareCnPpi)

        query_fields = ['m', 'start_m', 'end_m', 'limit', 'offset']
        self.tushare_fields = [
            "month", "ppi_yoy", "ppi_mp_yoy", "ppi_mp_qm_yoy", "ppi_mp_rm_yoy", "ppi_mp_p_yoy", "ppi_cg_yoy",
            "ppi_cg_f_yoy", "ppi_cg_c_yoy", "ppi_cg_adu_yoy", "ppi_cg_dcg_yoy", "ppi_mom", "ppi_mp_mom",
            "ppi_mp_qm_mom", "ppi_mp_rm_mom", "ppi_mp_p_mom", "ppi_cg_mom", "ppi_cg_f_mom", "ppi_cg_c_mom",
            "ppi_cg_adu_mom", "ppi_cg_dcg_mom", "ppi_accu", "ppi_mp_accu", "ppi_mp_qm_accu", "ppi_mp_rm_accu",
            "ppi_mp_p_accu", "ppi_cg_accu", "ppi_cg_f_accu", "ppi_cg_c_accu", "ppi_cg_adu_accu", "ppi_cg_dcg_accu"
        ]
        entity_fields = [
            "month", "ppi_yoy", "ppi_mp_yoy", "ppi_mp_qm_yoy", "ppi_mp_rm_yoy", "ppi_mp_p_yoy", "ppi_cg_yoy",
            "ppi_cg_f_yoy", "ppi_cg_c_yoy", "ppi_cg_adu_yoy", "ppi_cg_dcg_yoy", "ppi_mom", "ppi_mp_mom",
            "ppi_mp_qm_mom", "ppi_mp_rm_mom", "ppi_mp_p_mom", "ppi_cg_mom", "ppi_cg_f_mom", "ppi_cg_c_mom",
            "ppi_cg_adu_mom", "ppi_cg_dcg_mom", "ppi_accu", "ppi_mp_accu", "ppi_mp_qm_accu", "ppi_mp_rm_accu",
            "ppi_mp_p_accu", "ppi_cg_accu", "ppi_cg_f_accu", "ppi_cg_c_accu", "ppi_cg_adu_accu", "ppi_cg_dcg_accu"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareCnPpi, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "cn_ppi", config)
        TuShareBase.__init__(self, "cn_ppi", config, 600)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "month",
            "type": "String",
            "comment": "月份YYYYMM"
        }, {
            "name": "ppi_yoy",
            "type": "Float",
            "comment": "PPI：全部工业品：当月同比"
        }, {
            "name": "ppi_mp_yoy",
            "type": "Float",
            "comment": "PPI：生产资料：当月同比"
        }, {
            "name": "ppi_mp_qm_yoy",
            "type": "Float",
            "comment": "PPI：生产资料：采掘业：当月同比"
        }, {
            "name": "ppi_mp_rm_yoy",
            "type": "Float",
            "comment": "PPI：生产资料：原料业：当月同比"
        }, {
            "name": "ppi_mp_p_yoy",
            "type": "Float",
            "comment": "PPI：生产资料：加工业：当月同比"
        }, {
            "name": "ppi_cg_yoy",
            "type": "Float",
            "comment": "PPI：生活资料：当月同比"
        }, {
            "name": "ppi_cg_f_yoy",
            "type": "Float",
            "comment": "PPI：生活资料：食品类：当月同比"
        }, {
            "name": "ppi_cg_c_yoy",
            "type": "Float",
            "comment": "PPI：生活资料：衣着类：当月同比"
        }, {
            "name": "ppi_cg_adu_yoy",
            "type": "Float",
            "comment": "PPI：生活资料：一般日用品类：当月同比"
        }, {
            "name": "ppi_cg_dcg_yoy",
            "type": "Float",
            "comment": "PPI：生活资料：耐用消费品类：当月同比"
        }, {
            "name": "ppi_mom",
            "type": "Float",
            "comment": "PPI：全部工业品：环比"
        }, {
            "name": "ppi_mp_mom",
            "type": "Float",
            "comment": "PPI：生产资料：环比"
        }, {
            "name": "ppi_mp_qm_mom",
            "type": "Float",
            "comment": "PPI：生产资料：采掘业：环比"
        }, {
            "name": "ppi_mp_rm_mom",
            "type": "Float",
            "comment": "PPI：生产资料：原料业：环比"
        }, {
            "name": "ppi_mp_p_mom",
            "type": "Float",
            "comment": "PPI：生产资料：加工业：环比"
        }, {
            "name": "ppi_cg_mom",
            "type": "Float",
            "comment": "PPI：生活资料：环比"
        }, {
            "name": "ppi_cg_f_mom",
            "type": "Float",
            "comment": "PPI：生活资料：食品类：环比"
        }, {
            "name": "ppi_cg_c_mom",
            "type": "Float",
            "comment": "PPI：生活资料：衣着类：环比"
        }, {
            "name": "ppi_cg_adu_mom",
            "type": "Float",
            "comment": "PPI：生活资料：一般日用品类：环比"
        }, {
            "name": "ppi_cg_dcg_mom",
            "type": "Float",
            "comment": "PPI：生活资料：耐用消费品类：环比"
        }, {
            "name": "ppi_accu",
            "type": "Float",
            "comment": "PPI：全部工业品：累计同比"
        }, {
            "name": "ppi_mp_accu",
            "type": "Float",
            "comment": "PPI：生产资料：累计同比"
        }, {
            "name": "ppi_mp_qm_accu",
            "type": "Float",
            "comment": "PPI：生产资料：采掘业：累计同比"
        }, {
            "name": "ppi_mp_rm_accu",
            "type": "Float",
            "comment": "PPI：生产资料：原料业：累计同比"
        }, {
            "name": "ppi_mp_p_accu",
            "type": "Float",
            "comment": "PPI：生产资料：加工业：累计同比"
        }, {
            "name": "ppi_cg_accu",
            "type": "Float",
            "comment": "PPI：生活资料：累计同比"
        }, {
            "name": "ppi_cg_f_accu",
            "type": "Float",
            "comment": "PPI：生活资料：食品类：累计同比"
        }, {
            "name": "ppi_cg_c_accu",
            "type": "Float",
            "comment": "PPI：生活资料：衣着类：累计同比"
        }, {
            "name": "ppi_cg_adu_accu",
            "type": "Float",
            "comment": "PPI：生活资料：一般日用品类：累计同比"
        }, {
            "name": "ppi_cg_dcg_accu",
            "type": "Float",
            "comment": "PPI：生活资料：耐用消费品类：累计同比"
        }]

    def cn_ppi(self, fields='', **kwargs):
        """
        获取PPI工业生产者出厂价格指数数据
        | Arguments:
        | m(str):   月份（YYYYMM，下同），支持多个月份同时输入，逗号分隔
        | start_m(str):   开始月份
        | end_m(str):   结束月份
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         month(str)  月份YYYYMM Y
         ppi_yoy(float)  PPI：全部工业品：当月同比 Y
         ppi_mp_yoy(float)  PPI：生产资料：当月同比 Y
         ppi_mp_qm_yoy(float)  PPI：生产资料：采掘业：当月同比 Y
         ppi_mp_rm_yoy(float)  PPI：生产资料：原料业：当月同比 Y
         ppi_mp_p_yoy(float)  PPI：生产资料：加工业：当月同比 Y
         ppi_cg_yoy(float)  PPI：生活资料：当月同比 Y
         ppi_cg_f_yoy(float)  PPI：生活资料：食品类：当月同比 Y
         ppi_cg_c_yoy(float)  PPI：生活资料：衣着类：当月同比 Y
         ppi_cg_adu_yoy(float)  PPI：生活资料：一般日用品类：当月同比 Y
         ppi_cg_dcg_yoy(float)  PPI：生活资料：耐用消费品类：当月同比 Y
         ppi_mom(float)  PPI：全部工业品：环比 Y
         ppi_mp_mom(float)  PPI：生产资料：环比 Y
         ppi_mp_qm_mom(float)  PPI：生产资料：采掘业：环比 Y
         ppi_mp_rm_mom(float)  PPI：生产资料：原料业：环比 Y
         ppi_mp_p_mom(float)  PPI：生产资料：加工业：环比 Y
         ppi_cg_mom(float)  PPI：生活资料：环比 Y
         ppi_cg_f_mom(float)  PPI：生活资料：食品类：环比 Y
         ppi_cg_c_mom(float)  PPI：生活资料：衣着类：环比 Y
         ppi_cg_adu_mom(float)  PPI：生活资料：一般日用品类：环比 Y
         ppi_cg_dcg_mom(float)  PPI：生活资料：耐用消费品类：环比 Y
         ppi_accu(float)  PPI：全部工业品：累计同比 Y
         ppi_mp_accu(float)  PPI：生产资料：累计同比 Y
         ppi_mp_qm_accu(float)  PPI：生产资料：采掘业：累计同比 Y
         ppi_mp_rm_accu(float)  PPI：生产资料：原料业：累计同比 Y
         ppi_mp_p_accu(float)  PPI：生产资料：加工业：累计同比 Y
         ppi_cg_accu(float)  PPI：生活资料：累计同比 Y
         ppi_cg_f_accu(float)  PPI：生活资料：食品类：累计同比 Y
         ppi_cg_c_accu(float)  PPI：生活资料：衣着类：累计同比 Y
         ppi_cg_adu_accu(float)  PPI：生活资料：一般日用品类：累计同比 Y
         ppi_cg_dcg_accu(float)  PPI：生活资料：耐用消费品类：累计同比 Y
        
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
        init_args = {"m": "", "start_m": "", "end_m": "", "limit": "", "offset": ""}
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
                self.logger.debug("Invoke pro.cn_ppi with args: {}".format(kwargs))
                return self.tushare_query('cn_ppi', fields=self.tushare_fields, **kwargs)
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


setattr(CnPpi, 'default_limit', default_limit_ext)
setattr(CnPpi, 'default_cron_express', default_cron_express_ext)
setattr(CnPpi, 'default_order_by', default_order_by_ext)
setattr(CnPpi, 'prepare', prepare_ext)
setattr(CnPpi, 'query_parameters', query_parameters_ext)
setattr(CnPpi, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.cn_ppi())

    api = CnPpi(config)
    print(api.process())    # 同步增量数据
    print(api.cn_ppi())    # 数据查询接口
