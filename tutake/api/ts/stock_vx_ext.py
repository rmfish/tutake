"""
Tushare stock_vx接口
小沛估值因子
数据接口  https://tushare.pro/document/2?doc_id=303
"""
from tutake.api.ts.date_utils import day_by_day_params


def default_cron_express_ext(self):
    return None


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'trade_date,ts_code'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "2000"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return day_by_day_params(self, "20140101", "trade_date")
