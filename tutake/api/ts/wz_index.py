"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare wz_index接口
温州民间借贷利率，即温州指数，即温州民间融资综合利率指数，该指数及时反映民间金融交易活跃度和交易价格。该指数样板数据主要采集于四个方面：由温州市设立的几百家企业测报点，把各自借入的民间资本利率通过各地方金融办不记名申报收集起来；对各小额贷款公司借出的利率进行加权平均；融资性担保公司如典当行在融资过程中的利率，由温州经信委和商务局负责测报；民间借贷服务中心的实时利率。这些利率进行加权平均，就得出了“温州指数”。它是温州民间融资利率的风向标。2012年12月7日，温州指数正式对外发布。
数据接口-宏观经济-国内宏观-利率数据-温州民间借贷利率  https://tushare.pro/document/2?doc_id=173

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import wz_index_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareWzIndex(TutakeTableBase):
    __tablename__ = "tushare_wz_index"
    date = Column(String, index=True, comment='日期')
    comp_rate = Column(Float, comment='温州民间融资综合利率指数')
    center_rate = Column(Float, comment='民间借贷服务中心利率')
    micro_rate = Column(Float, comment='小额贷款公司放款利率')
    cm_rate = Column(Float, comment='民间资本管理公司融资价格')
    sdb_rate = Column(Float, comment='社会直接借贷利率')
    om_rate = Column(Float, comment='其他市场主体利率')
    aa_rate = Column(Float, comment='农村互助会互助金费率')
    m1_rate = Column(Float, comment='温州地区民间借贷分期限利率（一月期）')
    m3_rate = Column(Float, comment='温州地区民间借贷分期限利率（三月期）')
    m6_rate = Column(Float, comment='温州地区民间借贷分期限利率（六月期）')
    m12_rate = Column(Float, comment='温州地区民间借贷分期限利率（一年期）')
    long_rate = Column(Float, comment='温州地区民间借贷分期限利率（长期）')


class WzIndex(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_wz_index"
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
        TushareWzIndex.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareWzIndex)

        query_fields = ['date', 'start_date', 'end_date', 'limit', 'offset']
        self.tushare_fields = [
            "date", "comp_rate", "center_rate", "micro_rate", "cm_rate", "sdb_rate", "om_rate", "aa_rate", "m1_rate",
            "m3_rate", "m6_rate", "m12_rate", "long_rate"
        ]
        entity_fields = [
            "date", "comp_rate", "center_rate", "micro_rate", "cm_rate", "sdb_rate", "om_rate", "aa_rate", "m1_rate",
            "m3_rate", "m6_rate", "m12_rate", "long_rate"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareWzIndex, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "wz_index", config)
        TuShareBase.__init__(self, "wz_index", config, 2000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "date",
            "type": "String",
            "comment": "日期"
        }, {
            "name": "comp_rate",
            "type": "Float",
            "comment": "温州民间融资综合利率指数"
        }, {
            "name": "center_rate",
            "type": "Float",
            "comment": "民间借贷服务中心利率"
        }, {
            "name": "micro_rate",
            "type": "Float",
            "comment": "小额贷款公司放款利率"
        }, {
            "name": "cm_rate",
            "type": "Float",
            "comment": "民间资本管理公司融资价格"
        }, {
            "name": "sdb_rate",
            "type": "Float",
            "comment": "社会直接借贷利率"
        }, {
            "name": "om_rate",
            "type": "Float",
            "comment": "其他市场主体利率"
        }, {
            "name": "aa_rate",
            "type": "Float",
            "comment": "农村互助会互助金费率"
        }, {
            "name": "m1_rate",
            "type": "Float",
            "comment": "温州地区民间借贷分期限利率（一月期）"
        }, {
            "name": "m3_rate",
            "type": "Float",
            "comment": "温州地区民间借贷分期限利率（三月期）"
        }, {
            "name": "m6_rate",
            "type": "Float",
            "comment": "温州地区民间借贷分期限利率（六月期）"
        }, {
            "name": "m12_rate",
            "type": "Float",
            "comment": "温州地区民间借贷分期限利率（一年期）"
        }, {
            "name": "long_rate",
            "type": "Float",
            "comment": "温州地区民间借贷分期限利率（长期）"
        }]

    def wz_index(self, fields='', **kwargs):
        """
        温州民间借贷利率，即温州指数，即温州民间融资综合利率指数，该指数及时反映民间金融交易活跃度和交易价格。该指数样板数据主要采集于四个方面：由温州市设立的几百家企业测报点，把各自借入的民间资本利率通过各地方金融办不记名申报收集起来；对各小额贷款公司借出的利率进行加权平均；融资性担保公司如典当行在融资过程中的利率，由温州经信委和商务局负责测报；民间借贷服务中心的实时利率。这些利率进行加权平均，就得出了“温州指数”。它是温州民间融资利率的风向标。2012年12月7日，温州指数正式对外发布。
        | Arguments:
        | date(str):   日期
        | start_date(str):   开始日期
        | end_date(str):   结束日期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         date(str)  日期 Y
         comp_rate(float)  温州民间融资综合利率指数 Y
         center_rate(float)  民间借贷服务中心利率 Y
         micro_rate(float)  小额贷款公司放款利率 Y
         cm_rate(float)  民间资本管理公司融资价格 Y
         sdb_rate(float)  社会直接借贷利率 Y
         om_rate(float)  其他市场主体利率 Y
         aa_rate(float)  农村互助会互助金费率 Y
         m1_rate(float)  温州地区民间借贷分期限利率（一月期） Y
         m3_rate(float)  温州地区民间借贷分期限利率（三月期） Y
         m6_rate(float)  温州地区民间借贷分期限利率（六月期） Y
         m12_rate(float)  温州地区民间借贷分期限利率（一年期） Y
         long_rate(float)  温州地区民间借贷分期限利率（长期） Y
        
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
                self.logger.debug("Invoke pro.wz_index with args: {}".format(kwargs))
                return self.tushare_query('wz_index', fields=self.tushare_fields, **kwargs)
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


extends_attr(WzIndex, wz_index_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.wz_index())

    api = WzIndex(config)
    print(api.process())    # 同步增量数据
    print(api.wz_index())    # 数据查询接口
