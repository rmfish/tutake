"""
Tushare index_weight接口
获取各类指数成分和权重，月度数据 。
数据接口-指数-指数成分和权重  https://tushare.pro/document/2?doc_id=96
"""
from tutake.api.ts.date_utils import day_by_day_params


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'index_code,trade_date desc'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "5000"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return day_by_day_params(self, '20050115', date_column='trade_date')
