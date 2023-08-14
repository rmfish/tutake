from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao
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
        elif 'start_date' in self.query_fields:
            return 'start_date', 'end_date', self.entities.trade_date
        elif 'start_month' in self.query_fields:
            return 'start_month', 'end_month', self.entities.month
        return None
