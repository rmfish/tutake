"""
Tushare fund_div接口
获取公募基金分红数据
数据接口-公募基金-基金分红  https://tushare.pro/document/2?doc_id=120
"""

from tutake.api.ts.date_utils import day_by_day_params


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'ann_date desc,ts_code'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "1200"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return day_by_day_params(self, "19990329", "ann_date")
