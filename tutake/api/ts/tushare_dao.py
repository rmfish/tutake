from sqlalchemy import create_engine, and_, orm
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from tutake.api.base_dao import BaseDao
from tutake.api.ts.tushare_base import Records
from tutake.utils.config import TutakeConfig

engine_pool = {}


def create_shared_engine(url: str, **connect_args):
    # return create_engine("duckdb:///D:\\Dataset\\quant\\tutake\\tutake.duckdb", poolclass=QueuePool, **connect_args)
    if url.startswith("duckdb"):
        return create_engine(url, poolclass=QueuePool)
    else:
        return create_engine(url, poolclass=QueuePool, **connect_args)
    # return create_engine("duckdb:///D:\\Dataset\\quant\\tutake\\tutake1.duckdb", poolclass=QueuePool)


class TushareDAO(BaseDao):

    def __init__(self, engine, session_factory: sessionmaker, entities, database, table_name, query_fields,
                 entity_fields, column_mapping, config: TutakeConfig):
        super().__init__(engine, session_factory, entities, database, table_name, query_fields, entity_fields,
                         column_mapping, config)
        self.records = Records()

    def filter_process(self, filter_criterion, filter_by):
        split_columns = []
        if self.table_name in ['tushare_daily', 'tushare_weekly', 'tushare_monthly', 'tushare_adj_factor',
                               'tushare_stock_basic']:
            split_columns = ['ts_code']
        elif self.table_name in ['tushare_trade_cal']:
            split_columns = ['exchange']
        return self.filter_process_by_column(filter_criterion, filter_by, split_columns)

    def filter_process_by_column(self, filter_criterion, filter_by, split_columns):
        keys_to_remove = []
        for key in filter_by.keys():
            field = filter_by.get(key)
            if field is not None:
                codes = None
                if key in split_columns and "," in field:
                    codes = field.split(",")
                elif isinstance(field, list):
                    codes = field
                if codes is not None:
                    keys_to_remove.append(key)
                    if filter_criterion is None:
                        filter_criterion = orm.class_mapper(self.entities).c[key].in_(codes)
                    else:
                        filter_criterion = and_(orm.class_mapper(self.entities).c[key].in_(codes), filter_criterion)
                    # del filter_by[key]
        for key in keys_to_remove:
            del filter_by[key]
        return filter_criterion, filter_by

    def default_time_range(self) -> ():
        if self.table_name == 'tushare_trade_cal':
            return 'start_date', 'end_date', self.entities.cal_date
        elif self.table_name == 'tushare_new_share':
            return 'start_date', 'end_date', self.entities.ipo_date
        elif self.table_name in ['tushare_balancesheet_vip', 'tushare_fund_portfolio', 'tushare_fina_indicator_vip',
                                 'tushare_income_vip', 'tushare_express_vip', 'tushare_forecast_vip',
                                 'tushare_cashflow_vip']:
            return 'start_date', 'end_date', self.entities.end_date
        elif self.table_name == 'tushare_fund_nav':
            return 'start_date', 'end_date', self.entities.nav_date
        elif self.table_name in ['tushare_stk_managers', 'tushare_namechange', 'tushare_anns', 'tushare_fina_audit',
                                 'tushare_top10_floatholders', 'tushare_top10_holders']:
            return 'start_date', 'end_date', self.entities.ann_date
        elif self.table_name in ['tushare_cn_cpi', 'tushare_cn_m', 'tushare_cn_ppi', 'tushare_sf_month']:
            return 'start_m', 'end_m', self.entities.month
        elif self.table_name in ['tushare_cn_gdp']:
            return 'start_q', 'end_q', self.entities.quarter
        elif self.table_name in ['tushare_us_tbr', 'tushare_us_tltr', 'tushare_us_trltr', 'tushare_us_trycr',
                                 'tushare_us_tycr', 'tushare_gz_index', 'tushare_hibor', 'tushare_libor',
                                 'tushare_shibor', 'tushare_shibor_lpr', 'tushare_wz_index', 'tushare_eco_cal']:
            return 'start_date', 'end_date', self.entities.date
        elif self.table_name in ['tushare_index_stock']:
            return 'start_date', 'end_date', self.entities.list_date
        elif 'start_date' in self.query_fields:
            return 'start_date', 'end_date', self.entities.trade_date
        elif 'start_month' in self.query_fields:
            return 'start_month', 'end_month', self.entities.month
        elif 'start_m' in self.query_fields:
            return 'start_m', 'end_m', self.entities.month
        return None
