"""
Tushare fx_daily接口
外汇日线行情
数据接口-外汇-外汇日线行情  https://tushare.pro/document/2?doc_id=179
"""
from tutake.api.ts.date_utils import start_end_step_params


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return ''


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "4000"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, "19381229", 365)
