from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao
from tutake.api.ts.tushare_base import Records
from tutake.utils.config import TutakeConfig

engine_pool = {}


def create_shared_engine(url: str, **connect_args):
    engine = engine_pool.get(url)
    if engine is None:
        engine = create_engine(url, **connect_args)
        engine_pool[url] = engine
    return engine


class TushareDAO(BaseDao):

    def __init__(self, engine, session_factory: sessionmaker, entities, database, table_name, query_fields,
                 entity_fields,
                 config: TutakeConfig):
        super().__init__(engine, session_factory, entities, database, table_name, query_fields, entity_fields, config)
        self.records = Records()

    def filter_process(self, filter_criterion, filter_by):
        if self.table_name in ['tushare_daily', 'tushare_weekly', 'tushare_monthly']:
            ts_code = filter_by.get("ts_code")
            if ts_code is not None and "," in ts_code:
                codes = ts_code.split(",")
                if filter_criterion is None:
                    filter_criterion = self.entities.in_(codes)
                else:
                    filter_criterion = and_(self.entities.ts_code.in_(codes), filter_criterion)
                del filter_by['ts_code']
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
        elif self.table_name in ['tushare_stk_managers', 'tushare_namechange', 'tushare_anns']:
            return 'start_date', 'end_date', self.entities.ann_date
        elif self.table_name in ['tushare_cn_cpi', 'tushare_cn_m', 'tushare_cn_ppi', 'tushare_sf_month']:
            return 'start_m', 'end_m', self.entities.month
        elif self.table_name in ['tushare_cn_gdp']:
            return 'start_q', 'end_q', self.entities.quarter
        elif self.table_name in ['tushare_us_tbr', 'tushare_us_tltr', 'tushare_us_trltr', 'tushare_us_trycr']:
            return 'start_date', 'end_date', self.entities.date
        elif 'start_date' in self.query_fields:
            return 'start_date', 'end_date', self.entities.trade_date
        elif 'start_month' in self.query_fields:
            return 'start_month', 'end_month', self.entities.month
        elif 'start_m' in self.query_fields:
            return 'start_m', 'end_m', self.entities.month
        return None
