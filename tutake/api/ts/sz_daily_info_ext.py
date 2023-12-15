"""
Tushare sz_daily_info接口
获取深圳市场每日交易概况
数据接口-指数-深圳市场每日交易情况  https://tushare.pro/document/2?doc_id=268
"""
from tutake.api.ts.date_utils import start_end_step_params


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
    return start_end_step_params(self, start_date='20080102', step=30)
